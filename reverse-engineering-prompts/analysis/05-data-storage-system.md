# Data Storage and Management System

## Overview
MAP4 uses a sophisticated SQLAlchemy-based storage system with SQLite as the primary database. The system manages tracks, analysis results, HAMMS vectors, AI enrichment data, and metadata through a well-designed relational schema with proper relationships and constraints.

## Database Architecture

### Core Schema Design
The database consists of several interconnected tables that maintain referential integrity while supporting complex music analysis workflows:

```python
# Base declarative class
class Base(DeclarativeBase):
    pass

# Main tables:
# - tracks (TrackORM)
# - analysis_results (AnalysisResultORM) 
# - hamms_vectors (HAMMSVectorORM)
# - ai_analysis (AIAnalysis)
# - hamms_advanced (HAMMSAdvanced)
```

### Storage Wrapper (`src/services/storage.py`)
```python
@dataclass
class Storage:
    """SQLite storage wrapper using SQLAlchemy ORM."""
    
    db_url: str
    
    @classmethod
    def from_path(cls, db_path: str | Path) -> "Storage":
        """Create storage from file path or URL"""
        if isinstance(db_path, str) and "://" in db_path:
            return cls(db_path)  # Direct URL
        
        p = Path(db_path)
        abs_path = p.resolve()
        return cls(f"sqlite:///{abs_path}")
```

## Table Schemas

### 1. Tracks Table (`TrackORM`)
The central table that represents audio files and their basic metadata:

```python
class TrackORM(Base):
    __tablename__ = "tracks"
    
    # Primary identifier
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # File system integration
    path: Mapped[str] = mapped_column(String, unique=True, index=True)
    file_mtime: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    file_hash: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Basic metadata
    title: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    artist: Mapped[Optional[str]] = mapped_column(String, nullable=True) 
    album: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    duration_sec: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sample_rate: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Professional metadata
    isrc: Mapped[Optional[str]] = mapped_column(String(15), nullable=True)
    
    # DJ-specific metadata
    bpm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    initial_key: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    camelot_key: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    energy_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Processing metadata
    analyzed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    enrichment_status: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    
    # Relationships
    analysis: Mapped["AnalysisResultORM"] = relationship(back_populates="track", uselist=False, lazy="joined")
```

### 2. Analysis Results Table (`AnalysisResultORM`)
Stores the core analysis results from audio processing:

```python
class AnalysisResultORM(Base):
    __tablename__ = "analysis_results"
    
    # Primary key and foreign key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    track_id: Mapped[int] = mapped_column(ForeignKey("tracks.id"), index=True)
    
    # Core analysis results
    bpm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    key: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    energy: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # HAMMS vector reference
    hamms_id: Mapped[int] = mapped_column(ForeignKey("hamms_vectors.id"))
    
    # Analysis metadata
    analysis_source: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    source_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    track: Mapped[TrackORM] = relationship(back_populates="analysis")
    hamms: Mapped[HAMMSVectorORM] = relationship()
```

### 3. HAMMS Vectors Table (`HAMMSVectorORM`)
Stores the 12-dimensional HAMMS vectors with metadata:

```python
class HAMMSVectorORM(Base):
    __tablename__ = "hamms_vectors"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Vector data (JSON serialized)
    dims_json: Mapped[str] = mapped_column(Text)
    
    # Analysis method metadata
    method: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
```

### 4. AI Analysis Table (`AIAnalysis`)
Stores AI-generated semantic analysis data:

```python
class AIAnalysis(Base):
    __tablename__ = "ai_analysis"
    
    # Primary key - references tracks table
    track_id: Mapped[int] = mapped_column(Integer, ForeignKey("tracks.id"), primary_key=True)
    
    # AI Analysis results
    genre: Mapped[Optional[str]] = mapped_column(String(100))
    subgenre: Mapped[Optional[str]] = mapped_column(String(100))
    mood: Mapped[Optional[str]] = mapped_column(String(100))
    era: Mapped[Optional[str]] = mapped_column(String(50))
    tags: Mapped[Optional[str]] = mapped_column(Text)  # JSON array
    
    # Professional metadata  
    isrc: Mapped[Optional[str]] = mapped_column(String(15))
    
    # AI metadata
    ai_confidence: Mapped[Optional[float]] = mapped_column(Float)
    ai_model: Mapped[Optional[str]] = mapped_column(String(50), default="gpt-4")
    openai_response: Mapped[Optional[str]] = mapped_column(Text)  # Full response for debugging
    
    # Processing metadata
    analysis_date: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.utcnow)
    processing_time_ms: Mapped[Optional[int]] = mapped_column(Integer)
```

### 5. Advanced HAMMS Table (`HAMMSAdvanced`)
Stores enhanced HAMMS v3.0 analysis with 12-dimensional vectors:

```python
class HAMMSAdvanced(Base):
    __tablename__ = "hamms_advanced"
    
    # Primary key and foreign key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    track_id: Mapped[int] = mapped_column(ForeignKey("tracks.id"), unique=True, index=True)
    
    # 12-dimensional HAMMS vector (JSON serialized)
    vector_12d: Mapped[Optional[str]] = mapped_column(Text)
    
    # Individual dimension scores (JSON serialized)
    dimension_scores: Mapped[Optional[str]] = mapped_column(Text)
    
    # Analysis confidence and metadata
    ml_confidence: Mapped[Optional[float]] = mapped_column(Float)
    analysis_version: Mapped[Optional[str]] = mapped_column(String(20), default="3.0")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Relationship
    track: Mapped["TrackORM"] = relationship(back_populates="hamms_advanced", lazy="select")
```

## Data Access Layer

### Core CRUD Operations

#### Track Management
```python
def get_track_by_path(self, path: str) -> Optional[TrackORM]:
    """Get track by file path with related data"""
    with self.session() as s:
        stmt = select(TrackORM).where(TrackORM.path == path)
        track = s.scalars(stmt).first()
        
        if track:
            # Manually load AI analysis data
            ai_stmt = select(AIAnalysis).where(AIAnalysis.track_id == track.id)
            track.ai_analysis = s.scalars(ai_stmt).first()
            
            # Load HAMMS advanced data if available
            try:
                from src.models.hamms_advanced import HAMMSAdvanced
                hamms_stmt = select(HAMMSAdvanced).where(HAMMSAdvanced.track_id == track.id)
                track.hamms_advanced = s.scalars(hamms_stmt).first()
            except ImportError:
                track.hamms_advanced = None
        
        return track

def upsert_track(self, path: str) -> TrackORM:
    """Insert or update track by path"""
    with self.session() as s:
        t = s.scalar(select(TrackORM).where(TrackORM.path == path))
        if not t:
            t = TrackORM(path=path)
            s.add(t)
            s.commit()
            s.refresh(t)
        return t
```

#### Analysis Storage
```python
def add_analysis(self, track_path: str, analysis: Dict[str, Any]) -> AnalysisResultORM:
    """Store comprehensive analysis results"""
    
    # CRITICAL: Validate inputs using enhanced methodology
    if not isinstance(track_path, str) or not track_path.strip():
        raise ValueError("Track path must be non-empty string")
    
    if not isinstance(analysis, dict):
        raise TypeError(f"Analysis must be dictionary, got {type(analysis)}")
    
    # Validate critical analysis fields
    required_fields = {"bpm", "key", "energy", "hamms"}
    present_fields = set(analysis.keys())
    missing_fields = required_fields - present_fields
    if missing_fields:
        print(f"WARNING: Missing analysis fields for {track_path}: {missing_fields}")
    
    # Validate HAMMS vector
    hamms = analysis.get("hamms")
    if hamms is not None:
        if not isinstance(hamms, list):
            raise ValueError(f"HAMMS must be list, got {type(hamms)}")
        if len(hamms) != 12:
            raise ValueError(f"HAMMS vector must be 12-element list, got {len(hamms)}")
        if not all(isinstance(x, (int, float)) for x in hamms):
            raise ValueError("HAMMS vector must contain only numbers")
    
    with self.session() as s:
        # Get or create track
        t = s.scalar(select(TrackORM).where(TrackORM.path == track_path))
        if not t:
            t = TrackORM(path=track_path, analyzed_at=datetime.now(timezone.utc))
            s.add(t)
            s.flush()
        else:
            t.analyzed_at = datetime.now(timezone.utc)
        
        # Store HAMMS vector
        hamms_dims = analysis.get("hamms") or [0.0] * 12
        hv = HAMMSVectorORM(
            dims_json=json.dumps(hamms_dims), 
            method=analysis.get("hamms_method")
        )
        s.add(hv)
        s.flush()
        
        # Store analysis result
        ar = AnalysisResultORM(
            track_id=t.id,
            bpm=analysis.get("bpm"),
            key=analysis.get("key"),
            energy=analysis.get("energy"),
            hamms_id=hv.id,
            analysis_source=analysis.get("analysis_source"),
            source_confidence=analysis.get("source_confidence")
        )
        s.add(ar)
        
        # Update track metadata if provided
        if analysis.get("title"):
            t.title = analysis.get("title")
        if analysis.get("artist"):
            t.artist = analysis.get("artist")
        if analysis.get("album"):
            t.album = analysis.get("album")
        if analysis.get("isrc"):
            t.isrc = analysis.get("isrc")
        if analysis.get("bpm"):
            t.bpm = float(analysis.get("bpm"))
        if analysis.get("initial_key"):
            t.initial_key = analysis.get("initial_key")
        if analysis.get("camelot_key"):
            t.camelot_key = analysis.get("camelot_key")
        
        s.commit()
        s.refresh(ar)
        return ar
```

#### Data Retrieval
```python
def get_analysis_by_path(self, track_path: str) -> Optional[Dict[str, Any]]:
    """Get complete analysis data for a track"""
    with self.session() as s:
        t = s.scalar(select(TrackORM).where(TrackORM.path == track_path))
        if not t or not t.analysis:
            return None
            
        ar = t.analysis
        hv = ar.hamms
        
        # Parse HAMMS vector
        try:
            hamms = json.loads(hv.dims_json) if hv and hv.dims_json else []
        except (json.JSONDecodeError, TypeError) as e:
            print(f"WARNING: Failed to parse HAMMS vector for {track_path}: {e}")
            hamms = [0.0] * 12
        
        # Get AI analysis data
        ai_data = s.scalar(select(AIAnalysis).where(AIAnalysis.track_id == t.id))
        
        return {
            "path": t.path,
            "bpm": ar.bpm if ar.bpm is not None else t.bpm,
            "key": t.initial_key or ar.key,
            "energy": ar.energy,
            "hamms": hamms,
            "title": t.title,
            "artist": t.artist,
            "album": t.album,
            "isrc": t.isrc,
            "comment": t.comment,
            "analyzed_at": t.analyzed_at.isoformat() if t.analyzed_at else None,
            # AI analysis fields
            "genre": ai_data.genre if ai_data else None,
            "subgenre": ai_data.subgenre if ai_data else None,
            "mood": ai_data.mood if ai_data else None,
            "era": ai_data.era if ai_data else None,
            "tags": ai_data.tags if ai_data else None,
            "ai_confidence": ai_data.ai_confidence if ai_data else None
        }
```

## AI Analysis Integration

### AI Analysis Model Methods
```python
class AIAnalysis(Base):
    def get_tags(self) -> list[str]:
        """Get tags as a list of strings"""
        if not self.tags:
            return []
        
        try:
            tags = json.loads(self.tags)
            if isinstance(tags, list):
                return [str(tag) for tag in tags]
        except (json.JSONDecodeError, TypeError):
            pass
        
        return []
    
    def set_tags(self, tags: list[str]) -> None:
        """Set tags from a list of strings"""
        if not isinstance(tags, list):
            raise ValueError("Tags must be a list")
        
        # Validate and clean tags
        clean_tags = []
        for tag in tags:
            if isinstance(tag, str) and tag.strip():
                clean_tags.append(tag.strip().lower())
        
        self.tags = json.dumps(clean_tags)
    
    @classmethod
    def from_llm_response(cls, track_id: int, response_data: Dict[str, Any], 
                         processing_time_ms: Optional[int] = None) -> 'AIAnalysis':
        """Create AIAnalysis instance from LLM API response"""
        analysis = cls()
        analysis.track_id = track_id
        analysis.processing_time_ms = processing_time_ms
        
        # Extract fields from response
        analysis.genre = response_data.get("genre")
        analysis.subgenre = response_data.get("subgenre")
        analysis.mood = response_data.get("mood")
        analysis.era = response_data.get("era")
        analysis.ai_confidence = response_data.get("confidence", 0.5)
        
        # Handle tags
        tags = response_data.get("tags", [])
        if isinstance(tags, list):
            analysis.set_tags(tags)
        
        # Store full response for debugging
        analysis.openai_response = json.dumps(response_data)
        
        return analysis
```

## Caching and Performance

### File Change Detection
```python
def get_cached_analysis(self, track_path: str, file_mtime: float | None) -> Optional[Dict[str, Any]]:
    """Return analysis dict if file mtimes match and analysis exists."""
    with self.session() as s:
        t = s.scalar(select(TrackORM).where(TrackORM.path == track_path))
        if not t or t.file_mtime is None or file_mtime is None:
            return None
            
        # Check if file has been modified (with floating point tolerance)
        if abs(t.file_mtime - float(file_mtime)) > 1e-6:
            return None  # File changed, cache invalid
            
        ar = t.analysis
        if not ar:
            return None  # No analysis cached
            
        # Return cached analysis
        hv = ar.hamms
        try:
            hamms = json.loads(hv.dims_json) if hv and hv.dims_json else []
        except (json.JSONDecodeError, TypeError):
            hamms = [0.0] * 12
            
        return {
            "path": t.path,
            "bmp": ar.bpm if ar.bpm is not None else t.bmp,
            "key": t.initial_key or ar.key,
            "energy": ar.energy,
            "hamms": hamms,
            # ... additional fields
        }
```

### Batch Operations
```python
def list_all_analyses(self) -> list[Dict[str, Any]]:
    """Get all analysis results efficiently"""
    with self.session() as s:
        rows = s.execute(select(TrackORM)).scalars().all()
        out: list[Dict[str, Any]] = []
        
        for t in rows:
            ar = t.analysis
            if not ar:
                continue
                
            # Parse HAMMS vector
            hv = ar.hamms
            try:
                hamms = json.loads(hv.dims_json) if hv and hv.dims_json else []
            except (json.JSONDecodeError, TypeError) as e:
                print(f"WARNING: Failed to parse HAMMS vector for {t.path}: {e}")
                hamms = [0.0] * 12
                
            # Get AI analysis data
            ai_data = s.scalar(select(AIAnalysis).where(AIAnalysis.track_id == t.id))
            
            out.append({
                "path": t.path,
                "title": t.title,
                "artist": t.artist,
                "album": t.album,
                "bpm": ar.bpm if ar.bpm is not None else t.bpm,
                "key": t.initial_key or ar.key,
                "energy": ar.energy,
                "hamms": hamms,
                "comment": t.comment,
                # AI fields
                "genre": ai_data.genre if ai_data else None,
                "subgenre": ai_data.subgenre if ai_data else None,
                "mood": ai_data.mood if ai_data else None,
                "era": ai_data.era if ai_data else None,
                "tags": ai_data.tags if ai_data else None,
                "ai_confidence": ai_data.ai_confidence if ai_data else None
            })
            
        return out
```

## Advanced Queries

### Genre-Based Filtering
```python
def get_tracks_with_ai_analysis(self, subgenre_filter: Optional[str] = None) -> list[Dict[str, Any]]:
    """Get tracks with their AI analysis data, optionally filtered by subgenre."""
    with self.session() as s:
        
        query = select(TrackORM).join(AIAnalysis, TrackORM.id == AIAnalysis.track_id)
        
        if subgenre_filter:
            query = query.where(AIAnalysis.subgenre == subgenre_filter)
        
        tracks = s.execute(query).scalars().all()
        # ... process results
```

### Statistical Summaries
```python
def summary(self) -> Dict[str, Any]:
    """Get database summary statistics"""
    from sqlalchemy import func
    
    with self.session() as s:
        total = s.scalar(select(func.count(TrackORM.id))) or 0
        with_analysis = s.scalar(select(func.count(AnalysisResultORM.id))) or 0
        avg_bpm = s.scalar(select(func.avg(AnalysisResultORM.bpm)))
        
        # Key distribution
        key_counts = {}
        for row in s.execute(select(TrackORM.initial_key)).all():
            k = row[0]
            if k:
                key_counts[k] = key_counts.get(k, 0) + 1
                
        top_keys = sorted(key_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "tracks": total,
            "with_analysis": with_analysis,
            "avg_bpm": float(avg_bpm) if avg_bpm is not None else None,
            "top_keys": top_keys
        }
```

## Database Migrations and Schema Evolution

### Alembic Integration
The system uses Alembic for database migrations:

```python
# alembic/versions/001_initial_schema.py
def upgrade():
    """Create initial schema"""
    op.create_table('tracks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('path', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=True),
        # ... other columns
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('path')
    )
    op.create_index(op.f('ix_tracks_path'), 'tracks', ['path'], unique=True)
```

### Schema Validation
```python
def validate_database_schema(storage: Storage) -> bool:
    """Validate database schema integrity"""
    try:
        with storage.session() as s:
            # Test basic table access
            s.execute(select(TrackORM).limit(1))
            s.execute(select(AnalysisResultORM).limit(1))
            s.execute(select(HAMMSVectorORM).limit(1))
            s.execute(select(AIAnalysis).limit(1))
            
        return True
    except Exception as e:
        print(f"Database schema validation failed: {e}")
        return False
```

## Error Handling and Data Integrity

### Transaction Management
```python
def safe_transaction(self, operation: Callable) -> bool:
    """Execute operation with proper transaction management"""
    try:
        with self.session() as s:
            result = operation(s)
            s.commit()
            return result
    except Exception as e:
        print(f"Transaction failed: {e}")
        return False
```

### Data Validation
```python
def validate_hamms_vector(hamms: List[float]) -> bool:
    """Validate HAMMS vector before storage"""
    if not isinstance(hamms, list):
        return False
    if len(hamms) != 12:
        return False
    if not all(isinstance(x, (int, float)) for x in hamms):
        return False
    if any(math.isnan(x) or math.isinf(x) for x in hamms):
        return False
    return True
```

### Backup and Recovery
```python
def backup_database(storage: Storage, backup_path: str) -> bool:
    """Create database backup"""
    try:
        import shutil
        db_path = storage.db_url.replace("sqlite:///", "")
        shutil.copy2(db_path, backup_path)
        return True
    except Exception as e:
        print(f"Backup failed: {e}")
        return False
```

The data storage system provides a robust, scalable foundation for managing complex music analysis data while maintaining referential integrity and supporting efficient queries across large music libraries. The design supports both simple operations and complex analytical queries while providing comprehensive error handling and data validation.