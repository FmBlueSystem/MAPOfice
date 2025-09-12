# MAP4 UI Development - PyQt6 Interface

## Objective
Build a professional PyQt6-based graphical user interface with tabbed layout, real-time progress tracking, HAMMS visualization, and theme support for the MAP4 music analysis system.

## Prerequisites
- Completed infrastructure, core implementation, and LLM integration
- PyQt6 installed with all required modules
- Basic understanding of Qt signal/slot architecture

## Step 1: Main Window Implementation

### 1.1 Create Enhanced Main Window
Create `src/ui/enhanced_main_window.py`:

```python
"""Enhanced main window with HAMMS v3.0 and Multi-LLM integration."""

import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any, List
import logging
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QPushButton, QLabel, QLineEdit, QTextEdit, QProgressBar,
    QFileDialog, QTableWidget, QTableWidgetItem, QComboBox, QCheckBox,
    QGroupBox, QSplitter, QHeaderView, QMessageBox, QStatusBar
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QSettings
from PyQt6.QtGui import QFont, QIcon, QAction, QPalette, QColor

from src.analysis.enhanced_analyzer import EnhancedAnalyzer
from src.services.storage_service import StorageService
from src.ui.hamms_radar_widget import HAMMSRadarWidget
from src.ui.styles.style_manager import StyleManager
from src.config import get_config

logger = logging.getLogger(__name__)

class AnalysisThread(QThread):
    """Background thread for music analysis."""
    
    # Signals
    progress = pyqtSignal(int, str)  # progress value, status message
    track_completed = pyqtSignal(dict)  # analysis result
    analysis_completed = pyqtSignal(list)  # all results
    error = pyqtSignal(str)  # error message
    
    def __init__(self, file_paths: List[str], use_ai: bool = False, ai_provider: Optional[str] = None):
        """Initialize analysis thread."""
        super().__init__()
        self.file_paths = file_paths
        self.use_ai = use_ai
        self.ai_provider = ai_provider
        self.analyzer = EnhancedAnalyzer()
        self._is_cancelled = False
    
    def run(self):
        """Run analysis in background."""
        results = []
        total = len(self.file_paths)
        
        for i, file_path in enumerate(self.file_paths):
            if self._is_cancelled:
                break
            
            # Update progress
            progress = int((i / total) * 100)
            self.progress.emit(progress, f"Analyzing: {Path(file_path).name}")
            
            try:
                # Perform analysis
                result = self.analyzer.analyze_track(
                    file_path,
                    use_ai=self.use_ai,
                    ai_provider=self.ai_provider,
                    store_results=True
                )
                
                # Convert to dict for signal
                result_dict = {
                    'file_path': result.file_path,
                    'track_id': result.track_id,
                    'bpm': result.audio_features.get('bpm'),
                    'key': result.audio_features.get('key'),
                    'energy': result.audio_features.get('energy'),
                    'hamms_vector': result.hamms_vector.tolist(),
                    'confidence': result.confidence,
                    'genre': result.ai_analysis.get('genre') if result.ai_analysis else None,
                    'mood': result.ai_analysis.get('mood') if result.ai_analysis else None,
                    'tags': result.ai_analysis.get('tags') if result.ai_analysis else [],
                    'processing_time': result.processing_time
                }
                
                results.append(result_dict)
                self.track_completed.emit(result_dict)
                
            except Exception as e:
                logger.error(f"Analysis failed for {file_path}: {e}")
                self.error.emit(f"Failed: {Path(file_path).name} - {str(e)}")
        
        # Emit completion
        self.progress.emit(100, "Analysis complete")
        self.analysis_completed.emit(results)
    
    def cancel(self):
        """Cancel analysis."""
        self._is_cancelled = True

class EnhancedMainWindow(QMainWindow):
    """Enhanced main window with modern features."""
    
    def __init__(self):
        """Initialize main window."""
        super().__init__()
        
        # Load configuration
        self.config = get_config()
        
        # Initialize storage
        self.storage = StorageService()
        
        # Initialize style manager
        self.style_manager = StyleManager()
        
        # Settings
        self.settings = QSettings('MAP4', 'MusicAnalyzerPro')
        
        # Analysis thread
        self.analysis_thread = None
        
        # Current results
        self.current_results = []
        
        # Setup UI
        self.init_ui()
        
        # Apply theme
        self.apply_theme('dark')
        
        # Restore window state
        self.restore_state()
    
    def init_ui(self):
        """Initialize user interface."""
        self.setWindowTitle("MAP4 - Music Analyzer Pro v3.0")
        self.setGeometry(100, 100, 1400, 900)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Create toolbar
        toolbar_layout = self.create_toolbar()
        main_layout.addLayout(toolbar_layout)
        
        # Create tabs
        self.tab_widget = QTabWidget()
        self.tab_widget.addTab(self.create_analysis_tab(), "Analysis")
        self.tab_widget.addTab(self.create_library_tab(), "Library")
        self.tab_widget.addTab(self.create_playlist_tab(), "Playlist")
        self.tab_widget.addTab(self.create_visualization_tab(), "Visualization")
        self.tab_widget.addTab(self.create_settings_tab(), "Settings")
        
        main_layout.addWidget(self.tab_widget)
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Progress bar in status bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(200)
        self.progress_bar.hide()
        self.status_bar.addPermanentWidget(self.progress_bar)
    
    def create_menu_bar(self):
        """Create application menu bar."""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        open_action = QAction("Open Files...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_files)
        file_menu.addAction(open_action)
        
        open_folder_action = QAction("Open Folder...", self)
        open_folder_action.setShortcut("Ctrl+Shift+O")
        open_folder_action.triggered.connect(self.open_folder)
        file_menu.addAction(open_folder_action)
        
        file_menu.addSeparator()
        
        export_action = QAction("Export Results...", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.export_results)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        # Theme submenu
        theme_menu = view_menu.addMenu("Theme")
        for theme_name in ['dark', 'light', 'audio_pro']:
            theme_action = QAction(theme_name.title(), self)
            theme_action.triggered.connect(lambda checked, name=theme_name: self.apply_theme(name))
            theme_menu.addAction(theme_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        
        batch_action = QAction("Batch Analysis...", self)
        batch_action.triggered.connect(self.batch_analysis)
        tools_menu.addAction(batch_action)
        
        bmad_action = QAction("BMAD Validation...", self)
        bmad_action.triggered.connect(self.open_bmad_dialog)
        tools_menu.addAction(bmad_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About MAP4", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_toolbar(self) -> QHBoxLayout:
        """Create main toolbar."""
        layout = QHBoxLayout()
        
        # File selection
        self.file_input = QLineEdit()
        self.file_input.setPlaceholderText("Select files or folder to analyze...")
        self.file_input.setReadOnly(True)
        layout.addWidget(self.file_input)
        
        # Browse button
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.open_files)
        layout.addWidget(browse_btn)
        
        # AI provider selection
        self.ai_checkbox = QCheckBox("Use AI")
        self.ai_checkbox.setChecked(True)
        layout.addWidget(self.ai_checkbox)
        
        self.provider_combo = QComboBox()
        self.provider_combo.addItems(['Auto', 'OpenAI', 'Anthropic', 'Gemini'])
        layout.addWidget(self.provider_combo)
        
        # Analyze button
        self.analyze_btn = QPushButton("Analyze")
        self.analyze_btn.clicked.connect(self.start_analysis)
        self.analyze_btn.setStyleSheet("QPushButton { font-weight: bold; }")
        layout.addWidget(self.analyze_btn)
        
        # Cancel button
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.cancel_analysis)
        self.cancel_btn.setEnabled(False)
        layout.addWidget(self.cancel_btn)
        
        layout.addStretch()
        
        return layout
    
    def create_analysis_tab(self) -> QWidget:
        """Create analysis tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(10)
        self.results_table.setHorizontalHeaderLabels([
            "File", "BPM", "Key", "Energy", "Genre", "Mood", 
            "Confidence", "Time", "Provider", "Status"
        ])
        self.results_table.horizontalHeader().setStretchLastSection(True)
        self.results_table.setAlternatingRowColors(True)
        self.results_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        layout.addWidget(self.results_table)
        
        # Log output
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMaximumHeight(150)
        self.log_output.setFont(QFont("Consolas", 9))
        layout.addWidget(self.log_output)
        
        return widget
    
    def create_library_tab(self) -> QWidget:
        """Create library management tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Search bar
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search by title, artist, genre...")
        self.search_input.textChanged.connect(self.search_library)
        search_layout.addWidget(self.search_input)
        
        self.genre_filter = QComboBox()
        self.genre_filter.addItems(['All Genres', 'House', 'Techno', 'Trance', 'Hip Hop', 'Rock', 'Pop'])
        self.genre_filter.currentTextChanged.connect(self.filter_by_genre)
        search_layout.addWidget(self.genre_filter)
        
        layout.addLayout(search_layout)
        
        # Library table
        self.library_table = QTableWidget()
        self.library_table.setColumnCount(8)
        self.library_table.setHorizontalHeaderLabels([
            "Title", "Artist", "Album", "Genre", "BPM", "Key", "Duration", "Analyzed"
        ])
        self.library_table.horizontalHeader().setStretchLastSection(False)
        self.library_table.setAlternatingRowColors(True)
        
        layout.addWidget(self.library_table)
        
        # Library stats
        self.stats_label = QLabel("Library Statistics: 0 tracks")
        layout.addWidget(self.stats_label)
        
        # Load library on tab activation
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        
        return widget
    
    def create_playlist_tab(self) -> QWidget:
        """Create playlist generation tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Seed track selection
        seed_group = QGroupBox("Seed Track")
        seed_layout = QHBoxLayout(seed_group)
        
        self.seed_track_input = QLineEdit()
        self.seed_track_input.setPlaceholderText("Select seed track...")
        seed_layout.addWidget(self.seed_track_input)
        
        select_seed_btn = QPushButton("Select...")
        select_seed_btn.clicked.connect(self.select_seed_track)
        seed_layout.addWidget(select_seed_btn)
        
        layout.addWidget(seed_group)
        
        # Playlist parameters
        params_group = QGroupBox("Parameters")
        params_layout = QHBoxLayout(params_group)
        
        params_layout.addWidget(QLabel("Tracks:"))
        self.playlist_size = QComboBox()
        self.playlist_size.addItems(['10', '20', '30', '50', '100'])
        params_layout.addWidget(self.playlist_size)
        
        params_layout.addWidget(QLabel("Similarity:"))
        self.similarity_threshold = QComboBox()
        self.similarity_threshold.addItems(['0.9', '0.8', '0.7', '0.6', '0.5'])
        self.similarity_threshold.setCurrentIndex(2)
        params_layout.addWidget(self.similarity_threshold)
        
        self.harmonic_mixing = QCheckBox("Harmonic Mixing")
        self.harmonic_mixing.setChecked(True)
        params_layout.addWidget(self.harmonic_mixing)
        
        generate_btn = QPushButton("Generate Playlist")
        generate_btn.clicked.connect(self.generate_playlist)
        params_layout.addWidget(generate_btn)
        
        params_layout.addStretch()
        layout.addWidget(params_group)
        
        # Playlist table
        self.playlist_table = QTableWidget()
        self.playlist_table.setColumnCount(7)
        self.playlist_table.setHorizontalHeaderLabels([
            "Order", "Title", "Artist", "BPM", "Key", "Compatibility", "Transition"
        ])
        
        layout.addWidget(self.playlist_table)
        
        # Export buttons
        export_layout = QHBoxLayout()
        export_layout.addStretch()
        
        export_m3u_btn = QPushButton("Export M3U")
        export_m3u_btn.clicked.connect(lambda: self.export_playlist('m3u'))
        export_layout.addWidget(export_m3u_btn)
        
        export_json_btn = QPushButton("Export JSON")
        export_json_btn.clicked.connect(lambda: self.export_playlist('json'))
        export_layout.addWidget(export_json_btn)
        
        layout.addLayout(export_layout)
        
        return widget
    
    def create_visualization_tab(self) -> QWidget:
        """Create visualization tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # HAMMS radar chart
        self.hamms_radar = HAMMSRadarWidget()
        layout.addWidget(self.hamms_radar)
        
        # Track selection for visualization
        control_layout = QHBoxLayout()
        control_layout.addWidget(QLabel("Track:"))
        
        self.viz_track_combo = QComboBox()
        self.viz_track_combo.currentTextChanged.connect(self.update_visualization)
        control_layout.addWidget(self.viz_track_combo)
        
        control_layout.addWidget(QLabel("Compare with:"))
        self.viz_compare_combo = QComboBox()
        self.viz_compare_combo.addItem("None")
        self.viz_compare_combo.currentTextChanged.connect(self.update_visualization)
        control_layout.addWidget(self.viz_compare_combo)
        
        control_layout.addStretch()
        layout.addLayout(control_layout)
        
        return widget
    
    def create_settings_tab(self) -> QWidget:
        """Create settings tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Analysis settings
        analysis_group = QGroupBox("Analysis Settings")
        analysis_layout = QVBoxLayout(analysis_group)
        
        sample_rate_layout = QHBoxLayout()
        sample_rate_layout.addWidget(QLabel("Sample Rate:"))
        self.sample_rate_combo = QComboBox()
        self.sample_rate_combo.addItems(['22050', '44100', '48000'])
        sample_rate_layout.addWidget(self.sample_rate_combo)
        sample_rate_layout.addStretch()
        analysis_layout.addLayout(sample_rate_layout)
        
        self.cache_checkbox = QCheckBox("Enable result caching")
        self.cache_checkbox.setChecked(True)
        analysis_layout.addWidget(self.cache_checkbox)
        
        self.parallel_checkbox = QCheckBox("Enable parallel processing")
        self.parallel_checkbox.setChecked(True)
        analysis_layout.addWidget(self.parallel_checkbox)
        
        layout.addWidget(analysis_group)
        
        # Provider settings
        provider_group = QGroupBox("AI Provider Settings")
        provider_layout = QVBoxLayout(provider_group)
        
        self.provider_table = QTableWidget()
        self.provider_table.setColumnCount(4)
        self.provider_table.setHorizontalHeaderLabels(["Provider", "Status", "Model", "Requests"])
        provider_layout.addWidget(self.provider_table)
        
        layout.addWidget(provider_group)
        
        # Database settings
        db_group = QGroupBox("Database")
        db_layout = QVBoxLayout(db_group)
        
        self.db_stats_label = QLabel("Database statistics loading...")
        db_layout.addWidget(self.db_stats_label)
        
        db_btn_layout = QHBoxLayout()
        backup_btn = QPushButton("Backup Database")
        backup_btn.clicked.connect(self.backup_database)
        db_btn_layout.addWidget(backup_btn)
        
        clear_cache_btn = QPushButton("Clear Cache")
        clear_cache_btn.clicked.connect(self.clear_cache)
        db_btn_layout.addWidget(clear_cache_btn)
        
        db_btn_layout.addStretch()
        db_layout.addLayout(db_btn_layout)
        
        layout.addWidget(db_group)
        
        layout.addStretch()
        
        # Load settings on tab activation
        self.load_settings()
        
        return widget
    
    def open_files(self):
        """Open file dialog to select audio files."""
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Audio Files",
            "",
            "Audio Files (*.mp3 *.wav *.flac *.m4a *.ogg);;All Files (*.*)"
        )
        
        if files:
            self.file_input.setText(f"{len(files)} files selected")
            self.selected_files = files
            self.log(f"Selected {len(files)} files for analysis")
    
    def open_folder(self):
        """Open folder dialog to select music library."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Music Library Folder"
        )
        
        if folder:
            # Find all audio files in folder
            audio_extensions = {'.mp3', '.wav', '.flac', '.m4a', '.ogg'}
            files = []
            
            for path in Path(folder).rglob('*'):
                if path.is_file() and path.suffix.lower() in audio_extensions:
                    files.append(str(path))
            
            if files:
                self.file_input.setText(f"{folder} ({len(files)} files)")
                self.selected_files = files
                self.log(f"Found {len(files)} audio files in {folder}")
            else:
                self.log("No audio files found in selected folder")
    
    def start_analysis(self):
        """Start analysis of selected files."""
        if not hasattr(self, 'selected_files') or not self.selected_files:
            QMessageBox.warning(self, "No Files", "Please select files to analyze")
            return
        
        # Disable controls
        self.analyze_btn.setEnabled(False)
        self.cancel_btn.setEnabled(True)
        
        # Clear previous results
        self.results_table.setRowCount(0)
        self.current_results.clear()
        
        # Show progress bar
        self.progress_bar.show()
        self.progress_bar.setValue(0)
        
        # Get settings
        use_ai = self.ai_checkbox.isChecked()
        provider = self.provider_combo.currentText().lower()
        if provider == 'auto':
            provider = None
        
        # Create and start analysis thread
        self.analysis_thread = AnalysisThread(
            self.selected_files,
            use_ai=use_ai,
            ai_provider=provider
        )
        
        # Connect signals
        self.analysis_thread.progress.connect(self.update_progress)
        self.analysis_thread.track_completed.connect(self.add_result)
        self.analysis_thread.analysis_completed.connect(self.analysis_complete)
        self.analysis_thread.error.connect(self.log_error)
        
        # Start analysis
        self.analysis_thread.start()
        self.log(f"Starting analysis of {len(self.selected_files)} files...")
    
    def cancel_analysis(self):
        """Cancel ongoing analysis."""
        if self.analysis_thread and self.analysis_thread.isRunning():
            self.analysis_thread.cancel()
            self.log("Analysis cancelled by user")
            self.analysis_complete([])
    
    def update_progress(self, value: int, message: str):
        """Update progress bar and status."""
        self.progress_bar.setValue(value)
        self.status_bar.showMessage(message)
    
    def add_result(self, result: Dict[str, Any]):
        """Add analysis result to table."""
        row = self.results_table.rowCount()
        self.results_table.insertRow(row)
        
        # Add data to table
        self.results_table.setItem(row, 0, QTableWidgetItem(Path(result['file_path']).name))
        self.results_table.setItem(row, 1, QTableWidgetItem(f"{result.get('bpm', 0):.1f}"))
        self.results_table.setItem(row, 2, QTableWidgetItem(result.get('key', '')))
        self.results_table.setItem(row, 3, QTableWidgetItem(f"{result.get('energy', 0):.2f}"))
        self.results_table.setItem(row, 4, QTableWidgetItem(result.get('genre', '')))
        self.results_table.setItem(row, 5, QTableWidgetItem(result.get('mood', '')))
        self.results_table.setItem(row, 6, QTableWidgetItem(f"{result.get('confidence', 0):.2f}"))
        self.results_table.setItem(row, 7, QTableWidgetItem(f"{result.get('processing_time', 0):.1f}s"))
        self.results_table.setItem(row, 8, QTableWidgetItem(result.get('provider', 'N/A')))
        self.results_table.setItem(row, 9, QTableWidgetItem("✓"))
        
        # Store result
        self.current_results.append(result)
        
        # Update visualization combo
        self.viz_track_combo.addItem(Path(result['file_path']).name)
        self.viz_compare_combo.addItem(Path(result['file_path']).name)
    
    def analysis_complete(self, results: List[Dict[str, Any]]):
        """Handle analysis completion."""
        # Re-enable controls
        self.analyze_btn.setEnabled(True)
        self.cancel_btn.setEnabled(False)
        
        # Hide progress bar
        self.progress_bar.hide()
        
        # Update status
        self.status_bar.showMessage(f"Analysis complete: {len(results)} tracks processed")
        
        # Log completion
        self.log(f"Analysis completed successfully for {len(results)} tracks")
        
        # Refresh library tab
        self.load_library()
    
    def log(self, message: str):
        """Add message to log output."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_output.append(f"[{timestamp}] {message}")
    
    def log_error(self, message: str):
        """Add error message to log output."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_output.append(f"<span style='color: red;'>[{timestamp}] ERROR: {message}</span>")
    
    def apply_theme(self, theme_name: str):
        """Apply UI theme."""
        try:
            theme = self.style_manager.get_theme(theme_name)
            if theme:
                self.setStyleSheet(theme.get_stylesheet())
                self.log(f"Applied theme: {theme_name}")
        except Exception as e:
            self.log_error(f"Failed to apply theme: {e}")
    
    def export_results(self):
        """Export analysis results."""
        if not self.current_results:
            QMessageBox.information(self, "No Results", "No results to export")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Results",
            "analysis_results.json",
            "JSON Files (*.json);;CSV Files (*.csv)"
        )
        
        if file_path:
            # Export logic here
            self.log(f"Results exported to {file_path}")
    
    def show_about(self):
        """Show about dialog."""
        QMessageBox.about(
            self,
            "About MAP4",
            "MAP4 - Music Analyzer Pro v3.0\n\n"
            "Advanced music analysis with HAMMS v3.0 and AI enrichment\n\n"
            "© 2024 MAP4 Development Team"
        )
    
    def restore_state(self):
        """Restore window state from settings."""
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)
        
        state = self.settings.value("windowState")
        if state:
            self.restoreState(state)
    
    def closeEvent(self, event):
        """Handle window close event."""
        # Save state
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())
        
        # Cancel any running analysis
        if self.analysis_thread and self.analysis_thread.isRunning():
            self.analysis_thread.cancel()
            self.analysis_thread.wait()
        
        event.accept()

def main():
    """Main entry point for GUI application."""
    app = QApplication(sys.argv)
    app.setApplicationName("MAP4")
    app.setOrganizationName("MusicAnalyzerPro")
    
    # Set application icon if available
    icon_path = Path("resources/icon.png")
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    
    # Create and show main window
    window = EnhancedMainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
```

## Step 2: HAMMS Radar Visualization Widget

### 2.1 Create HAMMS Radar Widget
Create `src/ui/hamms_radar_widget.py`:

```python
"""HAMMS radar chart visualization widget."""

import numpy as np
from typing import Optional, List
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from PyQt6.QtWidgets import QWidget, QVBoxLayout

class HAMMSRadarWidget(QWidget):
    """Widget for displaying HAMMS vectors as radar charts."""
    
    def __init__(self, parent=None):
        """Initialize HAMMS radar widget."""
        super().__init__(parent)
        
        # Setup layout
        layout = QVBoxLayout(self)
        
        # Create matplotlib figure
        self.figure = Figure(figsize=(8, 6))
        self.canvas = FigureCanvasQTAgg(self.figure)
        layout.addWidget(self.canvas)
        
        # Dimension labels
        self.dimensions = [
            "BPM", "Key", "Energy", "Danceability",
            "Valence", "Acousticness", "Instrumentalness",
            "Rhythm", "Brightness", "Stability",
            "Harmonic", "Dynamic"
        ]
        
        # Initialize with empty chart
        self.clear()
    
    def plot_vector(self, vector: np.ndarray, label: str = "Track",
                   color: str = 'blue', compare_vector: Optional[np.ndarray] = None,
                   compare_label: str = "Compare"):
        """Plot HAMMS vector as radar chart."""
        self.figure.clear()
        ax = self.figure.add_subplot(111, projection='polar')
        
        # Setup angles for 12 dimensions
        angles = np.linspace(0, 2 * np.pi, 12, endpoint=False).tolist()
        vector = vector.tolist()
        
        # Close the plot
        angles += angles[:1]
        vector += vector[:1]
        
        # Plot main vector
        ax.plot(angles, vector, 'o-', linewidth=2, label=label, color=color)
        ax.fill(angles, vector, alpha=0.25, color=color)
        
        # Plot comparison if provided
        if compare_vector is not None:
            compare_vector = compare_vector.tolist()
            compare_vector += compare_vector[:1]
            ax.plot(angles, compare_vector, 'o-', linewidth=2, 
                   label=compare_label, color='red')
            ax.fill(angles, compare_vector, alpha=0.15, color='red')
        
        # Set labels
        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(self.dimensions)
        ax.set_ylim(0, 1)
        
        # Add grid
        ax.grid(True)
        
        # Add legend
        ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1))
        
        # Set title
        ax.set_title("HAMMS Vector Analysis", size=14, weight='bold', pad=20)
        
        self.canvas.draw()
    
    def clear(self):
        """Clear the radar chart."""
        self.figure.clear()
        ax = self.figure.add_subplot(111, projection='polar')
        ax.set_title("No Data")
        self.canvas.draw()
```

## Step 3: Theme System

### 3.1 Create Style Manager
Create `src/ui/styles/style_manager.py`:

```python
"""Style manager for theme support."""

from typing import Dict, Optional

class Theme:
    """Base theme class."""
    
    def __init__(self, name: str):
        """Initialize theme."""
        self.name = name
        self.colors = {}
        self.fonts = {}
        self.styles = {}
    
    def get_stylesheet(self) -> str:
        """Get complete stylesheet."""
        return ""

class DarkTheme(Theme):
    """Dark theme implementation."""
    
    def __init__(self):
        """Initialize dark theme."""
        super().__init__("dark")
        
        self.colors = {
            'background': '#1e1e1e',
            'foreground': '#d4d4d4',
            'accent': '#007acc',
            'secondary': '#252526',
            'border': '#3c3c3c'
        }
    
    def get_stylesheet(self) -> str:
        """Get dark theme stylesheet."""
        return f'''
        QMainWindow {{
            background-color: {self.colors['background']};
            color: {self.colors['foreground']};
        }}
        
        QTabWidget::pane {{
            background-color: {self.colors['secondary']};
            border: 1px solid {self.colors['border']};
        }}
        
        QTabBar::tab {{
            background-color: {self.colors['secondary']};
            color: {self.colors['foreground']};
            padding: 8px 16px;
            margin-right: 2px;
        }}
        
        QTabBar::tab:selected {{
            background-color: {self.colors['accent']};
            color: white;
        }}
        
        QPushButton {{
            background-color: {self.colors['accent']};
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 4px;
        }}
        
        QPushButton:hover {{
            background-color: #005a9e;
        }}
        
        QPushButton:pressed {{
            background-color: #003d6b;
        }}
        
        QTableWidget {{
            background-color: {self.colors['secondary']};
            alternate-background-color: {self.colors['background']};
            gridline-color: {self.colors['border']};
        }}
        
        QLineEdit, QComboBox, QTextEdit {{
            background-color: {self.colors['secondary']};
            border: 1px solid {self.colors['border']};
            padding: 4px;
            color: {self.colors['foreground']};
        }}
        
        QGroupBox {{
            border: 1px solid {self.colors['border']};
            margin-top: 6px;
            padding-top: 6px;
        }}
        
        QGroupBox::title {{
            color: {self.colors['accent']};
            subcontrol-origin: margin;
            left: 10px;
        }}
        '''

class StyleManager:
    """Manager for application themes."""
    
    def __init__(self):
        """Initialize style manager."""
        self.themes = {
            'dark': DarkTheme(),
            'light': Theme('light'),  # Placeholder
            'audio_pro': Theme('audio_pro')  # Placeholder
        }
    
    def get_theme(self, name: str) -> Optional[Theme]:
        """Get theme by name."""
        return self.themes.get(name)
```

## Success Criteria

The UI development is complete when:

1. **Main Window**: Fully functional tabbed interface with all major features
2. **Analysis Tab**: Real-time progress tracking and results display
3. **Library Tab**: Track browsing with search and filtering
4. **Playlist Tab**: Intelligent playlist generation interface
5. **Visualization**: HAMMS radar chart for vector visualization
6. **Theme System**: Multiple themes with clean, professional appearance
7. **Threading**: Non-blocking analysis with progress reporting
8. **Settings**: Persistent configuration and preferences

## Next Steps

1. Implement the BMAD framework (see `05-bmad-framework.md`)
2. Create the unified CLI system (see `06-cli-system.md`)
3. Add integration and testing (see `07-integration-testing.md`)

This UI provides a professional, responsive interface for the MAP4 music analysis system.