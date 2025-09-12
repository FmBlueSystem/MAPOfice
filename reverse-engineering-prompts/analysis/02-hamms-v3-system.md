# HAMMS v3.0 - 12-Dimensional Harmonic Analysis System

## Overview
HAMMS v3.0 (Harmonic Analysis for Music Mixing System) is the core music analysis engine that generates 12-dimensional feature vectors for comprehensive music analysis and compatibility scoring. It's designed specifically for DJ and music production workflows.

## Core Concept
Unlike traditional audio analysis that focuses on single features, HAMMS v3.0 creates a multi-dimensional "fingerprint" of each track that captures:
- **Harmonic Content**: Key signature and harmonic complexity
- **Rhythmic Properties**: BPM, tempo stability, rhythmic patterns
- **Timbral Characteristics**: Spectral centroid, dynamic range, acousticness
- **Musical Semantics**: Danceability, valence, instrumentalness

## The 12 Dimensions

### 1. BPM (Tempo) - Weight: 1.3
```python
def _normalize_bpm(self, bpm: float) -> float:
    """Normalize BPM to 0-1 range (60-200 BPM)"""
    return np.clip((float(bpm) - 60) / 140, 0, 1)
```
- **Range**: 60-200 BPM normalized to [0, 1]
- **Importance**: Most critical for DJ mixing
- **Usage**: Beatmatching, tempo transitions

### 2. Key Signature - Weight: 1.4
```python
def _camelot_to_numeric(self, key: str) -> float:
    """Convert key to Camelot wheel position (0-1)"""
    # 1A-12A = 0.0-0.458, 1B-12B = 0.5-0.958
```
- **System**: Camelot wheel notation (1A-12B)
- **Importance**: Most critical for harmonic compatibility
- **Usage**: Harmonic mixing, key-based playlist generation

### 3. Energy Level - Weight: 1.2
```python
energy = float(np.clip(energy or 0.5, 0, 1))
```
- **Range**: [0, 1] representing track intensity
- **Calculation**: RMS energy from audio analysis
- **Usage**: Energy curve management in sets

### 4. Danceability - Weight: 0.9
```python
def _calculate_danceability(self, track_data: Dict) -> float:
    # Genre-based mapping + BPM influence + energy factor
    dance_genres = {
        'house': 0.9, 'techno': 0.95, 'trance': 0.8,
        'edm': 0.9, 'disco': 0.85, 'funk': 0.8
    }
```
- **Calculation**: Genre + BPM + energy analysis
- **Optimal BPM Range**: 110-140 BPM for maximum danceability
- **Usage**: Club-ready track identification

### 5. Valence (Mood) - Weight: 0.8
```python
def _calculate_valence(self, track_data: Dict) -> float:
    # Genre influence + key signature (major vs minor)
    positive_genres = {'house': 0.8, 'disco': 0.9, 'pop': 0.7}
    key_valence = 0.7 if 'B' in key else 0.4  # Major vs Minor
```
- **Range**: [0, 1] representing musical positivity
- **Factors**: Genre characteristics + major/minor key
- **Usage**: Mood-based playlist curation

### 6. Acousticness - Weight: 0.6
```python
acoustic_genres = {'folk': 0.9, 'acoustic': 0.95, 'jazz': 0.7}
electronic_genres = {'house': 0.1, 'techno': 0.05, 'edm': 0.1}
```
- **Range**: [0, 1] where 0=electronic, 1=acoustic
- **Usage**: Production style categorization

### 7. Instrumentalness - Weight: 0.5
```python
instrumental_genres = {'ambient': 0.8, 'classical': 0.9}
vocal_genres = {'pop': 0.1, 'rock': 0.2, 'r&b': 0.1}
```
- **Range**: [0, 1] where 0=vocal, 1=instrumental
- **Detection**: Genre analysis + title keywords
- **Usage**: Vocal vs instrumental mixing decisions

### 8. Rhythmic Pattern Complexity - Weight: 1.1
```python
rhythm_map = {
    'jazz': 0.9, 'prog': 0.8, 'techno': 0.8,
    'house': 0.7, 'pop': 0.4, 'ambient': 0.2
}
```
- **Range**: [0, 1] representing rhythmic complexity
- **Factors**: Genre + BPM influence
- **Usage**: Mixing complexity assessment

### 9. Spectral Centroid (Brightness) - Weight: 0.7
```python
bright_genres = {'house': 0.7, 'techno': 0.8, 'edm': 0.8}
dark_genres = {'ambient': 0.3, 'darkwave': 0.25}
```
- **Range**: [0, 1] representing timbral brightness
- **Usage**: Frequency content matching

### 10. Tempo Stability - Weight: 0.9
```python
stable_genres = {'house': 0.9, 'techno': 0.95, 'edm': 0.85}
unstable_genres = {'jazz': 0.4, 'classical': 0.5}
```
- **Range**: [0, 1] representing beat consistency
- **Importance**: Critical for seamless mixing
- **Usage**: Beatmatching reliability assessment

### 11. Harmonic Complexity - Weight: 0.8
```python
def _calculate_harmonic_complexity(self, track_data: Dict) -> float:
    key_complexity = 0.6 if 'A' in key else 0.4  # Minor = more complex
    complex_genres = {'jazz': 0.9, 'classical': 0.8, 'prog': 0.8}
```
- **Factors**: Key signature (minor = complex) + genre
- **Usage**: Harmonic compatibility assessment

### 12. Dynamic Range - Weight: 0.6
```python
dynamic_genres = {'classical': 0.9, 'jazz': 0.8, 'rock': 0.7}
compressed_genres = {'pop': 0.3, 'edm': 0.25, 'house': 0.3}
```
- **Range**: [0, 1] representing dynamic variation
- **Usage**: Loudness/compression matching

## Vector Calculation Process

### 1. Input Validation
```python
def calculate_extended_vector(self, track_data: Dict[str, Any]) -> np.ndarray:
    # Input validation
    if not isinstance(track_data, dict):
        raise TypeError(f"Track data must be dictionary")
```

### 2. Feature Extraction
```python
# Extract basic features with defaults
bpm = track_data.get('bpm', 120.0)
key = track_data.get('key', 'Am') 
energy = track_data.get('energy', 0.5)
genre = track_data.get('genre', '').lower()
```

### 3. Dimension Calculation
```python
# Calculate extended dimensions
danceability = self._calculate_danceability(track_data)
valence = self._calculate_valence(track_data)
acousticness = self._calculate_acousticness(track_data)
# ... etc for all 12 dimensions
```

### 4. Vector Assembly
```python
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
```

### 5. Quality Gate Validation
```python
# Quality gate validation
assert len(vector) == 12, f"Vector must have 12 dimensions, got {len(vector)}"
assert np.all((vector >= 0) & (vector <= 1)), f"All values must be 0-1"
assert not np.any(np.isnan(vector)), f"No NaN values allowed"
assert not np.any(np.isinf(vector)), f"No infinite values allowed"
```

## Similarity Calculation

### Weighted Distance Metrics
```python
def calculate_similarity(self, vector1: np.ndarray, vector2: np.ndarray):
    # Apply dimension weights
    weights = np.array(list(self.DIMENSION_WEIGHTS.values()))
    weighted_v1 = vector1 * weights
    weighted_v2 = vector2 * weights
    
    # Euclidean distance (inverted to similarity)
    euclidean_dist = np.linalg.norm(weighted_v1 - weighted_v2)
    euclidean_sim = 1.0 - (euclidean_dist / max_distance)
    
    # Cosine similarity
    cosine_sim = np.dot(weighted_v1, weighted_v2) / (norm_v1 * norm_v2)
    
    # Combined similarity
    overall_similarity = euclidean_sim * 0.6 + cosine_sim * 0.4
```

### Compatibility Scoring
The HAMMS system generates similarity scores between 0 and 1:
- **0.9-1.0**: Excellent compatibility (same key, similar BPM, matching energy)
- **0.8-0.9**: Good compatibility (related keys, compatible BPMs)
- **0.7-0.8**: Fair compatibility (workable with skill)
- **0.6-0.7**: Poor compatibility (challenging mix)
- **0.0-0.6**: Incompatible (different genres, clashing keys/BPMs)

## Integration with Audio Processing

### From Audio Features to HAMMS
```python
# Basic audio analysis provides foundation
basic_result = audio_processing.analyze_track(track_path)

# Enhanced track data for HAMMS calculation
track_data = {
    'bmp': basic_result.get('bpm', 120.0),
    'key': basic_result.get('key', 'Am'),
    'energy': basic_result.get('energy', 0.5),
    'title': Path(track_path).stem,
    'artist': 'Unknown'
}

# Calculate 12-dimensional HAMMS vector
hamms_vector = hamms_analyzer.calculate_extended_vector(track_data)
```

### Storage and Retrieval
```python
# Store HAMMS vector in database
hamms_record = HAMMSAdvanced()
hamms_record.set_vector_12d(result.hamms_vector)
hamms_record.set_dimension_scores(result.hamms_dimensions)

# Retrieve and use for compatibility
compatible_tracks = hamms_analyzer.get_compatible_tracks(
    seed_vector, candidate_vectors, threshold=0.7, limit=20
)
```

## Use Cases

### 1. Playlist Generation
```python
# Find tracks compatible with seed track
seed_vector = hamms_analyzer.calculate_extended_vector(seed_data)
candidates = [hamms_analyzer.calculate_extended_vector(t) for t in library]
compatible = hamms_analyzer.get_compatible_tracks(seed_vector, candidates)
```

### 2. DJ Set Planning
- **Energy Curve Management**: Use energy dimension for set flow
- **Harmonic Mixing**: Use key + harmonic complexity for smooth transitions
- **BPM Progression**: Use BPM + tempo stability for beatmatching

### 3. Music Discovery
- **Similar Track Finding**: Use overall similarity scoring
- **Genre Classification**: Use genre-specific dimension patterns
- **Mood-based Filtering**: Use valence + energy dimensions

### 4. Quality Control
- **Analysis Validation**: Confidence scoring based on vector quality
- **Data Integrity**: Quality gates ensure vector consistency
- **Error Detection**: NaN/infinity checks prevent corrupted data

## Advanced Features

### Camelot Wheel Integration
```python
CAMELOT_WHEEL = {
    'C': '8B', 'Am': '8A', 'G': '9B', 'Em': '9A',
    'D': '10B', 'Bm': '10A', 'A': '11B', 'F#m': '11A',
    # ... complete wheel mapping
}
```

### Genre-Aware Analysis
The system uses genre information to improve dimension calculations:
- **Electronic genres**: Higher tempo stability, lower acousticness
- **Acoustic genres**: Higher acousticness, variable tempo stability
- **Dance genres**: Higher danceability, specific BPM ranges
- **Complex genres**: Higher rhythmic and harmonic complexity

### Confidence Scoring
```python
def _calculate_confidence(self, track_data: Dict, hamms_vector: np.ndarray) -> float:
    confidence = 0.8  # Base confidence
    
    # Reduce for missing/invalid data
    if not track_data.get('bpm') or track_data.get('bpm') <= 0:
        confidence -= 0.2
    if not track_data.get('key'):
        confidence -= 0.1
    
    # Check vector quality
    if np.any(np.isnan(hamms_vector)) or np.any(np.isinf(hamms_vector)):
        confidence = 0.0
    
    return np.clip(confidence, 0.0, 1.0)
```

## Performance Optimization
- **Vector Caching**: 1000-item LRU cache for frequent calculations
- **Numpy Operations**: Vectorized operations for batch similarity calculations
- **Quality Gates**: Early validation to prevent expensive computations on bad data
- **Dimension Weights**: Pre-computed weight arrays for fast similarity scoring

The HAMMS v3.0 system provides the mathematical foundation for all compatibility scoring and playlist generation in MAP4, offering a sophisticated yet computationally efficient approach to music analysis that understands the practical needs of DJs and music professionals.