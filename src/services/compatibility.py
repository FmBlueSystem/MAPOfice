from __future__ import annotations

from typing import List, Dict, Any, Tuple, Optional


def parse_camelot(code: Optional[str]) -> Optional[Tuple[int, str]]:
    if not code:
        return None
    s = str(code).strip().upper()
    import re

    m = re.match(r"^(1[0-2]|[1-9])([AB])$", s)
    if not m:
        return None
    return (int(m.group(1)), m.group(2))


def camelot_distance(c1: Optional[str], c2: Optional[str]) -> Optional[float]:
    a = parse_camelot(c1)
    b = parse_camelot(c2)
    if not a or not b:
        return None
    n1, m1 = a
    n2, m2 = b
    ring = min(abs(n1 - n2), 12 - abs(n1 - n2))  # 0..6
    mode_penalty = 0.0 if m1 == m2 else 0.5  # relative major/minor is close
    return float(ring) + mode_penalty


def bpm_score(b1: Optional[float], b2: Optional[float]) -> float:
    if not b1 or not b2:
        return 0.5
    lo, hi = sorted([b1, b2])
    ratio = lo / hi
    # consider double/half tempo
    ratio2 = min(abs((2 * lo) / hi), abs(lo / (2 * hi)))
    best = max(ratio, ratio2)
    # Smooth mapping: within ±6% -> 1.0, ±8% -> 0.9, ±16% (double/half) -> 0.75, else decay
    if best >= 0.94:
        return 1.0
    if best >= 0.92:
        return 0.9
    if best >= 0.84:
        return 0.75
    if best >= 0.75:
        return 0.55
    return 0.2


def camelot_score(c1: Optional[str], c2: Optional[str]) -> float:
    d = camelot_distance(c1, c2)
    if d is None:
        return 0.5
    if d == 0:
        return 1.0
    # relative major/minor very close
    if d == 0.5:
        return 0.92
    if d <= 1.0:
        return 0.88
    if d <= 2.0:
        return 0.7
    if d <= 3.0:
        return 0.5
    return 0.2


def hamms_score(h1: List[float], h2: List[float]) -> float:
    # Fail-fast: validate HAMMS vectors
    if not isinstance(h1, list) or not isinstance(h2, list):
        raise TypeError("HAMMS vectors must be lists")
    if len(h1) != 12 or len(h2) != 12:
        raise ValueError(f"HAMMS vectors must be 12-dimensional, got {len(h1)} and {len(h2)}")
    if not h1 or not h2:
        return 0.5
    dist = sum(abs((a or 0.0) - (b or 0.0)) for a, b in zip(h1, h2))  # 0..2
    # invert and clamp to [0,1]
    s = max(0.0, 1.0 - dist / 2.0)
    return s


def energy_penalty(e1: Optional[float], e2: Optional[float]) -> float:
    if e1 is None or e2 is None:
        return 0.0
    return min(0.5, abs(e1 - e2) * 0.5)


def bpm_within_tolerance(b1: Optional[float], b2: Optional[float], tol: float = 0.08) -> bool:
    """Return True if tempos are within tolerance considering half/double tempo.
    tol is a ratio (e.g., 0.08 for ±8%).
    """
    if not b1 or not b2:
        return False
    
    # Calculate absolute difference as percentage of the first BPM
    diff_pct = abs(b1 - b2) / b1
    if diff_pct <= tol:
        return True
    
    # Consider double tempo (2x)
    diff_pct_double = abs(b1 - b2*2) / b1
    if diff_pct_double <= tol:
        return True
        
    # Consider half tempo (0.5x)
    diff_pct_half = abs(b1 - b2/2) / b1
    if diff_pct_half <= tol:
        return True
        
    # Consider reverse double/half relationships
    diff_pct_double2 = abs(b1*2 - b2) / (b1*2)
    if diff_pct_double2 <= tol:
        return True
        
    diff_pct_half2 = abs(b1/2 - b2) / (b1/2)
    if diff_pct_half2 <= tol:
        return True
    
    return False


def is_relative_major_minor(c1: Optional[str], c2: Optional[str]) -> bool:
    a = parse_camelot(c1)
    b = parse_camelot(c2)
    if not a or not b:
        return False
    n1, m1 = a
    n2, m2 = b
    return n1 == n2 and m1 != m2


def suggest_compatible(track: Dict[str, Any], candidates: List[Dict[str, Any]], limit: int = 10) -> List[Dict[str, Any]]:
    # Fail-fast: validate inputs
    if not isinstance(track, dict):
        raise TypeError("Track must be a dictionary")
    if not isinstance(candidates, list):
        raise TypeError("Candidates must be a list")
    if limit <= 0:
        raise ValueError("Limit must be positive")
    base_hamms = track.get("hamms") or [0.0] * 12
    base_key = track.get("camelot_key") or track.get("key")
    base_bpm = track.get("bpm")
    base_energy = track.get("energy")
    
    # CRITICAL: Reject seed track if it has no BPM
    if not base_bpm:
        print(f"ERROR: Seed track has no BPM calculated: {track.get('path', 'unknown')}")
        return []

    scored: List[Tuple[float, Dict[str, Any]]] = []
    for c in candidates:
        # CRITICAL: Skip candidates without BPM
        candidate_bpm = c.get("bpm")
        if not candidate_bpm:
            print(f"SKIPPING track without BPM: {c.get('path', 'unknown')}")
            continue
        h = c.get("hamms") or [0.0] * 12
        s_h = hamms_score(base_hamms, h)
        s_k = camelot_score(base_key, c.get("camelot_key") or c.get("key"))
        s_b = bpm_score(base_bpm, c.get("bpm"))
        pen_e = energy_penalty(base_energy, c.get("energy"))
        # weights: key 0.4, bpm 0.3, hamms 0.3 minus energy penalty
        score = 0.4 * s_k + 0.3 * s_b + 0.3 * s_h - pen_e
        scored.append((score, c))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [c for _, c in scored[:limit]]


def bpm_difference(b1: Optional[float], b2: Optional[float]) -> float:
    """Calculate BPM difference between two tracks.
    
    Returns the absolute difference in BPM, considering half/double tempo relationships.
    Returns 0.0 if either BPM is None.
    """
    if not b1 or not b2:
        return 0.0
    
    # Direct difference
    direct_diff = abs(b1 - b2)
    
    # Half/double tempo differences
    half_diff = min(abs(b1 - b2/2), abs(b1/2 - b2))
    double_diff = min(abs(b1 - b2*2), abs(b1*2 - b2))
    
    # Return the smallest meaningful difference
    return min(direct_diff, half_diff, double_diff)


def transition_score(a: Dict[str, Any], b: Dict[str, Any], prefer_rel: bool = False) -> float:
    """Composite score for transition a -> b using Camelot/BPM/HAMMS and energy penalty.

    Returns a value roughly in [0,1], higher is better.
    """
    # Fail-fast: validate input tracks
    if not isinstance(a, dict) or not isinstance(b, dict):
        raise TypeError("Track data must be dictionaries")
    
    # Fail-fast: require BPM for both tracks
    if not a.get("bpm") or not b.get("bpm"):
        raise ValueError(f"Both tracks must have BPM: {a.get('path', 'unknown')} -> {b.get('path', 'unknown')}")
    s_k = camelot_score(a.get("camelot_key") or a.get("key"), b.get("camelot_key") or b.get("key"))
    s_b = bpm_score(a.get("bpm"), b.get("bpm"))
    s_h = hamms_score(a.get("hamms") or [0.0] * 12, b.get("hamms") or [0.0] * 12)
    pen = energy_penalty(a.get("energy"), b.get("energy"))
    base = max(0.0, 0.4 * s_k + 0.3 * s_b + 0.3 * s_h - pen)
    if prefer_rel and is_relative_major_minor(a.get("camelot_key") or a.get("key"), b.get("camelot_key") or b.get("key")):
        base += 0.05
    return min(base, 1.0)
