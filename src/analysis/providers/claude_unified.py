"""Unified Anthropic Claude Provider

Consolidated implementation of Claude provider using the factory pattern.
"""

from __future__ import annotations

import json
import time
import re
from typing import Dict, Any, List, Optional

try:
    import anthropic
except ImportError:
    anthropic = None

from src.analysis.provider_factory import (
    BaseProvider, 
    ProviderConfig, 
    ProviderResponse,
    ProviderType,
    ProviderFactory
)


@ProviderFactory.register_provider("anthropic")
@ProviderFactory.register_provider("claude")  # Also register as "claude" for compatibility
class UnifiedClaudeProvider(BaseProvider):
    """Unified Anthropic Claude provider for music analysis"""
    
    # Class-level metadata
    provider_type = ProviderType.ANTHROPIC
    supported_models = [
        "claude-3-haiku-20240307",
        "claude-3-sonnet-20240229", 
        "claude-3-opus-20240229",
        "claude-3-5-sonnet-20241022",
        "claude-3-5-haiku-20241022"
    ]
    
    def __init__(self, config: ProviderConfig):
        """Initialize Claude provider
        
        Args:
            config: Provider configuration
            
        Raises:
            ImportError: If anthropic package is not installed
        """
        super().__init__(config)
        
        if anthropic is None:
            raise ImportError(
                "anthropic package is required for Claude support. "
                "Install it with: pip install anthropic"
            )
        
        self.client = anthropic.Anthropic(api_key=config.api_key)
        
        # Claude pricing per 1K tokens (updated for 2024)
        self.pricing = self._get_model_pricing(config.model)
        
    def _get_model_pricing(self, model: str) -> Dict[str, float]:
        """Get pricing information for Claude models (per 1K tokens)"""
        pricing_map = {
            "claude-3-haiku-20240307": {"input": 0.00025, "output": 0.00125},
            "claude-3-sonnet-20240229": {"input": 0.003, "output": 0.015},
            "claude-3-opus-20240229": {"input": 0.015, "output": 0.075},
            "claude-3-5-sonnet-20241022": {"input": 0.003, "output": 0.015},
            "claude-3-5-haiku-20241022": {"input": 0.001, "output": 0.005},
            "default": {"input": 0.00025, "output": 0.00125}  # Default to Haiku pricing
        }
        return pricing_map.get(model, pricing_map["default"])
    
    def _extract_json_from_response(self, text: str) -> Dict[str, Any]:
        """Extract JSON from Claude's response with multiple strategies"""
        if not text or not text.strip():
            raise ValueError("Empty response from Claude")
        
        text = text.strip()
        
        # Strategy 1: Direct JSON parsing
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        # Strategy 2: Find JSON block within ```json```
        json_match = re.search(r'```json\s*({.*?})\s*```', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
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
        
        # Strategy 4: Look for JSON patterns with regex
        patterns = [
            r'\{[^{}]*\}',  # Simple single-level JSON
            r'\{(?:[^{}]|{[^{}]*})*\}',  # Nested JSON structures
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            for match in matches:
                try:
                    return json.loads(match)
                except json.JSONDecodeError:
                    continue
        
        raise ValueError(f"No valid JSON found in Claude response: {text[:200]}...")
    
    def _create_optimized_prompt(self, track_data: Dict[str, Any]) -> str:
        """Create an optimized prompt for Claude with comprehensive analysis guidelines"""
        title = track_data.get('title', 'Unknown')
        artist = track_data.get('artist', 'Unknown')
        bpm = track_data.get('bpm', 0)
        energy = track_data.get('energy', 0.0)
        key = track_data.get('key', 'Unknown')
        date = track_data.get('date', 'Unknown')
        
        # Include HAMMS vector if available
        hamms_info = ""
        if 'hamms_vector' in track_data:
            hamms = track_data['hamms_vector']
            hamms_formatted = ', '.join([f"{v:.3f}" for v in hamms])
            hamms_info = f"\nHAMMS Vector: [{hamms_formatted}]"
        
        return f"""Analyze this music track and return ONLY a JSON response:

Track: {artist} - {title}
BPM: {bpm}
Key: {key}
Energy: {energy:.2f}
Date: {date}{hamms_info}

CRITICAL: Determine the original release year if you know this artist/track, then classify accurately.

Required JSON format:
{{
    "date_verification": {{
        "artist_known": true/false,
        "track_known": true/false,
        "known_original_year": "1979" or null,
        "metadata_year": "{date}",
        "is_likely_reissue": true/false,
        "verification_notes": "Brief explanation"
    }},
    "genre": "specific primary genre",
    "subgenre": "more specific classification",
    "mood": "emotional mood/atmosphere",
    "era": "decade (1970s/1980s/1990s/2000s/2010s/2020s)",
    "tags": ["descriptive", "keywords", "style"],
    "confidence": 0.85,
    "analysis_notes": "Brief explanation"
}}

Genre Classification Guidelines:
- 1970s: disco, funk, soul, prog rock, punk
- 1980s: new wave, synth-pop, post-punk, hip-hop
- 1990s: house, techno, grunge, trip-hop
- 2000s+: electro house, dubstep, indie rock

Use your knowledge to verify dates and classify accurately. Return ONLY valid JSON."""
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for Claude (roughly 4 chars per token)"""
        return len(text) // 4
    
    def analyze_track(self, track_metadata: Dict[str, Any]) -> ProviderResponse:
        """Analyze track using Claude API
        
        Args:
            track_metadata: Dictionary containing track information
            
        Returns:
            ProviderResponse with analysis results
        """
        start_time = time.time()
        
        try:
            # Wait for rate limiting
            self._wait_for_rate_limit()
            
            # Create optimized prompt
            prompt = self._create_optimized_prompt(track_metadata)
            
            # Make API call to Claude
            message = self.client.messages.create(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                system="You are a music analysis expert. Respond with valid JSON only.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Extract response content
            if message and message.content:
                # Claude returns a list of content blocks
                content_text = message.content[0].text if isinstance(message.content, list) else str(message.content)
                
                # Parse JSON response
                try:
                    content_json = self._extract_json_from_response(content_text)
                except (json.JSONDecodeError, ValueError) as e:
                    # Generate fallback response
                    content_json = self._generate_fallback_response(track_metadata)
                    content_json["error_note"] = f"JSON parsing failed: {str(e)}"
                
                # Calculate metrics
                input_tokens = self._estimate_tokens(prompt)
                output_tokens = self._estimate_tokens(content_text)
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
                    error_message="Empty response from Claude API"
                )
                
        except Exception as e:
            return ProviderResponse(
                success=False,
                content={},
                raw_response="",
                provider_type=self.provider_type,
                model=self.config.model,
                processing_time_ms=int((time.time() - start_time) * 1000),
                error_message=f"Claude API error: {str(e)}"
            )
    
    def _generate_fallback_response(self, track_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback response when parsing fails"""
        bpm = track_data.get('bpm', 120)
        energy = track_data.get('energy', 0.5)
        
        # Basic genre inference
        if bpm > 140:
            genre = "electronic"
            subgenre = "high-energy"
        elif bpm >= 120:
            genre = "pop"
            subgenre = "dance-pop"
        elif bpm >= 90:
            genre = "rock"
            subgenre = "mid-tempo"
        else:
            genre = "ballad"
            subgenre = "slow"
        
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
            "analysis_notes": "Fallback classification based on BPM and energy"
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
        """Test connection to Claude API
        
        Returns:
            True if connection is successful
        """
        try:
            message = self.client.messages.create(
                model=self.config.model,
                max_tokens=10,
                messages=[
                    {"role": "user", "content": "Say 'OK'"}
                ]
            )
            return message is not None
        except Exception as e:
            print(f"Claude connection test failed: {e}")
            return False
    
    def _estimate_cost(self, prompt_tokens: int, response_tokens: int) -> float:
        """Estimate the cost of the API call
        
        Args:
            prompt_tokens: Number of input tokens
            response_tokens: Number of output tokens
            
        Returns:
            Cost estimate in USD
        """
        # Claude pricing is per 1K tokens, not per 1M
        input_cost = (prompt_tokens / 1000) * self.pricing["input"]
        output_cost = (response_tokens / 1000) * self.pricing["output"]
        return input_cost + output_cost