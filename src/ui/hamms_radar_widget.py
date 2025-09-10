"""HAMMS Radar Chart Widget

This module provides a PyQt6 widget for visualizing 12-dimensional HAMMS vectors
using interactive radar/polar charts powered by Plotly.

POML Quality Gates:
- Input validation for HAMMS vector data
- Responsive chart scaling and layout
- Interactive hover information and zoom
- Performance optimization for real-time updates
"""

from __future__ import annotations

import json
from typing import Dict, List, Optional, Any, Union
from pathlib import Path

# IMPORTANT: Import QtWebEngineWidgets first to avoid initialization errors
try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
except ImportError:
    QWebEngineView = None

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QComboBox, QSlider, QCheckBox,
    QGroupBox, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
import plotly.graph_objects as go
import plotly.offline as pyo


class HAMMSRadarWidget(QWidget):
    """Interactive HAMMS radar chart widget for 12-dimensional music analysis visualization
    
    This widget displays HAMMS vectors as radar/polar charts with:
    - Interactive hover information
    - Comparison between multiple tracks
    - Customizable dimension weights and visibility
    - Export capabilities for charts and data
    
    Signals:
        trackSelected: Emitted when user selects a track from comparison view
        exportRequested: Emitted when user requests chart export
    """
    
    trackSelected = pyqtSignal(str)  # track_path
    exportRequested = pyqtSignal(dict)  # export_data
    
    # HAMMS dimension labels and descriptions
    DIMENSION_LABELS = {
        'bpm': 'BPM (Tempo)',
        'key': 'Key Signature', 
        'energy': 'Energy Level',
        'danceability': 'Danceability',
        'valence': 'Valence (Mood)',
        'acousticness': 'Acousticness',
        'instrumentalness': 'Instrumentalness',
        'rhythmic_pattern': 'Rhythmic Pattern',
        'spectral_centroid': 'Spectral Centroid',
        'tempo_stability': 'Tempo Stability',
        'harmonic_complexity': 'Harmonic Complexity',
        'dynamic_range': 'Dynamic Range'
    }
    
    DIMENSION_DESCRIPTIONS = {
        'bmp': 'Normalized tempo/beats per minute (0=slow, 1=fast)',
        'key': 'Musical key signature confidence (0=uncertain, 1=clear)',
        'energy': 'Overall energy and intensity level (0=calm, 1=energetic)',
        'danceability': 'How suitable the track is for dancing (0=not danceable, 1=very danceable)',
        'valence': 'Musical mood/emotion (0=sad/dark, 1=happy/bright)',
        'acousticness': 'Amount of acoustic vs electronic content (0=electronic, 1=acoustic)',
        'instrumentalness': 'Likelihood track is instrumental (0=vocal, 1=instrumental)',
        'rhythmic_pattern': 'Complexity of rhythmic patterns (0=simple, 1=complex)',
        'spectral_centroid': 'Brightness of sound (0=dark/muffled, 1=bright/clear)',
        'tempo_stability': 'Consistency of tempo throughout (0=variable, 1=stable)',
        'harmonic_complexity': 'Sophistication of harmonic content (0=simple, 1=complex)',
        'dynamic_range': 'Variation in volume levels (0=compressed, 1=dynamic)'
    }
    
    # Default colors for different tracks
    TRACK_COLORS = [
        '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd',
        '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
    ]
    
    def __init__(self, parent=None):
        """Initialize the HAMMS radar chart widget
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        # Widget state
        self.tracks_data: Dict[str, Dict[str, Any]] = {}  # track_path -> track_data
        self.visible_dimensions: List[str] = list(self.DIMENSION_LABELS.keys())
        self.comparison_mode = False
        
        # Initialize UI
        self._init_ui()
        self._init_chart()
        
    def _init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)
        
        # Control panel
        controls_frame = self._create_controls_panel()
        layout.addWidget(controls_frame)
        
        # Chart container
        chart_frame = QFrame()
        chart_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        chart_frame.setMinimumHeight(400)
        chart_frame.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        chart_layout = QVBoxLayout(chart_frame)
        chart_layout.setContentsMargins(2, 2, 2, 2)
        
        # Web view for Plotly chart
        if QWebEngineView is not None:
            self.web_view = QWebEngineView()
            self.web_view.setMinimumHeight(380)
            chart_layout.addWidget(self.web_view)
        else:
            # Fallback when QWebEngineView is not available
            from PyQt6.QtWidgets import QTextEdit
            self.web_view = QTextEdit()
            self.web_view.setMinimumHeight(380)
            self.web_view.setReadOnly(True)
            self.web_view.setPlainText("HAMMS Radar Chart visualization requires QtWebEngineWidgets.\nInstall with: pip install PyQt6-WebEngine")
            chart_layout.addWidget(self.web_view)
        
        layout.addWidget(chart_frame)
        
        # Status label
        self.status_label = QLabel("No HAMMS data loaded")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.status_label)
        
    def _create_controls_panel(self) -> QFrame:
        """Create the controls panel with chart customization options
        
        Returns:
            Controls panel frame
        """
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.StyledPanel)
        frame.setMaximumHeight(100)
        
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(10)
        
        # Comparison mode toggle
        comparison_group = QGroupBox("Display Mode")
        comparison_layout = QVBoxLayout(comparison_group)
        comparison_layout.setContentsMargins(5, 5, 5, 5)
        
        self.comparison_checkbox = QCheckBox("Comparison Mode")
        self.comparison_checkbox.setToolTip("Show multiple tracks for comparison")
        self.comparison_checkbox.toggled.connect(self._on_comparison_toggled)
        comparison_layout.addWidget(self.comparison_checkbox)
        
        layout.addWidget(comparison_group)
        
        # Chart style options
        style_group = QGroupBox("Chart Style")
        style_layout = QVBoxLayout(style_group)
        style_layout.setContentsMargins(5, 5, 5, 5)
        
        style_row = QHBoxLayout()
        
        style_row.addWidget(QLabel("Fill:"))
        self.fill_combo = QComboBox()
        self.fill_combo.addItems(["tonext", "toself", "none"])
        self.fill_combo.setCurrentText("tonext")
        self.fill_combo.currentTextChanged.connect(self._refresh_chart)
        style_row.addWidget(self.fill_combo)
        
        style_row.addWidget(QLabel("Opacity:"))
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(10, 100)
        self.opacity_slider.setValue(60)
        self.opacity_slider.setToolTip("Chart fill opacity (10-100%)")
        self.opacity_slider.valueChanged.connect(self._refresh_chart)
        style_row.addWidget(self.opacity_slider)
        
        style_layout.addLayout(style_row)
        layout.addWidget(style_group)
        
        # Export controls
        export_group = QGroupBox("Export")
        export_layout = QVBoxLayout(export_group)
        export_layout.setContentsMargins(5, 5, 5, 5)
        
        export_row = QHBoxLayout()
        
        self.export_png_btn = QPushButton("PNG")
        self.export_png_btn.setToolTip("Export chart as PNG image")
        self.export_png_btn.clicked.connect(lambda: self._export_chart("png"))
        export_row.addWidget(self.export_png_btn)
        
        self.export_html_btn = QPushButton("HTML")
        self.export_html_btn.setToolTip("Export interactive chart as HTML")
        self.export_html_btn.clicked.connect(lambda: self._export_chart("html"))
        export_row.addWidget(self.export_html_btn)
        
        export_layout.addLayout(export_row)
        layout.addWidget(export_group)
        
        # Stretch to push controls to the left
        layout.addStretch()
        
        return frame
        
    def _init_chart(self):
        """Initialize empty chart"""
        self._create_empty_chart()
        
    def _create_empty_chart(self):
        """Create an empty radar chart as placeholder"""
        # Create empty figure
        fig = go.Figure()
        
        # Add placeholder data
        angles = list(self.DIMENSION_LABELS.keys())
        values = [0.0] * len(angles)
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=angles,
            fill='tonext',
            fillcolor='rgba(100,100,100,0.1)',
            line_color='rgba(100,100,100,0.3)',
            name='No Data',
            hoverinfo='skip'
        ))
        
        # Configure layout
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1],
                    tickmode='linear',
                    tick0=0,
                    dtick=0.2,
                    showticklabels=True,
                    tickfont=dict(size=10),
                    gridcolor='rgba(200,200,200,0.5)'
                ),
                angularaxis=dict(
                    tickfont=dict(size=11),
                    rotation=90,
                    direction='clockwise'
                )
            ),
            title={
                'text': "HAMMS v3.0 Analysis - No Data Loaded",
                'x': 0.5,
                'y': 0.95,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': {'size': 16}
            },
            showlegend=False,
            margin=dict(l=50, r=50, t=80, b=50),
            height=350,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        # Convert to HTML and display
        html_content = pyo.plot(fig, output_type='div', include_plotlyjs='cdn')
        self.web_view.setHtml(html_content)
        
    def load_track_data(self, track_path: str, hamms_vector: List[float], 
                       track_metadata: Optional[Dict[str, Any]] = None):
        """Load HAMMS data for a track
        
        Args:
            track_path: Path to the audio file
            hamms_vector: 12-dimensional HAMMS vector
            track_metadata: Additional track metadata (title, artist, etc.)
            
        Raises:
            ValueError: If HAMMS vector is invalid
        """
        # POML Quality Gate: Input validation
        if not isinstance(track_path, str) or not track_path.strip():
            raise ValueError("Track path must be non-empty string")
            
        if not isinstance(hamms_vector, list) or len(hamms_vector) != 12:
            raise ValueError(f"HAMMS vector must be 12-element list, got {len(hamms_vector) if isinstance(hamms_vector, list) else 'non-list'}")
            
        if not all(isinstance(v, (int, float)) for v in hamms_vector):
            raise ValueError("HAMMS vector must contain only numeric values")
            
        if not all(0.0 <= v <= 1.0 for v in hamms_vector):
            raise ValueError("HAMMS vector values must be between 0.0 and 1.0")
            
        # Store track data
        track_name = Path(track_path).stem
        if track_metadata:
            if track_metadata.get('title'):
                track_name = track_metadata['title']
                if track_metadata.get('artist'):
                    track_name = f"{track_metadata['artist']} - {track_name}"
        
        self.tracks_data[track_path] = {
            'name': track_name,
            'hamms_vector': hamms_vector,
            'metadata': track_metadata or {},
            'path': track_path
        }
        
        # Update chart
        self._refresh_chart()
        self._update_status()
        
    def clear_tracks(self):
        """Clear all loaded track data"""
        self.tracks_data.clear()
        self._create_empty_chart()
        self._update_status()
        
    def remove_track(self, track_path: str):
        """Remove a specific track from the display
        
        Args:
            track_path: Path of track to remove
        """
        if track_path in self.tracks_data:
            del self.tracks_data[track_path]
            self._refresh_chart()
            self._update_status()
            
    def set_visible_dimensions(self, dimensions: List[str]):
        """Set which HAMMS dimensions are visible on the chart
        
        Args:
            dimensions: List of dimension names to show
        """
        # POML Quality Gate: Validate dimensions
        valid_dimensions = set(self.DIMENSION_LABELS.keys())
        invalid_dims = set(dimensions) - valid_dimensions
        if invalid_dims:
            raise ValueError(f"Invalid dimensions: {invalid_dims}")
            
        self.visible_dimensions = dimensions
        self._refresh_chart()
        
    def _refresh_chart(self):
        """Refresh the radar chart with current data"""
        if not self.tracks_data:
            self._create_empty_chart()
            return
            
        # Create figure
        fig = go.Figure()
        
        # Get chart style settings
        fill_mode = self.fill_combo.currentText()
        opacity = self.opacity_slider.value() / 100.0
        
        # Add traces for each track
        for i, (track_path, track_data) in enumerate(self.tracks_data.items()):
            if not self.comparison_mode and i > 0:
                break  # Only show first track in single mode
                
            hamms_vector = track_data['hamms_vector']
            track_name = track_data['name']
            
            # Extract values for visible dimensions
            dimension_names = list(self.DIMENSION_LABELS.keys())
            angles = [self.DIMENSION_LABELS[dim] for dim in dimension_names if dim in self.visible_dimensions]
            values = [hamms_vector[dimension_names.index(dim)] for dim in dimension_names if dim in self.visible_dimensions]
            
            # Choose color
            color = self.TRACK_COLORS[i % len(self.TRACK_COLORS)]
            
            # Create hover text
            hover_text = []
            for dim, value in zip([d for d in dimension_names if d in self.visible_dimensions], values):
                desc = self.DIMENSION_DESCRIPTIONS.get(dim, dim)
                hover_text.append(f"<b>{self.DIMENSION_LABELS[dim]}</b><br>{desc}<br>Value: {value:.3f}")
            
            # Add trace
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=angles,
                fill=fill_mode,
                fillcolor=f'rgba{(*self._hex_to_rgb(color), opacity)}',
                line=dict(color=color, width=2),
                name=track_name,
                hovertemplate='%{text}<extra></extra>',
                text=hover_text,
                meta=track_path  # Store track path for interaction
            ))
            
        # Configure layout
        title_text = "HAMMS v3.0 Analysis"
        if len(self.tracks_data) == 1:
            title_text += f" - {list(self.tracks_data.values())[0]['name']}"
        elif len(self.tracks_data) > 1:
            title_text += f" - Comparison ({len(self.tracks_data)} tracks)"
            
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1],
                    tickmode='linear',
                    tick0=0,
                    dtick=0.2,
                    showticklabels=True,
                    tickfont=dict(size=10),
                    gridcolor='rgba(200,200,200,0.8)',
                    gridwidth=1
                ),
                angularaxis=dict(
                    tickfont=dict(size=10, color='#333'),
                    rotation=90,
                    direction='clockwise'
                )
            ),
            title={
                'text': title_text,
                'x': 0.5,
                'y': 0.95,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': {'size': 14, 'color': '#333'}
            },
            showlegend=len(self.tracks_data) > 1,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.1,
                xanchor="center",
                x=0.5
            ),
            margin=dict(l=50, r=50, t=80, b=50),
            height=350,
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        # Convert to HTML and display
        html_content = pyo.plot(fig, output_type='div', include_plotlyjs='cdn')
        self.web_view.setHtml(html_content)
        
    def _hex_to_rgb(self, hex_color: str) -> tuple:
        """Convert hex color to RGB tuple
        
        Args:
            hex_color: Hex color string (e.g., '#1f77b4')
            
        Returns:
            RGB tuple (r, g, b)
        """
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
    def _on_comparison_toggled(self, checked: bool):
        """Handle comparison mode toggle
        
        Args:
            checked: Whether comparison mode is enabled
        """
        self.comparison_mode = checked
        self._refresh_chart()
        
    def _export_chart(self, format_type: str):
        """Export the current chart
        
        Args:
            format_type: Export format ('png', 'html', 'json')
        """
        if not self.tracks_data:
            return
            
        export_data = {
            'format': format_type,
            'tracks': list(self.tracks_data.keys()),
            'timestamp': self._get_timestamp()
        }
        
        self.exportRequested.emit(export_data)
        
    def _get_timestamp(self) -> str:
        """Get current timestamp for exports"""
        from datetime import datetime
        return datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def _update_status(self):
        """Update status label"""
        if not self.tracks_data:
            self.status_label.setText("No HAMMS data loaded")
        elif len(self.tracks_data) == 1:
            track_name = list(self.tracks_data.values())[0]['name']
            self.status_label.setText(f"Loaded: {track_name}")
        else:
            self.status_label.setText(f"Loaded: {len(self.tracks_data)} tracks for comparison")
            
    def get_current_tracks(self) -> List[str]:
        """Get list of currently loaded track paths
        
        Returns:
            List of track paths
        """
        return list(self.tracks_data.keys())
        
    def get_track_data(self, track_path: str) -> Optional[Dict[str, Any]]:
        """Get data for a specific track
        
        Args:
            track_path: Path of track to get data for
            
        Returns:
            Track data dictionary or None if not found
        """
        return self.tracks_data.get(track_path)