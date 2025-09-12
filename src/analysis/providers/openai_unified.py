"""Unified OpenAI Provider

Consolidated implementation of OpenAI provider using the factory pattern.
"""

from __future__ import annotations

import json
import time
import re
from typing import Dict, Any, List, Optional

try:
    import openai
except ImportError:
    openai = None

from src.analysis.provider_factory import (
    BaseProvider, 
    ProviderConfig, 
    ProviderResponse,
    ProviderType,
    ProviderFactory
)


@ProviderFactory.register_provider("openai")
class UnifiedOpenAIProvider(BaseProvider):
    """Unified OpenAI provider for music analysis"""
    
    # Class-level metadata
    provider_type = ProviderType.OPENAI
    supported_models = [
        "gpt-4o",
        "gpt-4o-mini", 
        "gpt-4-turbo",
        "gpt-4",
        "gpt-3.5-turbo",
        "gpt-3.5-turbo-0125"
    ]
    
    def __init__(self, config: ProviderConfig):
        """Initialize OpenAI provider
        
        Args:
            config: Provider configuration
            
        Raises:
            ImportError: If openai package is not installed
        """
        super().__init__(config)
        
        if openai is None:
            raise ImportError(
                "openai package is required for OpenAI support. "
                "Install it with: pip install openai"
            )
        
        self.client = openai.OpenAI(api_key=config.api_key)
        
        # OpenAI pricing per 1M tokens
        self.pricing = self._get_model_pricing(config.model)
        
    def _get_model_pricing(self, model: str) -> Dict[str, float]:
        """Get pricing information for OpenAI models (per 1M tokens)"""
        pricing_map = {
            "gpt-4o": {"input": 2.50, "output": 10.00},
            "gpt-4o-mini": {"input": 0.15, "output": 0.60},
            "gpt-4-turbo": {"input": 10.00, "output": 30.00},
            "gpt-4": {"input": 30.00, "output": 60.00},
            "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
            "gpt-3.5-turbo-0125": {"input": 0.50, "output": 1.50},
            "default": {"input": 0.15, "output": 0.60}  # Default to gpt-4o-mini pricing
        }
        return pricing_map.get(model, pricing_map["default"])
    
    def _extract_json_from_response(self, text: str) -> Dict[str, Any]:
        """Extract JSON from OpenAI's response"""
        if not text or not text.strip():
            raise ValueError("Empty response from OpenAI")
        
        text = text.strip()
        
        # Strategy 1: Direct JSON parsing
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        # Strategy 2: Clean markdown code blocks
        if text.startswith("```json"):
            text = text[7:]
        if text.endswith("```"):
            text = text[:-3]
        
        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            pass
        
        # Strategy 3: Extract from first { to last }
        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > start:
            try:
                return json.loads(text[start:end])
            except json.JSONDecodeError:
                pass
        
        # Strategy 4: Regex patterns
        patterns = [
            r'\{[^{}]*\}',  # Simple single-level JSON
            r'\{(?:[^{}]|{[^{}]*})*\}',  # Nested JSON
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            for match in matches:
                try:
                    return json.loads(match)
                except json.JSONDecodeError:
                    continue
        
        raise ValueError(f"No valid JSON found in response: {text[:200]}...")
    
    def _create_analysis_prompt(self, track_data: Dict[str, Any]) -> str:
        """Create music analysis prompt for OpenAI"""
        title = track_data.get('title', 'Unknown')
        artist = track_data.get('artist', 'Unknown')
        bpm = track_data.get('bpm', 0)
        energy = track_data.get('energy', 0.0)
        key = track_data.get('key', 'Unknown')
        date = track_data.get('date', 'Unknown')
        
        return f"""Analyze this music track and provide a JSON response:

Track: {artist} - {title}
BPM: {bpm}
Key: {key}
Energy: {energy:.3f}
Metadata Date: {date}

Provide analysis in this exact JSON format:
{{
    "date_verification": {{
        "artist_known": true/false,
        "track_known": true/false,
        "known_original_year": "YYYY" or null,
        "metadata_year": "{date}",
        "is_likely_reissue": true/false,
        "verification_notes": "explanation"
    }},
    "genre": "primary genre",
    "subgenre": "specific subgenre",
    "mood": "emotional atmosphere",
    "era": "decade (e.g., 1980s)",
    "tags": ["tag1", "tag2", "tag3"],
    "confidence": 0.0-1.0,
    "analysis_notes": "brief explanation"
}}

Guidelines:
- Identify the ORIGINAL release year if known
- Use specific genre names (e.g., "synth-pop" not just "pop")
- Era should reflect original release decade
- Include 3-5 relevant tags

Return ONLY valid JSON, no additional text."""
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count (roughly 4 chars per token for English)"""
        return len(text) // 4
    
    def analyze_track(self, track_metadata: Dict[str, Any]) -> ProviderResponse:
        """Analyze track using OpenAI API
        
        Args:
            track_metadata: Dictionary containing track information
            
        Returns:
            ProviderResponse with analysis results
        """
        start_time = time.time()
        
        try:
            # Wait for rate limiting
            self._wait_for_rate_limit()
            
            # Create prompt
            user_prompt = self._create_analysis_prompt(track_metadata)
            
            # System message for JSON-only response
            system_prompt = """You are a music analysis expert with deep knowledge of music history, genres, and artists.
Always respond with valid JSON only, no additional text or explanations."""
            
            # Make API call
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
                response_format={"type": "json_object"} if "gpt-4" in self.config.model else None
            )
            
            # Extract response
            if response and response.choices:
                content_text = response.choices[0].message.content
                
                # Parse JSON
                try:
                    content_json = self._extract_json_from_response(content_text)
                except (json.JSONDecodeError, ValueError):
                    content_json = self._generate_fallback_response(track_metadata)
                
                # Calculate metrics
                input_tokens = self._estimate_tokens(system_prompt + user_prompt)
                output_tokens = self._estimate_tokens(content_text)
                
                # Get actual token usage if available
                if hasattr(response, 'usage'):
                    input_tokens = response.usage.prompt_tokens
                    output_tokens = response.usage.completion_tokens
                
                cost_estimate = self._estimate_cost(input_tokens, output_tokens)
                processing_time = int((time.time() - start_time) * 1000)
                
                return ProviderResponse(
                    success=True,
                    content=content_json,
                    raw_response=content_text,
                    provider_type=self.provider_type,
                    model=self.config.model,
                    processing_time_ms=processing_time,
                    tokens_used=input_tokens + output_tokens,
                    cost_estimate=cost_estimate
                )
            else:
                return ProviderResponse(
                    success=False,
                    content={},
                    raw_response="",
                    provider_type=self.provider_type,
                    model=self.config.model,
                    processing_time_ms=int((time.time() - start_time) * 1000),
                    error_message="Empty response from OpenAI API"
                )
                
        except Exception as e:
            return ProviderResponse(
                success=False,
                content={},
                raw_response="",
                provider_type=self.provider_type,
                model=self.config.model,
                processing_time_ms=int((time.time() - start_time) * 1000),
                error_message=f"OpenAI API error: {str(e)}"
            )
    
    def _generate_fallback_response(self, track_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback response when parsing fails"""
        bpm = track_data.get('bpm', 120)
        energy = track_data.get('energy', 0.5)
        
        # Basic classification
        if bpm > 140:
            genre, subgenre = "electronic", "dance"
        elif bpm >= 120:
            genre, subgenre = "pop", "dance-pop"
        elif bpm >= 90:
            genre, subgenre = "rock", "alternative"
        else:
            genre, subgenre = "ballad", "slow"
        
        return {
            "date_verification": {
                "artist_known": False,
                "track_known": False,
                "known_original_year": None,
                "metadata_year": track_data.get('date', 'Unknown'),
                "is_likely_reissue": False,
                "verification_notes": "Fallback classification"
            },
            "genre": genre,
            "subgenre": subgenre,
            "mood": "neutral",
            "era": "2020s",
            "tags": [genre, f"{int(bpm)}bpm"],
            "confidence": 0.3,
            "analysis_notes": "Fallback classification based on audio features"
        }
    
    def batch_analyze(self, tracks: List[Dict[str, Any]]) -> List[ProviderResponse]:
        """Analyze multiple tracks
        
        Args:
            tracks: List of track metadata dictionaries
            
        Returns:
            List of ProviderResponse objects
        """
        results = []
        for track in tracks:
            result = self.analyze_track(track)
            results.append(result)
        return results
    
    def test_connection(self) -> bool:
        """Test connection to OpenAI API
        
        Returns:
            True if connection is successful
        """
        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "user", "content": "Say OK"}
                ],
                max_tokens=5
            )
            return response is not None
        except Exception as e:
            print(f"OpenAI connection test failed: {e}")
            return False
    
    def _estimate_cost(self, prompt_tokens: int, response_tokens: int) -> float:
        """Estimate the cost of the API call
        
        Args:
            prompt_tokens: Number of input tokens
            response_tokens: Number of output tokens
            
        Returns:
            Cost estimate in USD
        """
        input_cost = (prompt_tokens / 1_000_000) * self.pricing["input"]
        output_cost = (response_tokens / 1_000_000) * self.pricing["output"]
        return input_cost + output_cost