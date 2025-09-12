# MAP4 Feature Specifications - Detailed Requirements

## 1. Professional Export System

### 1.1 PDF Report Generation
**Priority:** CRITICAL
**Complexity:** MEDIUM

#### Functional Requirements
```yaml
PDF_Export:
  formats:
    - Single Track Report (1-2 pages)
    - Playlist Analysis Report (5-10 pages)
    - Library Overview Report (10-20 pages)
    - Comparative Analysis Report (custom length)
  
  components:
    header:
      - Logo/Branding customizable
      - Report title and date
      - User/Organization info
    
    track_analysis:
      - HAMMS radar chart visualization
      - BPM, Key, Energy graphs
      - AI analysis summary
      - Compatibility scores
      - Waveform visualization
    
    statistics:
      - Distribution charts
      - Trend analysis
      - Aggregate metrics
    
  customization:
    - Template selection
    - Color schemes
    - Logo upload
    - Section enable/disable
    - Custom fields
```

#### Technical Implementation
```python
class PDFReportGenerator:
    """Generate professional PDF reports from analysis data."""
    
    def __init__(self, template: str = "default"):
        self.template = self.load_template(template)
        self.renderer = PDFRenderer()  # Using ReportLab or WeasyPrint
        
    def generate_track_report(self, track_data: Dict) -> bytes:
        """Generate single track analysis report."""
        sections = [
            self.render_header(track_data),
            self.render_hamms_visualization(track_data['hamms_vector']),
            self.render_audio_features(track_data),
            self.render_ai_analysis(track_data.get('ai_analysis')),
            self.render_compatibility_suggestions(track_data)
        ]
        return self.renderer.compile(sections)
    
    def generate_batch_report(self, tracks: List[Dict], options: Dict) -> bytes:
        """Generate report for multiple tracks."""
        # Implementation details...
```

### 1.2 Excel/CSV Export
**Priority:** CRITICAL
**Complexity:** LOW

#### Data Structure
```python
EXPORT_COLUMNS = {
    'basic': [
        'file_path', 'title', 'artist', 'album', 'duration',
        'bpm', 'key', 'energy', 'genre', 'year'
    ],
    'hamms': [
        'hamms_dim_1', 'hamms_dim_2', ..., 'hamms_dim_12',
        'hamms_confidence', 'compatibility_score'
    ],
    'ai_analysis': [
        'ai_genre', 'ai_subgenre', 'ai_mood', 'ai_era',
        'ai_tags', 'ai_confidence', 'ai_provider'
    ],
    'technical': [
        'sample_rate', 'bit_rate', 'file_size', 'format',
        'analysis_date', 'analysis_version'
    ]
}
```

### 1.3 JSON Export
**Priority:** HIGH
**Complexity:** LOW

#### Schema Definition
```json
{
  "version": "2.0.0",
  "export_date": "2024-12-01T10:00:00Z",
  "total_tracks": 1000,
  "analysis_config": {
    "hamms_version": "3.0",
    "ai_providers": ["openai", "anthropic"],
    "quality_gates": true
  },
  "tracks": [
    {
      "id": "uuid",
      "metadata": {},
      "analysis": {
        "hamms": {},
        "ai": {},
        "compatibility": {}
      }
    }
  ],
  "statistics": {
    "by_genre": {},
    "by_bpm": {},
    "by_key": {}
  }
}
```

## 2. Scalable Batch Processing

### 2.1 Multi-threaded Analysis Engine
**Priority:** CRITICAL
**Complexity:** HIGH

#### Architecture
```python
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
from queue import PriorityQueue
import multiprocessing as mp

class BatchAnalysisEngine:
    """Scalable batch processing with parallel execution."""
    
    def __init__(self, max_workers: int = None):
        self.max_workers = max_workers or mp.cpu_count()
        self.analysis_queue = PriorityQueue()
        self.results_cache = {}
        
    def analyze_batch(self, 
                      file_paths: List[str], 
                      priority: int = 5,
                      use_ai: bool = True) -> Generator:
        """Process batch with parallel workers."""
        
        # Add to priority queue
        for path in file_paths:
            self.analysis_queue.put((priority, path))
        
        # Process with thread pool for I/O bound tasks
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            while not self.analysis_queue.empty():
                _, path = self.analysis_queue.get()
                
                # Check cache first
                if path in self.results_cache:
                    yield self.results_cache[path]
                    continue
                
                # Submit for analysis
                future = executor.submit(self._analyze_single, path, use_ai)
                futures.append((path, future))
            
            # Yield results as they complete
            for path, future in futures:
                result = future.result()
                self.results_cache[path] = result
                yield result
```

### 2.2 Persistent Queue System
**Priority:** CRITICAL
**Complexity:** MEDIUM

#### Queue Management
```python
import pickle
from pathlib import Path

class PersistentQueue:
    """Queue that survives application restarts."""
    
    def __init__(self, queue_file: str = "analysis_queue.pkl"):
        self.queue_file = Path(queue_file)
        self.items = self._load_queue()
        
    def _load_queue(self) -> List:
        """Load queue from disk if exists."""
        if self.queue_file.exists():
            with open(self.queue_file, 'rb') as f:
                return pickle.load(f)
        return []
    
    def save(self):
        """Persist queue to disk."""
        with open(self.queue_file, 'wb') as f:
            pickle.dump(self.items, f)
    
    def add_batch(self, items: List, priority: int = 5):
        """Add items with priority."""
        for item in items:
            self.items.append({
                'item': item,
                'priority': priority,
                'status': 'pending',
                'added_at': datetime.now()
            })
        self.save()
```

## 3. Advanced Database & Search

### 3.1 Full-text Search Implementation
**Priority:** CRITICAL
**Complexity:** MEDIUM

#### Database Schema Enhancement
```sql
-- Add full-text search indexes
CREATE INDEX idx_tracks_fulltext ON tracks 
USING gin(to_tsvector('english', 
  title || ' ' || artist || ' ' || album || ' ' || genre));

-- Add search function
CREATE FUNCTION search_tracks(query TEXT)
RETURNS TABLE(
  id INTEGER,
  title TEXT,
  artist TEXT,
  relevance FLOAT
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    t.id,
    t.title,
    t.artist,
    ts_rank(to_tsvector('english', t.title || ' ' || t.artist), 
            plainto_tsquery('english', query)) as relevance
  FROM tracks t
  WHERE to_tsvector('english', t.title || ' ' || t.artist || ' ' || t.album) 
        @@ plainto_tsquery('english', query)
  ORDER BY relevance DESC;
END;
$$ LANGUAGE plpgsql;
```

### 3.2 Advanced Filtering System
**Priority:** HIGH
**Complexity:** MEDIUM

#### Filter Configuration
```python
class AdvancedFilter:
    """Multi-parameter filtering with complex conditions."""
    
    OPERATORS = {
        'eq': '=',
        'ne': '!=',
        'gt': '>',
        'gte': '>=',
        'lt': '<',
        'lte': '<=',
        'in': 'IN',
        'between': 'BETWEEN',
        'like': 'LIKE',
        'regex': '~'
    }
    
    def build_query(self, filters: List[Dict]) -> str:
        """Build SQL query from filter conditions."""
        conditions = []
        
        for f in filters:
            field = f['field']
            operator = self.OPERATORS[f['operator']]
            value = f['value']
            
            if f['operator'] == 'between':
                condition = f"{field} BETWEEN {value[0]} AND {value[1]}"
            elif f['operator'] == 'in':
                values = ','.join([f"'{v}'" for v in value])
                condition = f"{field} IN ({values})"
            else:
                condition = f"{field} {operator} '{value}'"
            
            conditions.append(condition)
        
        return ' AND '.join(conditions)
```

## 4. Comparative Analysis Suite

### 4.1 Track Comparison Engine
**Priority:** HIGH
**Complexity:** MEDIUM

#### Comparison Metrics
```python
class TrackComparator:
    """Compare multiple tracks across dimensions."""
    
    def compare_tracks(self, tracks: List[Dict]) -> Dict:
        """Generate comprehensive comparison."""
        
        comparison = {
            'tracks': [self._extract_features(t) for t in tracks],
            'hamms_similarity': self._calculate_hamms_similarity(tracks),
            'key_compatibility': self._analyze_key_compatibility(tracks),
            'bpm_compatibility': self._analyze_bpm_compatibility(tracks),
            'energy_flow': self._analyze_energy_flow(tracks),
            'recommendations': self._generate_recommendations(tracks)
        }
        
        return comparison
    
    def _calculate_hamms_similarity(self, tracks: List[Dict]) -> np.ndarray:
        """Calculate pairwise HAMMS similarity matrix."""
        n = len(tracks)
        similarity_matrix = np.zeros((n, n))
        
        for i in range(n):
            for j in range(i+1, n):
                v1 = np.array(tracks[i]['hamms_vector'])
                v2 = np.array(tracks[j]['hamms_vector'])
                
                # Weighted cosine similarity
                similarity = self._weighted_cosine_similarity(v1, v2)
                similarity_matrix[i][j] = similarity
                similarity_matrix[j][i] = similarity
        
        return similarity_matrix
```

### 4.2 Compatibility Matrix
**Priority:** HIGH
**Complexity:** LOW

#### Matrix Visualization
```python
class CompatibilityMatrix:
    """Visual matrix for track compatibility."""
    
    def generate_matrix(self, tracks: List[Dict]) -> Dict:
        """Create compatibility matrix with color coding."""
        
        matrix = {
            'size': len(tracks),
            'tracks': [t['title'] for t in tracks],
            'compatibility': [],
            'color_scale': {
                'excellent': '#00ff00',  # Green
                'good': '#90ee90',       # Light green
                'moderate': '#ffff00',   # Yellow
                'poor': '#ff0000'        # Red
            }
        }
        
        for i, track1 in enumerate(tracks):
            row = []
            for j, track2 in enumerate(tracks):
                if i == j:
                    score = 1.0  # Perfect match with self
                else:
                    score = self._calculate_compatibility(track1, track2)
                
                row.append({
                    'score': score,
                    'color': self._score_to_color(score),
                    'details': self._compatibility_details(track1, track2)
                })
            
            matrix['compatibility'].append(row)
        
        return matrix
```

## 5. Duplicate & Similar Detection

### 5.1 Audio Fingerprinting
**Priority:** HIGH
**Complexity:** HIGH

#### Fingerprint Generation
```python
import chromaprint
import hashlib

class AudioFingerprinter:
    """Generate and compare audio fingerprints."""
    
    def generate_fingerprint(self, audio_path: str) -> Dict:
        """Generate multiple fingerprint types."""
        
        # Load audio
        audio, sr = librosa.load(audio_path, sr=None)
        
        # Chromaprint fingerprint
        chromaprint_fp = chromaprint.calculate_fingerprint(audio, sr)
        
        # Spectral hash
        spectral_hash = self._generate_spectral_hash(audio, sr)
        
        # MFCC fingerprint
        mfcc_fp = self._generate_mfcc_fingerprint(audio, sr)
        
        return {
            'chromaprint': chromaprint_fp,
            'spectral_hash': spectral_hash,
            'mfcc': mfcc_fp,
            'duration': len(audio) / sr,
            'sample_rate': sr
        }
    
    def find_duplicates(self, 
                       library: List[Dict], 
                       threshold: float = 0.95) -> List[List[Dict]]:
        """Find duplicate tracks in library."""
        
        duplicates = []
        processed = set()
        
        for i, track1 in enumerate(library):
            if track1['id'] in processed:
                continue
            
            duplicate_group = [track1]
            
            for j, track2 in enumerate(library[i+1:], i+1):
                similarity = self._calculate_similarity(
                    track1['fingerprint'], 
                    track2['fingerprint']
                )
                
                if similarity >= threshold:
                    duplicate_group.append(track2)
                    processed.add(track2['id'])
            
            if len(duplicate_group) > 1:
                duplicates.append(duplicate_group)
            
            processed.add(track1['id'])
        
        return duplicates
```

## 6. Watch Folders Integration

### 6.1 Folder Monitoring System
**Priority:** MEDIUM
**Complexity:** MEDIUM

#### File System Watcher
```python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import asyncio

class MusicFolderWatcher(FileSystemEventHandler):
    """Monitor folders for new music files."""
    
    SUPPORTED_EXTENSIONS = {'.mp3', '.wav', '.flac', '.m4a', '.ogg', '.aiff'}
    
    def __init__(self, analyzer, auto_analyze: bool = True):
        self.analyzer = analyzer
        self.auto_analyze = auto_analyze
        self.queue = asyncio.Queue()
        
    def on_created(self, event):
        """Handle new file creation."""
        if not event.is_directory:
            file_path = Path(event.src_path)
            if file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                self.queue.put_nowait({
                    'action': 'analyze',
                    'path': str(file_path),
                    'timestamp': datetime.now()
                })
                
                if self.auto_analyze:
                    asyncio.create_task(self._analyze_file(file_path))
    
    def on_modified(self, event):
        """Handle file modification."""
        if not event.is_directory:
            file_path = Path(event.src_path)
            if file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                # Mark for re-analysis
                self.queue.put_nowait({
                    'action': 're-analyze',
                    'path': str(file_path),
                    'timestamp': datetime.now()
                })
    
    async def _analyze_file(self, file_path: Path):
        """Analyze file asynchronously."""
        try:
            result = await self.analyzer.analyze_async(str(file_path))
            logger.info(f"Auto-analyzed: {file_path.name}")
            return result
        except Exception as e:
            logger.error(f"Failed to analyze {file_path}: {e}")
```

## 7. Library Statistics Dashboard

### 7.1 Analytics Engine
**Priority:** MEDIUM
**Complexity:** LOW

#### Statistics Calculator
```python
class LibraryAnalytics:
    """Calculate comprehensive library statistics."""
    
    def calculate_statistics(self, library: List[Dict]) -> Dict:
        """Generate library statistics."""
        
        stats = {
            'total_tracks': len(library),
            'total_duration': sum(t.get('duration', 0) for t in library),
            'total_size_gb': sum(t.get('file_size', 0) for t in library) / (1024**3),
            
            'by_genre': self._group_by_field(library, 'genre'),
            'by_year': self._group_by_field(library, 'year'),
            'by_key': self._group_by_field(library, 'key'),
            'by_bpm_range': self._group_by_bpm_ranges(library),
            
            'averages': {
                'bpm': np.mean([t['bpm'] for t in library if t.get('bpm')]),
                'energy': np.mean([t['energy'] for t in library if t.get('energy')]),
                'duration': np.mean([t['duration'] for t in library if t.get('duration')])
            },
            
            'distributions': {
                'bpm': self._calculate_distribution(library, 'bpm', bins=20),
                'energy': self._calculate_distribution(library, 'energy', bins=10),
                'years': self._calculate_distribution(library, 'year', bins=10)
            },
            
            'quality_metrics': {
                'analyzed_percentage': len([t for t in library if t.get('hamms_vector')]) / len(library) * 100,
                'ai_enriched_percentage': len([t for t in library if t.get('ai_analysis')]) / len(library) * 100,
                'metadata_completeness': self._calculate_metadata_completeness(library)
            }
        }
        
        return stats
```

---

**Document Version:** 1.0.0
**Last Updated:** 2024-12
**Next Review:** Q1 2025
**Owner:** Engineering Team