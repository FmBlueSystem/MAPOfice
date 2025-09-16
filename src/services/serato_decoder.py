"""
Serato Metadata Decoder
Extracts beatgrids, cue points, loops and other DJ metadata from Serato tags.

Serato stores data in several ID3 GEOB (General Encapsulated Object) frames:
- Serato Markers_: Contains hot cues and memory cues
- Serato Markers2: Contains beatgrid, colored cues, loops
- Serato BeatGrid: Contains detailed beatgrid data
- Serato Autotags: Contains auto-analyzed BPM and key
- Serato OfflineAd: Contains additional performance data
"""

import base64
import struct
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class CuePoint:
    """Represents a Serato cue point."""
    index: int  # 0-7 for hot cues
    position_ms: float  # Position in milliseconds
    color: str  # RGB color as hex string
    name: Optional[str] = None
    type: str = "cue"  # cue, loop, memory


@dataclass
class BeatGrid:
    """Represents Serato beatgrid data with downbeats."""
    bpm: float
    first_beat_position: float  # Position of first beat in seconds
    first_downbeat_position: float = 0  # Position of first downbeat (bar start)
    beats: List[float] = None  # List of beat positions in seconds
    downbeats: List[float] = None  # List of downbeat positions (bar starts)
    bars_count: int = 0  # Number of bars detected
    time_signature: str = "4/4"  # Time signature (usually 4/4 for electronic)


@dataclass
class Loop:
    """Represents a Serato loop."""
    start_position_ms: float
    end_position_ms: float
    color: str
    name: Optional[str] = None
    enabled: bool = False


class SeratoDecoder:
    """Decodes Serato metadata from ID3 tags."""

    # Serato color palette (index to RGB)
    SERATO_COLORS = {
        0: "#CC0000",  # Red
        1: "#CC4400",  # Orange
        2: "#CC8800",  # Yellow
        3: "#CCCC00",  # Lime
        4: "#88CC00",  # Green
        5: "#00CC00",  # Aqua
        6: "#00CC88",  # Cyan
        7: "#00CCCC",  # Light Blue
        8: "#0088CC",  # Blue
        9: "#0044CC",  # Purple
        10: "#4400CC", # Violet
        11: "#8800CC", # Magenta
        12: "#CC00CC", # Pink
        13: "#CC0088", # Fuchsia
        14: "#CC0044", # Carmine
        15: "#FFFFFF", # White
    }

    @staticmethod
    def decode_serato_markers(data: bytes) -> Dict[str, Any]:
        """
        Decode Serato Markers_ tag (version 1).
        Contains hot cues and memory cues.
        """
        if not data:
            return {}

        try:
            # Serato uses a custom encoding, need to unescape
            data = SeratoDecoder._unescape_serato_data(data)

            cues = []
            offset = 0

            # Parse header
            if len(data) < 2:
                return {}

            version = struct.unpack('>H', data[offset:offset+2])[0]
            offset += 2

            # Parse entries
            while offset < len(data) - 22:  # Minimum entry size
                # Check for entry marker
                if data[offset:offset+4] != b'CUE\x00':
                    offset += 1
                    continue

                offset += 4
                entry_size = struct.unpack('>I', data[offset:offset+4])[0]
                offset += 4

                if offset + entry_size > len(data):
                    break

                # Parse cue entry
                entry_data = data[offset:offset+entry_size]
                cue = SeratoDecoder._parse_cue_entry(entry_data)
                if cue:
                    cues.append(cue)

                offset += entry_size

            return {"cues": cues}

        except Exception as e:
            logger.warning(f"Failed to decode Serato Markers: {e}")
            return {}

    @staticmethod
    def decode_serato_markers2(data: bytes) -> Dict[str, Any]:
        """
        Decode Serato Markers2 tag (version 2).
        Contains beatgrid, colored cues, loops, and more.
        """
        if not data:
            return {}

        try:
            data = SeratoDecoder._unescape_serato_data(data)

            result = {
                "cues": [],
                "loops": [],
                "beatgrid": None,
                "bpm": None
            }

            offset = 0

            # Parse header
            if len(data) < 2:
                return {}

            version = struct.unpack('>H', data[offset:offset+2])[0]
            offset += 2

            # Parse entries
            while offset < len(data) - 8:
                # Read entry type
                if offset + 4 > len(data):
                    break

                entry_type = data[offset:offset+4]
                offset += 4

                if offset + 4 > len(data):
                    break

                entry_size = struct.unpack('>I', data[offset:offset+4])[0]
                offset += 4

                if offset + entry_size > len(data):
                    break

                entry_data = data[offset:offset+entry_size]

                # Parse different entry types
                if entry_type == b'CUE\x00':
                    cue = SeratoDecoder._parse_cue_entry(entry_data)
                    if cue:
                        result["cues"].append(cue)

                elif entry_type == b'LOOP':
                    loop = SeratoDecoder._parse_loop_entry(entry_data)
                    if loop:
                        result["loops"].append(loop)

                elif entry_type == b'BEAT':
                    beatgrid = SeratoDecoder._parse_beatgrid_entry(entry_data)
                    if beatgrid:
                        result["beatgrid"] = beatgrid
                        result["bpm"] = beatgrid.bpm

                offset += entry_size

            return result

        except Exception as e:
            logger.warning(f"Failed to decode Serato Markers2: {e}")
            return {}

    @staticmethod
    def decode_serato_beatgrid(data: bytes) -> Optional[BeatGrid]:
        """
        Decode Serato BeatGrid tag.
        Contains detailed beat position information including downbeats.
        Serato marks downbeats (bar starts) with special markers.
        """
        if not data:
            return None

        try:
            data = SeratoDecoder._unescape_serato_data(data)

            offset = 0

            # Parse header
            if len(data) < 4:
                return None

            version = struct.unpack('>I', data[offset:offset+4])[0]
            offset += 4

            if offset + 8 > len(data):
                return None

            # Number of markers (beats + downbeats)
            num_markers = struct.unpack('>I', data[offset:offset+4])[0]
            offset += 4

            # BPM (as float)
            bpm = struct.unpack('>f', data[offset:offset+4])[0]
            offset += 4

            beats = []
            downbeats = []
            first_downbeat = None

            # Parse beat markers
            # Serato uses a special format where every 4th beat (in 4/4) is marked as downbeat
            # The data includes flags for each beat marker
            beat_counter = 0

            for i in range(min(num_markers, 10000)):  # Limit to prevent memory issues
                if offset + 5 > len(data):  # 4 bytes position + 1 byte flags
                    break

                beat_position = struct.unpack('>f', data[offset:offset+4])[0]
                beat_position_sec = beat_position / 1000.0  # Convert to seconds
                offset += 4

                # Read beat flags (1 byte)
                if offset < len(data):
                    flags = data[offset]
                    offset += 1

                    # Check if this is a downbeat (bar start)
                    # Bit 0x01 usually indicates downbeat in Serato
                    is_downbeat = bool(flags & 0x01)

                    # Alternative: Check beat counter (every 4th beat in 4/4)
                    if beat_counter % 4 == 0:
                        is_downbeat = True
                else:
                    # Fallback: assume downbeat every 4 beats
                    is_downbeat = (beat_counter % 4 == 0)

                beats.append(beat_position_sec)

                if is_downbeat:
                    downbeats.append(beat_position_sec)
                    if first_downbeat is None:
                        first_downbeat = beat_position_sec

                beat_counter += 1

            # If no explicit downbeats found, calculate them from beats
            if not downbeats and beats:
                # Assume 4/4 time signature, downbeat every 4 beats
                downbeats = [beats[i] for i in range(0, len(beats), 4)]
                first_downbeat = downbeats[0] if downbeats else beats[0]

            if beats:
                return BeatGrid(
                    bpm=bpm,
                    first_beat_position=beats[0] if beats else 0,
                    first_downbeat_position=first_downbeat or beats[0],
                    beats=beats,
                    downbeats=downbeats,
                    bars_count=len(downbeats),
                    time_signature="4/4"  # Serato typically assumes 4/4
                )

            return None

        except Exception as e:
            logger.warning(f"Failed to decode Serato BeatGrid: {e}")
            return None

    @staticmethod
    def decode_serato_autotags(data: bytes) -> Dict[str, Any]:
        """
        Decode Serato Autotags.
        Contains auto-analyzed BPM, key, gain, etc.
        """
        if not data:
            return {}

        try:
            data = SeratoDecoder._unescape_serato_data(data)

            result = {}
            offset = 0

            # Parse as key-value pairs
            while offset < len(data) - 8:
                # Read key length
                if offset + 4 > len(data):
                    break

                key_len = struct.unpack('>I', data[offset:offset+4])[0]
                offset += 4

                if offset + key_len > len(data):
                    break

                key = data[offset:offset+key_len].decode('utf-8', errors='ignore')
                offset += key_len

                # Read value length
                if offset + 4 > len(data):
                    break

                val_len = struct.unpack('>I', data[offset:offset+4])[0]
                offset += 4

                if offset + val_len > len(data):
                    break

                value = data[offset:offset+val_len]
                offset += val_len

                # Parse known keys
                if key == "BPM" and val_len == 4:
                    result["auto_bpm"] = struct.unpack('>f', value)[0]
                elif key == "KEY":
                    result["auto_key"] = value.decode('utf-8', errors='ignore')
                elif key == "GAIN" and val_len == 4:
                    result["auto_gain"] = struct.unpack('>f', value)[0]

            return result

        except Exception as e:
            logger.warning(f"Failed to decode Serato Autotags: {e}")
            return {}

    @staticmethod
    def _unescape_serato_data(data: bytes) -> bytes:
        """
        Unescape Serato's custom encoding.
        Serato uses a form of SERATO_ESCAPE where 0x00 is escaped as 0xFF 0x00.
        """
        if not data:
            return data

        result = bytearray()
        i = 0
        while i < len(data):
            if data[i] == 0xFF and i + 1 < len(data) and data[i + 1] == 0x00:
                result.append(0x00)
                i += 2
            else:
                result.append(data[i])
                i += 1

        return bytes(result)

    @staticmethod
    def _parse_cue_entry(data: bytes) -> Optional[CuePoint]:
        """Parse a single cue entry."""
        try:
            if len(data) < 13:
                return None

            offset = 0

            # Index (1 byte)
            index = data[offset]
            offset += 1

            # Position in milliseconds (4 bytes, big-endian)
            position = struct.unpack('>I', data[offset:offset+4])[0]
            offset += 4

            # Color (1 byte, index into palette)
            color_index = data[offset] if offset < len(data) else 0
            offset += 1

            # Get color from palette
            color = SeratoDecoder.SERATO_COLORS.get(
                color_index % 16,
                "#CC0000"
            )

            # Name (if present)
            name = None
            if offset < len(data):
                name_data = data[offset:]
                # Find null terminator
                null_idx = name_data.find(b'\x00')
                if null_idx > 0:
                    name = name_data[:null_idx].decode('utf-8', errors='ignore')

            return CuePoint(
                index=index,
                position_ms=float(position),
                color=color,
                name=name,
                type="cue"
            )

        except Exception as e:
            logger.debug(f"Failed to parse cue entry: {e}")
            return None

    @staticmethod
    def _parse_loop_entry(data: bytes) -> Optional[Loop]:
        """Parse a single loop entry."""
        try:
            if len(data) < 8:
                return None

            offset = 0

            # Start position (4 bytes)
            start_pos = struct.unpack('>I', data[offset:offset+4])[0]
            offset += 4

            # End position (4 bytes)
            end_pos = struct.unpack('>I', data[offset:offset+4])[0]
            offset += 4

            # Color and flags
            color = "#00CC00"  # Default green for loops
            enabled = False

            if offset < len(data):
                flags = data[offset]
                enabled = bool(flags & 0x01)
                color_index = (flags >> 4) & 0x0F
                color = SeratoDecoder.SERATO_COLORS.get(color_index, "#00CC00")

            return Loop(
                start_position_ms=float(start_pos),
                end_position_ms=float(end_pos),
                color=color,
                enabled=enabled
            )

        except Exception as e:
            logger.debug(f"Failed to parse loop entry: {e}")
            return None

    @staticmethod
    def _parse_beatgrid_entry(data: bytes) -> Optional[BeatGrid]:
        """Parse beatgrid from markers2 including downbeats."""
        try:
            if len(data) < 8:
                return None

            offset = 0

            # BPM
            bpm = struct.unpack('>f', data[offset:offset+4])[0]
            offset += 4

            # First beat position
            first_beat = struct.unpack('>f', data[offset:offset+4])[0]
            offset += 4

            # Check for additional data (downbeat offset)
            first_downbeat = first_beat  # Default to first beat

            if offset + 4 <= len(data):
                # Serato sometimes includes downbeat offset
                downbeat_offset = struct.unpack('>f', data[offset:offset+4])[0]
                if downbeat_offset > 0:
                    first_downbeat = downbeat_offset
                offset += 4

            # Time signature (if present)
            time_sig = "4/4"
            if offset + 2 <= len(data):
                numerator = data[offset]
                denominator = data[offset + 1]
                if numerator > 0 and denominator > 0:
                    time_sig = f"{numerator}/{denominator}"

            return BeatGrid(
                bpm=bpm,
                first_beat_position=first_beat / 1000.0,
                first_downbeat_position=first_downbeat / 1000.0,
                beats=[],  # Will be populated from full beatgrid data
                downbeats=[],  # Will be populated from full beatgrid data
                time_signature=time_sig
            )

        except Exception as e:
            logger.debug(f"Failed to parse beatgrid entry: {e}")
            return None