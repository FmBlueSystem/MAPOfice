"""Responsive layout manager for adaptive UI sizing."""

from typing import Literal, Callable, Optional
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QWidget

LayoutMode = Literal['compact', 'medium', 'large']


class ResponsiveLayoutManager(QObject):
    """Manages responsive layout switching based on window size.
    
    Provides breakpoint-based layout switching optimized for different
    screen sizes, with special focus on MacBook Pro 13" optimization.
    
    Breakpoints:
        - compact (≤1300px): MacBook Pro 13", optimized for vertical space
        - medium (1301-1600px): MacBook Pro 15/16", balanced layout
        - large (>1600px): External monitors, full-featured layout
        
    Signals:
        layout_mode_changed: Emitted when layout mode changes
        
    Example:
        manager = ResponsiveLayoutManager(main_window)
        manager.layout_mode_changed.connect(self.handle_layout_change)
        manager.update_layout_mode(window.width(), window.height())
    """
    
    layout_mode_changed = pyqtSignal(str)  # LayoutMode as string
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._current_mode: LayoutMode = 'large'
        self._breakpoints = {
            'compact': (0, 1300),
            'medium': (1301, 1600),
            'large': (1601, float('inf'))
        }
        
    @property
    def current_mode(self) -> LayoutMode:
        """Get the current layout mode."""
        return self._current_mode
        
    def detect_layout_mode(self, width: int, height: int = 0) -> LayoutMode:
        """Detect appropriate layout mode based on dimensions.
        
        Args:
            width: Window width in pixels
            height: Window height in pixels (unused for now, future expansion)
            
        Returns:
            Appropriate layout mode for the given dimensions
        """
        for mode, (min_width, max_width) in self._breakpoints.items():
            if min_width <= width <= max_width:
                return mode
        return 'large'  # fallback
        
    def update_layout_mode(self, width: int, height: int = 0) -> bool:
        """Update layout mode if window size requires change.
        
        Args:
            width: Current window width
            height: Current window height
            
        Returns:
            True if layout mode changed, False otherwise
        """
        new_mode = self.detect_layout_mode(width, height)
        if new_mode != self._current_mode:
            old_mode = self._current_mode
            self._current_mode = new_mode
            self.layout_mode_changed.emit(new_mode)
            return True
        return False
        
    def get_layout_config(self, mode: Optional[LayoutMode] = None) -> dict:
        """Get layout configuration for specified mode.
        
        Args:
            mode: Layout mode to get config for, defaults to current mode
            
        Returns:
            Dictionary with layout configuration parameters
        """
        mode = mode or self._current_mode
        
        configs = {
            'compact': {
                'window_size': (1200, 650),
                'window_min_size': (1000, 550),
                'main_spacing': 6,
                'section_spacing': 4,
                'margins': 8,
                'font_size': 12,
                'button_height': 28,
                'progress_height': 16,
                'use_horizontal_layout': True,
                'show_icons': True,
                'compact_headers': True,
            },
            'medium': {
                'window_size': (1300, 700),
                'window_min_size': (1200, 600),
                'main_spacing': 10,
                'section_spacing': 8,
                'margins': 12,
                'font_size': 13,
                'button_height': 32,
                'progress_height': 20,
                'use_horizontal_layout': False,
                'show_icons': True,
                'compact_headers': False,
            },
            'large': {
                'window_size': (1400, 800),
                'window_min_size': (1300, 700),
                'main_spacing': 15,
                'section_spacing': 12,
                'margins': 15,
                'font_size': 13,
                'button_height': 36,
                'progress_height': 24,
                'use_horizontal_layout': False,
                'show_icons': False,
                'compact_headers': False,
            }
        }
        
        return configs.get(mode, configs['large'])
        
    def get_optimal_window_size(self, mode: Optional[LayoutMode] = None) -> tuple[int, int]:
        """Get optimal window size for specified mode.
        
        Args:
            mode: Layout mode, defaults to current mode
            
        Returns:
            (width, height) tuple for optimal window size
        """
        config = self.get_layout_config(mode)
        return config['window_size']
        
    def get_minimum_window_size(self, mode: Optional[LayoutMode] = None) -> tuple[int, int]:
        """Get minimum window size for specified mode.
        
        Args:
            mode: Layout mode, defaults to current mode
            
        Returns:
            (width, height) tuple for minimum window size
        """
        config = self.get_layout_config(mode)
        return config['window_min_size']