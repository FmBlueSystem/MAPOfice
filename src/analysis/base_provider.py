"""Base provider interface for all LLM providers.

This module defines the abstract base class that all LLM providers must implement,
ensuring consistent behavior across different provider implementations.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ProviderConfig:
    """Configuration for LLM providers."""
    api_key: Optional[str] = None
    api_key_env: Optional[str] = None
    base_url: Optional[str] = None
    model: Optional[str] = None
    timeout: int = 30
    max_retries: int = 3
    batch_size: int = 10


class BaseLLMProvider(ABC):
    """Abstract base class for all LLM providers.
    
    This class defines the interface that all LLM providers must implement
    to ensure consistent behavior across different implementations.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the provider with configuration.
        
        Args:
            config: Provider-specific configuration dictionary
        """
        self.config = ProviderConfig(**config) if isinstance(config, dict) else config
        self._validate_config()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    @abstractmethod
    def _validate_config(self):
        """Validate provider-specific configuration.
        
        Raises:
            ValueError: If configuration is invalid
        """
        pass
    
    @abstractmethod
    def analyze_track(self, track_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a single track and return enriched metadata.
        
        Args:
            track_metadata: Dictionary containing track information
                Expected keys: title, artist, album, duration, file_path
        
        Returns:
            Dictionary with enriched metadata including:
                - Original metadata
                - Genre classification
                - Mood analysis
                - Key and BPM detection
                - Contextual information
        """
        pass
    
    @abstractmethod
    def batch_analyze(self, tracks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze multiple tracks efficiently.
        
        Args:
            tracks: List of track metadata dictionaries
        
        Returns:
            List of enriched metadata dictionaries
        """
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """Test if provider is accessible and configured correctly.
        
        Returns:
            True if connection successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about the provider.
        
        Returns:
            Dictionary containing:
                - name: Provider name
                - version: API version
                - capabilities: List of supported features
                - limits: Rate limits and constraints
        """
        pass
    
    def analyze_playlist(self, playlist_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze an entire playlist and provide cohesion insights.
        
        Args:
            playlist_metadata: Dictionary containing playlist information
                Expected keys: name, description, tracks
        
        Returns:
            Dictionary with playlist analysis including:
                - Overall mood and energy flow
                - Genre consistency
                - Transition quality between tracks
                - Recommendations for improvement
        """
        # Default implementation - can be overridden by specific providers
        if 'tracks' not in playlist_metadata:
            raise ValueError("Playlist metadata must contain 'tracks' key")
        
        analyzed_tracks = self.batch_analyze(playlist_metadata['tracks'])
        
        return {
            'name': playlist_metadata.get('name', 'Untitled Playlist'),
            'description': playlist_metadata.get('description', ''),
            'tracks': analyzed_tracks,
            'analysis': {
                'total_tracks': len(analyzed_tracks),
                'provider': self.__class__.__name__,
                'timestamp': None  # To be filled by implementation
            }
        }
    
    def get_rate_limit_status(self) -> Dict[str, Any]:
        """Get current rate limit status.
        
        Returns:
            Dictionary with rate limit information
        """
        return {
            'requests_remaining': None,
            'reset_time': None,
            'limit': None
        }
    
    @staticmethod
    def parse_duration(duration_str: str) -> float:
        """Parse duration string to seconds.
        
        Args:
            duration_str: Duration in format "MM:SS" or seconds
        
        Returns:
            Duration in seconds as float
        """
        if ':' in duration_str:
            parts = duration_str.split(':')
            if len(parts) == 2:
                return float(parts[0]) * 60 + float(parts[1])
            elif len(parts) == 3:
                return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
        return float(duration_str)
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """Format duration in seconds to string.
        
        Args:
            seconds: Duration in seconds
        
        Returns:
            Formatted duration string "MM:SS"
        """
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"