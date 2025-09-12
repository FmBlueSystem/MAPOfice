"""Unified Z.ai Provider Implementation

This module consolidates all ZAI provider variants into a single, optimized implementation
that uses the factory pattern for auto-registration.
"""

from __future__ import annotations

import json
import time
import re
from typing import Dict, Any, List, Optional

try:
    from zai import ZaiClient
except ImportError:
    ZaiClient = None

from src.analysis.provider_factory import (
    BaseProvider, 
    ProviderConfig, 
    ProviderResponse,
    ProviderType,
    ProviderFactory
)


@ProviderFactory.register_provider("zai")
class UnifiedZaiProvider(BaseProvider):
    """Unified Z.ai provider implementation with best features from all variants"""
    
    # Class-level metadata for auto-registration
    provider_type = ProviderType.ZAI
    supported_models = [
        "glm-4.5",           # Flagship model
        "glm-4.5v",          # Visual reasoning
        "glm-4.5-flash",     # FREE unlimited usage
        "glm-4-32b-0414-128k"  # Large context
    ]
    
    def __init__(self, config: ProviderConfig):
        """Initialize Z.ai provider
        
        Args:
            config: Configuration for Z.ai API
            
        Raises:
            ImportError: If zai-sdk package is not installed
        """
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
        
        # Strategy 1: Clean markdown code blocks
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
        
        # Strategy 3: Look for <json>...</json> tags
        m = re.search(r"<json>(.*?)</json>", text, flags=re.DOTALL)
        if m:
            try:
                return json.loads(m.group(1).strip())
            except json.JSONDecodeError:
                pass
        
        # Strategy 4: Extract from first { to last }
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start:end+1])
            except json.JSONDecodeError:
                pass
        
        # Strategy 5: Try regex patterns
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
        
        raise ValueError(f"No valid JSON found in text: {text[:200]}...")
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for text"""
        # Rough estimation: ~4 characters per token
        return len(text) // 4
    
    def _generate_fallback_json(self, track_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate fallback JSON when response parsing fails"""
        bpm = track_data.get('bpm', 120)
        energy = track_data.get('energy', 0.5)
        metadata_date = track_data.get('date', 'Unknown')
        
        # Extract year for era classification
        era = "2020s"
        if isinstance(metadata_date, str):
            year_match = re.search(r'(\d{4})', metadata_date)
            if year_match:
                year = int(year_match.group(1))
                era = f"{(year // 10) * 10}s"
        
        # Genre classification based on BPM and energy
        if bpm > 140 and energy > 0.7:
            genre = "dance" if era >= "2000s" else "electronic"
            mood = "energetic"
        elif bpm >= 120 and energy > 0.6:
            if era == "1980s":
                genre = "synth-pop"
            elif era == "1970s":
                genre = "disco"
            else:
                genre = "pop"
            mood = "upbeat"
        elif bpm < 90 and energy < 0.4:
            genre = "ballad"
            mood = "calm"
        else:
            genre = "pop"
            mood = "moderate"
        
        return {
            "artist_known": False,
            "genre": genre,
            "subgenre": f"{genre.lower()}_general",
            "era": era,
            "mood": mood,
            "confidence": 0.5,
            "analysis_notes": "Fallback classification based on audio features"
        }
    
    def analyze_track(self, track_metadata: Dict[str, Any]) -> ProviderResponse:
        """Analyze track using Z.ai API
        
        Args:
            track_metadata: Dictionary containing track information
            
        Returns:
            ProviderResponse with analysis results
        """
        start_time = time.time()
        
        try:
            # Wait for rate limiting
            self._wait_for_rate_limit()
            
            # Extract track information
            title = track_metadata.get('title', 'Unknown')
            artist = track_metadata.get('artist', 'Unknown')
            bpm = track_metadata.get('bpm', 0)
            key = track_metadata.get('key', 'Unknown')
            energy = track_metadata.get('energy', 0.0)
            metadata_date = track_metadata.get('date', 'Unknown')
            
            # Create optimized prompt
            user_prompt = f"""Classify this song: {artist} - {title}

BPM: {bpm}, Key: {key}, Energy: {energy:.3f}, Date: {metadata_date}

Return JSON only:
{{"artist_known": true/false, "genre": "specific_genre", "subgenre": "detailed_subgenre", "era": "decade", "mood": "descriptive_word", "confidence": 0.0-1.0}}

Genre patterns:
- 1980s synth/electronic → "synth-pop", "new wave"
- 1970s dance → "disco", "funk", "soul"  
- 1990s electronic → "house", "techno", "eurodance"
- 2000s+ → "electro house", "progressive house"

Era based on original release decade, not reissue."""
            
            # System message for clear expectations
            system_prompt = """You are a music classification expert. Respond ONLY with valid JSON.
Use your knowledge of the specific artist and song.
Be precise with genre classification based on musical style and era."""
            
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            # Make API call
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens
            )
            
            # Extract and parse response
            if response and response.choices and len(response.choices) > 0:
                message = response.choices[0].message
                content_text = message.content
                
                # Handle GLM-4.5-Flash reasoning content
                if not content_text and hasattr(message, 'reasoning_content'):
                    content_text = self._extract_json_from_reasoning(message.reasoning_content)
                
                raw_response = content_text
                
                # Parse JSON response
                try:
                    content_json = self._extract_json_robust(content_text)
                except (json.JSONDecodeError, ValueError):
                    # Use fallback if parsing fails
                    content_json = self._generate_fallback_json(track_metadata)
                
                # Calculate metrics
                input_tokens = self._estimate_tokens(user_prompt + system_prompt)
                output_tokens = self._estimate_tokens(content_text)
                cost_estimate = self._estimate_cost(input_tokens, output_tokens)
                processing_time = int((time.time() - start_time) * 1000)
                
                return ProviderResponse(
                    success=True,
                    content=content_json,
                    raw_response=raw_response,
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
                    error_message="Empty response from Z.ai API"
                )
                
        except Exception as e:
            return ProviderResponse(
                success=False,
                content={},
                raw_response="",
                provider_type=self.provider_type,
                model=self.config.model,
                processing_time_ms=int((time.time() - start_time) * 1000),
                error_message=f"Z.ai API error: {str(e)}"
            )
    
    def _extract_json_from_reasoning(self, reasoning_text: str) -> str:
        """Extract JSON from GLM-4.5-Flash reasoning content"""
        patterns = [
            r'\{[^{}]*\}',  # Simple single-level JSON
            r'\{(?:[^{}]|{[^{}]*})*\}',  # Nested JSON structures
            r'```json\s*(\{.*?\})\s*```',  # JSON in code blocks
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, reasoning_text, re.DOTALL)
            for match in matches:
                try:
                    json.loads(match)
                    return match
                except json.JSONDecodeError:
                    continue
        
        # Return empty JSON if extraction fails
        return "{}"
    
    def batch_analyze(self, tracks: List[Dict[str, Any]]) -> List[ProviderResponse]:
        """Analyze multiple tracks efficiently
        
        Args:
            tracks: List of track metadata dictionaries
            
        Returns:
            List of ProviderResponse objects
        """
        results = []
        for track in tracks:
            try:
                result = self.analyze_track(track)
                results.append(result)
            except Exception as e:
                results.append(ProviderResponse(
                    success=False,
                    content={},
                    raw_response="",
                    provider_type=self.provider_type,
                    model=self.config.model,
                    processing_time_ms=0,
                    error_message=str(e)
                ))
        return results
    
    def test_connection(self) -> bool:
        """Test connection to Z.ai API
        
        Returns:
            True if connection is successful, False otherwise
        """
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