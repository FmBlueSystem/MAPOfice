"""
Mixed In Key Metadata Decoder
Extracts cue points, energy levels, and musical analysis from Mixed In Key tags.

Mixed In Key stores data in ID3 comment fields and custom tags:
- COMM frame: Contains energy level, cue points, and key information
- TXXX frames: Custom user-defined text frames with MIK data
- TKEY: Musical key in standard notation
"""

import re
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class MixedInKeyCue:
    """Represents a Mixed In Key cue point."""
    position_ms: float
    type: str  # intro, outro, verse, chorus, break, drop, bridge
    energy: Optional[int] = None
    phrase: Optional[int] = None  # Phrase number (8-bar segments)
    name: Optional[str] = None


@dataclass
class MixedInKeyAnalysis:
    """Complete Mixed In Key analysis data."""
    key: Optional[str] = None
    camelot: Optional[str] = None
    energy: Optional[int] = None  # 1-10 scale
    cues: List[MixedInKeyCue] = None
    compatible_keys: List[str] = None
    danceability: Optional[int] = None  # 1-10 scale
    mood: Optional[str] = None  # Dark, Happy, Euphoric, Relaxed, etc.


class MixedInKeyDecoder:
    """Decodes Mixed In Key metadata from ID3 tags."""

    # Key compatibility wheel (Camelot system)
    CAMELOT_WHEEL = {
        "1A": ["12A", "1A", "2A", "1B"],   # Ab minor
        "1B": ["12B", "1B", "2B", "1A"],   # B major
        "2A": ["1A", "2A", "3A", "2B"],    # Eb minor
        "2B": ["1B", "2B", "3B", "2A"],    # Gb major
        "3A": ["2A", "3A", "4A", "3B"],    # Bb minor
        "3B": ["2B", "3B", "4B", "3A"],    # Db major
        "4A": ["3A", "4A", "5A", "4B"],    # F minor
        "4B": ["3B", "4B", "5B", "4A"],    # Ab major
        "5A": ["4A", "5A", "6A", "5B"],    # C minor
        "5B": ["4B", "5B", "6B", "5A"],    # Eb major
        "6A": ["5A", "6A", "7A", "6B"],    # G minor
        "6B": ["5B", "6B", "7B", "6A"],    # Bb major
        "7A": ["6A", "7A", "8A", "7B"],    # D minor
        "7B": ["6B", "7B", "8B", "7A"],    # F major
        "8A": ["7A", "8A", "9A", "8B"],    # A minor
        "8B": ["7B", "8B", "9B", "8A"],    # C major
        "9A": ["8A", "9A", "10A", "9B"],   # E minor
        "9B": ["8B", "9B", "10B", "9A"],   # G major
        "10A": ["9A", "10A", "11A", "10B"], # B minor
        "10B": ["9B", "10B", "11B", "10A"], # D major
        "11A": ["10A", "11A", "12A", "11B"], # F# minor
        "11B": ["10B", "11B", "12B", "11A"], # A major
        "12A": ["11A", "12A", "1A", "12B"],  # Db minor
        "12B": ["11B", "12B", "1B", "12A"],  # E major
    }

    @staticmethod
    def extract_from_comment(comment: str) -> MixedInKeyAnalysis:
        """
        Extract Mixed In Key data from ID3 comment field.
        MIK stores data in comments with specific patterns.
        """
        if not comment:
            return MixedInKeyAnalysis()

        analysis = MixedInKeyAnalysis(cues=[])

        # Extract energy level (Energy 1-10)
        energy_match = re.search(r'Energy\s*[:=]?\s*(\d{1,2})', comment, re.IGNORECASE)
        if energy_match:
            analysis.energy = int(energy_match.group(1))

        # Extract Camelot key (e.g., "8A", "12B")
        camelot_match = re.search(r'\b(1[0-2]|[1-9])[AB]\b', comment.upper())
        if camelot_match:
            analysis.camelot = camelot_match.group(0)
            analysis.compatible_keys = MixedInKeyDecoder.get_compatible_keys(analysis.camelot)

        # Extract cue points (format varies)
        # Format 1: "Cue 1: Intro (0:00)"
        cue_pattern1 = r'Cue\s*\d+:\s*(\w+)\s*\((\d+):(\d+)\)'
        for match in re.finditer(cue_pattern1, comment, re.IGNORECASE):
            cue_type = match.group(1).lower()
            minutes = int(match.group(2))
            seconds = int(match.group(3))
            position_ms = (minutes * 60 + seconds) * 1000

            cue = MixedInKeyCue(
                position_ms=position_ms,
                type=cue_type,
                name=match.group(1)
            )
            analysis.cues.append(cue)

        # Format 2: JSON embedded in comment (newer MIK versions)
        json_match = re.search(r'\{.*"cues".*\}', comment)
        if json_match:
            try:
                json_data = json.loads(json_match.group(0))
                analysis = MixedInKeyDecoder._parse_json_data(json_data, analysis)
            except json.JSONDecodeError:
                pass

        # Extract mood
        mood_patterns = [
            r'Mood:\s*(\w+)',
            r'Feeling:\s*(\w+)',
            r'Vibe:\s*(\w+)'
        ]
        for pattern in mood_patterns:
            mood_match = re.search(pattern, comment, re.IGNORECASE)
            if mood_match:
                analysis.mood = mood_match.group(1).capitalize()
                break

        # Extract danceability
        dance_match = re.search(r'Danceability\s*[:=]?\s*(\d{1,2})', comment, re.IGNORECASE)
        if dance_match:
            analysis.danceability = int(dance_match.group(1))

        return analysis

    @staticmethod
    def extract_from_txxx_frames(tags: Dict[str, Any]) -> MixedInKeyAnalysis:
        """
        Extract Mixed In Key data from TXXX (user-defined text) frames.
        MIK sometimes uses custom TXXX frames for structured data.
        """
        analysis = MixedInKeyAnalysis(cues=[])

        # Look for MIK-specific TXXX frames
        mik_frames = {
            'TXXX:MIK_KEY': 'key',
            'TXXX:MIK_ENERGY': 'energy',
            'TXXX:MIK_CUE_POINTS': 'cues',
            'TXXX:MIK_MOOD': 'mood',
            'TXXX:MIK_DANCEABILITY': 'danceability',
            'TXXX:INITIALKEY': 'key',
            'TXXX:ENERGY': 'energy',
        }

        for frame_key, attr_name in mik_frames.items():
            if frame_key in tags:
                value = tags[frame_key]
                if isinstance(value, list) and value:
                    value = value[0]

                if attr_name == 'energy' or attr_name == 'danceability':
                    try:
                        setattr(analysis, attr_name, int(str(value)))
                    except (ValueError, TypeError):
                        pass
                elif attr_name == 'cues':
                    # Parse cue points from TXXX frame
                    cues = MixedInKeyDecoder._parse_cue_string(str(value))
                    analysis.cues.extend(cues)
                else:
                    setattr(analysis, attr_name, str(value))

        # Convert key to Camelot if present
        if analysis.key and not analysis.camelot:
            analysis.camelot = MixedInKeyDecoder.key_to_camelot(analysis.key)
            if analysis.camelot:
                analysis.compatible_keys = MixedInKeyDecoder.get_compatible_keys(analysis.camelot)

        return analysis

    @staticmethod
    def _parse_json_data(json_data: Dict, analysis: MixedInKeyAnalysis) -> MixedInKeyAnalysis:
        """Parse JSON-formatted MIK data."""
        if 'energy' in json_data:
            analysis.energy = int(json_data['energy'])

        if 'key' in json_data:
            analysis.key = json_data['key']

        if 'camelot' in json_data:
            analysis.camelot = json_data['camelot']

        if 'cues' in json_data and isinstance(json_data['cues'], list):
            for cue_data in json_data['cues']:
                if isinstance(cue_data, dict):
                    cue = MixedInKeyCue(
                        position_ms=float(cue_data.get('position', 0)),
                        type=cue_data.get('type', 'unknown'),
                        energy=cue_data.get('energy'),
                        phrase=cue_data.get('phrase'),
                        name=cue_data.get('name')
                    )
                    analysis.cues.append(cue)

        if 'mood' in json_data:
            analysis.mood = json_data['mood']

        if 'danceability' in json_data:
            analysis.danceability = int(json_data['danceability'])

        return analysis

    @staticmethod
    def _parse_cue_string(cue_string: str) -> List[MixedInKeyCue]:
        """Parse cue points from a string format."""
        cues = []

        # Format: "Intro:0.0,Outro:240.5,Drop:60.0"
        parts = cue_string.split(',')
        for part in parts:
            if ':' in part:
                cue_type, position = part.split(':', 1)
                try:
                    position_sec = float(position)
                    cue = MixedInKeyCue(
                        position_ms=position_sec * 1000,
                        type=cue_type.lower().strip(),
                        name=cue_type.strip()
                    )
                    cues.append(cue)
                except ValueError:
                    continue

        return cues

    @staticmethod
    def key_to_camelot(key: str) -> Optional[str]:
        """Convert standard key notation to Camelot."""
        key_mapping = {
            # Major keys
            "C": "8B", "C major": "8B", "Cmaj": "8B",
            "Db": "3B", "Db major": "3B", "C#": "3B", "C# major": "3B",
            "D": "10B", "D major": "10B", "Dmaj": "10B",
            "Eb": "5B", "Eb major": "5B", "D#": "5B", "D# major": "5B",
            "E": "12B", "E major": "12B", "Emaj": "12B",
            "F": "7B", "F major": "7B", "Fmaj": "7B",
            "Gb": "2B", "Gb major": "2B", "F#": "2B", "F# major": "2B",
            "G": "9B", "G major": "9B", "Gmaj": "9B",
            "Ab": "4B", "Ab major": "4B", "G#": "4B", "G# major": "4B",
            "A": "11B", "A major": "11B", "Amaj": "11B",
            "Bb": "6B", "Bb major": "6B", "A#": "6B", "A# major": "6B",
            "B": "1B", "B major": "1B", "Bmaj": "1B",

            # Minor keys
            "Am": "8A", "A minor": "8A", "Amin": "8A",
            "Bbm": "3A", "Bb minor": "3A", "A#m": "3A", "A# minor": "3A",
            "Bm": "10A", "B minor": "10A", "Bmin": "10A",
            "Cm": "5A", "C minor": "5A", "Cmin": "5A",
            "C#m": "12A", "C# minor": "12A", "Dbm": "12A", "Db minor": "12A",
            "Dm": "7A", "D minor": "7A", "Dmin": "7A",
            "Ebm": "2A", "Eb minor": "2A", "D#m": "2A", "D# minor": "2A",
            "Em": "9A", "E minor": "9A", "Emin": "9A",
            "Fm": "4A", "F minor": "4A", "Fmin": "4A",
            "F#m": "11A", "F# minor": "11A", "Gbm": "11A", "Gb minor": "11A",
            "Gm": "6A", "G minor": "6A", "Gmin": "6A",
            "G#m": "1A", "G# minor": "1A", "Abm": "1A", "Ab minor": "1A",
        }

        # Clean the key string
        key_clean = key.strip()

        # Direct lookup
        if key_clean in key_mapping:
            return key_mapping[key_clean]

        # Try with 'major' or 'minor' suffix
        for suffix in ['', ' major', ' minor', 'maj', 'min', 'm']:
            test_key = key_clean + suffix
            if test_key in key_mapping:
                return key_mapping[test_key]

        return None

    @staticmethod
    def get_compatible_keys(camelot: str) -> List[str]:
        """Get harmonically compatible keys for a Camelot key."""
        if camelot in MixedInKeyDecoder.CAMELOT_WHEEL:
            return MixedInKeyDecoder.CAMELOT_WHEEL[camelot]
        return []

    @staticmethod
    def detect_phrase_structure(bpm: float, duration_ms: float) -> List[int]:
        """
        Detect phrase structure based on BPM and duration.
        Electronic music typically has 8-bar phrases.
        """
        if not bpm or bpm <= 0 or not duration_ms:
            return []

        # Calculate duration of 8 bars in milliseconds
        bar_duration_ms = (60000 / bpm) * 4  # 4 beats per bar
        phrase_duration_ms = bar_duration_ms * 8  # 8 bars per phrase

        phrases = []
        current_time = 0
        phrase_num = 1

        while current_time < duration_ms:
            phrases.append(int(current_time))
            current_time += phrase_duration_ms
            phrase_num += 1

        return phrases