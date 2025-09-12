"""Gemini (Google) Provider implementation.

This module implements the Gemini LLM provider using the unified provider interface.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
import google.generativeai as genai
from datetime import datetime

from ..base_provider import BaseLLMProvider, ProviderConfig
from ..provider_factory import register_provider

logger = logging.getLogger(__name__)


@register_provider("gemini")
class GeminiProvider(BaseLLMProvider):
    """Gemini (Google) LLM Provider implementation."""
    
    DEFAULT_MODEL = "gemini-1.5-flash"
    
    def _validate_config(self):
        """Validate Gemini-specific configuration."""
        # Check for API key
        if not self.config.api_key and self.config.api_key_env:
            api_key = os.getenv(self.config.api_key_env or 'GEMINI_API_KEY')
            if not api_key:
                raise ValueError(f"Gemini API key not found in environment variable: {self.config.api_key_env or 'GEMINI_API_KEY'}")
            self.config.api_key = api_key
        
        if not self.config.api_key:
            raise ValueError("Gemini API key is required")
        
        # Set defaults
        if not self.config.model:
            self.config.model = self.DEFAULT_MODEL
        
        # Configure Gemini
        genai.configure(api_key=self.config.api_key)
        self.model = genai.GenerativeModel(self.config.model)
    
    def analyze_track(self, track_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a single track using Gemini.
        
        Args:
            track_metadata: Track information
        
        Returns:
            Enriched metadata with AI analysis
        """
        prompt = self._create_analysis_prompt(track_metadata)
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=1000
                )
            )
            
            # Parse response
            analysis = self._parse_response(response.text)
            
            # Merge with original metadata
            result = track_metadata.copy()
            result['ai_analysis'] = analysis
            result['provider'] = 'gemini'
            result['model'] = self.config.model
            result['timestamp'] = datetime.now().isoformat()
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing track with Gemini: {e}")
            raise
    
    def batch_analyze(self, tracks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze multiple tracks efficiently.
        
        Args:
            tracks: List of track metadata
        
        Returns:
            List of enriched metadata
        """
        results = []
        batch_size = self.config.batch_size
        
        for i in range(0, len(tracks), batch_size):
            batch = tracks[i:i + batch_size]
            batch_prompt = self._create_batch_prompt(batch)
            
            try:
                response = self.model.generate_content(
                    batch_prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.7,
                        max_output_tokens=2000
                    )
                )
                
                batch_analyses = self._parse_batch_response(response.text, len(batch))
                
                for track, analysis in zip(batch, batch_analyses):
                    result = track.copy()
                    result['ai_analysis'] = analysis
                    result['provider'] = 'gemini'
                    result['model'] = self.config.model
                    result['timestamp'] = datetime.now().isoformat()
                    results.append(result)
                    
            except Exception as e:
                logger.error(f"Error in batch analysis: {e}")
                for track in batch:
                    result = track.copy()
                    result['ai_analysis'] = None
                    result['error'] = str(e)
                    results.append(result)
        
        return results
    
    def test_connection(self) -> bool:
        """Test Gemini API connection.
        
        Returns:
            True if connection successful
        """
        try:
            response = self.model.generate_content("Respond with OK")
            return 'OK' in response.text
        except Exception as e:
            logger.error(f"Gemini connection test failed: {e}")
            return False
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get Gemini provider information.
        
        Returns:
            Provider information dictionary
        """
        return {
            'name': 'Gemini (Google)',
            'version': '1.0',
            'model': self.config.model,
            'capabilities': [
                'track_analysis',
                'batch_analysis',
                'playlist_analysis',
                'genre_detection',
                'mood_analysis',
                'cultural_context',
                'multi_language_support'
            ],
            'limits': {
                'max_batch_size': self.config.batch_size,
                'timeout': self.config.timeout,
                'rate_limit': '60 requests per minute'
            },
            'available': self.test_connection()
        }
    
    def _create_analysis_prompt(self, track_metadata: Dict[str, Any]) -> str:
        """Create analysis prompt for single track."""
        title = track_metadata.get('title', 'Unknown')
        artist = track_metadata.get('artist', 'Unknown')
        album = track_metadata.get('album', 'Unknown')
        duration = track_metadata.get('duration', 0)
        
        prompt = f"""As a music analysis expert, analyze this track:

Title: {title}
Artist: {artist}
Album: {album}
Duration: {self.format_duration(duration) if duration else 'Unknown'}

Provide a detailed analysis in JSON format with these fields:
{{
    "genre": "primary genre",
    "sub_genres": ["list", "of", "sub-genres"],
    "mood": "overall mood",
    "energy_level": 7,  // 1-10 scale
    "bpm": 120,  // estimated beats per minute
    "key": "C major",
    "themes": ["list", "of", "themes"],
    "similar_artists": ["artist1", "artist2"],
    "era": "2020s",
    "contexts": ["workout", "study", "party"]
}}

Be specific and accurate based on the artist and title."""
        
        return prompt
    
    def _create_batch_prompt(self, tracks: List[Dict[str, Any]]) -> str:
        """Create analysis prompt for batch of tracks."""
        prompt = "Analyze these music tracks and provide JSON array output:\n\n"
        
        for i, track in enumerate(tracks, 1):
            prompt += f"Track {i}:\n"
            prompt += f"Title: {track.get('title', 'Unknown')}\n"
            prompt += f"Artist: {track.get('artist', 'Unknown')}\n"
            prompt += f"Album: {track.get('album', 'Unknown')}\n\n"
        
        prompt += """Return a JSON array where each element contains:
{{"genre": "...", "mood": "...", "bpm": 120, "key": "...", "energy_level": 5}}"""
        
        return prompt
    
    def _parse_response(self, content: str) -> Dict[str, Any]:
        """Parse Gemini response."""
        try:
            # Clean up markdown code blocks if present
            content = content.replace('```json', '').replace('```', '')
            
            # Try to extract JSON
            if '{' in content:
                start = content.index('{')
                end = content.rindex('}') + 1
                json_str = content[start:end]
                return json.loads(json_str)
        except Exception as e:
            logger.warning(f"Failed to parse Gemini response as JSON: {e}")
        
        # Fallback parsing
        return {
            'genre': 'Unknown',
            'mood': 'Unknown',
            'raw_analysis': content
        }
    
    def _parse_batch_response(self, content: str, expected_count: int) -> List[Dict[str, Any]]:
        """Parse Gemini batch response."""
        try:
            # Clean up markdown code blocks
            content = content.replace('```json', '').replace('```', '')
            
            if '[' in content:
                start = content.index('[')
                end = content.rindex(']') + 1
                json_str = content[start:end]
                analyses = json.loads(json_str)
                
                # Ensure correct count
                while len(analyses) < expected_count:
                    analyses.append({'genre': 'Unknown', 'mood': 'Unknown'})
                
                return analyses[:expected_count]
        except Exception as e:
            logger.warning(f"Failed to parse batch response: {e}")
        
        return [{'genre': 'Unknown', 'mood': 'Unknown'} for _ in range(expected_count)]