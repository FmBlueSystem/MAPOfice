from __future__ import annotations

from typing import List, Dict, Any

from src.services.compatibility import (
    suggest_compatible,
    camelot_distance,
    bpm_score,
    transition_score,
    bpm_within_tolerance,
)
from src.lib.quality_gates import quality_gates, enforce_quality_gate
from src.analysis.enhanced_similarity import EnhancedSimilarityAnalyzer


def get_adaptive_tolerance(bpm: float) -> float:
    """Calculate adaptive BPM tolerance based on track tempo.
    
    Musical reasoning:
    - Slower tracks (< 90 BPM): More tolerance needed for transitions
    - Medium tracks (90-140 BPM): Standard tolerance works well  
    - Faster tracks (> 140 BPM): Can be more strict due to energy matching
    
    Args:
        bpm: Current track BPM
        
    Returns:
        Adaptive tolerance value (0.0-1.0)
    """
    if bpm <= 0:
        return 0.20  # Default fallback
    
    if bpm < 90:
        return 0.25  # 25% tolerance for slow tracks (ballads, downtempo)
    elif bpm < 110:
        return 0.20  # 20% tolerance for medium-slow tracks
    elif bpm < 140:
        return 0.15  # 15% tolerance for standard dance tracks
    else:
        return 0.12  # 12% tolerance for high-energy tracks
        

def calculate_transition_quality(bpm1: float, bpm2: float) -> float:
    """Calculate transition quality score between two BPMs.
    
    Returns score from 0.0 (bad) to 1.0 (perfect).
    Higher scores indicate smoother transitions.
    """
    if not bpm1 or not bpm2:
        return 0.0
    
    # Direct BPM ratio
    ratio = min(bpm1, bpm2) / max(bpm1, bpm2)
    
    # Check for harmonic relationships (2x, 1.5x, 3/4x, etc.)
    harmonic_ratios = [1.0, 0.5, 2.0, 0.75, 1.33, 0.67, 1.5, 0.8, 1.25]
    best_harmonic = 0.0
    
    for harmonic in harmonic_ratios:
        test_ratio = min(bpm1 * harmonic, bpm2) / max(bpm1 * harmonic, bpm2)
        if test_ratio > best_harmonic:
            best_harmonic = test_ratio
    
    return max(ratio, best_harmonic)


def validate_playlist_tolerance(playlist: List[Dict[str, Any]], tolerance: float) -> Dict[str, Any]:
    """Validate that playlist meets BPM tolerance requirements.
    
    Returns validation report with compliance statistics.
    """
    if len(playlist) < 2:
        return {"valid": True, "violations": 0, "total_transitions": 0, "compliance_rate": 100.0, "report": []}
    
    violations = []
    total_transitions = len(playlist) - 1
    
    for i in range(1, len(playlist)):
        prev_track = playlist[i-1]
        current_track = playlist[i]
        
        prev_bpm = prev_track.get('bpm')
        current_bpm = current_track.get('bpm')
        
        # CRITICAL: Both tracks must have BPM calculated
        if not prev_bpm or not current_bpm:
            violations.append({
                "position": i,
                "from_bpm": prev_bpm or "MISSING",
                "to_bpm": current_bpm or "MISSING", 
                "difference_pct": float('inf'),
                "allowed_pct": tolerance * 100,
                "error": "Missing BPM data"
            })
            continue
            
        if prev_bpm and current_bpm:
            # Calculate actual BPM difference percentage
            diff_pct = abs(current_bpm - prev_bpm) / prev_bpm * 100
            
            # Check if within tolerance (considering double/half tempo)
            within_tolerance = bpm_within_tolerance(prev_bpm, current_bpm, tolerance)
            
            if not within_tolerance:
                violations.append({
                    "position": i,
                    "from_bpm": prev_bpm,
                    "to_bpm": current_bpm,
                    "difference_pct": diff_pct,
                    "allowed_pct": tolerance * 100
                })
    
    compliance_rate = ((total_transitions - len(violations)) / total_transitions * 100) if total_transitions > 0 else 100.0
    
    return {
        "valid": len(violations) == 0,
        "violations": len(violations),
        "total_transitions": total_transitions,
        "compliance_rate": compliance_rate,
        "report": violations
    }


def energy_curve(length: int, mode: str = "ascending") -> List[float]:
    if length <= 0:
        return []
    if mode == "flat":
        return [0.5] * length
    if mode == "descending":
        return [max(0.0, 1.0 - i / max(1, length - 1)) for i in range(length)]
    # default ascending
    return [min(1.0, i / max(1, length - 1)) for i in range(length)]


@enforce_quality_gate("playlist_generation")
def generate_playlist(
    seed: Dict[str, Any],
    candidates: List[Dict[str, Any]],
    length: int = 10,
    curve: str = "ascending",
    bpm_tolerance: float = 0.15,
    prefer_relative: bool = False,
) -> List[Dict[str, Any]]:
    """Generate playlist with comprehensive quality gates.
    
    Quality Gates:
    1. Input validation: seed, candidates, parameters
    2. BPM requirement enforcement
    3. Progressive fallback with warnings
    4. Post-generation validation
    """
    # QUALITY GATE 1: Input validation
    if not isinstance(seed, dict):
        raise TypeError("Seed must be a dictionary")
    if not isinstance(candidates, list):
        raise TypeError("Candidates must be a list")
    if length <= 0:
        raise ValueError("Length must be positive")
    if not (0.0 < bpm_tolerance <= 1.0):
        raise ValueError("BPM tolerance must be between 0.0 and 1.0")
    
    # QUALITY GATE 2: BPM requirement enforcement
    seed_bpm = seed.get("bpm")
    if not seed_bpm:
        raise ValueError(f"Seed track missing BPM: {seed.get('path', 'unknown')}")
    
    # Filter candidates to only include tracks with BPM
    valid_candidates = [c for c in candidates if c.get("bpm")]
    rejected_count = len(candidates) - len(valid_candidates)
    if rejected_count > 0:
        print(f"QUALITY GATE: Rejected {rejected_count} tracks without BPM data")
    
    if not valid_candidates:
        raise ValueError("No valid candidates with BPM data available")
    if length <= 1:
        return [seed]
        
    # Use only valid candidates with BPM data
    plan = [seed]
    used = {seed.get("path")}
    curve_vals = energy_curve(length, curve)

    current = seed
    for i in range(1, length):
        pool = [c for c in valid_candidates if c.get("path") not in used]
        ranked = suggest_compatible(current, pool, limit=100)
        if not ranked:
            break
        # ENHANCED: Progressive BPM tolerance with musical intelligence
        filtered = []
        current_bpm = current.get("bpm", 0)
        
        # Step 1: Try strict tolerance with good key compatibility
        for r in ranked:
            dist = camelot_distance(current.get("camelot_key") or current.get("key"), r.get("camelot_key") or r.get("key"))
            ok_bpm = bpm_within_tolerance(current.get("bpm"), r.get("bpm"), tol=bpm_tolerance)
            if (dist is None or dist <= 2.0) and ok_bpm:
                filtered.append(r)
        
        # Step 2: If nothing found, try adaptive BPM tolerance (more permissive for different BPM ranges)
        if not filtered:
            adaptive_tolerance = get_adaptive_tolerance(current_bpm)
            print(f"Using adaptive BPM tolerance: {adaptive_tolerance*100:.1f}% for {current_bpm:.1f} BPM")
            for r in ranked:
                ok_bpm = bpm_within_tolerance(current.get("bpm"), r.get("bpm"), tol=adaptive_tolerance)
                if ok_bpm:
                    filtered.append(r)
        
        # Step 3: If still nothing, try excellent key compatibility with relaxed BPM
        if not filtered:
            for r in ranked:
                dist = camelot_distance(current.get("camelot_key") or current.get("key"), r.get("camelot_key") or r.get("key"))
                if dist is not None and dist <= 1.0:  # Perfect or relative major/minor only
                    filtered.append(r)
        
        # Only use unfiltered ranked list as LAST resort (and log warning)
        if not filtered:
            print(f"WARNING: No compatible tracks found. Using top-ranked candidates with BPM constraint bypass.")
            # Select only candidates that won't create jarring transitions (within 40% BPM difference)
            emergency_filtered = []
            for r in ranked[:10]:
                candidate_bpm = r.get("bpm", 0)
                if candidate_bpm > 0 and current_bpm > 0:
                    diff_pct = abs(candidate_bpm - current_bpm) / current_bpm
                    if diff_pct <= 0.4:  # 40% emergency threshold
                        emergency_filtered.append(r)
            cand_list = emergency_filtered[:3] if emergency_filtered else ranked[:2]
        else:
            cand_list = filtered

        # Choose candidate that best matches target energy while maximizing transition score
        target_energy = curve_vals[i] if i < len(curve_vals) else 0.5
        def energy_or(v):
            e = v.get("energy")
            return e if e is not None else 0.5
        cand_list.sort(key=lambda r: (abs(energy_or(r) - target_energy), -transition_score(current, r, prefer_rel=prefer_relative)))
        nxt = cand_list[0]
        plan.append(nxt)
        used.add(nxt.get("path"))
        current = nxt
    
    # Post-generation validation
    validation = validate_playlist_tolerance(plan, bpm_tolerance)
    
    # Print validation report
    print(f"\n=== PLAYLIST BPM TOLERANCE VALIDATION ===")
    print(f"Requested tolerance: ±{bpm_tolerance*100:.1f}%")
    print(f"Total transitions: {validation['total_transitions']}")
    print(f"Violations: {validation['violations']}")
    print(f"Compliance rate: {validation['compliance_rate']:.1f}%")
    
    if validation['violations'] > 0:
        print(f"❌ PLAYLIST FAILS BPM tolerance requirements!")
        for violation in validation['report']:
            print(f"  → Position {violation['position']}: {violation['from_bpm']:.1f} → {violation['to_bpm']:.1f} BPM "
                  f"({violation['difference_pct']:.1f}% > {violation['allowed_pct']:.1f}%)")
    else:
        print(f"✅ PLAYLIST COMPLIES with BPM tolerance requirements!")
    print("=" * 45)
    
    return plan


def cultural_context_score(track1: Dict[str, Any], track2: Dict[str, Any]) -> float:
    """Calculate cultural context similarity score between two tracks.
    
    Args:
        track1: First track with cultural_context data
        track2: Second track with cultural_context data
        
    Returns:
        Similarity score between 0.0 and 1.0
        
    Quality Gates:
        - Input validation for cultural_context structure
        - Safe handling of missing data
        - Score normalization
    """
    # Quality gate: Validate cultural context availability
    cultural1 = track1.get("cultural_context", {})
    cultural2 = track2.get("cultural_context", {})
    
    if not cultural1 or not cultural2:
        return 0.5  # Neutral score when data missing
    
    score = 0.0
    scoring_components = 0
    
    # 1. Club scenes similarity (40% weight)
    club_scenes1 = set(cultural1.get("club_scenes", []))
    club_scenes2 = set(cultural2.get("club_scenes", []))
    if club_scenes1 and club_scenes2:
        intersection = len(club_scenes1 & club_scenes2)
        union = len(club_scenes1 | club_scenes2)
        if union > 0:
            score += (intersection / union) * 0.4
            scoring_components += 0.4
    
    # 2. Production markers similarity (30% weight)
    production1 = set(cultural1.get("production_markers", []))
    production2 = set(cultural2.get("production_markers", []))
    if production1 and production2:
        intersection = len(production1 & production2)
        union = len(production1 | production2)
        if union > 0:
            score += (intersection / union) * 0.3
            scoring_components += 0.3
    
    # 3. Media formats overlap (20% weight)
    media1 = set(cultural1.get("media_formats", []))
    media2 = set(cultural2.get("media_formats", []))
    if media1 and media2:
        intersection = len(media1 & media2)
        union = len(media1 | media2)
        if union > 0:
            score += (intersection / union) * 0.2
            scoring_components += 0.2
    
    # 4. Distribution channels similarity (10% weight)
    distribution1 = set(cultural1.get("distribution_channels", []))
    distribution2 = set(cultural2.get("distribution_channels", []))
    if distribution1 and distribution2:
        intersection = len(distribution1 & distribution2)
        union = len(distribution1 | distribution2)
        if union > 0:
            score += (intersection / union) * 0.1
            scoring_components += 0.1
    
    # Normalize score based on available components
    if scoring_components > 0:
        score = score / scoring_components
    else:
        score = 0.5  # Default when no valid comparisons possible
    
    return max(0.0, min(1.0, score))


def lyrics_similarity_score(track1: Dict[str, Any], track2: Dict[str, Any]) -> float:
    """Calculate lyrics similarity score between two tracks.
    
    Args:
        track1: First track with lyrics data
        track2: Second track with lyrics data
        
    Returns:
        Similarity score between 0.0 and 1.0
        
    Quality Gates:
        - Input validation for lyrics structure
        - Language compatibility checking
        - Safe handling of missing lyrics data
        - Phrase overlap calculation
    """
    # Quality gate: Validate lyrics availability
    lyrics1 = track1.get("lyrics", {})
    lyrics2 = track2.get("lyrics", {})
    
    if not lyrics1 or not lyrics2:
        return 0.5  # Neutral score when data missing
    
    # Check if lyrics are available and confident enough
    if not lyrics1.get("available", False) or not lyrics2.get("available", False):
        return 0.5
    
    if lyrics1.get("confidence", 0.0) < 0.6 or lyrics2.get("confidence", 0.0) < 0.6:
        return 0.5
    
    score = 0.0
    scoring_components = 0
    
    # 1. Language compatibility (20% weight)
    lang1 = lyrics1.get("language", "unknown")
    lang2 = lyrics2.get("language", "unknown")
    if lang1 != "unknown" and lang2 != "unknown":
        if lang1 == lang2:
            score += 0.2
        else:
            # Different languages reduce compatibility
            score += 0.05
        scoring_components += 0.2
    
    # 2. Common phrases similarity (50% weight)
    phrases1 = set(lyrics1.get("common_phrases", []))
    phrases2 = set(lyrics2.get("common_phrases", []))
    if phrases1 and phrases2:
        intersection = len(phrases1 & phrases2)
        union = len(phrases1 | phrases2)
        if union > 0:
            phrase_similarity = intersection / union
            score += phrase_similarity * 0.5
            scoring_components += 0.5
    
    # 3. Rhyme seeds compatibility (30% weight)
    rhymes1 = set(lyrics1.get("rhyme_seeds", []))
    rhymes2 = set(lyrics2.get("rhyme_seeds", []))
    if rhymes1 and rhymes2:
        intersection = len(rhymes1 & rhymes2)
        union = len(rhymes1 | rhymes2)
        if union > 0:
            rhyme_similarity = intersection / union
            score += rhyme_similarity * 0.3
            scoring_components += 0.3
    
    # Normalize score based on available components
    if scoring_components > 0:
        score = score / scoring_components
    else:
        score = 0.5  # Default when no valid comparisons possible
    
    return max(0.0, min(1.0, score))


def cohesion_score(track1: Dict[str, Any], track2: Dict[str, Any]) -> float:
    """Calculate playlist cohesion score using OpenAI-generated cohesion data.
    
    Args:
        track1: First track with cultural_context.playlist_cohesion data
        track2: Second track with cultural_context.playlist_cohesion data
        
    Returns:
        Cohesion score between 0.0 and 1.0
        
    Quality Gates:
        - BPM band compatibility checking
        - Energy and valence window validation
        - Cohesive hooks similarity
        - Safe handling of missing cohesion data
    """
    # Quality gate: Extract cohesion data
    cohesion1 = track1.get("cultural_context", {}).get("playlist_cohesion", {})
    cohesion2 = track2.get("cultural_context", {}).get("playlist_cohesion", {})
    
    if not cohesion1 or not cohesion2:
        return 0.5  # Neutral score when data missing
    
    score = 0.0
    scoring_components = 0
    
    # 1. BPM band compatibility (40% weight)
    bpm_band1 = cohesion1.get("bpm_band", {})
    bpm_band2 = cohesion2.get("bpm_band", {})
    
    if bpm_band1 and bpm_band2:
        # Check if tracks can transition using cruise/lift/reset bands
        current_bpm = track1.get("bpm", 0)
        candidate_bpm = track2.get("bpm", 0)
        
        if current_bpm > 0 and candidate_bpm > 0:
            # Check if candidate BPM falls in any of current track's transition bands
            cruise_range = bpm_band1.get("cruise", [current_bpm-3, current_bpm+3])
            lift_range = bpm_band1.get("lift", [current_bpm+6, current_bpm+8])
            reset_range = bpm_band1.get("reset", [current_bpm-8, current_bpm-6])
            
            bpm_compatible = (
                cruise_range[0] <= candidate_bpm <= cruise_range[1] or
                lift_range[0] <= candidate_bpm <= lift_range[1] or
                reset_range[0] <= candidate_bpm <= reset_range[1]
            )
            
            score += (1.0 if bpm_compatible else 0.3) * 0.4
            scoring_components += 0.4
    
    # 2. Energy window compatibility (25% weight)
    energy_window1 = cohesion1.get("energy_window", [])
    energy_window2 = cohesion2.get("energy_window", [])
    
    if len(energy_window1) == 2 and len(energy_window2) == 2:
        track2_energy = track2.get("energy", 0.5)
        # Check if track2 energy falls within track1's preferred energy window
        if energy_window1[0] <= track2_energy <= energy_window1[1]:
            score += 0.25
        else:
            # Partial score based on how close it is
            distance = min(abs(track2_energy - energy_window1[0]), 
                          abs(track2_energy - energy_window1[1]))
            score += max(0.0, 0.25 * (1.0 - distance))
        scoring_components += 0.25
    
    # 3. Valence window compatibility (25% weight)
    valence_window1 = cohesion1.get("valence_window", [])
    valence_window2 = cohesion2.get("valence_window", [])
    
    if len(valence_window1) == 2 and len(valence_window2) == 2:
        track2_valence = track2.get("hamms", [0]*12)[4] if track2.get("hamms") else 0.5
        # Check if track2 valence falls within track1's preferred valence window
        if valence_window1[0] <= track2_valence <= valence_window1[1]:
            score += 0.25
        else:
            # Partial score based on how close it is
            distance = min(abs(track2_valence - valence_window1[0]), 
                          abs(track2_valence - valence_window1[1]))
            score += max(0.0, 0.25 * (1.0 - distance))
        scoring_components += 0.25
    
    # 4. Cohesive hooks similarity (10% weight)
    hooks1 = set(cohesion1.get("cohesive_hooks", []))
    hooks2 = set(cohesion2.get("cohesive_hooks", []))
    
    if hooks1 and hooks2:
        intersection = len(hooks1 & hooks2)
        union = len(hooks1 | hooks2)
        if union > 0:
            hooks_similarity = intersection / union
            score += hooks_similarity * 0.1
            scoring_components += 0.1
    
    # Normalize score based on available components
    if scoring_components > 0:
        score = score / scoring_components
    else:
        score = 0.5  # Default when no valid comparisons possible
    
    return max(0.0, min(1.0, score))


@enforce_quality_gate("enhanced_playlist_generation")
def generate_enhanced_playlist(
    seed: Dict[str, Any],
    candidates: List[Dict[str, Any]],
    length: int = 10,
    curve: str = "ascending",
    subgenre_weight: float = 0.20,
    hamms_weight: float = 0.30,
    era_weight: float = 0.15,
    mood_weight: float = 0.15,
    cultural_weight: float = 0.10,
    lyrics_weight: float = 0.10,
    bpm_tolerance: float = 0.15,
    enable_isrc_dedup: bool = True,
) -> List[Dict[str, Any]]:
    """Generate playlist using HAMMS v3.0, cultural context, and lyrics analysis.
    
    Args:
        seed: Seed track with HAMMS vector, subgenre, ISRC, cultural_context, lyrics, etc.
        candidates: Pool of candidate tracks
        length: Target playlist length
        curve: Energy curve ("ascending", "descending", "flat")
        subgenre_weight: Weight for subgenre compatibility (0-1)
        hamms_weight: Weight for HAMMS v3.0 similarity (0-1)
        era_weight: Weight for era compatibility (0-1)
        mood_weight: Weight for mood compatibility (0-1)
        cultural_weight: Weight for cultural context similarity (0-1)
        lyrics_weight: Weight for lyrics similarity (0-1)
        bpm_tolerance: BPM tolerance for transitions
        enable_isrc_dedup: Enable ISRC duplicate detection
        
    Returns:
        Enhanced playlist with cultural and lyrical coherence
        
    Quality Gates:
        - HAMMS v3.0 12-dimensional vector validation
        - Cultural context and lyrics data validation
        - ISRC duplicate detection and filtering
        - Enhanced similarity scoring with cultural/lyrics integration
        - Progressive fallback with detailed logging
    """
    # Initialize enhanced similarity analyzer
    similarity_analyzer = EnhancedSimilarityAnalyzer()
    
    # QUALITY GATE 1: Enhanced input validation
    if not isinstance(seed, dict):
        raise TypeError("Seed must be a dictionary")
    if not isinstance(candidates, list):
        raise TypeError("Candidates must be a list")
    if length <= 0:
        raise ValueError("Length must be positive")
    if not (0.0 < bpm_tolerance <= 1.0):
        raise ValueError("BPM tolerance must be between 0.0 and 1.0")
    
    # Validate weight parameters
    total_weights = subgenre_weight + hamms_weight + era_weight + mood_weight + cultural_weight + lyrics_weight
    if abs(total_weights - 1.0) > 0.1:
        print(f"WARNING: Weights sum to {total_weights:.2f}, not 1.0. Normalizing...")
        # Normalize weights
        subgenre_weight /= total_weights
        hamms_weight /= total_weights
        era_weight /= total_weights
        mood_weight /= total_weights
        cultural_weight /= total_weights
        lyrics_weight /= total_weights
    
    # QUALITY GATE 2: HAMMS vector validation
    seed_hamms = seed.get("hamms")
    if not seed_hamms or not isinstance(seed_hamms, list) or len(seed_hamms) != 12:
        raise ValueError(f"Seed track missing valid HAMMS v3.0 vector: {seed.get('path', 'unknown')}")
    
    # Filter candidates with valid HAMMS vectors
    valid_candidates = []
    rejected_count = 0
    
    for candidate in candidates:
        hamms = candidate.get("hamms")
        if not hamms or not isinstance(hamms, list) or len(hamms) != 12:
            rejected_count += 1
            continue
        if not candidate.get("bpm"):
            rejected_count += 1
            continue
        valid_candidates.append(candidate)
    
    if rejected_count > 0:
        print(f"QUALITY GATE: Rejected {rejected_count} tracks without valid HAMMS v3.0 vectors or BPM")
    
    # QUALITY GATE 2.5: Cultural context and lyrics data availability assessment
    cultural_available = 0
    lyrics_available = 0
    for candidate in valid_candidates:
        if candidate.get("cultural_context"):
            cultural_available += 1
        if candidate.get("lyrics", {}).get("available", False):
            lyrics_available += 1
    
    print(f"QUALITY GATE: Cultural context available for {cultural_available}/{len(valid_candidates)} tracks ({cultural_available/len(valid_candidates)*100:.1f}%)")
    print(f"QUALITY GATE: Lyrics data available for {lyrics_available}/{len(valid_candidates)} tracks ({lyrics_available/len(valid_candidates)*100:.1f}%)")
    
    # Adaptive weight adjustment based on data availability
    if cultural_available / len(valid_candidates) < 0.3:
        print(f"WARNING: Low cultural context availability, reducing cultural_weight from {cultural_weight:.2f} to {cultural_weight*0.5:.2f}")
        cultural_weight *= 0.5
    
    if lyrics_available / len(valid_candidates) < 0.3:
        print(f"WARNING: Low lyrics availability, reducing lyrics_weight from {lyrics_weight:.2f} to {lyrics_weight*0.5:.2f}")
        lyrics_weight *= 0.5
    
    # Re-normalize weights after adaptive adjustment
    total_adjusted_weights = subgenre_weight + hamms_weight + era_weight + mood_weight + cultural_weight + lyrics_weight
    if abs(total_adjusted_weights - 1.0) > 0.01:
        subgenre_weight /= total_adjusted_weights
        hamms_weight /= total_adjusted_weights
        era_weight /= total_adjusted_weights
        mood_weight /= total_adjusted_weights
        cultural_weight /= total_adjusted_weights
        lyrics_weight /= total_adjusted_weights
    
    if not valid_candidates:
        raise ValueError("No valid candidates with HAMMS vectors and BPM available")
    if length <= 1:
        return [seed]
    
    # QUALITY GATE 3: ISRC duplicate detection and filtering
    used_isrcs = set()
    if seed.get("isrc") and enable_isrc_dedup:
        used_isrcs.add(seed.get("isrc"))
    
    # Filter out ISRC duplicates from candidates
    if enable_isrc_dedup:
        filtered_candidates = []
        duplicate_count = 0
        for candidate in valid_candidates:
            candidate_isrc = candidate.get("isrc")
            if candidate_isrc and candidate_isrc in used_isrcs:
                duplicate_count += 1
                continue
            filtered_candidates.append(candidate)
        
        if duplicate_count > 0:
            print(f"QUALITY GATE: Filtered {duplicate_count} ISRC duplicates")
        valid_candidates = filtered_candidates
    
    # Initialize playlist
    playlist = [seed]
    used_paths = {seed.get("path")}
    curve_vals = energy_curve(length, curve)
    current_track = seed
    
    print(f"\n=== ENHANCED PLAYLIST GENERATION ===")
    print(f"Seed: {seed.get('artist', 'Unknown')} - {seed.get('title', 'Unknown')}")
    print(f"Subgenre: {seed.get('subgenre', 'Unknown')}, Era: {seed.get('era', 'Unknown')}")
    hamms_preview = [f'{x:.2f}' for x in seed_hamms[:4]]
    print(f"HAMMS Vector: {hamms_preview}...")
    print(f"Weights: Subgenre={subgenre_weight:.2f}, HAMMS={hamms_weight:.2f}, Era={era_weight:.2f}, Mood={mood_weight:.2f}, Cultural={cultural_weight:.2f}, Lyrics={lyrics_weight:.2f}")
    print("-" * 50)
    
    # Generate playlist using enhanced similarity
    for position in range(1, length):
        # Get available candidates (not already used)
        available_candidates = [
            c for c in valid_candidates 
            if c.get("path") not in used_paths
        ]
        
        # ENHANCED: If we run out of unique candidates, allow reuse but prefer unused ones
        if not available_candidates:
            print(f"INFO: No unused candidates at position {position}, allowing track reuse for better playlist completion")
            # Allow reuse of tracks, but still filter out the immediate previous track to avoid repetition
            if len(playlist) >= 2:
                previous_path = playlist[-1].get("path")
                available_candidates = [
                    c for c in valid_candidates 
                    if c.get("path") != previous_path
                ]
            else:
                available_candidates = valid_candidates
                
        if not available_candidates:
            print(f"ERROR: No candidates available at position {position}")
            break
        
        # Calculate enhanced similarity scores for all candidates
        candidate_scores = []
        target_energy = curve_vals[position] if position < len(curve_vals) else 0.5
        
        for candidate in available_candidates:
            try:
                # Use enhanced similarity algorithm
                similarity_result = similarity_analyzer.calculate_enhanced_similarity(
                    current_track, candidate
                )
                
                overall_score = similarity_result.get("overall", 0.0)
                hamms_score = similarity_result.get("hamms", 0.0)
                subgenre_score = similarity_result.get("subgenre", 0.0)
                era_score = similarity_result.get("era", 0.0)
                mood_score = similarity_result.get("mood", 0.0)
                bpm_score = similarity_result.get("bpm", 0.0)
                
                # Calculate cultural context and lyrics scores
                cultural_score = cultural_context_score(current_track, candidate)
                lyrics_score = lyrics_similarity_score(current_track, candidate)
                cohesion_bonus = cohesion_score(current_track, candidate)
                
                # Apply custom weights (base scoring)
                weighted_score = (
                    subgenre_score * subgenre_weight +
                    hamms_score * hamms_weight +
                    era_score * era_weight +
                    mood_score * mood_weight +
                    cultural_score * cultural_weight +
                    lyrics_score * lyrics_weight
                )
                
                # Energy curve matching bonus
                candidate_energy = candidate.get("energy", 0.5)
                energy_match = 1.0 - abs(candidate_energy - target_energy)
                
                # BPM compatibility check
                bpm_compatible = bpm_within_tolerance(
                    current_track.get("bpm"), candidate.get("bpm"), bpm_tolerance
                )
                bpm_penalty = 0.0 if bpm_compatible else 0.3
                
                # Apply cohesion bonus (additional 10% boost for highly cohesive tracks)
                cohesion_boost = cohesion_bonus * 0.1
                
                final_score = (weighted_score * 0.75 + energy_match * 0.15 + cohesion_boost) - bpm_penalty
                
                candidate_scores.append({
                    "track": candidate,
                    "final_score": final_score,
                    "overall_similarity": overall_score,
                    "hamms_similarity": hamms_score,
                    "subgenre_similarity": subgenre_score,
                    "era_similarity": era_score,
                    "mood_similarity": mood_score,
                    "cultural_similarity": cultural_score,
                    "lyrics_similarity": lyrics_score,
                    "cohesion_score": cohesion_bonus,
                    "bpm_similarity": bpm_score,
                    "energy_match": energy_match,
                    "bpm_compatible": bpm_compatible
                })
                
            except Exception as e:
                print(f"WARNING: Failed to calculate similarity for {candidate.get('path', 'unknown')}: {e}")
                continue
        
        if not candidate_scores:
            print(f"ERROR: No valid similarity scores calculated at position {position}")
            break
        
        # Sort by final score (descending)
        candidate_scores.sort(key=lambda x: x["final_score"], reverse=True)
        
        # CRITICAL FIX: Filter by BPM compatibility first to prevent tolerance violations
        compatible_candidates = [c for c in candidate_scores if c["bpm_compatible"]]
        
        if compatible_candidates:
            # Select best BMP-compatible candidate
            best_candidate_data = compatible_candidates[0]
        else:
            print(f"WARNING: No BPM-compatible candidates at position {position}, using best available")
            # Fallback to best candidate even if not BPM compatible
            best_candidate_data = candidate_scores[0]
            
        best_candidate = best_candidate_data["track"]
        
        # Add to playlist
        playlist.append(best_candidate)
        # Only add to used_paths if we have sufficient candidates to avoid reuse
        if len(valid_candidates) > length:
            used_paths.add(best_candidate.get("path"))
        
        # Track ISRC for deduplication
        if enable_isrc_dedup and best_candidate.get("isrc"):
            used_isrcs.add(best_candidate.get("isrc"))
        
        # Update current track for next iteration
        current_track = best_candidate
        
        # Log transition details with cultural and lyrics information
        print(f"Position {position}: {best_candidate.get('artist', 'Unknown')} - {best_candidate.get('title', 'Unknown')}")
        print(f"  Subgenre: {best_candidate.get('subgenre', 'Unknown')} (similarity: {best_candidate_data['subgenre_similarity']:.3f})")
        print(f"  HAMMS similarity: {best_candidate_data['hamms_similarity']:.3f}")
        print(f"  Era: {best_candidate.get('era', 'Unknown')} (similarity: {best_candidate_data['era_similarity']:.3f})")
        print(f"  Cultural similarity: {best_candidate_data['cultural_similarity']:.3f}")
        print(f"  Lyrics similarity: {best_candidate_data['lyrics_similarity']:.3f}")
        print(f"  Cohesion score: {best_candidate_data['cohesion_score']:.3f}")
        print(f"  BPM: {best_candidate.get('bpm', 0):.1f} (compatible: {best_candidate_data['bpm_compatible']})")
        print(f"  Final score: {best_candidate_data['final_score']:.3f}")
        print()
    
    # QUALITY GATE 4: Post-generation validation
    validation = validate_playlist_tolerance(playlist, bpm_tolerance)
    
    # Enhanced validation report
    print(f"=== ENHANCED PLAYLIST VALIDATION ===")
    print(f"Generated tracks: {len(playlist)}/{length}")
    print(f"BPM tolerance: ±{bpm_tolerance*100:.1f}%")
    print(f"Transitions: {validation['total_transitions']}")
    print(f"BPM violations: {validation['violations']}")
    print(f"Compliance rate: {validation['compliance_rate']:.1f}%")
    
    # Analyze subgenre diversity
    subgenres = [track.get("subgenre") for track in playlist if track.get("subgenre")]
    unique_subgenres = len(set(subgenres))
    print(f"Subgenre diversity: {unique_subgenres} unique subgenres")
    
    # Analyze era distribution
    eras = [track.get("era") for track in playlist if track.get("era")]
    unique_eras = len(set(eras))
    print(f"Era diversity: {unique_eras} unique eras")
    
    # ISRC deduplication report
    if enable_isrc_dedup:
        isrcs = [track.get("isrc") for track in playlist if track.get("isrc")]
        print(f"ISRC deduplication: {len(set(isrcs))} unique tracks")
    
    if validation['violations'] > 0:
        print(f"❌ PLAYLIST HAS BPM TOLERANCE VIOLATIONS!")
    else:
        print(f"✅ PLAYLIST COMPLIES with all quality gates!")
    
    print("=" * 45)
    
    return playlist
