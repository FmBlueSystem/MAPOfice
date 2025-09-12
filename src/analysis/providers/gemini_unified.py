"""Unified Google Gemini Provider

Consolidated implementation of Gemini provider using the factory pattern.
"""

from __future__ import annotations

import json
import time
import re
from typing import Dict, Any, List, Optional

try:
    import google.generativeai as genai
except ImportError:
    genai = None

from src.analysis.provider_factory import (
    BaseProvider, 
    ProviderConfig, 
    ProviderResponse,
    ProviderType,
    ProviderFactory
)


@ProviderFactory.register_provider("gemini")
class UnifiedGeminiProvider(BaseProvider):
    """Unified Google Gemini provider for music analysis"""
    
    # Class-level metadata
    provider_type = ProviderType.GEMINI
    supported_models = [
        "gemini-1.5-flash",
        "gemini-1.5-flash-8b",
        "gemini-1.5-pro",
        "gemini-1.0-pro",
        "gemini-pro"
    ]
    
    def __init__(self, config: ProviderConfig):
        """Initialize Gemini provider
        
        Args:
            config: Provider configuration
            
        Raises:
            ImportError: If google-generativeai package is not installed
        """
        super().__init__(config)
        
        if genai is None:
            raise ImportError(
                "google-generativeai package is required for Gemini support. "
                "Install it with: pip install google-generativeai"
            )
        
        # Configure Gemini with API key
        genai.configure(api_key=config.api_key)
        
        # Initialize the model
        self.model = genai.GenerativeModel(config.model)
        
        # Gemini pricing per 1M tokens
        self.pricing = self._get_model_pricing(config.model)
        
    def _get_model_pricing(self, model: str) -> Dict[str, float]:
        """Get pricing information for Gemini models (per 1M tokens)"""
        pricing_map = {
            "gemini-1.5-flash": {"input": 0.075, "output": 0.30},  # Most cost-effective
            "gemini-1.5-flash-8b": {"input": 0.0375, "output": 0.15},  # Even cheaper
            "gemini-1.5-pro": {"input": 1.25, "output": 5.00},
            "gemini-1.0-pro": {"input": 0.50, "output": 1.50},
            "gemini-pro": {"input": 0.50, "output": 1.50},
            "default": {"input": 0.075, "output": 0.30}
        }
        return pricing_map.get(model, pricing_map["default"])
    
    def _extract_json_from_response(self, text: str) -> Dict[str, Any]:
        """Extract JSON from Gemini's response"""
        if not text or not text.strip():
            raise ValueError("Empty response from Gemini")
        
        text = text.strip()
        
        # Strategy 1: Direct JSON parsing
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        # Strategy 2: Clean markdown code blocks
        if "```json" in text:
            match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1))
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
        
        # Strategy 4: Regex patterns for JSON structures
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
        """Create music analysis prompt for Gemini"""
        title = track_data.get('title', 'Unknown')
        artist = track_data.get('artist', 'Unknown')
        bpm = track_data.get('bpm', 0)
        energy = track_data.get('energy', 0.0)
        key = track_data.get('key', 'Unknown')
        date = track_data.get('date', 'Unknown')
        
        return f"""You are a music analysis expert. Analyze this track and respond with ONLY valid JSON:

Track Information:
- Artist: {artist}
- Title: {title}
- BPM: {bpm}
- Key: {key}
- Energy: {energy:.3f}
- Date: {date}

CRITICAL: Determine if you know this artist/track and identify the original release year.

Return this exact JSON structure:
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
    "mood": "emotional mood",
    "era": "decade (1960s/1970s/1980s/1990s/2000s/2010s/2020s)",
    "tags": ["tag1", "tag2", "tag3"],
    "confidence": 0.85,
    "analysis_notes": "brief explanation"
}}

Genre Guidelines:
- Be specific: use "synth-pop", "new wave", "post-punk" instead of generic "pop" or "rock"
- Consider the era: 1970s→disco/funk, 1980s→new wave/synth-pop, 1990s→house/techno
- Use BPM as a guide: 110-130→disco/house, 140+→punk/hardcore

RESPOND ONLY WITH JSON, NO OTHER TEXT."""
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count (roughly 4 chars per token)"""
        return len(text) // 4
    
    def analyze_track(self, track_metadata: Dict[str, Any]) -> ProviderResponse:
        """Analyze track using Gemini API
        
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
            prompt = self._create_analysis_prompt(track_metadata)
            
            # Configure generation settings
            generation_config = genai.types.GenerationConfig(
                temperature=self.config.temperature,
                max_output_tokens=self.config.max_tokens,
            )
            
            # Make API call
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            # Extract response
            if response and response.text:
                content_text = response.text
                
                # Parse JSON
                try:
                    content_json = self._extract_json_from_response(content_text)
                except (json.JSONDecodeError, ValueError):
                    content_json = self._generate_fallback_response(track_metadata)
                
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
                    error_message="Empty response from Gemini API"
                )
                
        except Exception as e:
            return ProviderResponse(
                success=False,
                content={},
                raw_response="",
                provider_type=self.provider_type,
                model=self.config.model,
                processing_time_ms=int((time.time() - start_time) * 1000),
                error_message=f"Gemini API error: {str(e)}"
            )
    
    def _generate_fallback_response(self, track_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback response when parsing fails"""
        bpm = track_data.get('bpm', 120)
        energy = track_data.get('energy', 0.5)
        date = track_data.get('date', 'Unknown')
        
        # Extract year for era
        era = "2020s"
        if isinstance(date, str):
            year_match = re.search(r'(\d{4})', date)
            if year_match:
                year = int(year_match.group(1))
                era = f"{(year // 10) * 10}s"
        
        # Basic classification
        if bpm > 140 and energy > 0.7:
            genre, subgenre = "electronic", "high-energy"
            mood = "energetic"
        elif bpm >= 120 and energy > 0.6:
            genre, subgenre = "pop", "dance-pop"
            mood = "upbeat"
        elif bpm >= 90:
            genre, subgenre = "rock", "mid-tempo"
            mood = "moderate"
        else:
            genre, subgenre = "ballad", "slow"
            mood = "calm"
        
        return {
            "date_verification": {
                "artist_known": False,
                "track_known": False,
                "known_original_year": None,
                "metadata_year": date,
                "is_likely_reissue": False,
                "verification_notes": "Fallback classification"
            },
            "genre": genre,
            "subgenre": subgenre,
            "mood": mood,
            "era": era,
            "tags": [genre, f"{int(bpm)}bpm", mood],
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
        """Test connection to Gemini API
        
        Returns:
            True if connection is successful
        """
        try:
            response = self.model.generate_content(
                "Say OK",
                generation_config=genai.types.GenerationConfig(max_output_tokens=10)
            )
            return response is not None
        except Exception as e:
            print(f"Gemini connection test failed: {e}")
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