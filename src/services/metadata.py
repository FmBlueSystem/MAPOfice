from __future__ import annotations

import re
import base64
import logging
from typing import Dict, Any, Optional, Tuple, List

# Import our new decoders
from src.services.serato_decoder import SeratoDecoder, CuePoint, BeatGrid, Loop
from src.services.mixedinkey_decoder import MixedInKeyDecoder, MixedInKeyCue

logger = logging.getLogger(__name__)


def extract_precomputed_metadata(path: str) -> Dict[str, Any]:
    """Extract precomputed DJ metadata including Serato and Mixed In Key data.

    - Uses mutagen if installed; otherwise returns {}.
    - For MP3 (ID3): TBPM, TKEY, COMM frames.
    - Serato tags: Markers_, Markers2, BeatGrid, Autotags
    - Mixed In Key: Energy levels, cue points, mood from comments and TXXX frames
    - Returns comprehensive metadata including beatgrid, cue points, loops, and more.
    """
    try:
        import mutagen  # type: ignore
    except Exception:
        return {}

    try:
        f = mutagen.File(path)
        if f is None or not hasattr(f, "tags") or f.tags is None:
            return {}
        # Normalize tag keys to lowercase for robust lookups
        raw_tags = f.tags
        # Mutagen mapping to dict-like may vary; coerce to dict of str->value
        tags = {}
        try:
            for k in raw_tags.keys():
                try:
                    v = raw_tags.get(k)
                except Exception:
                    v = raw_tags[k]
                tags[str(k).lower()] = v
        except Exception:
            tags = raw_tags or {}
        data: Dict[str, Any] = {}

        # BPM
        bpm_val = None
        for key in ("tbpm", "bpm"):
            if key in tags:
                try:
                    v = tags[key]
                    bpm_val = float(str(v[0] if isinstance(v, list) else v))
                    break
                except Exception:
                    pass
        if bpm_val is not None:
            data["bpm"] = bpm_val

        # Key (initial musical key)
        key_val = None
        for key in ("tkey", "initialkey", "initial_key", "initial key", "key"):
            if key in tags:
                try:
                    v = tags[key]
                    key_val = str(v[0] if isinstance(v, list) else v)
                    break
                except Exception:
                    pass
        if key_val:
            data["initial_key"] = key_val
            ck = to_camelot(key_val)
            if ck:
                data["camelot_key"] = ck

        # Camelot explicit tag if present
        for key in ("camelot", "camelot_key", "camelot key"):
            if key in tags and not data.get("camelot_key"):
                try:
                    v = tags[key]
                    cv = str(v[0] if isinstance(v, list) else v)
                    if re.match(r"^(?:[1-9]|1[0-2])[AB]$", cv.upper()):
                        data["camelot_key"] = cv.upper()
                except Exception:
                    pass

        # Comment (could contain energy or MixedInKey markers and Camelot)
        comment_text = None
        comment_text = None
        for ck in ("comm::xxx", "comm", "comment"):
            if ck in tags:
                try:
                    v = tags[ck]
                    comment_text = str(v[0] if isinstance(v, list) else v)
                    break
                except Exception:
                    continue
        if comment_text:
            data["comment"] = comment_text
            m = re.search(r"Energy\s*(\d{1,2})", comment_text, re.IGNORECASE)
            if m:
                try:
                    data["energy_level"] = int(m.group(1))
                except Exception:
                    pass
            # Camelot code in comment (e.g., "8A", "12B")
            m2 = re.search(r"\b(1[0-2]|[1-9])[AB]\b", comment_text.upper())
            if m2 and not data.get("camelot_key"):
                data["camelot_key"] = m2.group(0)
            # source hints & energy tag fallback
            if "mixedinkey" in comment_text.lower():
                data["analysis_source"] = "mixedinkey"
                data["source_confidence"] = 0.95
        # direct energy tag
        for ek in ("energylevel", "energy_level", "energy"):
            if ek in tags and "energy_level" not in data:
                try:
                    ev = tags[ek]
                    data["energy_level"] = int(str(ev[0] if isinstance(ev, list) else ev))
                except Exception:
                    pass

        # Extract Serato metadata
        serato_data = extract_serato_metadata(raw_tags)
        if serato_data:
            data["serato"] = serato_data
            # Merge Serato BPM if not already set
            if "bpm" in serato_data and "bpm" not in data:
                data["bpm"] = serato_data["bpm"]
            # Add beatgrid, cues, loops directly to top level for easy access
            if "beatgrid" in serato_data:
                data["beatgrid"] = serato_data["beatgrid"]
            if "cues" in serato_data:
                data["cue_points"] = serato_data["cues"]
            if "loops" in serato_data:
                data["loops"] = serato_data["loops"]

        # Extract Mixed In Key metadata
        mik_data = extract_mixedinkey_metadata(raw_tags, comment_text)
        if mik_data:
            data["mixedinkey"] = mik_data
            # Merge MIK data if not already set
            if mik_data.get("energy") and "energy_level" not in data:
                data["energy_level"] = mik_data["energy"]
            if mik_data.get("camelot") and "camelot_key" not in data:
                data["camelot_key"] = mik_data["camelot"]
            if mik_data.get("mood"):
                data["mood"] = mik_data["mood"]
            if mik_data.get("danceability"):
                data["danceability"] = mik_data["danceability"]
            # Merge cue points (MIK cues are more descriptive)
            if mik_data.get("cues") and not data.get("cue_points"):
                data["cue_points"] = mik_data["cues"]

        # Set analysis source based on what we found
        if "serato" in data and "mixedinkey" in data:
            data["analysis_source"] = "serato+mixedinkey"
            data["source_confidence"] = 0.99
        elif "serato" in data:
            data["analysis_source"] = "serato"
            data["source_confidence"] = 0.95
        elif "mixedinkey" in data:
            data["analysis_source"] = "mixedinkey"
            data["source_confidence"] = 0.95

        return data
    except Exception as e:
        logger.warning(f"Failed to extract metadata from {path}: {e}")
        return {}


def to_camelot(initial_key: str) -> Optional[str]:
    """Convert musical key strings to Camelot code (e.g., 'A minor' -> '8A').

    Supports variants: sharps/flats (G#/Ab), 'min'/'minor'/'m', 'maj'/'major'.
    If already Camelot (e.g., '8A') returns normalized uppercase.
    """
    if not initial_key:
        return None
    s = initial_key.strip().upper()
    import re

    if re.match(r"^(?:[1-9]|1[0-2])[AB]$", s):
        return s

    # Normalize symbols
    s = s.replace("♯", "#").replace("♭", "B")

    # Extract note and quality
    m = re.match(r"^\s*([A-G](?:#|B)?)\s*(MAJ|MAJOR|MIN|MINOR|M)?\s*$", s)
    if not m:
        # Try formats like 'F#M' / 'Gm'
        m = re.match(r"^\s*([A-G](?:#|B)?)(M|MIN|MINOR)?\s*$", s)
        if not m:
            return None
    note = m.group(1)
    qual = m.group(2) or "MAJ"
    is_minor = qual in ("M", "MIN", "MINOR")

    # Enharmonic map flats to sharps
    enh = {"DB": "C#", "EB": "D#", "GB": "F#", "AB": "G#", "BB": "A#"}
    note = enh.get(note, note)

    major_map = {
        "C": "8B", "G": "9B", "D": "10B", "A": "11B", "E": "12B", "B": "1B",
        "F#": "2B", "C#": "3B", "G#": "4B", "D#": "5B", "A#": "6B", "F": "7B",
    }
    minor_map = {
        "A": "8A", "E": "9A", "B": "10A", "F#": "11A", "C#": "12A", "G#": "1A",
        "D#": "2A", "A#": "3A", "F": "4A", "C": "5A", "G": "6A", "D": "7A",
    }

    return (minor_map if is_minor else major_map).get(note)


def extract_serato_metadata(tags: Dict) -> Dict[str, Any]:
    """Extract Serato-specific metadata from ID3 tags."""
    serato_data = {}
    decoder = SeratoDecoder()

    # Look for Serato GEOB frames
    serato_frames = {
        'GEOB:Serato Markers_': 'markers',
        'GEOB:Serato Markers2': 'markers2',
        'GEOB:Serato BeatGrid': 'beatgrid_raw',
        'GEOB:Serato Autotags': 'autotags',
        'GEOB:Serato OfflineAd': 'offline',
    }

    for frame_key in serato_frames:
        if frame_key in tags:
            try:
                # Get the frame data
                frame = tags[frame_key]
                if hasattr(frame, 'data'):
                    data = frame.data
                elif isinstance(frame, bytes):
                    data = frame
                else:
                    continue

                # Decode based on frame type
                if frame_key == 'GEOB:Serato Markers_':
                    result = decoder.decode_serato_markers(data)
                    if result and result.get('cues'):
                        serato_data['cues'] = result['cues']

                elif frame_key == 'GEOB:Serato Markers2':
                    result = decoder.decode_serato_markers2(data)
                    if result:
                        if result.get('cues'):
                            # Merge with existing cues or set new
                            if 'cues' in serato_data:
                                serato_data['cues'].extend(result['cues'])
                            else:
                                serato_data['cues'] = result['cues']
                        if result.get('loops'):
                            serato_data['loops'] = result['loops']
                        if result.get('beatgrid'):
                            serato_data['beatgrid'] = result['beatgrid']
                        if result.get('bpm'):
                            serato_data['bpm'] = result['bpm']

                elif frame_key == 'GEOB:Serato BeatGrid':
                    beatgrid = decoder.decode_serato_beatgrid(data)
                    if beatgrid:
                        serato_data['beatgrid'] = beatgrid
                        if beatgrid.bpm:
                            serato_data['bpm'] = beatgrid.bpm

                elif frame_key == 'GEOB:Serato Autotags':
                    autotags = decoder.decode_serato_autotags(data)
                    if autotags:
                        serato_data['autotags'] = autotags
                        if 'auto_bpm' in autotags and 'bpm' not in serato_data:
                            serato_data['bpm'] = autotags['auto_bpm']
                        if 'auto_key' in autotags:
                            serato_data['key'] = autotags['auto_key']

            except Exception as e:
                logger.debug(f"Failed to decode {frame_key}: {e}")
                continue

    return serato_data


def extract_mixedinkey_metadata(tags: Dict, comment_text: Optional[str] = None) -> Dict[str, Any]:
    """Extract Mixed In Key metadata from tags and comments."""
    decoder = MixedInKeyDecoder()
    mik_data = {}

    # First, analyze comment if available
    if comment_text:
        analysis = decoder.extract_from_comment(comment_text)
        if analysis.energy:
            mik_data['energy'] = analysis.energy
        if analysis.camelot:
            mik_data['camelot'] = analysis.camelot
        if analysis.mood:
            mik_data['mood'] = analysis.mood
        if analysis.danceability:
            mik_data['danceability'] = analysis.danceability
        if analysis.cues:
            mik_data['cues'] = analysis.cues
        if analysis.compatible_keys:
            mik_data['compatible_keys'] = analysis.compatible_keys

    # Then check TXXX frames for additional MIK data
    analysis_txxx = decoder.extract_from_txxx_frames(tags)

    # Merge TXXX data (prefer TXXX for structured data)
    if analysis_txxx.energy and 'energy' not in mik_data:
        mik_data['energy'] = analysis_txxx.energy
    if analysis_txxx.camelot and 'camelot' not in mik_data:
        mik_data['camelot'] = analysis_txxx.camelot
    if analysis_txxx.key:
        mik_data['key'] = analysis_txxx.key
    if analysis_txxx.mood and 'mood' not in mik_data:
        mik_data['mood'] = analysis_txxx.mood
    if analysis_txxx.danceability and 'danceability' not in mik_data:
        mik_data['danceability'] = analysis_txxx.danceability
    if analysis_txxx.cues and (not mik_data.get('cues') or len(analysis_txxx.cues) > len(mik_data.get('cues', []))):
        mik_data['cues'] = analysis_txxx.cues
    if analysis_txxx.compatible_keys and 'compatible_keys' not in mik_data:
        mik_data['compatible_keys'] = analysis_txxx.compatible_keys

    return mik_data
