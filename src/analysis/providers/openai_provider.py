"""OpenAI Provider implementation.

This module implements the OpenAI LLM provider using the unified provider interface.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
import openai
from datetime import datetime

from ..base_provider import BaseLLMProvider, ProviderConfig
from ..provider_factory import register_provider

logger = logging.getLogger(__name__)


@register_provider("openai")
class OpenAIProvider(BaseLLMProvider):
    """OpenAI LLM Provider implementation."""
    
    DEFAULT_MODEL = "gpt-4-turbo-preview"
    DEFAULT_BASE_URL = "https://api.openai.com/v1"
    
    def _validate_config(self):
        """Validate OpenAI-specific configuration."""
        # Check for API key
        if not self.config.api_key and self.config.api_key_env:
            api_key = os.getenv(self.config.api_key_env or 'OPENAI_API_KEY')
            if not api_key:
                raise ValueError(f"OpenAI API key not found in environment variable: {self.config.api_key_env or 'OPENAI_API_KEY'}")
            self.config.api_key = api_key
        
        if not self.config.api_key:
            raise ValueError("OpenAI API key is required")
        
        # Set defaults
        if not self.config.model:
            self.config.model = self.DEFAULT_MODEL
        
        if not self.config.base_url:
            self.config.base_url = self.DEFAULT_BASE_URL
        
        # Initialize client
        self.client = openai.OpenAI(
            api_key=self.config.api_key,
            base_url=self.config.base_url
        )
    
    def analyze_track(self, track_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a single track using OpenAI.
        
        Args:
            track_metadata: Track information
        
        Returns:
            Enriched metadata with AI analysis
        """
        prompt = self._create_analysis_prompt(track_metadata)
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": "You are a professional music analyst with deep knowledge of all music genres, styles, and history."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000,
                response_format={"type": "json_object"}
            )
            
            # Parse response
            analysis = self._parse_response(response.choices[0].message.content)
            
            # Merge with original metadata
            result = track_metadata.copy()
            result['ai_analysis'] = analysis
            result['provider'] = 'openai'
            result['model'] = self.config.model
            result['timestamp'] = datetime.now().isoformat()
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing track with OpenAI: {e}")
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
                response = self.client.chat.completions.create(
                    model=self.config.model,
                    messages=[
                        {"role": "system", "content": "You are a music analyst. Analyze multiple tracks efficiently."},
                        {"role": "user", "content": batch_prompt}
                    ],
                    temperature=0.7,
                    max_tokens=2000
                )
                
                batch_analyses = self._parse_batch_response(response.choices[0].message.content, len(batch))
                
                for track, analysis in zip(batch, batch_analyses):
                    result = track.copy()
                    result['ai_analysis'] = analysis
                    result['provider'] = 'openai'
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
        """Test OpenAI API connection.
        
        Returns:
            True if connection successful
        """
        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "user", "content": "Respond with OK"}
                ],
                max_tokens=10
            )
            return 'OK' in response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI connection test failed: {e}")
            return False
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get OpenAI provider information.
        
        Returns:
            Provider information dictionary
        """
        return {
            'name': 'OpenAI',
            'version': '1.0',
            'model': self.config.model,
            'base_url': self.config.base_url,
            'capabilities': [
                'track_analysis',
                'batch_analysis',
                'playlist_analysis',
                'genre_detection',
                'mood_analysis',
                'key_detection',
                'bpm_estimation',
                'structured_output',
                'function_calling'
            ],
            'limits': {
                'max_batch_size': self.config.batch_size,
                'timeout': self.config.timeout,
                'max_tokens': 4096,
                'rate_limit': 'Varies by tier'
            },
            'available': self.test_connection()
        }
    
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """Get current rate limit status from headers."""
        # OpenAI provides rate limit info in response headers
        # This would need to be captured from actual API responses
        return {
            'requests_remaining': None,
            'reset_time': None,
            'limit': None,
            'note': 'Rate limit info available in response headers'
        }
    
    def _create_analysis_prompt(self, track_metadata: Dict[str, Any]) -> str:
        """Create analysis prompt for single track."""
        title = track_metadata.get('title', 'Unknown')
        artist = track_metadata.get('artist', 'Unknown')
        album = track_metadata.get('album', 'Unknown')
        duration = track_metadata.get('duration', 0)
        
        prompt = f"""Analyze this music track and provide comprehensive metadata:

Track Information:
- Title: {title}
- Artist: {artist}
- Album: {album}
- Duration: {self.format_duration(duration) if duration else 'Unknown'}

Provide a detailed JSON response with the following structure:
{{
    "genre": "primary genre classification",
    "sub_genres": ["sub-genre 1", "sub-genre 2"],
    "mood": "overall emotional mood",
    "energy_level": 7,  // 1-10 scale
    "valence": 0.6,  // 0-1 scale (sad to happy)
    "danceability": 0.7,  // 0-1 scale
    "bpm": 120,  // estimated beats per minute
    "key": "C major",  // musical key
    "time_signature": "4/4",
    "themes": ["theme 1", "theme 2"],
    "instruments": ["guitar", "drums", "bass"],
    "vocal_style": "description of vocal style",
    "production_style": "production characteristics",
    "similar_artists": ["artist 1", "artist 2", "artist 3"],
    "influences": ["influence 1", "influence 2"],
    "era": "2020s",  // decade or era
    "contexts": ["workout", "study", "party", "relaxation"],
    "tags": ["indie", "alternative", "melodic"]
}}

Ensure accuracy based on the actual artist and track information provided."""
        
        return prompt
    
    def _create_batch_prompt(self, tracks: List[Dict[str, Any]]) -> str:
        """Create analysis prompt for batch of tracks."""
        prompt = "Analyze the following music tracks and provide metadata for each:\n\n"
        
        for i, track in enumerate(tracks, 1):
            prompt += f"Track {i}:\n"
            prompt += f"  Title: {track.get('title', 'Unknown')}\n"
            prompt += f"  Artist: {track.get('artist', 'Unknown')}\n"
            prompt += f"  Album: {track.get('album', 'Unknown')}\n"
            prompt += f"  Duration: {self.format_duration(track.get('duration', 0))}\n\n"
        
        prompt += """Return a JSON array with one object per track. Each object should contain:
- genre (string)
- mood (string)
- energy_level (1-10)
- bpm (number)
- key (string)
- similar_artists (array of strings)
- contexts (array of suitable listening contexts)

Format: [{"genre": "...", "mood": "...", ...}, ...]"""
        
        return prompt
    
    def _parse_response(self, content: str) -> Dict[str, Any]:
        """Parse OpenAI response."""
        try:
            # OpenAI with JSON mode should return valid JSON
            return json.loads(content)
        except json.JSONDecodeError:
            # Try to extract JSON from text
            try:
                if '{' in content:
                    start = content.index('{')
                    end = content.rindex('}') + 1
                    json_str = content[start:end]
                    return json.loads(json_str)
            except:
                pass
        
        # Fallback
        return {
            'genre': 'Unknown',
            'mood': 'Unknown',
            'raw_response': content
        }
    
    def _parse_batch_response(self, content: str, expected_count: int) -> List[Dict[str, Any]]:
        """Parse OpenAI batch response."""
        try:
            # Try to parse as JSON array
            if content.strip().startswith('['):
                analyses = json.loads(content)
            else:
                # Extract JSON array from text
                start = content.index('[')
                end = content.rindex(']') + 1
                json_str = content[start:end]
                analyses = json.loads(json_str)
            
            # Ensure correct count
            while len(analyses) < expected_count:
                analyses.append({
                    'genre': 'Unknown',
                    'mood': 'Unknown',
                    'error': 'Missing analysis'
                })
            
            return analyses[:expected_count]
            
        except Exception as e:
            logger.warning(f"Failed to parse batch response: {e}")
            return [{'genre': 'Unknown', 'mood': 'Unknown', 'error': str(e)} 
                   for _ in range(expected_count)]