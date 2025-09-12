"""Enhanced Z.ai Provider with complete A→B fallback system"""

from __future__ import annotations

import json
import time
import re
from typing import Dict, Any, Optional

try:
    from zai import ZaiClient
except ImportError:
    ZaiClient = None

from src.analysis.llm_provider import BaseLLMProvider, LLMConfig, LLMResponse, LLMProvider


class EnhancedZaiProvider(BaseLLMProvider):
    """Enhanced Z.ai provider with A→B fallback and date verification"""
    
    def __init__(self, config: LLMConfig):
        """Initialize enhanced Z.ai provider"""
        super().__init__(config)
        
        if ZaiClient is None:
            raise ImportError(
                "zai-sdk package is required for Z.ai support. "
                "Install it with: pip install zai-sdk"
            )
        
        # Initialize Z.ai client
        self.client = ZaiClient(api_key=config.api_key)
        
        # Z.ai pricing per million tokens
        self.pricing = self._get_model_pricing(config.model)
        
    def _get_model_pricing(self, model: str) -> Dict[str, float]:
        """Get pricing information for Z.ai models"""
        pricing_map = {
            "glm-4.5": {"input": 0.60, "output": 2.20},
            "glm-4.5v": {"input": 0.60, "output": 1.80},
            "glm-4-32b-0414-128k": {"input": 0.10, "output": 0.10},
            "glm-4.5-flash": {"input": 0.00, "output": 0.00},  # FREE
            "default": {"input": 1.00, "output": 3.00}
        }
        return pricing_map.get(model, pricing_map["default"])
    
    def _extract_json_robust(self, text: str) -> Dict[str, Any]:
        """Enhanced JSON extraction with multiple fallback strategies"""
        if not text or not text.strip():
            raise ValueError("Empty text provided")
        
        # Strategy 1: Look for <json>...</json> tags (for Version A)
        m = re.search(r"<json>(.*?)</json>", text, flags=re.DOTALL)
        if m:
            try:
                candidate = m.group(1).strip()
                return json.loads(candidate)
            except json.JSONDecodeError:
                pass
        
        # Strategy 2: Clean markdown code blocks
        clean_text = text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:]
        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]
        
        # Strategy 3: Try direct JSON parsing
        try:
            return json.loads(clean_text.strip())
        except json.JSONDecodeError:
            pass
        
        # Strategy 4: Extract from first { to last }
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                candidate = text[start:end+1]
                return json.loads(candidate)
            except json.JSONDecodeError:
                pass
        
        # Strategy 5: Find JSON-like structures with regex
        json_patterns = [
            r'\\{[^{}]*\\}',  # Simple single-level JSON
            r'\\{(?:[^{}]|{[^{}]*})*\\}',  # Nested JSON structures
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            for match in matches:
                try:
                    return json.loads(match)
                except json.JSONDecodeError:
                    continue
        
        # If all strategies fail, raise error
        raise ValueError(f"No valid JSON found in text: {text[:200]}...")
    
    def _create_system_prompt_a(self) -> str:
        """Create Version A system prompt (detailed with date verification)"""
        return """Eres un validador musical experto. PIENSA en silencio y NO muestres tu razonamiento.
Responde con JSON VÁLIDO y NADA MÁS.
NO incluyas explicaciones, saludos, listas, Markdown, ni fences (```).

Salidas permitidas:
1) UNA ÚNICA línea JSON entre las etiquetas <json> y </json>.
2) Booleans en minúscula (true/false). Usa null cuando no sepas.

CRÍTICO - Reglas de decisión:
- "artist_known": true solo si reconoces con CONFIANZA al artista y la canción (esa combinación exacta)
- "known_original_year": año original del lanzamiento si lo sabes; si no, null
- "is_likely_reissue": true si el "metadata_date" sugiere reedición/compilado distinto del año original
- "genre"/"subgenre": específicos y en minúsculas (ej: "disco", "boogie", "new wave", "synthpop")
- "era": década basada en el lanzamiento ORIGINAL si se conoce; si no, usa la década más probable
- "mood": 1-3 palabras (ej: "upbeat", "melancholic", "optimistic")

Formato EXACTO:
<json>{"date_verification":{"artist_known":true/false,"known_original_year":1979|null,"metadata_year":"1992-01-01","is_likely_reissue":true/false},"genre":"disco","subgenre":"boogie","era":"1970s","mood":"upbeat"}</json>"""
    
    def _create_user_prompt_a(self, track_data: Dict[str, Any]) -> str:
        """Create Version A user prompt (detailed)"""
        title = track_data.get('title', 'Unknown')
        artist = track_data.get('artist', 'Unknown')
        bpm = track_data.get('bpm', 0)
        key = track_data.get('key', 'Unknown')
        energy = track_data.get('energy', 0.0)
        metadata_date = track_data.get('date', 'Unknown')
        
        return f"""Track: {artist} - "{title}"
BPM: {bpm}, Key: {key}, Energy: {energy:.3f}
Metadata Date: {metadata_date}

¿Conoces este artista/canción exactos? ¿Cuál es el año ORIGINAL de lanzamiento?
RESPONDE SOLO con el bloque <json>...</json> descrito."""
    
    def _create_system_prompt_b(self) -> str:
        """Create Version B system prompt (ultra-minimal fallback)"""
        return """DEVUELVE SOLO JSON (una línea), SIN NADA MÁS.
Booleans en minúscula. Usa null si no sabes. No texto adicional."""
    
    def _create_user_prompt_b(self, track_data: Dict[str, Any]) -> str:
        """Create Version B user prompt (minimal)"""
        title = track_data.get('title', 'Unknown')
        artist = track_data.get('artist', 'Unknown')
        bpm = track_data.get('bpm', 0)
        key = track_data.get('key', 'Unknown')
        energy = track_data.get('energy', 0.0)
        metadata_date = track_data.get('date', 'Unknown')
        
        return f"""{artist} - "{title}" | BPM {bpm} | Key {key} | Energy {energy:.3f} | Metadata {metadata_date}

{{"artist_known":false,"known_year":null,"is_reissue":false,"genre":"disco","subgenre":"boogie","era":"1970s","mood":"upbeat"}}"""
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for text"""
        return len(text) // 4
    
    def _estimate_cost(self, prompt_tokens: int, response_tokens: int) -> float:
        """Estimate the cost of the API call"""
        input_cost = (prompt_tokens / 1_000_000) * self.pricing["input"]
        output_cost = (response_tokens / 1_000_000) * self.pricing["output"]
        return input_cost + output_cost
    
    def analyze_track(self, track_data: Dict[str, Any]) -> LLMResponse:
        """Analyze track using A→B fallback orchestration"""
        start_time = time.time()
        
        try:
            # Wait for rate limiting
            self._wait_for_rate_limit()
            
            # Try Version A (detailed with date verification) first
            try:
                result = self._try_version_a(track_data, start_time)
                if result:
                    return result
            except Exception:
                pass  # Fall through to Version B
            
            # Fallback to Version B (ultra-minimal)
            return self._try_version_b(track_data, start_time)
                
        except Exception as e:
            processing_time = int((time.time() - start_time) * 1000)
            return LLMResponse(
                success=False,
                content={},
                raw_response="",
                provider=LLMProvider.ZAI,
                model=self.config.model,
                processing_time_ms=processing_time,
                error_message=f"Z.ai API error: {str(e)}"
            )
    
    def _try_version_a(self, track_data: Dict[str, Any], start_time: float) -> Optional[LLMResponse]:
        """Try Version A (detailed prompt with XML tags and date verification)"""
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
            model=self.config.model,
            messages=messages,
            temperature=0.1,
            max_tokens=800
        )
        
        if response and response.choices and len(response.choices) > 0:
            message = response.choices[0].message
            content_text = message.content or ""
            
            # Handle GLM-4.5-Flash reasoning_content
            if not content_text and hasattr(message, 'reasoning_content'):
                content_text = message.reasoning_content or ""
            
            try:
                # Try to extract JSON using the robust extractor
                content_json = self._extract_json_robust(content_text)
                
                # Calculate metrics
                input_tokens = self._estimate_tokens(self._create_user_prompt_a(track_data))
                output_tokens = self._estimate_tokens(content_text)
                cost_estimate = self._estimate_cost(input_tokens, output_tokens)
                processing_time = int((time.time() - start_time) * 1000)
                
                return LLMResponse(
                    success=True,
                    content=content_json,
                    raw_response=content_text,
                    provider=LLMProvider.ZAI,
                    model=self.config.model,
                    processing_time_ms=processing_time,
                    tokens_used=input_tokens + output_tokens,
                    cost_estimate=cost_estimate
                )
            except ValueError:
                # JSON extraction failed, will fallback to Version B
                return None
        
        return None
    
    def _try_version_b(self, track_data: Dict[str, Any], start_time: float) -> LLMResponse:
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
            model=self.config.model,
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
            
            try:
                # Try to extract JSON
                simple_json = self._extract_json_robust(content_text)
                
                # Normalize simplified format to full format
                normalized_json = self._normalize_version_b_response(simple_json, track_data)
                
                # Calculate metrics
                input_tokens = self._estimate_tokens(self._create_user_prompt_b(track_data))
                output_tokens = self._estimate_tokens(content_text)
                cost_estimate = self._estimate_cost(input_tokens, output_tokens)
                processing_time = int((time.time() - start_time) * 1000)
                
                return LLMResponse(
                    success=True,
                    content=normalized_json,
                    raw_response=content_text,
                    provider=LLMProvider.ZAI,
                    model=self.config.model,
                    processing_time_ms=processing_time,
                    tokens_used=input_tokens + output_tokens,
                    cost_estimate=cost_estimate
                )
            except ValueError:
                # Ultimate fallback
                fallback_json = self._generate_fallback_json(track_data)
                normalized_json = self._normalize_version_b_response(json.loads(fallback_json), track_data)
                
                processing_time = int((time.time() - start_time) * 1000)
                return LLMResponse(
                    success=True,
                    content=normalized_json,
                    raw_response="Fallback response used",
                    provider=LLMProvider.ZAI,
                    model=self.config.model,
                    processing_time_ms=processing_time,
                    tokens_used=100,  # Estimated
                    cost_estimate=0.0
                )
        
        # Ultimate fallback if no response
        fallback_json = self._generate_fallback_json(track_data)
        normalized_json = self._normalize_version_b_response(json.loads(fallback_json), track_data)
        processing_time = int((time.time() - start_time) * 1000)
        
        return LLMResponse(
            success=False,
            content=normalized_json,
            raw_response="No response from API",
            provider=LLMProvider.ZAI,
            model=self.config.model,
            processing_time_ms=processing_time,
            error_message="No response from Z.ai API, used fallback"
        )
    
    def _normalize_version_b_response(self, simple_json: Dict[str, Any], track_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert Version B simplified response to full format expected by the system"""
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
    
    def _generate_fallback_json(self, track_data: Dict[str, Any]) -> str:
        """Generate fallback JSON when all else fails"""
        # Basic genre inference from BPM and energy
        bpm = track_data.get('bpm', 120)
        energy = track_data.get('energy', 0.5)
        
        if bpm > 140 and energy > 0.7:
            genre = "electronic"
            mood = "energetic"
        elif bpm > 120 and energy > 0.6:
            genre = "disco"
            mood = "upbeat"
        elif bpm < 90 and energy < 0.4:
            genre = "ballad"
            mood = "calm"
        else:
            genre = "pop"
            mood = "moderate"
        
        fallback_response = {
            "date_verification": {
                "artist_known": False,
                "known_original_year": None,
                "metadata_year": track_data.get('date', 'Unknown'),
                "is_likely_reissue": False
            },
            "genre": genre,
            "subgenre": f"{genre} fusion",
            "mood": mood,
            "era": "unknown",
            "tags": [genre, mood, "fallback"],
            "confidence": 0.3,
            "analysis_notes": "Generated from basic audio features (system fallback)"
        }
        
        return json.dumps(fallback_response)
    
    def test_connection(self) -> bool:
        """Test connection to Z.ai API"""
        try:
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello, respond with just 'OK'"}
            ]
            
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                max_tokens=10
            )
            
            return response is not None and len(response.choices) > 0
        except Exception as e:
            print(f"Z.ai connection test failed: {e}")
            return False