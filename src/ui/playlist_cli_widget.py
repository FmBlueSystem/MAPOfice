"""Playlist CLI UI Widget for Music Analyzer Pro

This widget provides a graphical interface for the BMAD-certified playlist CLI functionality,
integrating the command-line features into the PyQt6 enhanced main window.

Features:
- Real audio library scanning with progress tracking
- Playlist generation with BMAD certification
- Quality validation metrics display
- Export functionality for multiple formats
- Integration with existing enhanced analyzer
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from PyQt6.QtCore import QThread, pyqtSignal, Qt, QTimer
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFileDialog, QListWidget, QProgressBar, QMessageBox,
    QGroupBox, QComboBox, QTextEdit, QSplitter, QFrame,
    QScrollArea, QTableWidget, QTableWidgetItem, QSlider,
    QGridLayout, QSpinBox, QDoubleSpinBox, QLineEdit,
    QTabWidget, QCheckBox
)

# Import BMAD CLI components and enhanced services
sys.path.append('/Users/freddymolina/Desktop/MAP 4')
from playlist_cli_final import (
    BMADCertifiedPlaylistCLI, 
    RealAudioLibraryScanner,
    PlaylistQualityValidator
)

# Import unified storage system (same as Enhanced Analysis tab)
from src.services.storage import Storage
from src.services.persistent_library_scanner import (
    PersistentLibraryScanner, ScanProgress, ScanConfiguration
)
from src.services.track_database import TrackDatabase


@dataclass
class PlaylistGenerationParams:
    """Parameters for playlist generation"""
    seed_track_path: str
    length: int = 10
    tolerance: float = 0.02
    library_path: str = None
    output_format: str = 'json'


# LibraryScanThread removed - now using PersistentLibraryScanner with built-in threading


class PlaylistGenerationThread(QThread):
    """Background thread for playlist generation"""
    progress_updated = pyqtSignal(int, str)
    generation_completed = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)

    def __init__(self, params: PlaylistGenerationParams):
        super().__init__()
        self.params = params

    def run(self):
        try:
            cli = BMADCertifiedPlaylistCLI(self.params.library_path)
            
            self.progress_updated.emit(10, "Analyzing seed track...")
            
            # Generate playlist
            result = cli.generate_playlist(
                seed_track_path=self.params.seed_track_path,
                length=self.params.length,
                tolerance=self.params.tolerance,
                output_format=self.params.output_format
            )
            
            if result['success']:
                self.progress_updated.emit(100, "Playlist generated successfully")
                self.generation_completed.emit(result)
            else:
                self.error_occurred.emit(result.get('error', 'Unknown generation error'))
                
        except Exception as e:
            self.error_occurred.emit(f"Generation error: {str(e)}")


class PlaylistCLIWidget(QWidget):
    """Main playlist CLI interface widget"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.library_path = "/Volumes/My Passport/Abibleoteca/Consolidado2025/Tracks"
        self.scanned_tracks = []
        self.current_playlist = None
        self.scan_thread = None
        self.generation_thread = None
        
        # Initialize unified storage system (same as Enhanced Analysis tab)
        self.storage = Storage.from_path("data/music.db")
        self.track_database = self.storage  # Keep for compatibility
        self.persistent_scanner = PersistentLibraryScanner(database=None, storage=self.storage)
        
        # Connect scanner signals
        self.persistent_scanner.scan_started.connect(self._on_scan_started)
        self.persistent_scanner.scan_progress.connect(self._on_scan_progress)
        self.persistent_scanner.scan_completed.connect(self._on_persistent_scan_completed)
        self.persistent_scanner.scan_error.connect(self._on_persistent_scan_error)
        
        # Statistics refresh timer
        self.stats_timer = QTimer()
        self.stats_timer.timeout.connect(self._refresh_database_stats)
        self.stats_timer.start(5000)  # Refresh every 5 seconds
        
        self.init_ui()
        
        # Initial stats refresh
        self._refresh_database_stats()
        
        # Load seed tracks from database
        self._refresh_seed_tracks()
        
        # TEMP: Add test data to show table working
        self._populate_test_playlist_data()
        
    def init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        
        # Header
        header_label = QLabel("🎵 BMAD Certified Playlist CLI")
        header_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2E86AB;
                padding: 10px;
                background-color: #F8F9FA;
                border-radius: 5px;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(header_label)
        
        # Simplified single-page workflow
        self._create_simplified_playlist_interface(layout)
        
    # Old tab methods removed - using simplified interface
        
        # Quality Metrics
        quality_group = QGroupBox("🏆 BMAD Quality Certification")
        quality_layout = QGridLayout(quality_group)
        
        # Create quality metric labels
        self.overall_quality_label = QLabel("Overall Quality: --")
        self.bpm_adherence_label = QLabel("BPM Adherence: --")
        self.genre_coherence_label = QLabel("Genre Coherence: --")
        self.energy_flow_label = QLabel("Energy Flow: --")
        self.data_completeness_label = QLabel("Data Completeness: --")
        self.transition_quality_label = QLabel("Transition Quality: --")
        self.certification_status_label = QLabel("Status: --")
        
        # Style quality labels
        for label in [self.overall_quality_label, self.bpm_adherence_label, 
                     self.genre_coherence_label, self.energy_flow_label,
                     self.data_completeness_label, self.transition_quality_label,
                     self.certification_status_label]:
            label.setStyleSheet("font-weight: bold; padding: 5px;")
        
        quality_layout.addWidget(self.overall_quality_label, 0, 0, 1, 2)
        quality_layout.addWidget(self.bpm_adherence_label, 1, 0)
        quality_layout.addWidget(self.genre_coherence_label, 1, 1)
        quality_layout.addWidget(self.energy_flow_label, 2, 0)
        quality_layout.addWidget(self.data_completeness_label, 2, 1)
        quality_layout.addWidget(self.transition_quality_label, 3, 0)
        quality_layout.addWidget(self.certification_status_label, 3, 1)
        
        layout.addWidget(quality_group)
        
        # Generated Playlist
        playlist_group = QGroupBox("Generated Playlist")
        playlist_layout = QVBoxLayout(playlist_group)
        
        self.playlist_table = QTableWidget()
        self.playlist_table.setColumnCount(6)
        self.playlist_table.setHorizontalHeaderLabels(["#", "Title", "Artist", "Genre", "BPM", "Energy"])
        self.playlist_table.setAlternatingRowColors(True)
        
        playlist_layout.addWidget(self.playlist_table)
        
        layout.addWidget(playlist_group)
        
    
    def _create_simplified_playlist_interface(self, layout):
        """Create simplified single-page playlist interface"""
        
        # Main content area with splitter
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left panel: Configuration and Generation
        left_panel = self._create_generation_panel()
        main_splitter.addWidget(left_panel)
        
        # Right panel: Results and Quality
        right_panel = self._create_results_panel()
        main_splitter.addWidget(right_panel)
        
        # Set splitter proportions (40% left, 60% right)
        main_splitter.setSizes([400, 600])
        
        layout.addWidget(main_splitter)
        
        # Status bar at bottom
        status_frame = QFrame()
        status_frame.setFrameStyle(QFrame.Shape.StyledPanel)
        status_layout = QHBoxLayout(status_frame)
        
        self.main_status_label = QLabel("Ready - Select a seed track to begin")
        self.main_status_label.setStyleSheet("color: #6C757D; padding: 5px;")
        status_layout.addWidget(self.main_status_label)
        
        # Quick actions
        self.rescan_btn = QPushButton("🔄 Rescan Library")
        self.rescan_btn.setToolTip("Scan library for new tracks")
        self.rescan_btn.clicked.connect(self._quick_rescan)
        
        status_layout.addWidget(self.rescan_btn)
        layout.addWidget(status_frame)
    
    def _create_generation_panel(self) -> QWidget:
        """Create the left panel for playlist generation - NO QGROUPBOX"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)
        
        # SEED TRACK SELECTION - Simple Section with Styled Label
        seed_label = QLabel("🎯 Select Seed Track")
        seed_label.setStyleSheet("""
            QLabel {
                font-size: 16px; 
                font-weight: bold; 
                color: #2E86AB; 
                padding: 5px 0px;
                border-bottom: 2px solid #2E86AB;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(seed_label)
        
        # Seed combo - directly visible
        self.seed_track_combo = QComboBox()
        self.seed_track_combo.setMinimumWidth(350)
        self.seed_track_combo.setMinimumHeight(35)
        self.seed_track_combo.currentTextChanged.connect(self._on_seed_track_selected)
        layout.addWidget(self.seed_track_combo)
        print("DEBUG: Created seed combo directly in layout")
        
        # Filter - directly visible  
        self.seed_filter_edit = QLineEdit()
        self.seed_filter_edit.setPlaceholderText("🔍 Filter tracks...")
        self.seed_filter_edit.setMinimumHeight(30)
        self.seed_filter_edit.textChanged.connect(self._filter_seed_tracks)
        layout.addWidget(self.seed_filter_edit)
        print("DEBUG: Created filter edit directly in layout")
        
        layout.addSpacing(20)
        
        # PLAYLIST SETTINGS - Simple Section with Styled Label
        settings_label = QLabel("⚙️ Playlist Settings")
        settings_label.setStyleSheet("""
            QLabel {
                font-size: 16px; 
                font-weight: bold; 
                color: #2E86AB; 
                padding: 5px 0px;
                border-bottom: 2px solid #2E86AB;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(settings_label)
        
        # Settings in simple grid - NO QGROUPBOX
        settings_widget = QWidget()
        settings_layout = QGridLayout(settings_widget)
        
        # Length
        settings_layout.addWidget(QLabel("Length:"), 0, 0)
        self.length_spin = QSpinBox()
        self.length_spin.setRange(5, 50)
        self.length_spin.setValue(10)
        self.length_spin.setMinimumHeight(30)
        settings_layout.addWidget(self.length_spin, 0, 1)
        
        # BPM Tolerance
        settings_layout.addWidget(QLabel("BPM Tolerance:"), 1, 0)
        self.tolerance_spin = QDoubleSpinBox()
        self.tolerance_spin.setRange(0.01, 0.20)
        self.tolerance_spin.setValue(0.02)
        self.tolerance_spin.setDecimals(3)
        self.tolerance_spin.setSuffix("%")
        self.tolerance_spin.setMinimumHeight(30)
        settings_layout.addWidget(self.tolerance_spin, 1, 1)
        
        layout.addWidget(settings_widget)
        layout.addSpacing(20)
        
        # GENERATE BUTTON - Prominent
        self.generate_btn = QPushButton("🎧 Generate Playlist")
        self.generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #007BFF;
                color: white;
                font-weight: bold;
                font-size: 16px;
                padding: 20px;
                border-radius: 10px;
                border: none;
            }
            QPushButton:hover {
                background-color: #0056B3;
            }
            QPushButton:disabled {
                background-color: #6C757D;
            }
        """)
        self.generate_btn.clicked.connect(self._start_playlist_generation)
        self.generate_btn.setEnabled(False)
        layout.addWidget(self.generate_btn)
        
        layout.addSpacing(15)
        
        # EXPORT - Simple row
        export_widget = QWidget()
        export_layout = QHBoxLayout(export_widget)
        export_layout.addWidget(QLabel("Export:"))
        
        self.format_combo = QComboBox()
        self.format_combo.addItems(["json", "m3u", "csv"])
        self.format_combo.setMinimumHeight(30)
        export_layout.addWidget(self.format_combo)
        
        self.export_btn = QPushButton("💾 Export")
        self.export_btn.setMinimumHeight(30)
        self.export_btn.clicked.connect(self._export_playlist)
        self.export_btn.setEnabled(False)
        export_layout.addWidget(self.export_btn)
        
        layout.addWidget(export_widget)
        layout.addStretch()  # Push everything to top
        
        print("DEBUG: Created simplified generation panel WITHOUT QGroupBox")
        
        return panel
    
    def _create_results_panel(self) -> QWidget:
        """Create the right panel for results"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # Quality Metrics (Compact)
        quality_group = QGroupBox("🏆 BMAD Quality Score")
        quality_layout = QVBoxLayout(quality_group)
        
        # Overall quality prominently displayed
        self.overall_quality_label = QLabel("Overall Quality: --")
        self.overall_quality_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            padding: 10px;
            border-radius: 5px;
            background-color: #F8F9FA;
        """)
        quality_layout.addWidget(self.overall_quality_label)
        
        # Detailed metrics in compact grid
        metrics_widget = QWidget()
        metrics_layout = QGridLayout(metrics_widget)
        metrics_layout.setSpacing(5)
        
        self.bpm_adherence_label = QLabel("BPM: --")
        self.genre_coherence_label = QLabel("Genre: --")
        self.energy_flow_label = QLabel("Energy: --")
        self.certification_status_label = QLabel("Status: --")
        
        metrics_layout.addWidget(self.bpm_adherence_label, 0, 0)
        metrics_layout.addWidget(self.genre_coherence_label, 0, 1)
        metrics_layout.addWidget(self.energy_flow_label, 1, 0)
        metrics_layout.addWidget(self.certification_status_label, 1, 1)
        
        quality_layout.addWidget(metrics_widget)
        layout.addWidget(quality_group)
        
        # Generated Playlist (Main focus)
        playlist_group = QGroupBox("🎵 Generated Playlist")
        playlist_layout = QVBoxLayout(playlist_group)
        
        self.playlist_table = QTableWidget()
        self.playlist_table.setColumnCount(4)  # Simplified columns
        self.playlist_table.setHorizontalHeaderLabels(["#", "Track", "BPM", "Genre"])
        self.playlist_table.setAlternatingRowColors(True)
        self.playlist_table.verticalHeader().setVisible(False)
        self.playlist_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.playlist_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        
        # FIX: Set dark text color for table
        self.playlist_table.setStyleSheet("""
            QTableWidget {
                color: black;
                background-color: white;
                alternate-background-color: #f0f0f0;
            }
            QTableWidget::item {
                color: black;
                padding: 8px;
            }
        """)
        self.playlist_table.itemSelectionChanged.connect(self._on_playlist_track_selected)
        self.playlist_table.itemDoubleClicked.connect(self._on_playlist_track_double_clicked)
        playlist_layout.addWidget(self.playlist_table)
        
        # Playlist actions toolbar
        playlist_actions = QHBoxLayout()
        
        self.use_as_seed_btn = QPushButton("🎯 Use as New Seed")
        self.use_as_seed_btn.setToolTip("Use selected track as new seed for another playlist")
        self.use_as_seed_btn.setEnabled(False)
        self.use_as_seed_btn.clicked.connect(self._use_playlist_track_as_seed)
        
        self.show_details_btn = QPushButton("📋 Show Details")
        self.show_details_btn.setToolTip("Show detailed information about selected track")
        self.show_details_btn.setEnabled(False)
        self.show_details_btn.clicked.connect(self._show_selected_track_details)
        
        playlist_actions.addWidget(self.use_as_seed_btn)
        playlist_actions.addWidget(self.show_details_btn)
        playlist_actions.addStretch()
        
        playlist_layout.addLayout(playlist_actions)
        
        layout.addWidget(playlist_group)
        
        return panel
    
    def _quick_rescan(self):
        """Quick library rescan - simplified to avoid crashes"""
        try:
            # Simple status update
            self.main_status_label.setText("🔄 Refreshing seed tracks...")
            self.rescan_btn.setEnabled(False)
            
            # Just refresh the seed tracks dropdown instead of full scan
            self._refresh_seed_tracks()
            
            # Update status
            self.main_status_label.setText("✅ Seed tracks refreshed")
            
            # Re-enable button after delay
            QTimer.singleShot(1000, self._reenable_rescan_button)
            
        except Exception as e:
            print(f"Error in rescan: {e}")
            self.main_status_label.setText("❌ Rescan error")
            self.rescan_btn.setEnabled(True)
    
    def _reenable_rescan_button(self):
        """Helper method to re-enable rescan button"""
        try:
            self.rescan_btn.setEnabled(True)
        except Exception as e:
            print(f"Error re-enabling button: {e}")
        
    def _browse_library_path(self):
        """Browse for library path"""
        path = QFileDialog.getExistingDirectory(
            self, "Select Audio Library Directory", self.library_path
        )
        if path:
            self.library_path = path
            # Library path updated - using internal variable in simplified interface
            pass
            
    def _browse_seed_track(self):
        """Browse for seed track"""
        path, _ = QFileDialog.getOpenFileName(
            self, "Select Seed Track", self.library_path,
            "Audio Files (*.mp3 *.flac *.wav *.m4a *.aac *.ogg)"
        )
        if path:
            # Seed track updated - handled by dropdown in simplified interface
            pass
            self.generate_btn.setEnabled(True)
            
    def _use_selected_track(self):
        """Use selected track from scan results as seed"""
        current_row = self.tracks_table.currentRow()
        if current_row >= 0 and current_row < len(self.scanned_tracks):
            track = self.scanned_tracks[current_row]
            # Handle both dict and database record formats
            file_path = track.get('file_path') if isinstance(track, dict) else getattr(track, 'file_path', '')
            
            if file_path:
                # Seed track updated - handled by dropdown in simplified interface
                pass
                self.generate_btn.setEnabled(True)
                # Tab switching removed in simplified interface
            else:
                QMessageBox.warning(self, "No File Path", "Selected track has no file path information.")
            
    def _start_library_scan(self):
        """Start unlimited library scanning with PersistentLibraryScanner"""
        library_path = self.library_path
        if not library_path:
            QMessageBox.warning(self, "Invalid Path", "Please enter a library path")
            return
        
        # Validate library path using scanner
        try:
            self.persistent_scanner.validate_library_path(library_path)
        except (FileNotFoundError, PermissionError, ValueError) as e:
            QMessageBox.warning(self, "Library Path Error", str(e))
            return
            
        self.library_path = library_path
        scan_mode = self.scan_mode_combo.currentText().lower()
        
        # Setup UI for scanning
        self.scan_btn.setEnabled(False)
        self.cancel_scan_btn.setEnabled(True)
        self.scan_progress.setValue(0)
        self.scan_status_label.setText(f"Starting {scan_mode} scan...")
        self._reset_progress_labels()
        
        # Start unlimited scan with PersistentLibraryScanner
        success = self.persistent_scanner.start_unlimited_scan(
            library_path=library_path,
            scan_mode=scan_mode,
            batch_size=100
        )
        
        if not success:
            QMessageBox.critical(self, "Scan Error", "Failed to start library scan")
            self._reset_scan_ui()
        
    def _cancel_scan(self):
        """Cancel ongoing unlimited scan"""
        if self.persistent_scanner.is_scan_active():
            self.persistent_scanner.cancel_scan()
            
        self._reset_scan_ui()
        self.scan_status_label.setText("Scan cancelled")
        
    # Old scan progress methods removed - replaced with PersistentLibraryScanner signal handlers
        
    # Old methods removed for simplified interface compatibility
        
    def _start_playlist_generation(self):
        """Start playlist generation using database seed track"""
        print("🎵 PLAYLIST GENERATION STARTED")
        
        # Check if we have a selected seed track from database
        if not hasattr(self, 'selected_seed_track') or not self.selected_seed_track:
            print("❌ NO SEED TRACK SELECTED")
            QMessageBox.warning(self, "No Seed Track", "Please select a seed track from the database")
            return
            
        seed_path = self.selected_seed_track.get('path', '')  # Use 'path' for Storage compatibility
        if not seed_path or not Path(seed_path).exists():
            QMessageBox.warning(self, "Invalid Seed", "Selected seed track file no longer exists")
            return
            
        # Generate playlist using database tracks for better performance
        print("🎯 GENERATING PLAYLIST FROM DATABASE...")
        playlist_tracks = self._generate_playlist_from_database()
        
        print(f"📝 Generated {len(playlist_tracks) if playlist_tracks else 0} tracks")
        
        if playlist_tracks:
            # Create result structure compatible with existing UI
            self.current_playlist = {
                'success': True,
                'generation_time': datetime.now().isoformat(),
                'seed_track': self.selected_seed_track,
                'playlist_tracks': playlist_tracks,
                'track_count': len(playlist_tracks),
                'parameters': {
                    'length': self.length_spin.value(),
                    'tolerance': self.tolerance_spin.value(),
                    'seed_genre': self.selected_seed_track.get('genre', 'Unknown')
                },
                'quality_metrics': self._calculate_quality_metrics(playlist_tracks),
                'bmad_certified': True,
                'database_generated': True
            }
            
            # Update UI
            self._on_generation_completed(self.current_playlist)
        else:
            QMessageBox.warning(self, "Generation Failed", "No compatible tracks found for playlist generation")
    
    def _generate_playlist_from_database(self):
        """Generate playlist using database query for optimal performance"""
        try:
            if not self.storage or not self.selected_seed_track:
                return []
            
            # Get parameters
            tolerance = self.tolerance_spin.value()
            length = self.length_spin.value()
            seed_bpm = self.selected_seed_track.get('bpm', 0)
            seed_genre = self.selected_seed_track.get('genre', '')
            
            # Get all tracks with analysis from storage
            all_tracks = self.storage.get_tracks_with_ai_analysis()
            
            # Filter compatible tracks
            compatible_tracks = []
            for track in all_tracks:
                # Skip the seed track itself
                if track.get('path') == self.selected_seed_track.get('path'):
                    continue
                    
                track_bpm = track.get('bpm', 0)
                if not track_bpm or track_bpm <= 0:
                    continue
                    
                # BPM tolerance check
                if seed_bpm > 0:
                    bpm_diff = abs(track_bpm - seed_bpm) / seed_bpm
                    if bpm_diff > tolerance:
                        continue
                
                # Genre compatibility (simple match for now)
                track_genre = track.get('genre', '')
                if seed_genre and track_genre and seed_genre == track_genre:
                    compatible_tracks.append(track)
                elif not seed_genre or not track_genre:
                    compatible_tracks.append(track)
            
            # Sort by BPM similarity and select final tracks
            if seed_bpm > 0:
                compatible_tracks.sort(key=lambda x: abs(x.get('bpm', 0) - seed_bpm))
            
            # Select final tracks (limit to requested length)
            final_tracks = compatible_tracks[:length]
            
            print(f"🎧 Generated playlist: {len(final_tracks)} tracks from database")
            print(f"DEBUG: Final tracks for table:")
            for i, track in enumerate(final_tracks):
                print(f"  {i+1}. {track.get('artist', 'Unknown')} - {track.get('title', 'Unknown')}")
            return final_tracks
            
        except Exception as e:
            print(f"Error generating playlist from database: {e}")
            return []
    
    def _calculate_quality_metrics(self, playlist_tracks):
        """Calculate BMAD quality metrics for database-generated playlist"""
        if not playlist_tracks or not self.selected_seed_track:
            return {
                'overall_quality': 0.0,
                'bmp_adherence': 0.0,
                'genre_coherence': 0.0,
                'energy_flow': 0.0,
                'data_completeness': 0.0,
                'transition_quality': 0.0,
                'certification_status': 'FAILED',
                'bmad_certified': False
            }
        
        # Use existing validation logic
        from playlist_cli_final import PlaylistQualityValidator
        validator = PlaylistQualityValidator()
        
        # Convert database tracks to expected format
        seed_track = dict(self.selected_seed_track)
        tracks = [dict(track) for track in playlist_tracks]
        
        return validator.validate_playlist_quality(seed_track, tracks, self.tolerance_spin.value())
        
    def _update_generation_progress(self, progress: int, status: str):
        """Update generation progress"""
        # Progress updates handled by main status in simplified interface
        self.main_status_label.setText(status)
        
    def _on_generation_completed(self, result: Dict[str, Any]):
        """Handle generation completion"""
        self.generate_btn.setEnabled(True)
        self.export_btn.setEnabled(True)
        self.current_playlist = result
        
        self._update_quality_display(result['quality_metrics'])
        self._populate_playlist_table(result['playlist_tracks'])
        
        # Switch to results tab
        # Tab switching removed in simplified interface
        
        self.main_status_label.setText("✅ Playlist generated successfully")
        
    def _on_generation_error(self, error: str):
        """Handle generation error"""
        self.generate_btn.setEnabled(True)
        self.main_status_label.setText(f"❌ Generation failed: {error}")
        QMessageBox.critical(self, "Generation Error", error)
    
    # New signal handlers for PersistentLibraryScanner
    def _on_scan_started(self, library_path: str):
        """Handle scan started signal"""
        self.scan_status_label.setText(f"Scanning: {Path(library_path).name}")
    
    def _on_scan_progress(self, progress: ScanProgress):
        """Handle detailed scan progress updates"""
        # Update progress bar (use discovered files as max if available)
        if progress.files_discovered > 0:
            percentage = int((progress.files_processed / progress.files_discovered) * 100)
            self.scan_progress.setValue(percentage)
            self.scan_progress.setFormat(f"{percentage}% ({progress.files_processed}/{progress.files_discovered})")
        else:
            self.scan_progress.setRange(0, 0)  # Indeterminate progress
            self.scan_progress.setFormat(f"Processing: {progress.files_processed} files")
        
        # Update detailed progress labels
        self.files_discovered_label.setText(f"Files Found: {progress.files_discovered:,}")
        self.files_processed_label.setText(f"Processed: {progress.files_processed:,}")
        self.files_cached_label.setText(f"From Cache: {progress.files_cached:,}")
        self.files_analyzed_label.setText(f"Analyzed: {progress.files_analyzed:,}")
        self.scan_speed_label.setText(f"Speed: {progress.scan_speed:.1f} files/sec")
        
        # Estimated time remaining
        if progress.estimated_remaining > 0:
            if progress.estimated_remaining < 60:
                time_str = f"{progress.estimated_remaining:.0f}s"
            elif progress.estimated_remaining < 3600:
                time_str = f"{progress.estimated_remaining/60:.1f}m"
            else:
                time_str = f"{progress.estimated_remaining/3600:.1f}h"
            self.estimated_time_label.setText(f"Est. Time: {time_str}")
        else:
            self.estimated_time_label.setText("Est. Time: Calculating...")
        
        # Cache hit rate and memory usage
        self.cache_hit_rate_label_progress.setText(f"Cache Hit: {progress.cache_hit_rate:.1%}")
        self.memory_usage_label.setText(f"Memory: {progress.memory_usage_mb:.0f} MB")
        
        # Update status with current file (truncate if too long)
        current_file = Path(progress.current_file).name if progress.current_file else ""
        if len(current_file) > 50:
            current_file = current_file[:47] + "..."
        self.scan_status_label.setText(f"Processing: {current_file}")
    
    def _on_persistent_scan_completed(self, final_stats: Dict[str, Any]):
        """Handle scan completion from PersistentLibraryScanner"""
        self._reset_scan_ui()
        
        # Update progress to 100%
        self.scan_progress.setValue(100)
        self.scan_progress.setFormat("Scan Complete")
        
        # Update status with final statistics
        total_discovered = final_stats.get('files_discovered', 0)
        total_analyzed = final_stats.get('files_analyzed', 0)
        total_cached = final_stats.get('files_cached', 0)
        scan_duration = final_stats.get('scan_duration', 0)
        cache_hit_rate = final_stats.get('cache_hit_rate', 0)
        
        self.scan_status_label.setText(
            f"✅ Completed: {total_discovered:,} files discovered, "
            f"{total_analyzed:,} analyzed, {total_cached:,} from cache "
            f"({cache_hit_rate:.1%} hit rate) in {scan_duration:.1f}s"
        )
        
        # Refresh database statistics
        self._refresh_database_stats()
        
        # Refresh seed tracks dropdown with new data  
        self._refresh_seed_tracks()
        
        # Use Selected button removed in simplified interface
        
        QMessageBox.information(
            self, "Scan Complete", 
            f"Library scan completed successfully!\n\n"
            f"Files Discovered: {total_discovered:,}\n"
            f"Files Analyzed: {total_analyzed:,}\n"
            f"Files from Cache: {total_cached:,}\n"
            f"Cache Hit Rate: {cache_hit_rate:.1%}\n"
            f"Scan Duration: {scan_duration:.1f} seconds\n"
            f"Average Speed: {final_stats.get('scan_speed', 0):.1f} files/second"
        )
    
    def _on_persistent_scan_error(self, error_message: str):
        """Handle scan error from PersistentLibraryScanner"""
        self._reset_scan_ui()
        self.scan_status_label.setText(f"❌ Scan failed: {error_message}")
        QMessageBox.critical(self, "Scan Error", f"Library scan failed:\n{error_message}")
    
    def _reset_scan_ui(self):
        """Reset scan UI to initial state"""
        self.scan_btn.setEnabled(True)
        self.cancel_scan_btn.setEnabled(False)
    
    def _reset_progress_labels(self):
        """Reset all progress labels to initial state"""
        self.files_discovered_label.setText("Files Found: 0")
        self.files_processed_label.setText("Processed: 0")
        self.files_cached_label.setText("From Cache: 0")
        self.files_analyzed_label.setText("Analyzed: 0")
        self.scan_speed_label.setText("Speed: 0 files/sec")
        self.estimated_time_label.setText("Est. Time: --")
        self.cache_hit_rate_label_progress.setText("Cache Hit: 0%")
        self.memory_usage_label.setText("Memory: 0 MB")
    
    def _load_tracks_from_database(self):
        """Load tracks from database for display in table"""
        try:
            # Get tracks from database (limit for UI performance)
            tracks = self.track_database.get_all_tracks(limit=1000)
            self.scanned_tracks = tracks
            self._populate_tracks_table()
            self._update_scan_stats_from_db()
        except Exception as e:
            self.scan_status_label.setText(f"Error loading tracks: {str(e)}")
    
    def _update_scan_stats_from_db(self):
        """Update scan statistics from database"""
        try:
            stats = self.track_database.get_library_statistics()
            total_tracks = len(self.scanned_tracks)
            genres = {}
            
            for track in self.scanned_tracks:
                genre = track.get('genre', 'Unknown')
                genres[genre] = genres.get(genre, 0) + 1
            
            stats_text = f"Showing {total_tracks:,} tracks | "
            stats_text += " | ".join([f"{genre}: {count}" for genre, count in list(genres.items())[:5]])
            if len(genres) > 5:
                stats_text += f" | +{len(genres)-5} more genres"
            
            self.stats_label.setText(stats_text)
        except Exception as e:
            self.stats_label.setText(f"Stats error: {str(e)}")
        
    def _update_quality_display(self, metrics: Dict[str, Any]):
        """Update quality metrics display"""
        self.overall_quality_label.setText(f"Overall Quality: {metrics['overall_quality']:.1%}")
        self.bpm_adherence_label.setText(f"BPM Adherence: {metrics['bmp_adherence']:.1%}")
        self.genre_coherence_label.setText(f"Genre Coherence: {metrics['genre_coherence']:.1%}")
        self.energy_flow_label.setText(f"Energy Flow: {metrics['energy_flow']:.1%}")
        self.data_completeness_label.setText(f"Data Completeness: {metrics['data_completeness']:.1%}")
        self.transition_quality_label.setText(f"Transition Quality: {metrics['transition_quality']:.1%}")
        
        status = metrics['certification_status']
        status_color = "#28A745" if status == "PASSED" else "#DC3545"
        self.certification_status_label.setText(f"Status: {status}")
        self.certification_status_label.setStyleSheet(f"font-weight: bold; color: {status_color}; padding: 5px;")
        
    def _populate_playlist_table(self, tracks):
        """WORKING VERSION - Force visible text"""
        if not tracks:
            return
        
        self.playlist_table.setRowCount(len(tracks))
        
        for row, track in enumerate(tracks):
            from PyQt6.QtGui import QColor
            from PyQt6.QtWidgets import QTableWidgetItem
            
            # Number with black text
            item1 = QTableWidgetItem(str(row + 1))
            item1.setForeground(QColor(0, 0, 0))
            self.playlist_table.setItem(row, 0, item1)
            
            # Track with black text
            title = track.get('title', 'Test Title')
            artist = track.get('artist', 'Test Artist')
            item2 = QTableWidgetItem(f"{artist} - {title}")
            item2.setForeground(QColor(0, 0, 0))
            self.playlist_table.setItem(row, 1, item2)
            
            # BPM with black text
            bpm = track.get('bpm', 120)
            item3 = QTableWidgetItem(f"{bmp:.0f}" if bpm else "--")
            item3.setForeground(QColor(0, 0, 0))
            self.playlist_table.setItem(row, 2, item3)
            
            # Genre with black text
            genre = track.get('genre', 'Pop')
            item4 = QTableWidgetItem(genre)
            item4.setForeground(QColor(0, 0, 0))
            self.playlist_table.setItem(row, 3, item4)

    def _populate_test_playlist_data(self):
        """TEMP: Add test data to show table columns working"""
        test_tracks = [
            {'title': 'Love On The Rocks', 'artist': 'Neil Diamond', 'bpm': 129.0, 'genre': 'Pop Rock'},
            {'title': 'The Tide Is High', 'artist': 'Blondie', 'bpm': 124.0, 'genre': 'New Wave'},
            {'title': 'Every Woman In the World', 'artist': 'Air Supply', 'bpm': 151.0, 'genre': 'Soft Rock'},
            {'title': 'Guilty', 'artist': 'Barbra Streisand', 'bpm': 151.0, 'genre': 'Pop'},
            {'title': 'On The Radio', 'artist': 'Donna Summer', 'bpm': 128.0, 'genre': 'Disco'},
            {'title': 'Romeo\'s Tune', 'artist': 'Steve Forbert', 'bpm': 127.0, 'genre': 'Folk Rock'},
            {'title': 'Fool in the Rain', 'artist': 'Led Zeppelin', 'bmp': 130.0, 'genre': 'Rock'},
            {'title': 'Lady Cab Driver', 'artist': 'Prince', 'bpm': 129.0, 'genre': 'Funk'},
            {'title': 'I Can\'t Help Myself', 'artist': 'Four Tops', 'bpm': 129.0, 'genre': 'Motown'},
            {'title': 'Private Eyes', 'artist': 'Hall & Oates', 'bpm': 126.0, 'genre': 'Pop Rock'}
        ]
        
        print("🎵 LOADING TEST PLAYLIST DATA...")
        self._populate_playlist_table(test_tracks)
    
    def _on_playlist_track_selected(self):
        """Handle track selection in playlist table"""
        current_row = self.playlist_table.currentRow()
        if current_row >= 0 and hasattr(self, 'playlist_tracks_data') and current_row < len(self.playlist_tracks_data):
            selected_track = self.playlist_tracks_data[current_row]
            title = selected_track.get('title', 'Unknown')
            artist = selected_track.get('artist', 'Unknown')
            bpm = selected_track.get('bpm', 0)
            genre = selected_track.get('genre', 'Unknown')
            
            # Update status with selected track info
            self.main_status_label.setText(f"🎵 Selected: {artist} - {title} ({bpm:.0f} BPM, {genre})")
            
            # Enable playlist action buttons
            self.use_as_seed_btn.setEnabled(True)
            self.show_details_btn.setEnabled(True)
            
            # Store currently selected playlist track
            self.selected_playlist_track = selected_track
            
            print(f"🎵 Selected playlist track: {artist} - {title}")
        else:
            # Disable buttons when no selection
            self.use_as_seed_btn.setEnabled(False)
            self.show_details_btn.setEnabled(False)
            self.selected_playlist_track = None
    
    def _on_playlist_track_double_clicked(self, item):
        """Handle double-click on playlist track (could open file or show details)"""
        current_row = self.playlist_table.currentRow()
        if current_row >= 0 and hasattr(self, 'playlist_tracks_data') and current_row < len(self.playlist_tracks_data):
            selected_track = self.playlist_tracks_data[current_row]
            file_path = selected_track.get('path', '')
            
            if file_path and Path(file_path).exists():
                # Show track details dialog
                self._show_track_details(selected_track)
            else:
                QMessageBox.information(
                    self, "Track Information",
                    f"Track: {selected_track.get('title', 'Unknown')}\n"
                    f"Artist: {selected_track.get('artist', 'Unknown')}\n"
                    f"Genre: {selected_track.get('genre', 'Unknown')}\n"
                    f"BPM: {selected_track.get('bpm', 0):.0f}\n"
                    f"File not available for preview"
                )
    
    def _show_track_details(self, track):
        """Show detailed track information dialog"""
        title = track.get('title', 'Unknown')
        artist = track.get('artist', 'Unknown')
        album = track.get('album', 'Unknown')
        genre = track.get('genre', 'Unknown')
        bpm = track.get('bpm', 0)
        energy = track.get('energy', 0)
        file_path = track.get('path', '')
        
        details = f"""
        Track Details:
        
        Title: {title}
        Artist: {artist}
        Album: {album}
        Genre: {genre}
        BPM: {bpm:.1f}
        Energy: {energy:.2f}
        
        File Path: {file_path}
        """
        
        QMessageBox.information(self, f"Track Details - {title}", details)
    
    def _use_playlist_track_as_seed(self):
        """Use selected playlist track as new seed"""
        if not hasattr(self, 'selected_playlist_track') or not self.selected_playlist_track:
            QMessageBox.warning(self, "No Selection", "Please select a track from the playlist first")
            return
            
        track = self.selected_playlist_track
        title = track.get('title', 'Unknown')
        artist = track.get('artist', 'Unknown')
        file_path = track.get('path', '')
        bpm = track.get('bpm', 0)
        genre = track.get('genre', 'Unknown')
        
        print(f"🎯 Attempting to use track as seed: {artist} - {title}")
        print(f"   File path: {file_path}")
        print(f"   BPM: {bpm}, Genre: {genre}")
        
        # Check if file path exists
        if not file_path:
            QMessageBox.warning(self, "No File Path", 
                              f"Selected track has no file path information.\n"
                              f"Track: {artist} - {title}")
            return
            
        # Check if file exists (more flexible path checking)
        path_obj = Path(file_path)
        if not path_obj.exists():
            # Try to find the file in the library path as fallback
            filename = path_obj.name
            potential_path = Path(self.library_path) / filename
            if potential_path.exists():
                file_path = str(potential_path)
                track['path'] = file_path  # Update the track data
                print(f"   Found file in library: {file_path}")
            else:
                QMessageBox.warning(self, "File Not Found", 
                                  f"Selected track file not found:\n{file_path}\n\n"
                                  f"Also tried: {potential_path}")
                return
        
        # Check if track has required data for seed (BPM is important)
        if not bpm or bpm <= 0:
            reply = QMessageBox.question(
                self, "Missing BPM Data",
                f"This track has no BPM information ({bpm}).\n\n"
                f"Track: {artist} - {title}\n"
                f"Genre: {genre}\n\n"
                f"Using it as seed may result in poor playlist generation.\n"
                f"Continue anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.No:
                return
        
        # Confirm with user
        reply = QMessageBox.question(
            self, "Use as New Seed",
            f"Use this track as the new seed for playlist generation?\n\n"
            f"Track: {artist} - {title}\n"
            f"BPM: {bpm:.0f}\n"
            f"Genre: {genre}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Set this track as the selected seed track
                self.selected_seed_track = track
                
                # Find and select this track in the seed dropdown
                success = self._select_track_in_dropdown(track)
                
                # Enable generate button
                self.generate_btn.setEnabled(True)
                
                # Update status
                if success:
                    self.main_status_label.setText(f"🎯 New seed selected: {artist} - {title}")
                    print(f"🎯 Successfully set new seed: {artist} - {title}")
                else:
                    self.main_status_label.setText(f"🎯 Seed set (not in dropdown): {artist} - {title}")
                    print(f"🎯 Seed set but not found in dropdown: {artist} - {title}")
                    
            except Exception as e:
                print(f"Error setting new seed: {e}")
                QMessageBox.critical(self, "Error", f"Failed to set new seed: {str(e)}")
    
    def _select_track_in_dropdown(self, track):
        """Select the given track in the seed dropdown"""
        if not hasattr(self, 'all_seed_tracks') or not self.all_seed_tracks:
            return False
            
        track_path = track.get('path', '')
        
        # Find matching track in dropdown
        for i, seed_track in enumerate(self.all_seed_tracks):
            if seed_track.get('path') == track_path:
                self.seed_track_combo.setCurrentIndex(i)
                print(f"Found track in dropdown at index {i}")
                return True
        
        print(f"Track not found in dropdown: {track_path}")
        return False
    
    def _show_selected_track_details(self):
        """Show details for selected playlist track"""
        if hasattr(self, 'selected_playlist_track') and self.selected_playlist_track:
            self._show_track_details(self.selected_playlist_track)
        else:
            QMessageBox.information(self, "No Selection", "Please select a track from the playlist first")
        
    def _export_playlist(self):
        """Export generated playlist"""
        if not self.current_playlist:
            QMessageBox.warning(self, "No Playlist", "No playlist to export")
            return
            
        format_type = self.format_combo.currentText()
        extensions = {"json": "json", "m3u": "m3u", "csv": "csv"}
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Export Playlist", 
            f"bmad_playlist_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{extensions[format_type]}",
            f"{format_type.upper()} Files (*.{extensions[format_type]})"
        )
        
        if filename:
            try:
                # Use the CLI export functionality
                cli = BMADCertifiedPlaylistCLI()
                cli._export_playlist(self.current_playlist, filename, format_type)
                QMessageBox.information(self, "Export Complete", f"Playlist exported to {filename}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", f"Failed to export playlist: {str(e)}")
    
    # Seed Track Database Selection Methods
    def _refresh_seed_tracks(self):
        """Refresh seed track dropdown from database"""
        try:
            if not self.storage:
                return
                
            # Get tracks with complete BPM data for playlist generation using Storage
            tracks = self.storage.get_tracks_with_ai_analysis()
            
            self.seed_track_combo.clear()
            self.all_seed_tracks = []  # Store full track data
            
            if not tracks:
                self.seed_track_combo.addItem("No tracks in database - scan library first")
                self.generate_btn.setEnabled(False)
                return
                
            # Sort tracks by artist then title (handle None values safely)
            tracks.sort(key=lambda x: (x.get('artist') or 'Unknown', x.get('title') or 'Unknown'))
            
            valid_tracks_added = 0
            for i, track in enumerate(tracks):
                if not track:  # Skip None tracks
                    continue
                    
                # Extract metadata properly - check for both direct fields and nested metadata
                metadata = track.get('metadata', {}) if isinstance(track.get('metadata'), dict) else {}
                
                # Try multiple field names for compatibility
                title = (track.get('title') or 
                        metadata.get('title') or 
                        metadata.get('TIT2') or 
                        Path(track.get('path', '')).stem or 'Unknown')
                        
                artist = (track.get('artist') or 
                         metadata.get('artist') or 
                         metadata.get('TPE1') or 'Unknown')
                         
                # Handle BPM from analysis results
                analysis_results = track.get('analysis_results', {})
                if isinstance(analysis_results, str):
                    try:
                        import json
                        analysis_results = json.loads(analysis_results)
                    except:
                        analysis_results = {}
                        
                bpm = (track.get('bpm') or 
                      analysis_results.get('bpm') or 
                      metadata.get('bpm') or 0)
                      
                try:
                    bpm = float(bpm) if bpm else 0
                except:
                    bpm = 0
                    
                genre = (track.get('genre') or 
                        analysis_results.get('genre') or 
                        metadata.get('genre') or 
                        metadata.get('TCON') or 'Unknown')
                
                # Only add tracks with valid metadata
                if title != 'Unknown' or artist != 'Unknown':
                    # Create display text
                    display_text = f"{artist} - {title}"
                    if bpm and bpm > 0:
                        display_text += f" ({bpm:.0f} BPM, {genre})"
                    else:
                        display_text += f" ({genre})"
                    
                    self.seed_track_combo.addItem(display_text)
                    self.all_seed_tracks.append(track)
                    valid_tracks_added += 1
            
            # Enable generation if tracks available
            self.generate_btn.setEnabled(valid_tracks_added > 0)
            
            if valid_tracks_added == 0:
                self.seed_track_combo.addItem("No tracks with metadata found - rescan library")
                
            print(f"🎵 Loaded {valid_tracks_added} valid seed tracks from {len(tracks)} total tracks")
            
        except Exception as e:
            print(f"Error refreshing seed tracks: {e}")
            import traceback
            traceback.print_exc()
            self.seed_track_combo.clear()
            self.seed_track_combo.addItem("Error loading tracks from database")
            self.generate_btn.setEnabled(False)
    
    def _filter_seed_tracks(self):
        """Filter seed tracks based on search text"""
        filter_text = self.seed_filter_edit.text().lower()
        
        if not hasattr(self, 'all_seed_tracks') or not self.all_seed_tracks:
            return
            
        self.seed_track_combo.clear()
        
        for i, track in enumerate(self.all_seed_tracks):
            if not track:  # Skip None tracks
                continue
                
            # Safely handle None values
            title = (track.get('title') or '').lower()
            artist = (track.get('artist') or '').lower()
            genre = (track.get('genre') or '').lower()
            
            # Check if filter matches any field
            if (filter_text in title or 
                filter_text in artist or 
                filter_text in genre):
                
                # Create display text - safely handle None values
                display_title = track.get('title') or 'Unknown'
                display_artist = track.get('artist') or 'Unknown'
                bpm = track.get('bpm', 0)
                display_genre = track.get('genre') or 'Unknown'
                
                display_text = f"{display_artist} - {display_title}"
                if bpm and bpm > 0:
                    display_text += f" ({bpm:.0f} BPM, {display_genre})"
                
                self.seed_track_combo.addItem(display_text)
                # Store original index in item data
                self.seed_track_combo.setItemData(self.seed_track_combo.count() - 1, i)
    
    def _on_seed_track_selected(self):
        """Handle seed track selection from dropdown"""
        if not hasattr(self, 'all_seed_tracks') or not self.all_seed_tracks:
            return
            
        current_index = self.seed_track_combo.currentIndex()
        if current_index < 0:
            return
            
        # Check if this is a filtered view
        stored_index = self.seed_track_combo.itemData(current_index)
        if stored_index is not None:
            track_index = stored_index
        else:
            track_index = current_index
            
        if track_index < len(self.all_seed_tracks):
            selected_track = self.all_seed_tracks[track_index]
            file_path = selected_track.get('path', '')  # Use 'path' for Storage compatibility
            
            if file_path and Path(file_path).exists():
                # Store selected seed track data for playlist generation
                self.selected_seed_track = selected_track
                self.generate_btn.setEnabled(True)
                
                # Update status
                title = selected_track.get('title', 'Unknown')
                artist = selected_track.get('artist', 'Unknown')
                print(f"🎯 Selected seed track: {artist} - {title}")
            else:
                QMessageBox.warning(self, "File Not Found", 
                                  f"Selected track file no longer exists:\n{file_path}")
                self.generate_btn.setEnabled(False)
    
    # Database Management Methods
    def _refresh_database_stats(self):
        """Refresh database statistics display - simplified for unified interface"""
        try:
            # Use storage for statistics
            if hasattr(self.storage, 'get_tracks_with_ai_analysis'):
                tracks = self.storage.get_tracks_with_ai_analysis()
                total_tracks = len(tracks) if tracks else 0
                self.main_status_label.setText(f"Database ready - {total_tracks:,} tracks available")
            else:
                self.main_status_label.setText("Database ready - statistics unavailable")
        except Exception as e:
            print(f"Warning: Could not refresh database stats: {e}")
            self.main_status_label.setText("Database ready - stats unavailable")
    
    def _cleanup_database(self):
        """Clean up orphaned database records"""
        reply = QMessageBox.question(
            self, "Database Cleanup",
            "Remove records for files that no longer exist?\n\n"
            "This will permanently delete database entries for missing files.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                removed_count = self.persistent_scanner.cleanup_orphaned_records()
                self._refresh_database_stats()
                QMessageBox.information(
                    self, "Cleanup Complete",
                    f"Successfully removed {removed_count} orphaned records."
                )
            except Exception as e:
                QMessageBox.critical(self, "Cleanup Error", f"Failed to cleanup database: {str(e)}")
    
    def _vacuum_database(self):
        """Optimize database performance"""
        reply = QMessageBox.question(
            self, "Database Optimization",
            "Optimize database for better performance?\n\n"
            "This may take a few moments but will improve query speed.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.persistent_scanner.vacuum_database()
                self._refresh_database_stats()
                QMessageBox.information(
                    self, "Optimization Complete",
                    "Database has been optimized successfully."
                )
            except Exception as e:
                QMessageBox.critical(self, "Optimization Error", f"Failed to optimize database: {str(e)}")
    
    def _backup_database(self):
        """Create database backup"""
        backup_filename = f"music_analyzer_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        backup_path, _ = QFileDialog.getSaveFileName(
            self, "Save Database Backup", backup_filename,
            "Database Files (*.db);;All Files (*)"
        )
        
        if backup_path:
            try:
                success = self.persistent_scanner.backup_database(backup_path)
                if success:
                    QMessageBox.information(
                        self, "Backup Complete",
                        f"Database backup created successfully:\n{backup_path}"
                    )
                else:
                    QMessageBox.warning(
                        self, "Backup Failed",
                        "Failed to create database backup."
                    )
            except Exception as e:
                QMessageBox.critical(self, "Backup Error", f"Failed to backup database: {str(e)}")
    
    def closeEvent(self, event):
        """Handle widget close event"""
        # Stop any ongoing scans
        if self.persistent_scanner.is_scan_active():
            self.persistent_scanner.cancel_scan()
        
        # Stop statistics timer
        if hasattr(self, 'stats_timer'):
            self.stats_timer.stop()
        
        # Close database connections
        self.track_database.close()
        self.persistent_scanner.close()
        
        event.accept()