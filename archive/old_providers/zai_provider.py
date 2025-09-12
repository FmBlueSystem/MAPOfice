"""Z.ai Provider Implementation for Multi-LLM Architecture"""

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


class ZaiProvider(BaseLLMProvider):
    """Z.ai provider implementation"""
    
    def __init__(self, config: LLMConfig):
        """Initialize Z.ai provider
        
        Args:
            config: Configuration for Z.ai API
            
        Raises:
            ImportError: If zai-sdk package is not installed
            ValueError: If configuration is invalid
        """
        super().__init__(config)
        
        if ZaiClient is None:
            raise ImportError(
                "zai-sdk package is required for Z.ai support. "
                "Install it with: pip install zai-sdk"
            )
        
        # Initialize Z.ai client
        self.client = ZaiClient(api_key=config.api_key)
        
        # Z.ai pricing per million tokens (estimated based on competitive pricing)
        self.pricing = self._get_model_pricing(config.model)
        
    def _get_model_pricing(self, model: str) -> Dict[str, float]:
        """Get pricing information for Z.ai models
        
        Args:
            model: Model name
            
        Returns:
            Dictionary with 'input' and 'output' pricing per million tokens
        """
        # Z.ai pricing - based on official documentation
        pricing_map = {
            "glm-4.5": {"input": 0.60, "output": 2.20},        # Flagship model
            "glm-4.5v": {"input": 0.60, "output": 1.80},       # Visual reasoning
            "glm-4-32b-0414-128k": {"input": 0.10, "output": 0.10},  # $0.1 per 1M tokens
            "glm-4.5-flash": {"input": 0.00, "output": 0.00},  # FREE unlimited usage
            "default": {"input": 1.00, "output": 3.00}
        }
        
        return pricing_map.get(model, pricing_map["default"])
    
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

    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for text
        
        Args:
            text: Input text
            
        Returns:
            Estimated token count (rough approximation)
        """
        # Rough estimation: ~4 characters per token for most languages
        return len(text) // 4
    
    def _estimate_cost(self, prompt_tokens: int, response_tokens: int) -> float:
        """Estimate the cost of the API call (abstract method implementation)
        
        Args:
            prompt_tokens: Number of input tokens
            response_tokens: Number of output tokens
            
        Returns:
            Cost estimate in USD
        """
        input_cost = (prompt_tokens / 1_000_000) * self.pricing["input"]
        output_cost = (response_tokens / 1_000_000) * self.pricing["output"]
        return input_cost + output_cost
    
    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost estimate for API call (convenience method)
        
        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            
        Returns:
            Cost estimate in USD
        """
        return self._estimate_cost(input_tokens, output_tokens)
    
    def _extract_json_robust(self, text: str) -> Dict[str, Any]:
        """Enhanced JSON extraction with multiple fallback strategies"""
        if not text or not text.strip():
            raise ValueError("Empty text provided")
        
        # Strategy 1: Clean markdown code blocks (existing logic)
        clean_text = text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text[7:]
        if clean_text.endswith("```"):
            clean_text = clean_text[:-3]
        
        # Strategy 2: Try direct JSON parsing first
        try:
            return json.loads(clean_text.strip())
        except json.JSONDecodeError:
            pass
        
        # Strategy 3: Look for <json>...</json> tags (for enhanced prompts)
        m = re.search(r"<json>(.*?)</json>", text, flags=re.DOTALL)
        if m:
            try:
                candidate = m.group(1).strip()
                return json.loads(candidate)
            except json.JSONDecodeError:
                pass
        
        # Strategy 4: Extract from first { to last } (original fallback)
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                candidate = text[start:end+1]
                return json.loads(candidate)
            except json.JSONDecodeError:
                pass
        
        # Strategy 5: Try to find any JSON-like structure with regex
        json_patterns = [
            r'\{[^{}]*\}',  # Simple single-level JSON
            r'\{(?:[^{}]|{[^{}]*})*\}',  # Nested JSON structures
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
    
    def analyze_track(self, track_data: Dict[str, Any]) -> LLMResponse:
        """Analyze track using Z.ai API
        
        Args:
            track_data: Dictionary containing track information
            
        Returns:
            LLMResponse with analysis results
        """
        start_time = time.time()
        
        try:
            # Wait for rate limiting
            self._wait_for_rate_limit()
            
            # Use exact same prompt format that worked in debug script
            title = track_data.get('title', 'Unknown')
            artist = track_data.get('artist', 'Unknown')
            bpm = track_data.get('bpm', 0)
            key = track_data.get('key', 'Unknown')
            energy = track_data.get('energy', 0.0)
            
            # Extract metadata date for comparison
            metadata_date = track_data.get('date', 'Unknown')
            
            # Use microprompt strategy: Simple, direct, pattern-based
            microprompt = f"""Classify this song: {artist} - {title}

Return JSON only:
{{"artist_known": true/false, "genre": "specific_genre", "era": "decade", "mood": "descriptive_word"}}

Genre patterns:
- 1980s synth/electronic pop → "synth-pop", "new wave", "dance-pop"
- 1970s dance music → "disco", "funk", "soul"  
- 1990s electronic → "house", "techno", "eurodance"
- 2000s+ → "electro house", "progressive house"
- Rock variants → "rock", "alternative rock", "indie rock"
- Slower songs → "ballad", "soft rock"

Era based on original release decade, not reissue."""
            
            # Enhanced system message with clear music knowledge expectations
            messages = [
                {
                    "role": "system", 
                    "content": """You are a music classification expert with deep knowledge of artists, genres, and musical eras.

CRITICAL RULES:
- Respond ONLY with valid JSON
- Use your knowledge of the specific artist and song
- Be precise with genre classification based on musical style and era
- Era should reflect the original release decade"""
                },
                {
                    "role": "user", 
                    "content": microprompt
                }
            ]
            
            # Make API call to Z.ai with higher token limit for full responses
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=800  # Increased for Z.ai to generate complete responses
            )
            
            # Extract response content
            if response and response.choices and len(response.choices) > 0:
                message = response.choices[0].message
                content_text = message.content
                
                # For GLM-4.5-Flash, handle reasoning_content differently
                if not content_text and hasattr(message, 'reasoning_content'):
                    reasoning_text = message.reasoning_content
                    raw_response = reasoning_text
                    
                    # Try to extract JSON from reasoning content
                    # GLM-4.5-Flash embeds JSON in reasoning text with code blocks
                    try:
                        import re
                        
                        # Try multiple extraction patterns in order of preference
                        patterns = [
                            r'\{[^{}]*\}',  # Simple single-level JSON
                            r'\{(?:[^{}]|{[^{}]*})*\}',    # Nested JSON structures
                            r'```json\s*(\{.*?\})\s*```',  # JSON in code blocks
                            r'(\{.*?\})',                   # Any JSON-like structure
                        ]
                        
                        json_found = False
                        for pattern in patterns:
                            matches = re.findall(pattern, reasoning_text, re.DOTALL)
                            for match in matches:
                                try:
                                    # Test if it's valid JSON
                                    json.loads(match)
                                    content_text = match
                                    json_found = True
                                    break
                                except json.JSONDecodeError:
                                    continue
                            if json_found:
                                break
                        
                        if not json_found:
                            # Fallback: create basic JSON from the music analysis context
                            content_text = self._generate_fallback_json(track_data)
                            
                    except Exception:
                        content_text = self._generate_fallback_json(track_data)
                else:
                    raw_response = content_text
                
                # Parse JSON response with enhanced extraction
                try:
                    content_json = self._extract_json_robust(content_text)
                except (json.JSONDecodeError, ValueError) as e:
                    return LLMResponse(
                        success=False,
                        content={},
                        raw_response=content_text,
                        provider=LLMProvider.ZAI,
                        model=self.config.model,
                        processing_time_ms=int((time.time() - start_time) * 1000),
                        error_message=f"Failed to parse JSON response: {e}"
                    )
                
                # Calculate cost estimate
                input_tokens = self._estimate_tokens(prompt)
                output_tokens = self._estimate_tokens(content_text)
                cost_estimate = self._calculate_cost(input_tokens, output_tokens)
                
                processing_time = int((time.time() - start_time) * 1000)
                
                return LLMResponse(
                    success=True,
                    content=content_json,
                    raw_response=raw_response,
                    provider=LLMProvider.ZAI,
                    model=self.config.model,
                    processing_time_ms=processing_time,
                    tokens_used=input_tokens + output_tokens,
                    cost_estimate=cost_estimate
                )
            else:
                return LLMResponse(
                    success=False,
                    content={},
                    raw_response="",
                    provider=LLMProvider.ZAI,
                    model=self.config.model,
                    processing_time_ms=int((time.time() - start_time) * 1000),
                    error_message="Empty response from Z.ai API"
                )
                
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
    
    def get_cost_estimates(self) -> Dict[str, float]:
        """Get cost estimates for this provider
        
        Returns:
            Dictionary with cost per million tokens
        """
        return {
            "input_cost_per_1M": self.pricing["input"],
            "output_cost_per_1M": self.pricing["output"]
        }
    
    def _generate_fallback_json(self, track_data: Dict[str, Any]) -> str:
        """Generate fallback JSON when GLM-4.5-Flash reasoning doesn't contain parseable JSON"""
        # Basic genre inference from BPM and energy with improved logic
        bpm = track_data.get('bpm', 120)
        energy = track_data.get('energy', 0.5)
        metadata_date = track_data.get('date', 'Unknown')
        
        # Try to extract year from metadata_date for era classification
        era = "2020s"  # default
        if isinstance(metadata_date, str):
            import re
            year_match = re.search(r'(\d{4})', metadata_date)
            if year_match:
                year = int(year_match.group(1))
                if 1950 <= year < 1960:
                    era = "1950s"
                elif 1960 <= year < 1970:
                    era = "1960s"
                elif 1970 <= year < 1980:
                    era = "1970s"
                elif 1980 <= year < 1990:
                    era = "1980s"
                elif 1990 <= year < 2000:
                    era = "1990s"
                elif 2000 <= year < 2010:
                    era = "2000s"
                elif 2010 <= year < 2020:
                    era = "2010s"
                elif 2020 <= year < 2030:
                    era = "2020s"
        
        # Improved genre classification based on BPM and energy
        if bpm > 140 and energy > 0.7:
            genre = "dance" if era in ["2000s", "2010s", "2020s"] else "electronic"
            subgenre = "high energy dance"
            mood = "energetic"
        elif bpm >= 120 and energy > 0.6:
            if era == "1980s":
                genre = "synth-pop"
                subgenre = "new wave"
            elif era == "1970s":
                genre = "disco"
                subgenre = "classic disco"
            else:
                genre = "pop"
                subgenre = "upbeat pop"
            mood = "upbeat"
        elif bpm < 90 and energy < 0.4:
            genre = "ballad"
            subgenre = "slow ballad"
            mood = "calm"
        else:
            genre = "pop"
            subgenre = "mid-tempo pop"
            mood = "moderate"
        
        fallback_response = {
            "artist_known": False,
            "genre": genre,
            "era": era,
            "mood": mood
        }
        
        return json.dumps(fallback_response)

    def test_connection(self) -> bool:
        """Test connection to Z.ai API
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            # Simple test request
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