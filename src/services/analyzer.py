from __future__ import annotations

from typing import Dict, Any, Optional

from src.lib.audio_processing import analyze_track
from src.lib.progress_callback import ProgressCallback
from src.services.storage import Storage
from src.services.metadata import extract_precomputed_metadata
from src.analysis.enhanced_similarity import EnhancedSimilarityAnalyzer
import os
import hashlib


class Analyzer:
    """Coordinates analysis of tracks and persists results via Storage."""

    def __init__(self, storage: Storage, *, compute_hash: bool = False):
        self.storage = storage
        self.compute_hash = compute_hash
        self.similarity_analyzer = EnhancedSimilarityAnalyzer()

    def analyze_path(self, path: str, progress_callback: Optional[ProgressCallback] = None) -> Dict[str, Any]:
        # Input validation
        if not isinstance(path, str) or not path.strip():
            raise ValueError("Path must be non-empty string")
        
        if not os.path.exists(path):
            raise FileNotFoundError(f"File not found: {path}")
        
        if not os.path.isfile(path):
            raise ValueError(f"Path is not a file: {path}")
        
        # Cache check by mtime
        try:
            mtime = os.path.getmtime(path)
        except (OSError, IOError) as e:
            print(f"WARNING: Could not get modification time for {path}: {e}")
            mtime = None
        if mtime is not None:
            cached = self.storage.get_cached_analysis(path, mtime)
            if cached:
                return cached

        # Prefer precomputed metadata when available
        pre = extract_precomputed_metadata(path)
        result = analyze_track(path, progress_callback=progress_callback)
        # Merge: pre tags take precedence for bpm/key/energy_level
        if "bpm" in pre:
            result["bpm"] = pre["bpm"]
        if pre.get("initial_key"):
            # store both key (for analysis_result) and initial_key as DJ meta
            result["key"] = pre["initial_key"]
            result["initial_key"] = pre["initial_key"]
        if pre.get("camelot_key"):
            result["camelot_key"] = pre["camelot_key"]
        if pre.get("energy_level") is not None:
            # Map energy_level (1-10) to energy (0-1) approximately
            try:
                lvl = int(pre["energy_level"]) 
                result["energy"] = max(0.0, min(1.0, lvl / 10.0))
            except (ValueError, TypeError) as e:
                print(f"WARNING: Invalid energy_level for {path}: {e}")
        if pre.get("comment"):
            result["comment"] = pre["comment"]
        if pre.get("analysis_source"):
            result["analysis_source"] = pre["analysis_source"]
        if pre.get("source_confidence") is not None:
            result["source_confidence"] = pre["source_confidence"]
        # Fill file cache metadata
        result["file_mtime"] = mtime
        # optional hash (expensive)
        if self.compute_hash:
            try:
                h = hashlib.sha1()
                with open(path, 'rb') as f:
                    for chunk in iter(lambda: f.read(8192), b''):
                        h.update(chunk)
                result["file_hash"] = h.hexdigest()
            except (OSError, IOError) as e:
                print(f"WARNING: Could not compute hash for {path}: {e}")

        self.storage.add_analysis(path, result)
        return result

    def find_similar_tracks(self, reference_path: str, limit: int = 10, 
                          min_confidence: float = 0.3) -> list[Dict[str, Any]]:
        """Find tracks similar to the reference track using enhanced similarity algorithm.
        
        Args:
            reference_path: Path to the reference track
            limit: Maximum number of similar tracks to return
            min_confidence: Minimum similarity confidence (0-1)
            
        Returns:
            List of similar tracks with similarity scores
        """
        # Get reference track analysis
        ref_analysis = self.storage.get_analysis_by_path(reference_path)
        if not ref_analysis:
            return []
        
        # Get all tracks from storage
        all_analyses = self.storage.list_all_analyses()
        
        # Filter out the reference track itself
        candidates = [a for a in all_analyses if a['path'] != reference_path]
        
        # Calculate similarity scores using enhanced algorithm
        similar_tracks = []
        for candidate in candidates:
            try:
                similarity_result = self.similarity_analyzer.calculate_enhanced_similarity(
                    ref_analysis, candidate
                )
                similarity_score = similarity_result.get('overall', 0.0)
                if similarity_score >= min_confidence:
                    candidate_with_score = candidate.copy()
                    candidate_with_score['similarity_score'] = similarity_score
                    similar_tracks.append(candidate_with_score)
            except Exception as e:
                print(f"WARNING: Failed to calculate similarity for {candidate.get('path', 'unknown')}: {e}")
                continue
        
        # Sort by similarity score (descending) and limit results
        similar_tracks.sort(key=lambda x: x['similarity_score'], reverse=True)
        return similar_tracks[:limit]

    def generate_enhanced_playlist(self, seed_paths: list[str], 
                                 target_length: int = 20,
                                 subgenre_focus: Optional[str] = None) -> list[Dict[str, Any]]:
        """Generate a playlist using enhanced similarity algorithm with subgenre awareness.
        
        Args:
            seed_paths: List of seed track paths to base playlist on
            target_length: Target number of tracks in playlist
            subgenre_focus: Optional subgenre to focus the playlist on
            
        Returns:
            List of tracks forming an optimized playlist
        """
        if not seed_paths:
            return []
            
        # Get seed track analyses
        seed_analyses = []
        for path in seed_paths:
            analysis = self.storage.get_analysis_by_path(path)
            if analysis:
                seed_analyses.append(analysis)
        
        if not seed_analyses:
            return []
        
        # Get all available tracks
        all_analyses = self.storage.list_all_analyses()
        
        # Filter by subgenre if specified
        if subgenre_focus:
            # This would require AI analysis data - for now, include all tracks
            # In future iterations, filter by subgenre from ai_analysis table
            pass
        
        # Use enhanced similarity algorithm to generate playlist
        try:
            playlist = self.similarity_analyzer.generate_smart_playlist(
                seed_analyses, all_analyses, target_length
            )
            return playlist
        except Exception as e:
            print(f"WARNING: Enhanced playlist generation failed: {e}")
            # Fallback to simple similarity-based selection
            return self._generate_simple_playlist(seed_analyses, all_analyses, target_length)
    
    def _generate_simple_playlist(self, seed_analyses: list[Dict[str, Any]], 
                                all_analyses: list[Dict[str, Any]], 
                                target_length: int) -> list[Dict[str, Any]]:
        """Fallback playlist generation using basic similarity."""
        playlist = seed_analyses.copy()
        candidates = [a for a in all_analyses if a['path'] not in [s['path'] for s in seed_analyses]]
        
        while len(playlist) < target_length and candidates:
            best_candidate = None
            best_score = -1
            
            # Find best candidate based on similarity to recent playlist additions
            recent_tracks = playlist[-3:]  # Consider last 3 tracks
            
            for candidate in candidates:
                avg_similarity = 0
                for recent in recent_tracks:
                    try:
                        similarity_result = self.similarity_analyzer.calculate_enhanced_similarity(
                            recent, candidate
                        )
                        avg_similarity += similarity_result.get('overall', 0.0)
                    except:
                        continue
                
                if recent_tracks:
                    avg_similarity /= len(recent_tracks)
                
                if avg_similarity > best_score:
                    best_score = avg_similarity
                    best_candidate = candidate
            
            if best_candidate and best_score > 0.2:  # Minimum similarity threshold
                playlist.append(best_candidate)
                candidates.remove(best_candidate)
            else:
                break
        
        return playlist

    def generate_enhanced_playlist_with_hamms(self, seed_path: str, target_length: int = 20,
                                            subgenre_focus: Optional[str] = None,
                                            curve: str = "ascending",
                                            subgenre_weight: float = 0.25,
                                            hamms_weight: float = 0.35,
                                            era_weight: float = 0.15,
                                            mood_weight: float = 0.15,
                                            bpm_tolerance: float = 0.15) -> list[Dict[str, Any]]:
        """Generate enhanced playlist using HAMMS v3.0 and full similarity analysis.
        
        Args:
            seed_path: Path to seed track
            target_length: Target playlist length
            subgenre_focus: Optional subgenre filter
            curve: Energy curve pattern
            subgenre_weight: Weight for subgenre compatibility
            hamms_weight: Weight for HAMMS v3.0 similarity
            era_weight: Weight for era compatibility
            mood_weight: Weight for mood compatibility
            bpm_tolerance: BPM tolerance for playlist generation (default 0.15 = 15%)
            
        Returns:
            Enhanced playlist with comprehensive analysis
        """
        # Import here to avoid circular imports
        from src.services.playlist import generate_enhanced_playlist
        
        # Get seed track analysis
        seed_analysis = self.storage.get_analysis_by_path(seed_path)
        if not seed_analysis:
            raise ValueError(f"No analysis found for seed track: {seed_path}")
        
        # Get candidates (all tracks or filtered by subgenre)
        if subgenre_focus:
            candidates = self.storage.get_tracks_with_ai_analysis(subgenre_filter=subgenre_focus)
        else:
            candidates = self.storage.list_all_analyses()
        
        # Generate enhanced playlist using HAMMS v3.0 algorithm
        enhanced_playlist = generate_enhanced_playlist(
            seed=seed_analysis,
            candidates=candidates,
            length=target_length,
            curve=curve,
            subgenre_weight=subgenre_weight,
            hamms_weight=hamms_weight,
            era_weight=era_weight,
            mood_weight=mood_weight,
            bpm_tolerance=bpm_tolerance,
            enable_isrc_dedup=True
        )
        
        return enhanced_playlist
