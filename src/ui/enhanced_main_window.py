"""Enhanced PyQt6 UI with HAMMS v3.0 and Multi-LLM Integration

This enhanced main window extends the original with:
- HAMMS v3.0 12-dimensional analysis
- Multi-LLM enrichment integration (Z.ai, Gemini, OpenAI)  
- Interactive HAMMS radar chart visualization
- Enhanced analysis workflow with both basic and advanced modes

POML Quality Gates:
- Backward compatibility with existing analysis workflow
- Error handling and graceful degradation when services unavailable
- Progress tracking for enhanced analysis pipeline
- Data validation and integrity checks
"""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

# IMPORTANT: Import QtWebEngineWidgets first to avoid initialization errors
try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
except ImportError:
    QWebEngineView = None

from PyQt6.QtCore import QThread, pyqtSignal, QSettings, Qt, QTimer
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QFileDialog, QListWidget,
    QProgressBar, QStatusBar, QMessageBox, QCheckBox,
    QTabWidget, QGroupBox, QComboBox, QTextEdit, QSplitter,
    QFrame, QScrollArea, QTableWidget, QTableWidgetItem,
    QSlider, QGridLayout, QApplication, QInputDialog
)

# Import existing components
from src.ui.hamms_radar_widget import HAMMSRadarWidget
from src.ui.styles import StyleManager

# Import enhanced services
from src.services.enhanced_analyzer import EnhancedAnalyzer, EnhancedAnalysisResult
from src.services.storage import Storage
from src.analysis import create_enricher_from_env
from src.analysis.library_analytics import LibraryAnalyzer, LibraryAnalytics
from src.services.analyzer import Analyzer


@dataclass 
class EnhancedAnalysisSettings:
    """Settings for enhanced analysis"""
    enable_hamms_v3: bool = True
    enable_ai: bool = True
    force_reanalysis: bool = False
    batch_size: int = 5
    show_radar_chart: bool = True


class EnhancedAnalyzeWorker(QThread):
    """Worker thread for enhanced music analysis"""
    
    progress = pyqtSignal(int, int)  # current, total
    log = pyqtSignal(str)
    done = pyqtSignal(list)  # List[EnhancedAnalysisResult]
    track_analyzed = pyqtSignal(str, dict)  # track_path, analysis_data
    llm_progress = pyqtSignal(str, str, str)  # track_path, provider, status
    error = pyqtSignal(str)
    
    def __init__(self, track_paths: List[str], analyzer: EnhancedAnalyzer, 
                 settings: EnhancedAnalysisSettings):
        super().__init__()
        self.track_paths = track_paths
        self.analyzer = analyzer
        self.settings = settings
        self._stop_requested = False
        
    def run(self):
        """Run the enhanced analysis"""
        try:
            self.log.emit("Starting enhanced analysis...")
            results = []
            
            total = len(self.track_paths)
            
            for i, track_path in enumerate(self.track_paths, 1):
                if self._stop_requested:
                    self.log.emit("Analysis cancelled by user")
                    break
                    
                self.log.emit(f"Analyzing {Path(track_path).name} ({i}/{total})")
                self.progress.emit(i-1, total)
                
                # Perform enhanced analysis
                result = self.analyzer.analyze_track(
                    track_path, 
                    force_reanalysis=self.settings.force_reanalysis
                )
                
                results.append(result)
                
                if result.success:
                    # Emit data for radar chart update
                    self.track_analyzed.emit(track_path, {
                        'hamms_vector': result.hamms_vector,
                        'genre': result.genre,
                        'mood': result.mood,
                        'confidence': result.hamms_confidence
                    })
                    
                    analysis_type = "Enhanced" if result.genre else "HAMMS Only"
                    self.log.emit(f"  ✓ {analysis_type} analysis complete")
                else:
                    self.log.emit(f"  ✗ Analysis failed: {result.error_message}")
                    
            self.progress.emit(total, total)
            self.done.emit(results)
            
        except Exception as e:
            self.error.emit(f"Analysis failed: {str(e)}")
            
    def stop(self):
        """Request the worker to stop"""
        self._stop_requested = True


class EnhancedMainWindow(QMainWindow):
    """Enhanced main window with HAMMS v3.0 and Multi-LLM integration
    
    This window provides a complete music analysis interface with:
    - Legacy mode (original analysis workflow)
    - Enhanced mode (HAMMS v3.0 + Multi-LLM enrichment)
    - Interactive HAMMS radar chart visualization
    - Side-by-side track comparison
    - Enhanced progress tracking and logging
    """
    
    def __init__(self, parent=None):
        """Initialize the enhanced main window"""
        super().__init__(parent)
        
        # Initialize theme system
        self.style_manager = StyleManager()
        self.style_manager.set_theme('audio_pro')
        self.style_manager.apply_theme_to_app(QApplication.instance())
        
        # Initialize services
        self.storage = Storage.from_path("data/music.db")
        self.enhanced_analyzer = EnhancedAnalyzer(self.storage, enable_ai=True)
        self.analyzer = Analyzer(self.storage)
        self.library_analyzer = LibraryAnalyzer(self.storage)
        self.ai_available = create_enricher_from_env() is not None
        
        # State
        self.worker: Optional[EnhancedAnalyzeWorker] = None
        self.current_results: List[EnhancedAnalysisResult] = []
        self.settings = EnhancedAnalysisSettings()
        
        self.setWindowTitle("Music Analyzer Pro - Enhanced (HAMMS v3.0 + AI)")
        self.setMinimumSize(1200, 650)  # Further reduced minimum height
        self.resize(1200, 650)  # Set initial size
        
        self._init_ui()
        self._connect_signals()
        self._check_services()
        
    def _init_ui(self):
        """Initialize the user interface"""
        # Central widget with tab layout
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QVBoxLayout(central)
        layout.setContentsMargins(1, 1, 1, 1)  # Ultra minimal margins
        layout.setSpacing(1)  # Ultra minimal spacing
        
        # Header with service status - minimal space
        header = self._create_header()
        layout.addWidget(header)
        layout.setStretchFactor(header, 0)  # Don't stretch header
        
        # Main content area with enhanced styling
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.TabPosition.North)
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #000000;
                border-radius: 4px;
                background-color: white;
                margin-top: 0px;
            }
            QTabBar::tab {
                background-color: #ffffff;
                border: 1px solid #000000;
                padding: 6px 12px;
                margin-right: 1px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                font-weight: 500;
                font-size: 11px;
                color: #000000;
                min-width: 80px;
            }
            QTabBar::tab:selected {
                background-color: #0066cc;
                color: #ffffff;
                border: 2px solid #004499;
                border-bottom-color: white;
                font-weight: bold;
            }
            QTabBar::tab:hover {
                background-color: #f0f8ff;
                color: #000000;
                border: 2px solid #0066cc;
            }
        """)
        
        # Enhanced Analysis Tab
        self.enhanced_tab = self._create_enhanced_analysis_tab()
        self.tab_widget.addTab(self.enhanced_tab, "Enhanced Analysis")
        
        # Visualization Tab
        self.viz_tab = self._create_visualization_tab()
        self.tab_widget.addTab(self.viz_tab, "HAMMS Visualization")
        
        # Results Tab
        self.results_tab = self._create_results_tab()
        self.tab_widget.addTab(self.results_tab, "Analysis Results")
        
        # Library Analytics Tab
        self.analytics_tab = self._create_library_analytics_tab()
        self.tab_widget.addTab(self.analytics_tab, "Library Analytics")
        
        layout.addWidget(self.tab_widget)
        layout.setStretchFactor(self.tab_widget, 1)  # Give all space to tabs
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready - HAMMS v3.0 + Multi-LLM Integration")
        
    def _create_header(self) -> QFrame:
        """Create header with service status indicators"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.StyledPanel)
        frame.setMaximumHeight(25)  # Minimal header height
        
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(1, 1, 1, 1)  # Ultra minimal margins
        
        # Title with smaller, more compact design
        title = QLabel("🎵 Music Analyzer Pro")
        title.setStyleSheet("""
            font-size: 11px; 
            font-weight: bold; 
            color: #000000;
            background-color: #ffffff;
            padding: 2px 6px;
            border-radius: 3px;
            border: 1px solid #000000;
        """)
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Service status indicators - compact
        status_layout = QHBoxLayout()  # Changed to horizontal for more space
        
        # HAMMS v3.0 status - compact
        self.hamms_status = QLabel("✓ HAMMS v3.0")
        self.hamms_status.setStyleSheet("color: #000000; font-weight: bold; background-color: #ffffff; font-size: 10px; padding: 1px 3px;")
        status_layout.addWidget(self.hamms_status)
        
        # AI LLM status - compact
        self.ai_status = QLabel("✗ AI LLM" if not self.ai_available else "✓ AI LLM")
        self.ai_status.setStyleSheet("color: #000000; font-weight: bold; background-color: #ffffff; font-size: 10px; padding: 1px 3px;")
        status_layout.addWidget(self.ai_status)
        
        layout.addLayout(status_layout)
        
        return frame
        
    def _create_enhanced_analysis_tab(self) -> QWidget:
        """Create the enhanced analysis tab"""
        widget = QWidget()
        widget.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                color: #000000;
            }
        """)
        layout = QVBoxLayout(widget)
        layout.setSpacing(1)  # Ultra minimal spacing
        layout.setContentsMargins(1, 1, 1, 1)  # Ultra minimal margins
        
        # Directory selection
        dir_group = QGroupBox("Audio Directory")
        dir_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                color: #000000;
                background-color: #ffffff;
                border: 2px solid #000000;
                border-radius: 6px;
                padding-top: 10px;
                margin-top: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 5px 0 5px;
                color: #000000;
                background-color: #ffffff;
            }
        """)
        dir_layout = QVBoxLayout(dir_group)
        dir_layout.setSpacing(1)
        dir_layout.setContentsMargins(2, 2, 2, 2)
        
        dir_row = QHBoxLayout()
        self.dir_label = QLabel("No directory selected")
        self.dir_label.setStyleSheet("""
            padding: 4px 8px; 
            border: 1px solid #000000; 
            background-color: #ffffff;
            border-radius: 4px;
            font-size: 12px;
            min-height: 16px;
            color: #000000;
            font-weight: 500;
        """)
        dir_row.addWidget(self.dir_label, 1)
        
        self.browse_btn = QPushButton("📁 Browse...")
        self.browse_btn.setMinimumWidth(120)
        self.browse_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196f3;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
            QPushButton:pressed {
                background-color: #0d47a1;
            }
        """)
        dir_row.addWidget(self.browse_btn)
        
        dir_layout.addLayout(dir_row)
        layout.addWidget(dir_group)
        
        # Analysis settings
        settings_group = QGroupBox("Analysis Settings")
        settings_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                color: #000000;
                background-color: #ffffff;
                border: 2px solid #000000;
                border-radius: 6px;
                padding-top: 10px;
                margin-top: 5px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 5px 0 5px;
                color: #000000;
                background-color: #ffffff;
            }
        """)
        settings_layout = QVBoxLayout(settings_group)
        settings_layout.setSpacing(1)
        settings_layout.setContentsMargins(2, 2, 2, 2)
        
        settings_row1 = QHBoxLayout()
        
        self.hamms_checkbox = QCheckBox("🎯 Enable HAMMS v3.0 (12D)")
        self.hamms_checkbox.setChecked(True)
        self.hamms_checkbox.setToolTip("12-dimensional harmonic analysis")
        self.hamms_checkbox.setStyleSheet("""
            QCheckBox {
                font-size: 13px;
                padding: 4px;
                color: #000000;
                font-weight: 500;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 3px;
                border: 2px solid #666666;
                background-color: #ffffff;
            }
            QCheckBox::indicator:checked {
                background-color: #0066cc;
                border: 2px solid #004499;
            }
        """)
        settings_row1.addWidget(self.hamms_checkbox)
        
        self.ai_checkbox = QCheckBox("🤖 Enable AI Enrichment") 
        self.ai_checkbox.setChecked(self.ai_available)
        self.ai_checkbox.setEnabled(self.ai_available)
        self.ai_checkbox.setToolTip("AI-powered genre, mood, and tag analysis")
        self.ai_checkbox.setStyleSheet(self.hamms_checkbox.styleSheet())
        settings_row1.addWidget(self.ai_checkbox)
        
        self.force_checkbox = QCheckBox("🔄 Force Re-analysis")
        self.force_checkbox.setToolTip("Re-analyze tracks even if already processed")
        self.force_checkbox.setStyleSheet(self.hamms_checkbox.styleSheet())
        settings_row1.addWidget(self.force_checkbox)
        
        # Add metadata writing checkbox
        self.write_metadata_checkbox = QCheckBox("📝 Write to File Tags")
        self.write_metadata_checkbox.setChecked(True)  # Enable by default
        self.write_metadata_checkbox.setToolTip("Write genre and analysis results to audio file metadata")
        self.write_metadata_checkbox.setStyleSheet(self.hamms_checkbox.styleSheet())
        settings_row1.addWidget(self.write_metadata_checkbox)
        
        settings_row1.addStretch()
        
        settings_layout.addLayout(settings_row1)
        layout.addWidget(settings_group)
        
        # Control buttons
        controls_group = QGroupBox("Controls")
        controls_layout = QHBoxLayout(controls_group)
        controls_layout.setSpacing(2)
        controls_layout.setContentsMargins(2, 2, 2, 2)
        
        self.start_btn = QPushButton("🚀 Start Enhanced Analysis")
        self.start_btn.setToolTip("Begin HAMMS v3.0 + Multi-LLM analysis of selected directory (Ctrl+R)")
        self.start_btn.setShortcut("Ctrl+R")
        self.start_btn.setMinimumWidth(150)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #388e3c;
            }
            QPushButton:pressed {
                background-color: #2e7d32;
            }
            QPushButton:disabled {
                background-color: #c8e6c9;
                color: #666;
            }
        """)
        controls_layout.addWidget(self.start_btn)
        
        self.stop_btn = QPushButton("🛑 Stop")
        self.stop_btn.setToolTip("Stop current analysis process (Escape)")
        self.stop_btn.setShortcut("Escape")
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
            QPushButton:pressed {
                background-color: #c62828;
            }
            QPushButton:disabled {
                background-color: #ffcdd2;
                color: #666;
            }
        """)
        controls_layout.addWidget(self.stop_btn)
        
        controls_layout.addStretch()
        
        self.export_btn = QPushButton("Export Results")
        self.export_btn.setEnabled(False)
        controls_layout.addWidget(self.export_btn)
        
        layout.addWidget(controls_group)
        
        # Progress section
        progress_group = QGroupBox("Progress")
        progress_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                color: #000000;
                background-color: #ffffff;
                border: 2px solid #000000;
                border-radius: 6px;
                padding-top: 8px;
                margin-top: 3px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 5px 0 5px;
                color: #000000;
                background-color: #ffffff;
            }
        """)
        progress_layout = QVBoxLayout(progress_group)
        progress_layout.setSpacing(0)  # No spacing
        progress_layout.setContentsMargins(2, 2, 2, 2)  # Minimal margins
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #000000;
                border-radius: 8px;
                text-align: center;
                font-weight: bold;
                font-size: 12px;
                height: 20px;
                background: #f5f5f5;
            }
            QProgressBar::chunk {
                background-color: #228b22;
                border-radius: 6px;
                margin: 1px;
            }
        """)
        progress_layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel("Ready to analyze...")
        progress_layout.addWidget(self.progress_label)
        
        # LLM status label
        self.llm_status_label = QLabel("")
        self.llm_status_label.setStyleSheet("color: #666; font-style: italic; font-size: 10px;")
        progress_layout.addWidget(self.llm_status_label)
        
        layout.addWidget(progress_group)
        
        # Log output
        log_group = QGroupBox("Analysis Log")
        log_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 13px;
                color: #000000;
                background-color: #ffffff;
                border: 2px solid #000000;
                border-radius: 6px;
                padding-top: 8px;
                margin-top: 3px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 8px;
                padding: 0 5px 0 5px;
                color: #000000;
                background-color: #ffffff;
            }
        """)
        log_layout = QVBoxLayout(log_group)
        log_layout.setSpacing(0)  # No spacing
        log_layout.setContentsMargins(2, 2, 2, 2)  # Minimal margins
        
        self.log_output = QTextEdit()
        self.log_output.setMaximumHeight(70)  # Further reduced for space
        self.log_output.setReadOnly(True)
        self.log_output.setStyleSheet("""
            font-family: 'Monaco', 'Courier New', monospace;
            background-color: #ffffff;
            border: 2px solid #000000;
            border-radius: 6px;
            padding: 8px;
            font-size: 12px;
            line-height: 1.4;
            color: #212529;
        """)
        log_layout.addWidget(self.log_output)
        
        layout.addWidget(log_group)
        
        return widget
        
    def _create_visualization_tab(self) -> QWidget:
        """Create the visualization tab with HAMMS radar chart"""
        widget = QWidget()
        widget.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                color: #000000;
            }
        """)
        layout = QVBoxLayout(widget)
        layout.setSpacing(1)
        layout.setContentsMargins(1, 1, 1, 1)
        
        # Instructions
        instructions = QLabel(
            "HAMMS v3.0 Radar Chart - Select tracks from analysis results to visualize their 12-dimensional vectors"
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("""
            padding: 6px;
            background-color: #e8f5e8;
            border-radius: 4px;
            border: 1px solid #c8e6c9;
            color: #2e7d32;
            font-size: 13px;
            line-height: 1.5;
        """)
        layout.addWidget(instructions)
        
        # HAMMS Radar Chart
        self.radar_widget = HAMMSRadarWidget()
        layout.addWidget(self.radar_widget)
        
        return widget
        
    def _create_results_tab(self) -> QWidget:
        """Create the results tab with analysis results table"""
        widget = QWidget()
        widget.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                color: #000000;
            }
        """)
        layout = QVBoxLayout(widget)
        layout.setSpacing(1)  # Ultra minimal spacing for maximum table space
        layout.setContentsMargins(2, 2, 2, 2)  # Ultra minimal margins
        
        # Results table
        self.results_table = QTableWidget()
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.results_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #000000;
                background-color: #ffffff;
                alternate-background-color: #f5f5f5;
                border: 2px solid #000000;
                border-radius: 6px;
                font-size: 12px;
                color: #000000;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #dddddd;
                color: #000000;
            }
            QTableWidget::item:selected {
                background-color: #0066cc;
                color: #ffffff;
            }
            QHeaderView::section {
                background-color: #e6f2ff;
                padding: 8px;
                border: 1px solid #000000;
                font-weight: bold;
                color: #000000;
            }
        """)
        
        # Set up table columns
        columns = [
            "Track", "Artist", "Genre", "Subgenre", "Mood", "Era", "BPM", "Key", "Energy",
            "HAMMS Confidence", "AI Confidence", "Status"
        ]
        self.results_table.setColumnCount(len(columns))
        self.results_table.setHorizontalHeaderLabels(columns)
        
        # Adjust column widths
        header = self.results_table.horizontalHeader()
        header.setStretchLastSection(True)
        
        layout.addWidget(self.results_table)
        
        # Table controls
        table_controls = QHBoxLayout()
        
        self.visualize_selected_btn = QPushButton("📊 Visualize Selected")
        self.visualize_selected_btn.setToolTip("Show HAMMS radar chart for selected track (Ctrl+V)")
        self.visualize_selected_btn.setShortcut("Ctrl+V")
        self.visualize_selected_btn.setEnabled(False)
        self.visualize_selected_btn.setToolTip("Show selected tracks in HAMMS radar chart")
        table_controls.addWidget(self.visualize_selected_btn)
        
        self.compare_btn = QPushButton("⚖️ Compare Tracks")
        self.compare_btn.setToolTip("Compare similarity between selected tracks (Ctrl+Shift+C)")
        self.compare_btn.setShortcut("Ctrl+Shift+C")
        self.compare_btn.setEnabled(False) 
        self.compare_btn.setToolTip("Enable comparison mode for multiple tracks")
        table_controls.addWidget(self.compare_btn)
        
        table_controls.addStretch()
        
        self.clear_results_btn = QPushButton("🗑️ Clear Results")
        self.clear_results_btn.setToolTip("Clear all analysis results (Ctrl+L)")
        self.clear_results_btn.setShortcut("Ctrl+L")
        table_controls.addWidget(self.clear_results_btn)
        
        layout.addLayout(table_controls)
        
        return widget
        
    def _connect_signals(self):
        """Connect UI signals to handlers"""
        # Main controls
        self.browse_btn.clicked.connect(self._browse_directory)
        self.start_btn.clicked.connect(self._start_analysis)
        self.stop_btn.clicked.connect(self._stop_analysis)
        self.export_btn.clicked.connect(self._export_results)
        
        # Results table
        self.results_table.selectionModel().selectionChanged.connect(self._on_selection_changed)
        self.visualize_selected_btn.clicked.connect(self._visualize_selected)
        self.compare_btn.clicked.connect(self._toggle_comparison)
        self.clear_results_btn.clicked.connect(self._clear_results)
        
        # Settings checkboxes
        self.hamms_checkbox.toggled.connect(self._update_settings)
        self.ai_checkbox.toggled.connect(self._update_settings)
        self.force_checkbox.toggled.connect(self._update_settings)
        
    def _check_services(self):
        """Check availability of analysis services"""
        # This is already done in __init__, just update UI if needed
        if not self.ai_available:
            self.log_output.append("⚠️ No LLM providers configured - AI enrichment disabled")
        else:
            self.log_output.append("✓ Multi-LLM integration ready")
            
        self.log_output.append("✓ HAMMS v3.0 analyzer ready")
        
        # Load existing tracks for playlist generation
        self._update_seed_tracks()
        
    def _browse_directory(self):
        """Browse for audio directory"""
        dir_path = QFileDialog.getExistingDirectory(
            self, 
            "Select Audio Directory",
            os.path.expanduser("~")
        )
        
        if dir_path:
            self.dir_label.setText(dir_path)
            self.dir_label.setToolTip(dir_path)
            
            # Count audio files
            audio_files = self._find_audio_files(Path(dir_path))
            self.log_output.append(f"📁 Selected directory: {dir_path}")
            self.log_output.append(f"🎵 Found {len(audio_files)} audio files")
            
    def _find_audio_files(self, directory: Path) -> List[Path]:
        """Find all audio files in directory"""
        audio_extensions = {'.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a'}
        audio_files = []
        
        for ext in audio_extensions:
            audio_files.extend(directory.glob(f"**/*{ext}"))
            
        return audio_files
        
    def _start_analysis(self):
        """Start enhanced analysis"""
        if self.worker and self.worker.isRunning():
            QMessageBox.warning(self, "Analysis in Progress", "Please wait for current analysis to complete")
            return
            
        dir_text = self.dir_label.text()
        if dir_text == "No directory selected":
            QMessageBox.warning(self, "No Directory", "Please select an audio directory first")
            return
            
        directory = Path(dir_text)
        if not directory.exists():
            QMessageBox.warning(self, "Invalid Directory", "Selected directory does not exist")
            return
            
        # Find audio files
        audio_files = self._find_audio_files(directory)
        if not audio_files:
            QMessageBox.information(self, "No Audio Files", "No supported audio files found in directory")
            return
            
        # Update settings
        self._update_settings()
        
        # Clear previous results
        self._clear_results()
        
        # Start analysis
        self.log_output.append(f"🚀 Starting enhanced analysis of {len(audio_files)} files...")
        
        self.worker = EnhancedAnalyzeWorker(
            [str(f) for f in audio_files],
            self.enhanced_analyzer,
            self.settings
        )
        
        # Connect worker signals
        self.worker.progress.connect(self._on_progress)
        self.worker.log.connect(self._on_log)
        self.worker.done.connect(self._on_analysis_done)
        self.worker.track_analyzed.connect(self._on_track_analyzed)
        self.worker.llm_progress.connect(self._on_llm_progress)
        self.worker.error.connect(self._on_error)
        
        # Update UI state
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setValue(0)
        
        self.worker.start()
        
    def _stop_analysis(self):
        """Stop current analysis"""
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.log_output.append("🛑 Stopping analysis...")
            
    def _update_settings(self):
        """Update analysis settings from UI"""
        self.settings.enable_hamms_v3 = self.hamms_checkbox.isChecked()
        self.settings.enable_ai = self.ai_checkbox.isChecked() and self.ai_available
        self.settings.force_reanalysis = self.force_checkbox.isChecked()
        
    def _on_progress(self, current: int, total: int):
        """Handle analysis progress update"""
        if total > 0:
            percent = int((current / total) * 100)
            self.progress_bar.setValue(percent)
            self.progress_label.setText(f"Analyzing... {current}/{total} files")
            
    def _on_log(self, message: str):
        """Handle log message"""
        self.log_output.append(message)
        # Auto-scroll to bottom
        scrollbar = self.log_output.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
        
    def _on_track_analyzed(self, track_path: str, analysis_data: Dict[str, Any]):
        """Handle individual track analysis completion"""
        # Add to radar chart if it's visible
        if self.tab_widget.currentIndex() == 1:  # Visualization tab
            try:
                # Get title from analysis data or fallback to filename
                title = analysis_data.get('title') or Path(track_path).stem
                artist = analysis_data.get('artist')
                display_name = f"{artist} - {title}" if artist else title
                
                self.radar_widget.load_track_data(
                    track_path,
                    analysis_data['hamms_vector'],
                    {'title': display_name}
                )
            except Exception as e:
                self.log_output.append(f"⚠️ Failed to update visualization: {e}")
                
    def _on_llm_progress(self, track_path: str, provider: str, status: str):
        """Handle LLM progress updates"""
        filename = Path(track_path).name
        if status == "analyzing":
            self.llm_status_label.setText(f"🤖 AI enriching {filename} with {provider.title()}...")
        elif status == "success":
            self.llm_status_label.setText(f"✅ {filename} enriched with {provider.title()}")
        elif status == "failed":
            self.llm_status_label.setText(f"⚠️ {provider.title()} failed, trying fallback...")
        elif status == "complete":
            self.llm_status_label.setText("")
                
    def _on_analysis_done(self, results: List[EnhancedAnalysisResult]):
        """Handle analysis completion"""
        self.current_results = results
        
        # Update UI state
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.export_btn.setEnabled(True)
        
        # Populate results table
        self._populate_results_table(results)
        
        # Show summary
        successful = sum(1 for r in results if r.success)
        ai_enriched = sum(1 for r in results if r.success and r.genre is not None)
        
        self.log_output.append(f"✅ Analysis complete!")
        self.log_output.append(f"   • {successful}/{len(results)} tracks analyzed successfully")
        self.log_output.append(f"   • {ai_enriched}/{successful} tracks AI-enriched")
        
        # Switch to results tab
        self.tab_widget.setCurrentIndex(2)
        
    def _on_error(self, error_message: str):
        """Handle analysis error"""
        self.log_output.append(f"❌ Error: {error_message}")
        
        # Reset UI state
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        
        QMessageBox.critical(self, "Analysis Error", error_message)
        
    def _populate_results_table(self, results: List[EnhancedAnalysisResult]):
        """Populate the results table with analysis data"""
        self.results_table.setRowCount(len(results))
        
        for row, result in enumerate(results):
            # Use metadata from result, fallback to filename
            track_name = result.title or Path(result.track_path).name
            
            # Extract artist from result
            artist = result.artist or "Unknown"
            
            # Extract key from result or HAMMS analysis
            key = result.key or "N/A"
            if key == "N/A" and result.hamms_dimensions.get('key'):
                # Convert normalized key to musical key if possible
                key_val = result.hamms_dimensions.get('key', 0)
                if key_val > 0:
                    # Simple key mapping (this could be enhanced)
                    keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
                    key_idx = int(key_val * 12) % 12
                    key = keys[key_idx]
            
            # Use actual BPM from analysis result
            bpm = "N/A"
            if hasattr(result, 'bpm') and result.bpm:
                bpm = str(int(result.bpm))
            elif result.hamms_dimensions.get('bpm'):
                # BPM from HAMMS is already in correct range, not normalized
                bpm = str(int(result.hamms_dimensions.get('bpm', 0)))
            
            items = [
                track_name,
                artist,
                result.genre or "N/A",
                result.subgenre or "N/A",
                result.mood or "N/A",
                result.era or "N/A", 
                bpm,
                key,
                f"{result.hamms_dimensions.get('energy', 0):.2f}" if result.hamms_dimensions.get('energy') else "N/A",
                f"{result.hamms_confidence:.2f}" if result.hamms_confidence else "0.00",
                f"{result.ai_confidence:.2f}" if result.ai_confidence else "N/A",
                "✓ Success" if result.success else f"✗ {result.error_message or 'Failed'}"
            ]
            
            for col, item_text in enumerate(items):
                item = QTableWidgetItem(str(item_text))
                self.results_table.setItem(row, col, item)
                
        # Enable controls
        self.visualize_selected_btn.setEnabled(True)
        self.compare_btn.setEnabled(True)
        
    def _on_selection_changed(self):
        """Handle results table selection change"""
        selected_rows = set()
        for item in self.results_table.selectedItems():
            selected_rows.add(item.row())
            
        # Update button states
        has_selection = len(selected_rows) > 0
        self.visualize_selected_btn.setEnabled(has_selection)
        
    def _visualize_selected(self):
        """Visualize selected tracks in radar chart"""
        selected_rows = set()
        for item in self.results_table.selectedItems():
            selected_rows.add(item.row())
            
        if not selected_rows:
            return
            
        # Clear existing chart data
        self.radar_widget.clear_tracks()
        
        # Add selected tracks to visualization
        for row in selected_rows:
            if row < len(self.current_results):
                result = self.current_results[row]
                if result.success:
                    track_name = Path(result.track_path).name
                    try:
                        self.radar_widget.load_track_data(
                            result.track_path,
                            result.hamms_vector,
                            {'title': track_name}
                        )
                    except Exception as e:
                        self.log_output.append(f"⚠️ Failed to load {track_name}: {e}")
                        
        # Switch to visualization tab
        self.tab_widget.setCurrentIndex(1)
        
    def _toggle_comparison(self):
        """Toggle comparison mode in radar chart"""
        # Enable comparison mode for radar chart
        self.radar_widget.comparison_checkbox.setChecked(True)
        
    def _clear_results(self):
        """Clear analysis results"""
        self.current_results.clear()
        self.results_table.setRowCount(0)
        self.radar_widget.clear_tracks()
        self.log_output.clear()
        self.progress_bar.setValue(0)
        self.progress_label.setText("Ready to analyze...")
        self.llm_status_label.setText("")
        
        # Reset button states
        self.export_btn.setEnabled(False)
        self.visualize_selected_btn.setEnabled(False)
        self.compare_btn.setEnabled(False)
        
    def _export_results(self):
        """Export analysis results to CSV"""
        if not self.current_results:
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Analysis Results",
            f"music_analysis_enhanced_{self._get_timestamp()}.csv",
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if file_path:
            try:
                self._export_to_csv(file_path)
                QMessageBox.information(self, "Export Complete", f"Results exported to:\n{file_path}")
                self.log_output.append(f"📊 Results exported to: {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export results:\n{str(e)}")
                
    def _export_to_csv(self, file_path: str):
        """Export results to CSV file"""
        import csv
        
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Header
            header = [
                'Track Path', 'Title', 'Artist', 'Album', 'BPM', 'Key', 'Success', 'Genre', 'Subgenre', 'Mood', 'Era',
                'Tags', 'HAMMS Confidence', 'AI Confidence', 'Processing Time (ms)',
                'HAMMS Vector', 'Error Message'
            ]
            writer.writerow(header)
            
            # Data rows
            for result in self.current_results:
                track_name = result.title or Path(result.track_path).name
                tags_str = ', '.join(result.tags) if result.tags else ''
                hamms_str = ', '.join(f'{v:.4f}' for v in result.hamms_vector) if result.hamms_vector else ''
                
                row = [
                    result.track_path,
                    track_name,
                    result.artist or '',
                    result.album or '',
                    result.bpm or '',
                    result.key or '',
                    result.success,
                    result.genre or '',
                    result.subgenre or '',
                    result.mood or '',
                    result.era or '',
                    tags_str,
                    result.hamms_confidence or 0.0,
                    result.ai_confidence or 0.0,
                    result.processing_time_ms,
                    hamms_str,
                    result.error_message or ''
                ]
                writer.writerow(row)
                
    def _get_timestamp(self) -> str:
        """Get current timestamp for file naming"""
        from datetime import datetime
        return datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def closeEvent(self, event):
        """Handle window close event"""
        if self.worker and self.worker.isRunning():
            reply = QMessageBox.question(
                self,
                "Analysis in Progress",
                "Analysis is still running. Stop and exit?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.worker.stop()
                self.worker.wait(3000)  # Wait up to 3 seconds
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


    def _create_library_analytics_tab(self) -> QWidget:
        """Create the library analytics tab with subgenre filters and insights"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(2, 2, 2, 2)  # Minimal margins
        layout.setSpacing(2)  # Minimal spacing
        
        # Header with refresh button
        header_layout = QHBoxLayout()
        
        title = QLabel("📈 Library Analytics & Subgenre Intelligence")
        title.setStyleSheet("""
            font-size: 18px; 
            font-weight: bold; 
            color: #000000;
            background-color: #ffffff;
            padding: 12px 16px;
            border-radius: 8px;
            border: 3px solid #000000;
            margin-bottom: 10px;
        """)
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        self.refresh_analytics_btn = QPushButton("🔄 Refresh Analytics")
        self.refresh_analytics_btn.clicked.connect(self._refresh_library_analytics)
        self.refresh_analytics_btn.setStyleSheet("""
            QPushButton {
                background-color: #228b22;
                color: #ffffff;
                border: 3px solid #000000;
                padding: 10px 18px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #1e6b1e;
            }
            QPushButton:pressed {
                background: #388e3c;
            }
        """)
        header_layout.addWidget(self.refresh_analytics_btn)
        
        layout.addLayout(header_layout)
        
        # Create main content splitter
        content_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel: Controls and filters
        left_panel = self._create_analytics_controls_panel()
        content_splitter.addWidget(left_panel)
        
        # Right panel: Analytics display
        right_panel = self._create_analytics_display_panel()
        content_splitter.addWidget(right_panel)
        
        # Set splitter proportions
        content_splitter.setStretchFactor(0, 1)  # Controls panel
        content_splitter.setStretchFactor(1, 2)  # Display panel
        
        layout.addWidget(content_splitter)
        
        return tab
    
    def _create_analytics_controls_panel(self) -> QWidget:
        """Create the analytics controls and filters panel"""
        panel = QWidget()
        panel.setMaximumWidth(280)  # Further reduced width for maximum display space
        panel.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                color: #000000;
            }
        """)
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(1, 1, 1, 1)  # Ultra minimal margins
        layout.setSpacing(2)  # Ultra reduced spacing
        
        # Subgenre filter section
        subgenre_group = QGroupBox("🎵 Subgenre Filters")
        subgenre_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #000000;
                background-color: #ffffff;
                border: 3px solid #000000;
                border-radius: 8px;
                padding-top: 15px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #000000;
                background-color: #ffffff;
            }
        """)
        subgenre_layout = QVBoxLayout(subgenre_group)
        
        # Filter by subgenre dropdown
        filter_layout = QHBoxLayout()
        filter_label = QLabel("Filter by:")
        filter_label.setStyleSheet("color: #000000; font-weight: bold; background-color: #ffffff;")
        filter_layout.addWidget(filter_label)
        self.subgenre_filter_combo = QComboBox()
        self.subgenre_filter_combo.addItem("All Subgenres")
        self.subgenre_filter_combo.setStyleSheet("""
            QComboBox {
                color: #000000;
                background-color: #ffffff;
                border: 2px solid #000000;
                border-radius: 4px;
                padding: 5px;
                font-weight: bold;
            }
            QComboBox::drop-down {
                border: none;
                background-color: #ffffff;
            }
            QComboBox::down-arrow {
                border: 2px solid #000000;
                background-color: #000000;
            }
        """)
        self.subgenre_filter_combo.currentTextChanged.connect(self._on_subgenre_filter_changed)
        filter_layout.addWidget(self.subgenre_filter_combo)
        subgenre_layout.addLayout(filter_layout)
        
        # Top subgenres list
        subgenres_label = QLabel("Top Subgenres:")
        subgenres_label.setStyleSheet("color: #000000; font-weight: bold; background-color: #ffffff;")
        subgenre_layout.addWidget(subgenres_label)
        self.subgenres_list = QListWidget()
        self.subgenres_list.setMaximumHeight(120)  # Reduced height
        self.subgenres_list.setStyleSheet("""
            QListWidget {
                color: #000000;
                background-color: #ffffff;
                border: 3px solid #000000;
                border-radius: 6px;
                font-weight: bold;
                selection-background-color: #0066cc;
                selection-color: #ffffff;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid #dddddd;
            }
            QListWidget::item:hover {
                background-color: #f0f8ff;
            }
            QListWidget::item:selected {
                background-color: #0066cc;
                color: #ffffff;
            }
        """)
        self.subgenres_list.itemClicked.connect(self._on_subgenre_selected)
        subgenre_layout.addWidget(self.subgenres_list)
        
        layout.addWidget(subgenre_group)
        
        # Analytics options section
        options_group = QGroupBox("📊 Analytics Options")
        options_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #000000;
                background-color: #ffffff;
                border: 3px solid #000000;
                border-radius: 8px;
                padding-top: 15px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #000000;
                background-color: #ffffff;
            }
        """)
        options_layout = QVBoxLayout(options_group)
        
        self.show_compatibility_matrix = QCheckBox("Show Compatibility Matrix")
        self.show_compatibility_matrix.setChecked(True)
        self.show_compatibility_matrix.setStyleSheet("""
            QCheckBox {
                font-size: 13px;
                padding: 4px;
                color: #000000;
                font-weight: 500;
                background-color: #ffffff;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 3px;
                border: 2px solid #000000;
                background-color: #ffffff;
            }
            QCheckBox::indicator:checked {
                background-color: #0066cc;
                border: 2px solid #004499;
            }
        """)
        options_layout.addWidget(self.show_compatibility_matrix)
        
        self.show_hamms_clustering = QCheckBox("HAMMS Vector Clustering")
        self.show_hamms_clustering.setChecked(False)
        self.show_hamms_clustering.setStyleSheet(self.show_compatibility_matrix.styleSheet())
        options_layout.addWidget(self.show_hamms_clustering)
        
        self.show_mixing_suggestions = QCheckBox("DJ Mixing Suggestions")
        self.show_mixing_suggestions.setChecked(True)
        self.show_mixing_suggestions.setStyleSheet(self.show_compatibility_matrix.styleSheet())
        options_layout.addWidget(self.show_mixing_suggestions)
        
        layout.addWidget(options_group)
        
        # Playlist generation section
        playlist_group = QGroupBox("🎧 Enhanced Playlist Generation")
        playlist_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #000000;
                background-color: #ffffff;
                border: 3px solid #000000;
                border-radius: 8px;
                padding-top: 15px;
                margin-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 8px 0 8px;
                color: #000000;
                background-color: #ffffff;
            }
        """)
        playlist_layout = QVBoxLayout(playlist_group)
        
        # Seed track selection
        seed_label = QLabel("Seed Track:")
        seed_label.setStyleSheet("color: #000000; font-weight: bold; background-color: #ffffff;")
        playlist_layout.addWidget(seed_label)
        self.seed_track_combo = QComboBox()
        self.seed_track_combo.setStyleSheet("""
            QComboBox {
                color: #000000;
                background-color: #ffffff;
                border: 2px solid #000000;
                border-radius: 4px;
                padding: 5px;
                font-weight: bold;
            }
            QComboBox::drop-down {
                border: none;
                background-color: #ffffff;
            }
        """)
        playlist_layout.addWidget(self.seed_track_combo)
        
        # Playlist parameters
        params_layout = QHBoxLayout()
        length_label = QLabel("Length:")
        length_label.setStyleSheet("color: #000000; font-weight: bold; background-color: #ffffff;")
        params_layout.addWidget(length_label)
        self.playlist_length_combo = QComboBox()
        self.playlist_length_combo.addItems(["10", "15", "20", "25", "30"])
        self.playlist_length_combo.setCurrentText("20")
        self.playlist_length_combo.setStyleSheet(self.seed_track_combo.styleSheet())
        params_layout.addWidget(self.playlist_length_combo)
        
        # BPM tolerance control
        tolerance_label = QLabel("BPM Tolerance:")
        tolerance_label.setStyleSheet("color: #000000; font-weight: bold; background-color: #ffffff;")
        params_layout.addWidget(tolerance_label)
        self.bpm_tolerance_combo = QComboBox()
        self.bpm_tolerance_combo.addItems(["5%", "8%", "12%", "15%", "20%", "25%"])
        self.bpm_tolerance_combo.setCurrentText("15%")  # Default to adaptive tolerance
        self.bpm_tolerance_combo.setStyleSheet(self.seed_track_combo.styleSheet())
        params_layout.addWidget(self.bpm_tolerance_combo)
        
        playlist_layout.addLayout(params_layout)
        
        # Advanced playlist controls
        advanced_group = QGroupBox("🎛️ Advanced Cultural & Lyrics Weights")
        advanced_group.setCheckable(True)
        advanced_group.setChecked(False)  # Collapsed by default
        advanced_layout = QVBoxLayout(advanced_group)
        
        # Weight controls with sliders
        weights_grid = QGridLayout()
        
        # Cultural weight
        weights_grid.addWidget(QLabel("Cultural Context:"), 0, 0)
        self.cultural_weight_slider = QSlider(Qt.Orientation.Horizontal)
        self.cultural_weight_slider.setRange(0, 30)  # 0-30% (0.0-0.3)
        self.cultural_weight_slider.setValue(10)  # Default 10% (0.1)
        weights_grid.addWidget(self.cultural_weight_slider, 0, 1)
        self.cultural_weight_label = QLabel("10%")
        weights_grid.addWidget(self.cultural_weight_label, 0, 2)
        self.cultural_weight_slider.valueChanged.connect(
            lambda v: self.cultural_weight_label.setText(f"{v}%")
        )
        
        # Lyrics weight
        weights_grid.addWidget(QLabel("Lyrics Similarity:"), 1, 0)
        self.lyrics_weight_slider = QSlider(Qt.Orientation.Horizontal)
        self.lyrics_weight_slider.setRange(0, 30)  # 0-30% (0.0-0.3)
        self.lyrics_weight_slider.setValue(10)  # Default 10% (0.1)
        weights_grid.addWidget(self.lyrics_weight_slider, 1, 1)
        self.lyrics_weight_label = QLabel("10%")
        weights_grid.addWidget(self.lyrics_weight_label, 1, 2)
        self.lyrics_weight_slider.valueChanged.connect(
            lambda v: self.lyrics_weight_label.setText(f"{v}%")
        )
        
        # HAMMS weight (for reference, adjustable)
        weights_grid.addWidget(QLabel("HAMMS Similarity:"), 2, 0)
        self.hamms_weight_slider = QSlider(Qt.Orientation.Horizontal)
        self.hamms_weight_slider.setRange(20, 50)  # 20-50% (0.2-0.5)
        self.hamms_weight_slider.setValue(30)  # Default 30% (0.3)
        weights_grid.addWidget(self.hamms_weight_slider, 2, 1)
        self.hamms_weight_label = QLabel("30%")
        weights_grid.addWidget(self.hamms_weight_label, 2, 2)
        self.hamms_weight_slider.valueChanged.connect(
            lambda v: self.hamms_weight_label.setText(f"{v}%")
        )
        
        advanced_layout.addLayout(weights_grid)
        
        # Note about automatic normalization
        note_label = QLabel("💡 Note: Weights are automatically normalized to sum to 100%")
        note_label.setStyleSheet("color: #666; font-style: italic; font-size: 11px;")
        advanced_layout.addWidget(note_label)
        
        playlist_layout.addWidget(advanced_group)
        
        # Generate playlist button
        self.generate_playlist_btn = QPushButton("🎵 Generate Enhanced Playlist")
        self.generate_playlist_btn.clicked.connect(self._generate_enhanced_playlist)
        self.generate_playlist_btn.setProperty("class", "success")  # Use success style from theme
        playlist_layout.addWidget(self.generate_playlist_btn)
        
        # Export playlist button  
        self.export_playlist_btn = QPushButton("💾 Export Playlist")
        self.export_playlist_btn.clicked.connect(self._export_playlist)
        self.export_playlist_btn.setEnabled(False)  # Disabled until playlist is generated
        self.export_playlist_btn.setProperty("class", "primary")
        playlist_layout.addWidget(self.export_playlist_btn)
        
        layout.addWidget(playlist_group)
        
        layout.addStretch()
        
        return panel
    
    def _create_analytics_display_panel(self) -> QWidget:
        """Create the analytics display panel"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(1, 1, 1, 1)  # Ultra minimal margins
        layout.setSpacing(2)  # Ultra reduced spacing
        
        # Analytics display area with tabs
        self.analytics_tab_widget = QTabWidget()
        
        # Overview tab
        self.overview_tab = self._create_overview_analytics_tab()
        self.analytics_tab_widget.addTab(self.overview_tab, "📊 Overview")
        
        # Subgenre details tab
        self.subgenre_details_tab = self._create_subgenre_details_tab()
        self.analytics_tab_widget.addTab(self.subgenre_details_tab, "🎵 Subgenre Analysis")
        
        # Compatibility matrix tab
        self.compatibility_tab = self._create_compatibility_matrix_tab()
        self.analytics_tab_widget.addTab(self.compatibility_tab, "🔗 Compatibility")
        
        # Playlist results tab
        self.playlist_results_tab = self._create_playlist_results_tab()
        self.analytics_tab_widget.addTab(self.playlist_results_tab, "🎧 Playlist")
        
        layout.addWidget(self.analytics_tab_widget)
        
        return panel
    
    def _create_overview_analytics_tab(self) -> QWidget:
        """Create overview analytics tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Scroll area for analytics content
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        self.analytics_content = QTextEdit()
        self.analytics_content.setReadOnly(True)
        self.analytics_content.setPlainText("Click 'Refresh Analytics' to analyze your library...")
        self.analytics_content.setStyleSheet("""
            font-family: 'Monaco', 'Courier New', monospace;
            font-size: 11px;
            color: #000000;
            background-color: #ffffff;
            border: 3px solid #000000;
            border-radius: 6px;
            padding: 12px;
            line-height: 1.5;
        """)
        
        scroll.setWidget(self.analytics_content)
        layout.addWidget(scroll)
        
        return tab
    
    def _create_subgenre_details_tab(self) -> QWidget:
        """Create subgenre details tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        self.subgenre_details = QTextEdit()
        self.subgenre_details.setReadOnly(True)
        self.subgenre_details.setPlainText("Select a subgenre from the list to see detailed analysis...")
        self.subgenre_details.setStyleSheet("""
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 12px;
            background-color: #ffffff;
            border: 2px solid #000000;
            border-radius: 6px;
            padding: 12px;
            line-height: 1.5;
        """)
        
        layout.addWidget(self.subgenre_details)
        
        return tab
    
    def _create_compatibility_matrix_tab(self) -> QWidget:
        """Create compatibility matrix tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Compatibility table
        self.compatibility_table = QTableWidget()
        self.compatibility_table.setAlternatingRowColors(True)
        self.compatibility_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.compatibility_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #000000;
                background-color: white;
                alternate-background-color: #f8f8f8;
                border: 2px solid #000000;
                border-radius: 6px;
                font-size: 12px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #000000;
            }
            QTableWidget::item:selected {
                background-color: #007acc;
                color: #000000;
            }
            QHeaderView::section {
                background-color: #ffffff;
                padding: 8px;
                border: 1px solid #000000;
                font-weight: bold;
                color: #000000;
            }
        """)
        
        layout.addWidget(QLabel("🔗 Subgenre Compatibility Matrix"))
        layout.addWidget(self.compatibility_table)
        
        return tab
    
    def _create_playlist_results_tab(self) -> QWidget:
        """Create playlist results tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        layout.addWidget(QLabel("🎧 Generated Playlist Results"))
        
        self.playlist_results = QTextEdit()
        self.playlist_results.setReadOnly(True)
        self.playlist_results.setPlainText(
            "🎵 ENHANCED PLAYLIST GENERATOR\n\n"
            "📋 HOW TO GENERATE A PLAYLIST:\n\n"
            "1. 🔍 First, analyze your music collection:\n"
            "   • Go to 'Enhanced Analysis' tab\n"
            "   • Select a folder with music files\n"
            "   • Click 'Start Enhanced Analysis'\n\n"
            "2. 🎯 Select a seed track:\n"
            "   • Choose from the dropdown above\n"
            "   • This determines the playlist style\n\n"
            "3. ⚙️ Adjust settings (optional):\n"
            "   • Set playlist length (5-50 tracks)\n"
            "   • Choose subgenre filter for focus\n\n"
            "4. 🎵 Click 'Generate Enhanced Playlist'\n\n"
            "✨ The algorithm uses HAMMS v3.0 analysis and AI to create\n"
            "   perfectly compatible playlists based on:\n"
            "   • Musical harmony and energy\n"
            "   • BPM and key compatibility  \n"
            "   • Genre and mood similarity\n"
            "   • Advanced audio features\n\n"
            "💡 Start by analyzing some music files!"
        )
        self.playlist_results.setStyleSheet("""
            font-family: 'Monaco', 'Courier New', monospace;
            font-size: 11px;
            color: #000000;
            background-color: #ffffff;
            border: 3px solid #000000;
            border-radius: 6px;
            padding: 12px;
            line-height: 1.5;
        """)
        
        layout.addWidget(self.playlist_results)
        
        return tab
    
    def _refresh_library_analytics(self):
        """Refresh library analytics and update displays"""
        try:
            self.analytics_content.setPlainText("🔄 Analyzing library...")
            self.status_bar.showMessage("Running library analytics...")
            
            # Run library analysis
            analytics = self.library_analyzer.analyze_library(include_hamms_clustering=False)
            
            # Update overview display
            self._display_analytics_overview(analytics)
            
            # Update subgenre filter dropdown and list
            self._update_subgenre_controls(analytics)
            
            # Update compatibility matrix
            self._update_compatibility_matrix(analytics)
            
            # Update seed track combo
            self._update_seed_tracks()
            
            self.status_bar.showMessage(f"Analytics complete - Quality Score: {analytics.collection_quality_score}/100")
            
        except Exception as e:
            self.analytics_content.setPlainText(f"❌ Analytics failed: {str(e)}")
            self.status_bar.showMessage("Analytics failed")
    
    def _display_analytics_overview(self, analytics: LibraryAnalytics):
        """Display analytics overview"""
        report = []
        report.append("=" * 60)
        report.append("🔍 LIBRARY ANALYTICS REPORT")
        report.append("=" * 60)
        report.append("")
        
        # Overview stats
        report.append("📊 OVERVIEW")
        report.append(f"Total Tracks: {analytics.total_tracks}")
        report.append(f"Analyzed Tracks: {analytics.analyzed_tracks} ({analytics.hamms_coverage:.1%})")
        report.append(f"AI Analyzed: {analytics.ai_analyzed_tracks} ({analytics.ai_coverage:.1%})")
        report.append(f"Total Genres: {analytics.total_genres}")
        report.append(f"Total Subgenres: {analytics.total_subgenres}")
        report.append(f"Collection Quality Score: {analytics.collection_quality_score:.1f}/100")
        report.append("")
        
        # Top genres
        report.append("🎵 TOP GENRES")
        for genre in analytics.genre_distribution[:5]:
            avg_bpm = f"{genre.avg_bpm:.1f}" if genre.avg_bpm else "N/A"
            report.append(f"  {genre.name}: {genre.track_count} tracks ({genre.percentage:.1f}%) - Avg BPM: {avg_bpm}")
        report.append("")
        
        # Top subgenres
        report.append("🎼 TOP SUBGENRES")
        for subgenre in analytics.subgenre_distribution[:5]:
            report.append(f"  {subgenre.name}: {subgenre.track_count} tracks ({subgenre.percentage:.1f}%)")
            if subgenre.compatibility_scores:
                top_compat = max(subgenre.compatibility_scores.items(), key=lambda x: x[1])
                report.append(f"    → Best mix with: {top_compat[0]} (compatibility: {top_compat[1]:.2f})")
        report.append("")
        
        # Technical analysis
        report.append("⚡ TECHNICAL ANALYSIS")
        if analytics.bpm_analysis['count'] > 0:
            report.append(f"BPM Range: {analytics.bpm_analysis['min']:.1f} - {analytics.bpm_analysis['max']:.1f} (avg: {analytics.bpm_analysis['avg']:.1f})")
        if analytics.energy_analysis['count'] > 0:
            report.append(f"Energy Range: {analytics.energy_analysis['min']:.2f} - {analytics.energy_analysis['max']:.2f} (avg: {analytics.energy_analysis['avg']:.2f})")
        report.append("")
        
        # Compatible pairs
        report.append("🔗 TOP COMPATIBLE PAIRS")
        for pair in analytics.top_compatible_pairs[:5]:
            report.append(f"  {pair[0]} ↔ {pair[1]}: {pair[2]:.2f} compatibility")
        report.append("")
        
        # Recommendations
        report.append("💡 MIXING RECOMMENDATIONS")
        for rec in analytics.mixing_recommendations[:3]:
            report.append(f"  • {rec['recommendation']}")
        
        report.append("=" * 60)
        
        self.analytics_content.setPlainText("\n".join(report))
    
    def _update_subgenre_controls(self, analytics: LibraryAnalytics):
        """Update subgenre filter controls using existing database data"""
        # Update dropdown - get subgenres directly from database
        self.subgenre_filter_combo.clear()
        self.subgenre_filter_combo.addItem("All Subgenres")
        
        try:
            # Get available subgenres directly from database
            available_subgenres = self.storage.get_available_subgenres()
            
            # Filter out empty/invalid subgenres
            valid_subgenres = []
            for sg in available_subgenres:
                if sg and sg.strip() and sg.lower() not in ['unknown', 'none', '']:
                    valid_subgenres.append(sg)
            
            # Add valid subgenres to combo box
            if valid_subgenres:
                # Sort subgenres alphabetically
                valid_subgenres.sort()
                self.subgenre_filter_combo.addItems(valid_subgenres)
                print(f"✅ Loaded {len(valid_subgenres)} subgenres for filtering")
            
            # Update list widget
            self.subgenres_list.clear()
            
            if valid_subgenres:
                # Show analytics data if available, otherwise show database counts
                if analytics.subgenre_distribution:
                    for subgenre in analytics.subgenre_distribution[:10]:  # Top 10
                        if subgenre.name and subgenre.name.strip() and subgenre.name.lower() not in ['unknown', 'none', '']:
                            item_text = f"{subgenre.name} ({subgenre.track_count} tracks)"
                            self.subgenres_list.addItem(item_text)
                else:
                    # Fallback: show available subgenres from database
                    for sg in valid_subgenres[:10]:  # Top 10
                        # Get count for this subgenre
                        subgenre_tracks = self.storage.get_tracks_with_ai_analysis(subgenre_filter=sg)
                        item_text = f"{sg} ({len(subgenre_tracks)} tracks)"
                        self.subgenres_list.addItem(item_text)
            else:
                self.subgenres_list.addItem("No subgenre data found in database")
                
        except Exception as e:
            print(f"❌ Error loading subgenres: {e}")
            self.subgenre_filter_combo.addItem("Error loading subgenres")
            self.subgenres_list.addItem(f"Error: {str(e)}")
    
    def _update_compatibility_matrix(self, analytics: LibraryAnalytics):
        """Update compatibility matrix table"""
        if not analytics.top_compatible_pairs:
            return
            
        self.compatibility_table.setRowCount(len(analytics.top_compatible_pairs))
        self.compatibility_table.setColumnCount(3)
        self.compatibility_table.setHorizontalHeaderLabels(["Subgenre 1", "Subgenre 2", "Compatibility"])
        
        for i, (sg1, sg2, score) in enumerate(analytics.top_compatible_pairs):
            self.compatibility_table.setItem(i, 0, QTableWidgetItem(sg1))
            self.compatibility_table.setItem(i, 1, QTableWidgetItem(sg2))
            self.compatibility_table.setItem(i, 2, QTableWidgetItem(f"{score:.3f}"))
        
        self.compatibility_table.resizeColumnsToContents()
    
    def _update_seed_tracks(self):
        """Update seed track selection with enhanced user feedback"""
        self.seed_track_combo.clear()
        
        try:
            tracks = self.storage.list_all_analyses()[:50]  # Limit to 50 for performance
            
            # Debug: Print first few tracks
            print(f"DEBUG: Found {len(tracks)} tracks for seed dropdown")
            for i, track in enumerate(tracks[:3]):
                print(f"DEBUG Seed Track {i}: title={track.get('title')}, artist={track.get('artist')}, path={track.get('path')}")
            
            if not tracks:
                # No tracks analyzed yet
                self.seed_track_combo.addItem("📋 No analyzed tracks available - Please run analysis first", None)
                self.generate_playlist_btn.setEnabled(False)
                self.generate_playlist_btn.setText("🚫 Analysis Required")
                return
            
            # Add helpful instruction as first item
            self.seed_track_combo.addItem("🎯 Select a seed track to start playlist generation...", None)
            
            for track in tracks:
                artist = track.get('artist') or ''
                title = track.get('title') or ''
                path = track.get('path', '')
                
                # If we have artist and title, use them
                if artist and title:
                    display_name = f"{artist} - {title}"
                # If we have only title, show it
                elif title:
                    display_name = title
                # If we have only artist, show it
                elif artist:
                    display_name = f"{artist} - [Unknown Title]"
                # Otherwise, use filename
                else:
                    from pathlib import Path
                    filename = Path(path).stem if path else "Unknown Track"
                    display_name = filename
                    
                self.seed_track_combo.addItem(display_name, path)
            
            # Enable playlist generation and update button text
            self.generate_playlist_btn.setEnabled(True)
            self.generate_playlist_btn.setText("🎵 Generate Enhanced Playlist")
            
        except Exception as e:
            print(f"Error loading seed tracks: {e}")
            self.seed_track_combo.addItem("❌ Error loading tracks", None)
            self.generate_playlist_btn.setEnabled(False)
    
    def _on_subgenre_filter_changed(self, subgenre: str):
        """Handle subgenre filter change"""
        if subgenre == "All Subgenres":
            self.subgenre_details.setPlainText("Showing all subgenres. Select a specific subgenre for detailed analysis.")
        else:
            self._show_subgenre_details(subgenre)
    
    def _on_subgenre_selected(self, item):
        """Handle subgenre selection from list"""
        item_text = item.text()
        subgenre_name = item_text.split(" (")[0]  # Extract subgenre name
        self.subgenre_filter_combo.setCurrentText(subgenre_name)
    
    def _show_subgenre_details(self, subgenre: str):
        """Show detailed analysis for a specific subgenre"""
        try:
            # Get tracks for this subgenre
            tracks = self.storage.get_tracks_with_ai_analysis(subgenre_filter=subgenre)
            
            # Debug: Print first few tracks to understand data structure
            print(f"DEBUG: Subgenre {subgenre} has {len(tracks)} tracks")
            for i, track in enumerate(tracks[:3]):
                print(f"DEBUG Track {i}: title={track.get('title')}, artist={track.get('artist')}, path={track.get('path')}")
            
            if not tracks:
                self.subgenre_details.setPlainText(f"No tracks found for subgenre: {subgenre}")
                return
            
            details = []
            details.append(f"🎵 SUBGENRE ANALYSIS: {subgenre}")
            details.append("=" * 50)
            details.append(f"Total Tracks: {len(tracks)}")
            details.append("")
            
            # Calculate averages
            bpms = [t.get('bpm') for t in tracks if t.get('bpm')]
            energies = [t.get('energy') for t in tracks if t.get('energy')]
            eras = [t.get('era') for t in tracks if t.get('era')]
            
            if bpms:
                details.append(f"Average BPM: {sum(bpms)/len(bpms):.1f}")
                details.append(f"BPM Range: {min(bpms):.1f} - {max(bpms):.1f}")
            
            if energies:
                details.append(f"Average Energy: {sum(energies)/len(energies):.2f}")
            
            if eras:
                era_counts = {}
                for era in eras:
                    era_counts[era] = era_counts.get(era, 0) + 1
                details.append(f"Most common era: {max(era_counts.items(), key=lambda x: x[1])[0]}")
            
            details.append("")
            details.append("📀 TRACKS:")
            for track in tracks[:10]:  # Show first 10 tracks
                artist = track.get('artist') or None
                title = track.get('title') or None  
                path = track.get('path', '')
                bpm = track.get('bpm', 0)
                
                # Use intelligent name formatting
                if artist and title:
                    display_name = f"{artist} - {title}"
                elif title:
                    display_name = title
                elif artist:
                    display_name = f"{artist} - [Unknown Title]"
                elif path:
                    from pathlib import Path
                    display_name = Path(path).stem
                else:
                    display_name = "Unknown Track"
                    
                details.append(f"  • {display_name} ({bpm:.1f} BPM)")
            
            if len(tracks) > 10:
                details.append(f"  ... and {len(tracks) - 10} more tracks")
            
            self.subgenre_details.setPlainText("\n".join(details))
            
        except Exception as e:
            self.subgenre_details.setPlainText(f"Error analyzing subgenre: {str(e)}")
    
    def _generate_enhanced_playlist(self):
        """Generate enhanced playlist using HAMMS v3.0 and subgenre intelligence"""
        try:
            # Comprehensive validation
            seed_path = self.seed_track_combo.currentData()
            if not seed_path:
                self.playlist_results.setPlainText(
                    "⚠️ PLAYLIST GENERATION GUIDE:\n\n"
                    "1. 📋 First, run analysis on your music collection\n"
                    "2. 🎯 Select a seed track from the dropdown above\n"
                    "3. ⚙️ Adjust length and filters (optional)\n"
                    "4. 🎵 Click this button to generate playlist\n\n"
                    "💡 The seed track determines the musical style and energy of your playlist."
                )
                return
            
            # Check if we have enough tracks for the requested length
            all_tracks = self.storage.list_all_analyses()
            length = int(self.playlist_length_combo.currentText())
            
            if len(all_tracks) < 5:
                self.playlist_results.setPlainText(
                    f"❌ INSUFFICIENT TRACKS:\n\n"
                    f"Only {len(all_tracks)} tracks analyzed, but need at least 5 for playlist generation.\n\n"
                    f"📋 Please analyze more tracks first in the 'Enhanced Analysis' tab."
                )
                return
            
            if length > len(all_tracks):
                self.playlist_results.setPlainText(
                    f"⚠️ PLAYLIST LENGTH ADJUSTED:\n\n"
                    f"Requested: {length} tracks\n"
                    f"Available: {len(all_tracks)} tracks\n\n"
                    f"Generating playlist with {min(length, len(all_tracks))} tracks instead."
                )
                length = min(length, len(all_tracks))
            
            # Get selected subgenre filter
            subgenre_focus = None
            current_filter = self.subgenre_filter_combo.currentText()
            if current_filter != "All Subgenres":
                subgenre_focus = current_filter
            
            # Get BPM tolerance from UI
            tolerance_text = self.bpm_tolerance_combo.currentText()
            bpm_tolerance = float(tolerance_text.rstrip('%')) / 100.0  # Convert "15%" to 0.15
            
            # Show progress
            self.playlist_results.setPlainText(
                f"🎵 GENERATING ENHANCED PLAYLIST...\n\n"
                f"🎯 Seed Track: {self.seed_track_combo.currentText()}\n"
                f"📏 Target Length: {length} tracks\n"
                f"🏷️ Subgenre Focus: {subgenre_focus or 'All Genres'}\n"
                f"🎵 BPM Tolerance: {tolerance_text}\n\n"
                f"⏳ Please wait while we analyze compatibility..."
            )
            self.generate_playlist_btn.setEnabled(False)
            self.generate_playlist_btn.setText("⏳ Generating...")
            
            # Generate playlist using enhanced algorithm
            playlist = self.analyzer.generate_enhanced_playlist_with_hamms(
                seed_path=seed_path,
                target_length=length,
                subgenre_focus=subgenre_focus,
                curve="ascending",
                bpm_tolerance=bpm_tolerance
            )
            
            # Display results with enhanced formatting
            if playlist and len(playlist) > 0:
                # Store playlist for export functionality
                self.current_playlist = playlist
                self.current_seed_track = self.seed_track_combo.currentText()
                self.current_subgenre_focus = subgenre_focus
                
                results = []
                results.append("✨ ENHANCED PLAYLIST GENERATED!")
                results.append("=" * 50)
                results.append(f"🎯 Seed Track: {self.seed_track_combo.currentText()}")
                results.append(f"📏 Length: {len(playlist)} tracks")
                if subgenre_focus:
                    results.append(f"🏷️ Subgenre Focus: {subgenre_focus}")
                
                # Calculate some statistics
                bpms = [track.get('bpm', 0) for track in playlist if track.get('bpm')]
                avg_bpm = sum(bpms) / len(bpms) if bpms else 0
                subgenres = set(track.get('subgenre', 'Unknown') for track in playlist)
                
                results.append(f"🎼 Average BPM: {avg_bpm:.1f}")
                results.append(f"🎵 Subgenres: {', '.join(list(subgenres)[:3])}" + ("..." if len(subgenres) > 3 else ""))
                results.append("")
                results.append("📋 PLAYLIST:")
                results.append("-" * 30)
                
                for i, track in enumerate(playlist, 1):
                    artist = track.get('artist') or ''
                    title = track.get('title') or ''
                    path = track.get('path', '')
                    bpm = track.get('bpm', 0)
                    subgenre = track.get('subgenre', 'Unknown')
                    energy = track.get('energy', 0)
                    
                    # Apply intelligent name fallback (same as _update_seed_tracks)
                    if artist and title:
                        display_name = f"{artist} - {title}"
                    elif title:
                        display_name = title
                    elif artist:
                        display_name = f"{artist} - [Unknown Title]"
                    else:
                        # Extract from filename as fallback
                        from pathlib import Path
                        filename = Path(path).stem if path else "Unknown Track"
                        display_name = filename
                    
                    # Calculate BPM difference from previous track
                    bpm_diff_text = ""
                    if i > 1 and bpm > 0:
                        prev_bpm = playlist[i-2].get('bpm', 0)
                        if prev_bpm > 0:
                            bpm_diff = bpm - prev_bpm
                            sign = "+" if bpm_diff > 0 else ""
                            bpm_diff_text = f" ({sign}{bpm_diff:.1f})"
                    
                    # Format track entry with better layout
                    results.append(f"{i:2d}. 🎵 {display_name}")
                    details = f"     🏷️ {subgenre} | 🥁 {bpm:.1f} BPM{bpm_diff_text}"
                    if energy:
                        details += f" | ⚡ Energy: {energy:.2f}"
                    results.append(details)
                    results.append("")
                
                # Add helpful footer
                results.append("-" * 50)
                results.append("💡 Tips:")
                results.append("• Use different seed tracks for varied playlists")
                results.append("• Adjust subgenre filter for focused selections") 
                results.append("• Export results from Analysis Results tab")
                
                self.playlist_results.setPlainText("\n".join(results))
                self.analytics_tab_widget.setCurrentIndex(3)  # Switch to playlist tab
                
                # Enable export button now that we have a playlist
                self.export_playlist_btn.setEnabled(True)
                
            else:
                self.playlist_results.setPlainText(
                    "❌ PLAYLIST GENERATION FAILED\n\n"
                    "Possible reasons:\n"
                    "• Not enough compatible tracks found\n"
                    "• Seed track has insufficient analysis data\n"
                    "• Try a different seed track or adjust filters\n\n"
                    "💡 Suggestion: Try selecting a different seed track or use 'All Subgenres' filter."
                )
                # Disable export button when generation fails
                self.export_playlist_btn.setEnabled(False)
                
        except Exception as e:
            error_msg = str(e)
            self.playlist_results.setPlainText(
                f"❌ PLAYLIST GENERATION ERROR\n\n"
                f"Technical error: {error_msg}\n\n"
                f"🔧 Troubleshooting steps:\n"
                f"• Verify the seed track has complete analysis data\n"
                f"• Try selecting a different seed track\n"
                f"• Check that enough tracks are analyzed (minimum 5)\n"
                f"• Restart the application if issues persist\n\n"
                f"💡 If this error continues, the track database may need rebuilding."
            )
            print(f"Playlist generation error: {error_msg}")  # For debugging
            # Disable export button on error
            self.export_playlist_btn.setEnabled(False)
        finally:
            self.generate_playlist_btn.setEnabled(True)
            self.generate_playlist_btn.setText("🎵 Generate Enhanced Playlist")
    
    def _export_playlist(self):
        """Export current playlist to various formats"""
        if not hasattr(self, 'current_playlist') or not self.current_playlist:
            QMessageBox.warning(self, "No Playlist", "No playlist to export. Generate a playlist first.")
            return
            
        try:
            # Get export format preference from user
            formats = ["CSV (*.csv)", "M3U Playlist (*.m3u)", "Text File (*.txt)", "JSON (*.json)"]
            format_choice, ok = QInputDialog.getItem(
                self, "Export Format", "Choose export format:", formats, 0, False
            )
            
            if not ok:
                return
                
            # Determine file extension
            if "CSV" in format_choice:
                ext = ".csv"
                file_filter = "CSV files (*.csv)"
            elif "M3U" in format_choice:
                ext = ".m3u"
                file_filter = "M3U Playlist files (*.m3u)"
            elif "JSON" in format_choice:
                ext = ".json"
                file_filter = "JSON files (*.json)"
            else:
                ext = ".txt"
                file_filter = "Text files (*.txt)"
            
            # Get save location
            default_name = f"playlist_{self.current_seed_track.replace(' - ', '_').replace(' ', '_')}"
            default_name = "".join(c for c in default_name if c.isalnum() or c in '_-')[:50]  # Clean filename
            
            file_path, _ = QFileDialog.getSaveFileName(
                self, 
                "Export Playlist", 
                f"{default_name}{ext}",
                file_filter
            )
            
            if not file_path:
                return
                
            # Export based on format
            if ext == ".csv":
                self._export_playlist_csv(file_path)
            elif ext == ".m3u":
                self._export_playlist_m3u(file_path)
            elif ext == ".json":
                self._export_playlist_json(file_path)
            else:
                self._export_playlist_txt(file_path)
            
            QMessageBox.information(
                self, "Export Complete", 
                f"Playlist exported successfully to:\n{file_path}"
            )
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export playlist:\n{str(e)}")
    
    def _export_playlist_csv(self, file_path: str):
        """Export playlist as CSV file"""
        import csv
        
        with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow([
                'Position', 'Artist', 'Title', 'Album', 'BPM', 'Key', 
                'Subgenre', 'Era', 'Energy', 'Path', 'BPM_Difference'
            ])
            
            # Write tracks
            for i, track in enumerate(self.current_playlist, 1):
                # Calculate BPM difference
                bpm_diff = ""
                if i > 1:
                    current_bpm = track.get('bpm', 0)
                    prev_bpm = self.current_playlist[i-2].get('bpm', 0)
                    if current_bpm > 0 and prev_bpm > 0:
                        diff = current_bpm - prev_bpm
                        bpm_diff = f"{diff:+.1f}"
                
                writer.writerow([
                    i,
                    track.get('artist', 'Unknown Artist'),
                    track.get('title', 'Unknown Title'),
                    track.get('album', 'Unknown Album'),
                    track.get('bpm', 0),
                    track.get('key', 'Unknown'),
                    track.get('subgenre', 'Unknown'),
                    track.get('era', 'Unknown'),
                    track.get('energy', 0),
                    track.get('path', ''),
                    bpm_diff
                ])
    
    def _export_playlist_m3u(self, file_path: str):
        """Export playlist as M3U playlist file"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("#EXTM3U\n")
            f.write(f"#PLAYLIST: Generated by Music Analyzer Pro - {self.current_seed_track}\n")
            
            for i, track in enumerate(self.current_playlist, 1):
                artist = track.get('artist', 'Unknown Artist')
                title = track.get('title', 'Unknown Title')
                path = track.get('path', '')
                
                # Estimate duration (could be enhanced with actual duration if available)
                duration = 180  # Default 3 minutes
                
                f.write(f"#EXTINF:{duration},{artist} - {title}\n")
                f.write(f"{path}\n")
    
    def _export_playlist_json(self, file_path: str):
        """Export playlist as JSON file"""
        import json
        
        playlist_data = {
            "metadata": {
                "generated_by": "Music Analyzer Pro",
                "seed_track": self.current_seed_track,
                "subgenre_focus": self.current_subgenre_focus,
                "length": len(self.current_playlist),
                "export_timestamp": str(time.time())
            },
            "tracks": []
        }
        
        for i, track in enumerate(self.current_playlist, 1):
            # Calculate BPM difference
            bpm_diff = None
            if i > 1:
                current_bpm = track.get('bpm', 0)
                prev_bpm = self.current_playlist[i-2].get('bpm', 0)
                if current_bpm > 0 and prev_bpm > 0:
                    bpm_diff = current_bpm - prev_bpm
            
            track_data = {
                "position": i,
                "artist": track.get('artist', 'Unknown Artist'),
                "title": track.get('title', 'Unknown Title'),
                "album": track.get('album', 'Unknown Album'),
                "bpm": track.get('bpm', 0),
                "key": track.get('key', 'Unknown'),
                "subgenre": track.get('subgenre', 'Unknown'),
                "era": track.get('era', 'Unknown'),  
                "energy": track.get('energy', 0),
                "path": track.get('path', ''),
                "bpm_difference": bpm_diff
            }
            playlist_data["tracks"].append(track_data)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(playlist_data, f, indent=2, ensure_ascii=False)
    
    def _export_playlist_txt(self, file_path: str):
        """Export playlist as text file"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("🎵 MUSIC ANALYZER PRO - ENHANCED PLAYLIST\n")
            f.write("=" * 50 + "\n")
            f.write(f"🎯 Seed Track: {self.current_seed_track}\n")
            f.write(f"📏 Length: {len(self.current_playlist)} tracks\n")
            if self.current_subgenre_focus:
                f.write(f"🏷️ Subgenre Focus: {self.current_subgenre_focus}\n")
            f.write(f"📅 Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("\n📋 PLAYLIST:\n")
            f.write("-" * 30 + "\n\n")
            
            for i, track in enumerate(self.current_playlist, 1):
                artist = track.get('artist', 'Unknown Artist')
                title = track.get('title', 'Unknown Title')
                bpm = track.get('bpm', 0)
                subgenre = track.get('subgenre', 'Unknown')
                energy = track.get('energy', 0)
                
                # Calculate BPM difference
                bpm_diff_text = ""
                if i > 1 and bpm > 0:
                    prev_bpm = self.current_playlist[i-2].get('bpm', 0)
                    if prev_bpm > 0:
                        bpm_diff = bpm - prev_bpm
                        sign = "+" if bpm_diff > 0 else ""
                        bpm_diff_text = f" ({sign}{bpm_diff:.1f})"
                
                f.write(f"{i:2d}. 🎵 {artist} - {title}\n")
                details = f"     🏷️ {subgenre} | 🥁 {bpm:.1f} BPM{bpm_diff_text}"
                if energy:
                    details += f" | ⚡ Energy: {energy:.2f}"
                f.write(details + "\n")
                f.write("\n")
            
            f.write("-" * 50 + "\n")
            f.write("Generated by Music Analyzer Pro\n")


def create_enhanced_window() -> EnhancedMainWindow:
    """Create and return an enhanced main window instance"""
    return EnhancedMainWindow()


if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication
    
    # Create QApplication
    app = QApplication(sys.argv)
    app.setApplicationName("Music Analyzer Pro - Enhanced Edition")
    app.setApplicationDisplayName("Music Analyzer Pro - Enhanced Edition")
    
    # Create and show main window
    window = EnhancedMainWindow()
    window.show()
    
    # Start event loop
    sys.exit(app.exec())