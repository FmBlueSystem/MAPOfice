"""
Persistent Track Database for Music Analyzer Pro - Enhanced Version
================================================================

SQLite-based persistent storage system with unlimited scanning capabilities:
- Enhanced connection pooling for concurrent access  
- Batch insert operations for high-performance scanning
- Scan session tracking with complete metadata
- Optimized indexes for large datasets (10K+ tracks)
- Database size monitoring and optimization
- Intelligent caching with file modification tracking

Performance Requirements:
- Handle >10K track inserts efficiently (<5 seconds)
- Query performance <100ms for filtered searches  
- Connection pooling prevents database locks
- Scan sessions tracked with complete metadata
"""

import sqlite3
import hashlib
import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Generator
from datetime import datetime
import time
import threading
from contextlib import contextmanager
import queue
import logging
from concurrent.futures import ThreadPoolExecutor
# import psutil  # Not used in current implementation


class DatabaseConnectionPool:
    """Thread-safe connection pool for SQLite database"""
    
    def __init__(self, db_path: str, max_connections: int = 5):
        self.db_path = db_path
        self.max_connections = max_connections
        self.connections = queue.Queue(maxsize=max_connections)
        self.lock = threading.Lock()
        self._initialize_connections()
    
    def _initialize_connections(self):
        """Create initial connection pool with optimized settings"""
        for _ in range(self.max_connections):
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            # Optimize SQLite settings for performance
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA cache_size=10000")
            conn.execute("PRAGMA temp_store=memory")
            conn.execute("PRAGMA mmap_size=268435456")  # 256MB
            self.connections.put(conn)
    
    @contextmanager
    def get_connection(self):
        """Get connection from pool with automatic return"""
        conn = self.connections.get()
        try:
            yield conn
        finally:
            self.connections.put(conn)
    
    def close_all(self):
        """Close all connections in pool"""
        while not self.connections.empty():
            try:
                conn = self.connections.get_nowait()
                conn.close()
            except queue.Empty:
                break


class TrackDatabase:
    """Enhanced persistent SQLite database for track analysis results with unlimited scanning support"""
    
    def __init__(self, db_path: str = None, max_connections: int = 5):
        """Initialize enhanced database with connection pooling"""
        if db_path is None:
            # Default to project directory
            db_path = Path(__file__).parent.parent.parent / "music_analyzer.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize connection pool
        self.pool = DatabaseConnectionPool(str(self.db_path), max_connections)
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Initialize database schema
        self._init_database()
        
        # Performance monitoring
        self._query_stats = {
            'total_queries': 0,
            'total_time': 0.0,
            'batch_operations': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }
    
    def _init_database(self):
        """Initialize enhanced database schema with optimized indexes"""
        with self.pool.get_connection() as conn:
            # Create enhanced schema
            conn.executescript("""
            CREATE TABLE IF NOT EXISTS tracks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT UNIQUE NOT NULL,
                file_hash TEXT NOT NULL,
                file_size INTEGER NOT NULL,
                modification_time REAL NOT NULL,
                analysis_time REAL NOT NULL,
                
                -- Basic metadata
                title TEXT,
                artist TEXT,
                album TEXT,
                genre TEXT,
                duration REAL,
                
                -- Audio analysis results
                bpm REAL,
                energy REAL,
                key_signature TEXT,
                hamms TEXT,  -- JSON string of HAMMS vector
                
                -- Quality metrics
                has_complete_data BOOLEAN,
                analysis_method TEXT,
                confidence_score REAL,
                
                -- ISRC and additional metadata
                isrc TEXT,
                year INTEGER,
                track_number INTEGER,
                
                -- Enhanced fields for unlimited scanning
                scan_session_id INTEGER,
                last_verified REAL,
                file_status TEXT DEFAULT 'active',  -- 'active', 'missing', 'moved'
                
                UNIQUE(file_path)
            );
            
            CREATE TABLE IF NOT EXISTS scan_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_start REAL NOT NULL,
                session_end REAL,
                library_path TEXT NOT NULL,
                scan_type TEXT NOT NULL,  -- 'full', 'incremental', 'smart'
                files_discovered INTEGER DEFAULT 0,
                files_analyzed INTEGER DEFAULT 0,
                files_cached INTEGER DEFAULT 0,
                files_skipped INTEGER DEFAULT 0,
                files_error INTEGER DEFAULT 0,
                scan_duration REAL,
                status TEXT DEFAULT 'running',  -- 'running', 'completed', 'cancelled', 'error'
                error_message TEXT,
                memory_peak_mb REAL,
                database_size_mb REAL
            );
            
            CREATE TABLE IF NOT EXISTS library_scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                library_path TEXT NOT NULL,
                scan_time REAL NOT NULL,
                total_files INTEGER,
                analyzed_files INTEGER,
                skipped_files INTEGER,
                error_files INTEGER,
                scan_duration REAL,
                scan_type TEXT  -- 'full', 'incremental', 'update'
            );
            
            CREATE TABLE IF NOT EXISTS genre_statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                genre TEXT NOT NULL,
                track_count INTEGER,
                avg_bpm REAL,
                avg_energy REAL,
                last_updated REAL,
                UNIQUE(genre)
            );
            
            -- Enhanced indexes for large dataset performance
            CREATE INDEX IF NOT EXISTS idx_file_path ON tracks(file_path);
            CREATE INDEX IF NOT EXISTS idx_file_hash ON tracks(file_hash);
            CREATE INDEX IF NOT EXISTS idx_genre ON tracks(genre);
            CREATE INDEX IF NOT EXISTS idx_bpm ON tracks(bpm) WHERE bpm IS NOT NULL;
            CREATE INDEX IF NOT EXISTS idx_analysis_time ON tracks(analysis_time);
            CREATE INDEX IF NOT EXISTS idx_modification_time ON tracks(modification_time);
            
            -- Composite indexes for common query patterns
            CREATE INDEX IF NOT EXISTS idx_composite_scan ON tracks(modification_time, has_complete_data, file_status);
            CREATE INDEX IF NOT EXISTS idx_playlist_generation ON tracks(bpm, genre, energy) WHERE bpm IS NOT NULL AND has_complete_data = 1;
            CREATE INDEX IF NOT EXISTS idx_file_status ON tracks(file_path, modification_time, file_status);
            CREATE INDEX IF NOT EXISTS idx_scan_session ON tracks(scan_session_id, analysis_time);
            
            -- Partial indexes for performance
            CREATE INDEX IF NOT EXISTS idx_complete_tracks ON tracks(genre, bpm, energy) WHERE has_complete_data = 1;
            CREATE INDEX IF NOT EXISTS idx_active_tracks ON tracks(file_path, modification_time) WHERE file_status = 'active';
            
            -- Scan session indexes
            CREATE INDEX IF NOT EXISTS idx_scan_sessions_time ON scan_sessions(session_start);
            CREATE INDEX IF NOT EXISTS idx_scan_sessions_path ON scan_sessions(library_path, session_start);
            """)
            
            conn.commit()
            
            # Enable query optimization
            conn.execute("ANALYZE")
    
    def get_file_hash(self, file_path: str) -> str:
        """Calculate file hash for deduplication with enhanced error handling"""
        try:
            if not Path(file_path).exists():
                raise FileNotFoundError(f"File not found: {file_path}")
                
            hasher = hashlib.md5()
            with open(file_path, 'rb') as f:
                # Read first and last 64KB for speed
                chunk = f.read(65536)
                if chunk:
                    hasher.update(chunk)
                
                # Try to read from end for larger files
                try:
                    f.seek(-65536, 2)
                    chunk = f.read(65536)
                    if chunk:
                        hasher.update(chunk)
                except (OSError, IOError):
                    # File too small, that's fine
                    pass
                    
            return hasher.hexdigest()
            
        except Exception as e:
            self.logger.warning(f"Error calculating hash for {file_path}: {e}")
            # Fallback to path-based hash
            return hashlib.md5(str(file_path).encode()).hexdigest()
    
    def is_file_cached(self, file_path: str) -> Tuple[bool, Optional[Dict]]:
        """Enhanced cache validation with file status tracking"""
        try:
            # Validate file path first (defensive programming)
            if not file_path or not Path(file_path).exists():
                return False, None
                
            file_stat = os.stat(file_path)
            modification_time = file_stat.st_mtime
            
            with self.pool.get_connection() as conn:
                cursor = conn.execute(
                    "SELECT * FROM tracks WHERE file_path = ? AND file_status = 'active'",
                    (str(file_path),)
                )
                row = cursor.fetchone()
                
                if row:
                    # Check if file has been modified
                    if row['modification_time'] >= modification_time:
                        # File hasn't changed, update last_verified and return cached data
                        conn.execute(
                            "UPDATE tracks SET last_verified = ? WHERE file_path = ?",
                            (time.time(), str(file_path))
                        )
                        conn.commit()
                        self._query_stats['cache_hits'] += 1
                        return True, dict(row)
                    else:
                        # File modified, needs re-analysis
                        self._query_stats['cache_misses'] += 1
                        return False, dict(row)
                
                self._query_stats['cache_misses'] += 1
                return False, None
                
        except Exception as e:
            self.logger.error(f"Error checking cache for {file_path}: {e}")
            self._query_stats['cache_misses'] += 1
            return False, None
    
    def batch_check_cached_files(self, file_paths: List[str]) -> Dict[str, Tuple[bool, Optional[Dict]]]:
        """Efficiently check cache status for multiple files"""
        results = {}
        
        try:
            with self.pool.get_connection() as conn:
                # Get all cached files in one query
                placeholders = ','.join(['?' for _ in file_paths])
                cursor = conn.execute(f"""
                    SELECT * FROM tracks 
                    WHERE file_path IN ({placeholders}) 
                    AND file_status = 'active'
                """, file_paths)
                
                cached_files = {row['file_path']: dict(row) for row in cursor.fetchall()}
                
                # Check modification times for each file
                current_time = time.time()
                cache_hits = []
                
                for file_path in file_paths:
                    try:
                        if not Path(file_path).exists():
                            results[file_path] = (False, None)
                            continue
                            
                        file_stat = os.stat(file_path)
                        modification_time = file_stat.st_mtime
                        
                        if file_path in cached_files:
                            cached_data = cached_files[file_path]
                            if cached_data['modification_time'] >= modification_time:
                                results[file_path] = (True, cached_data)
                                cache_hits.append(file_path)
                                self._query_stats['cache_hits'] += 1
                            else:
                                results[file_path] = (False, cached_data)
                                self._query_stats['cache_misses'] += 1
                        else:
                            results[file_path] = (False, None)
                            self._query_stats['cache_misses'] += 1
                            
                    except Exception as e:
                        self.logger.warning(f"Error checking {file_path}: {e}")
                        results[file_path] = (False, None)
                
                # Update last_verified for cached files in batch
                if cache_hits:
                    placeholders = ','.join(['?' for _ in cache_hits])
                    conn.execute(f"""
                        UPDATE tracks SET last_verified = ? 
                        WHERE file_path IN ({placeholders})
                    """, [current_time] + cache_hits)
                    conn.commit()
                
                return results
                
        except Exception as e:
            self.logger.error(f"Error in batch cache check: {e}")
            # Fallback to individual checks
            for file_path in file_paths:
                results[file_path] = self.is_file_cached(file_path)
            return results
    
    def save_track_analysis(self, file_path: str, analysis_data: Dict[str, Any], scan_session_id: Optional[int] = None) -> bool:
        """Save single track analysis to database with enhanced metadata"""
        try:
            # Validate file path first (defensive programming requirement)
            if not Path(file_path).exists():
                self.logger.error(f"ERROR: File path does not exist: {file_path}")
                return False
                
            file_stat = os.stat(file_path)
            file_hash = self.get_file_hash(file_path)
            
            # Prepare data for insertion
            track_data = {
                'file_path': str(file_path),
                'file_hash': file_hash,
                'file_size': file_stat.st_size,
                'modification_time': file_stat.st_mtime,
                'analysis_time': time.time(),
                
                'title': analysis_data.get('title'),
                'artist': analysis_data.get('artist'),
                'album': analysis_data.get('album'),
                'genre': analysis_data.get('genre'),
                'duration': analysis_data.get('duration'),
                
                'bpm': analysis_data.get('bpm'),
                'energy': analysis_data.get('energy'),
                'key_signature': analysis_data.get('key'),
                'hamms': json.dumps(analysis_data.get('hamms')) if analysis_data.get('hamms') else None,
                
                'has_complete_data': analysis_data.get('has_complete_data', False),
                'analysis_method': analysis_data.get('analysis_method', 'unknown'),
                'confidence_score': analysis_data.get('confidence_score'),
                
                'isrc': analysis_data.get('isrc'),
                'year': analysis_data.get('year'),
                'track_number': analysis_data.get('track_number'),
                
                # Enhanced fields
                'scan_session_id': scan_session_id,
                'last_verified': time.time(),
                'file_status': 'active'
            }
            
            with self.pool.get_connection() as conn:
                # Insert or replace
                conn.execute("""
                    INSERT OR REPLACE INTO tracks (
                        file_path, file_hash, file_size, modification_time, analysis_time,
                        title, artist, album, genre, duration,
                        bpm, energy, key_signature, hamms,
                        has_complete_data, analysis_method, confidence_score,
                        isrc, year, track_number,
                        scan_session_id, last_verified, file_status
                    ) VALUES (
                        :file_path, :file_hash, :file_size, :modification_time, :analysis_time,
                        :title, :artist, :album, :genre, :duration,
                        :bpm, :energy, :key_signature, :hamms,
                        :has_complete_data, :analysis_method, :confidence_score,
                        :isrc, :year, :track_number,
                        :scan_session_id, :last_verified, :file_status
                    )
                """, track_data)
                
                conn.commit()
                
            self._query_stats['total_queries'] += 1
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving track {file_path}: {e}")
            return False
    
    def batch_insert_tracks(self, tracks_data: List[Tuple[str, Dict[str, Any]]], scan_session_id: Optional[int] = None, batch_size: int = 1000) -> Tuple[int, int]:
        """
        Efficiently insert multiple tracks in batches for high-performance scanning
        
        Requirements:
        - Database must handle >10K track inserts efficiently (<5 seconds)
        - Validate all file paths before database operations
        - Ensure database integrity after batch operations
        
        Args:
            tracks_data: List of (file_path, analysis_data) tuples
            scan_session_id: Optional scan session ID to associate with tracks
            batch_size: Number of tracks to process in each batch
            
        Returns:
            Tuple of (successful_inserts, failed_inserts)
        """
        start_time = time.time()
        successful = 0
        failed = 0
        
        self.logger.info(f"Starting batch insert of {len(tracks_data)} tracks")
        
        try:
            # Process in batches for memory efficiency
            for i in range(0, len(tracks_data), batch_size):
                batch = tracks_data[i:i + batch_size]
                batch_records = []
                
                # Prepare batch data with validation
                for file_path, analysis_data in batch:
                    try:
                        # Validate file exists (defensive programming requirement)
                        if not Path(file_path).exists():
                            self.logger.warning(f"Skipping non-existent file: {file_path}")
                            failed += 1
                            continue
                            
                        file_stat = os.stat(file_path)
                        
                        # Check file modification time accurately (requirement)
                        modification_time = file_stat.st_mtime
                        if modification_time <= 0:
                            self.logger.warning(f"Invalid modification time for {file_path}")
                            failed += 1
                            continue
                            
                        file_hash = self.get_file_hash(file_path)
                        current_time = time.time()
                        
                        record = (
                            str(file_path), file_hash, file_stat.st_size, 
                            modification_time, current_time,
                            
                            analysis_data.get('title'), analysis_data.get('artist'),
                            analysis_data.get('album'), analysis_data.get('genre'),
                            analysis_data.get('duration'),
                            
                            analysis_data.get('bpm'), analysis_data.get('energy'),
                            analysis_data.get('key'),
                            json.dumps(analysis_data.get('hamms')) if analysis_data.get('hamms') else None,
                            
                            analysis_data.get('has_complete_data', False),
                            analysis_data.get('analysis_method', 'unknown'),
                            analysis_data.get('confidence_score'),
                            
                            analysis_data.get('isrc'), analysis_data.get('year'),
                            analysis_data.get('track_number'),
                            
                            scan_session_id, current_time, 'active'
                        )
                        batch_records.append(record)
                        
                    except Exception as e:
                        self.logger.warning(f"Error preparing batch record for {file_path}: {e}")
                        failed += 1
                
                # Batch insert with integrity checks
                if batch_records:
                    with self.pool.get_connection() as conn:
                        try:
                            # Begin transaction for integrity
                            conn.execute("BEGIN TRANSACTION")
                            
                            conn.executemany("""
                                INSERT OR REPLACE INTO tracks (
                                    file_path, file_hash, file_size, modification_time, analysis_time,
                                    title, artist, album, genre, duration,
                                    bpm, energy, key_signature, hamms,
                                    has_complete_data, analysis_method, confidence_score,
                                    isrc, year, track_number,
                                    scan_session_id, last_verified, file_status
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, batch_records)
                            
                            conn.commit()  # Commit transaction
                            successful += len(batch_records)
                            
                            self.logger.debug(f"Batch {i//batch_size + 1}: {len(batch_records)} records inserted")
                            
                        except Exception as e:
                            conn.rollback()  # Rollback on error to ensure integrity
                            self.logger.error(f"Batch insert error: {e}")
                            failed += len(batch_records)
            
            # Update performance stats
            duration = time.time() - start_time
            self._query_stats['batch_operations'] += 1
            self._query_stats['total_time'] += duration
            
            # Validate performance requirement: >10K inserts in <5 seconds
            if len(tracks_data) > 10000 and duration > 5.0:
                self.logger.warning(f"Performance requirement violation: {len(tracks_data)} tracks took {duration:.2f}s (>5s limit)")
            
            self.logger.info(f"Batch insert completed: {successful} successful, {failed} failed in {duration:.2f}s")
            return successful, failed
            
        except Exception as e:
            self.logger.error(f"Critical error in batch_insert_tracks: {e}")
            return successful, failed
    
    def start_scan_session(self, library_path: str, scan_type: str = 'full') -> int:
        """Start a new scan session and return session ID"""
        try:
            with self.pool.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO scan_sessions (
                        session_start, library_path, scan_type, status
                    ) VALUES (?, ?, ?, 'running')
                """, (time.time(), str(library_path), scan_type))
                
                session_id = cursor.lastrowid
                conn.commit()
                
                self.logger.info(f"Started scan session {session_id} for {library_path} ({scan_type})")
                return session_id
                
        except Exception as e:
            self.logger.error(f"Error starting scan session: {e}")
            return 0
    
    def update_scan_session(self, session_id: int, **kwargs) -> bool:
        """Update scan session with progress statistics"""
        try:
            if not kwargs:
                return True
                
            # Build dynamic update query
            set_clauses = []
            params = []
            
            valid_fields = {
                'files_discovered', 'files_analyzed', 'files_cached', 
                'files_skipped', 'files_error', 'status', 'error_message',
                'memory_peak_mb', 'database_size_mb'
            }
            
            for key, value in kwargs.items():
                if key in valid_fields:
                    set_clauses.append(f"{key} = ?")
                    params.append(value)
            
            if not set_clauses:
                return True
                
            params.append(session_id)
            
            with self.pool.get_connection() as conn:
                conn.execute(f"""
                    UPDATE scan_sessions SET {', '.join(set_clauses)}
                    WHERE id = ?
                """, params)
                conn.commit()
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating scan session {session_id}: {e}")
            return False
    
    def complete_scan_session(self, session_id: int, final_stats: Dict[str, Any]) -> bool:
        """Mark scan session as completed with final statistics"""
        try:
            end_time = time.time()
            
            with self.pool.get_connection() as conn:
                # Get session start time to calculate duration
                cursor = conn.execute(
                    "SELECT session_start FROM scan_sessions WHERE id = ?",
                    (session_id,)
                )
                row = cursor.fetchone()
                
                if not row:
                    self.logger.warning(f"Scan session {session_id} not found")
                    return False
                
                scan_duration = end_time - row['session_start']
                
                # Update with final stats
                conn.execute("""
                    UPDATE scan_sessions SET 
                        session_end = ?, scan_duration = ?, status = 'completed',
                        files_discovered = ?, files_analyzed = ?, files_cached = ?,
                        files_skipped = ?, files_error = ?, memory_peak_mb = ?,
                        database_size_mb = ?
                    WHERE id = ?
                """, (
                    end_time, scan_duration, 
                    final_stats.get('files_discovered', 0),
                    final_stats.get('files_analyzed', 0),
                    final_stats.get('files_cached', 0),
                    final_stats.get('files_skipped', 0),
                    final_stats.get('files_error', 0),
                    final_stats.get('memory_peak_mb', 0),
                    final_stats.get('database_size_mb', 0),
                    session_id
                ))
                conn.commit()
                
                self.logger.info(f"Completed scan session {session_id} in {scan_duration:.2f}s")
                return True
                
        except Exception as e:
            self.logger.error(f"Error completing scan session {session_id}: {e}")
            return False
    
    def get_all_tracks(self, filters: Dict[str, Any] = None, limit: Optional[int] = None, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get tracks with enhanced filtering and pagination for large datasets
        
        Requirements:
        - Query performance <100ms for filtered searches
        """
        start_time = time.time()
        
        query = "SELECT * FROM tracks WHERE file_status = 'active'"
        params = []
        
        if filters:
            conditions = []
            for key, value in filters.items():
                if key == 'genre' and value:
                    conditions.append("genre = ?")
                    params.append(value)
                elif key == 'has_bpm' and value:
                    conditions.append("bpm IS NOT NULL AND bpm > 0")
                elif key == 'min_bpm' and value:
                    conditions.append("bpm >= ?")
                    params.append(value)
                elif key == 'max_bpm' and value:
                    conditions.append("bpm <= ?")
                    params.append(value)
                elif key == 'has_complete_data' and value:
                    conditions.append("has_complete_data = 1")
                elif key == 'scan_session_id' and value:
                    conditions.append("scan_session_id = ?")
                    params.append(value)
            
            if conditions:
                query += " AND " + " AND ".join(conditions)
        
        query += " ORDER BY analysis_time DESC"
        
        # Add pagination for large datasets
        if limit:
            query += " LIMIT ? OFFSET ?"
            params.extend([limit, offset])
        
        try:
            with self.pool.get_connection() as conn:
                cursor = conn.execute(query, params)
                rows = cursor.fetchall()
                
                tracks = []
                for row in rows:
                    track = dict(row)
                    # Parse HAMMS vector
                    if track['hamms']:
                        try:
                            track['hamms'] = json.loads(track['hamms'])
                        except json.JSONDecodeError:
                            track['hamms'] = None
                    tracks.append(track)
                
                # Update performance stats and validate requirement
                duration = time.time() - start_time
                self._query_stats['total_queries'] += 1
                self._query_stats['total_time'] += duration
                
                # Log warning if query exceeds 100ms requirement
                if duration > 0.1:
                    self.logger.warning(f"Query performance requirement violation: {duration*1000:.1f}ms (>100ms limit)")
                
                return tracks
                
        except Exception as e:
            self.logger.error(f"Error getting tracks: {e}")
            return []
    
    def get_tracks_for_playlist(self, seed_track_path: str, filters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Get tracks suitable for playlist generation with enhanced performance
        
        Requirements:
        - Query performance <100ms for filtered searches
        - Validate all input data completeness
        """
        start_time = time.time()
        
        try:
            with self.pool.get_connection() as conn:
                # Get seed track info with validation
                cursor = conn.execute(
                    "SELECT * FROM tracks WHERE file_path = ? AND file_status = 'active'", 
                    (str(seed_track_path),)
                )
                seed_track = cursor.fetchone()
                
                if not seed_track:
                    self.logger.warning(f"Seed track not found: {seed_track_path}")
                    return []
                
                seed_track = dict(seed_track)
                
                # Validate seed track has required data (defensive programming requirement)
                if not seed_track.get('bpm') or seed_track['bpm'] <= 0:
                    self.logger.error(f"ERROR: Seed track has no BPM calculated: {seed_track_path}")
                    return []
                
                # Find compatible tracks with enhanced query
                query = """
                    SELECT * FROM tracks 
                    WHERE file_path != ? 
                    AND bpm IS NOT NULL 
                    AND bpm > 0
                    AND has_complete_data = 1
                    AND file_status = 'active'
                """
                params = [str(seed_track_path)]
                
                # Add BPM tolerance filter
                if seed_track['bpm'] and filters and 'bpm_tolerance' in filters:
                    tolerance = filters['bpm_tolerance']
                    min_bpm = seed_track['bpm'] * (1 - tolerance)
                    max_bpm = seed_track['bpm'] * (1 + tolerance)
                    query += " AND bpm BETWEEN ? AND ?"
                    params.extend([min_bpm, max_bpm])
                
                # Add genre filter
                if seed_track['genre'] and filters and filters.get('genre_compatibility', True):
                    query += " AND genre = ?"
                    params.append(seed_track['genre'])
                
                # Enhanced sorting for better compatibility
                query += " ORDER BY ABS(bpm - ?) ASC, analysis_time DESC LIMIT ?"
                params.extend([seed_track['bpm'], filters.get('max_results', 100)])
                
                cursor = conn.execute(query, params)
                tracks = [dict(row) for row in cursor.fetchall()]
                
                # Parse HAMMS vectors with error handling
                for track in tracks:
                    if track['hamms']:
                        try:
                            track['hamms'] = json.loads(track['hamms'])
                        except json.JSONDecodeError:
                            track['hamms'] = None
                
                # Update performance stats and validate requirement
                duration = time.time() - start_time
                self._query_stats['total_queries'] += 1
                self._query_stats['total_time'] += duration
                
                # Log performance warning if query exceeds 100ms
                if duration > 0.1:
                    self.logger.warning(f"Slow playlist query: {duration*1000:.1f}ms for {len(tracks)} results (>100ms limit)")
                
                return tracks
                
        except Exception as e:
            self.logger.error(f"Error getting tracks for playlist: {e}")
            return []
    
    def get_database_size_info(self) -> Dict[str, Any]:
        """Get comprehensive database size and performance information"""
        try:
            db_file_size = self.db_path.stat().st_size / (1024 * 1024)  # MB
            
            with self.pool.get_connection() as conn:
                # Database page info
                cursor = conn.execute("PRAGMA page_count")
                page_count = cursor.fetchone()[0]
                
                cursor = conn.execute("PRAGMA page_size")
                page_size = cursor.fetchone()[0]
                
                # Get individual table counts
                cursor = conn.execute("SELECT COUNT(*) FROM tracks WHERE file_status = 'active'")
                active_tracks_count = cursor.fetchone()[0]
                
                cursor = conn.execute("SELECT COUNT(*) FROM tracks")
                total_tracks_count = cursor.fetchone()[0]
                
                cursor = conn.execute("SELECT COUNT(*) FROM scan_sessions")
                sessions_count = cursor.fetchone()[0]
                
                # Index information
                cursor = conn.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='index' AND tbl_name='tracks'
                """)
                indexes = [row[0] for row in cursor.fetchall()]
                
                return {
                    'file_size_mb': round(db_file_size, 2),
                    'page_count': page_count,
                    'page_size_kb': page_size / 1024,
                    'active_tracks_count': active_tracks_count,
                    'total_tracks_count': total_tracks_count,
                    'scan_sessions_count': sessions_count,
                    'indexes': indexes,
                    'estimated_size_per_track_kb': round((db_file_size * 1024) / max(total_tracks_count, 1), 2),
                    'query_stats': dict(self._query_stats)
                }
                
        except Exception as e:
            self.logger.error(f"Error getting database size info: {e}")
            return {'error': str(e)}
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get database performance statistics"""
        stats = dict(self._query_stats)
        
        if stats['total_queries'] > 0:
            stats['average_query_time_ms'] = (stats['total_time'] / stats['total_queries']) * 1000
            stats['cache_hit_rate_percent'] = (stats['cache_hits'] / (stats['cache_hits'] + stats['cache_misses'])) * 100 if (stats['cache_hits'] + stats['cache_misses']) > 0 else 0
        else:
            stats['average_query_time_ms'] = 0
            stats['cache_hit_rate_percent'] = 0
            
        return stats
    
    def optimize_database(self) -> Dict[str, Any]:
        """Perform database optimization operations"""
        results = {
            'optimizations_performed': [],
            'errors': []
        }
        
        try:
            with self.pool.get_connection() as conn:
                # Update statistics for query optimizer
                try:
                    conn.execute("ANALYZE")
                    results['optimizations_performed'].append('Statistics updated')
                except Exception as e:
                    results['errors'].append(f"ANALYZE failed: {e}")
                
                # Vacuum to reclaim space (only if significant fragmentation)
                try:
                    cursor = conn.execute("PRAGMA freelist_count")
                    free_pages = cursor.fetchone()[0]
                    
                    if free_pages > 100:  # Only vacuum if significant free space
                        conn.execute("VACUUM")
                        results['optimizations_performed'].append(f'Vacuumed {free_pages} free pages')
                    else:
                        results['optimizations_performed'].append(f'Vacuum skipped ({free_pages} free pages)')
                        
                except Exception as e:
                    results['errors'].append(f"VACUUM failed: {e}")
                
                # Reindex if needed
                try:
                    conn.execute("REINDEX")
                    results['optimizations_performed'].append('Indexes rebuilt')
                except Exception as e:
                    results['errors'].append(f"REINDEX failed: {e}")
                
        except Exception as e:
            results['errors'].append(f"Database optimization error: {e}")
        
        return results
    
    def cleanup_orphaned_records(self) -> int:
        """Remove records for files that no longer exist with enhanced verification"""
        removed_count = 0
        
        try:
            with self.pool.get_connection() as conn:
                # Get all file paths for verification
                cursor = conn.execute("SELECT file_path, id FROM tracks WHERE file_status = 'active'")
                all_records = cursor.fetchall()
                
                orphaned_ids = []
                
                for file_path, record_id in all_records:
                    if not Path(file_path).exists():
                        orphaned_ids.append(record_id)
                
                if orphaned_ids:
                    # Mark as missing rather than delete (safer)
                    placeholders = ','.join(['?' for _ in orphaned_ids])
                    conn.execute(f"""
                        UPDATE tracks SET file_status = 'missing', last_verified = ?
                        WHERE id IN ({placeholders})
                    """, [time.time()] + orphaned_ids)
                    
                    removed_count = len(orphaned_ids)
                    conn.commit()
                    
                    self.logger.info(f"Marked {removed_count} missing tracks")
                
                return removed_count
                
        except Exception as e:
            self.logger.error(f"Error cleaning orphaned records: {e}")
            return 0
    
    def get_library_statistics(self) -> Dict[str, Any]:
        """Get comprehensive library statistics with enhanced metrics"""
        stats = {}
        
        try:
            with self.pool.get_connection() as conn:
                # Basic counts - only active tracks
                cursor = conn.execute("SELECT COUNT(*) FROM tracks WHERE file_status = 'active'")
                stats['total_tracks'] = cursor.fetchone()[0]
                
                cursor = conn.execute("SELECT COUNT(*) FROM tracks WHERE bpm IS NOT NULL AND bpm > 0 AND file_status = 'active'")
                stats['tracks_with_bpm'] = cursor.fetchone()[0]
                
                cursor = conn.execute("SELECT COUNT(*) FROM tracks WHERE has_complete_data = 1 AND file_status = 'active'")
                stats['complete_tracks'] = cursor.fetchone()[0]
                
                # File status distribution
                cursor = conn.execute("""
                    SELECT file_status, COUNT(*) as count 
                    FROM tracks 
                    GROUP BY file_status
                """)
                stats['file_status_distribution'] = {row[0]: row[1] for row in cursor.fetchall()}
                
                # Genre distribution (only active tracks)
                cursor = conn.execute("""
                    SELECT genre, COUNT(*) as count 
                    FROM tracks 
                    WHERE genre IS NOT NULL AND file_status = 'active'
                    GROUP BY genre 
                    ORDER BY count DESC
                    LIMIT 20
                """)
                stats['genre_distribution'] = {row[0]: row[1] for row in cursor.fetchall()}
                
                # BPM statistics (only active tracks)
                cursor = conn.execute("""
                    SELECT AVG(bpm), MIN(bpm), MAX(bpm), COUNT(*) 
                    FROM tracks 
                    WHERE bpm IS NOT NULL AND bpm > 0 AND file_status = 'active'
                """)
                row = cursor.fetchone()
                if row[0]:
                    stats['bpm_stats'] = {
                        'average': round(row[0], 1),
                        'minimum': round(row[1], 1),
                        'maximum': round(row[2], 1),
                        'count': row[3]
                    }
                
                # Recent scan sessions info
                cursor = conn.execute("""
                    SELECT * FROM scan_sessions 
                    ORDER BY session_start DESC 
                    LIMIT 5
                """)
                recent_sessions = [dict(row) for row in cursor.fetchall()]
                stats['recent_scan_sessions'] = recent_sessions
                
                # Legacy scan info for backwards compatibility
                cursor = conn.execute("""
                    SELECT * FROM library_scans 
                    ORDER BY scan_time DESC 
                    LIMIT 1
                """)
                last_scan = cursor.fetchone()
                if last_scan:
                    stats['last_scan'] = dict(last_scan)
                
                # Cache efficiency metrics
                if recent_sessions:
                    latest_session = recent_sessions[0]
                    total_files = latest_session.get('files_discovered', 0)
                    cached_files = latest_session.get('files_cached', 0)
                    
                    if total_files > 0:
                        stats['cache_efficiency'] = {
                            'hit_rate_percent': round((cached_files / total_files) * 100, 1),
                            'total_files': total_files,
                            'cached_files': cached_files
                        }
                
                # Database size info
                stats['database_info'] = self.get_database_size_info()
                
                # Performance stats
                stats['performance'] = self.get_performance_stats()
                
        except Exception as e:
            self.logger.error(f"Error getting library statistics: {e}")
            stats['error'] = str(e)
        
        return stats
    
    def record_scan_session(self, library_path: str, scan_stats: Dict[str, Any]):
        """Legacy method - record completed scan session statistics"""
        try:
            with self.pool.get_connection() as conn:
                conn.execute("""
                    INSERT INTO library_scans (
                        library_path, scan_time, total_files, analyzed_files,
                        skipped_files, error_files, scan_duration, scan_type
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    str(library_path),
                    time.time(),
                    scan_stats.get('total_files', 0),
                    scan_stats.get('analyzed_files', 0),
                    scan_stats.get('skipped_files', 0),
                    scan_stats.get('error_files', 0),
                    scan_stats.get('scan_duration', 0),
                    scan_stats.get('scan_type', 'full')
                ))
                conn.commit()
        except Exception as e:
            self.logger.error(f"Error recording scan session: {e}")
    
    def vacuum_database(self):
        """Legacy method - optimize database size and performance"""
        try:
            with self.pool.get_connection() as conn:
                conn.execute("VACUUM")
                conn.commit()
        except Exception as e:
            self.logger.error(f"Error vacuuming database: {e}")
    
    def backup_database(self, backup_path: str) -> bool:
        """Create database backup with connection pool support"""
        try:
            backup_conn = sqlite3.connect(backup_path)
            
            with self.pool.get_connection() as conn:
                conn.backup(backup_conn)
            
            backup_conn.close()
            self.logger.info(f"Database backup created: {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Backup failed: {e}")
            return False
    
    def close(self):
        """Close database connection pool"""
        if hasattr(self, 'pool'):
            self.pool.close_all()
    
    def __del__(self):
        """Cleanup on destruction"""
        self.close()