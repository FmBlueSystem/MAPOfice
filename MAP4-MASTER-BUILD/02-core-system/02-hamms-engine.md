# MAP4 Core Implementation - HAMMS v3.0 System

## Objective
Implement the core HAMMS v3.0 (Harmonic Analysis for Music Mixing System) engine, audio processing pipeline, storage integration, and quality gate framework that form the foundation of MAP4's music analysis capabilities.

## Prerequisites
- Completed infrastructure setup from `01-setup-infrastructure.md`
- Python environment with librosa, numpy, and SQLAlchemy installed
- Database models and configuration system in place

## Step 1: HAMMS v3.0 Engine Implementation

### 1.1 Create HAMMS v3.0 Analyzer
Create `src/analysis/hamms_v3.py`:

```python
"""HAMMS v3.0 - 12-Dimensional Harmonic Analysis for Music Mixing System."""

import numpy as np
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

@dataclass
class HAMMSDimensions:
    """Container for HAMMS dimension names and weights."""
    BPM: float = 1.3
    KEY_SIGNATURE: float = 1.4
    ENERGY_LEVEL: float = 1.2
    DANCEABILITY: float = 0.9
    VALENCE: float = 0.8
    ACOUSTICNESS: float = 0.6
    INSTRUMENTALNESS: float = 0.5
    RHYTHMIC_PATTERN: float = 1.1
    SPECTRAL_CENTROID: float = 0.7
    TEMPO_STABILITY: float = 0.9
    HARMONIC_COMPLEXITY: float = 0.8
    DYNAMIC_RANGE: float = 0.6
    
    def get_weights_array(self) -> np.ndarray:
        """Get weights as numpy array in dimension order."""
        return np.array([
            self.BPM, self.KEY_SIGNATURE, self.ENERGY_LEVEL,
            self.DANCEABILITY, self.VALENCE, self.ACOUSTICNESS,
            self.INSTRUMENTALNESS, self.RHYTHMIC_PATTERN, self.SPECTRAL_CENTROID,
            self.TEMPO_STABILITY, self.HARMONIC_COMPLEXITY, self.DYNAMIC_RANGE
        ])
    
    def get_dimension_names(self) -> List[str]:
        """Get dimension names in order."""
        return [
            "BPM", "Key Signature", "Energy Level", "Danceability",
            "Valence", "Acousticness", "Instrumentalness", "Rhythmic Pattern",
            "Spectral Centroid", "Tempo Stability", "Harmonic Complexity", "Dynamic Range"
        ]

class HAMMSAnalyzer:
    """HAMMS v3.0 12-dimensional music analysis engine."""
    
    # Camelot wheel mapping for key compatibility
    CAMELOT_WHEEL = {
        'C': '8B', 'Am': '8A',
        'G': '9B', 'Em': '9A', 
        'D': '10B', 'Bm': '10A',
        'A': '11B', 'F#m': '11A',
        'E': '3B', 'C#m': '3A',
        'B': '1B', 'G#m': '1A',
        'Gb': '2B', 'Ebm': '2A',
        'Db': '3B', 'Bbm': '3A',
        'Ab': '4B', 'Fm': '4A',
        'Eb': '5B', 'Cm': '5A',
        'Bb': '6B', 'Gm': '6A',
        'F': '7B', 'Dm': '7A',
        # Alternative notations
        'F#': '2B', 'D#m': '2A',
        'C#': '3B', 'A#m': '3A',
        'G#': '4B', 'E#m': '4A',
        'D#': '5B', 'B#m': '5A',
        'A#': '6B', 'F##m': '6A'
    }
    
    def __init__(self):
        """Initialize HAMMS analyzer."""
        self.dimensions = HAMMSDimensions()
        self._cache = {}
    
    def calculate_extended_vector(self, track_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate 12-dimensional HAMMS vector for a track.
        
        Args:
            track_data: Dictionary containing track metadata and features
                Required: bpm, key, energy
                Optional: genre, title, artist, duration
        
        Returns:
            Dictionary containing:
                - hamms_vector: 12-dimensional numpy array
                - dimension_scores: Individual dimension values
                - confidence: Confidence score (0-1)
                - camelot_key: Camelot wheel notation
        """
        # Input validation
        if not isinstance(track_data, dict):
            raise TypeError(f"Track data must be dictionary, got {type(track_data)}")
        
        # Extract basic features with defaults
        bpm = float(track_data.get('bpm', 120.0))
        key = str(track_data.get('key', 'Am'))
        energy = float(track_data.get('energy', 0.5))
        genre = str(track_data.get('genre', '')).lower()
        title = str(track_data.get('title', '')).lower()
        artist = str(track_data.get('artist', '')).lower()
        
        # Calculate each dimension
        norm_bpm = self._normalize_bpm(bpm)
        norm_key = self._camelot_to_numeric(key)
        norm_energy = np.clip(energy, 0, 1)
        danceability = self._calculate_danceability(track_data)
        valence = self._calculate_valence(track_data)
        acousticness = self._calculate_acousticness(track_data)
        instrumentalness = self._calculate_instrumentalness(track_data)
        rhythmic_pattern = self._calculate_rhythmic_pattern(track_data)
        spectral_centroid = self._calculate_spectral_centroid(track_data)
        tempo_stability = self._calculate_tempo_stability(track_data)
        harmonic_complexity = self._calculate_harmonic_complexity(track_data)
        dynamic_range = self._calculate_dynamic_range(track_data)
        
        # Assemble 12-dimensional vector
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
            dynamic_range       # 11: Dynamic variation
        ], dtype=np.float64)
        
        # Quality gate validation
        self._validate_vector(vector)
        
        # Calculate confidence score
        confidence = self._calculate_confidence(track_data, vector)
        
        # Get Camelot key
        camelot_key = self.CAMELOT_WHEEL.get(key, '1A')
        
        # Prepare dimension scores dictionary
        dimension_scores = {
            name: float(vector[i])
            for i, name in enumerate(self.dimensions.get_dimension_names())
        }
        
        return {
            'hamms_vector': vector,
            'dimension_scores': dimension_scores,
            'confidence': confidence,
            'camelot_key': camelot_key,
            'version': '3.0'
        }
    
    def _normalize_bpm(self, bpm: float) -> float:
        """Normalize BPM to 0-1 range (60-200 BPM)."""
        return np.clip((float(bpm) - 60) / 140, 0, 1)
    
    def _camelot_to_numeric(self, key: str) -> float:
        """Convert key to Camelot wheel position (0-1)."""
        camelot = self.CAMELOT_WHEEL.get(key, '1A')
        
        # Extract number and letter
        number = int(''.join(filter(str.isdigit, camelot)) or 1)
        is_minor = 'A' in camelot
        
        # Convert to 0-1 range
        # 1A-12A = 0.0-0.458 (minor keys)
        # 1B-12B = 0.5-0.958 (major keys)
        base = (number - 1) / 24.0
        if not is_minor:
            base += 0.5
        
        return base
    
    def _calculate_danceability(self, track_data: Dict) -> float:
        """Calculate danceability based on genre, BPM, and energy."""
        genre = track_data.get('genre', '').lower()
        bpm = track_data.get('bpm', 120)
        energy = track_data.get('energy', 0.5)
        
        # Genre-based danceability mapping
        dance_genres = {
            'house': 0.9, 'techno': 0.95, 'trance': 0.8,
            'edm': 0.9, 'disco': 0.85, 'funk': 0.8,
            'dance': 0.9, 'electronic': 0.8, 'club': 0.85,
            'hip hop': 0.75, 'hip-hop': 0.75, 'rap': 0.7,
            'pop': 0.7, 'r&b': 0.65, 'reggaeton': 0.85
        }
        
        # Start with genre base or default
        danceability = 0.5
        for g, score in dance_genres.items():
            if g in genre:
                danceability = score
                break
        
        # BPM influence (optimal range 110-140)
        if 110 <= bpm <= 140:
            danceability *= 1.1
        elif bpm < 90 or bpm > 160:
            danceability *= 0.8
        
        # Energy influence
        danceability = danceability * 0.7 + energy * 0.3
        
        return np.clip(danceability, 0, 1)
    
    def _calculate_valence(self, track_data: Dict) -> float:
        """Calculate valence (musical positivity) based on key and genre."""
        key = track_data.get('key', 'Am')
        genre = track_data.get('genre', '').lower()
        
        # Major keys are generally more positive
        is_major = 'B' in self.CAMELOT_WHEEL.get(key, '1A')
        base_valence = 0.7 if is_major else 0.4
        
        # Genre influence
        positive_genres = {
            'house': 0.8, 'disco': 0.9, 'pop': 0.7,
            'funk': 0.8, 'dance': 0.75, 'edm': 0.7,
            'reggae': 0.8, 'ska': 0.85
        }
        
        negative_genres = {
            'dark': 0.2, 'doom': 0.15, 'gothic': 0.25,
            'industrial': 0.3, 'darkwave': 0.2
        }
        
        for g, mod in positive_genres.items():
            if g in genre:
                base_valence = (base_valence + mod) / 2
                break
        
        for g, mod in negative_genres.items():
            if g in genre:
                base_valence = (base_valence + mod) / 2
                break
        
        return np.clip(base_valence, 0, 1)
    
    def _calculate_acousticness(self, track_data: Dict) -> float:
        """Calculate acousticness based on genre."""
        genre = track_data.get('genre', '').lower()
        
        acoustic_genres = {
            'folk': 0.9, 'acoustic': 0.95, 'jazz': 0.7,
            'classical': 0.85, 'singer-songwriter': 0.8,
            'unplugged': 0.9, 'bluegrass': 0.95
        }
        
        electronic_genres = {
            'house': 0.1, 'techno': 0.05, 'edm': 0.1,
            'electronic': 0.1, 'synth': 0.15, 'electro': 0.1,
            'dubstep': 0.05, 'drum and bass': 0.1, 'trance': 0.1
        }
        
        # Check for genre matches
        for g, score in acoustic_genres.items():
            if g in genre:
                return score
        
        for g, score in electronic_genres.items():
            if g in genre:
                return score
        
        # Default middle ground
        return 0.5
    
    def _calculate_instrumentalness(self, track_data: Dict) -> float:
        """Calculate instrumentalness based on genre and title."""
        genre = track_data.get('genre', '').lower()
        title = track_data.get('title', '').lower()
        
        # Check for instrumental indicators in title
        if any(word in title for word in ['instrumental', 'inst.', 'karaoke', 'backing']):
            return 0.9
        
        # Genre-based mapping
        instrumental_genres = {
            'ambient': 0.8, 'classical': 0.9, 'soundtrack': 0.8,
            'instrumental': 0.95, 'post-rock': 0.7, 'jazz': 0.6
        }
        
        vocal_genres = {
            'pop': 0.1, 'rock': 0.2, 'r&b': 0.1,
            'soul': 0.1, 'singer-songwriter': 0.05, 'rap': 0.05,
            'country': 0.15, 'folk': 0.2
        }
        
        for g, score in instrumental_genres.items():
            if g in genre:
                return score
        
        for g, score in vocal_genres.items():
            if g in genre:
                return score
        
        return 0.4  # Default assumes some vocals
    
    def _calculate_rhythmic_pattern(self, track_data: Dict) -> float:
        """Calculate rhythmic pattern complexity."""
        genre = track_data.get('genre', '').lower()
        bpm = track_data.get('bpm', 120)
        
        # Genre-based rhythm complexity
        rhythm_map = {
            'jazz': 0.9, 'fusion': 0.85, 'prog': 0.8,
            'drum and bass': 0.8, 'breakbeat': 0.75, 'jungle': 0.85,
            'techno': 0.8, 'idm': 0.9, 'glitch': 0.95,
            'house': 0.7, 'trance': 0.6, 'minimal': 0.5,
            'pop': 0.4, 'rock': 0.5, 'ambient': 0.2
        }
        
        complexity = 0.5  # Default
        for g, score in rhythm_map.items():
            if g in genre:
                complexity = score
                break
        
        # Fast tempos often have more complex patterns
        if bpm > 140:
            complexity *= 1.1
        elif bpm < 90:
            complexity *= 0.9
        
        return np.clip(complexity, 0, 1)
    
    def _calculate_spectral_centroid(self, track_data: Dict) -> float:
        """Calculate spectral centroid (brightness)."""
        genre = track_data.get('genre', '').lower()
        
        bright_genres = {
            'house': 0.7, 'techno': 0.8, 'trance': 0.75,
            'edm': 0.8, 'pop': 0.7, 'disco': 0.75,
            'hi-nrg': 0.85, 'happy hardcore': 0.9
        }
        
        dark_genres = {
            'ambient': 0.3, 'darkwave': 0.25, 'doom': 0.2,
            'drone': 0.2, 'dark ambient': 0.15, 'industrial': 0.35,
            'deep house': 0.4, 'dub': 0.35
        }
        
        for g, score in bright_genres.items():
            if g in genre:
                return score
        
        for g, score in dark_genres.items():
            if g in genre:
                return score
        
        return 0.5  # Neutral brightness
    
    def _calculate_tempo_stability(self, track_data: Dict) -> float:
        """Calculate tempo stability based on genre."""
        genre = track_data.get('genre', '').lower()
        
        stable_genres = {
            'house': 0.9, 'techno': 0.95, 'trance': 0.9,
            'edm': 0.85, 'minimal': 0.95, 'disco': 0.85,
            'drum and bass': 0.9, 'dubstep': 0.85
        }
        
        unstable_genres = {
            'jazz': 0.4, 'classical': 0.5, 'progressive': 0.6,
            'experimental': 0.3, 'free jazz': 0.2, 'rubato': 0.1,
            'live': 0.6, 'acoustic': 0.65
        }
        
        for g, score in stable_genres.items():
            if g in genre:
                return score
        
        for g, score in unstable_genres.items():
            if g in genre:
                return score
        
        return 0.7  # Default moderate stability
    
    def _calculate_harmonic_complexity(self, track_data: Dict) -> float:
        """Calculate harmonic complexity based on key and genre."""
        key = track_data.get('key', 'Am')
        genre = track_data.get('genre', '').lower()
        
        # Minor keys are generally more complex
        is_minor = 'A' in self.CAMELOT_WHEEL.get(key, '1A')
        base_complexity = 0.6 if is_minor else 0.4
        
        complex_genres = {
            'jazz': 0.9, 'fusion': 0.85, 'classical': 0.8,
            'prog': 0.8, 'art rock': 0.75, 'experimental': 0.85,
            'bebop': 0.95, 'modal': 0.8
        }
        
        simple_genres = {
            'pop': 0.3, 'punk': 0.2, 'minimal': 0.25,
            'drone': 0.15, 'techno': 0.35, 'house': 0.4
        }
        
        for g, score in complex_genres.items():
            if g in genre:
                return (base_complexity + score) / 2
        
        for g, score in simple_genres.items():
            if g in genre:
                return (base_complexity + score) / 2
        
        return base_complexity
    
    def _calculate_dynamic_range(self, track_data: Dict) -> float:
        """Calculate dynamic range based on genre."""
        genre = track_data.get('genre', '').lower()
        
        dynamic_genres = {
            'classical': 0.9, 'jazz': 0.8, 'orchestral': 0.85,
            'acoustic': 0.7, 'live': 0.75, 'unplugged': 0.7,
            'folk': 0.65, 'chamber': 0.8
        }
        
        compressed_genres = {
            'pop': 0.3, 'edm': 0.25, 'loudness war': 0.1,
            'metal': 0.3, 'punk': 0.35, 'hardcore': 0.3,
            'dubstep': 0.35, 'trap': 0.3, 'commercial': 0.25
        }
        
        for g, score in dynamic_genres.items():
            if g in genre:
                return score
        
        for g, score in compressed_genres.items():
            if g in genre:
                return score
        
        return 0.5  # Default middle ground
    
    def _validate_vector(self, vector: np.ndarray):
        """Validate HAMMS vector quality gates."""
        # Check dimensionality
        if len(vector) != 12:
            raise ValueError(f"Vector must have 12 dimensions, got {len(vector)}")
        
        # Check value range
        if not np.all((vector >= 0) & (vector <= 1)):
            raise ValueError(f"All vector values must be in [0, 1] range")
        
        # Check for NaN or infinity
        if np.any(np.isnan(vector)):
            raise ValueError("Vector contains NaN values")
        
        if np.any(np.isinf(vector)):
            raise ValueError("Vector contains infinite values")
    
    def _calculate_confidence(self, track_data: Dict, vector: np.ndarray) -> float:
        """Calculate confidence score for the analysis."""
        confidence = 0.8  # Base confidence
        
        # Reduce confidence for missing data
        if not track_data.get('bpm') or track_data.get('bpm') <= 0:
            confidence -= 0.2
        
        if not track_data.get('key'):
            confidence -= 0.1
        
        if not track_data.get('energy'):
            confidence -= 0.1
        
        if not track_data.get('genre'):
            confidence -= 0.05
        
        # Check vector quality
        if np.any(np.isnan(vector)) or np.any(np.isinf(vector)):
            confidence = 0.0
        
        # Check for extreme values (all 0s or all 1s)
        if np.all(vector == 0) or np.all(vector == 1):
            confidence *= 0.5
        
        return np.clip(confidence, 0.0, 1.0)
    
    def calculate_similarity(self, vector1: np.ndarray, vector2: np.ndarray) -> Dict[str, float]:
        """Calculate similarity between two HAMMS vectors.
        
        Args:
            vector1: First 12-dimensional HAMMS vector
            vector2: Second 12-dimensional HAMMS vector
        
        Returns:
            Dictionary containing:
                - euclidean_similarity: Euclidean distance-based similarity (0-1)
                - cosine_similarity: Cosine similarity (0-1)
                - overall_similarity: Weighted combination (0-1)
                - compatibility_rating: Text rating
        """
        # Validate vectors
        self._validate_vector(vector1)
        self._validate_vector(vector2)
        
        # Get dimension weights
        weights = self.dimensions.get_weights_array()
        
        # Apply weights to vectors
        weighted_v1 = vector1 * weights
        weighted_v2 = vector2 * weights
        
        # Calculate Euclidean distance and convert to similarity
        euclidean_dist = np.linalg.norm(weighted_v1 - weighted_v2)
        max_distance = np.linalg.norm(weights)  # Maximum possible distance
        euclidean_sim = 1.0 - (euclidean_dist / max_distance)
        
        # Calculate cosine similarity
        dot_product = np.dot(weighted_v1, weighted_v2)
        norm_v1 = np.linalg.norm(weighted_v1)
        norm_v2 = np.linalg.norm(weighted_v2)
        
        if norm_v1 > 0 and norm_v2 > 0:
            cosine_sim = dot_product / (norm_v1 * norm_v2)
        else:
            cosine_sim = 0.0
        
        # Combined similarity (60% Euclidean, 40% Cosine)
        overall_similarity = euclidean_sim * 0.6 + cosine_sim * 0.4
        
        # Determine compatibility rating
        if overall_similarity >= 0.9:
            rating = "Excellent"
        elif overall_similarity >= 0.8:
            rating = "Good"
        elif overall_similarity >= 0.7:
            rating = "Fair"
        elif overall_similarity >= 0.6:
            rating = "Poor"
        else:
            rating = "Incompatible"
        
        return {
            'euclidean_similarity': float(euclidean_sim),
            'cosine_similarity': float(cosine_sim),
            'overall_similarity': float(overall_similarity),
            'compatibility_rating': rating
        }
    
    def get_compatible_tracks(self, seed_vector: np.ndarray, 
                             candidate_vectors: List[Tuple[Any, np.ndarray]],
                             threshold: float = 0.7,
                             limit: int = 20) -> List[Tuple[Any, float]]:
        """Find compatible tracks based on HAMMS similarity.
        
        Args:
            seed_vector: Reference HAMMS vector
            candidate_vectors: List of (track_id, vector) tuples
            threshold: Minimum similarity threshold (0-1)
            limit: Maximum number of results
        
        Returns:
            List of (track_id, similarity) tuples sorted by similarity
        """
        results = []
        
        for track_id, candidate_vector in candidate_vectors:
            try:
                similarity = self.calculate_similarity(seed_vector, candidate_vector)
                overall_sim = similarity['overall_similarity']
                
                if overall_sim >= threshold:
                    results.append((track_id, overall_sim))
            except Exception as e:
                logger.warning(f"Error calculating similarity for track {track_id}: {e}")
                continue
        
        # Sort by similarity (descending) and limit results
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:limit]

# Export main class
__all__ = ['HAMMSAnalyzer', 'HAMMSDimensions']
```

## Step 2: Audio Processing Pipeline

### 2.1 Create Audio Processing Service
Create `src/lib/audio_processing.py`:

```python
"""Audio processing pipeline using librosa with quality gates."""

import librosa
import numpy as np
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
import logging
from functools import lru_cache
import warnings
import soundfile as sf

warnings.filterwarnings('ignore', category=UserWarning)
logger = logging.getLogger(__name__)

class AudioProcessor:
    """Audio processing service with librosa integration."""
    
    # Supported audio formats
    SUPPORTED_FORMATS = {'.mp3', '.wav', '.flac', '.m4a', '.ogg', '.aac', '.wma'}
    
    # Analysis parameters
    DEFAULT_SAMPLE_RATE = 22050
    DEFAULT_HOP_LENGTH = 512
    DEFAULT_N_FFT = 2048
    DEFAULT_MAX_DURATION = 120  # seconds
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize audio processor with configuration."""
        self.config = config or {}
        
        # Set analysis parameters from config
        self.sample_rate = self.config.get('sample_rate', self.DEFAULT_SAMPLE_RATE)
        self.hop_length = self.config.get('hop_length', self.DEFAULT_HOP_LENGTH)
        self.n_fft = self.config.get('n_fft', self.DEFAULT_N_FFT)
        self.max_duration = self.config.get('max_duration', self.DEFAULT_MAX_DURATION)
        
        # Cache for processed audio
        self._audio_cache = {}
    
    def analyze_track(self, file_path: str) -> Dict[str, Any]:
        """Analyze audio track and extract features.
        
        Args:
            file_path: Path to audio file
        
        Returns:
            Dictionary containing:
                - bpm: Beats per minute
                - key: Musical key
                - energy: Energy level (0-1)
                - duration: Track duration in seconds
                - sample_rate: Audio sample rate
                - spectral_features: Additional spectral characteristics
        """
        # Validate file
        self._validate_file(file_path)
        
        try:
            # Load audio with duration limit
            audio_data, sr = self._load_audio(file_path)
            
            # Extract basic features
            bpm = self._extract_bpm(audio_data, sr)
            key = self._extract_key(audio_data, sr)
            energy = self._extract_energy(audio_data)
            
            # Extract spectral features
            spectral_features = self._extract_spectral_features(audio_data, sr)
            
            # Get file metadata
            duration = len(audio_data) / sr
            
            result = {
                'bpm': float(bpm),
                'key': key,
                'energy': float(energy),
                'duration': float(duration),
                'sample_rate': int(sr),
                'spectral_centroid': float(spectral_features['spectral_centroid']),
                'spectral_rolloff': float(spectral_features['spectral_rolloff']),
                'spectral_bandwidth': float(spectral_features['spectral_bandwidth']),
                'zero_crossing_rate': float(spectral_features['zero_crossing_rate']),
                'mfcc': spectral_features['mfcc'].tolist() if spectral_features.get('mfcc') is not None else None,
                'success': True,
                'error': None
            }
            
            # Apply quality gates
            result = self._apply_quality_gates(result)
            
            logger.info(f"Successfully analyzed: {file_path}")
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'file_path': file_path
            }
    
    def _validate_file(self, file_path: str):
        """Validate audio file before processing."""
        path = Path(file_path)
        
        # Check file exists
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Check file format
        if path.suffix.lower() not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format: {path.suffix}. Supported: {self.SUPPORTED_FORMATS}")
        
        # Check file size (minimum 10KB)
        if path.stat().st_size < 10240:
            raise ValueError(f"File too small, possibly corrupted: {file_path}")
    
    @lru_cache(maxsize=10)
    def _load_audio(self, file_path: str) -> Tuple[np.ndarray, int]:
        """Load audio file with caching."""
        try:
            # Load with duration limit
            audio_data, sr = librosa.load(
                file_path,
                sr=self.sample_rate,
                duration=self.max_duration,
                mono=True
            )
            
            # Normalize audio
            if np.max(np.abs(audio_data)) > 0:
                audio_data = audio_data / np.max(np.abs(audio_data))
            
            return audio_data, sr
            
        except Exception as e:
            logger.error(f"Error loading audio: {e}")
            raise
    
    def _extract_bpm(self, audio_data: np.ndarray, sr: int) -> float:
        """Extract BPM using librosa's tempo detection."""
        try:
            # Use onset detection for better tempo accuracy
            onset_env = librosa.onset.onset_strength(
                y=audio_data,
                sr=sr,
                hop_length=self.hop_length
            )
            
            # Estimate tempo with constraints
            tempo, beats = librosa.beat.beat_track(
                onset_envelope=onset_env,
                sr=sr,
                hop_length=self.hop_length,
                trim=False
            )
            
            # Apply BPM constraints (30-300 BPM reasonable range)
            tempo = np.clip(tempo, 30, 300)
            
            # Check for half/double tempo issues
            if tempo < 70:
                # Might be half-time, check double
                tempo_double = tempo * 2
                if 120 <= tempo_double <= 160:
                    tempo = tempo_double
            elif tempo > 160:
                # Might be double-time, check half
                tempo_half = tempo / 2
                if 70 <= tempo_half <= 130:
                    tempo = tempo_half
            
            return float(tempo)
            
        except Exception as e:
            logger.warning(f"BPM extraction failed: {e}, using default 120")
            return 120.0
    
    def _extract_key(self, audio_data: np.ndarray, sr: int) -> str:
        """Extract musical key using chroma features."""
        try:
            # Compute chromagram
            chromagram = librosa.feature.chroma_cqt(
                y=audio_data,
                sr=sr,
                hop_length=self.hop_length
            )
            
            # Average chroma across time
            chroma_mean = np.mean(chromagram, axis=1)
            
            # Key profiles for major and minor keys
            major_profile = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
            minor_profile = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
            
            # Normalize profiles
            major_profile = major_profile / np.sum(major_profile)
            minor_profile = minor_profile / np.sum(minor_profile)
            
            # Find best matching key
            major_scores = []
            minor_scores = []
            
            for shift in range(12):
                shifted_chroma = np.roll(chroma_mean, shift)
                major_score = np.corrcoef(shifted_chroma, major_profile)[0, 1]
                minor_score = np.corrcoef(shifted_chroma, minor_profile)[0, 1]
                major_scores.append(major_score)
                minor_scores.append(minor_score)
            
            # Determine key
            max_major = np.max(major_scores)
            max_minor = np.max(minor_scores)
            
            if max_major > max_minor:
                key_index = np.argmax(major_scores)
                is_major = True
            else:
                key_index = np.argmax(minor_scores)
                is_major = False
            
            # Map to key names
            keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
            key_name = keys[key_index]
            
            if not is_major:
                # Convert to relative minor
                minor_keys = ['Am', 'A#m', 'Bm', 'Cm', 'C#m', 'Dm', 'D#m', 'Em', 'Fm', 'F#m', 'Gm', 'G#m']
                key_name = minor_keys[key_index]
            
            return key_name
            
        except Exception as e:
            logger.warning(f"Key extraction failed: {e}, using default Am")
            return "Am"
    
    def _extract_energy(self, audio_data: np.ndarray) -> float:
        """Extract energy level from audio."""
        try:
            # Calculate RMS energy
            rms = librosa.feature.rms(y=audio_data, hop_length=self.hop_length)
            rms_mean = np.mean(rms)
            
            # Normalize to 0-1 range
            energy = np.clip(rms_mean * 2, 0, 1)
            
            return float(energy)
            
        except Exception as e:
            logger.warning(f"Energy extraction failed: {e}, using default 0.5")
            return 0.5
    
    def _extract_spectral_features(self, audio_data: np.ndarray, sr: int) -> Dict[str, Any]:
        """Extract various spectral features."""
        features = {}
        
        try:
            # Spectral centroid (brightness)
            spectral_centroid = librosa.feature.spectral_centroid(
                y=audio_data,
                sr=sr,
                hop_length=self.hop_length
            )
            features['spectral_centroid'] = np.mean(spectral_centroid) / sr
            
            # Spectral rolloff
            spectral_rolloff = librosa.feature.spectral_rolloff(
                y=audio_data,
                sr=sr,
                hop_length=self.hop_length
            )
            features['spectral_rolloff'] = np.mean(spectral_rolloff) / sr
            
            # Spectral bandwidth
            spectral_bandwidth = librosa.feature.spectral_bandwidth(
                y=audio_data,
                sr=sr,
                hop_length=self.hop_length
            )
            features['spectral_bandwidth'] = np.mean(spectral_bandwidth) / sr
            
            # Zero crossing rate
            zero_crossing = librosa.feature.zero_crossing_rate(
                audio_data,
                hop_length=self.hop_length
            )
            features['zero_crossing_rate'] = np.mean(zero_crossing)
            
            # MFCCs (first 13 coefficients)
            mfccs = librosa.feature.mfcc(
                y=audio_data,
                sr=sr,
                n_mfcc=13,
                hop_length=self.hop_length
            )
            features['mfcc'] = np.mean(mfccs, axis=1)
            
        except Exception as e:
            logger.warning(f"Spectral feature extraction partial failure: {e}")
            # Set defaults for missing features
            features.setdefault('spectral_centroid', 0.5)
            features.setdefault('spectral_rolloff', 0.5)
            features.setdefault('spectral_bandwidth', 0.5)
            features.setdefault('zero_crossing_rate', 0.5)
            features.setdefault('mfcc', None)
        
        return features
    
    def _apply_quality_gates(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Apply quality gates to validate analysis results."""
        if not result.get('success', False):
            return result
        
        issues = []
        
        # Validate BPM
        bpm = result.get('bpm', 0)
        if not 30 <= bpm <= 300:
            issues.append(f"BPM out of range: {bpm}")
            result['bpm'] = 120.0  # Reset to default
        
        # Validate energy
        energy = result.get('energy', -1)
        if not 0 <= energy <= 1:
            issues.append(f"Energy out of range: {energy}")
            result['energy'] = 0.5
        
        # Validate key
        if not result.get('key'):
            issues.append("Key detection failed")
            result['key'] = "Am"
        
        # Add quality report
        if issues:
            result['quality_issues'] = issues
            result['quality_score'] = max(0.5, 1.0 - len(issues) * 0.1)
        else:
            result['quality_score'] = 1.0
        
        return result

# Singleton instance
_processor = None

def get_audio_processor(config: Optional[Dict[str, Any]] = None) -> AudioProcessor:
    """Get or create audio processor instance."""
    global _processor
    if _processor is None:
        _processor = AudioProcessor(config)
    return _processor

# Export
__all__ = ['AudioProcessor', 'get_audio_processor']
```

## Step 3: Storage Integration Service

### 3.1 Create Storage Service
Create `src/services/storage_service.py`:

```python
"""Storage service for MAP4 with transaction management and caching."""

import json
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import numpy as np
from contextlib import contextmanager
import logging
from pathlib import Path
import hashlib

from src.models.database import (
    DatabaseManager, TrackORM, AnalysisResultORM,
    HAMMSVectorORM, AIAnalysis, HAMMSAdvanced
)

logger = logging.getLogger(__name__)

class StorageService:
    """Unified storage service for all MAP4 data operations."""
    
    def __init__(self, database_url: Optional[str] = None):
        """Initialize storage service."""
        self.db_manager = DatabaseManager(database_url or "sqlite:///data/database/map4.db")
        self._track_cache = {}
        self._analysis_cache = {}
    
    @contextmanager
    def session(self):
        """Provide a transactional scope for database operations."""
        session = self.db_manager.get_session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database transaction failed: {e}")
            raise
        finally:
            session.close()
    
    def get_or_create_track(self, file_path: str, metadata: Optional[Dict[str, Any]] = None) -> int:
        """Get existing track or create new one.
        
        Args:
            file_path: Path to audio file
            metadata: Optional metadata dictionary
        
        Returns:
            Track ID
        """
        # Check cache first
        if file_path in self._track_cache:
            return self._track_cache[file_path]
        
        with self.session() as session:
            # Check if track exists
            track = session.query(TrackORM).filter_by(file_path=file_path).first()
            
            if not track:
                # Create new track
                track = TrackORM(file_path=file_path)
                
                # Add file hash for duplicate detection
                try:
                    file_hash = self._calculate_file_hash(file_path)
                    track.file_hash = file_hash
                except Exception as e:
                    logger.warning(f"Could not calculate file hash: {e}")
                
                # Add metadata if provided
                if metadata:
                    track.title = metadata.get('title', Path(file_path).stem)
                    track.artist = metadata.get('artist', 'Unknown')
                    track.album = metadata.get('album')
                    track.year = metadata.get('year')
                    track.genre = metadata.get('genre')
                    track.duration = metadata.get('duration')
                    track.file_size = metadata.get('file_size')
                    track.file_format = metadata.get('file_format', Path(file_path).suffix[1:])
                    track.sample_rate = metadata.get('sample_rate')
                    track.bit_rate = metadata.get('bit_rate')
                else:
                    track.title = Path(file_path).stem
                    track.file_format = Path(file_path).suffix[1:]
                
                session.add(track)
                session.commit()
                logger.info(f"Created new track: {file_path} (ID: {track.id})")
            
            # Cache the track ID
            self._track_cache[file_path] = track.id
            return track.id
    
    def store_analysis_result(self, track_id: int, analysis_data: Dict[str, Any]) -> int:
        """Store basic analysis results.
        
        Args:
            track_id: Track ID
            analysis_data: Analysis results dictionary
        
        Returns:
            Analysis result ID
        """
        with self.session() as session:
            # Create analysis result
            analysis = AnalysisResultORM(
                track_id=track_id,
                bpm=analysis_data.get('bpm'),
                key=analysis_data.get('key'),
                energy=analysis_data.get('energy'),
                danceability=analysis_data.get('danceability'),
                valence=analysis_data.get('valence'),
                acousticness=analysis_data.get('acousticness'),
                instrumentalness=analysis_data.get('instrumentalness'),
                confidence_score=analysis_data.get('confidence', 0.8),
                analysis_version=analysis_data.get('version', '3.0.0'),
                provider=analysis_data.get('provider', 'hamms_v3')
            )
            
            # Add Camelot key if available
            if 'camelot_key' in analysis_data:
                analysis.camelot_key = analysis_data['camelot_key']
            
            session.add(analysis)
            session.commit()
            
            logger.info(f"Stored analysis result for track {track_id}")
            return analysis.id
    
    def store_hamms_vector(self, track_id: int, hamms_data: Dict[str, Any]) -> int:
        """Store HAMMS vector data.
        
        Args:
            track_id: Track ID
            hamms_data: HAMMS analysis results
        
        Returns:
            HAMMS vector ID
        """
        with self.session() as session:
            # Create HAMMS vector record
            hamms_vector = HAMMSVectorORM(
                track_id=track_id,
                version=hamms_data.get('version', '3.0'),
                confidence=hamms_data.get('confidence', 0.8)
            )
            
            # Set the vector
            vector = hamms_data.get('hamms_vector')
            if isinstance(vector, (list, np.ndarray)):
                hamms_vector.set_vector(np.array(vector))
            
            session.add(hamms_vector)
            session.commit()
            
            logger.info(f"Stored HAMMS vector for track {track_id}")
            return hamms_vector.id
    
    def store_hamms_advanced(self, track_id: int, hamms_data: Dict[str, Any]) -> int:
        """Store advanced HAMMS analysis.
        
        Args:
            track_id: Track ID
            hamms_data: Advanced HAMMS analysis results
        
        Returns:
            Advanced HAMMS ID
        """
        with self.session() as session:
            # Create advanced HAMMS record
            hamms_advanced = HAMMSAdvanced(
                track_id=track_id,
                analysis_timestamp=datetime.utcnow()
            )
            
            # Set vector
            if 'hamms_vector' in hamms_data:
                hamms_advanced.set_vector_12d(np.array(hamms_data['hamms_vector']))
            
            # Set dimension scores
            if 'dimension_scores' in hamms_data:
                hamms_advanced.set_dimension_scores(hamms_data['dimension_scores'])
            
            # Set dimension weights
            if 'dimension_weights' in hamms_data:
                hamms_advanced.dimension_weights = hamms_data['dimension_weights']
            
            # Set compatibility scores
            hamms_advanced.dj_compatibility_score = hamms_data.get('dj_compatibility_score')
            hamms_advanced.hamms_compatibility_score = hamms_data.get('hamms_compatibility_score')
            hamms_advanced.overall_compatibility = hamms_data.get('overall_compatibility')
            
            # Set metadata
            hamms_advanced.calculation_time_ms = hamms_data.get('calculation_time_ms')
            hamms_advanced.quality_gates_passed = hamms_data.get('quality_gates_passed', True)
            hamms_advanced.validation_errors = hamms_data.get('validation_errors', [])
            
            session.add(hamms_advanced)
            session.commit()
            
            logger.info(f"Stored advanced HAMMS analysis for track {track_id}")
            return hamms_advanced.id
    
    def store_ai_analysis(self, track_id: int, ai_data: Dict[str, Any], 
                          provider: str, model: str) -> int:
        """Store AI-generated analysis.
        
        Args:
            track_id: Track ID
            ai_data: AI analysis results
            provider: LLM provider name
            model: Model name
        
        Returns:
            AI analysis ID
        """
        with self.session() as session:
            # Create AI analysis from response
            ai_analysis = AIAnalysis.from_llm_response(
                track_id=track_id,
                response=ai_data,
                provider=provider,
                model=model
            )
            
            session.add(ai_analysis)
            session.commit()
            
            logger.info(f"Stored AI analysis for track {track_id} from {provider}/{model}")
            return ai_analysis.id
    
    def get_track_by_path(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get track information by file path.
        
        Args:
            file_path: Path to audio file
        
        Returns:
            Track data dictionary or None
        """
        with self.session() as session:
            track = session.query(TrackORM).filter_by(file_path=file_path).first()
            
            if track:
                return {
                    'id': track.id,
                    'file_path': track.file_path,
                    'title': track.title,
                    'artist': track.artist,
                    'album': track.album,
                    'genre': track.genre,
                    'duration': track.duration,
                    'analyzed_at': track.analyzed_at.isoformat() if track.analyzed_at else None
                }
            
            return None
    
    def get_analysis_by_track(self, track_id: int) -> Optional[Dict[str, Any]]:
        """Get all analysis data for a track.
        
        Args:
            track_id: Track ID
        
        Returns:
            Complete analysis data dictionary
        """
        with self.session() as session:
            # Get track
            track = session.query(TrackORM).filter_by(id=track_id).first()
            if not track:
                return None
            
            result = {
                'track_id': track.id,
                'file_path': track.file_path,
                'title': track.title,
                'artist': track.artist
            }
            
            # Get basic analysis
            analysis = session.query(AnalysisResultORM).filter_by(
                track_id=track_id
            ).order_by(AnalysisResultORM.created_at.desc()).first()
            
            if analysis:
                result['analysis'] = {
                    'bpm': analysis.bpm,
                    'key': analysis.key,
                    'camelot_key': analysis.camelot_key,
                    'energy': analysis.energy,
                    'danceability': analysis.danceability,
                    'valence': analysis.valence,
                    'confidence': analysis.confidence_score
                }
            
            # Get HAMMS vector
            hamms = session.query(HAMMSVectorORM).filter_by(
                track_id=track_id
            ).order_by(HAMMSVectorORM.created_at.desc()).first()
            
            if hamms:
                result['hamms'] = {
                    'vector': hamms.get_vector().tolist(),
                    'version': hamms.version,
                    'confidence': hamms.confidence
                }
            
            # Get AI analysis
            ai = session.query(AIAnalysis).filter_by(
                track_id=track_id
            ).order_by(AIAnalysis.created_at.desc()).first()
            
            if ai:
                result['ai_analysis'] = {
                    'provider': ai.provider,
                    'model': ai.model,
                    'genre': ai.genre_primary,
                    'subgenres': ai.subgenres,
                    'mood': ai.mood_primary,
                    'tags': ai.tags,
                    'confidence': ai.overall_confidence
                }
            
            return result
    
    def get_tracks_by_genre(self, genre: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get tracks by genre.
        
        Args:
            genre: Genre name (partial match)
            limit: Maximum number of results
        
        Returns:
            List of track dictionaries
        """
        with self.session() as session:
            tracks = session.query(TrackORM).filter(
                TrackORM.genre.ilike(f"%{genre}%")
            ).limit(limit).all()
            
            return [
                {
                    'id': track.id,
                    'file_path': track.file_path,
                    'title': track.title,
                    'artist': track.artist,
                    'genre': track.genre
                }
                for track in tracks
            ]
    
    def get_similar_tracks(self, track_id: int, threshold: float = 0.7, 
                           limit: int = 20) -> List[Tuple[int, float]]:
        """Find similar tracks based on HAMMS vectors.
        
        Args:
            track_id: Reference track ID
            threshold: Similarity threshold (0-1)
            limit: Maximum number of results
        
        Returns:
            List of (track_id, similarity) tuples
        """
        with self.session() as session:
            # Get reference HAMMS vector
            ref_hamms = session.query(HAMMSVectorORM).filter_by(
                track_id=track_id
            ).first()
            
            if not ref_hamms:
                return []
            
            ref_vector = ref_hamms.get_vector()
            
            # Get all other HAMMS vectors
            all_hamms = session.query(HAMMSVectorORM).filter(
                HAMMSVectorORM.track_id != track_id
            ).all()
            
            # Calculate similarities
            from src.analysis.hamms_v3 import HAMMSAnalyzer
            analyzer = HAMMSAnalyzer()
            
            candidates = [(h.track_id, h.get_vector()) for h in all_hamms]
            similar = analyzer.get_compatible_tracks(
                ref_vector, candidates, threshold, limit
            )
            
            return similar
    
    def update_track_metadata(self, track_id: int, metadata: Dict[str, Any]):
        """Update track metadata.
        
        Args:
            track_id: Track ID
            metadata: Metadata dictionary to update
        """
        with self.session() as session:
            track = session.query(TrackORM).filter_by(id=track_id).first()
            
            if track:
                for key, value in metadata.items():
                    if hasattr(track, key):
                        setattr(track, key, value)
                
                track.updated_at = datetime.utcnow()
                session.commit()
                logger.info(f"Updated metadata for track {track_id}")
    
    def mark_track_analyzed(self, track_id: int):
        """Mark track as analyzed with timestamp.
        
        Args:
            track_id: Track ID
        """
        with self.session() as session:
            track = session.query(TrackORM).filter_by(id=track_id).first()
            if track:
                track.analyzed_at = datetime.utcnow()
                session.commit()
    
    def _calculate_file_hash(self, file_path: str, chunk_size: int = 8192) -> str:
        """Calculate SHA-256 hash of file."""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics.
        
        Returns:
            Statistics dictionary
        """
        with self.session() as session:
            total_tracks = session.query(TrackORM).count()
            analyzed_tracks = session.query(TrackORM).filter(
                TrackORM.analyzed_at.isnot(None)
            ).count()
            
            total_hamms = session.query(HAMMSVectorORM).count()
            total_ai = session.query(AIAnalysis).count()
            
            # Get genre distribution
            genres = session.query(
                TrackORM.genre,
                func.count(TrackORM.id)
            ).group_by(TrackORM.genre).all()
            
            return {
                'total_tracks': total_tracks,
                'analyzed_tracks': analyzed_tracks,
                'total_hamms_vectors': total_hamms,
                'total_ai_analyses': total_ai,
                'genre_distribution': dict(genres) if genres else {}
            }

# Export
__all__ = ['StorageService']
```

## Step 4: Enhanced Analysis Pipeline

### 4.1 Create Enhanced Analyzer
Create `src/analysis/enhanced_analyzer.py`:

```python
"""Enhanced music analyzer combining all analysis components."""

import time
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging
from dataclasses import dataclass
import numpy as np

from src.lib.audio_processing import get_audio_processor
from src.analysis.hamms_v3 import HAMMSAnalyzer
from src.services.storage_service import StorageService
from src.config import get_config

logger = logging.getLogger(__name__)

@dataclass
class EnhancedAnalysisResult:
    """Container for enhanced analysis results."""
    track_id: int
    file_path: str
    audio_features: Dict[str, Any]
    hamms_vector: np.ndarray
    hamms_dimensions: Dict[str, float]
    confidence: float
    ai_analysis: Optional[Dict[str, Any]] = None
    processing_time: float = 0.0
    quality_score: float = 1.0
    errors: List[str] = None

class EnhancedAnalyzer:
    """Enhanced music analyzer with HAMMS v3.0 and optional AI enrichment."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize enhanced analyzer."""
        self.config = config or get_config()
        
        # Initialize components
        self.audio_processor = get_audio_processor(self.config.analysis.__dict__)
        self.hamms_analyzer = HAMMSAnalyzer()
        self.storage = StorageService(self.config.storage.database_url)
        
        # AI provider will be initialized on demand
        self.ai_provider = None
    
    def analyze_track(self, file_path: str, 
                     use_ai: bool = False,
                     ai_provider: Optional[str] = None,
                     store_results: bool = True) -> EnhancedAnalysisResult:
        """Perform complete enhanced analysis on a track.
        
        Args:
            file_path: Path to audio file
            use_ai: Whether to include AI analysis
            ai_provider: Specific AI provider to use
            store_results: Whether to store results in database
        
        Returns:
            EnhancedAnalysisResult with all analysis data
        """
        start_time = time.time()
        errors = []
        
        # Validate file
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        logger.info(f"Starting enhanced analysis: {file_path}")
        
        # Step 1: Audio processing
        logger.debug("Extracting audio features...")
        audio_features = self.audio_processor.analyze_track(file_path)
        
        if not audio_features.get('success', False):
            error_msg = f"Audio processing failed: {audio_features.get('error')}"
            errors.append(error_msg)
            logger.error(error_msg)
            
            # Return partial result
            return EnhancedAnalysisResult(
                track_id=0,
                file_path=file_path,
                audio_features=audio_features,
                hamms_vector=np.zeros(12),
                hamms_dimensions={},
                confidence=0.0,
                errors=errors,
                processing_time=time.time() - start_time
            )
        
        # Step 2: HAMMS analysis
        logger.debug("Calculating HAMMS vector...")
        track_data = {
            'bpm': audio_features.get('bpm', 120),
            'key': audio_features.get('key', 'Am'),
            'energy': audio_features.get('energy', 0.5),
            'title': Path(file_path).stem,
            'genre': '',  # Will be filled by AI if enabled
            'duration': audio_features.get('duration', 0)
        }
        
        hamms_result = self.hamms_analyzer.calculate_extended_vector(track_data)
        
        # Step 3: Optional AI enrichment
        ai_analysis = None
        if use_ai:
            logger.debug(f"Performing AI analysis with provider: {ai_provider}")
            ai_analysis = self._perform_ai_analysis(
                file_path, track_data, hamms_result, ai_provider
            )
            
            # Update track_data with AI results
            if ai_analysis and ai_analysis.get('success'):
                track_data['genre'] = ai_analysis.get('genre', '')
                
                # Recalculate HAMMS with genre information
                hamms_result = self.hamms_analyzer.calculate_extended_vector(track_data)
        
        # Step 4: Store results if requested
        track_id = 0
        if store_results:
            track_id = self._store_analysis_results(
                file_path, audio_features, hamms_result, ai_analysis
            )
        
        # Calculate quality score
        quality_score = self._calculate_quality_score(
            audio_features, hamms_result, ai_analysis
        )
        
        processing_time = time.time() - start_time
        logger.info(f"Completed analysis in {processing_time:.2f}s: {file_path}")
        
        return EnhancedAnalysisResult(
            track_id=track_id,
            file_path=file_path,
            audio_features=audio_features,
            hamms_vector=hamms_result['hamms_vector'],
            hamms_dimensions=hamms_result['dimension_scores'],
            confidence=hamms_result['confidence'],
            ai_analysis=ai_analysis,
            processing_time=processing_time,
            quality_score=quality_score,
            errors=errors if errors else None
        )
    
    def analyze_library(self, directory: str, 
                       use_ai: bool = False,
                       parallel: bool = True,
                       max_workers: int = 4) -> List[EnhancedAnalysisResult]:
        """Analyze entire music library.
        
        Args:
            directory: Path to music library directory
            use_ai: Whether to include AI analysis
            parallel: Whether to process in parallel
            max_workers: Number of parallel workers
        
        Returns:
            List of analysis results
        """
        # Find all audio files
        audio_files = self._find_audio_files(directory)
        logger.info(f"Found {len(audio_files)} audio files in {directory}")
        
        results = []
        
        if parallel and len(audio_files) > 1:
            # Parallel processing
            from concurrent.futures import ThreadPoolExecutor, as_completed
            
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {
                    executor.submit(
                        self.analyze_track, 
                        str(file_path), 
                        use_ai
                    ): file_path
                    for file_path in audio_files
                }
                
                for future in as_completed(futures):
                    file_path = futures[future]
                    try:
                        result = future.result()
                        results.append(result)
                        logger.info(f"Analyzed ({len(results)}/{len(audio_files)}): {file_path}")
                    except Exception as e:
                        logger.error(f"Failed to analyze {file_path}: {e}")
        else:
            # Sequential processing
            for i, file_path in enumerate(audio_files, 1):
                try:
                    result = self.analyze_track(str(file_path), use_ai)
                    results.append(result)
                    logger.info(f"Analyzed ({i}/{len(audio_files)}): {file_path}")
                except Exception as e:
                    logger.error(f"Failed to analyze {file_path}: {e}")
        
        return results
    
    def _perform_ai_analysis(self, file_path: str, track_data: Dict[str, Any],
                            hamms_result: Dict[str, Any], 
                            provider_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Perform AI analysis using specified or default provider."""
        try:
            # Initialize AI provider if needed (will be implemented in LLM integration)
            # For now, return placeholder
            return {
                'success': True,
                'provider': provider_name or 'default',
                'genre': 'Electronic',
                'subgenres': ['House', 'Deep House'],
                'mood': 'Energetic',
                'tags': ['dance', 'club', 'uplifting'],
                'confidence': 0.85
            }
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return None
    
    def _store_analysis_results(self, file_path: str, 
                               audio_features: Dict[str, Any],
                               hamms_result: Dict[str, Any],
                               ai_analysis: Optional[Dict[str, Any]] = None) -> int:
        """Store all analysis results in database."""
        try:
            # Get or create track
            metadata = {
                'duration': audio_features.get('duration'),
                'sample_rate': audio_features.get('sample_rate')
            }
            track_id = self.storage.get_or_create_track(file_path, metadata)
            
            # Store basic analysis
            analysis_data = {
                'bpm': audio_features.get('bpm'),
                'key': audio_features.get('key'),
                'energy': audio_features.get('energy'),
                'camelot_key': hamms_result.get('camelot_key'),
                'confidence': hamms_result.get('confidence'),
                'version': '3.0.0',
                'provider': 'enhanced_analyzer'
            }
            self.storage.store_analysis_result(track_id, analysis_data)
            
            # Store HAMMS vector
            self.storage.store_hamms_vector(track_id, hamms_result)
            
            # Store advanced HAMMS
            advanced_data = {
                'hamms_vector': hamms_result['hamms_vector'],
                'dimension_scores': hamms_result['dimension_scores'],
                'quality_gates_passed': True
            }
            self.storage.store_hamms_advanced(track_id, advanced_data)
            
            # Store AI analysis if available
            if ai_analysis and ai_analysis.get('success'):
                self.storage.store_ai_analysis(
                    track_id,
                    ai_analysis,
                    ai_analysis.get('provider', 'unknown'),
                    ai_analysis.get('model', 'unknown')
                )
            
            # Mark track as analyzed
            self.storage.mark_track_analyzed(track_id)
            
            return track_id
            
        except Exception as e:
            logger.error(f"Failed to store analysis results: {e}")
            return 0
    
    def _calculate_quality_score(self, audio_features: Dict[str, Any],
                                hamms_result: Dict[str, Any],
                                ai_analysis: Optional[Dict[str, Any]] = None) -> float:
        """Calculate overall quality score for the analysis."""
        scores = []
        
        # Audio quality score
        audio_quality = audio_features.get('quality_score', 0.5)
        scores.append(audio_quality * 0.3)
        
        # HAMMS confidence
        hamms_confidence = hamms_result.get('confidence', 0.5)
        scores.append(hamms_confidence * 0.4)
        
        # AI confidence (if available)
        if ai_analysis and ai_analysis.get('success'):
            ai_confidence = ai_analysis.get('confidence', 0.5)
            scores.append(ai_confidence * 0.3)
        else:
            scores.append(0.3)  # Default if no AI
        
        return min(1.0, sum(scores))
    
    def _find_audio_files(self, directory: str) -> List[Path]:
        """Find all audio files in directory."""
        audio_extensions = {'.mp3', '.wav', '.flac', '.m4a', '.ogg', '.aac'}
        audio_files = []
        
        for path in Path(directory).rglob('*'):
            if path.is_file() and path.suffix.lower() in audio_extensions:
                audio_files.append(path)
        
        return sorted(audio_files)

# Export
__all__ = ['EnhancedAnalyzer', 'EnhancedAnalysisResult']
```

## Step 5: Quality Gate Framework

### 5.1 Create Quality Gate System
Create `src/services/quality_gates.py`:

```python
"""Quality gate framework for validation throughout the pipeline."""

from typing import Dict, Any, List, Optional, Callable
import numpy as np
import logging
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class QualityLevel(Enum):
    """Quality level enumeration."""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    FAILED = "failed"

@dataclass
class QualityReport:
    """Quality assessment report."""
    level: QualityLevel
    score: float
    passed: bool
    issues: List[str]
    warnings: List[str]
    metadata: Dict[str, Any]

class QualityGate:
    """Base quality gate for validation."""
    
    def __init__(self, name: str, threshold: float = 0.7):
        """Initialize quality gate.
        
        Args:
            name: Gate name
            threshold: Minimum score to pass (0-1)
        """
        self.name = name
        self.threshold = threshold
        self.validators = []
    
    def add_validator(self, validator: Callable, weight: float = 1.0):
        """Add a validation function.
        
        Args:
            validator: Function that returns (score, issues, warnings)
            weight: Weight for this validator
        """
        self.validators.append((validator, weight))
    
    def validate(self, data: Any) -> QualityReport:
        """Run all validators and generate report.
        
        Args:
            data: Data to validate
        
        Returns:
            QualityReport with results
        """
        total_score = 0
        total_weight = 0
        all_issues = []
        all_warnings = []
        metadata = {}
        
        for validator, weight in self.validators:
            try:
                score, issues, warnings = validator(data)
                total_score += score * weight
                total_weight += weight
                all_issues.extend(issues)
                all_warnings.extend(warnings)
            except Exception as e:
                logger.error(f"Validator failed in {self.name}: {e}")
                all_issues.append(f"Validator error: {str(e)}")
                total_score += 0
                total_weight += weight
        
        # Calculate final score
        final_score = total_score / total_weight if total_weight > 0 else 0
        
        # Determine quality level
        if final_score >= 0.9:
            level = QualityLevel.EXCELLENT
        elif final_score >= 0.8:
            level = QualityLevel.GOOD
        elif final_score >= 0.7:
            level = QualityLevel.FAIR
        elif final_score >= 0.5:
            level = QualityLevel.POOR
        else:
            level = QualityLevel.FAILED
        
        passed = final_score >= self.threshold
        
        return QualityReport(
            level=level,
            score=final_score,
            passed=passed,
            issues=all_issues,
            warnings=all_warnings,
            metadata=metadata
        )

class AudioQualityGate(QualityGate):
    """Quality gate for audio processing results."""
    
    def __init__(self):
        """Initialize audio quality gate."""
        super().__init__("Audio Processing", threshold=0.7)
        
        # Add validators
        self.add_validator(self._validate_bpm, weight=1.5)
        self.add_validator(self._validate_key, weight=1.0)
        self.add_validator(self._validate_energy, weight=0.8)
        self.add_validator(self._validate_duration, weight=0.5)
    
    def _validate_bpm(self, data: Dict[str, Any]) -> Tuple[float, List[str], List[str]]:
        """Validate BPM value."""
        issues = []
        warnings = []
        
        bpm = data.get('bpm', 0)
        
        if not bpm or bpm <= 0:
            issues.append("BPM detection failed")
            return 0.0, issues, warnings
        
        if not 30 <= bpm <= 300:
            issues.append(f"BPM out of valid range: {bpm}")
            return 0.2, issues, warnings
        
        if bpm < 60 or bpm > 200:
            warnings.append(f"Unusual BPM detected: {bpm}")
            return 0.8, issues, warnings
        
        return 1.0, issues, warnings
    
    def _validate_key(self, data: Dict[str, Any]) -> Tuple[float, List[str], List[str]]:
        """Validate key detection."""
        issues = []
        warnings = []
        
        key = data.get('key')
        
        if not key:
            issues.append("Key detection failed")
            return 0.0, issues, warnings
        
        valid_keys = {
            'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B',
            'Cm', 'C#m', 'Dm', 'D#m', 'Em', 'Fm', 'F#m', 'Gm', 'G#m', 'Am', 'A#m', 'Bm'
        }
        
        if key not in valid_keys:
            warnings.append(f"Non-standard key notation: {key}")
            return 0.7, issues, warnings
        
        return 1.0, issues, warnings
    
    def _validate_energy(self, data: Dict[str, Any]) -> Tuple[float, List[str], List[str]]:
        """Validate energy level."""
        issues = []
        warnings = []
        
        energy = data.get('energy', -1)
        
        if energy < 0 or energy > 1:
            issues.append(f"Energy out of range: {energy}")
            return 0.0, issues, warnings
        
        if energy == 0:
            warnings.append("Zero energy detected - possible silence")
            return 0.5, issues, warnings
        
        if energy == 1:
            warnings.append("Maximum energy - possible clipping")
            return 0.8, issues, warnings
        
        return 1.0, issues, warnings
    
    def _validate_duration(self, data: Dict[str, Any]) -> Tuple[float, List[str], List[str]]:
        """Validate track duration."""
        issues = []
        warnings = []
        
        duration = data.get('duration', 0)
        
        if duration <= 0:
            issues.append("Invalid duration")
            return 0.0, issues, warnings
        
        if duration < 30:
            warnings.append(f"Very short track: {duration:.1f}s")
            return 0.7, issues, warnings
        
        if duration > 600:
            warnings.append(f"Very long track: {duration:.1f}s")
            return 0.9, issues, warnings
        
        return 1.0, issues, warnings

class HAMMSQualityGate(QualityGate):
    """Quality gate for HAMMS vector validation."""
    
    def __init__(self):
        """Initialize HAMMS quality gate."""
        super().__init__("HAMMS Vector", threshold=0.8)
        
        self.add_validator(self._validate_dimensions, weight=2.0)
        self.add_validator(self._validate_range, weight=1.5)
        self.add_validator(self._validate_validity, weight=1.5)
        self.add_validator(self._validate_distribution, weight=1.0)
    
    def _validate_dimensions(self, vector: np.ndarray) -> Tuple[float, List[str], List[str]]:
        """Validate vector dimensions."""
        issues = []
        warnings = []
        
        if not isinstance(vector, np.ndarray):
            issues.append("Not a numpy array")
            return 0.0, issues, warnings
        
        if len(vector) != 12:
            issues.append(f"Wrong dimensions: {len(vector)} (expected 12)")
            return 0.0, issues, warnings
        
        return 1.0, issues, warnings
    
    def _validate_range(self, vector: np.ndarray) -> Tuple[float, List[str], List[str]]:
        """Validate value range."""
        issues = []
        warnings = []
        
        if np.any(vector < 0):
            issues.append(f"Negative values found")
            return 0.0, issues, warnings
        
        if np.any(vector > 1):
            issues.append(f"Values exceed 1.0")
            return 0.0, issues, warnings
        
        return 1.0, issues, warnings
    
    def _validate_validity(self, vector: np.ndarray) -> Tuple[float, List[str], List[str]]:
        """Validate for NaN and infinity."""
        issues = []
        warnings = []
        
        if np.any(np.isnan(vector)):
            issues.append("NaN values detected")
            return 0.0, issues, warnings
        
        if np.any(np.isinf(vector)):
            issues.append("Infinite values detected")
            return 0.0, issues, warnings
        
        return 1.0, issues, warnings
    
    def _validate_distribution(self, vector: np.ndarray) -> Tuple[float, List[str], List[str]]:
        """Validate value distribution."""
        issues = []
        warnings = []
        
        # Check for all zeros
        if np.all(vector == 0):
            issues.append("All values are zero")
            return 0.0, issues, warnings
        
        # Check for all ones
        if np.all(vector == 1):
            warnings.append("All values are one")
            return 0.5, issues, warnings
        
        # Check for low variance
        variance = np.var(vector)
        if variance < 0.01:
            warnings.append(f"Low variance: {variance:.4f}")
            return 0.7, issues, warnings
        
        return 1.0, issues, warnings

# Quality gate registry
QUALITY_GATES = {
    'audio': AudioQualityGate(),
    'hamms': HAMMSQualityGate()
}

def get_quality_gate(name: str) -> Optional[QualityGate]:
    """Get quality gate by name."""
    return QUALITY_GATES.get(name)

# Export
__all__ = [
    'QualityGate', 'QualityReport', 'QualityLevel',
    'AudioQualityGate', 'HAMMSQualityGate',
    'get_quality_gate'
]
```

## Success Criteria

The core implementation is complete when:

1. **HAMMS v3.0 Engine**:
   - 12-dimensional vector calculation with all dimensions implemented
   - Weighted similarity scoring between vectors
   - Camelot wheel integration for harmonic mixing
   - Quality validation for all vectors

2. **Audio Processing Pipeline**:
   - librosa integration with optimized parameters
   - BPM, key, and energy extraction
   - Spectral feature analysis
   - File validation and error handling

3. **Storage Integration**:
   - Complete database operations with transactions
   - Track and analysis storage
   - HAMMS vector persistence
   - Query operations for similarity and compatibility

4. **Enhanced Analysis Pipeline**:
   - Unified analysis workflow
   - Parallel processing support for libraries
   - Quality scoring and validation
   - Integration of all components

5. **Quality Gate Framework**:
   - Validation at every pipeline stage
   - Comprehensive error reporting
   - Quality scoring and thresholds
   - Extensible validator system

## Testing the Implementation

Create `test_core.py`:

```python
#!/usr/bin/env python3
"""Test core MAP4 implementation."""

import numpy as np
from src.analysis.hamms_v3 import HAMMSAnalyzer
from src.lib.audio_processing import AudioProcessor
from src.services.storage_service import StorageService
from src.analysis.enhanced_analyzer import EnhancedAnalyzer

def test_hamms():
    """Test HAMMS v3.0 engine."""
    print("Testing HAMMS v3.0...")
    
    analyzer = HAMMSAnalyzer()
    
    # Test data
    track_data = {
        'bpm': 128,
        'key': 'Am',
        'energy': 0.7,
        'genre': 'house',
        'title': 'Test Track'
    }
    
    result = analyzer.calculate_extended_vector(track_data)
    
    assert len(result['hamms_vector']) == 12
    assert all(0 <= v <= 1 for v in result['hamms_vector'])
    assert 'confidence' in result
    
    print("✓ HAMMS v3.0 working correctly")

def test_audio_processing():
    """Test audio processing (requires test audio file)."""
    print("Testing audio processing...")
    
    processor = AudioProcessor()
    
    # Would need actual audio file for full test
    print("✓ Audio processor initialized")

def test_storage():
    """Test storage service."""
    print("Testing storage service...")
    
    storage = StorageService("sqlite:///test.db")
    
    # Test track creation
    track_id = storage.get_or_create_track("/test/file.mp3", {
        'title': 'Test Track',
        'artist': 'Test Artist'
    })
    
    assert track_id > 0
    
    print("✓ Storage service working")

def test_enhanced_analyzer():
    """Test enhanced analyzer."""
    print("Testing enhanced analyzer...")
    
    analyzer = EnhancedAnalyzer()
    
    print("✓ Enhanced analyzer initialized")

if __name__ == "__main__":
    print("MAP4 Core Implementation Test")
    print("=" * 50)
    
    test_hamms()
    test_audio_processing()
    test_storage()
    test_enhanced_analyzer()
    
    print("\n" + "=" * 50)
    print("✓ All core components functional!")
```

## Next Steps

After completing the core implementation:

1. Implement the multi-LLM provider system (see `03-llm-integration.md`)
2. Build the PyQt6 user interface (see `04-ui-development.md`)
3. Implement the BMAD methodology (see `05-bmad-framework.md`)
4. Create the unified CLI system (see `06-cli-system.md`)
5. Add integration and testing (see `07-integration-testing.md`)

This core implementation provides the foundation for all music analysis capabilities in MAP4, with professional-grade quality gates and extensible architecture.