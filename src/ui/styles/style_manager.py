"""Style management system for Music Analyzer Pro."""

from typing import Optional
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtCore import QObject

from .themes.dark_theme import DarkTheme
from .themes.compact_theme import CompactTheme
from .themes.audio_pro_theme import AudioProTheme
from .themes.base_theme import BaseTheme


class StyleManager(QObject):
    """Manages UI styling and themes for the application.
    
    The StyleManager provides a centralized system for applying consistent
    styling across the Music Analyzer Pro interface. It supports multiple
    themes and handles dynamic theme switching.
    
    Features:
        - Multiple theme support (currently: dark theme)
        - Application-wide or widget-specific styling
        - Dynamic color retrieval from active theme
        - Easy theme switching capability
        
    Example:
        style_manager = StyleManager()
        style_manager.set_theme('dark')
        style_manager.apply_theme_to_app(app)
        
        # Get colors from active theme
        primary_color = style_manager.get_color('primary')
    """
    
    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._current_theme: Optional[BaseTheme] = None
        self._available_themes = {
            'dark': DarkTheme(),
            'compact': CompactTheme(),
            'audio_pro': AudioProTheme(),
        }
        
    def set_theme(self, theme_name: str = 'dark') -> bool:
        """Set the current theme by name.
        
        Args:
            theme_name: Name of the theme to apply
            
        Returns:
            True if theme was applied successfully, False otherwise
        """
        if theme_name not in self._available_themes:
            return False
            
        self._current_theme = self._available_themes[theme_name]
        return True
        
    def apply_theme_to_app(self, app: QApplication) -> None:
        """Apply current theme to the entire application.
        
        Args:
            app: QApplication instance to style
        """
        if self._current_theme:
            stylesheet = self._current_theme.get_stylesheet()
            app.setStyleSheet(stylesheet)
            
    def apply_theme_to_widget(self, widget: QWidget) -> None:
        """Apply current theme to a specific widget.
        
        Args:
            widget: Widget to apply styling to
        """
        if self._current_theme:
            stylesheet = self._current_theme.get_stylesheet()
            widget.setStyleSheet(stylesheet)
            
    def get_color(self, color_name: str) -> str:
        """Get a color value from the current theme.
        
        Args:
            color_name: Name of the color to retrieve
            
        Returns:
            Color value as hex string
        """
        if self._current_theme:
            return self._current_theme.get_color(color_name)
        return '#ffffff'
        
    @property
    def current_theme(self) -> Optional[BaseTheme]:
        """Get the currently active theme."""
        return self._current_theme
        
    @property
    def available_themes(self) -> list[str]:
        """Get list of available theme names."""
        return list(self._available_themes.keys())