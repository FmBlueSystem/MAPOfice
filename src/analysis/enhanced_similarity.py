"""Enhanced Similarity Algorithm with Subgenre and ISRC Support

This module provides advanced similarity calculation that combines:
- HAMMS v3.0 12-dimensional vectors
- Genre and subgenre semantic similarity
- ISRC-based track identification and deduplication
- Era and mood compatibility factors

POML Quality Gates:
- Input validation for all similarity parameters
- Subgenre compatibility matrix validation
- ISRC format validation and duplicate detection
- Similarity score normalization and bounds checking
"""

from __future__ import annotations

import re
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass
import numpy as np

from .hamms_v3 import HAMMSAnalyzerV3


@dataclass
class EnhancedTrackData:
    """Enhanced track data with ISRC and subgenre information"""
    track_id: int
    path: str
    hamms_vector: List[float]
    
    # Basic metadata
    title: Optional[str] = None
    artist: Optional[str] = None
    bpm: Optional[float] = None
    key: Optional[str] = None
    energy: Optional[float] = None
    
    # AI-enhanced metadata
    genre: Optional[str] = None
    subgenre: Optional[str] = None
    mood: Optional[str] = None
    era: Optional[str] = None
    tags: List[str] = None
    
    # Professional metadata
    isrc: Optional[str] = None
    
    # Confidence scores
    hamms_confidence: float = 0.0
    ai_confidence: float = 0.0
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        # Validate ISRC format if provided
        if self.isrc and not self._validate_isrc(self.isrc):
            self.isrc = None
            
    def _validate_isrc(self, isrc: str) -> bool:
        """Validate ISRC format (XX-XXX-XX-XXXXX)"""
        pattern = r'^[A-Z]{2}-[A-Z0-9]{3}-\d{2}-\d{5}$'
        return bool(re.match(pattern, isrc.upper())) if isrc else False


class EnhancedSimilarityAnalyzer:
    """Enhanced similarity analysis with subgenre and ISRC support"""
    
    # Comprehensive subgenre compatibility matrix (0.0 = incompatible, 1.0 = perfect match)
    SUBGENRE_COMPATIBILITY = {
        # === ELECTRONIC MUSIC ===
        # House Family
        ('Deep House', 'Deep House'): 1.0,
        ('Deep House', 'Progressive House'): 0.85,
        ('Deep House', 'Tech House'): 0.75,
        ('Deep House', 'House'): 0.80,
        ('Deep House', 'Techno'): 0.60,
        ('Deep House', 'Trance'): 0.45,
        ('Deep House', 'Eurodance'): 0.30,
        
        ('Progressive House', 'Progressive House'): 1.0,
        ('Progressive House', 'Deep House'): 0.85,
        ('Progressive House', 'Tech House'): 0.80,
        ('Progressive House', 'Trance'): 0.75,
        ('Progressive House', 'House'): 0.85,
        
        ('Tech House', 'Tech House'): 1.0,
        ('Tech House', 'Techno'): 0.85,
        ('Tech House', 'Deep House'): 0.75,
        ('Tech House', 'Progressive House'): 0.80,
        
        # Techno Family
        ('Techno', 'Techno'): 1.0,
        ('Techno', 'Minimal Techno'): 0.90,
        ('Techno', 'Tech House'): 0.85,
        ('Techno', 'Industrial'): 0.70,
        ('Techno', 'Deep House'): 0.60,
        
        # Trance Family
        ('Trance', 'Trance'): 1.0,
        ('Trance', 'Progressive Trance'): 0.90,
        ('Trance', 'Uplifting Trance'): 0.85,
        ('Trance', 'Progressive House'): 0.75,
        ('Trance', 'Eurodance'): 0.65,
        
        # Eurodance Family
        ('Eurodance', 'Eurodance'): 1.0,
        ('Eurodance', 'Dance'): 0.85,
        ('Eurodance', 'Italo Disco'): 0.75,
        ('Eurodance', 'Hi-NRG'): 0.80,
        ('Eurodance', 'Trance'): 0.65,
        
        # === LATIN MUSIC ===
        # Reggaeton Family
        ('Reggaeton', 'Reggaeton'): 1.0,
        ('Reggaeton', 'Latin Trap'): 0.90,
        ('Reggaeton', 'Dembow'): 0.85,
        ('Reggaeton', 'Moombahton'): 0.70,
        ('Reggaeton', 'Hip-Hop'): 0.60,
        ('Reggaeton', 'Salsa'): 0.40,
        ('Reggaeton', 'Bachata'): 0.35,
        
        # Salsa Family
        ('Salsa', 'Salsa'): 1.0,
        ('Salsa', 'Salsa Romantica'): 0.95,
        ('Salsa', 'Salsa Dura'): 0.90,
        ('Salsa', 'Merengue'): 0.80,
        ('Salsa', 'Bachata'): 0.70,
        ('Salsa', 'Mambo'): 0.75,
        ('Salsa', 'Cha Cha'): 0.65,
        ('Salsa', 'Latin Jazz'): 0.60,
        
        # Bachata Family
        ('Bachata', 'Bachata'): 1.0,
        ('Bachata', 'Bachata Sensual'): 0.95,
        ('Bachata', 'Bachata Moderna'): 0.90,
        ('Bachata', 'Salsa'): 0.70,
        ('Bachata', 'Merengue'): 0.75,
        ('Bachata', 'Ballad'): 0.60,
        
        # Merengue Family
        ('Merengue', 'Merengue'): 1.0,
        ('Merengue', 'Salsa'): 0.80,
        ('Merengue', 'Bachata'): 0.75,
        ('Merengue', 'Cumbia'): 0.65,
        
        # === ROCK MUSIC ===
        # Classic Rock Family
        ('Classic Rock', 'Classic Rock'): 1.0,
        ('Classic Rock', 'Hard Rock'): 0.85,
        ('Classic Rock', 'Blues Rock'): 0.80,
        ('Classic Rock', 'Progressive Rock'): 0.70,
        ('Classic Rock', 'Southern Rock'): 0.75,
        
        # Alternative Rock Family
        ('Alternative Rock', 'Alternative Rock'): 1.0,
        ('Alternative Rock', 'Grunge'): 0.90,
        ('Alternative Rock', 'Indie Rock'): 0.85,
        ('Alternative Rock', 'Post-Rock'): 0.70,
        ('Alternative Rock', 'Punk Rock'): 0.65,
        
        # Metal Family
        ('Heavy Metal', 'Heavy Metal'): 1.0,
        ('Heavy Metal', 'Hard Rock'): 0.80,
        ('Heavy Metal', 'Thrash Metal'): 0.75,
        ('Heavy Metal', 'Death Metal'): 0.60,
        ('Heavy Metal', 'Black Metal'): 0.55,
        
        # === HIP-HOP MUSIC ===
        ('Hip-Hop', 'Hip-Hop'): 1.0,
        ('Hip-Hop', 'Rap'): 0.95,
        ('Hip-Hop', 'Trap'): 0.85,
        ('Hip-Hop', 'Old School Hip-Hop'): 0.80,
        ('Hip-Hop', 'Conscious Hip-Hop'): 0.90,
        ('Hip-Hop', 'Gangsta Rap'): 0.85,
        ('Hip-Hop', 'Latin Trap'): 0.70,
        ('Hip-Hop', 'Reggaeton'): 0.60,
        
        # Trap Family
        ('Trap', 'Trap'): 1.0,
        ('Trap', 'Hip-Hop'): 0.85,
        ('Trap', 'Latin Trap'): 0.80,
        ('Trap', 'Drill'): 0.75,
        
        # === POP MUSIC ===
        ('Pop', 'Pop'): 1.0,
        ('Pop', 'Dance Pop'): 0.85,
        ('Pop', 'Electropop'): 0.80,
        ('Pop', 'Teen Pop'): 0.90,
        ('Pop', 'Synth Pop'): 0.75,
        ('Pop', 'Latin Pop'): 0.70,
        
        # === R&B/SOUL ===
        ('R&B', 'R&B'): 1.0,
        ('R&B', 'Contemporary R&B'): 0.95,
        ('R&B', 'Neo Soul'): 0.85,
        ('R&B', 'Soul'): 0.90,
        ('R&B', 'Funk'): 0.75,
        ('R&B', 'Gospel'): 0.70,
        
        # === JAZZ ===
        ('Jazz', 'Jazz'): 1.0,
        ('Jazz', 'Smooth Jazz'): 0.85,
        ('Jazz', 'Latin Jazz'): 0.80,
        ('Jazz', 'Jazz Fusion'): 0.75,
        ('Jazz', 'Blues'): 0.70,
        ('Jazz', 'Bebop'): 0.90,
        
        # === REGGAE ===
        ('Reggae', 'Reggae'): 1.0,
        ('Reggae', 'Dancehall'): 0.85,
        ('Reggae', 'Dub'): 0.80,
        ('Reggae', 'Ska'): 0.70,
        
        # === COUNTRY ===
        ('Country', 'Country'): 1.0,
        ('Country', 'Country Rock'): 0.85,
        ('Country', 'Bluegrass'): 0.75,
        ('Country', 'Folk'): 0.70,
        
        # === CROSS-GENRE COMPATIBILITY ===
        # Electronic with other genres
        ('House', 'Disco'): 0.70,
        ('Techno', 'Industrial'): 0.75,
        ('Trance', 'Ambient'): 0.60,
        
        # Latin cross-compatibility
        ('Latin Pop', 'Pop'): 0.80,
        ('Latin Jazz', 'Jazz'): 0.85,
        ('Latin Trap', 'Trap'): 0.90,
        
        # Rock cross-compatibility
        ('Country Rock', 'Country'): 0.85,
        ('Blues Rock', 'Blues'): 0.90,
        ('Folk Rock', 'Folk'): 0.85,
    }
    
    # Era compatibility (tracks from similar eras mix better)
    ERA_COMPATIBILITY = {
        ('1990s', '1990s'): 1.0,
        ('1990s', '2000s'): 0.8,
        ('1990s', '1980s'): 0.7,
        ('2000s', '2000s'): 1.0,
        ('2000s', '2010s'): 0.9,
        ('2000s', '1990s'): 0.8,
        ('2010s', '2010s'): 1.0,
        ('2010s', '2020s'): 0.95,
        ('2010s', '2000s'): 0.9,
        ('2020s', '2020s'): 1.0,
        ('2020s', '2010s'): 0.95,
        ('Contemporary', 'Contemporary'): 1.0,
        ('Contemporary', '2020s'): 0.9,
        ('Contemporary', '2010s'): 0.85,
    }
    
    def __init__(self):
        """Initialize the enhanced similarity analyzer"""
        self.hamms_analyzer = HAMMSAnalyzerV3()
        
    def _dict_to_enhanced_track_data(self, track_dict: Dict[str, Any]) -> EnhancedTrackData:
        """Convert a dictionary to EnhancedTrackData object"""
        return EnhancedTrackData(
            track_id=track_dict.get('id', 0),
            path=track_dict.get('path', ''),
            hamms_vector=track_dict.get('hamms', [0.0] * 12),
            title=track_dict.get('title'),
            artist=track_dict.get('artist'),
            bpm=track_dict.get('bpm', 0.0),
            key=track_dict.get('key'),
            energy=track_dict.get('energy', 0.5),
            genre=track_dict.get('genre', 'Unknown'),
            subgenre=track_dict.get('subgenre', 'Unknown'),
            mood=track_dict.get('mood', 'Neutral'),
            era=track_dict.get('era', '2020s'),
            isrc=track_dict.get('isrc', ''),
            hamms_confidence=0.8  # Default confidence
        )

    def calculate_enhanced_similarity(self, track1: Union[EnhancedTrackData, Dict[str, Any]], 
                                    track2: Union[EnhancedTrackData, Dict[str, Any]]) -> Dict[str, float]:
        """Calculate enhanced similarity between two tracks
        
        Args:
            track1: First track data
            track2: Second track data
            
        Returns:
            Dictionary with detailed similarity scores
            
        Quality Gates:
            - HAMMS vector validation (12 dimensions)
            - ISRC duplicate detection
            - Subgenre compatibility validation
            - Final score normalization
        """
        # Convert dictionaries to EnhancedTrackData if needed
        if isinstance(track1, dict):
            track1 = self._dict_to_enhanced_track_data(track1)
        if isinstance(track2, dict):
            track2 = self._dict_to_enhanced_track_data(track2)
            
        # POML Quality Gate: Input validation
        if not self._validate_track_data(track1) or not self._validate_track_data(track2):
            return self._create_error_result("Invalid track data")
            
        # ISRC duplicate detection
        if track1.isrc and track2.isrc and track1.isrc == track2.isrc:
            return {
                'overall': 1.0,
                'hamms': 1.0,
                'subgenre': 1.0,
                'era': 1.0,
                'mood': 1.0,
                'duplicate_detected': True,
                'duplicate_type': 'ISRC_MATCH'
            }
            
        # Calculate base HAMMS similarity
        hamms_vector1 = np.array(track1.hamms_vector)
        hamms_vector2 = np.array(track2.hamms_vector)
        
        hamms_result = self.hamms_analyzer.calculate_similarity(hamms_vector1, hamms_vector2)
        hamms_similarity = hamms_result['overall']
        
        # Calculate subgenre compatibility
        subgenre_similarity = self._calculate_subgenre_similarity(track1, track2)
        
        # Calculate era compatibility
        era_similarity = self._calculate_era_similarity(track1, track2)
        
        # Calculate mood compatibility
        mood_similarity = self._calculate_mood_similarity(track1, track2)
        
        # BPM compatibility (for DJ mixing)
        bpm_similarity = self._calculate_bpm_compatibility(track1, track2)
        
        # Key compatibility (harmonic mixing)
        key_similarity = self._calculate_key_compatibility(track1, track2)
        
        # Weighted overall similarity
        weights = {
            'hamms': 0.35,      # Core HAMMS analysis
            'subgenre': 0.20,   # Subgenre compatibility
            'bpm': 0.15,        # BPM matching for transitions
            'key': 0.10,        # Harmonic compatibility
            'era': 0.10,        # Era consistency
            'mood': 0.10        # Mood matching
        }
        
        overall_similarity = (
            hamms_similarity * weights['hamms'] +
            subgenre_similarity * weights['subgenre'] +
            bpm_similarity * weights['bpm'] +
            key_similarity * weights['key'] +
            era_similarity * weights['era'] +
            mood_similarity * weights['mood']
        )
        
        # POML Quality Gate: Normalize final score
        overall_similarity = np.clip(overall_similarity, 0.0, 1.0)
        
        return {
            'overall': float(overall_similarity),
            'hamms': float(hamms_similarity),
            'subgenre': float(subgenre_similarity),
            'era': float(era_similarity),
            'mood': float(mood_similarity),
            'bpm': float(bpm_similarity),
            'key': float(key_similarity),
            'duplicate_detected': False,
            'confidence': float(min(track1.hamms_confidence, track2.hamms_confidence))
        }
        
    def _validate_track_data(self, track: EnhancedTrackData) -> bool:
        """Validate track data structure"""
        if not isinstance(track.hamms_vector, list) or len(track.hamms_vector) != 12:
            return False
        if not all(isinstance(v, (int, float)) for v in track.hamms_vector):
            return False
        if not all(0.0 <= v <= 1.0 for v in track.hamms_vector):
            return False
        return True
        
    def _create_error_result(self, error_msg: str) -> Dict[str, float]:
        """Create error result dictionary"""
        return {
            'overall': 0.0,
            'hamms': 0.0,
            'subgenre': 0.0,
            'era': 0.0,
            'mood': 0.0,
            'bmp': 0.0,
            'key': 0.0,
            'duplicate_detected': False,
            'error': error_msg
        }
        
    def _calculate_subgenre_similarity(self, track1: EnhancedTrackData, 
                                     track2: EnhancedTrackData) -> float:
        """Calculate subgenre compatibility score"""
        if not track1.subgenre or not track2.subgenre:
            # Fall back to genre comparison
            return self._calculate_genre_similarity(track1, track2)
            
        # Check direct compatibility
        key = (track1.subgenre, track2.subgenre)
        if key in self.SUBGENRE_COMPATIBILITY:
            return self.SUBGENRE_COMPATIBILITY[key]
            
        # Check reverse compatibility
        reverse_key = (track2.subgenre, track1.subgenre)
        if reverse_key in self.SUBGENRE_COMPATIBILITY:
            return self.SUBGENRE_COMPATIBILITY[reverse_key]
            
        # Same genre bonus if subgenres not in matrix
        if track1.genre and track2.genre and track1.genre == track2.genre:
            return 0.6  # Moderate compatibility within same genre
            
        return 0.3  # Low compatibility for different genres/unknown subgenres
        
    def _calculate_genre_similarity(self, track1: EnhancedTrackData, 
                                  track2: EnhancedTrackData) -> float:
        """Calculate basic genre similarity"""
        if not track1.genre or not track2.genre:
            return 0.5  # Neutral score for unknown genres
            
        if track1.genre == track2.genre:
            return 0.8  # High compatibility for same genre
        else:
            return 0.4  # Lower compatibility for different genres
            
    def _calculate_era_similarity(self, track1: EnhancedTrackData, 
                                track2: EnhancedTrackData) -> float:
        """Calculate era compatibility score"""
        if not track1.era or not track2.era:
            return 0.7  # Neutral score for unknown eras
            
        key = (track1.era, track2.era)
        if key in self.ERA_COMPATIBILITY:
            return self.ERA_COMPATIBILITY[key]
            
        reverse_key = (track2.era, track1.era)
        if reverse_key in self.ERA_COMPATIBILITY:
            return self.ERA_COMPATIBILITY[reverse_key]
            
        # Default compatibility for unknown era combinations
        return 0.5
        
    def _calculate_mood_similarity(self, track1: EnhancedTrackData, 
                                 track2: EnhancedTrackData) -> float:
        """Calculate mood compatibility score"""
        if not track1.mood or not track2.mood:
            return 0.7  # Neutral score for unknown moods
            
        # Simple mood matching (can be enhanced with mood categories)
        if track1.mood.lower() == track2.mood.lower():
            return 1.0
        
        # Mood category matching
        energetic_moods = ['energetic', 'uplifting', 'exciting', 'powerful']
        calm_moods = ['calm', 'peaceful', 'relaxed', 'chill']
        dark_moods = ['dark', 'mysterious', 'melancholic', 'intense']
        
        mood1_lower = track1.mood.lower()
        mood2_lower = track2.mood.lower()
        
        # Same mood category
        for mood_category in [energetic_moods, calm_moods, dark_moods]:
            if mood1_lower in mood_category and mood2_lower in mood_category:
                return 0.8
                
        return 0.4  # Different mood categories
        
    def _calculate_bpm_compatibility(self, track1: EnhancedTrackData, 
                                   track2: EnhancedTrackData) -> float:
        """Calculate BPM compatibility for DJ mixing"""
        if not track1.bpm or not track2.bpm:
            return 0.5  # Neutral score for unknown BPM
            
        bpm_diff = abs(track1.bpm - track2.bpm)
        
        # Perfect match
        if bpm_diff == 0:
            return 1.0
        # Excellent for DJ mixing (within 5 BPM)
        elif bpm_diff <= 5:
            return 0.9
        # Good for mixing (within 10 BPM)
        elif bpm_diff <= 10:
            return 0.8
        # Moderate (within 20 BPM - double/half time possible)
        elif bpm_diff <= 20:
            return 0.6
        # Difficult transition (large BPM difference)
        else:
            return 0.2
            
    def _calculate_key_compatibility(self, track1: EnhancedTrackData, 
                                   track2: EnhancedTrackData) -> float:
        """Calculate key compatibility for harmonic mixing"""
        if not track1.key or not track2.key:
            return 0.5  # Neutral score for unknown keys
            
        # Implement Camelot wheel compatibility
        camelot_compatibility = {
            # Perfect matches (same key)
            ('1A', '1A'): 1.0, ('1B', '1B'): 1.0,
            # Adjacent keys (compatible)
            ('1A', '2A'): 0.9, ('1A', '12A'): 0.9,
            ('1B', '2B'): 0.9, ('1B', '12B'): 0.9,
            # Relative major/minor
            ('1A', '1B'): 0.8, ('1B', '1A'): 0.8,
            # Add more Camelot wheel combinations...
        }
        
        # Try to get compatibility from Camelot system
        key_pair = (track1.key, track2.key)
        if key_pair in camelot_compatibility:
            return camelot_compatibility[key_pair]
            
        # Same key name
        if track1.key == track2.key:
            return 1.0
            
        return 0.4  # Default for unknown key combinations
        
    def find_similar_tracks(self, seed_track: EnhancedTrackData, 
                          candidate_tracks: List[EnhancedTrackData],
                          threshold: float = 0.7, limit: int = 20) -> List[Tuple[EnhancedTrackData, float]]:
        """Find tracks similar to seed track using enhanced similarity
        
        Args:
            seed_track: Track to find similar tracks for
            candidate_tracks: List of candidate tracks to compare
            threshold: Minimum similarity threshold (0-1)
            limit: Maximum number of results
            
        Returns:
            List of (track, similarity_score) tuples, sorted by similarity
        """
        similar_tracks = []
        
        for candidate in candidate_tracks:
            # Skip self-comparison
            if seed_track.track_id == candidate.track_id:
                continue
                
            similarity_result = self.calculate_enhanced_similarity(seed_track, candidate)
            overall_similarity = similarity_result['overall']
            
            if overall_similarity >= threshold:
                similar_tracks.append((candidate, overall_similarity))
                
        # Sort by similarity (highest first) and limit results
        similar_tracks.sort(key=lambda x: x[1], reverse=True)
        return similar_tracks[:limit]
        
    def generate_transition_sequence(self, tracks: List[EnhancedTrackData], 
                                   optimize_for: str = 'dj_set') -> List[EnhancedTrackData]:
        """Generate optimized track sequence for transitions
        
        Args:
            tracks: List of tracks to sequence
            optimize_for: 'dj_set', 'playlist', or 'album'
            
        Returns:
            Optimally ordered track list
        """
        if len(tracks) <= 1:
            return tracks
            
        # Start with highest energy or most popular track
        remaining = tracks.copy()
        sequence = [remaining.pop(0)]  # Start with first track
        
        while remaining:
            current_track = sequence[-1]
            best_next = None
            best_score = -1
            
            for candidate in remaining:
                similarity = self.calculate_enhanced_similarity(current_track, candidate)
                
                # Weight different factors based on optimization target
                if optimize_for == 'dj_set':
                    # Prioritize BPM and key compatibility
                    score = similarity['bmp'] * 0.4 + similarity['key'] * 0.3 + similarity['overall'] * 0.3
                elif optimize_for == 'playlist':
                    # Prioritize mood and subgenre flow
                    score = similarity['mood'] * 0.4 + similarity['subgenre'] * 0.3 + similarity['overall'] * 0.3
                else:  # album
                    # Prioritize overall artistic flow
                    score = similarity['overall']
                    
                if score > best_score:
                    best_score = score
                    best_next = candidate
                    
            if best_next:
                sequence.append(best_next)
                remaining.remove(best_next)
            else:
                # Add remaining tracks if no good transitions found
                sequence.extend(remaining)
                break
                
        return sequence