from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any

from sqlalchemy import (
    String,
    Integer,
    Float,
    DateTime,
    ForeignKey,
    Text,
    create_engine,
    select,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session
from datetime import datetime, timezone

# Import the new models for relationships
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from src.models.hamms_advanced import HAMMSAdvanced

class Base(DeclarativeBase):
    pass


class AIAnalysis(Base):
    """Database model for AI analysis results"""
    
    __tablename__ = "ai_analysis"
    
    # Primary key - references tracks table
    track_id: Mapped[int] = mapped_column(Integer, ForeignKey("tracks.id"), primary_key=True)
    
    # AI Analysis results
    genre: Mapped[Optional[str]] = mapped_column(String(100))          # Primary genre
    subgenre: Mapped[Optional[str]] = mapped_column(String(100))       # Specific subgenre
    mood: Mapped[Optional[str]] = mapped_column(String(100))           # Emotional mood
    era: Mapped[Optional[str]] = mapped_column(String(50))             # Musical era/decade
    tags: Mapped[Optional[str]] = mapped_column(Text)                  # JSON array of tags
    
    # Professional metadata
    isrc: Mapped[Optional[str]] = mapped_column(String(15))            # International Standard Recording Code
    
    # AI metadata
    ai_confidence: Mapped[Optional[float]] = mapped_column(Float)      # Overall AI confidence (0-1)
    ai_model: Mapped[Optional[str]] = mapped_column(String(50), default="gpt-4")  # AI model used
    openai_response: Mapped[Optional[str]] = mapped_column(Text)       # Full OpenAI response for debugging
    
    # Processing metadata
    analysis_date: Mapped[Optional[datetime]] = mapped_column(DateTime, default=datetime.utcnow)
    processing_time_ms: Mapped[Optional[int]] = mapped_column(Integer)  # Time taken for analysis in ms
    
    def __repr__(self) -> str:
        return f"<AIAnalysis(track_id={self.track_id}, genre={self.genre}, mood={self.mood})>"
    
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
    
    def set_openai_response_data(self, response_data: Dict[str, Any]) -> None:
        """Set OpenAI response data"""
        if not isinstance(response_data, dict):
            raise ValueError("Response data must be a dictionary")
        
        self.openai_response = json.dumps(response_data)
    
    @classmethod
    def from_openai_response(cls, track_id: int, response_data: Dict[str, Any], 
                           processing_time_ms: Optional[int] = None) -> 'AIAnalysis':
        """Create AIAnalysis instance from OpenAI API response
        
        Args:
            track_id: ID of the track being analyzed
            response_data: Parsed response from OpenAI API
            processing_time_ms: Time taken for the analysis
            
        Returns:
            AIAnalysis instance ready for database insertion
        """
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
        analysis.set_openai_response_data(response_data)
        
        return analysis
    
    @classmethod 
    def from_llm_response(cls, track_id: int, response_data: Dict[str, Any], 
                         processing_time_ms: Optional[int] = None) -> 'AIAnalysis':
        """Create AIAnalysis instance from LLM API response
        
        Alias for from_openai_response to support multi-LLM architecture.
        """
        return cls.from_openai_response(track_id, response_data, processing_time_ms)


class TrackORM(Base):
    __tablename__ = "tracks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    path: Mapped[str] = mapped_column(String, unique=True, index=True)
    title: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    artist: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    album: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    duration_sec: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sample_rate: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    analyzed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    enrichment_status: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    # Professional metadata
    isrc: Mapped[Optional[str]] = mapped_column(String(15), nullable=True)
    # Optional DJ metadata (can be precomputed/imported)
    bpm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    initial_key: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    camelot_key: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    energy_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # File cache metadata
    file_mtime: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    file_hash: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    analysis: Mapped["AnalysisResultORM"] = relationship(back_populates="track", uselist=False, lazy="joined")
    # Relationships - using lazy loading to avoid circular import issues
    # hamms_advanced: Mapped["HAMMSAdvanced"] = relationship(back_populates="track", uselist=False, lazy="select")
    # ai_analysis: Mapped["AIAnalysis"] = relationship(back_populates="track", uselist=False, lazy="select")


class HAMMSVectorORM(Base):
    __tablename__ = "hamms_vectors"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    dims_json: Mapped[str] = mapped_column(Text)
    method: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))


class AnalysisResultORM(Base):
    __tablename__ = "analysis_results"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    track_id: Mapped[int] = mapped_column(ForeignKey("tracks.id"), index=True)
    bpm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    key: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    energy: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    hamms_id: Mapped[int] = mapped_column(ForeignKey("hamms_vectors.id"))
    analysis_source: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    source_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    track: Mapped[TrackORM] = relationship(back_populates="analysis")
    hamms: Mapped[HAMMSVectorORM] = relationship()


@dataclass
class Storage:
    """SQLite storage wrapper using SQLAlchemy ORM."""

    db_url: str

    @classmethod
    def from_path(cls, db_path: str | Path) -> "Storage":
        # Accept URL directly
        if isinstance(db_path, str) and "://" in db_path:
            return cls(db_path)
        p = Path(db_path)
        abs_path = p.resolve()
        return cls(f"sqlite:///{abs_path}")

    def __post_init__(self):
        self.engine = create_engine(self.db_url, future=True)
        Base.metadata.create_all(self.engine)

    # Sessions
    def session(self) -> Session:
        return Session(self.engine, future=True)

    # CRUD helpers
    def get_track_by_path(self, path: str) -> Optional[TrackORM]:
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
        with self.session() as s:
            t = s.scalar(select(TrackORM).where(TrackORM.path == path))
            if not t:
                t = TrackORM(path=path)
                s.add(t)
                s.commit()
                s.refresh(t)
            return t

    def add_analysis(self, track_path: str, analysis: Dict[str, Any]) -> AnalysisResultORM:
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
        
        # Validate HAMMS vector if present
        hamms = analysis.get("hamms")
        if hamms is not None:
            if not isinstance(hamms, list):
                raise ValueError(f"HAMMS must be list, got {type(hamms)}")
            if len(hamms) != 12:
                raise ValueError(f"HAMMS vector must be 12-element list, got {len(hamms)}")
            if not all(isinstance(x, (int, float)) for x in hamms):
                raise ValueError("HAMMS vector must contain only numbers")
        with self.session() as s:
            t = s.scalar(select(TrackORM).where(TrackORM.path == track_path))
            if not t:
                t = TrackORM(path=track_path, analyzed_at=datetime.now(timezone.utc))
                s.add(t)
                s.flush()
            else:
                t.analyzed_at = datetime.now(timezone.utc)
            # update file cache meta if provided
            if analysis.get("file_mtime") is not None:
                try:
                    t.file_mtime = float(analysis.get("file_mtime"))
                except (ValueError, TypeError) as e:
                    print(f"WARNING: Invalid file_mtime for {track_path}: {e}")
                    t.file_mtime = None
            if analysis.get("file_hash"):
                t.file_hash = str(analysis.get("file_hash"))

            hamms_dims = analysis.get("hamms") or [0.0] * 12
            hv = HAMMSVectorORM(dims_json=json.dumps(hamms_dims), method=analysis.get("hamms_method"))
            s.add(hv)
            s.flush()

            ar = AnalysisResultORM(
                track_id=t.id,
                bpm=analysis.get("bpm"),
                key=analysis.get("key"),
                energy=analysis.get("energy"),
                hamms_id=hv.id,
                analysis_source=analysis.get("analysis_source"),
                source_confidence=analysis.get("source_confidence"),
            )
            s.add(ar)
            # Update track-level DJ metadata if provided
            if analysis.get("comment"):
                t.comment = analysis.get("comment")
            # Update professional metadata
            if analysis.get("isrc"):
                t.isrc = analysis.get("isrc")
            if analysis.get("title"):
                t.title = analysis.get("title")
            if analysis.get("artist"):
                t.artist = analysis.get("artist")  
            if analysis.get("album"):
                t.album = analysis.get("album")
            if analysis.get("initial_key"):
                t.initial_key = analysis.get("initial_key")
            if analysis.get("camelot_key"):
                t.camelot_key = analysis.get("camelot_key")
            if analysis.get("energy_level") is not None:
                try:
                    t.energy_level = int(analysis.get("energy_level"))
                except (ValueError, TypeError) as e:
                    print(f"WARNING: Invalid energy_level for {track_path}: {e}")
                    t.energy_level = None
            if analysis.get("bpm") is not None:
                try:
                    t.bpm = float(analysis.get("bpm"))
                except (ValueError, TypeError) as e:
                    print(f"WARNING: Invalid bpm for {track_path}: {e}")
                    t.bpm = None
            s.commit()
            s.refresh(ar)
            return ar

    def summary(self) -> Dict[str, Any]:
        from sqlalchemy import func

        with self.session() as s:
            total = s.scalar(select(func.count(TrackORM.id))) or 0
            with_analysis = s.scalar(select(func.count(AnalysisResultORM.id))) or 0
            avg_bpm = s.scalar(select(func.avg(AnalysisResultORM.bpm)))
            # top keys from Track initial_key when available, fallback to AnalysisResult.key
            key_counts = {}
            for row in s.execute(select(TrackORM.initial_key)).all():
                k = row[0]
                if k:
                    key_counts[k] = key_counts.get(k, 0) + 1
            if not key_counts:
                for row in s.execute(select(AnalysisResultORM.key)).all():
                    k = row[0]
                    if k:
                        key_counts[k] = key_counts.get(k, 0) + 1
            top_keys = sorted(key_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            return {
                "tracks": total,
                "with_analysis": with_analysis,
                "avg_bpm": float(avg_bpm) if avg_bpm is not None else None,
                "top_keys": top_keys,
            }

    def get_analysis_by_path(self, track_path: str) -> Optional[Dict[str, Any]]:
        with self.session() as s:
            t = s.scalar(select(TrackORM).where(TrackORM.path == track_path))
            if not t:
                return None
            ar = t.analysis
            if not ar:
                return None
            hv = ar.hamms
            hamms = []
            try:
                hamms = json.loads(hv.dims_json) if hv and hv.dims_json else []
            except (json.JSONDecodeError, TypeError) as e:
                print(f"WARNING: Failed to parse HAMMS vector for {track_path}: {e}")
                hamms = [0.0] * 12
            
            # Get AI analysis data if available
            ai_data = s.scalar(select(AIAnalysis).where(AIAnalysis.track_id == t.id))
            
            return {
                "path": t.path,
                "bpm": ar.bpm if ar.bpm is not None else t.bpm,
                "key": t.initial_key or ar.key,
                "energy": ar.energy,
                "hamms": hamms,
                "comment": t.comment,
                "isrc": t.isrc,
                "title": t.title,
                "artist": t.artist,
                "album": t.album,
                "analyzed_at": t.analyzed_at.isoformat() if t.analyzed_at else None,
                # Add AI analysis fields
                "genre": ai_data.genre if ai_data else None,
                "subgenre": ai_data.subgenre if ai_data else None,
                "mood": ai_data.mood if ai_data else None,
                "era": ai_data.era if ai_data else None,
                "tags": ai_data.tags if ai_data else None,
                "ai_confidence": ai_data.ai_confidence if ai_data else None,
            }

    def list_all_analyses(self) -> list[Dict[str, Any]]:
        with self.session() as s:
            rows = s.execute(select(TrackORM)).scalars().all()
            out: list[Dict[str, Any]] = []
            for t in rows:
                ar = t.analysis
                if not ar:
                    continue
                hv = ar.hamms
                try:
                    hamms = json.loads(hv.dims_json) if hv and hv.dims_json else []
                except (json.JSONDecodeError, TypeError) as e:
                    print(f"WARNING: Failed to parse HAMMS vector for {t.path}: {e}")
                    hamms = [0.0] * 12
                # Get AI analysis data if available
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
                    # Add AI analysis fields
                    "genre": ai_data.genre if ai_data else None,
                    "subgenre": ai_data.subgenre if ai_data else None,
                    "mood": ai_data.mood if ai_data else None,
                    "era": ai_data.era if ai_data else None,
                    "tags": ai_data.tags if ai_data else None,
                    "ai_confidence": ai_data.ai_confidence if ai_data else None,
                })
            return out

    def get_cached_analysis(self, track_path: str, file_mtime: float | None) -> Optional[Dict[str, Any]]:
        """Return analysis dict if file mtimes match and analysis exists."""
        with self.session() as s:
            t = s.scalar(select(TrackORM).where(TrackORM.path == track_path))
            if not t or t.file_mtime is None or file_mtime is None:
                return None
            if abs(t.file_mtime - float(file_mtime)) > 1e-6:
                return None
            ar = t.analysis
            if not ar:
                return None
            hv = ar.hamms
            hamms = []
            try:
                hamms = json.loads(hv.dims_json) if hv and hv.dims_json else []
            except (json.JSONDecodeError, TypeError) as e:
                print(f"WARNING: Failed to parse HAMMS vector for {track_path}: {e}")
                hamms = [0.0] * 12
            return {
                "path": t.path,
                "bpm": ar.bpm if ar.bpm is not None else t.bpm,
                "key": t.initial_key or ar.key,
                "energy": ar.energy,
                "hamms": hamms,
                "comment": t.comment,
                "isrc": t.isrc,
                "title": t.title,
                "artist": t.artist,
                "album": t.album,
                "analyzed_at": t.analyzed_at.isoformat() if t.analyzed_at else None,
            }

    def update_track_dj_metadata(self, track_path: str, meta: Dict[str, Any]) -> None:
        with self.session() as s:
            t = s.scalar(select(TrackORM).where(TrackORM.path == track_path))
            if not t:
                t = TrackORM(path=track_path)
                s.add(t)
            for k in ("bpm", "initial_key", "camelot_key", "energy_level", "comment"):
                if meta.get(k) is not None:
                    setattr(t, k, meta.get(k))
            s.commit()

    def get_tracks_with_ai_analysis(self, subgenre_filter: Optional[str] = None) -> list[Dict[str, Any]]:
        """Get tracks with their AI analysis data, optionally filtered by subgenre."""
        with self.session() as s:
            
            query = select(TrackORM).join(AIAnalysis, TrackORM.id == AIAnalysis.track_id)
            
            if subgenre_filter:
                query = query.where(AIAnalysis.subgenre == subgenre_filter)
            
            tracks = s.execute(query).scalars().all()
            result = []
            
            for track in tracks:
                # Defensive access - ai_analysis relationship may not be available
                ai_analysis = getattr(track, 'ai_analysis', None)
                analysis_result = track.analysis
                
                # Get HAMMS vector
                hamms = []
                if analysis_result and analysis_result.hamms:
                    try:
                        hamms = json.loads(analysis_result.hamms.dims_json) if analysis_result.hamms.dims_json else []
                    except (json.JSONDecodeError, TypeError):
                        hamms = [0.0] * 12
                
                track_data = {
                    "path": track.path,
                    "title": track.title,
                    "artist": track.artist,
                    "album": track.album,
                    "isrc": track.isrc,
                    "bpm": analysis_result.bpm if analysis_result and analysis_result.bpm else track.bpm,
                    "key": track.initial_key or (analysis_result.key if analysis_result else None),
                    "energy": analysis_result.energy if analysis_result else None,
                    "hamms": hamms,
                    "comment": track.comment,
                    "analyzed_at": track.analyzed_at.isoformat() if track.analyzed_at else None,
                }
                
                # Add AI analysis data
                if ai_analysis:
                    track_data.update({
                        "genre": ai_analysis.genre,
                        "subgenre": ai_analysis.subgenre,
                        "mood": ai_analysis.mood,
                        "era": ai_analysis.era,
                        "tags": ai_analysis.get_tags(),
                        "ai_confidence": ai_analysis.ai_confidence,
                    })
                
                result.append(track_data)
            
            return result

    def get_available_subgenres(self) -> list[str]:
        """Get list of all available subgenres from AI analysis data."""
        with self.session() as s:
            
            subgenres = s.execute(
                select(AIAnalysis.subgenre).distinct().where(AIAnalysis.subgenre.isnot(None))
            ).scalars().all()
            
            return [sg for sg in subgenres if sg and sg.strip()]
