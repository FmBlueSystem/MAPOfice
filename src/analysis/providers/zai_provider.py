"""ZAI Provider implementation.

This module implements the ZAI LLM provider using the unified provider interface.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
import requests
from datetime import datetime

from ..base_provider import BaseLLMProvider, ProviderConfig
from ..provider_factory import register_provider

logger = logging.getLogger(__name__)


@register_provider("zai")
class ZAIProvider(BaseLLMProvider):
    """ZAI LLM Provider implementation."""
    
    DEFAULT_MODEL = "gpt-4"
    DEFAULT_BASE_URL = "https://api.zai.com/v1"
    
    def _validate_config(self):
        """Validate ZAI-specific configuration."""
        # Check for API key
        if not self.config.api_key and self.config.api_key_env:
            api_key = os.getenv(self.config.api_key_env)
            if not api_key:
                raise ValueError(f"ZAI API key not found in environment variable: {self.config.api_key_env}")
            self.config.api_key = api_key
        
        if not self.config.api_key:
            raise ValueError("ZAI API key is required")
        
        # Set defaults
        if not self.config.model:
            self.config.model = self.DEFAULT_MODEL
        
        if not self.config.base_url:
            self.config.base_url = self.DEFAULT_BASE_URL
    
    def analyze_track(self, track_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a single track using ZAI.
        
        Args:
            track_metadata: Track information
        
        Returns:
            Enriched metadata with AI analysis
        """
        # Prepare prompt
        prompt = self._create_analysis_prompt(track_metadata)
        
        # Make API request
        try:
            response = self._make_api_request(prompt)
            
            # Parse response
            analysis = self._parse_response(response)
            
            # Merge with original metadata
            result = track_metadata.copy()
            result['ai_analysis'] = analysis
            result['provider'] = 'zai'
            result['model'] = self.config.model
            result['timestamp'] = datetime.now().isoformat()
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing track with ZAI: {e}")
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
            
            # Create batch prompt
            batch_prompt = self._create_batch_prompt(batch)
            
            try:
                response = self._make_api_request(batch_prompt)
                batch_analyses = self._parse_batch_response(response, len(batch))
                
                # Merge analyses with tracks
                for track, analysis in zip(batch, batch_analyses):
                    result = track.copy()
                    result['ai_analysis'] = analysis
                    result['provider'] = 'zai'
                    result['model'] = self.config.model
                    result['timestamp'] = datetime.now().isoformat()
                    results.append(result)
                    
            except Exception as e:
                logger.error(f"Error in batch analysis: {e}")
                # Add tracks without analysis
                for track in batch:
                    result = track.copy()
                    result['ai_analysis'] = None
                    result['error'] = str(e)
                    results.append(result)
        
        return results
    
    def test_connection(self) -> bool:
        """Test ZAI API connection.
        
        Returns:
            True if connection successful
        """
        try:
            # Simple test request
            test_prompt = "Respond with 'OK' if you receive this."
            response = self._make_api_request(test_prompt, max_tokens=10)
            return 'OK' in str(response) or 'ok' in str(response).lower()
        except Exception as e:
            logger.error(f"ZAI connection test failed: {e}")
            return False
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get ZAI provider information.
        
        Returns:
            Provider information dictionary
        """
        return {
            'name': 'ZAI',
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
                'bpm_estimation'
            ],
            'limits': {
                'max_batch_size': self.config.batch_size,
                'timeout': self.config.timeout,
                'max_retries': self.config.max_retries
            },
            'available': self.test_connection()
        }
    
    def _create_analysis_prompt(self, track_metadata: Dict[str, Any]) -> str:
        """Create analysis prompt for single track."""
        title = track_metadata.get('title', 'Unknown')
        artist = track_metadata.get('artist', 'Unknown')
        album = track_metadata.get('album', 'Unknown')
        duration = track_metadata.get('duration', 0)
        
        prompt = f"""Analyze this music track and provide detailed metadata:

Title: {title}
Artist: {artist}
Album: {album}
Duration: {self.format_duration(duration) if duration else 'Unknown'}

Please provide:
1. Genre (primary and sub-genres if applicable)
2. Mood/Energy level (calm, energetic, melancholic, uplifting, etc.)
3. Estimated BPM
4. Musical key
5. Themes or lyrical content (if known)
6. Similar artists or influences
7. Era/Year estimate
8. Suitable contexts (workout, study, party, relaxation, etc.)

Format the response as JSON with these keys:
genre, sub_genres, mood, energy_level, bpm, key, themes, similar_artists, era, contexts"""
        
        return prompt
    
    def _create_batch_prompt(self, tracks: List[Dict[str, Any]]) -> str:
        """Create analysis prompt for batch of tracks."""
        prompt = "Analyze these music tracks and provide metadata for each:\n\n"
        
        for i, track in enumerate(tracks, 1):
            prompt += f"Track {i}:\n"
            prompt += f"  Title: {track.get('title', 'Unknown')}\n"
            prompt += f"  Artist: {track.get('artist', 'Unknown')}\n"
            prompt += f"  Album: {track.get('album', 'Unknown')}\n"
            prompt += f"  Duration: {self.format_duration(track.get('duration', 0))}\n\n"
        
        prompt += """For each track, provide:
- Genre and sub-genres
- Mood and energy level
- BPM and key
- Themes and similar artists

Format as a JSON array with one object per track."""
        
        return prompt
    
    def _make_api_request(self, prompt: str, max_tokens: Optional[int] = None) -> Dict[str, Any]:
        """Make request to ZAI API."""
        headers = {
            'Authorization': f'Bearer {self.config.api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': self.config.model,
            'messages': [
                {'role': 'system', 'content': 'You are a music analysis expert.'},
                {'role': 'user', 'content': prompt}
            ],
            'temperature': 0.7,
            'max_tokens': max_tokens or 500
        }
        
        url = f"{self.config.base_url}/chat/completions"
        
        response = requests.post(
            url,
            headers=headers,
            json=data,
            timeout=self.config.timeout
        )
        
        response.raise_for_status()
        return response.json()
    
    def _parse_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Parse ZAI API response for single track."""
        try:
            # Extract content from response
            content = response['choices'][0]['message']['content']
            
            # Try to parse as JSON
            if '{' in content and '}' in content:
                # Extract JSON portion
                start = content.index('{')
                end = content.rindex('}') + 1
                json_str = content[start:end]
                return json.loads(json_str)
            else:
                # Parse structured text response
                return self._parse_text_response(content)
                
        except (KeyError, IndexError, json.JSONDecodeError) as e:
            logger.warning(f"Failed to parse ZAI response: {e}")
            return {
                'genre': 'Unknown',
                'mood': 'Unknown',
                'error': 'Failed to parse response'
            }
    
    def _parse_batch_response(self, response: Dict[str, Any], expected_count: int) -> List[Dict[str, Any]]:
        """Parse ZAI API response for batch of tracks."""
        try:
            content = response['choices'][0]['message']['content']
            
            # Try to parse as JSON array
            if '[' in content and ']' in content:
                start = content.index('[')
                end = content.rindex(']') + 1
                json_str = content[start:end]
                analyses = json.loads(json_str)
                
                # Ensure we have the right number of analyses
                while len(analyses) < expected_count:
                    analyses.append({'genre': 'Unknown', 'mood': 'Unknown'})
                
                return analyses[:expected_count]
            else:
                # Fallback to empty analyses
                return [{'genre': 'Unknown', 'mood': 'Unknown'} for _ in range(expected_count)]
                
        except Exception as e:
            logger.warning(f"Failed to parse batch response: {e}")
            return [{'genre': 'Unknown', 'mood': 'Unknown'} for _ in range(expected_count)]
    
    def _parse_text_response(self, content: str) -> Dict[str, Any]:
        """Parse text response into structured data."""
        result = {}
        
        # Simple keyword extraction
        lines = content.lower().split('\n')
        for line in lines:
            if 'genre' in line:
                result['genre'] = line.split(':')[-1].strip()
            elif 'mood' in line:
                result['mood'] = line.split(':')[-1].strip()
            elif 'bpm' in line:
                try:
                    bpm_str = line.split(':')[-1].strip()
                    result['bpm'] = int(''.join(filter(str.isdigit, bpm_str)))
                except:
                    pass
            elif 'key' in line:
                result['key'] = line.split(':')[-1].strip()
        
        return result if result else {'genre': 'Unknown', 'mood': 'Unknown'}