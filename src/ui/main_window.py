"""Minimal PyQt6 UI for local DJ analysis.

Features:
- Select a directory of audio files
- Analyze sequentially in a background thread (cancelable)
- Show log and progress
- Export CSV summary
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable, List

from PyQt6.QtCore import QThread, pyqtSignal, QSettings, QItemSelectionModel, QSize
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
    QLabel,
    QFileDialog,
    QListWidget,
    QProgressBar,
    QStatusBar,
    QMessageBox,
    QComboBox,
    QSpinBox,
    QCheckBox,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QGroupBox,
)

from src.services.analyzer import Analyzer
from src.services.storage import Storage
from src.ui.visualizers.visuals import show_visuals
from src.models.progress import AnalysisProgress, AnalysisStage
from src.services.time_estimator import TimeEstimator
from src.lib.progress_callback import create_pyqt_signal_callback
from src.ui.styles import StyleManager
from src.ui.layouts import ResponsiveLayoutManager


AUDIO_EXTS = {".wav", ".mp3", ".flac", ".aac", ".ogg", ".m4a"}


def format_track_name(track_data: dict, path_fallback: str = None) -> str:
    """Format track name using available metadata or path fallback"""
    if not isinstance(track_data, dict):
        return path_fallback or "Unknown Track"
    
    artist = track_data.get('artist')
    title = track_data.get('title') 
    path = track_data.get('path') or path_fallback
    
    if artist and title:
        return f"{artist} - {title}"
    elif title:
        return title
    elif artist:
        return f"{artist} - [Unknown Title]"
    elif path:
        from pathlib import Path
        return Path(path).name
    else:
        return "Unknown Track"


def iter_audio_files(root: Path, exts: Iterable[str]) -> List[Path]:
    ex = {e.lower() if e.startswith(".") else f".{e.lower()}" for e in exts}
    out: List[Path] = []
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            if Path(fn).suffix.lower() in ex:
                out.append(Path(dirpath) / fn)
    return out


class AnalyzeWorker(QThread):
    progress = pyqtSignal(int, int)
    log = pyqtSignal(str)
    done = pyqtSignal(int, int)  # ok, errors
    
    # New detailed progress signals
    stage_progress = pyqtSignal(AnalysisStage, float, str)  # stage, progress (0-1), message
    stage_changed = pyqtSignal(AnalysisStage, str)  # new stage, file name
    time_estimate = pyqtSignal(float, float)  # elapsed seconds, remaining seconds
    track_completed = pyqtSignal(str, dict)  # path, analysis_results

    def __init__(self, dir_path: Path, db_path: Path, workers: int = 1, exts: Iterable[str] | None = None):
        super().__init__()
        self.dir_path = dir_path
        self.db_path = db_path
        self.workers = workers
        self.exts = list(exts or AUDIO_EXTS)
        self._stop = False
        
        # Progress tracking
        self.progress_tracker = AnalysisProgress()
        self.time_estimator = TimeEstimator()

    def stop(self):
        self._stop = True

    def run(self):
        try:
            storage = Storage.from_path(self.db_path)
            analyzer = Analyzer(storage)
        except Exception as e:
            self.log.emit(f"[ERR] init: {e}")
            self.done.emit(0, 1)
            return

        files = iter_audio_files(self.dir_path, self.exts)
        total = len(files)
        ok = 0
        errs = 0
        
        # Initialize progress tracking
        self.progress_tracker.reset(total_files=total)
        self.time_estimator.clear_history()
        
        # Create progress callback for detailed reporting
        progress_callback = create_pyqt_signal_callback(
            self.stage_progress,
            self.stage_changed,
            self.time_estimate,
            self.time_estimator
        )
        
        self.progress.emit(0, total)
        
        for i, f in enumerate(files, 1):
            if self._stop:
                self.log.emit("[INFO] Cancelled by user")
                break
            
            # Update progress tracker for new file
            self.progress_tracker.advance_file(f.name)
            self.time_estimator.start_file_analysis()
            
            try:
                # Analyze with detailed progress reporting
                analyzer.analyze_path(str(f), progress_callback=progress_callback)
                ok += 1
                self.log.emit(f"[OK] {f}")
                
                # Get analysis results and emit track completion signal
                result = storage.get_analysis_by_path(str(f))
                if result:
                    self.track_completed.emit(str(f), result)
                
                # Complete timing for this file
                self.time_estimator.complete_file_analysis()
                
            except Exception as e:
                errs += 1
                self.log.emit(f"[ERR] {f}: {e}")
                # Still complete timing even on error
                self.time_estimator.complete_file_analysis()
            
            # Update overall progress
            self.progress.emit(i, total)
            
            # Update time estimates
            remaining_files = total - i
            if remaining_files > 0:
                elapsed = self.time_estimator.get_elapsed_time()
                remaining = self.time_estimator.get_remaining_time_estimate(
                    AnalysisStage.HAMMS_COMPUTATION, 1.0, remaining_files
                )
                if remaining is not None:
                    self.time_estimate.emit(elapsed, remaining)
        
        self.done.emit(ok, errs)


class MainWindow(QMainWindow):
    def __init_subclass__(cls):
        return super().__init_subclass__()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Music Analyzer Pro")
        
        # Initialize responsive layout manager (simplified for MacBook Pro 13")
        self.responsive_manager = ResponsiveLayoutManager(self)
        self.current_layout_mode = 'compact'
        
        # Initialize style manager
        self.style_manager = StyleManager(self)
        
        # Set initial window size optimized for 13" MacBook Pro
        self.resize(1200, 650)
        self.setMinimumSize(1000, 550)

        self.dir_edit = QLineEdit()
        self.browse_btn = QPushButton("Browse…")
        self.start_btn = QPushButton("Analyze")
        self.start_btn.setObjectName("start_btn")
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setObjectName("stop_btn")
        self.export_btn = QPushButton("Export CSV…")
        # Compatibility / Playlist controls
        self.seed_edit = QLineEdit()
        self.seed_browse = QPushButton("Seed…")
        self.suggest_btn = QPushButton("Suggest Compat")
        self.playlist_btn = QPushButton("Generate Playlist")
        self.visualize_btn = QPushButton("Visualize Seed")
        self.export_pl_btn = QPushButton("Export Playlist…")
        self.curve_combo = QComboBox(); self.curve_combo.addItems(["ascending","descending","flat"])
        self.result_table = QTableWidget(0,6)
        self.result_table.setHorizontalHeaderLabels(["Type","Path","BPM","Key","Energy","Score"])
        self.result_table.setSortingEnabled(True)
        self.copy_btn = QPushButton("Copy Selected") 
        self.length_spin = QSpinBox(); self.length_spin.setRange(2, 100); self.length_spin.setValue(12)
        self.bpm_tol_spin = QSpinBox(); self.bpm_tol_spin.setRange(2, 25); self.bpm_tol_spin.setValue(2)
        self.pref_rel_cb = QCheckBox("Prefer relative maj/min")
        self.result_list = QListWidget()
        
        # Progress tracking components
        self.progress = QProgressBar()  # Overall progress (files X of Y)
        self.progress.setVisible(True)
        self.progress.setRange(0, 100)
        self.progress.setValue(0)
        
        self.file_progress_bar = QProgressBar()  # Current file progress
        self.file_progress_bar.setVisible(True)
        self.file_progress_bar.setRange(0, 100)
        self.file_progress_bar.setValue(0)
        
        self.stage_progress_bar = QProgressBar()  # Current stage progress
        self.stage_progress_bar.setVisible(True)
        self.stage_progress_bar.setRange(0, 100)
        self.stage_progress_bar.setValue(0)
        
        self.file_label = QLabel("Ready to analyze...")  # Current file name
        self.stage_label = QLabel("")  # Current stage name
        self.time_label = QLabel("")  # Time elapsed/remaining
        
        self.log_list = QListWidget()
        self.status = QStatusBar()
        self.setStatusBar(self.status)

        # Create main widget and layout
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        
        # Setup simplified compact layout for 13" MacBook Pro
        self.setup_compact_layout_only()
        
        # Set compact theme optimized for 13"
        self.style_manager.set_theme('compact')
        self.style_manager.apply_theme_to_widget(self)

        self.worker: AnalyzeWorker | None = None
        self.db_path = Path("data/music.db")
        self.current_playlist = []

        self.browse_btn.clicked.connect(self.on_browse)
        self.start_btn.clicked.connect(self.on_start)
        self.stop_btn.clicked.connect(self.on_stop)
        self.export_btn.clicked.connect(self.on_export)
        self.seed_browse.clicked.connect(self.on_browse_seed)
        self.suggest_btn.clicked.connect(self.on_suggest)
        self.playlist_btn.clicked.connect(self.on_generate_playlist)
        self.visualize_btn.clicked.connect(self.on_visualize)
        self.export_pl_btn.clicked.connect(self.on_export_playlist)
        self.copy_btn.clicked.connect(self.on_copy_selected)
        
        # UI setup complete

    def on_browse(self):
        d = QFileDialog.getExistingDirectory(self, "Select audio directory")
        if d:
            self.dir_edit.setText(d)

    def on_start(self):
        if self.worker and self.worker.isRunning():
            QMessageBox.warning(self, "Busy", "Analysis already in progress")
            return
        dir_path = self.dir_edit.text().strip()
        if not dir_path:
            QMessageBox.warning(self, "No directory", "Please select a directory")
            return
        d = Path(dir_path)
        if not d.exists() or not d.is_dir():
            QMessageBox.warning(self, "Invalid directory", "Path is not a directory")
            return

        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.progress.setValue(0)
        self.result_table.setRowCount(0)  # Clear previous analysis results
        self.result_list.clear()          # Clear previous playlist results
        self.log_list.clear()             # Clear previous logs
        self.status.showMessage("Analyzing…")

        self.worker = AnalyzeWorker(d, self.db_path)
        self.worker.progress.connect(self.on_progress)
        self.worker.log.connect(self.on_log)
        self.worker.done.connect(self.on_done)
        
        # Connect new detailed progress signals
        self.worker.stage_progress.connect(self.on_stage_progress)
        self.worker.stage_changed.connect(self.on_stage_changed)
        self.worker.time_estimate.connect(self.on_time_estimate)
        self.worker.track_completed.connect(self.on_track_completed)
        self.worker.start()

    def on_stop(self):
        if self.worker and self.worker.isRunning():
            self.worker.stop()

    def on_progress(self, i: int, total: int):
        # Update overall file progress (X of Y files)
        self.progress.setMaximum(total if total > 0 else 1)
        self.progress.setValue(i)

    def on_log(self, msg: str):
        # Color-code log messages based on type
        item_text = msg
        if msg.startswith("[OK]"):
            item_text = f"✓ {msg[4:].strip()}"
        elif msg.startswith("[ERR]"):
            item_text = f"✗ {msg[5:].strip()}"
        elif msg.startswith("[INFO]"):
            item_text = f"ℹ {msg[6:].strip()}"
        
        self.log_list.addItem(item_text)
        self.log_list.scrollToBottom()

    def on_done(self, ok: int, errs: int):
        # Update progress bar color based on results
        if errs > 0:
            self.progress.setProperty("state", "error")
        else:
            self.progress.setProperty("state", "success")
        
        # Refresh styling to apply new state
        self.progress.style().unpolish(self.progress)
        self.progress.style().polish(self.progress)
        
        status_msg = f"Analysis Complete - Success: {ok}, Errors: {errs}"
        if errs > 0:
            status_msg += f" ⚠️"
        else:
            status_msg += " ✅"
        
        self.status.showMessage(status_msg)
    
    def on_stage_progress(self, stage: AnalysisStage, progress: float, message: str):
        """Handle stage progress updates."""
        # Update stage progress bar (0-100%)
        self.stage_progress_bar.setValue(int(progress * 100))
        
        # Update stage label with current message
        self.stage_label.setText(f"{stage.value}: {message}")
        
        # Update file progress bar based on overall stage completion
        # Calculate overall file progress based on stage weights
        stage_weights = {
            AnalysisStage.AUDIO_LOADING: 0.1,
            AnalysisStage.BPM_DETECTION: 0.2,
            AnalysisStage.KEY_DETECTION: 0.3,
            AnalysisStage.ENERGY_CALCULATION: 0.2,
            AnalysisStage.HAMMS_COMPUTATION: 0.2,
        }
        
        # Calculate cumulative progress
        stages = list(AnalysisStage)
        current_index = stages.index(stage)
        
        file_progress = 0.0
        for i, s in enumerate(stages):
            if i < current_index:
                file_progress += stage_weights.get(s, 0.2)
            elif i == current_index:
                file_progress += stage_weights.get(s, 0.2) * progress
                
        self.file_progress_bar.setValue(int(file_progress * 100))
    
    def on_stage_changed(self, stage: AnalysisStage, filename: str):
        """Handle stage change notifications."""
        # Update current file label
        self.file_label.setText(f"Analyzing: {filename}")
        
        # If this is the first stage, reset file progress; otherwise preserve it
        if stage == AnalysisStage.AUDIO_LOADING:
            self.file_progress_bar.setValue(0)
        
        # Reset stage progress bar for new stage
        self.stage_progress_bar.setValue(0)
        self.stage_label.setText(f"{stage.value}: Starting...")
    
    def on_time_estimate(self, elapsed: float, remaining: float):
        """Handle time estimation updates."""
        elapsed_str = f"{elapsed:.1f}s"
        if remaining > 0:
            remaining_str = f"{remaining:.1f}s"
            self.time_label.setText(f"Elapsed: {elapsed_str} | Remaining: {remaining_str}")
        else:
            self.time_label.setText(f"Elapsed: {elapsed_str}")
    
    def on_track_completed(self, path: str, analysis: dict):
        """Handle completed track analysis by adding results to table."""
        row = self.result_table.rowCount()
        self.result_table.insertRow(row)
        
        # Use metadata if available, fallback to filename
        from pathlib import Path
        display_name = analysis.get('title') or Path(path).name
        if analysis.get('artist') and analysis.get('title'):
            display_name = f"{analysis.get('artist')} - {analysis.get('title')}"
        elif analysis.get('title'):
            display_name = analysis.get('title')
        else:
            display_name = Path(path).name
        
        # Set table items with analysis results
        self.result_table.setItem(row, 0, QTableWidgetItem("Analysis"))  # Type
        self.result_table.setItem(row, 1, QTableWidgetItem(display_name))    # Track name
        self.result_table.setItem(row, 2, QTableWidgetItem(str(analysis.get('bpm', 'N/A'))))  # BPM
        self.result_table.setItem(row, 3, QTableWidgetItem(str(analysis.get('key', 'N/A'))))   # Key  
        self.result_table.setItem(row, 4, QTableWidgetItem(f"{analysis.get('energy', 0):.3f}")) # Energy
        self.result_table.setItem(row, 5, QTableWidgetItem("1.00"))      # Score (analysis always has perfect score)
        
        # Auto-scroll to show new results
        self.result_table.scrollToBottom()

    def on_export(self):
        try:
            storage = Storage.from_path(self.db_path)
            rows = storage.list_all_analyses()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Cannot open DB: {e}")
            return
        out_path, _ = QFileDialog.getSaveFileName(self, "Export CSV", "analysis.csv", "CSV Files (*.csv)")
        if not out_path:
            return
        try:
            with open(out_path, "w", encoding="utf-8") as f:
                f.write("path,bpm,key,energy,comment\n")
                for r in rows:
                    path = r.get("path", "")
                    bpm = r.get("bpm")
                    key = r.get("key") or ""
                    energy = r.get("energy")
                    comment = (r.get("comment") or "").replace(",", " ")
                    f.write(f"{path},{bpm if bpm is not None else ''},{key},{energy if energy is not None else ''},{comment}\n")
            QMessageBox.information(self, "Exported", f"CSV exported to {out_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Export failed: {e}")

    # --- Compatibility / Playlist ---
    def on_browse_seed(self):
        f, _ = QFileDialog.getOpenFileName(self, "Select seed track")
        if f:
            self.seed_edit.setText(f)

    def on_suggest(self):
        from src.services.compatibility import suggest_compatible
        try:
            # UI Configuration validation
            seed = self.seed_edit.text().strip()
            if not seed:
                QMessageBox.warning(self, "No seed", "Select a seed track")
                return
            
            if not Path(seed).exists():
                QMessageBox.critical(self, "File Error", f"Seed file does not exist: {seed}")
                return
            
            if not Path(seed).is_file():
                QMessageBox.critical(self, "File Error", f"Seed path is not a file: {seed}")
                return
            
            # Validate supported audio format
            if Path(seed).suffix.lower() not in AUDIO_EXTS:
                QMessageBox.warning(self, "Unsupported Format", 
                                  f"File format not supported: {Path(seed).suffix}")
                return
            
            storage = Storage.from_path(self.db_path)
            target = storage.get_analysis_by_path(seed)
            if not target:
                QMessageBox.warning(self, "Not found", "Seed not analyzed. Run Analyze first.")
                return
            rows = storage.list_all_analyses()
            cands = [r for r in rows if r.get("path") != target.get("path")]
            ranked = suggest_compatible(target, cands, limit=25)
            self.result_list.clear()
            from src.services.compatibility import transition_score, bpm_difference
            for i, r in enumerate(ranked, 1):
                sc = transition_score(target, r)
                bpm_diff = bpm_difference(target.get('bpm'), r.get('bpm'))
                bpm_diff_str = f"±{bpm_diff:.1f}" if bpm_diff > 0 else "±0.0"
                track_name = format_track_name(r)
                self.result_list.addItem(f"{i:02d}. {track_name} | BPM={r.get('bpm')} ({bpm_diff_str}) | Key={r.get('key')} | Energy={r.get('energy')} | score={sc:.2f}")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def on_export_playlist(self):
        if not self.current_playlist:
            QMessageBox.information(self, "No playlist", "Generate a playlist first")
            return
        out_path, sel = QFileDialog.getSaveFileName(self, "Export Playlist", "playlist.m3u", "Playlists (*.m3u);;CSV Files (*.csv)")
        if not out_path:
            return
        try:
            p = Path(out_path)
            if p.suffix.lower() == ".csv" or sel.startswith("CSV"):
                with p.open("w", encoding="utf-8") as f:
                    f.write("path,bpm,key,energy\n")
                    for r in self.current_playlist:
                        path = r.get("path", "")
                        bpm = r.get("bpm")
                        key = r.get("key") or ""
                        energy = r.get("energy")
                        f.write(f"{path},{bpm if bpm is not None else ''},{key},{energy if energy is not None else ''}\n")
            else:
                with p.open("w", encoding="utf-8") as f:
                    f.write("#EXTM3U\n")
                    for r in self.current_playlist:
                        path = r.get("path", "")
                        f.write(f"{path}\n")
            QMessageBox.information(self, "Exported", f"Playlist exported to {out_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Export failed: {e}")

    def on_generate_playlist(self):
        from src.services.playlist import generate_playlist
        try:
            # UI Configuration validation
            seed = self.seed_edit.text().strip()
            if not seed:
                QMessageBox.warning(self, "No seed", "Select a seed track")
                return
            
            if not Path(seed).exists():
                QMessageBox.critical(self, "File Error", f"Seed file does not exist: {seed}")
                return
            
            # Validate playlist configuration
            playlist_length = self.length_spin.value()
            if playlist_length < 2:
                QMessageBox.warning(self, "Invalid Length", "Playlist must be at least 2 tracks")
                return
            
            bpm_tolerance = self.bpm_tol_spin.value()
            if bpm_tolerance < 1 or bpm_tolerance > 50:
                QMessageBox.warning(self, "Invalid Tolerance", "BPM tolerance must be between 1% and 50%")
                return
            
            storage = Storage.from_path(self.db_path)
            target = storage.get_analysis_by_path(seed)
            if not target:
                QMessageBox.warning(self, "Not found", "Seed not analyzed. Run Analyze first.")
                return
            rows = storage.list_all_analyses()
            cands = [r for r in rows if r.get("path") != target.get("path")]
            length = int(self.length_spin.value())
            curve = self.curve_combo.currentText()
            tol = float(self.bpm_tol_spin.value()) / 100.0
            pl = generate_playlist(target, cands, length=length, curve=curve, bpm_tolerance=tol, prefer_relative=self.pref_rel_cb.isChecked())
            self.current_playlist = pl
            self.result_list.clear()
            self.result_list.addItem(f"Playlist ({len(pl)}) [curve={curve}]:")
            from src.services.compatibility import transition_score, bpm_difference
            prev = target
            for i, r in enumerate(pl, 1):
                sc = transition_score(prev, r, prefer_rel=self.pref_rel_cb.isChecked())
                bpm_diff = bpm_difference(prev.get('bpm'), r.get('bpm'))
                bpm_diff_str = f"±{bpm_diff:.1f}" if bpm_diff > 0 else "±0.0"
                track_name = format_track_name(r)
                self.result_list.addItem(f"{i:02d}. {track_name} | BPM={r.get('bpm')} ({bpm_diff_str}) | Key={r.get('key')} | Energy={r.get('energy')} | score={sc:.2f}")
                prev = r
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def on_visualize(self):
        seed = self.seed_edit.text().strip()
        if not seed:
            QMessageBox.warning(self, "No seed", "Select a seed track")
            return
        try:
            show_visuals(seed)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Cannot visualize: {e}")

    def on_copy_selected(self):
        sel = self.result_table.selectionModel()
        if not sel or not sel.hasSelection():
            return
        rows = sorted(set(i.row() for i in sel.selectedIndexes()))
        out_lines = ["type,path,bpm,key,energy,score"]
        for r in rows:
            vals = []
            for c in range(self.result_table.columnCount()):
                item = self.result_table.item(r, c)
                vals.append((item.text() if item else "").replace(",", " "))
            out_lines.append(",".join(vals))
        QApplication.clipboard().setText("\n".join(out_lines))

    def setup_compact_layout_only(self):
        """Setup simplified compact layout for MacBook Pro 13 inch."""
        main_layout = QVBoxLayout(self.main_widget)
        main_layout.setSpacing(6)
        main_layout.setContentsMargins(8, 8, 8, 8)
        
        # Directory & Controls (Combined)
        dir_controls_group = QGroupBox("Directory & Controls")
        dir_controls_layout = QVBoxLayout(dir_controls_group)
        dir_controls_layout.setSpacing(4)
        
        # Directory row
        dir_row = QHBoxLayout()
        dir_row.addWidget(QLabel("Directory:"))
        dir_row.addWidget(self.dir_edit, 1)
        dir_row.addWidget(self.browse_btn)
        dir_controls_layout.addLayout(dir_row)
        
        # Controls row
        controls_row = QHBoxLayout()
        controls_row.addWidget(self.start_btn)
        controls_row.addWidget(self.stop_btn)
        controls_row.addStretch(1)
        controls_row.addWidget(self.copy_btn)
        controls_row.addWidget(self.export_btn)
        dir_controls_layout.addLayout(controls_row)
        
        main_layout.addWidget(dir_controls_group)
        
        # Progress Section (Compact)
        progress_group = QGroupBox("Analysis Progress")
        progress_layout = QVBoxLayout(progress_group)
        progress_layout.setSpacing(4)
        
        # Files progress
        file_row = QHBoxLayout()
        file_row.addWidget(QLabel("Files:"))
        file_row.addWidget(self.progress, 1)
        progress_layout.addLayout(file_row)
        
        # Current file
        progress_layout.addWidget(self.file_label)
        
        # File and stage progress in columns
        progress_cols = QHBoxLayout()
        
        # File progress
        file_prog_col = QVBoxLayout()
        file_prog_row = QHBoxLayout()
        file_prog_row.addWidget(QLabel("File:"))
        file_prog_row.addWidget(self.file_progress_bar, 1)
        file_prog_col.addLayout(file_prog_row)
        
        # Stage progress
        stage_prog_row = QHBoxLayout()
        stage_prog_row.addWidget(QLabel("Stage:"))
        stage_prog_row.addWidget(self.stage_progress_bar, 1)
        file_prog_col.addLayout(stage_prog_row)
        
        progress_cols.addLayout(file_prog_col, 1)
        
        # Time info column
        time_col = QVBoxLayout()
        time_col.addWidget(self.stage_label)
        time_col.addWidget(self.time_label)
        
        progress_cols.addLayout(time_col)
        progress_layout.addLayout(progress_cols)
        
        main_layout.addWidget(progress_group)
        
        # Two-column bottom
        bottom_layout = QHBoxLayout()
        
        # Left: Playlist tools
        playlist_group = QGroupBox("Playlist Tools")
        playlist_layout = QVBoxLayout(playlist_group)
        playlist_layout.setSpacing(4)
        
        # Seed
        seed_row = QHBoxLayout()
        seed_row.addWidget(QLabel("Seed:"))
        seed_row.addWidget(self.seed_edit, 1)
        seed_row.addWidget(self.seed_browse)
        playlist_layout.addLayout(seed_row)
        
        # Tools
        tools_row = QHBoxLayout()
        tools_row.addWidget(self.suggest_btn)
        tools_row.addWidget(self.playlist_btn)
        tools_row.addWidget(self.visualize_btn)
        playlist_layout.addLayout(tools_row)
        
        # Parameters
        params_row = QHBoxLayout()
        params_row.addWidget(QLabel("Curve:"))
        params_row.addWidget(self.curve_combo)
        params_row.addWidget(QLabel("Len:"))
        params_row.addWidget(self.length_spin)
        params_row.addWidget(QLabel("BPM±:"))
        params_row.addWidget(self.bpm_tol_spin)
        params_row.addWidget(self.pref_rel_cb)
        playlist_layout.addLayout(params_row)
        
        # Export
        export_row = QHBoxLayout()
        export_row.addWidget(self.export_pl_btn)
        export_row.addStretch(1)
        playlist_layout.addLayout(export_row)
        
        bottom_layout.addWidget(playlist_group, 1)
        
        # Right: Results and Log
        results_log_group = QGroupBox("Results & Log")
        results_log_layout = QVBoxLayout(results_log_group)
        results_log_layout.addWidget(self.result_table, 2)  # Analysis results table
        results_log_layout.addWidget(self.result_list, 1)   # Playlist results list  
        results_log_layout.addWidget(self.log_list, 1)      # System log
        
        bottom_layout.addWidget(results_log_group, 1)
        
        main_layout.addLayout(bottom_layout, 1)



def main() -> int:
    import sys

    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
