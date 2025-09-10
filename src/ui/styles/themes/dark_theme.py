"""Dark theme implementation for Music Analyzer Pro."""

from typing import Dict
from .base_theme import BaseTheme


class DarkTheme(BaseTheme):
    """Professional dark theme with modern color palette."""
    
    @property
    def name(self) -> str:
        return "Dark Professional"
    
    @property
    def colors(self) -> Dict[str, str]:
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
        """Generate complete stylesheet for dark theme."""
        c = self.colors
        
        return f"""
        /* Main Window Styling */
        QMainWindow {{
            background-color: {c['background']};
            color: {c['text']};
        }}
        
        /* Widget Base Styling */
        QWidget {{
            background-color: {c['background']};
            color: {c['text']};
            font-family: 'SF Pro Display', 'Helvetica Neue', BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-size: 13px;
        }}
        
        /* Button Styling */
        QPushButton {{
            background-color: {c['surface']};
            border: 1px solid {c['border']};
            border-radius: 6px;
            padding: 8px 16px;
            color: {c['text']};
            font-weight: 500;
            min-height: 20px;
        }}
        
        QPushButton:hover {{
            background-color: {c['hover']};
            border-color: {c['border_light']};
        }}
        
        QPushButton:pressed {{
            background-color: {c['pressed']};
        }}
        
        QPushButton:disabled {{
            background-color: {c['surface']};
            color: {c['text_disabled']};
            border-color: {c['border']};
        }}
        
        /* Primary Action Buttons */
        QPushButton#start_btn {{
            background-color: {c['primary']};
            border-color: {c['primary_variant']};
            color: white;
        }}
        
        QPushButton#start_btn:hover {{
            background-color: {c['primary_variant']};
        }}
        
        QPushButton#stop_btn {{
            background-color: {c['error']};
            border-color: #c62828;
            color: white;
        }}
        
        QPushButton#stop_btn:hover {{
            background-color: #c62828;
        }}
        
        /* Input Field Styling */
        QLineEdit {{
            background-color: {c['surface']};
            border: 1px solid {c['border']};
            border-radius: 4px;
            padding: 8px 12px;
            color: {c['text']};
        }}
        
        QLineEdit:focus {{
            border-color: {c['secondary']};
            background-color: {c['surface_variant']};
        }}
        
        /* ComboBox Styling */
        QComboBox {{
            background-color: {c['surface']};
            border: 1px solid {c['border']};
            border-radius: 4px;
            padding: 6px 12px;
            color: {c['text']};
        }}
        
        QComboBox:hover {{
            border-color: {c['border_light']};
        }}
        
        QComboBox::drop-down {{
            border: none;
            width: 20px;
        }}
        
        QComboBox::down-arrow {{
            image: none;
            border-left: 4px solid transparent;
            border-right: 4px solid transparent;
            border-top: 6px solid {c['text_secondary']};
        }}
        
        /* SpinBox Styling */
        QSpinBox {{
            background-color: {c['surface']};
            border: 1px solid {c['border']};
            border-radius: 4px;
            padding: 6px 8px;
            color: {c['text']};
        }}
        
        QSpinBox:focus {{
            border-color: {c['secondary']};
        }}
        
        /* Progress Bar Styling */
        QProgressBar {{
            background-color: {c['surface']};
            border: 1px solid {c['border']};
            border-radius: 4px;
            height: 20px;
            text-align: center;
        }}
        
        QProgressBar::chunk {{
            background-color: {c['secondary']};
            border-radius: 3px;
        }}
        
        /* Success Progress Bar */
        QProgressBar[state="success"]::chunk {{
            background-color: {c['success']};
        }}
        
        /* Error Progress Bar */ 
        QProgressBar[state="error"]::chunk {{
            background-color: {c['error']};
        }}
        
        /* List Widget Styling */
        QListWidget {{
            background-color: {c['surface']};
            border: 1px solid {c['border']};
            border-radius: 4px;
            alternate-background-color: {c['surface_variant']};
            selection-background-color: {c['selected']};
            outline: none;
        }}
        
        QListWidget::item {{
            padding: 6px 12px;
            border-bottom: 1px solid {c['border']};
        }}
        
        QListWidget::item:selected {{
            background-color: {c['selected']};
            color: white;
        }}
        
        QListWidget::item:hover {{
            background-color: {c['hover']};
        }}
        
        /* Table Widget Styling */
        QTableWidget {{
            background-color: {c['surface']};
            border: 1px solid {c['border']};
            border-radius: 4px;
            gridline-color: {c['border']};
            selection-background-color: {c['selected']};
            alternate-background-color: {c['surface_variant']};
        }}
        
        QTableWidget::item {{
            padding: 8px;
            border-bottom: 1px solid {c['border']};
        }}
        
        QHeaderView::section {{
            background-color: {c['surface_variant']};
            padding: 8px 12px;
            border: 1px solid {c['border']};
            border-radius: 0px;
            font-weight: bold;
        }}
        
        /* Label Styling */
        QLabel {{
            color: {c['text']};
            background: transparent;
        }}
        
        QLabel[class="heading"] {{
            font-size: 16px;
            font-weight: bold;
            color: {c['text']};
            margin: 10px 0px 5px 0px;
        }}
        
        QLabel[class="subheading"] {{
            font-size: 14px;
            font-weight: 600;
            color: {c['text_secondary']};
            margin: 5px 0px;
        }}
        
        /* CheckBox Styling */
        QCheckBox {{
            color: {c['text']};
            spacing: 8px;
        }}
        
        QCheckBox::indicator {{
            width: 16px;
            height: 16px;
            border-radius: 3px;
            border: 2px solid {c['border']};
            background-color: {c['surface']};
        }}
        
        QCheckBox::indicator:checked {{
            background-color: {c['primary']};
            border-color: {c['primary']};
        }}
        
        QCheckBox::indicator:checked {{
            image: none;
        }}
        
        /* Status Bar Styling */
        QStatusBar {{
            background-color: {c['surface_variant']};
            border-top: 1px solid {c['border']};
            color: {c['text_secondary']};
        }}
        
        /* Group Box Styling for sections */
        QGroupBox {{
            font-weight: bold;
            border: 2px solid {c['border']};
            border-radius: 8px;
            margin-top: 1ex;
            padding-top: 10px;
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
            color: {c['text']};
        }}
        
        /* Scrollbar Styling */
        QScrollBar:vertical {{
            background-color: {c['surface']};
            width: 12px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {c['border_light']};
            border-radius: 6px;
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {c['hover']};
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        """