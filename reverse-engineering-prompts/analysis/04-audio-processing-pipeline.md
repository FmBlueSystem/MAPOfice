# Audio Processing Pipeline with librosa

## Overview
The audio processing pipeline is the foundation of MAP4's analysis capabilities, extracting fundamental musical features from audio files using librosa. This module provides BPM detection, key identification, energy calculation, and HAMMS vector generation with robust error handling and quality gates.

## Core Architecture

### Main Entry Point (`src/lib/audio_processing.py`)
```python
def analyze_track(path: str, progress_callback: Optional[ProgressCallback] = None) -> Dict[str, object]:
    """Analyze an audio track and return BPM, key, energy, and HAMMS vector.
    
    Quality Gates:
    1. Input validation and file checks
    2. Supported format validation  
    3. File size and corruption checks
    4. Result validation and contract enforcement
    """
```

### Progressive Analysis Pipeline
The analysis follows a structured 5-stage pipeline with progress reporting:

1. **Audio Loading** (`AnalysisStage.AUDIO_LOADING`)
2. **BPM Detection** (`AnalysisStage.BPM_DETECTION`)
3. **Key Detection** (`AnalysisStage.KEY_DETECTION`)
4. **Energy Calculation** (`AnalysisStage.ENERGY_CALCULATION`)
5. **HAMMS Computation** (`AnalysisStage.HAMMS_COMPUTATION`)

## Quality Gates System

### Stage 1: Input Validation
```python
# QUALITY GATE 1: Input validation
if not isinstance(path, str):
    raise TypeError(f"Path must be string, got {type(path)}")

if not path.strip():
    raise ValueError("Path cannot be empty")
    
if not os.path.exists(path):
    raise FileNotFoundError(f"File not found: {path}")

if not os.path.isfile(path):
    raise ValueError(f"Path is not a file: {path}")
```

### Stage 2: Format Validation
```python
# QUALITY GATE 2: Supported format validation
SUPPORTED_EXTS = {'.wav', '.mp3', '.flac', '.aac', '.ogg', '.m4a'}
file_ext = os.path.splitext(path)[1].lower()
if file_ext not in SUPPORTED_EXTS:
    raise ValueError(f"Unsupported audio format: {file_ext}")
```

### Stage 3: File Integrity Checks
```python
# QUALITY GATE 3: File size and corruption checks
try:
    file_size = os.path.getsize(path)
    if file_size == 0:
        print(f"WARNING: Processing empty file (test mode): {path}")
    elif file_size < 100:  # Minimum viable audio file size
        raise ValueError(f"File too small to be valid audio: {file_size} bytes")
except OSError as e:
    raise ValueError(f"Cannot access file: {e}")
```

### Stage 4: Result Contract Enforcement
```python
# QUALITY GATE 4: Result validation and contract enforcement
if not isinstance(result, dict):
    raise ValueError(f"Analysis result must be dictionary, got {type(result)}")

required_keys = {"bpm", "key", "energy", "hamms"}
missing_keys = required_keys - set(result.keys())
if missing_keys:
    raise ValueError(f"Analysis result missing required keys: {missing_keys}")

# Validate HAMMS vector structure
hamms = result.get("hamms")
if not isinstance(hamms, list) or len(hamms) != 12:
    raise ValueError(f"HAMMS must be 12-element list")

# Validate numeric ranges
bpm = result.get("bpm")
if bmp and (not isinstance(bpm, (int, float)) or bpm <= 0 or bpm > 300):
    raise ValueError(f"BPM must be positive number ≤ 300, got {bpm}")

energy = result.get("energy")
if energy and (not isinstance(energy, (int, float)) or not 0 <= energy <= 1):
    raise ValueError(f"Energy must be in range [0,1], got {energy}")
```

## Audio Loading Stage

### Optimized librosa Configuration
```python
def _analyze_with_librosa(path: str, progress_callback: ProgressCallback) -> Dict[str, object]:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", UserWarning)
        
        # Stage 1: Audio Loading
        progress_callback(AnalysisStage.AUDIO_LOADING, 0.0, "Loading audio file", path)
        
        try:
            # Load with specific parameters to avoid mel filter issues
            y, sr = librosa.load(path, sr=22050, mono=True, duration=120)
            if y.size == 0:
                raise ValueError("no audio samples")
        except Exception as e:
            progress_callback(AnalysisStage.AUDIO_LOADING, 1.0, f"Audio loading failed: {str(e)}", path)
            raise
```

**Key Parameters:**
- **Sample Rate**: 22050 Hz (optimal for music analysis, reduces computation)
- **Mono**: Convert to single channel to simplify analysis
- **Duration Limit**: 120 seconds maximum to prevent hanging on very long files
- **Error Handling**: Comprehensive exception handling with progress reporting

## BPM Detection Stage

### Beat Tracking Algorithm
```python
# Stage 2: BPM Detection
progress_callback(AnalysisStage.BPM_DETECTION, 0.0, "Starting BPM analysis", path)

try:
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr, units='time')
    tempo_val = float(tempo) if tempo is not None else 0.0
except Exception as e:
    progress_callback(AnalysisStage.BPM_DETECTION, 1.0, f"BPM detection failed: {str(e)}", path)
    tempo_val = 0.0

progress_callback(AnalysisStage.BPM_DETECTION, 1.0, f"BPM detected: {tempo_val:.1f}", path)
```

**Algorithm Details:**
- **Method**: librosa.beat.beat_track() using onset detection
- **Units**: Time-based analysis for better accuracy
- **Fallback**: Returns 0.0 on failure (handled by downstream systems)
- **Validation**: BPM must be positive and ≤ 300

## Key Detection Stage

### Chromatic Analysis Approach
```python
# Stage 3: Key Detection
progress_callback(AnalysisStage.KEY_DETECTION, 0.0, "Starting key analysis", path)

try:
    # Calculate chroma features (used for both key detection and HAMMS)
    progress_callback(AnalysisStage.KEY_DETECTION, 0.3, "Computing chroma features", path)
    # Use simpler chroma_stft instead of chroma_cqt to avoid hanging
    chroma = librosa.feature.chroma_stft(y=y, sr=sr, n_fft=2048, hop_length=512)
    chroma_mean = chroma.mean(axis=1)
    
    progress_callback(AnalysisStage.KEY_DETECTION, 0.7, "Analyzing harmonic content", path)
    
    # Simple key estimation: index of max pitch class
    pitch_classes = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    key_idx = int(np.argmax(chroma_mean))
    key_name = pitch_classes[key_idx]
```

**Technical Details:**
- **Chroma Features**: Short-Time Fourier Transform (STFT) based chromagram
- **Window Size**: 2048 samples (good frequency resolution)
- **Hop Length**: 512 samples (good time resolution)
- **Key Estimation**: Simple maximum pitch class approach
- **Pitch Classes**: Standard 12-tone equal temperament system
- **Fallback**: Defaults to "C" on analysis failure

### Alternative: Complex Key Detection
For more sophisticated key detection, the system could be extended with:
```python
# Advanced key detection using Krumhansl-Schmuckler profiles
def advanced_key_detection(chroma_mean):
    """Advanced key detection using music theory profiles"""
    
    # Krumhansl-Schmuckler key profiles
    major_profile = [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
    minor_profile = [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]
    
    # Calculate correlations for all 24 keys
    correlations = []
    for i in range(12):
        # Major key
        major_corr = np.corrcoef(chroma_mean, np.roll(major_profile, i))[0,1]
        correlations.append(('major', i, major_corr))
        
        # Minor key  
        minor_corr = np.corrcoef(chroma_mean, np.roll(minor_profile, i))[0,1]
        correlations.append(('minor', i, minor_corr))
    
    # Find best correlation
    best_key = max(correlations, key=lambda x: x[2])
    return format_key_name(best_key[1], best_key[0])
```

## Energy Calculation Stage

### RMS Energy Analysis
```python
# Stage 4: Energy Calculation
progress_callback(AnalysisStage.ENERGY_CALCULATION, 0.0, "Calculating energy levels", path)

try:
    rms = librosa.feature.rms(y=y).mean()
    energy = float(np.clip(rms, 0.0, 1.0))
except Exception as e:
    progress_callback(AnalysisStage.ENERGY_CALCULATION, 1.0, f"Energy calculation failed: {str(e)}", path)
    energy = 0.5  # Default energy

progress_callback(AnalysisStage.ENERGY_CALCULATION, 1.0, f"Energy calculated: {energy:.3f}", path)
```

**Algorithm Details:**
- **Method**: Root Mean Square (RMS) energy calculation
- **Normalization**: Clipped to [0, 1] range for consistency
- **Frame-wise**: Computed across all frames then averaged
- **Fallback**: 0.5 (medium energy) on calculation failure

### Alternative Energy Metrics
The system supports multiple energy calculation approaches:
```python
# Alternative energy calculations
def calculate_spectral_energy(y, sr):
    """Spectral-based energy calculation"""
    spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
    return np.mean(spectral_centroids) / (sr/2)  # Normalized by Nyquist

def calculate_zero_crossing_rate(y):
    """Zero crossing rate as rhythmic energy indicator"""
    zcr = librosa.feature.zero_crossing_rate(y)[0]
    return np.mean(zcr)

def calculate_spectral_rolloff_energy(y, sr):
    """High-frequency energy based on spectral rolloff"""
    rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)[0]
    return np.mean(rolloff) / (sr/2)  # Normalized
```

## HAMMS Vector Computation Stage

### Chromagram-Based HAMMS Generation
```python
# Stage 5: HAMMS Computation
progress_callback(AnalysisStage.HAMMS_COMPUTATION, 0.0, "Computing HAMMS features", path)

try:
    progress_callback(AnalysisStage.HAMMS_COMPUTATION, 0.5, "Normalizing harmonic vector", path)
    
    # Create HAMMS-like vector (L1-normalized chroma)
    l1 = np.sum(np.abs(chroma_mean))
    if l1 == 0:
        hamms = [float(1.0 / 12.0)] * 12  # Equal distribution
    else:
        hamms = (np.abs(chroma_mean) / l1).tolist()
        
except Exception as e:
    progress_callback(AnalysisStage.HAMMS_COMPUTATION, 1.0, f"HAMMS computation failed: {str(e)}", path)
    hamms = [float(1.0 / 12.0)] * 12  # Equal distribution

progress_callback(AnalysisStage.HAMMS_COMPUTATION, 1.0, "HAMMS computation complete", path)
```

**Technical Implementation:**
- **Source Data**: 12-bin chromagram from key detection stage
- **Normalization**: L1 normalization (Manhattan distance = 1)
- **Vector Length**: Exactly 12 dimensions (validated by quality gates)
- **Fallback**: Equal distribution [0.0833...] × 12 on failure
- **Data Type**: Python list of float values for JSON serialization

### Advanced HAMMS Enhancement
The basic chromagram HAMMS is enhanced by the HAMMS v3.0 system:
```python
# Integration with HAMMS v3.0 for full 12-dimensional analysis
def integrate_with_hamms_v3(basic_hamms, track_metadata):
    """Enhance basic chromagram HAMMS with v3.0 analysis"""
    
    hamms_v3 = HAMMSAnalyzerV3()
    
    # Use basic HAMMS as harmonic foundation
    enhanced_track_data = {
        'hamms_basic': basic_hamms,  # 12D chromagram
        'bpm': track_metadata['bpm'],
        'key': track_metadata['key'], 
        'energy': track_metadata['energy'],
        'genre': track_metadata.get('genre', ''),
        'title': track_metadata.get('title', ''),
        'artist': track_metadata.get('artist', '')
    }
    
    # Generate full 12-dimensional HAMMS vector
    return hamms_v3.calculate_extended_vector(enhanced_track_data)
```

## Metadata Extraction

### Multi-Format Metadata Support
```python
def _extract_metadata(path: str) -> Dict[str, object]:
    """Extract ISRC and other metadata from audio file"""
    metadata = {}
    
    try:
        from mutagen import File
        audio_file = File(path)
        
        if audio_file is not None:
            # Extract ISRC (International Standard Recording Code)
            isrc_keys = ['TSRC', 'ISRC', 'isrc']
            for key in isrc_keys:
                if key in audio_file:
                    isrc_value = str(audio_file[key][0]) if isinstance(audio_file[key], list) else str(audio_file[key])
                    if isrc_value and len(isrc_value.strip()) > 0:
                        metadata['isrc'] = isrc_value.strip()
                        break
            
            # Extract standard metadata
            title_keys = ['TIT2', 'TITLE', 'title', '©nam']
            artist_keys = ['TPE1', 'ARTIST', 'artist', '©ART']
            album_keys = ['TALB', 'ALBUM', 'album', '©alb']
```

**Supported Formats:**
- **MP3**: ID3v1, ID3v2 tags
- **FLAC**: Vorbis comments
- **MP4/M4A**: iTunes-style metadata
- **OGG**: Vorbis comments
- **WAV**: INFO chunks (limited support)

### Metadata Field Mapping
```python
# Comprehensive metadata field mapping
METADATA_FIELD_MAPPING = {
    'title': ['TIT2', 'TITLE', 'title', '©nam', 'Title'],
    'artist': ['TPE1', 'ARTIST', 'artist', '©ART', 'Artist'],
    'album': ['TALB', 'ALBUM', 'album', '©alb', 'Album'],
    'albumartist': ['TPE2', 'ALBUMARTIST', 'albumartist', 'aART'],
    'date': ['TDRC', 'DATE', 'date', '©day'],
    'year': ['TYER', 'YEAR', 'year'],
    'genre': ['TCON', 'GENRE', 'genre', '©gen'],
    'track': ['TRCK', 'TRACKNUMBER', 'tracknumber'],
    'isrc': ['TSRC', 'ISRC', 'isrc'],
    'bpm': ['TBPM', 'BPM', 'bpm'],
    'key': ['TKEY', 'KEY', 'key', 'INITIALKEY']
}
```

## Error Handling and Resilience

### Graceful Degradation Strategy
```python
def analyze_track(path: str, progress_callback: Optional[ProgressCallback] = None) -> Dict[str, object]:
    """Main entry point with comprehensive error handling"""
    
    # Attempt analysis with fallback
    try:
        result = _analyze_with_librosa(path, progress_callback)
    except Exception as e:
        # Graceful fallback when analysis libs unavailable
        print(f"WARNING: Analysis failed for {path}: {e}")
        progress_callback(AnalysisStage.AUDIO_LOADING, 1.0, "Analysis failed, using fallback", path)
        
        # Return safe default values
        hamms: List[float] = [0.0] * 12
        result = {
            "bpm": None, 
            "key": None, 
            "energy": None, 
            "hamms": hamms
        }
    
    return result
```

### Warning System
The audio processing pipeline uses a comprehensive warning system:
- **INFO**: Non-critical information (e.g., "mutagen not available")
- **WARNING**: Recoverable errors (e.g., "Metadata extraction failed")
- **ERROR**: Critical failures that prevent analysis

### Progress Reporting Integration
```python
# Progress callback system for UI integration
class AnalysisStage(Enum):
    AUDIO_LOADING = "audio_loading"
    BPM_DETECTION = "bpm_detection"
    KEY_DETECTION = "key_detection"
    ENERGY_CALCULATION = "energy_calculation"
    HAMMS_COMPUTATION = "hamms_computation"

def create_no_op_callback() -> ProgressCallback:
    """Create a no-op progress callback for CLI usage"""
    def no_op(stage: AnalysisStage, progress: float, message: str, file_path: str):
        pass
    return no_op
```

## Performance Optimization

### librosa Configuration Tuning
```python
# Optimized parameters for speed vs accuracy
OPTIMAL_LIBROSA_PARAMS = {
    'sr': 22050,        # Half CD quality, sufficient for analysis
    'n_fft': 2048,      # Good frequency resolution
    'hop_length': 512,   # 4x overlap for stability
    'duration': 120,     # Limit analysis to 2 minutes
    'mono': True        # Single channel reduces computation 50%
}
```

### Memory Management
```python
# Memory-efficient processing for large files
def process_in_chunks(y, sr, chunk_duration=30):
    """Process audio in chunks to manage memory usage"""
    chunk_samples = int(chunk_duration * sr)
    
    for i in range(0, len(y), chunk_samples):
        chunk = y[i:i + chunk_samples]
        yield process_chunk(chunk, sr)
```

### Caching Strategy
The audio processing results are cached in the database to avoid reprocessing:
```python
# Integration with storage caching
def get_cached_analysis(self, track_path: str, file_mtime: float) -> Optional[Dict]:
    """Return cached analysis if file hasn't changed"""
    
    cached = self.storage.get_cached_analysis(track_path, file_mtime)
    if cached and abs(cached['file_mtime'] - file_mtime) < 1e-6:
        return cached  # File unchanged, use cached result
    
    return None  # File changed or no cache, need fresh analysis
```

## Integration Points

### Database Storage
```python
# Storage integration with full metadata
def store_analysis_results(track_path: str, analysis_result: Dict):
    """Store complete analysis results in database"""
    
    storage_data = {
        'bpm': analysis_result['bpm'],
        'key': analysis_result['key'],
        'energy': analysis_result['energy'],
        'hamms': analysis_result['hamms'],
        'title': analysis_result.get('title'),
        'artist': analysis_result.get('artist'),
        'album': analysis_result.get('album'),
        'isrc': analysis_result.get('isrc'),
        'file_mtime': os.path.getmtime(track_path),
        'analysis_source': 'librosa',
        'source_confidence': calculate_analysis_confidence(analysis_result)
    }
    
    storage.add_analysis(track_path, storage_data)
```

### HAMMS v3.0 Integration
```python
# Enhanced analysis pipeline integration
class EnhancedAnalyzer:
    def analyze_track(self, track_path: str) -> EnhancedAnalysisResult:
        # 1. Basic audio processing
        basic_analysis = audio_processing.analyze_track(track_path)
        
        # 2. Enhanced HAMMS calculation
        hamms_v3_result = self.hamms_analyzer.analyze_track(track_path)
        
        # 3. Combine results
        return combine_analysis_results(basic_analysis, hamms_v3_result)
```

The audio processing pipeline provides the robust foundation for all subsequent analysis in MAP4, with comprehensive error handling, quality gates, and optimizations that ensure reliable operation across a wide variety of audio files and system configurations.