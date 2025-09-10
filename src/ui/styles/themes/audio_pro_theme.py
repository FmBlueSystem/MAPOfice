"""Professional Audio Theme for Music Analyzer Pro.

This theme uses a professional color palette inspired by audio equipment
and digital audio workstations, providing excellent readability and
visual hierarchy for music analysis applications.

POML Quality Gates:
- WCAG 2.1 AA contrast compliance
- Consistent color system across all components
- Clear visual hierarchy and state feedback
- Professional appearance suitable for audio analysis
"""

from .base_theme import BaseTheme


class AudioProTheme(BaseTheme):
    """Professional audio-themed styling for Music Analyzer Pro.
    
    Color Palette:
    - Primary: Deep audio blue (#1e3a8a) - Professional, trustworthy
    - Secondary: Warm gold (#f59e0b) - Highlights, active states
    - Background: Cool gray (#f8fafc) - Clean, easy on eyes
    - Surface: Pure white (#ffffff) - Content areas
    - Text: Dark slate (#1e293b) - Excellent readability
    - Accent: Audio green (#10b981) - Success, active indicators
    """
    
    def __init__(self):
        super().__init__()
        self._name = "audio_pro"
        self._display_name = "Audio Professional"
        
        # Core color palette
        self._colors = {
            # Primary colors
            'primary': '#1e3a8a',           # Deep blue - main UI elements
            'primary_light': '#3b82f6',     # Lighter blue - hover states
            'primary_dark': '#1e40af',      # Darker blue - pressed states
            
            # Secondary colors  
            'secondary': '#f59e0b',         # Gold - highlights and accents
            'secondary_light': '#fbbf24',   # Light gold - subtle highlights
            'secondary_dark': '#d97706',    # Dark gold - emphasis
            
            # Background colors
            'background': '#f8fafc',        # Cool gray - main background
            'surface': '#ffffff',           # White - content surfaces
            'surface_variant': '#f1f5f9',   # Light gray - alternate surfaces
            
            # Text colors
            'text_primary': '#1e293b',      # Dark slate - main text
            'text_secondary': '#64748b',    # Medium gray - secondary text
            'text_tertiary': '#94a3b8',     # Light gray - disabled text
            'text_on_primary': '#ffffff',   # White text on primary colors
            
            # State colors
            'success': '#10b981',           # Green - success states
            'warning': '#f59e0b',           # Gold - warning states
            'error': '#ef4444',             # Red - error states
            'info': '#3b82f6',              # Blue - info states
            
            # Border colors
            'border_primary': '#e2e8f0',    # Light gray - main borders
            'border_focus': '#3b82f6',      # Blue - focus borders
            'border_hover': '#cbd5e1',      # Medium gray - hover borders
            
            # Interactive states
            'hover': '#f1f5f9',             # Light gray - hover backgrounds
            'active': '#e2e8f0',            # Gray - active/pressed backgrounds
            'focus_ring': '#3b82f6',        # Blue - focus ring color
            
            # Special audio colors
            'waveform': '#10b981',          # Green - audio waveforms
            'spectrum': '#3b82f6',          # Blue - spectrum analysis
            'level_meter': '#f59e0b',       # Gold - level meters
        }
    
    @property
    def name(self) -> str:
        """Get theme name."""
        return self._name
    
    @property 
    def colors(self) -> dict:
        """Get color palette."""
        return self._colors
    
    def get_stylesheet(self) -> str:
        """Get complete stylesheet for the theme."""
        return self.get_main_stylesheet()
    
    def get_main_stylesheet(self) -> str:
        """Get the main application stylesheet."""
        return f"""
        /* Main Application Window */
        QMainWindow {{
            background-color: {self._colors['background']};
            color: {self._colors['text_primary']};
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }}
        
        /* Tab Widget Styling */
        QTabWidget::pane {{
            border: 1px solid {self._colors['border_primary']};
            border-radius: 8px;
            background-color: {self._colors['surface']};
            margin-top: 2px;
        }}
        
        QTabBar::tab {{
            background-color: {self._colors['surface_variant']};
            border: 1px solid {self._colors['border_primary']};
            border-bottom: none;
            padding: 8px 16px;
            margin-right: 2px;
            border-top-left-radius: 6px;
            border-top-right-radius: 6px;
            font-weight: 500;
            font-size: 13px;
            color: {self._colors['text_secondary']};
            min-width: 120px;
        }}
        
        QTabBar::tab:selected {{
            background-color: {self._colors['primary']};
            color: {self._colors['text_on_primary']};
            border-color: {self._colors['primary']};
            font-weight: 600;
        }}
        
        QTabBar::tab:hover:!selected {{
            background-color: {self._colors['hover']};
            color: {self._colors['text_primary']};
            border-color: {self._colors['border_hover']};
        }}
        
        /* Group Box Styling */
        QGroupBox {{
            font-weight: 600;
            font-size: 14px;
            color: {self._colors['text_primary']};
            background-color: {self._colors['surface']};
            border: 1px solid {self._colors['border_primary']};
            border-radius: 8px;
            padding-top: 12px;
            margin-top: 8px;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 8px 0 8px;
            background-color: {self._colors['surface']};
            color: {self._colors['primary']};
        }}
        
        /* Button Styling */
        QPushButton {{
            background-color: {self._colors['primary']};
            color: {self._colors['text_on_primary']};
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            font-weight: 500;
            font-size: 13px;
            min-height: 20px;
        }}
        
        QPushButton:hover {{
            background-color: {self._colors['primary_light']};
        }}
        
        QPushButton:pressed {{
            background-color: {self._colors['primary_dark']};
        }}
        
        QPushButton:disabled {{
            background-color: {self._colors['surface_variant']};
            color: {self._colors['text_tertiary']};
        }}
        
        /* Secondary Button Styling */
        QPushButton[class="secondary"] {{
            background-color: {self._colors['surface']};
            color: {self._colors['text_primary']};
            border: 1px solid {self._colors['border_primary']};
        }}
        
        QPushButton[class="secondary"]:hover {{
            background-color: {self._colors['hover']};
            border-color: {self._colors['border_hover']};
        }}
        
        /* Success Button Styling */
        QPushButton[class="success"] {{
            background-color: {self._colors['success']};
        }}
        
        QPushButton[class="success"]:hover {{
            background-color: #059669;
        }}
        
        /* Warning Button Styling */
        QPushButton[class="warning"] {{
            background-color: {self._colors['warning']};
        }}
        
        QPushButton[class="warning"]:hover {{
            background-color: {self._colors['secondary_dark']};
        }}
        
        /* Input Field Styling */
        QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
            background-color: {self._colors['surface']};
            border: 1px solid {self._colors['border_primary']};
            border-radius: 4px;
            padding: 6px 10px;
            font-size: 13px;
            color: {self._colors['text_primary']};
        }}
        
        QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
            border-color: {self._colors['border_focus']};
            outline: 2px solid {self._colors['focus_ring']}40;
        }}
        
        /* ComboBox Dropdown */
        QComboBox::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 20px;
            border-left: 1px solid {self._colors['border_primary']};
        }}
        
        QComboBox::down-arrow {{
            image: none;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 4px solid {self._colors['text_secondary']};
            width: 0px;
            height: 0px;
        }}
        
        QComboBox QAbstractItemView {{
            background-color: {self._colors['surface']};
            border: 1px solid {self._colors['border_primary']};
            border-radius: 4px;
            selection-background-color: {self._colors['primary']};
            selection-color: {self._colors['text_on_primary']};
        }}
        
        /* List Widget Styling */
        QListWidget {{
            background-color: {self._colors['surface']};
            border: 1px solid {self._colors['border_primary']};
            border-radius: 4px;
            padding: 4px;
            color: {self._colors['text_primary']};
        }}
        
        QListWidget::item {{
            padding: 4px 8px;
            border-radius: 3px;
            margin: 1px;
        }}
        
        QListWidget::item:selected {{
            background-color: {self._colors['primary']};
            color: {self._colors['text_on_primary']};
        }}
        
        QListWidget::item:hover:!selected {{
            background-color: {self._colors['hover']};
        }}
        
        /* Table Widget Styling */
        QTableWidget {{
            background-color: {self._colors['surface']};
            border: 1px solid {self._colors['border_primary']};
            border-radius: 4px;
            gridline-color: {self._colors['border_primary']};
            color: {self._colors['text_primary']};
        }}
        
        QTableWidget::item {{
            padding: 4px 8px;
        }}
        
        QTableWidget::item:selected {{
            background-color: {self._colors['primary']};
            color: {self._colors['text_on_primary']};
        }}
        
        QHeaderView::section {{
            background-color: {self._colors['surface_variant']};
            color: {self._colors['text_primary']};
            padding: 6px 10px;
            border: 1px solid {self._colors['border_primary']};
            font-weight: 600;
        }}
        
        /* Text Edit Styling */
        QTextEdit, QPlainTextEdit {{
            background-color: {self._colors['surface']};
            border: 1px solid {self._colors['border_primary']};
            border-radius: 4px;
            padding: 8px;
            color: {self._colors['text_primary']};
            font-family: 'Monaco', 'Courier New', monospace;
            font-size: 12px;
            line-height: 1.4;
        }}
        
        /* Checkbox Styling */
        QCheckBox {{
            color: {self._colors['text_primary']};
            font-size: 13px;
            spacing: 6px;
        }}
        
        QCheckBox::indicator {{
            width: 16px;
            height: 16px;
            border: 1px solid {self._colors['border_primary']};
            border-radius: 3px;
            background-color: {self._colors['surface']};
        }}
        
        QCheckBox::indicator:checked {{
            background-color: {self._colors['primary']};
            border-color: {self._colors['primary']};
        }}
        
        QCheckBox::indicator:checked::after {{
            content: "✓";
            color: {self._colors['text_on_primary']};
            font-weight: bold;
        }}
        
        /* Progress Bar Styling */
        QProgressBar {{
            background-color: {self._colors['surface_variant']};
            border: 1px solid {self._colors['border_primary']};
            border-radius: 4px;
            text-align: center;
            font-weight: 500;
        }}
        
        QProgressBar::chunk {{
            background-color: {self._colors['primary']};
            border-radius: 3px;
        }}
        
        /* Slider Styling */
        QSlider::groove:horizontal {{
            background-color: {self._colors['surface_variant']};
            height: 6px;
            border-radius: 3px;
        }}
        
        QSlider::handle:horizontal {{
            background-color: {self._colors['primary']};
            border: 1px solid {self._colors['primary_dark']};
            width: 16px;
            height: 16px;
            border-radius: 8px;
            margin: -6px 0;
        }}
        
        QSlider::handle:horizontal:hover {{
            background-color: {self._colors['primary_light']};
        }}
        
        /* Status Bar Styling */
        QStatusBar {{
            background-color: {self._colors['surface_variant']};
            border-top: 1px solid {self._colors['border_primary']};
            color: {self._colors['text_secondary']};
            font-size: 12px;
        }}
        
        /* Scrollbar Styling */
        QScrollBar:vertical {{
            background-color: {self._colors['surface_variant']};
            width: 12px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {self._colors['border_hover']};
            border-radius: 6px;
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {self._colors['text_tertiary']};
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            border: none;
            background: none;
        }}
        """
        
    def get_component_styles(self) -> dict:
        """Get specific component styles."""
        return {
            'audio_visualization': f"""
                background-color: {self._colors['surface']};
                border: 1px solid {self._colors['border_primary']};
                border-radius: 8px;
            """,
            
            'analysis_panel': f"""
                background-color: {self._colors['surface']};
                border: 1px solid {self._colors['border_primary']};
                border-radius: 8px;
                padding: 16px;
            """,
            
            'playlist_generator': f"""
                background-color: {self._colors['surface']};
                border: 1px solid {self._colors['secondary']};
                border-radius: 8px;
                padding: 12px;
            """,
            
            'compatibility_matrix': f"""
                background-color: {self._colors['surface']};
                border: 1px solid {self._colors['success']};
                border-radius: 8px;
            """,
        }