"""
DJ Metadata Models
Data models for professional DJ metadata including beatgrids, cue points, and loops.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum


class CueType(Enum):
    """Types of cue points used in DJ software."""
    HOT_CUE = "hot_cue"       # Hot cue (1-8)
    MEMORY_CUE = "memory"      # Memory cue (unlimited)
    INTRO = "intro"            # Track intro point
    OUTRO = "outro"            # Track outro point
    DROP = "drop"              # Drop/breakdown point
    BREAK = "break"            # Break section
    BUILD = "build"            # Build-up section
    VERSE = "verse"            # Verse section
    CHORUS = "chorus"          # Chorus section
    BRIDGE = "bridge"          # Bridge section
    VOCAL = "vocal"            # Vocal start/end
    LOOP = "loop"              # Loop point


@dataclass
class DJCuePoint:
    """Professional DJ cue point with all metadata."""
    position_ms: float         # Position in milliseconds
    type: CueType              # Type of cue point
    index: Optional[int] = None  # Hot cue index (0-7)
    name: Optional[str] = None   # Custom name
    color: str = "#CC0000"       # RGB color as hex
    comment: Optional[str] = None  # Additional notes

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "position_ms": self.position_ms,
            "type": self.type.value,
            "index": self.index,
            "name": self.name,
            "color": self.color,
            "comment": self.comment
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DJCuePoint':
        """Create from dictionary."""
        return cls(
            position_ms=data["position_ms"],
            type=CueType(data["type"]),
            index=data.get("index"),
            name=data.get("name"),
            color=data.get("color", "#CC0000"),
            comment=data.get("comment")
        )


@dataclass
class DJLoop:
    """DJ loop region with start/end points."""
    start_ms: float            # Loop start in milliseconds
    end_ms: float              # Loop end in milliseconds
    length_beats: Optional[int] = None  # Loop length in beats (4, 8, 16, 32)
    color: str = "#00CC00"     # RGB color as hex
    name: Optional[str] = None # Custom name
    enabled: bool = False      # Is loop active

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "start_ms": self.start_ms,
            "end_ms": self.end_ms,
            "length_beats": self.length_beats,
            "color": self.color,
            "name": self.name,
            "enabled": self.enabled
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DJLoop':
        """Create from dictionary."""
        return cls(
            start_ms=data["start_ms"],
            end_ms=data["end_ms"],
            length_beats=data.get("length_beats"),
            color=data.get("color", "#00CC00"),
            name=data.get("name"),
            enabled=data.get("enabled", False)
        )


@dataclass
class DJBeatGrid:
    """Professional beatgrid with downbeat detection."""
    bpm: float                  # Tempo in BPM
    first_beat_ms: float        # Position of first beat
    beats: List[float] = field(default_factory=list)  # Beat positions in ms
    downbeats: List[float] = field(default_factory=list)  # Downbeat positions (bar starts)
    time_signature: str = "4/4"  # Time signature
    confidence: float = 1.0       # Analysis confidence (0-1)
    is_dynamic: bool = False      # True if tempo changes

    def get_beat_at_position(self, position_ms: float) -> Optional[int]:
        """Get the beat number at a given position."""
        if not self.beats:
            return None

        for i, beat in enumerate(self.beats):
            if beat > position_ms:
                return i - 1 if i > 0 else 0

        return len(self.beats) - 1

    def get_bar_at_position(self, position_ms: float) -> Optional[int]:
        """Get the bar number at a given position."""
        if not self.downbeats:
            return None

        for i, downbeat in enumerate(self.downbeats):
            if downbeat > position_ms:
                return i - 1 if i > 0 else 0

        return len(self.downbeats) - 1

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "bpm": self.bpm,
            "first_beat_ms": self.first_beat_ms,
            "beats": self.beats,
            "downbeats": self.downbeats,
            "time_signature": self.time_signature,
            "confidence": self.confidence,
            "is_dynamic": self.is_dynamic
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DJBeatGrid':
        """Create from dictionary."""
        return cls(
            bpm=data["bpm"],
            first_beat_ms=data["first_beat_ms"],
            beats=data.get("beats", []),
            downbeats=data.get("downbeats", []),
            time_signature=data.get("time_signature", "4/4"),
            confidence=data.get("confidence", 1.0),
            is_dynamic=data.get("is_dynamic", False)
        )


@dataclass
class TrackStructure:
    """Musical structure analysis of a track."""
    intro_ms: Optional[float] = None
    outro_ms: Optional[float] = None
    breakdown_ms: List[float] = field(default_factory=list)
    buildup_ms: List[float] = field(default_factory=list)
    drop_ms: List[float] = field(default_factory=list)
    phrase_length_bars: int = 8  # Typical phrase length
    total_bars: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "intro_ms": self.intro_ms,
            "outro_ms": self.outro_ms,
            "breakdown_ms": self.breakdown_ms,
            "buildup_ms": self.buildup_ms,
            "drop_ms": self.drop_ms,
            "phrase_length_bars": self.phrase_length_bars,
            "total_bars": self.total_bars
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TrackStructure':
        """Create from dictionary."""
        return cls(
            intro_ms=data.get("intro_ms"),
            outro_ms=data.get("outro_ms"),
            breakdown_ms=data.get("breakdown_ms", []),
            buildup_ms=data.get("buildup_ms", []),
            drop_ms=data.get("drop_ms", []),
            phrase_length_bars=data.get("phrase_length_bars", 8),
            total_bars=data.get("total_bars")
        )


@dataclass
class DJMetadata:
    """Complete DJ metadata for a track."""
    # Core analysis
    bpm: Optional[float] = None
    key: Optional[str] = None
    camelot_key: Optional[str] = None
    energy: Optional[int] = None  # 1-10 scale

    # DJ-specific data
    beatgrid: Optional[DJBeatGrid] = None
    cue_points: List[DJCuePoint] = field(default_factory=list)
    loops: List[DJLoop] = field(default_factory=list)
    structure: Optional[TrackStructure] = None

    # Mix compatibility
    compatible_keys: List[str] = field(default_factory=list)
    mix_in_key: Optional[str] = None  # Recommended mix-in key
    mix_out_key: Optional[str] = None  # Recommended mix-out key

    # Additional metadata
    mood: Optional[str] = None
    danceability: Optional[int] = None  # 1-10 scale
    genre: Optional[str] = None
    comment: Optional[str] = None

    # Source information
    analysis_source: Optional[str] = None  # serato, mixedinkey, etc.
    analysis_date: Optional[str] = None
    confidence: float = 1.0

    def add_cue_point(self, position_ms: float, cue_type: CueType,
                      name: Optional[str] = None, color: str = "#CC0000") -> DJCuePoint:
        """Add a new cue point."""
        # Find next available hot cue index if it's a hot cue
        index = None
        if cue_type == CueType.HOT_CUE:
            used_indices = {c.index for c in self.cue_points
                          if c.type == CueType.HOT_CUE and c.index is not None}
            for i in range(8):
                if i not in used_indices:
                    index = i
                    break

        cue = DJCuePoint(
            position_ms=position_ms,
            type=cue_type,
            index=index,
            name=name,
            color=color
        )
        self.cue_points.append(cue)
        return cue

    def add_loop(self, start_ms: float, end_ms: float,
                 name: Optional[str] = None) -> DJLoop:
        """Add a new loop."""
        loop = DJLoop(
            start_ms=start_ms,
            end_ms=end_ms,
            name=name
        )
        self.loops.append(loop)
        return loop

    def get_hot_cues(self) -> List[DJCuePoint]:
        """Get all hot cues sorted by index."""
        hot_cues = [c for c in self.cue_points if c.type == CueType.HOT_CUE]
        return sorted(hot_cues, key=lambda c: c.index or 999)

    def get_memory_cues(self) -> List[DJCuePoint]:
        """Get all memory cues sorted by position."""
        memory_cues = [c for c in self.cue_points if c.type == CueType.MEMORY_CUE]
        return sorted(memory_cues, key=lambda c: c.position_ms)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "bpm": self.bpm,
            "key": self.key,
            "camelot_key": self.camelot_key,
            "energy": self.energy,
            "beatgrid": self.beatgrid.to_dict() if self.beatgrid else None,
            "cue_points": [c.to_dict() for c in self.cue_points],
            "loops": [l.to_dict() for l in self.loops],
            "structure": self.structure.to_dict() if self.structure else None,
            "compatible_keys": self.compatible_keys,
            "mix_in_key": self.mix_in_key,
            "mix_out_key": self.mix_out_key,
            "mood": self.mood,
            "danceability": self.danceability,
            "genre": self.genre,
            "comment": self.comment,
            "analysis_source": self.analysis_source,
            "analysis_date": self.analysis_date,
            "confidence": self.confidence
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DJMetadata':
        """Create from dictionary."""
        metadata = cls(
            bpm=data.get("bpm"),
            key=data.get("key"),
            camelot_key=data.get("camelot_key"),
            energy=data.get("energy"),
            compatible_keys=data.get("compatible_keys", []),
            mix_in_key=data.get("mix_in_key"),
            mix_out_key=data.get("mix_out_key"),
            mood=data.get("mood"),
            danceability=data.get("danceability"),
            genre=data.get("genre"),
            comment=data.get("comment"),
            analysis_source=data.get("analysis_source"),
            analysis_date=data.get("analysis_date"),
            confidence=data.get("confidence", 1.0)
        )

        # Reconstruct complex objects
        if data.get("beatgrid"):
            metadata.beatgrid = DJBeatGrid.from_dict(data["beatgrid"])

        if data.get("cue_points"):
            metadata.cue_points = [DJCuePoint.from_dict(c) for c in data["cue_points"]]

        if data.get("loops"):
            metadata.loops = [DJLoop.from_dict(l) for l in data["loops"]]

        if data.get("structure"):
            metadata.structure = TrackStructure.from_dict(data["structure"])

        return metadata