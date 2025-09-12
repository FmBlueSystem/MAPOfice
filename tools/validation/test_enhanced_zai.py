#!/usr/bin/env python3
"""Test script for enhanced GLM-4.5-Flash prompt system with A→B fallback"""

import os
import json
import time
import re
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from zai import ZaiClient
except ImportError:
    ZaiClient = None

class EnhancedZaiTester:
    """Test implementation of enhanced Zai provider with A→B fallback"""
    
    def __init__(self, api_key: str, model: str = "glm-4.5-flash"):
        self.client = ZaiClient(api_key=api_key)
        self.model = model
    
    def _extract_json(self, text: str) -> Dict[str, Any]:
        """Extract JSON from LLM response, handling verbose outputs"""
        try:
            # 1) Preferente: bloque <json> ... </json>
            m = re.search(r"<json>(.*?)</json>", text, flags=re.DOTALL)
            if m:
                candidate = m.group(1).strip()
            else:
                # 2) Fallback: desde primer { hasta último }
                start = text.find("{")
                end = text.rfind("}")
                if start == -1 or end == -1 or end <= start:
                    raise ValueError("No JSON found")
                candidate = text[start:end+1]
            
            return json.loads(candidate)
        except (json.JSONDecodeError, ValueError) as e:
            raise ValueError(f"Failed to extract valid JSON: {e}")
    
    def _create_system_prompt_a(self) -> str:
        """Create reinforced JSON-only system prompt (Version A)"""
        return """Eres un validador musical. PIENSA en silencio y NO muestres tu razonamiento.
Responde con JSON VÁLIDO y NADA MÁS.
NO incluyas explicaciones, saludos, listas, Markdown, ni fences (```).

Salidas permitidas:
1) UNA ÚNICA línea JSON entre las etiquetas <json> y </json>.
2) Booleans en minúscula (true/false). Usa null cuando no sepas.

Reglas de decisión:
- "artist_known": true solo si reconoces con confianza al artista y la canción (esa combinación exacta).
- "known_original_year": año original del lanzamiento si lo sabes; si no, null.
- "is_likely_reissue": true si el "metadata_date" sugiere reedición/compilado distinto del año original.
- "genre"/"subgenre": específicos y en minúsculas (p. ej., "disco", "boogie", "italo disco", "house", "minimal house").
- "era": década basada en el lanzamiento original si se conoce; si no, usa la década más probable.
- "mood": 1–3 palabras (p. ej., "upbeat", "melancholic", "optimistic").

Formato EXACTO:
<json>{"date_verification":{"artist_known":true/false,"known_original_year":1234|null,"metadata_year":"YYYY"|"YYYY-MM-DD"|null,"is_likely_reissue":true/false},"genre":"...","subgenre":"...","era":"1950s|1960s|1970s|1980s|1990s|2000s|2010s|2020s","mood":"..."}</json>"""
    
    def _create_user_prompt_a(self, track_data: Dict[str, Any]) -> str:
        """Create user prompt for Version A (detailed)"""
        title = track_data.get('title', 'Unknown')
        artist = track_data.get('artist', 'Unknown')
        bpm = track_data.get('bpm', 0)
        key = track_data.get('key', 'Unknown')
        energy = track_data.get('energy', 0.0)
        metadata_date = track_data.get('date', 'Unknown')
        
        return f"""Track: {artist} - "{title}"
BPM: {bpm}, Key: {key}, Energy: {energy:.3f}
Metadata Date: {metadata_date}

RESPONDE SOLO con el bloque <json>...</json> descrito."""
    
    def _create_system_prompt_b(self) -> str:
        """Create ultra-stable minimal system prompt (Version B - fallback)"""
        return """DEVUELVE SOLO JSON (una línea), SIN NADA MÁS.

Reglas:
- Booleans en minúscula.
- Usa null si no sabes.
- No texto adicional, no Markdown, no comentarios."""
    
    def _create_user_prompt_b(self, track_data: Dict[str, Any]) -> str:
        """Create user prompt for Version B (minimal)"""
        title = track_data.get('title', 'Unknown')
        artist = track_data.get('artist', 'Unknown')
        bpm = track_data.get('bpm', 0)
        key = track_data.get('key', 'Unknown')
        energy = track_data.get('energy', 0.0)
        metadata_date = track_data.get('date', 'Unknown')
        
        return f"""{artist} - "{title}" | BPM {bpm} | Key {key} | Energy {energy:.3f} | Metadata {metadata_date}

{{"artist_known":true/false,"known_year":1234|null,"is_reissue":true/false,"genre":"...","subgenre":"...","era":"1950s|1960s|1970s|1980s|1990s|2000s|2010s|2020s","mood":"..."}}"""
    
    def analyze_track_with_fallback(self, track_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze track using A→B fallback orchestration"""
        
        print("🔄 Trying Version A (detailed with XML tags)...")
        
        # Try Version A first
        try:
            result = self._try_version_a(track_data)
            if result:
                print("✅ Version A succeeded!")
                return result
        except Exception as e:
            print(f"❌ Version A failed: {e}")
        
        print("🔄 Falling back to Version B (ultra-minimal)...")
        
        # Fallback to Version B
        try:
            result = self._try_version_b(track_data)
            print("✅ Version B succeeded!")
            return result
        except Exception as e:
            print(f"❌ Version B failed: {e}")
            return {"error": f"Both versions failed: {e}"}
    
    def _try_version_a(self, track_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Try Version A (detailed prompt with XML tags)"""
        messages = [
            {
                "role": "system", 
                "content": self._create_system_prompt_a()
            },
            {
                "role": "user", 
                "content": self._create_user_prompt_a(track_data)
            }
        ]
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.1,
            max_tokens=800,
            # stop=["</json>"]  # Uncomment if your client supports it
        )
        
        if response and response.choices and len(response.choices) > 0:
            message = response.choices[0].message
            content_text = message.content or ""
            
            # Handle GLM-4.5-Flash reasoning_content
            if not content_text and hasattr(message, 'reasoning_content'):
                content_text = message.reasoning_content or ""
            
            print(f"Raw response A: {content_text[:200]}...")
            
            # Try to extract JSON using the robust extractor
            return self._extract_json(content_text)
        
        return None
    
    def _try_version_b(self, track_data: Dict[str, Any]) -> Dict[str, Any]:
        """Try Version B (ultra-minimal fallback)"""
        messages = [
            {
                "role": "system", 
                "content": self._create_system_prompt_b()
            },
            {
                "role": "user", 
                "content": self._create_user_prompt_b(track_data)
            }
        ]
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.0,
            max_tokens=500
        )
        
        if response and response.choices and len(response.choices) > 0:
            message = response.choices[0].message
            content_text = message.content or ""
            
            # Handle GLM-4.5-Flash reasoning_content
            if not content_text and hasattr(message, 'reasoning_content'):
                content_text = message.reasoning_content or ""
            
            print(f"Raw response B: {content_text[:200]}...")
            
            # Try to extract JSON
            simple_json = self._extract_json(content_text)
            
            # Normalize simplified format to full format
            return self._normalize_version_b_response(simple_json, track_data)
        
        raise Exception("No response from Version B")
    
    def _normalize_version_b_response(self, simple_json: Dict[str, Any], track_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Version B simplified response to full format"""
        metadata_date = track_data.get('date', 'Unknown')
        
        # Handle both Version A and Version B formats
        if 'date_verification' in simple_json:
            # Already in Version A format
            return simple_json
        
        # Convert Version B to Version A format
        return {
            "date_verification": {
                "artist_known": simple_json.get("artist_known", False),
                "known_original_year": simple_json.get("known_year"),
                "metadata_year": metadata_date,
                "is_likely_reissue": simple_json.get("is_reissue", False)
            },
            "genre": simple_json.get("genre", "unknown"),
            "subgenre": simple_json.get("subgenre", "unknown"),
            "era": simple_json.get("era", "unknown"),
            "mood": simple_json.get("mood", "unknown")
        }


def main():
    """Test the enhanced system with Destination - Move On Up"""
    
    # Test data with the problematic track
    test_track = {
        'title': 'Move On Up',
        'artist': 'Destination', 
        'bpm': 118,
        'key': 'C',
        'energy': 0.75,
        'date': '1992-01-01',  # This is the Star-Funk compilation date, not original (1979)
        'hamms_vector': [0.8, 0.6, 0.7, 0.5, 0.9, 0.4, 0.6, 0.8, 0.7, 0.5, 0.6, 0.4]
    }
    
    # Initialize tester
    api_key = os.getenv('ZAI_API_KEY')
    if not api_key:
        print("❌ ZAI_API_KEY not found in environment")
        return
    
    tester = EnhancedZaiTester(api_key)
    
    print("🎵 TESTING ENHANCED ZAI SYSTEM")
    print(f"Track: {test_track['artist']} - {test_track['title']}")
    print(f"Metadata Date: {test_track['date']} (should be flagged as reissue - original is 1979)")
    print(f"BPM: {test_track['bpm']}, Energy: {test_track['energy']}")
    print("-" * 70)
    
    # Test the system
    result = tester.analyze_track_with_fallback(test_track)
    
    print("\n📊 FINAL RESULT:")
    print(json.dumps(result, indent=2))
    
    # Evaluate success
    if 'date_verification' in result:
        verification = result['date_verification']
        known_year = verification.get('known_original_year')
        is_reissue = verification.get('is_likely_reissue', False)
        
        print("\n🎯 EVALUATION:")
        print(f"   Artist Known: {verification.get('artist_known', 'N/A')}")
        print(f"   Known Original Year: {known_year}")
        print(f"   Is Likely Reissue: {is_reissue}")
        
        if known_year == 1979 and is_reissue:
            print("\n🎉 PERFECT SUCCESS: Identified 1979 as original and flagged 1992 as reissue!")
        elif result.get('era') == '1970s':
            print("\n✅ SUCCESS: Era correctly classified as 1970s despite 1992 metadata!")
        else:
            print(f"\n⚠️  PARTIAL: Era = {result.get('era')}, Genre = {result.get('genre')}")
    
    print(f"\n💰 Cost: FREE (GLM-4.5-Flash)")


if __name__ == "__main__":
    main()