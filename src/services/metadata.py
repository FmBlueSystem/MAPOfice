from __future__ import annotations

import re
from typing import Dict, Any, Optional, Tuple


def extract_precomputed_metadata(path: str) -> Dict[str, Any]:
    """Extract precomputed DJ metadata (BPM, key, energy, comment) from tags when available.

    - Uses mutagen if installed; otherwise returns {}.
    - For MP3 (ID3): TBPM, TKEY, COMM frames.
    - Energy level may be present in comments like "Energy 7" (MixedInKey style).
    - Returns keys: bpm, initial_key, camelot_key (if derivable), energy_level, comment, analysis_source, source_confidence.
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

        return data
    except Exception:
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
