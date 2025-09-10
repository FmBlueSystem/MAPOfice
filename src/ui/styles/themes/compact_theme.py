"""Compact theme optimized for MacBook Pro 13" displays."""

from typing import Dict
from .base_theme import BaseTheme


class CompactTheme(BaseTheme):
    """Compact theme optimized for 13" MacBook Pro displays.
    
    Features:
    - Reduced spacing and margins for vertical space efficiency
    - Smaller fonts while maintaining readability
    - Condensed controls and compact button styling
    - Optimized for 2560x1600 Retina displays
    """
    
    @property
    def name(self) -> str:
        return "Compact Dark"
    
    @property
    def colors(self) -> Dict[str, str]:
        # Inherit colors from dark theme but with some adjustments
        return {
            # Background colors
            'background': '#2b2b2b',
            'surface': '#3c3c3c',
            'surface_variant': '#4a4a4a',
            
            # Primary colors
            'primary': '#4CAF50',
            'primary_variant': '#388E3C',
            'secondary': '#2196F3',
            'secondary_variant': '#1976D2',
            
            # Status colors
            'success': '#4CAF50',
            'warning': '#ff9800',
            'error': '#f44336',
            'info': '#2196F3',
            
            # Text colors
            'text': '#ffffff',
            'text_secondary': '#b0b0b0',
            'text_disabled': '#666666',
            
            # Interactive colors
            'hover': '#5a5a5a',
            'selected': '#1976D2',
            'pressed': '#0d47a1',
            
            # Border colors
            'border': '#555555',
            'border_light': '#777777',
        }
    
    def get_stylesheet(self) -> str:
        """Generate compact stylesheet optimized for 13\" displays."""
        c = self.colors
        
        return f"""
        /* Main Window Styling - Compact */
        QMainWindow {{
            background-color: {c['background']};
            color: {c['text']};
        }}
        
        /* Widget Base Styling - Compact */
        QWidget {{
            background-color: {c['background']};
            color: {c['text']};
            font-family: 'SF Pro Display', 'Helvetica Neue', BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-size: 12px;
        }}
        
        /* Compact Button Styling */
        QPushButton {{
            background-color: {c['surface']};
            border: 1px solid {c['border']};
            border-radius: 4px;
            padding: 4px 12px;
            color: {c['text']};
            font-weight: 500;
            min-height: 20px;
            max-height: 28px;
        }}
        
        QPushButton:hover {{
            background-color: {c['hover']};
            border-color: {c['border_light']};
        }}
        
        QPushButton:pressed {{
            background-color: {c['pressed']};
        }}
        
        /* Primary Action Buttons - Compact */
        QPushButton#start_btn {{
            background-color: {c['primary']};
            border-color: {c['primary_variant']};
            color: white;
            font-weight: 600;
        }}
        
        QPushButton#start_btn:hover {{
            background-color: {c['primary_variant']};
        }}
        
        QPushButton#stop_btn {{
            background-color: {c['error']};
            border-color: #c62828;
            color: white;
            font-weight: 600;
        }}
        
        QPushButton#stop_btn:hover {{
            background-color: #c62828;
        }}
        
        /* Compact Input Field Styling */
        QLineEdit {{
            background-color: {c['surface']};
            border: 1px solid {c['border']};
            border-radius: 3px;
            padding: 4px 8px;
            color: {c['text']};
            min-height: 20px;
            max-height: 24px;
        }}
        
        QLineEdit:focus {{
            border-color: {c['secondary']};
            background-color: {c['surface_variant']};
        }}
        
        /* Compact ComboBox Styling */
        QComboBox {{
            background-color: {c['surface']};
            border: 1px solid {c['border']};
            border-radius: 3px;
            padding: 4px 8px;
            color: {c['text']};
            min-height: 20px;
            max-height: 24px;
        }}
        
        QComboBox:hover {{
            border-color: {c['border_light']};
        }}
        
        QComboBox::drop-down {{
            border: none;
            width: 16px;
        }}
        
        QComboBox::down-arrow {{
            image: none;
            border-left: 3px solid transparent;
            border-right: 3px solid transparent;
            border-top: 4px solid {c['text_secondary']};
        }}
        
        /* Compact SpinBox Styling */
        QSpinBox {{
            background-color: {c['surface']};
            border: 1px solid {c['border']};
            border-radius: 3px;
            padding: 4px 6px;
            color: {c['text']};
            min-height: 20px;
            max-height: 24px;
        }}
        
        QSpinBox:focus {{
            border-color: {c['secondary']};
        }}
        
        /* Compact Progress Bar Styling */
        QProgressBar {{
            background-color: {c['surface']};
            border: 1px solid {c['border']};
            border-radius: 3px;
            height: 16px;
            text-align: center;
            font-size: 11px;
        }}
        
        QProgressBar::chunk {{
            background-color: {c['secondary']};
            border-radius: 2px;
        }}
        
        /* Success Progress Bar */
        QProgressBar[state="success"]::chunk {{
            background-color: {c['success']};
        }}
        
        /* Error Progress Bar */ 
        QProgressBar[state="error"]::chunk {{
            background-color: {c['error']};
        }}
        
        /* Compact List Widget Styling */
        QListWidget {{
            background-color: {c['surface']};
            border: 1px solid {c['border']};
            border-radius: 3px;
            alternate-background-color: {c['surface_variant']};
            selection-background-color: {c['selected']};
            outline: none;
        }}
        
        QListWidget::item {{
            padding: 3px 8px;
            border-bottom: 1px solid {c['border']};
            min-height: 18px;
        }}
        
        QListWidget::item:selected {{
            background-color: {c['selected']};
            color: white;
        }}
        
        QListWidget::item:hover {{
            background-color: {c['hover']};
        }}
        
        /* Compact Table Widget Styling */
        QTableWidget {{
            background-color: {c['surface']};
            border: 1px solid {c['border']};
            border-radius: 3px;
            gridline-color: {c['border']};
            selection-background-color: {c['selected']};
            alternate-background-color: {c['surface_variant']};
        }}
        
        QTableWidget::item {{
            padding: 4px 6px;
            border-bottom: 1px solid {c['border']};
            min-height: 16px;
        }}
        
        QHeaderView::section {{
            background-color: {c['surface_variant']};
            padding: 4px 8px;
            border: 1px solid {c['border']};
            font-weight: bold;
            font-size: 11px;
        }}
        
        /* Compact Label Styling */
        QLabel {{
            color: {c['text']};
            background: transparent;
        }}
        
        QLabel[class="heading"] {{
            font-size: 14px;
            font-weight: bold;
            color: {c['text']};
            margin: 4px 0px 2px 0px;
        }}
        
        QLabel[class="subheading"] {{
            font-size: 12px;
            font-weight: 600;
            color: {c['text_secondary']};
            margin: 2px 0px;
        }}
        
        /* Compact CheckBox Styling */
        QCheckBox {{
            color: {c['text']};
            spacing: 6px;
            font-size: 12px;
        }}
        
        QCheckBox::indicator {{
            width: 14px;
            height: 14px;
            border-radius: 2px;
            border: 2px solid {c['border']};
            background-color: {c['surface']};
        }}
        
        QCheckBox::indicator:checked {{
            background-color: {c['primary']};
            border-color: {c['primary']};
        }}
        
        /* Compact Group Box Styling */
        QGroupBox {{
            font-weight: bold;
            font-size: 12px;
            border: 1px solid {c['border']};
            border-radius: 4px;
            margin-top: 6px;
            padding-top: 6px;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 8px;
            padding: 0 4px 0 4px;
            color: {c['text']};
            font-size: 11px;
        }}
        
        /* Compact Status Bar Styling */
        QStatusBar {{
            background-color: {c['surface_variant']};
            border-top: 1px solid {c['border']};
            color: {c['text_secondary']};
            font-size: 11px;
            max-height: 20px;
        }}
        
        /* Compact Scrollbar Styling */
        QScrollBar:vertical {{
            background-color: {c['surface']};
            width: 10px;
            border-radius: 5px;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {c['border_light']};
            border-radius: 5px;
            min-height: 15px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {c['hover']};
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        """