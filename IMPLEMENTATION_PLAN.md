# MAP4 Implementation Plan - BMAD Methodology

## Phase 1: BUILD - Foundation Components

### Sprint 1-2: Professional Export System
**Duration:** 2 weeks
**Team:** 1 Backend + 0.5 Frontend

#### Week 1: Core Export Infrastructure
```python
# Day 1-2: Base export framework
class ExportManager:
    """Central export coordination."""
    
    def __init__(self):
        self.exporters = {
            'pdf': PDFExporter(),
            'excel': ExcelExporter(),
            'csv': CSVExporter(),
            'json': JSONExporter()
        }
        self.templates = TemplateManager()
        self.queue = ExportQueue()
    
    async def export(self, data: Dict, format: str, options: Dict) -> bytes:
        """Execute export with specified format."""
        exporter = self.exporters.get(format)
        if not exporter:
            raise ValueError(f"Unsupported format: {format}")
        
        # Apply template if specified
        if options.get('template'):
            data = self.templates.apply(data, options['template'])
        
        # Execute export
        return await exporter.export(data, options)
```

#### Week 2: PDF Generation & Templates
```python
# Day 3-4: PDF report generator
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart

class PDFExporter:
    """Professional PDF report generation."""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self.custom_styles = self._create_custom_styles()
    
    def export(self, data: Dict, options: Dict) -> bytes:
        """Generate PDF report."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        
        # Build document elements
        elements = []
        
        # Add header
        elements.extend(self._create_header(data, options))
        
        # Add HAMMS visualization
        if data.get('hamms_vector'):
            elements.append(self._create_hamms_chart(data['hamms_vector']))
        
        # Add track details table
        elements.append(self._create_details_table(data))
        
        # Add AI analysis section
        if data.get('ai_analysis'):
            elements.extend(self._create_ai_section(data['ai_analysis']))
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer.read()
    
    def _create_hamms_chart(self, hamms_vector: List[float]) -> Drawing:
        """Create HAMMS radar chart."""
        # Implementation using reportlab graphics
        pass
```

#### Deliverables Week 1:
- [ ] Export framework architecture
- [ ] Base exporter classes
- [ ] Template system design
- [ ] Unit tests for exporters

#### Deliverables Week 2:
- [ ] PDF generation complete
- [ ] Excel/CSV exporters
- [ ] JSON schema implementation
- [ ] Integration tests
- [ ] UI export dialog

### Sprint 3-4: Scalable Batch Processing
**Duration:** 2 weeks
**Team:** 2 Backend

#### Week 3: Multi-threading Architecture
```python
# Day 1-3: Parallel processing engine
import concurrent.futures
import multiprocessing as mp
from typing import Generator, List, Dict, Optional
import queue

class BatchProcessor:
    """High-performance batch analysis engine."""
    
    def __init__(self, max_workers: Optional[int] = None):
        self.max_workers = max_workers or mp.cpu_count()
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers)
        self.process_pool = concurrent.futures.ProcessPoolExecutor(max_workers=self.max_workers//2)
        self.active_tasks = {}
        self.completed_tasks = {}
        
    def process_batch(self, 
                     items: List[str], 
                     processor_func: callable,
                     chunk_size: int = 100) -> Generator[Dict, None, None]:
        """Process items in parallel with chunking."""
        
        # Split into chunks for better memory management
        chunks = [items[i:i+chunk_size] for i in range(0, len(items), chunk_size)]
        
        # Submit chunks to executor
        futures = []
        for chunk_id, chunk in enumerate(chunks):
            future = self.executor.submit(self._process_chunk, chunk, processor_func)
            futures.append((chunk_id, future))
            self.active_tasks[chunk_id] = {
                'status': 'processing',
                'size': len(chunk),
                'started': datetime.now()
            }
        
        # Yield results as they complete
        for chunk_id, future in futures:
            try:
                results = future.result(timeout=300)  # 5 min timeout
                self.active_tasks[chunk_id]['status'] = 'completed'
                self.completed_tasks[chunk_id] = results
                
                for result in results:
                    yield result
                    
            except Exception as e:
                self.active_tasks[chunk_id]['status'] = 'failed'
                self.active_tasks[chunk_id]['error'] = str(e)
                logger.error(f"Chunk {chunk_id} failed: {e}")
    
    def _process_chunk(self, chunk: List[str], processor_func: callable) -> List[Dict]:
        """Process a chunk of items."""
        results = []
        for item in chunk:
            try:
                result = processor_func(item)
                results.append(result)
            except Exception as e:
                results.append({'error': str(e), 'item': item})
        return results
```

#### Week 4: Queue System & Persistence
```python
# Day 4-5: Persistent queue implementation
import sqlite3
import json
from enum import Enum
from dataclasses import dataclass, asdict

class TaskStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class AnalysisTask:
    id: str
    file_path: str
    priority: int
    status: TaskStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    result: Optional[Dict] = None
    error: Optional[str] = None

class PersistentTaskQueue:
    """SQLite-backed persistent task queue."""
    
    def __init__(self, db_path: str = "task_queue.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    file_path TEXT NOT NULL,
                    priority INTEGER DEFAULT 5,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    result TEXT,
                    error TEXT
                )
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_status_priority 
                ON tasks(status, priority DESC)
            """)
    
    def add_tasks(self, file_paths: List[str], priority: int = 5) -> List[str]:
        """Add multiple tasks to queue."""
        task_ids = []
        with sqlite3.connect(self.db_path) as conn:
            for path in file_paths:
                task_id = str(uuid.uuid4())
                conn.execute("""
                    INSERT INTO tasks (id, file_path, priority, status)
                    VALUES (?, ?, ?, 'pending')
                """, (task_id, path, priority))
                task_ids.append(task_id)
        return task_ids
    
    def get_next_task(self) -> Optional[AnalysisTask]:
        """Get highest priority pending task."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM tasks 
                WHERE status = 'pending'
                ORDER BY priority DESC, created_at ASC
                LIMIT 1
            """)
            row = cursor.fetchone()
            
            if row:
                # Mark as processing
                conn.execute("""
                    UPDATE tasks 
                    SET status = 'processing', started_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (row['id'],))
                
                return AnalysisTask(
                    id=row['id'],
                    file_path=row['file_path'],
                    priority=row['priority'],
                    status=TaskStatus.PROCESSING,
                    created_at=datetime.fromisoformat(row['created_at']),
                    started_at=datetime.now()
                )
        return None
```

## Phase 2: MEASURE - Performance Metrics

### Sprint 5-6: Advanced Database & Search
**Duration:** 2 weeks
**Team:** 1 Backend + 1 QA

#### Week 5: Database Optimization
```python
# Day 1-3: Enhanced database schema
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class Track(Base):
    """Enhanced track model with full-text search."""
    __tablename__ = 'tracks'
    
    id = Column(Integer, primary_key=True)
    file_path = Column(String, unique=True, nullable=False)
    file_hash = Column(String, index=True)  # For duplicate detection
    
    # Metadata
    title = Column(String, index=True)
    artist = Column(String, index=True)
    album = Column(String, index=True)
    genre = Column(String, index=True)
    year = Column(Integer, index=True)
    
    # Audio features
    duration = Column(Float)
    bpm = Column(Float, index=True)
    key = Column(String, index=True)
    energy = Column(Float, index=True)
    
    # HAMMS v3.0
    hamms_vector = Column(JSON)
    hamms_confidence = Column(Float)
    
    # AI Analysis
    ai_analysis = Column(JSON)
    ai_provider = Column(String)
    ai_timestamp = Column(DateTime)
    
    # Full-text search
    search_vector = Column(TSVECTOR)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    analyzed_at = Column(DateTime)
    
    __table_args__ = (
        Index('idx_search_vector', 'search_vector', postgresql_using='gin'),
        Index('idx_bpm_key', 'bpm', 'key'),
        Index('idx_genre_year', 'genre', 'year'),
    )

class SearchEngine:
    """Advanced search with caching."""
    
    def __init__(self, session):
        self.session = session
        self.cache = {}
    
    def search(self, query: str, filters: Dict = None) -> List[Track]:
        """Full-text search with filters."""
        
        # Build base query
        base_query = self.session.query(Track)
        
        # Apply full-text search
        if query:
            base_query = base_query.filter(
                Track.search_vector.match(query)
            )
        
        # Apply filters
        if filters:
            for field, condition in filters.items():
                if condition['operator'] == 'eq':
                    base_query = base_query.filter(
                        getattr(Track, field) == condition['value']
                    )
                elif condition['operator'] == 'range':
                    base_query = base_query.filter(
                        getattr(Track, field).between(
                            condition['min'], 
                            condition['max']
                        )
                    )
                # Add more operators as needed
        
        # Execute and cache
        cache_key = f"{query}:{json.dumps(filters, sort_keys=True)}"
        if cache_key not in self.cache:
            self.cache[cache_key] = base_query.all()
        
        return self.cache[cache_key]
```

#### Week 6: Caching System
```python
# Day 4-5: Smart caching implementation
import hashlib
import pickle
from typing import Optional, Any
import redis

class SmartCache:
    """Multi-level caching system."""
    
    def __init__(self, redis_url: str = None):
        self.memory_cache = {}  # L1: In-memory
        self.disk_cache_path = Path("cache")  # L2: Disk
        self.disk_cache_path.mkdir(exist_ok=True)
        
        # L3: Redis (optional)
        self.redis_client = None
        if redis_url:
            self.redis_client = redis.from_url(redis_url)
    
    def _generate_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments."""
        key_data = f"{args}:{kwargs}"
        return hashlib.sha256(key_data.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get from cache (check all levels)."""
        
        # L1: Memory
        if key in self.memory_cache:
            return self.memory_cache[key]
        
        # L2: Disk
        disk_file = self.disk_cache_path / f"{key}.pkl"
        if disk_file.exists():
            with open(disk_file, 'rb') as f:
                value = pickle.load(f)
                self.memory_cache[key] = value  # Promote to L1
                return value
        
        # L3: Redis
        if self.redis_client:
            value = self.redis_client.get(key)
            if value:
                value = pickle.loads(value)
                self.memory_cache[key] = value  # Promote to L1
                return value
        
        return None
    
    def set(self, key: str, value: Any, ttl: int = 3600):
        """Set in all cache levels."""
        
        # L1: Memory
        self.memory_cache[key] = value
        
        # L2: Disk
        disk_file = self.disk_cache_path / f"{key}.pkl"
        with open(disk_file, 'wb') as f:
            pickle.dump(value, f)
        
        # L3: Redis
        if self.redis_client:
            self.redis_client.setex(key, ttl, pickle.dumps(value))
    
    def invalidate(self, pattern: str = None):
        """Invalidate cache entries."""
        if pattern:
            # Pattern-based invalidation
            keys_to_remove = [k for k in self.memory_cache.keys() if pattern in k]
            for key in keys_to_remove:
                del self.memory_cache[key]
                
                # Remove from disk
                disk_file = self.disk_cache_path / f"{key}.pkl"
                if disk_file.exists():
                    disk_file.unlink()
                
                # Remove from Redis
                if self.redis_client:
                    self.redis_client.delete(key)
        else:
            # Clear all
            self.memory_cache.clear()
            for f in self.disk_cache_path.glob("*.pkl"):
                f.unlink()
            if self.redis_client:
                self.redis_client.flushdb()
```

## Phase 3: ANALYZE - Quality & Optimization

### Sprint 7-8: Comparative Analysis Suite
**Duration:** 2 weeks
**Team:** 1 Backend + 0.5 Frontend

#### Week 7: Comparison Engine
```python
# Day 1-3: Track comparison implementation
import numpy as np
from scipy.spatial.distance import cosine, euclidean
from typing import List, Dict, Tuple

class ComparisonEngine:
    """Advanced track comparison and compatibility analysis."""
    
    def __init__(self):
        self.weights = HAMMSDimensions()
        self.camelot_wheel = CamelotWheel()
    
    def compare_tracks(self, tracks: List[Dict]) -> Dict:
        """Comprehensive multi-track comparison."""
        
        n_tracks = len(tracks)
        
        # Initialize results structure
        comparison = {
            'tracks': [self._prepare_track(t) for t in tracks],
            'similarity_matrix': np.zeros((n_tracks, n_tracks)),
            'compatibility_matrix': np.zeros((n_tracks, n_tracks)),
            'optimal_order': [],
            'transition_quality': [],
            'key_relationships': [],
            'energy_flow': []
        }
        
        # Calculate pairwise similarities
        for i in range(n_tracks):
            for j in range(i+1, n_tracks):
                similarity, compatibility = self._compare_pair(
                    tracks[i], tracks[j]
                )
                comparison['similarity_matrix'][i][j] = similarity
                comparison['similarity_matrix'][j][i] = similarity
                comparison['compatibility_matrix'][i][j] = compatibility
                comparison['compatibility_matrix'][j][i] = compatibility
        
        # Calculate optimal ordering
        comparison['optimal_order'] = self._find_optimal_order(
            comparison['compatibility_matrix']
        )
        
        # Analyze transitions
        for i in range(len(comparison['optimal_order']) - 1):
            idx1 = comparison['optimal_order'][i]
            idx2 = comparison['optimal_order'][i+1]
            transition = self._analyze_transition(tracks[idx1], tracks[idx2])
            comparison['transition_quality'].append(transition)
        
        # Key relationships
        comparison['key_relationships'] = self._analyze_key_relationships(tracks)
        
        # Energy flow
        comparison['energy_flow'] = self._analyze_energy_flow(
            tracks, comparison['optimal_order']
        )
        
        return comparison
    
    def _compare_pair(self, track1: Dict, track2: Dict) -> Tuple[float, float]:
        """Compare two tracks for similarity and compatibility."""
        
        # HAMMS similarity
        v1 = np.array(track1['hamms_vector'])
        v2 = np.array(track2['hamms_vector'])
        weights = self.weights.get_weights_array()
        
        # Weighted cosine similarity
        weighted_v1 = v1 * weights
        weighted_v2 = v2 * weights
        similarity = 1 - cosine(weighted_v1, weighted_v2)
        
        # Compatibility score (considers mixing rules)
        compatibility = 0.0
        
        # BPM compatibility (±6% optimal for mixing)
        bpm1, bpm2 = track1['bpm'], track2['bpm']
        bpm_diff_percent = abs(bpm1 - bpm2) / min(bpm1, bpm2) * 100
        if bpm_diff_percent <= 2:
            compatibility += 0.4  # Perfect
        elif bpm_diff_percent <= 6:
            compatibility += 0.3  # Good
        elif bpm_diff_percent <= 10:
            compatibility += 0.1  # Acceptable
        
        # Key compatibility (Camelot wheel)
        key_compat = self.camelot_wheel.get_compatibility(
            track1['key'], track2['key']
        )
        compatibility += key_compat * 0.4
        
        # Energy compatibility
        energy_diff = abs(track1['energy'] - track2['energy'])
        if energy_diff <= 0.2:
            compatibility += 0.2  # Smooth transition
        elif energy_diff <= 0.4:
            compatibility += 0.1  # Acceptable
        
        return similarity, compatibility
```

## Phase 4: DECIDE - Deployment & Validation

### Sprint 9-10: Integration & Testing
**Duration:** 2 weeks
**Team:** Full team

#### Week 9: Integration Testing
```python
# Comprehensive integration test suite
import pytest
import tempfile
from pathlib import Path

class TestIntegration:
    """End-to-end integration tests."""
    
    @pytest.fixture
    def test_library(self):
        """Create test music library."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            test_files = []
            for i in range(100):
                file_path = Path(tmpdir) / f"track_{i}.mp3"
                # Create dummy MP3 file
                self._create_test_mp3(file_path)
                test_files.append(str(file_path))
            yield test_files
    
    def test_batch_processing_performance(self, test_library):
        """Test batch processing meets performance targets."""
        processor = BatchProcessor(max_workers=4)
        analyzer = EnhancedAnalyzer()
        
        start_time = time.time()
        results = list(processor.process_batch(
            test_library, 
            analyzer.analyze_track
        ))
        elapsed = time.time() - start_time
        
        # Assertions
        assert len(results) == 100
        assert elapsed < 30  # Should process 100 tracks in < 30 seconds
        
        # Check all tracks analyzed
        for result in results:
            assert 'hamms_vector' in result
            assert len(result['hamms_vector']) == 12
    
    def test_export_generation(self, test_library):
        """Test export functionality."""
        # Analyze library first
        analyzer = EnhancedAnalyzer()
        results = [analyzer.analyze_track(f) for f in test_library[:10]]
        
        # Test PDF export
        exporter = ExportManager()
        pdf_data = exporter.export(
            {'tracks': results},
            'pdf',
            {'template': 'professional'}
        )
        assert len(pdf_data) > 1000  # PDF should have content
        
        # Test Excel export
        excel_data = exporter.export(
            {'tracks': results},
            'excel',
            {}
        )
        assert len(excel_data) > 500
    
    def test_search_performance(self):
        """Test search functionality and performance."""
        # Setup database with test data
        engine = create_engine('sqlite:///:memory:')
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        # Add test tracks
        for i in range(1000):
            track = Track(
                file_path=f"/music/track_{i}.mp3",
                title=f"Track {i}",
                artist=f"Artist {i % 100}",
                genre=f"Genre {i % 10}",
                bpm=120 + (i % 60),
                key=f"{i % 12}A"
            )
            session.add(track)
        session.commit()
        
        # Test search
        search_engine = SearchEngine(session)
        
        start_time = time.time()
        results = search_engine.search("Track", {
            'bpm': {'operator': 'range', 'min': 120, 'max': 140}
        })
        elapsed = time.time() - start_time
        
        assert len(results) > 0
        assert elapsed < 0.1  # Search should be < 100ms
```

#### Week 10: Deployment Preparation
```bash
# Deployment configuration
# docker-compose.yml
version: '3.8'

services:
  map4:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./music:/music:ro
    environment:
      - DATABASE_URL=postgresql://map4:password@db:5432/map4
      - REDIS_URL=redis://redis:6379
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    depends_on:
      - db
      - redis
  
  db:
    image: postgres:14
    environment:
      - POSTGRES_DB=map4
      - POSTGRES_USER=map4
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:7
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

## Success Criteria & Validation

### Performance Benchmarks
- [ ] 500+ tracks/minute processing speed
- [ ] <5 second export for 1000 tracks
- [ ] <100ms search response time
- [ ] 70% cache hit rate achieved

### Quality Gates
- [ ] All unit tests passing (>90% coverage)
- [ ] Integration tests passing
- [ ] Performance benchmarks met
- [ ] Security audit completed
- [ ] Documentation updated

### Rollout Plan
1. **Alpha Release:** Internal testing (Week 10)
2. **Beta Release:** Limited user group (Week 11)
3. **Production Release:** Full rollout (Week 12)

---

**Document Version:** 1.0.0
**Last Updated:** 2024-12
**Next Review:** End of Sprint 2
**Owner:** Development Team