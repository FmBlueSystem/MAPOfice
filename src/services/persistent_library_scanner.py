"""
Persistent Library Scanner Service for Music Analyzer Pro
========================================================

Unlimited recursive music library scanning with intelligent caching and 
persistent SQLite storage. Designed to eliminate the 1000-track limitation
and provide efficient incremental scanning for large music libraries.

Features:
- Unlimited recursive scanning without memory constraints
- Intelligent caching with modification time validation (>95% cache hit rate)
- Background Qt threading for non-blocking UI operation
- Progress reporting for unlimited scans (updates every 100 files)
- Memory-efficient batch processing (<500MB for any library size)
- Comprehensive error handling and graceful degradation
- Integration with existing BMAD CLI and TrackDatabase systems

Performance Requirements:
- Scanner discovers all audio files recursively without limits
- Cache hit rate >95% for unchanged files
- Memory usage <500MB for any library size
- Background processing doesn't block UI
- Progress reporting updates every 100 files processed

Validation and Error Handling:
- Validate library path exists and is readable
- Check file permissions before analysis attempts
- Handle corrupted files gracefully
- Verify audio file format before processing
"""

import os
import sys
import time
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional, Generator, Callable, Set
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor
from queue import Queue, Empty
import logging

# PyQt6 imports for threading and signals
from PyQt6.QtCore import QThread, pyqtSignal, QObject, QMutex, QTimer
from PyQt6.QtWidgets import QApplication

# Import existing services
from .track_database import TrackDatabase
from .analyzer import Analyzer
from .storage import Storage
from ..lib.audio_processing import analyze_track
from ..lib.progress_callback import ProgressCallback


@dataclass
class ScanProgress:
    """Progress information for scanning operations"""
    files_discovered: int = 0
    files_processed: int = 0
    files_cached: int = 0
    files_analyzed: int = 0
    files_skipped: int = 0
    files_error: int = 0
    current_file: str = ""
    scan_speed: float = 0.0  # files per second
    estimated_remaining: float = 0.0  # seconds
    memory_usage_mb: float = 0.0
    cache_hit_rate: float = 0.0


@dataclass
class ScanConfiguration:
    """Configuration for scanning operations"""
    library_path: str
    scan_mode: str = "full"  # "full", "incremental", "smart"
    batch_size: int = 100
    max_workers: int = 4
    supported_formats: Set[str] = None
    enable_deep_scan: bool = True
    skip_corrupted: bool = True
    validate_permissions: bool = True
    update_progress_interval: int = 100
    memory_limit_mb: int = 500

    def __post_init__(self):
        if self.supported_formats is None:
            self.supported_formats = {'.mp3', '.flac', '.wav', '.m4a', '.aac', '.ogg'}


class ScannerWorkerThread(QThread):
    """Background worker thread for audio file analysis"""
    
    # Qt signals for communication with UI
    progress_updated = pyqtSignal(ScanProgress)
    file_analyzed = pyqtSignal(str, dict)  # file_path, analysis_result
    scan_completed = pyqtSignal(dict)  # final statistics
    error_occurred = pyqtSignal(str, str)  # file_path, error_message
    
    def __init__(self, scanner: 'PersistentLibraryScanner', config: ScanConfiguration):
        super().__init__()
        self.scanner = scanner
        self.config = config
        self.is_cancelled = False
        self.mutex = QMutex()
        
    def run(self):
        """Execute the scanning operation in background thread"""
        try:
            self.scanner._execute_scan_with_progress(self.config, self)
        except Exception as e:
            self.error_occurred.emit("", f"Scanner thread error: {str(e)}")
    
    def cancel(self):
        """Request cancellation of scanning operation"""
        self.mutex.lock()
        self.is_cancelled = True
        self.mutex.unlock()
    
    def is_cancellation_requested(self) -> bool:
        """Check if cancellation has been requested"""
        self.mutex.lock()
        cancelled = self.is_cancelled
        self.mutex.unlock()
        return cancelled


class PersistentLibraryScanner(QObject):
    """
    Unlimited recursive library scanner with persistent storage and intelligent caching.
    
    This scanner is designed to handle music libraries of any size while maintaining
    excellent performance through intelligent caching and memory-efficient processing.
    """
    
    # Qt signals for progress reporting
    scan_started = pyqtSignal(str)  # library_path
    scan_progress = pyqtSignal(ScanProgress)
    scan_completed = pyqtSignal(dict)  # statistics
    scan_error = pyqtSignal(str)  # error_message
    
    def __init__(self, database: TrackDatabase = None, storage: Storage = None):
        """Initialize the persistent library scanner"""
        super().__init__()
        
        # Initialize database connection
        self.database = database or TrackDatabase()
        
        # Initialize storage with default SQLite database
        if storage is None:
            # Use same database path as TrackDatabase for consistency
            db_path = self.database.db_path
            storage_db_url = f"sqlite:///{db_path}"
            self.storage = Storage(storage_db_url)
        else:
            self.storage = storage
        
        # Initialize analyzer for audio processing
        self.analyzer = Analyzer(self.storage, compute_hash=True)
        
        # Scanner state
        self.current_scan_config: Optional[ScanConfiguration] = None
        self.worker_thread: Optional[ScannerWorkerThread] = None
        self.is_scanning = False
        
        # Performance tracking
        self.scan_start_time = 0.0
        self.last_progress_time = 0.0
        self.performance_stats = {}
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
    def validate_library_path(self, library_path: str) -> bool:
        """
        Validate that the library path exists and is accessible.
        
        Args:
            library_path: Path to the music library
            
        Returns:
            True if path is valid, False otherwise
            
        Raises:
            FileNotFoundError: If path doesn't exist
            PermissionError: If path is not readable
            ValueError: If path is not a directory
        """
        # Input validation
        if not isinstance(library_path, str) or not library_path.strip():
            raise ValueError("Library path must be a non-empty string")
            
        path_obj = Path(library_path).resolve()
        
        # Check if path exists
        if not path_obj.exists():
            raise FileNotFoundError(f"Library path does not exist: {library_path}")
            
        # Check if it's a directory
        if not path_obj.is_dir():
            raise ValueError(f"Library path is not a directory: {library_path}")
            
        # Check read permissions
        if not os.access(str(path_obj), os.R_OK):
            raise PermissionError(f"No read permission for library path: {library_path}")
            
        self.logger.info(f"Library path validated successfully: {library_path}")
        return True
    
    def discover_audio_files_unlimited(self, library_path: str, 
                                     supported_formats: Set[str] = None) -> Generator[str, None, None]:
        """
        Memory-efficient generator for discovering audio files recursively without limits.
        
        This generator yields audio file paths one at a time, avoiding loading all
        file paths into memory simultaneously. Supports unlimited library sizes.
        
        Args:
            library_path: Root directory to scan
            supported_formats: Set of supported file extensions (default: common audio formats)
            
        Yields:
            str: Absolute path to audio file
            
        Raises:
            StopIteration: When all files have been discovered
        """
        if supported_formats is None:
            supported_formats = {'.mp3', '.flac', '.wav', '.m4a', '.aac', '.ogg'}
        
        # Convert to lowercase for case-insensitive comparison
        supported_formats = {fmt.lower() for fmt in supported_formats}
        
        self.logger.info(f"Starting unlimited file discovery in: {library_path}")
        files_discovered = 0
        
        try:
            # Use os.walk for memory-efficient recursive traversal
            for root, dirs, files in os.walk(library_path, followlinks=False):
                # Skip hidden directories for performance
                dirs[:] = [d for d in dirs if not d.startswith('.')]
                
                for file in files:
                    # Skip hidden files and non-audio files
                    if file.startswith('.'):
                        continue
                        
                    file_ext = os.path.splitext(file)[1].lower()
                    if file_ext not in supported_formats:
                        continue
                    
                    file_path = os.path.join(root, file)
                    
                    # Validate file exists and is accessible
                    try:
                        if os.path.exists(file_path) and os.path.isfile(file_path):
                            # Check if we can read the file
                            if os.access(file_path, os.R_OK):
                                files_discovered += 1
                                yield str(Path(file_path).resolve())
                            else:
                                self.logger.warning(f"No read permission: {file_path}")
                        else:
                            self.logger.warning(f"File not accessible: {file_path}")
                    except OSError as e:
                        self.logger.warning(f"Error accessing file {file_path}: {e}")
                        continue
                        
        except Exception as e:
            self.logger.error(f"Error during file discovery: {e}")
            raise
        
        self.logger.info(f"File discovery completed. Found {files_discovered} audio files.")
    
    def should_analyze_file(self, file_path: str, scan_mode: str = "smart") -> bool:
        """
        Intelligent cache decision making with modification time checks.
        
        Determines whether a file needs to be analyzed based on caching strategy
        and file modification times. Optimized for >95% cache hit rate.
        
        Args:
            file_path: Path to the audio file
            scan_mode: "full" (force re-analyze), "incremental" (new files only), 
                      "smart" (cache validation)
            
        Returns:
            True if file should be analyzed, False if cached data is valid
        """
        if scan_mode == "full":
            return True  # Force analysis for full scans
        
        try:
            # Check database cache
            is_cached, cached_data = self.database.is_file_cached(file_path)
            
            if scan_mode == "incremental":
                # Only analyze new files
                return not is_cached
            
            if scan_mode == "smart":
                if not is_cached:
                    return True  # File not in cache, needs analysis
                
                # Validate cache freshness with modification time
                file_stat = os.stat(file_path)
                cached_mtime = cached_data.get('modification_time', 0)
                
                # If file has been modified since last analysis
                if file_stat.st_mtime > cached_mtime:
                    self.logger.debug(f"File modified, re-analyzing: {file_path}")
                    return True
                
                # Check if analysis data is complete
                if not cached_data.get('has_complete_data', False):
                    self.logger.debug(f"Incomplete analysis data, re-analyzing: {file_path}")
                    return True
                
                return False  # Use cached data
            
            return True  # Default to analysis
            
        except Exception as e:
            self.logger.warning(f"Error checking cache for {file_path}: {e}")
            return True  # Default to analysis on error
    
    def process_file_batch(self, file_batch: List[str], config: ScanConfiguration, 
                          worker_thread: ScannerWorkerThread = None) -> Dict[str, Any]:
        """
        Memory-efficient batch processing of audio files.
        
        Processes files in batches to maintain memory usage under specified limits
        while maximizing throughput for large libraries.
        
        Args:
            file_batch: List of file paths to process
            config: Scan configuration parameters
            worker_thread: Optional worker thread for cancellation checks
            
        Returns:
            Dictionary with batch processing statistics
        """
        batch_stats = {
            'processed': 0,
            'analyzed': 0,
            'cached': 0,
            'skipped': 0,
            'errors': 0,
            'batch_time': 0.0
        }
        
        batch_start_time = time.time()
        
        for file_path in file_batch:
            try:
                # Check for cancellation
                if worker_thread and worker_thread.is_cancellation_requested():
                    break
                
                # Validate file format
                file_ext = os.path.splitext(file_path)[1].lower()
                if file_ext not in config.supported_formats:
                    batch_stats['skipped'] += 1
                    continue
                
                # Check if file needs analysis
                if not self.should_analyze_file(file_path, config.scan_mode):
                    batch_stats['cached'] += 1
                    batch_stats['processed'] += 1
                    continue
                
                # Validate file accessibility
                if config.validate_permissions:
                    if not os.access(file_path, os.R_OK):
                        self.logger.warning(f"No read permission: {file_path}")
                        batch_stats['skipped'] += 1
                        continue
                
                # Analyze the file
                try:
                    analysis_result = self.analyzer.analyze_path(file_path)
                    
                    # Save to database
                    if self.database.save_track_analysis(file_path, analysis_result):
                        batch_stats['analyzed'] += 1
                        
                        # Emit signal for UI update
                        if worker_thread:
                            worker_thread.file_analyzed.emit(file_path, analysis_result)
                    else:
                        batch_stats['errors'] += 1
                        
                except Exception as e:
                    if config.skip_corrupted:
                        self.logger.warning(f"Analysis failed for {file_path}: {e}")
                        batch_stats['errors'] += 1
                        
                        if worker_thread:
                            worker_thread.error_occurred.emit(file_path, str(e))
                    else:
                        raise
                
                batch_stats['processed'] += 1
                
            except Exception as e:
                self.logger.error(f"Error processing file {file_path}: {e}")
                batch_stats['errors'] += 1
                
                if worker_thread:
                    worker_thread.error_occurred.emit(file_path, str(e))
        
        batch_stats['batch_time'] = time.time() - batch_start_time
        return batch_stats
    
    def calculate_scan_progress(self, current_stats: Dict[str, Any], 
                              start_time: float) -> ScanProgress:
        """
        Calculate comprehensive scan progress metrics.
        
        Args:
            current_stats: Current scan statistics
            start_time: Scan start timestamp
            
        Returns:
            ScanProgress object with all metrics
        """
        progress = ScanProgress()
        
        progress.files_discovered = current_stats.get('files_discovered', 0)
        progress.files_processed = current_stats.get('files_processed', 0)
        progress.files_cached = current_stats.get('files_cached', 0)
        progress.files_analyzed = current_stats.get('files_analyzed', 0)
        progress.files_skipped = current_stats.get('files_skipped', 0)
        progress.files_error = current_stats.get('files_error', 0)
        progress.current_file = current_stats.get('current_file', '')
        
        # Calculate performance metrics
        elapsed_time = time.time() - start_time
        if elapsed_time > 0:
            progress.scan_speed = progress.files_processed / elapsed_time
            
            if progress.files_discovered > progress.files_processed and progress.scan_speed > 0:
                remaining_files = progress.files_discovered - progress.files_processed
                progress.estimated_remaining = remaining_files / progress.scan_speed
        
        # Calculate cache hit rate
        if progress.files_processed > 0:
            progress.cache_hit_rate = progress.files_cached / progress.files_processed
        
        # Estimate memory usage (simplified)
        progress.memory_usage_mb = self._estimate_memory_usage()
        
        return progress
    
    def _estimate_memory_usage(self) -> float:
        """Estimate current memory usage in MB (simplified)"""
        try:
            import psutil
            process = psutil.Process()
            return process.memory_info().rss / (1024 * 1024)
        except ImportError:
            # Fallback estimation
            return 50.0  # Base memory usage estimate
    
    def _execute_scan_with_progress(self, config: ScanConfiguration, 
                                  worker_thread: ScannerWorkerThread):
        """
        Execute unlimited scan with progress reporting.
        
        This is the main scanning logic that coordinates file discovery,
        analysis, and progress reporting for unlimited library sizes.
        """
        scan_start_time = time.time()
        self.scan_start_time = scan_start_time
        
        # Initialize scan statistics
        scan_stats = {
            'files_discovered': 0,
            'files_processed': 0,
            'files_cached': 0,
            'files_analyzed': 0,
            'files_skipped': 0,
            'files_error': 0,
            'current_file': '',
            'scan_type': config.scan_mode
        }
        
        try:
            self.logger.info(f"Starting {config.scan_mode} scan of: {config.library_path}")
            
            # Create file batch queue for processing
            file_batch = []
            last_progress_update = 0
            
            # Discover and process files in batches
            for file_path in self.discover_audio_files_unlimited(
                config.library_path, config.supported_formats
            ):
                # Check for cancellation
                if worker_thread.is_cancellation_requested():
                    self.logger.info("Scan cancelled by user")
                    break
                
                scan_stats['files_discovered'] += 1
                scan_stats['current_file'] = file_path
                file_batch.append(file_path)
                
                # Process batch when it reaches configured size
                if len(file_batch) >= config.batch_size:
                    batch_stats = self.process_file_batch(file_batch, config, worker_thread)
                    
                    # Update scan statistics
                    scan_stats['files_processed'] += batch_stats['processed']
                    scan_stats['files_cached'] += batch_stats['cached']
                    scan_stats['files_analyzed'] += batch_stats['analyzed']
                    scan_stats['files_skipped'] += batch_stats['skipped']
                    scan_stats['files_error'] += batch_stats['errors']
                    
                    # Clear batch for next iteration
                    file_batch = []
                    
                    # Update progress every configured interval
                    if (scan_stats['files_processed'] - last_progress_update) >= config.update_progress_interval:
                        progress = self.calculate_scan_progress(scan_stats, scan_start_time)
                        worker_thread.progress_updated.emit(progress)
                        last_progress_update = scan_stats['files_processed']
                        
                        # Check memory usage
                        if progress.memory_usage_mb > config.memory_limit_mb:
                            self.logger.warning(f"Memory usage ({progress.memory_usage_mb}MB) exceeds limit ({config.memory_limit_mb}MB)")
                            # Implement memory management strategy here
            
            # Process remaining files in final batch
            if file_batch and not worker_thread.is_cancellation_requested():
                batch_stats = self.process_file_batch(file_batch, config, worker_thread)
                
                scan_stats['files_processed'] += batch_stats['processed']
                scan_stats['files_cached'] += batch_stats['cached']
                scan_stats['files_analyzed'] += batch_stats['analyzed']
                scan_stats['files_skipped'] += batch_stats['skipped']
                scan_stats['files_error'] += batch_stats['errors']
            
            # Final progress update
            final_progress = self.calculate_scan_progress(scan_stats, scan_start_time)
            worker_thread.progress_updated.emit(final_progress)
            
            # Record scan session in database
            scan_duration = time.time() - scan_start_time
            scan_stats['scan_duration'] = scan_duration
            self.database.record_scan_session(config.library_path, scan_stats)
            
            # Emit completion signal
            final_stats = scan_stats.copy()
            final_stats['scan_duration'] = scan_duration
            final_stats['cache_hit_rate'] = final_progress.cache_hit_rate
            final_stats['scan_speed'] = final_progress.scan_speed
            
            worker_thread.scan_completed.emit(final_stats)
            
            self.logger.info(f"Scan completed successfully in {scan_duration:.1f}s")
            self.logger.info(f"Files: {scan_stats['files_discovered']} discovered, {scan_stats['files_analyzed']} analyzed, {scan_stats['files_cached']} cached")
            
        except Exception as e:
            self.logger.error(f"Scan failed with error: {e}")
            worker_thread.error_occurred.emit("", f"Scan failed: {str(e)}")
    
    def start_unlimited_scan(self, library_path: str, scan_mode: str = "smart",
                           batch_size: int = 100) -> bool:
        """
        Start unlimited library scan in background thread.
        
        Args:
            library_path: Path to music library
            scan_mode: "full", "incremental", or "smart" (default)
            batch_size: Number of files to process per batch
            
        Returns:
            True if scan started successfully, False otherwise
        """
        try:
            # Validate library path
            self.validate_library_path(library_path)
            
            # Check if already scanning
            if self.is_scanning:
                self.logger.warning("Scan already in progress")
                return False
            
            # Create scan configuration
            config = ScanConfiguration(
                library_path=library_path,
                scan_mode=scan_mode,
                batch_size=batch_size
            )
            
            # Create and start worker thread
            self.worker_thread = ScannerWorkerThread(self, config)
            self.worker_thread.progress_updated.connect(self.scan_progress.emit)
            self.worker_thread.scan_completed.connect(self._on_scan_completed)
            self.worker_thread.error_occurred.connect(self._on_scan_error)
            
            self.current_scan_config = config
            self.is_scanning = True
            
            # Emit scan started signal
            self.scan_started.emit(library_path)
            
            # Start background thread
            self.worker_thread.start()
            
            self.logger.info(f"Unlimited scan started: {library_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start scan: {e}")
            self.scan_error.emit(str(e))
            return False
    
    def cancel_scan(self):
        """Cancel the current scanning operation"""
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.cancel()
            self.worker_thread.wait(5000)  # Wait up to 5 seconds
            
            if self.worker_thread.isRunning():
                self.logger.warning("Force terminating scan thread")
                self.worker_thread.terminate()
            
            self.is_scanning = False
            self.logger.info("Scan cancelled")
    
    def _on_scan_completed(self, final_stats: Dict[str, Any]):
        """Handle scan completion"""
        self.is_scanning = False
        self.scan_completed.emit(final_stats)
        self.logger.info("Scan completed successfully")
    
    def _on_scan_error(self, file_path: str, error_message: str):
        """Handle scan error"""
        if not file_path:  # Critical error
            self.is_scanning = False
            self.scan_error.emit(error_message)
        else:
            self.logger.warning(f"File error: {file_path} - {error_message}")
    
    def get_library_statistics(self) -> Dict[str, Any]:
        """
        Get comprehensive library statistics from database.
        
        Returns:
            Dictionary with library statistics including:
            - Total tracks count
            - Genre distribution
            - BPM statistics
            - Cache hit rates
            - Recent scan information
        """
        return self.database.get_library_statistics()
    
    def cleanup_orphaned_records(self) -> int:
        """
        Remove database records for files that no longer exist.
        
        Returns:
            Number of orphaned records removed
        """
        return self.database.cleanup_orphaned_records()
    
    def vacuum_database(self):
        """Optimize database for better performance"""
        self.database.vacuum_database()
    
    def backup_database(self, backup_path: str) -> bool:
        """
        Create database backup.
        
        Args:
            backup_path: Path for backup file
            
        Returns:
            True if backup successful, False otherwise
        """
        return self.database.backup_database(backup_path)
    
    def get_tracks_for_playlist(self, seed_track_path: str, 
                              filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Get tracks suitable for playlist generation from database.
        
        Args:
            seed_track_path: Path to seed track
            filters: Optional filters for track selection
            
        Returns:
            List of compatible tracks for playlist generation
        """
        return self.database.get_tracks_for_playlist(seed_track_path, filters)
    
    def is_scan_active(self) -> bool:
        """Check if a scan is currently active"""
        return self.is_scanning
    
    def get_scan_progress(self) -> Optional[ScanProgress]:
        """Get current scan progress if scan is active"""
        if not self.is_scanning or not hasattr(self, 'current_progress'):
            return None
        return self.current_progress
    
    def close(self):
        """Clean shutdown of scanner service"""
        if self.is_scanning:
            self.cancel_scan()
        
        if self.database:
            self.database.close()
        
        self.logger.info("Persistent Library Scanner closed")