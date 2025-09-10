"""Base theme structure for Music Analyzer Pro UI."""

from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseTheme(ABC):
    """Base class for UI themes."""
    
    @property
    @abstractmethod
    def colors(self) -> Dict[str, str]:
        """Color palette for the theme."""
        pass
    
    @property 
    @abstractmethod
    def name(self) -> str:
        """Theme name."""
        pass
    
    @abstractmethod
    def get_stylesheet(self) -> str:
        """Get complete stylesheet for the theme."""
        pass
    
    def get_color(self, color_name: str) -> str:
        """Get a color by name from the theme palette."""
        return self.colors.get(color_name, '#ffffff')