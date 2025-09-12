"""Claude (Anthropic) Provider implementation.

This module implements the Claude LLM provider using the unified provider interface.
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional
import anthropic
from datetime import datetime

from ..base_provider import BaseLLMProvider, ProviderConfig
from ..provider_factory import register_provider

logger = logging.getLogger(__name__)


@register_provider("claude")
class ClaudeProvider(BaseLLMProvider):
    """Claude (Anthropic) LLM Provider implementation."""
    
    DEFAULT_MODEL = "claude-3-haiku-20240307"
    
    def _validate_config(self):
        """Validate Claude-specific configuration."""
        # Check for API key
        if not self.config.api_key and self.config.api_key_env:
            api_key = os.getenv(self.config.api_key_env or 'ANTHROPIC_API_KEY')
            if not api_key:
                raise ValueError(f"Anthropic API key not found in environment variable: {self.config.api_key_env or 'ANTHROPIC_API_KEY'}")
            self.config.api_key = api_key
        
        if not self.config.api_key:
            raise ValueError("Anthropic API key is required")
        
        # Set defaults
        if not self.config.model:
            self.config.model = self.DEFAULT_MODEL
        
        # Initialize client
        self.client = anthropic.Anthropic(api_key=self.config.api_key)
    
    def analyze_track(self, track_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a single track using Claude.
        
        Args:
            track_metadata: Track information
        
        Returns:
            Enriched metadata with AI analysis
        """
        prompt = self._create_analysis_prompt(track_metadata)
        
        try:
            response = self.client.messages.create(
                model=self.config.model,
                max_tokens=1000,
                temperature=0.7,
                system="You are a music analysis expert. Provide detailed, accurate metadata for music tracks.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Parse response
            analysis = self._parse_response(response.content[0].text)
            
            # Merge with original metadata
            result = track_metadata.copy()
            result['ai_analysis'] = analysis
            result['provider'] = 'claude'
            result['model'] = self.config.model
            result['timestamp'] = datetime.now().isoformat()
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing track with Claude: {e}")
            raise
    
    def batch_analyze(self, tracks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze multiple tracks efficiently.
        
        Args:
            tracks: List of track metadata
        
        Returns:
            List of enriched metadata
        """
        results = []
        batch_size = min(self.config.batch_size, 5)  # Claude works better with smaller batches
        
        for i in range(0, len(tracks), batch_size):
            batch = tracks[i:i + batch_size]
            batch_prompt = self._create_batch_prompt(batch)
            
            try:
                response = self.client.messages.create(
                    model=self.config.model,
                    max_tokens=2000,
                    temperature=0.7,
                    system="You are a music analysis expert. Analyze multiple tracks and provide detailed metadata.",
                    messages=[
                        {"role": "user", "content": batch_prompt}
                    ]
                )
                
                batch_analyses = self._parse_batch_response(response.content[0].text, len(batch))
                
                for track, analysis in zip(batch, batch_analyses):
                    result = track.copy()
                    result['ai_analysis'] = analysis
                    result['provider'] = 'claude'
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
        """Test Claude API connection.
        
        Returns:
            True if connection successful
        """
        try:
            response = self.client.messages.create(
                model=self.config.model,
                max_tokens=10,
                messages=[
                    {"role": "user", "content": "Respond with OK"}
                ]
            )
            return 'OK' in response.content[0].text
        except Exception as e:
            logger.error(f"Claude connection test failed: {e}")
            return False
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get Claude provider information.
        
        Returns:
            Provider information dictionary
        """
        return {
            'name': 'Claude (Anthropic)',
            'version': '1.0',
            'model': self.config.model,
            'capabilities': [
                'track_analysis',
                'batch_analysis',
                'playlist_analysis',
                'genre_detection',
                'mood_analysis',
                'contextual_understanding',
                'lyrical_analysis'
            ],
            'limits': {
                'max_batch_size': 5,
                'timeout': self.config.timeout,
                'max_tokens_per_request': 4096
            },
            'available': self.test_connection()
        }
    
    def _create_analysis_prompt(self, track_metadata: Dict[str, Any]) -> str:
        """Create analysis prompt for single track."""
        title = track_metadata.get('title', 'Unknown')
        artist = track_metadata.get('artist', 'Unknown')
        album = track_metadata.get('album', 'Unknown')
        duration = track_metadata.get('duration', 0)
        
        prompt = f"""Analyze this music track:

Title: {title}
Artist: {artist}
Album: {album}
Duration: {self.format_duration(duration) if duration else 'Unknown'}

Provide a JSON response with:
- genre: Primary genre
- sub_genres: List of sub-genres
- mood: Overall mood
- energy_level: Energy level (1-10)
- bpm: Estimated BPM
- key: Musical key
- themes: List of themes
- similar_artists: List of similar artists
- era: Estimated era/decade
- contexts: Suitable listening contexts

Be accurate and specific in your analysis."""
        
        return prompt
    
    def _create_batch_prompt(self, tracks: List[Dict[str, Any]]) -> str:
        """Create analysis prompt for batch of tracks."""
        prompt = "Analyze these music tracks:\n\n"
        
        for i, track in enumerate(tracks, 1):
            prompt += f"Track {i}:\n"
            prompt += f"- Title: {track.get('title', 'Unknown')}\n"
            prompt += f"- Artist: {track.get('artist', 'Unknown')}\n"
            prompt += f"- Album: {track.get('album', 'Unknown')}\n\n"
        
        prompt += "Return a JSON array with analysis for each track including genre, mood, BPM, and key."
        
        return prompt
    
    def _parse_response(self, content: str) -> Dict[str, Any]:
        """Parse Claude response."""
        try:
            # Try to extract JSON
            if '{' in content:
                start = content.index('{')
                end = content.rindex('}') + 1
                json_str = content[start:end]
                return json.loads(json_str)
        except:
            pass
        
        # Fallback parsing
        return {
            'genre': 'Unknown',
            'mood': 'Unknown',
            'analysis': content
        }
    
    def _parse_batch_response(self, content: str, expected_count: int) -> List[Dict[str, Any]]:
        """Parse Claude batch response."""
        try:
            if '[' in content:
                start = content.index('[')
                end = content.rindex(']') + 1
                json_str = content[start:end]
                analyses = json.loads(json_str)
                
                while len(analyses) < expected_count:
                    analyses.append({'genre': 'Unknown', 'mood': 'Unknown'})
                
                return analyses[:expected_count]
        except:
            pass
        
        return [{'genre': 'Unknown', 'mood': 'Unknown'} for _ in range(expected_count)]