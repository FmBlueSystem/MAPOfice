from __future__ import annotations

import csv
from pathlib import Path
from typing import Dict, Any

from src.services.storage import Storage


def import_mixedinkey_csv(csv_path: str | Path, storage: Storage, root_dir: str | None = None) -> int:
    """Import MixedInKey-like CSV metadata into the database.

    Tries to map flexible headers: path/location, bpm/tempo, initial key/key, camelot, energy/energy level, comments.
    Updates track DJ metadata without creating AnalysisResult records.
    Returns number of rows applied.
    """
    p = Path(csv_path)
    if not p.exists():
        raise FileNotFoundError(p)
    count = 0
    with p.open("r", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        for row in reader:
            low = { (k or "").strip().lower(): (v or "").strip() for k, v in row.items() }
            # Path resolution
            path = low.get("path") or low.get("file") or low.get("filename") or low.get("location") or low.get("file path") or low.get("file name")
            if not path:
                continue
            if root_dir and not path.startswith("/"):
                path = str(Path(root_dir) / path)
            meta: Dict[str, Any] = {}
            # BPM
            bpm = low.get("bpm") or low.get("tempo")
            try:
                if bpm:
                    meta["bpm"] = float(bpm)
            except Exception:
                pass
            # Keys
            meta["initial_key"] = low.get("initialkey") or low.get("initial key") or low.get("key")
            ck = low.get("camelot") or low.get("camelot key")
            if ck and ck.upper().endswith(("A","B")):
                meta["camelot_key"] = ck.upper()
            # Energy
            en = low.get("energylevel") or low.get("energy level") or low.get("energy")
            try:
                if en:
                    meta["energy_level"] = int(en)
            except Exception:
                pass
            # Comment
            meta["comment"] = low.get("comments") or low.get("comment")
            # Apply
            try:
                storage.update_track_dj_metadata(path, meta)
                count += 1
            except Exception:
                continue
    return count


def import_rekordbox_xml(xml_path: str | Path, storage: Storage, root_dir: str | None = None) -> int:
    """Import minimal metadata from Rekordbox XML collection.

    Extracts: Location/Path, AverageBpm, Tonality/InitialKey, Comments.
    """
    p = Path(xml_path)
    if not p.exists():
        raise FileNotFoundError(p)
    try:
        import xml.etree.ElementTree as ET
    except Exception as e:
        raise RuntimeError("XML parser not available") from e
    tree = ET.parse(p)
    root = tree.getroot()
    count = 0
    # Rekordbox XML tracks under COLLECTION/TRACK
    for tr in root.findall('.//TRACK'):
        loc = tr.get('Location') or tr.get('Path') or tr.get('Name')
        if not loc:
            continue
        path = loc
        if root_dir and not path.startswith('/'):
            path = str(Path(root_dir) / path)
        meta: Dict[str, Any] = {}
        bpm = tr.get('AverageBpm') or tr.get('Tempo')
        try:
            if bpm:
                meta['bpm'] = float(bpm)
        except Exception:
            pass
        key = tr.get('Tonality') or tr.get('InitialKey') or tr.get('Key')
        if key:
            meta['initial_key'] = key
        com = tr.get('Comments') or tr.get('Comment')
        if com:
            meta['comment'] = com
        try:
            storage.update_track_dj_metadata(path, meta)
            count += 1
        except Exception:
            continue
    return count


def import_traktor_nml(nml_path: str | Path, storage: Storage, root_dir: str | None = None) -> int:
    """Import minimal metadata from Traktor NML collection file.

    Extracts: FILE/@NAME, INFO/@KEY, INFO/@TEMPO or TEMPO/@BPM, COMMENTs.
    """
    p = Path(nml_path)
    if not p.exists():
        raise FileNotFoundError(p)
    try:
        import xml.etree.ElementTree as ET
    except Exception as e:
        raise RuntimeError("XML parser not available") from e
    tree = ET.parse(p)
    root = tree.getroot()
    count = 0
    for entry in root.findall('.//COLLECTION/ENTRY'):
        file_node = entry.find('LOCATION') or entry.find('FILE')
        path = None
        if file_node is not None:
            path = file_node.get('DIR') and (file_node.get('DIR') + (file_node.get('FILE') or ''))
            path = path or file_node.get('NAME')
        if not path:
            continue
        if root_dir and not path.startswith('/'):
            path = str(Path(root_dir) / path)
        meta: Dict[str, Any] = {}
        info = entry.find('INFO')
        if info is not None:
            key = info.get('KEY') or info.get('INITIALKEY')
            if key:
                meta['initial_key'] = key
            tempo = info.get('TEMPO')
            try:
                if tempo:
                    meta['bpm'] = float(tempo)
            except Exception:
                pass
        tempo_node = entry.find('TEMPO')
        if tempo_node is not None and 'BPM' in tempo_node.attrib:
            try:
                meta['bpm'] = float(tempo_node.get('BPM'))
            except Exception:
                pass
        comment_node = entry.find('COMMENT')
        if comment_node is not None and 'TEXT' in comment_node.attrib:
            meta['comment'] = comment_node.get('TEXT')
        try:
            storage.update_track_dj_metadata(path, meta)
            count += 1
        except Exception:
            continue
    return count
