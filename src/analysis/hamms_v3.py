"""HAMMS v3.0 - 12-Dimensional Harmonic Analysis System

This module implements the advanced HAMMS (Harmonic Analysis for Music Mixing System) v3.0
with 12-dimensional feature vectors for comprehensive music analysis and compatibility scoring.

Quality Gates:
- All vectors must be exactly 12 dimensions
- All values must be normalized to [0, 1] range
- No NaN or infinite values allowed
- Similarity scores must be between 0 and 1
"""

from __future__ import annotations

import json
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class HAMMSAnalyzerV3:
    """HAMMS v3.0 - 12-dimensional vector analysis system"""
    
    # HAMMS v3.0 dimension labels and descriptions
    DIMENSION_LABELS = {
        'bpm': 'BPM (Tempo)',
        'key': 'Key Signature', 
        'energy': 'Energy Level',
        'danceability': 'Danceability',
        'valence': 'Valence (Mood)',
        'acousticness': 'Acousticness',
        'instrumentalness': 'Instrumentalness',
        'rhythmic_pattern': 'Rhythmic Pattern',
        'spectral_centroid': 'Spectral Centroid',
        'tempo_stability': 'Tempo Stability',
        'harmonic_complexity': 'Harmonic Complexity',
        'dynamic_range': 'Dynamic Range'
    }
    
    # Dimension weights for similarity calculations
    DIMENSION_WEIGHTS = {
        'bpm': 1.3,              # Most important for mixing
        'key': 1.4,              # Critical for harmonic compatibility  
        'energy': 1.2,           # Essential for energy curves
        'danceability': 0.9,     # Important for club music
        'valence': 0.8,          # Mood component
        'acousticness': 0.6,     # Production style
        'instrumentalness': 0.5, # Vocal presence
        'rhythmic_pattern': 1.1, # Rhythm complexity
        'spectral_centroid': 0.7,# Brightness/timbre
        'tempo_stability': 0.9,  # Beat consistency
        'harmonic_complexity': 0.8, # Key complexity
        'dynamic_range': 0.6     # Dynamic variation
    }
    
    # Dimension names in order
    DIMENSION_NAMES = list(DIMENSION_WEIGHTS.keys())
    
    # Camelot wheel mapping
    CAMELOT_WHEEL = {
        'C': '8B', 'Am': '8A',
        'G': '9B', 'Em': '9A', 
        'D': '10B', 'Bm': '10A',
        'A': '11B', 'F#m': '11A',
        'E': '12B', 'C#m': '12A',
        'B': '1B', 'G#m': '1A',
        'Gb': '2B', 'Ebm': '2A',
        'Db': '3B', 'Bbm': '3A',
        'Ab': '4B', 'Fm': '4A',
        'Eb': '5B', 'Cm': '5A',
        'Bb': '6B', 'Gm': '6A',
        'F': '7B', 'Dm': '7A'
    }
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize HAMMS v3.0 analyzer
        
        Args:
            db_path: Optional database path for storage integration
        """
        self.db_path = db_path
        self.cache = {}
        self.cache_size = int(os.getenv('HAMMS_CACHE_SIZE', 1000))
        
    def calculate_extended_vector(self, track_data: Dict[str, Any]) -> np.ndarray:
        """Calculate 12-dimensional HAMMS vector for a track
        
        Args:
            track_data: Dictionary containing track metadata and analysis
            
        Returns:
            12-dimensional numpy array with normalized values [0, 1]
            
        Quality Gates:
            - Vector must have exactly 12 elements
            - All values must be 0-1 normalized
            - No NaN or inf values allowed
        """
        # Input validation
        if not isinstance(track_data, dict):
            raise TypeError(f"Track data must be dictionary, got {type(track_data)}")
        
        # Extract basic features with defaults
        bpm = track_data.get('bpm', 120.0)
        key = track_data.get('key', 'Am')
        energy = track_data.get('energy', 0.5)
        genre = track_data.get('genre', '').lower()
        
        # Calculate core dimensions (normalized to [0,1])
        norm_bpm = self._normalize_bpm(bpm)
        norm_key = self._camelot_to_numeric(key)
        norm_energy = np.clip(float(energy) if energy is not None else 0.5, 0, 1)
        
        # Calculate extended dimensions
        danceability = self._calculate_danceability(track_data)
        valence = self._calculate_valence(track_data) 
        acousticness = self._calculate_acousticness(track_data)
        instrumentalness = self._calculate_instrumentalness(track_data)
        rhythmic_pattern = self._calculate_rhythmic_pattern(track_data)
        spectral_centroid = self._calculate_spectral_centroid(track_data)
        tempo_stability = self._calculate_tempo_stability(track_data)
        harmonic_complexity = self._calculate_harmonic_complexity(track_data)
        dynamic_range = self._calculate_dynamic_range(track_data)
        
        # Create 12-dimensional vector
        vector = np.array([
            norm_bpm,           # 0: BPM normalized
            norm_key,           # 1: Camelot wheel position  
            norm_energy,        # 2: Energy level
            danceability,       # 3: Danceability factor
            valence,            # 4: Musical positivity
            acousticness,       # 5: Acoustic vs electronic
            instrumentalness,   # 6: Vocal vs instrumental
            rhythmic_pattern,   # 7: Rhythm complexity
            spectral_centroid,  # 8: Brightness/timbre
            tempo_stability,    # 9: Tempo consistency
            harmonic_complexity,# 10: Key complexity
            dynamic_range      # 11: Dynamic variation
        ], dtype=np.float64)
        
        # Quality gate validation
        assert len(vector) == 12, f"Vector must have 12 dimensions, got {len(vector)}"
        assert np.all((vector >= 0) & (vector <= 1)), f"All values must be 0-1, got {vector}"
        assert not np.any(np.isnan(vector)), f"No NaN values allowed, got {vector}"
        assert not np.any(np.isinf(vector)), f"No infinite values allowed, got {vector}"
        
        return vector
    
    def calculate_similarity(self, vector1: np.ndarray, vector2: np.ndarray) -> Dict[str, float]:
        """Calculate weighted similarity between two HAMMS vectors
        
        Args:
            vector1: First 12D HAMMS vector
            vector2: Second 12D HAMMS vector
            
        Returns:
            Dictionary with similarity metrics
            
        Quality Gates:
            - Both vectors must be 12-dimensional
            - Similarity scores must be between 0 and 1
        """
        # Input validation
        if not isinstance(vector1, np.ndarray) or not isinstance(vector2, np.ndarray):
            raise TypeError("Vectors must be numpy arrays")
        if len(vector1) != 12 or len(vector2) != 12:
            raise ValueError(f"Vectors must be 12-dimensional, got {len(vector1)} and {len(vector2)}")
        
        # Apply dimension weights
        weights = np.array(list(self.DIMENSION_WEIGHTS.values()), dtype=np.float64)
        weighted_v1 = vector1 * weights
        weighted_v2 = vector2 * weights
        
        # Euclidean distance (inverted to similarity)
        euclidean_dist = np.linalg.norm(weighted_v1 - weighted_v2)
        max_distance = np.linalg.norm(weights)  # Maximum possible distance
        euclidean_sim = 1.0 - (euclidean_dist / max_distance) if max_distance > 0 else 1.0
        
        # Cosine similarity  
        dot_product = np.dot(weighted_v1, weighted_v2)
        norm_v1 = np.linalg.norm(weighted_v1)
        norm_v2 = np.linalg.norm(weighted_v2)
        
        if norm_v1 > 0 and norm_v2 > 0:
            cosine_sim = dot_product / (norm_v1 * norm_v2)
        else:
            cosine_sim = 1.0 if np.array_equal(vector1, vector2) else 0.0
            
        # Overall similarity (weighted average)
        overall_similarity = euclidean_sim * 0.6 + cosine_sim * 0.4
        
        result = {
            'overall': float(np.clip(overall_similarity, 0, 1)),
            'euclidean': float(np.clip(euclidean_sim, 0, 1)),
            'cosine': float(np.clip(cosine_sim, -1, 1))  # Cosine can be negative
        }
        
        # Quality gate validation
        assert 0 <= result['overall'] <= 1, f"Overall similarity must be 0-1, got {result['overall']}"
        
        return result
    
    def get_compatible_tracks(self, seed_vector: np.ndarray, candidate_vectors: List[np.ndarray], 
                            threshold: float = 0.7, limit: int = 20) -> List[Tuple[int, float]]:
        """Get compatible tracks based on HAMMS similarity
        
        Args:
            seed_vector: 12D HAMMS vector of seed track
            candidate_vectors: List of 12D HAMMS vectors for candidates
            threshold: Minimum similarity threshold (0-1)
            limit: Maximum number of results to return
            
        Returns:
            List of tuples (index, similarity_score) sorted by similarity
        """
        if not isinstance(seed_vector, np.ndarray) or len(seed_vector) != 12:
            raise ValueError("Seed vector must be 12-dimensional numpy array")
            
        scored_candidates = []
        
        for i, candidate_vector in enumerate(candidate_vectors):
            if not isinstance(candidate_vector, np.ndarray) or len(candidate_vector) != 12:
                continue  # Skip invalid vectors
                
            similarity = self.calculate_similarity(seed_vector, candidate_vector)
            
            if similarity['overall'] >= threshold:
                scored_candidates.append((i, similarity['overall']))
        
        # Sort by similarity (highest first) and limit results
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        return scored_candidates[:limit]
    
    # Extended dimension calculation methods
    
    def _normalize_bpm(self, bpm: float) -> float:
        """Normalize BPM to 0-1 range (60-200 BPM)"""
        if bpm is None or bpm <= 0:
            return 0.5  # Default for unknown BPM
        return np.clip((float(bpm) - 60) / 140, 0, 1)
    
    def _camelot_to_numeric(self, key: str) -> float:
        """Convert key to Camelot wheel position (0-1)"""
        if not key:
            return 0.5  # Default for unknown key
            
        # Convert to Camelot if needed
        camelot_key = self.CAMELOT_WHEEL.get(key, key)
        
        # Parse Camelot notation (e.g., "8A", "12B")
        import re
        match = re.match(r'(\d+)([AB])', str(camelot_key).upper())
        if match:
            number = int(match.group(1))
            letter = match.group(2)
            
            # Map to 0-1 range: 1A-12A = 0.0-0.458, 1B-12B = 0.5-0.958
            base = (number - 1) / 12  # 0-0.916 for numbers 1-12
            if letter == 'B':
                base += 0.5
            return np.clip(base, 0, 1)
        
        return 0.5  # Default for unparseable keys
    
    def _calculate_danceability(self, track_data: Dict) -> float:
        """Calculate danceability based on genre, BPM, and energy"""
        genre = track_data.get('genre', '').lower()
        energy = track_data.get('energy', 0.5)
        bpm = track_data.get('bpm', 120)
        
        # Genre-based danceability mapping
        dance_genres = {
            'house': 0.9, 'techno': 0.95, 'trance': 0.8,
            'edm': 0.9, 'disco': 0.85, 'funk': 0.8,
            'electronic': 0.7, 'dance': 0.9, 'club': 0.85
        }
        
        base_danceability = dance_genres.get(genre, 0.5)
        
        # BPM influence (120-130 BPM optimal for dancing)
        if 110 <= bpm <= 140:
            bpm_factor = 1.0
        else:
            distance = min(abs(bpm - 110), abs(bpm - 140))
            bpm_factor = max(0.3, 1.0 - (distance / 50))
        
        # Energy influence
        danceability = base_danceability * float(energy or 0.5) * bpm_factor
        
        return np.clip(danceability, 0, 1)
    
    def _calculate_valence(self, track_data: Dict) -> float:
        """Calculate musical positivity/valence"""
        # If explicit valence available, use it
        if 'valence' in track_data and track_data['valence'] is not None:
            return np.clip(float(track_data['valence']), 0, 1)
        
        # Estimate from genre and key
        genre = track_data.get('genre', '').lower()
        key = track_data.get('key', '')
        
        # Genre influence on valence
        positive_genres = {
            'house': 0.8, 'disco': 0.9, 'funk': 0.8,
            'pop': 0.7, 'dance': 0.8, 'electronic': 0.6
        }
        negative_genres = {
            'darkwave': 0.2, 'industrial': 0.3, 'ambient': 0.4
        }
        
        genre_valence = positive_genres.get(genre, negative_genres.get(genre, 0.5))
        
        # Major keys tend to be more positive
        if 'B' in str(key):  # Major key in Camelot notation
            key_valence = 0.7
        elif 'A' in str(key):  # Minor key in Camelot notation
            key_valence = 0.4
        else:
            key_valence = 0.5
        
        # Combined valence
        valence = (genre_valence * 0.7 + key_valence * 0.3)
        
        return np.clip(valence, 0, 1)
    
    def _calculate_acousticness(self, track_data: Dict) -> float:
        """Calculate acoustic vs electronic character"""
        # If explicit acousticness available, use it
        if 'acousticness' in track_data and track_data['acousticness'] is not None:
            return np.clip(float(track_data['acousticness']), 0, 1)
        
        # Estimate from genre
        genre = track_data.get('genre', '').lower()
        
        acoustic_genres = {
            'folk': 0.9, 'acoustic': 0.95, 'country': 0.8,
            'classical': 0.9, 'jazz': 0.7
        }
        electronic_genres = {
            'house': 0.1, 'techno': 0.05, 'edm': 0.1,
            'electronic': 0.15, 'trance': 0.1, 'dubstep': 0.05
        }
        
        return acoustic_genres.get(genre, 1.0 - electronic_genres.get(genre, 0.5))
    
    def _calculate_instrumentalness(self, track_data: Dict) -> float:
        """Calculate instrumental vs vocal content"""
        # If explicit instrumentalness available, use it
        if 'instrumentalness' in track_data and track_data['instrumentalness'] is not None:
            return np.clip(float(track_data['instrumentalness']), 0, 1)
        
        # Estimate from genre and title
        genre = track_data.get('genre', '').lower()
        title = track_data.get('title', '').lower()
        
        # Genre influence
        instrumental_genres = {
            'ambient': 0.8, 'classical': 0.9, 'instrumental': 0.95,
            'post-rock': 0.7, 'soundtrack': 0.6
        }
        
        vocal_genres = {
            'pop': 0.1, 'rock': 0.2, 'r&b': 0.1, 'soul': 0.15
        }
        
        # Title keywords
        if any(word in title for word in ['instrumental', 'remix', 'mix', 'version']):
            title_factor = 0.3  # More likely instrumental
        else:
            title_factor = 0.0
        
        base = instrumental_genres.get(genre, 1.0 - vocal_genres.get(genre, 0.3))
        
        return np.clip(base + title_factor, 0, 1)
    
    def _calculate_rhythmic_pattern(self, track_data: Dict) -> float:
        """Calculate rhythmic complexity based on genre and BPM"""
        genre = track_data.get('genre', '').lower()
        bpm = track_data.get('bpm', 120)
        
        # Genre-based rhythm complexity
        rhythm_map = {
            'jazz': 0.9, 'prog': 0.8, 'techno': 0.8,
            'house': 0.7, 'trance': 0.6, 'ambient': 0.2,
            'pop': 0.4, 'rock': 0.5, 'classical': 0.7
        }
        
        base = rhythm_map.get(genre, 0.5)
        
        # BPM influence: faster typically more complex
        if bpm:
            bpm_factor = min(1.0, (float(bpm) - 60) / 140)
            return np.clip(base + (bpm_factor * 0.2), 0, 1)
        
        return base
    
    def _calculate_spectral_centroid(self, track_data: Dict) -> float:
        """Calculate brightness/timbre (spectral centroid)"""
        genre = track_data.get('genre', '').lower()
        energy = track_data.get('energy', 0.5)
        
        # Electronic genres typically have higher spectral centroid
        bright_genres = {
            'house': 0.7, 'techno': 0.8, 'trance': 0.75,
            'edm': 0.8, 'electronic': 0.7
        }
        
        dark_genres = {
            'ambient': 0.3, 'darkwave': 0.25, 'doom': 0.2
        }
        
        base = bright_genres.get(genre, 1.0 - dark_genres.get(genre, 0.5))
        
        # Energy influence on brightness
        energy_factor = float(energy or 0.5) * 0.3
        
        return np.clip(base + energy_factor, 0, 1)
    
    def _calculate_tempo_stability(self, track_data: Dict) -> float:
        """Calculate tempo consistency/stability"""
        # If explicit tempo stability available, use it
        if 'tempo_stability' in track_data and track_data['tempo_stability'] is not None:
            return np.clip(float(track_data['tempo_stability']), 0, 1)
        
        # Estimate from genre - electronic music typically more stable
        genre = track_data.get('genre', '').lower()
        
        stable_genres = {
            'house': 0.9, 'techno': 0.95, 'trance': 0.9,
            'edm': 0.85, 'electronic': 0.8
        }
        
        unstable_genres = {
            'jazz': 0.4, 'classical': 0.5, 'prog': 0.6
        }
        
        return stable_genres.get(genre, 1.0 - unstable_genres.get(genre, 0.3))
    
    def _calculate_harmonic_complexity(self, track_data: Dict) -> float:
        """Calculate harmonic complexity based on key and genre"""
        key = track_data.get('key', '')
        genre = track_data.get('genre', '').lower()
        
        # Minor keys generally more complex than major
        key_complexity = 0.6 if 'A' in str(key) else 0.4  # Camelot A = minor
        
        # Genre influence on harmonic complexity  
        complex_genres = {
            'jazz': 0.9, 'classical': 0.8, 'prog': 0.8,
            'fusion': 0.7, 'experimental': 0.8
        }
        
        simple_genres = {
            'pop': 0.3, 'house': 0.4, 'techno': 0.4
        }
        
        genre_complexity = complex_genres.get(genre, 1.0 - simple_genres.get(genre, 0.5))
        
        # Combined complexity
        return np.clip((key_complexity * 0.4 + genre_complexity * 0.6), 0, 1)
    
    def _calculate_dynamic_range(self, track_data: Dict) -> float:
        """Calculate dynamic range variation"""
        # If explicit dynamic range available, use it
        if 'dynamic_range' in track_data and track_data['dynamic_range'] is not None:
            return np.clip(float(track_data['dynamic_range']), 0, 1)
        
        # Estimate from genre and energy
        genre = track_data.get('genre', '').lower()
        energy = track_data.get('energy', 0.5)
        
        # Genres with typically high dynamic range
        dynamic_genres = {
            'classical': 0.9, 'jazz': 0.8, 'rock': 0.7,
            'metal': 0.6, 'ambient': 0.7
        }
        
        # Compressed genres (less dynamic range)
        compressed_genres = {
            'pop': 0.3, 'edm': 0.25, 'house': 0.3,
            'techno': 0.25
        }
        
        base = dynamic_genres.get(genre, 1.0 - compressed_genres.get(genre, 0.5))
        
        # High energy tracks might have more dynamic variation
        energy_factor = (1.0 - float(energy or 0.5)) * 0.2  # Inverse relationship
        
        return np.clip(base + energy_factor, 0, 1)
    
    def analyze_track(self, track_path: str) -> Dict[str, Any]:
        """Perform complete HAMMS v3.0 analysis on an audio track
        
        Args:
            track_path: Path to the audio file
            
        Returns:
            Dictionary with analysis results including HAMMS vector and metadata
        """
        try:
            # Import audio processing here to avoid circular imports
            from src.lib.audio_processing import analyze_track as basic_analyze
            from pathlib import Path
            
            # Perform basic audio analysis first (BPM, key, energy)
            basic_result = basic_analyze(track_path)
            
            # Create enhanced track data for HAMMS calculation
            track_data = {
                'bpm': basic_result.get('bpm', 120.0),
                'key': basic_result.get('key', 'Am'),
                'energy': basic_result.get('energy', 0.5),
                'genre': '',  # Will be filled by OpenAI if available
                'title': Path(track_path).stem,
                'artist': 'Unknown'
            }
            
            # Calculate 12-dimensional HAMMS vector
            hamms_vector = self.calculate_extended_vector(track_data)
            
            # Calculate dimension scores
            dimension_names = list(self.DIMENSION_LABELS.keys())
            dimension_scores = {}
            for i, dim_name in enumerate(dimension_names):
                if i < len(hamms_vector):
                    dimension_scores[dim_name] = float(hamms_vector[i])
            
            # Calculate confidence based on data quality
            confidence = self._calculate_confidence(track_data, hamms_vector)
            
            return {
                'success': True,
                'hamms_vector': hamms_vector.tolist(),
                'dimensions': dimension_scores,
                'confidence': confidence,
                'bpm': track_data['bpm'],
                'key': track_data['key'], 
                'energy': track_data['energy'],
                'title': track_data['title'],
                'artist': track_data['artist']
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'hamms_vector': [0.0] * 12,
                'dimensions': {},
                'confidence': 0.0
            }
    
    def _calculate_confidence(self, track_data: Dict[str, Any], hamms_vector: np.ndarray) -> float:
        """Calculate confidence score for HAMMS analysis"""
        confidence = 0.8  # Base confidence
        
        # Reduce confidence if basic analysis failed
        bpm = track_data.get('bpm')
        if bpm is None or bpm <= 0:
            confidence -= 0.2
        if not track_data.get('key'):
            confidence -= 0.1
        energy = track_data.get('energy')
        if energy is None or energy <= 0:
            confidence -= 0.1
            
        # Check for reasonable HAMMS vector values
        if np.any(np.isnan(hamms_vector)) or np.any(np.isinf(hamms_vector)):
            confidence = 0.0
        elif not np.all((hamms_vector >= 0) & (hamms_vector <= 1)):
            confidence *= 0.5
            
        return np.clip(confidence, 0.0, 1.0)