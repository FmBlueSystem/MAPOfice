"""Theme system for Music Analyzer Pro UI.

This module provides theme implementations for the application's styling system.
Themes define color palettes and complete stylesheets for consistent UI appearance.

Available Themes:
    - AudioProTheme: Professional audio-themed color scheme (default)
    - DarkTheme: Professional dark theme with modern color palette

Example:
    from src.ui.styles.themes.audio_pro_theme import AudioProTheme
    
    theme = AudioProTheme()
    stylesheet = theme.get_stylesheet()
    color = theme.get_color('primary')
"""

from .audio_pro_theme import AudioProTheme
from .dark_theme import DarkTheme
from .base_theme import BaseTheme

__all__ = ['AudioProTheme', 'DarkTheme', 'BaseTheme']