# Music Analyzer Pro - UI Styling Guide

## Overview

The Music Analyzer Pro uses a modular styling system based on PyQt6 stylesheets (QSS). The system provides consistent, professional theming with easy customization and extension capabilities.

## Architecture

### Core Components

- **StyleManager**: Central styling coordination
- **BaseTheme**: Abstract theme interface
- **DarkTheme**: Professional dark theme implementation
- **Component Modules**: Specialized widget styling (future expansion)

### Color Palette

The current dark theme uses the following color scheme:

```python
# Primary Colors
'background': '#2b2b2b'      # Main background
'surface': '#3c3c3c'         # Widget surfaces
'primary': '#4CAF50'         # Primary actions (green)
'secondary': '#2196F3'       # Secondary actions (blue)

# Status Colors
'success': '#4CAF50'         # Success states
'warning': '#ff9800'         # Warning states
'error': '#f44336'           # Error states
'info': '#2196F3'            # Information

# Text Colors
'text': '#ffffff'            # Primary text
'text_secondary': '#b0b0b0'  # Secondary text
'text_disabled': '#666666'   # Disabled text

# Interactive Colors
'hover': '#5a5a5a'           # Hover states
'selected': '#1976D2'        # Selection
'pressed': '#0d47a1'         # Pressed states
```

## Usage

### Basic Implementation

```python
from src.ui.styles import StyleManager

# Initialize and apply theme
style_manager = StyleManager()
style_manager.set_theme('dark')
style_manager.apply_theme_to_widget(self)

# Get colors programmatically
primary_color = style_manager.get_color('primary')
```

### Widget-Specific Styling

Certain widgets receive special styling through object names:

```python
# Primary action button (green)
button.setObjectName("start_btn")

# Error action button (red)  
button.setObjectName("stop_btn")

# Progress bar states
progress_bar.setProperty("state", "success")  # Green
progress_bar.setProperty("state", "error")    # Red
```

### Styled Components

The theme includes comprehensive styling for:

- **Buttons**: Hover effects, state colors, consistent sizing
- **Input Fields**: Focus indicators, consistent padding
- **Progress Bars**: Color-coded states, rounded corners
- **Lists/Tables**: Alternating rows, selection highlighting
- **Group Boxes**: Section organization, consistent borders
- **Scrollbars**: Custom appearance matching theme

## Extending the System

### Creating New Themes

1. Inherit from `BaseTheme`:

```python
from src.ui.styles.themes.base_theme import BaseTheme

class LightTheme(BaseTheme):
    @property
    def name(self) -> str:
        return "Light Professional"
    
    @property 
    def colors(self) -> Dict[str, str]:
        return {
            'background': '#ffffff',
            'surface': '#f5f5f5',
            # ... define all required colors
        }
    
    def get_stylesheet(self) -> str:
        # Return complete QSS stylesheet
        return "..."
```

2. Register in StyleManager:

```python
self._available_themes['light'] = LightTheme()
```

### Adding Component-Specific Styles

Create new modules in `src/ui/styles/components/` for specialized widget styling:

```python
# src/ui/styles/components/custom_widgets.py
def get_custom_widget_styles(colors: Dict[str, str]) -> str:
    return f"""
    QCustomWidget {{
        background-color: {colors['surface']};
        border: 1px solid {colors['border']};
    }}
    """
```

## Best Practices

### Color Usage Guidelines

- **Primary Green (#4CAF50)**: Success states, primary actions
- **Secondary Blue (#2196F3)**: Information, secondary actions, progress
- **Error Red (#f44336)**: Errors, destructive actions
- **Warning Orange (#ff9800)**: Warnings, caution states

### Styling Conventions

1. **Consistency**: Use theme colors exclusively, avoid hardcoded values
2. **Contrast**: Ensure sufficient contrast for accessibility (4.5:1 minimum)
3. **States**: Provide clear visual feedback for interactive elements
4. **Hierarchy**: Use color and typography to establish clear information hierarchy

### Performance Considerations

- Stylesheets are loaded once at application startup
- Dynamic color changes require style refresh:
  ```python
  widget.style().unpolish(widget)
  widget.style().polish(widget)
  ```
- Avoid excessive nesting in QSS selectors

## Troubleshooting

### Common Issues

1. **Fonts not loading**: Ensure font family fallbacks are specified
2. **Colors not updating**: Call `unpolish()/polish()` after property changes
3. **Selection not visible**: Check contrast between selection and background colors

### Debug Tips

- Use Qt Designer or qss files for rapid prototyping
- Test with different window sizes and content amounts
- Verify accessibility with system dark/light mode changes

## Future Enhancements

Potential improvements to the styling system:

- Light theme implementation
- High contrast accessibility theme
- User-customizable color schemes  
- Component-specific style modules
- Runtime theme switching interface
- CSS-like preprocessing for complex styles