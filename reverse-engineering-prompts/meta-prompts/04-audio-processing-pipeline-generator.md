# Audio Processing Pipeline Generator Meta-Prompt

## Overview
This meta-prompt generates comprehensive reproduction prompts for creating sophisticated audio processing pipelines with feature extraction, quality gates, batch processing, and configurable analysis systems. Based on MAP4's robust audio processing architecture.

## Meta-Prompt Template

### Audio Processing Configuration Parameters
Configure your audio processing pipeline:

```yaml
# Audio Processing Pipeline Configuration
PIPELINE_CONFIG:
  pipeline_name: "{PIPELINE_NAME}"                # e.g., "Music Analyzer", "Audio Processor"
  processing_focus: "{PROCESSING_FOCUS}"          # "MUSIC", "SPEECH", "GENERAL", "BROADCAST"
  complexity_level: "{COMPLEXITY}"                # "BASIC", "INTERMEDIATE", "ADVANCED", "PROFESSIONAL"
  
AUDIO_LIBRARIES:
  primary_library: "{PRIMARY_LIBRARY}"            # "librosa", "essentia", "audioflux", "pydub"
  secondary_library: "{SECONDARY_LIBRARY}"        # Optional fallback library
  format_support: [{SUPPORTED_FORMATS}]           # ["mp3", "wav", "flac", "m4a", "ogg"]

PROCESSING_CONFIG:
  sample_rate: {SAMPLE_RATE}                      # 22050, 44100, 48000
  frame_size: {FRAME_SIZE}                        # 1024, 2048, 4096
  hop_length: {HOP_LENGTH}                        # 512, 1024
  max_duration: {MAX_DURATION}                    # 300 (seconds)
  mono_conversion: {MONO_CONVERSION}               # true/false
  normalization: {NORMALIZATION}                  # true/false

FEATURE_EXTRACTION:
  spectral_features: {SPECTRAL_FEATURES}          # true/false
  temporal_features: {TEMPORAL_FEATURES}          # true/false
  harmonic_features: {HARMONIC_FEATURES}          # true/false
  rhythm_features: {RHYTHM_FEATURES}              # true/false
  energy_features: {ENERGY_FEATURES}              # true/false
  timbral_features: {TIMBRAL_FEATURES}            # true/false

QUALITY_GATES:
  enable_quality_gates: {QUALITY_GATES}           # true/false
  corruption_detection: {CORRUPTION_DETECTION}     # true/false
  silence_detection: {SILENCE_DETECTION}          # true/false
  clipping_detection: {CLIPPING_DETECTION}        # true/false
  snr_analysis: {SNR_ANALYSIS}                    # true/false

PERFORMANCE:
  batch_processing: {BATCH_PROCESSING}            # true/false
  parallel_processing: {PARALLEL_PROCESSING}      # true/false
  caching: {CACHING}                              # true/false
  memory_optimization: {MEMORY_OPTIMIZATION}      # true/false
  progress_tracking: {PROGRESS_TRACKING}          # true/false

OUTPUT_OPTIONS:
  feature_vectors: {FEATURE_VECTORS}              # true/false
  spectrograms: {SPECTROGRAMS}                    # true/false
  metadata_extraction: {METADATA_EXTRACTION}      # true/false
  analysis_reports: {ANALYSIS_REPORTS}            # true/false
```

## Generated Audio Processing Pipeline Template

Based on the configuration, this meta-prompt generates:

---

# {PIPELINE_NAME} - Professional Audio Processing Pipeline

## Pipeline Overview
Create a {COMPLEXITY}-level audio processing pipeline optimized for {PROCESSING_FOCUS} applications with robust feature extraction, quality gates, and high-performance batch processing capabilities.

### Key Features
{#if SPECTRAL_FEATURES}
- **Spectral Analysis**: STFT, spectral centroid, rolloff, bandwidth analysis
{/if}
{#if HARMONIC_FEATURES}
- **Harmonic Analysis**: Chroma features, tonnetz, harmonic-percussive separation
{/if}
{#if RHYTHM_FEATURES}
- **Rhythm Analysis**: Beat tracking, tempo estimation, onset detection
{/if}
{#if QUALITY_GATES}
- **Quality Assurance**: Comprehensive audio validation and error detection
{/if}
{#if BATCH_PROCESSING}
- **Batch Processing**: High-throughput processing with parallel execution
{/if}

## Core Pipeline Architecture

### 1. Audio Loader and Preprocessor
Foundation for audio file handling and preprocessing:

```python
"""
{PIPELINE_NAME} - Audio Processing Pipeline
Professional audio analysis with {PRIMARY_LIBRARY}
"""

import numpy as np
import {PRIMARY_LIBRARY}
{#if SECONDARY_LIBRARY and SECONDARY_LIBRARY != PRIMARY_LIBRARY}
import {SECONDARY_LIBRARY}
{/if}
from typing import Dict, Any, List, Tuple, Optional, Union
from pathlib import Path
import logging
from dataclasses import dataclass, field
from enum import Enum
import warnings
{#if METADATA_EXTRACTION}
import mutagen
from mutagen.id3 import ID3NoHeaderError
{/if}
{#if PARALLEL_PROCESSING}
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
{/if}
{#if PROGRESS_TRACKING}
from tqdm import tqdm
{/fi}
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore', category=UserWarning)

class ProcessingError(Exception):
    """Custom exception for processing errors."""
    pass

class AudioFormat(Enum):
    """Supported audio formats."""
    {#for format in SUPPORTED_FORMATS}
    {format.upper()} = "{format}"
    {/for}

@dataclass
class AudioConfig:
    """Configuration for audio processing."""
    sample_rate: int = {SAMPLE_RATE}
    frame_size: int = {FRAME_SIZE}
    hop_length: int = {HOP_LENGTH}
    max_duration: float = {MAX_DURATION}
    mono_conversion: bool = {MONO_CONVERSION}
    normalization: bool = {NORMALIZATION}
    
    # Quality gate settings
    {#if QUALITY_GATES}
    min_duration: float = 1.0
    max_silence_ratio: float = 0.95
    min_snr_db: float = 10.0
    max_clipping_ratio: float = 0.01
    {/if}
    
    def validate(self) -> bool:
        """Validate configuration parameters."""
        if self.sample_rate <= 0:
            return False
        if self.frame_size <= 0 or self.hop_length <= 0:
            return False
        if self.max_duration <= 0:
            return False
        return True

@dataclass
class AudioData:
    """Container for audio data and metadata."""
    file_path: Path
    audio: np.ndarray
    sample_rate: int
    duration: float
    channels: int
    format: str
    file_size: int
    {#if METADATA_EXTRACTION}
    metadata: Dict[str, Any] = field(default_factory=dict)
    {/if}
    {#if QUALITY_GATES}
    quality_score: float = 1.0
    quality_issues: List[str] = field(default_factory=list)
    {/if}
    processing_time: float = 0.0

@dataclass
class ProcessingResults:
    """Container for processing results."""
    file_path: Path
    success: bool
    {#if SPECTRAL_FEATURES}
    spectral_features: Dict[str, np.ndarray] = field(default_factory=dict)
    {/if}
    {#if TEMPORAL_FEATURES}
    temporal_features: Dict[str, float] = field(default_factory=dict)
    {/if}
    {#if HARMONIC_FEATURES}
    harmonic_features: Dict[str, np.ndarray] = field(default_factory=dict)
    {/if}
    {#if RHYTHM_FEATURES}
    rhythm_features: Dict[str, float] = field(default_factory=dict)
    {/if}
    {#if ENERGY_FEATURES}
    energy_features: Dict[str, float] = field(default_factory=dict)
    {/if}
    {#if TIMBRAL_FEATURES}
    timbral_features: Dict[str, float] = field(default_factory=dict)
    {/if}
    {#if FEATURE_VECTORS}
    feature_vector: np.ndarray = field(default_factory=lambda: np.array([]))
    {/if}
    {#if SPECTROGRAMS}
    spectrograms: Dict[str, np.ndarray] = field(default_factory=dict)
    {/if}
    processing_time: float = 0.0
    error_message: str = ""
    quality_score: float = 1.0

class AudioProcessor:
    """Main audio processing pipeline class."""
    
    def __init__(self, config: AudioConfig = None):
        """Initialize audio processor."""
        self.config = config or AudioConfig()
        if not self.config.validate():
            raise ValueError("Invalid audio configuration")
        
        {#if CACHING}
        self.cache = {}
        self.cache_hits = 0
        self.cache_misses = 0
        {/if}
        
        self.processing_stats = {
            "total_processed": 0,
            "successful": 0,
            "failed": 0,
            "total_time": 0.0
        }
        
        logger.info(f"Audio processor initialized with {PRIMARY_LIBRARY}")
    
    def load_audio(self, file_path: Union[str, Path]) -> AudioData:
        """Load audio file with error handling and preprocessing."""
        file_path = Path(file_path)
        start_time = time.time()
        
        try:
            # Validate file
            if not file_path.exists():
                raise ProcessingError(f"File not found: {file_path}")
            
            if not self._is_supported_format(file_path):
                raise ProcessingError(f"Unsupported format: {file_path.suffix}")
            
            # Load audio using primary library
            {#if PRIMARY_LIBRARY == "librosa"}
            audio, sr = librosa.load(
                str(file_path),
                sr=self.config.sample_rate,
                mono=self.config.mono_conversion,
                duration=self.config.max_duration
            )
            {/if}
            
            {#if PRIMARY_LIBRARY == "pydub"}
            from pydub import AudioSegment
            segment = AudioSegment.from_file(str(file_path))
            
            # Convert to numpy array
            audio = np.array(segment.get_array_of_samples())
            if segment.channels == 2:
                audio = audio.reshape((-1, 2))
                if self.config.mono_conversion:
                    audio = audio.mean(axis=1)
            
            sr = segment.frame_rate
            
            # Resample if needed
            if sr != self.config.sample_rate:
                import librosa
                audio = librosa.resample(audio, orig_sr=sr, target_sr=self.config.sample_rate)
                sr = self.config.sample_rate
            {/if}
            
            {#if PRIMARY_LIBRARY == "essentia"}
            import essentia.standard as es
            loader = es.MonoLoader(filename=str(file_path), sampleRate=self.config.sample_rate)
            audio = loader()
            sr = self.config.sample_rate
            {/if}
            
            # Apply normalization if configured
            {#if NORMALIZATION}
            if self.config.normalization and len(audio) > 0:
                audio = audio / np.max(np.abs(audio))
            {/if}
            
            # Create AudioData object
            audio_data = AudioData(
                file_path=file_path,
                audio=audio,
                sample_rate=sr,
                duration=len(audio) / sr,
                channels=1 if self.config.mono_conversion else (audio.ndim if audio.ndim > 1 else 1),
                format=file_path.suffix.lower(),
                file_size=file_path.stat().st_size,
                processing_time=time.time() - start_time
            )
            
            {#if METADATA_EXTRACTION}
            # Extract metadata
            audio_data.metadata = self._extract_metadata(file_path)
            {/if}
            
            {#if QUALITY_GATES}
            # Apply quality gates
            self._apply_quality_gates(audio_data)
            {/if}
            
            return audio_data
            
        except Exception as e:
            logger.error(f"Failed to load audio {file_path}: {e}")
            raise ProcessingError(f"Audio loading failed: {e}")
    
    def _is_supported_format(self, file_path: Path) -> bool:
        """Check if file format is supported."""
        return file_path.suffix.lower().lstrip('.') in [fmt.value for fmt in AudioFormat]
    
    {#if METADATA_EXTRACTION}
    def _extract_metadata(self, file_path: Path) -> Dict[str, Any]:
        """Extract metadata from audio file."""
        metadata = {}
        
        try:
            audio_file = mutagen.File(str(file_path))
            if audio_file is not None:
                for key, value in audio_file.tags.items() if audio_file.tags else []:
                    if isinstance(value, list) and len(value) == 1:
                        metadata[key] = value[0]
                    else:
                        metadata[key] = value
                
                # Add file info
                if hasattr(audio_file, 'info'):
                    info = audio_file.info
                    metadata.update({
                        'bitrate': getattr(info, 'bitrate', None),
                        'length': getattr(info, 'length', None),
                        'channels': getattr(info, 'channels', None)
                    })
        
        except Exception as e:
            logger.warning(f"Metadata extraction failed for {file_path}: {e}")
        
        return metadata
    {/if}
    
    {#if QUALITY_GATES}
    def _apply_quality_gates(self, audio_data: AudioData):
        """Apply quality gates to audio data."""
        issues = []
        quality_score = 1.0
        
        # Duration check
        if audio_data.duration < self.config.min_duration:
            issues.append(f"Duration too short: {audio_data.duration:.2f}s")
            quality_score *= 0.5
        
        {#if SILENCE_DETECTION}
        # Silence detection
        silence_ratio = self._calculate_silence_ratio(audio_data.audio)
        if silence_ratio > self.config.max_silence_ratio:
            issues.append(f"Too much silence: {silence_ratio:.1%}")
            quality_score *= 0.7
        {/if}
        
        {#if CLIPPING_DETECTION}
        # Clipping detection
        clipping_ratio = self._calculate_clipping_ratio(audio_data.audio)
        if clipping_ratio > self.config.max_clipping_ratio:
            issues.append(f"Audio clipping detected: {clipping_ratio:.1%}")
            quality_score *= 0.8
        {/if}
        
        {#if SNR_ANALYSIS}
        # SNR analysis
        snr_db = self._calculate_snr(audio_data.audio)
        if snr_db < self.config.min_snr_db:
            issues.append(f"Low SNR: {snr_db:.1f} dB")
            quality_score *= 0.6
        {/if}
        
        {#if CORRUPTION_DETECTION}
        # Corruption detection
        if self._detect_corruption(audio_data.audio):
            issues.append("Potential audio corruption detected")
            quality_score *= 0.3
        {/if}
        
        audio_data.quality_score = quality_score
        audio_data.quality_issues = issues
        
        if issues:
            logger.warning(f"Quality issues in {audio_data.file_path.name}: {', '.join(issues)}")
    
    {#if SILENCE_DETECTION}
    def _calculate_silence_ratio(self, audio: np.ndarray, threshold: float = 0.01) -> float:
        """Calculate ratio of silent samples."""
        if len(audio) == 0:
            return 1.0
        silent_samples = np.sum(np.abs(audio) < threshold)
        return silent_samples / len(audio)
    {/if}
    
    {#if CLIPPING_DETECTION}
    def _calculate_clipping_ratio(self, audio: np.ndarray, threshold: float = 0.99) -> float:
        """Calculate ratio of clipped samples."""
        if len(audio) == 0:
            return 0.0
        clipped_samples = np.sum(np.abs(audio) >= threshold)
        return clipped_samples / len(audio)
    {/if}
    
    {#if SNR_ANALYSIS}
    def _calculate_snr(self, audio: np.ndarray) -> float:
        """Calculate signal-to-noise ratio."""
        if len(audio) == 0:
            return 0.0
        
        # Simple SNR estimation
        signal_power = np.mean(audio ** 2)
        noise_power = np.var(audio - np.convolve(audio, np.ones(100)/100, mode='same'))
        
        if noise_power == 0:
            return 100.0  # Perfect signal
        
        snr = 10 * np.log10(signal_power / noise_power)
        return snr
    {/if}
    
    {#if CORRUPTION_DETECTION}
    def _detect_corruption(self, audio: np.ndarray) -> bool:
        """Detect potential audio corruption."""
        if len(audio) == 0:
            return True
        
        # Check for NaN or infinite values
        if np.any(np.isnan(audio)) or np.any(np.isinf(audio)):
            return True
        
        # Check for suspicious patterns
        if np.std(audio) == 0:  # Completely flat audio
            return True
        
        return False
    {/if}
    {/if}
    
    def extract_features(self, audio_data: AudioData) -> ProcessingResults:
        """Extract comprehensive audio features."""
        start_time = time.time()
        
        try:
            results = ProcessingResults(
                file_path=audio_data.file_path,
                success=False,
                quality_score=getattr(audio_data, 'quality_score', 1.0)
            )
            
            audio = audio_data.audio
            sr = audio_data.sample_rate
            
            {#if SPECTRAL_FEATURES}
            # Spectral features
            results.spectral_features = self._extract_spectral_features(audio, sr)
            {/if}
            
            {#if TEMPORAL_FEATURES}
            # Temporal features
            results.temporal_features = self._extract_temporal_features(audio, sr)
            {/if}
            
            {#if HARMONIC_FEATURES}
            # Harmonic features
            results.harmonic_features = self._extract_harmonic_features(audio, sr)
            {/if}
            
            {#if RHYTHM_FEATURES}
            # Rhythm features
            results.rhythm_features = self._extract_rhythm_features(audio, sr)
            {/if}
            
            {#if ENERGY_FEATURES}
            # Energy features
            results.energy_features = self._extract_energy_features(audio, sr)
            {/if}
            
            {#if TIMBRAL_FEATURES}
            # Timbral features
            results.timbral_features = self._extract_timbral_features(audio, sr)
            {/if}
            
            {#if FEATURE_VECTORS}
            # Combine into feature vector
            results.feature_vector = self._create_feature_vector(results)
            {/if}
            
            {#if SPECTROGRAMS}
            # Generate spectrograms
            results.spectrograms = self._generate_spectrograms(audio, sr)
            {/if}
            
            results.success = True
            results.processing_time = time.time() - start_time
            
            return results
            
        except Exception as e:
            logger.error(f"Feature extraction failed for {audio_data.file_path}: {e}")
            return ProcessingResults(
                file_path=audio_data.file_path,
                success=False,
                error_message=str(e),
                processing_time=time.time() - start_time
            )
    
    {#if SPECTRAL_FEATURES}
    def _extract_spectral_features(self, audio: np.ndarray, sr: int) -> Dict[str, np.ndarray]:
        """Extract spectral features from audio."""
        features = {}
        
        {#if PRIMARY_LIBRARY == "librosa"}
        # Spectral centroid
        features['spectral_centroid'] = librosa.feature.spectral_centroid(
            y=audio, sr=sr, hop_length=self.config.hop_length
        )[0]
        
        # Spectral rolloff
        features['spectral_rolloff'] = librosa.feature.spectral_rolloff(
            y=audio, sr=sr, hop_length=self.config.hop_length
        )[0]
        
        # Spectral bandwidth
        features['spectral_bandwidth'] = librosa.feature.spectral_bandwidth(
            y=audio, sr=sr, hop_length=self.config.hop_length
        )[0]
        
        # Zero crossing rate
        features['zcr'] = librosa.feature.zero_crossing_rate(
            audio, frame_length=self.config.frame_size, hop_length=self.config.hop_length
        )[0]
        
        # MFCCs
        features['mfcc'] = librosa.feature.mfcc(
            y=audio, sr=sr, n_mfcc=13, hop_length=self.config.hop_length
        )
        
        # Spectral contrast
        features['spectral_contrast'] = librosa.feature.spectral_contrast(
            y=audio, sr=sr, hop_length=self.config.hop_length
        )
        {/if}
        
        return features
    {/if}
    
    {#if TEMPORAL_FEATURES}
    def _extract_temporal_features(self, audio: np.ndarray, sr: int) -> Dict[str, float]:
        """Extract temporal features from audio."""
        features = {}
        
        # Basic statistics
        features['rms_energy'] = float(np.sqrt(np.mean(audio ** 2)))
        features['max_amplitude'] = float(np.max(np.abs(audio)))
        features['dynamic_range'] = float(np.max(audio) - np.min(audio))
        features['duration'] = float(len(audio) / sr)
        
        {#if PRIMARY_LIBRARY == "librosa"}
        # RMS energy over time
        rms = librosa.feature.rms(y=audio, hop_length=self.config.hop_length)[0]
        features['rms_mean'] = float(np.mean(rms))
        features['rms_std'] = float(np.std(rms))
        {/if}
        
        return features
    {/if}
    
    {#if HARMONIC_FEATURES}
    def _extract_harmonic_features(self, audio: np.ndarray, sr: int) -> Dict[str, np.ndarray]:
        """Extract harmonic features from audio."""
        features = {}
        
        {#if PRIMARY_LIBRARY == "librosa"}
        # Chroma features
        features['chroma'] = librosa.feature.chroma_stft(
            y=audio, sr=sr, hop_length=self.config.hop_length
        )
        
        # Tonnetz (harmonic network)
        features['tonnetz'] = librosa.feature.tonnetz(
            y=librosa.effects.harmonic(audio), sr=sr
        )
        
        # Harmonic-percussive separation
        harmonic, percussive = librosa.effects.hpss(audio)
        features['harmonic_ratio'] = np.array([
            np.sum(harmonic ** 2) / (np.sum(harmonic ** 2) + np.sum(percussive ** 2))
        ])
        {/if}
        
        return features
    {/if}
    
    {#if RHYTHM_FEATURES}
    def _extract_rhythm_features(self, audio: np.ndarray, sr: int) -> Dict[str, float]:
        """Extract rhythm features from audio."""
        features = {}
        
        {#if PRIMARY_LIBRARY == "librosa"}
        # Tempo and beat tracking
        try:
            tempo, beats = librosa.beat.beat_track(y=audio, sr=sr, hop_length=self.config.hop_length)
            features['tempo'] = float(tempo)
            features['beat_count'] = len(beats)
            
            # Beat regularity
            if len(beats) > 1:
                beat_intervals = np.diff(beats) / sr
                features['beat_regularity'] = float(1.0 / (1.0 + np.std(beat_intervals)))
            else:
                features['beat_regularity'] = 0.0
                
        except Exception as e:
            logger.warning(f"Beat tracking failed: {e}")
            features['tempo'] = 120.0  # Default tempo
            features['beat_count'] = 0
            features['beat_regularity'] = 0.0
        
        # Onset detection
        onset_frames = librosa.onset.onset_detect(y=audio, sr=sr, hop_length=self.config.hop_length)
        features['onset_count'] = len(onset_frames)
        features['onset_rate'] = len(onset_frames) / (len(audio) / sr)
        {/if}
        
        return features
    {/if}
    
    {#if ENERGY_FEATURES}
    def _extract_energy_features(self, audio: np.ndarray, sr: int) -> Dict[str, float]:
        """Extract energy-related features."""
        features = {}
        
        # Overall energy
        features['total_energy'] = float(np.sum(audio ** 2))
        features['average_energy'] = float(np.mean(audio ** 2))
        
        {#if PRIMARY_LIBRARY == "librosa"}
        # RMS energy
        rms = librosa.feature.rms(y=audio, hop_length=self.config.hop_length)[0]
        features['rms_energy'] = float(np.mean(rms))
        
        # Energy distribution across frequency bands
        stft = librosa.stft(audio, hop_length=self.config.hop_length)
        magnitude = np.abs(stft)
        
        # Low, mid, high frequency energy
        freqs = librosa.fft_frequencies(sr=sr)
        low_freq_mask = freqs < 250
        mid_freq_mask = (freqs >= 250) & (freqs < 4000)
        high_freq_mask = freqs >= 4000
        
        features['low_freq_energy'] = float(np.mean(magnitude[low_freq_mask]))
        features['mid_freq_energy'] = float(np.mean(magnitude[mid_freq_mask]))
        features['high_freq_energy'] = float(np.mean(magnitude[high_freq_mask]))
        {/if}
        
        return features
    {/if}
    
    {#if TIMBRAL_FEATURES}
    def _extract_timbral_features(self, audio: np.ndarray, sr: int) -> Dict[str, float]:
        """Extract timbral features from audio."""
        features = {}
        
        {#if PRIMARY_LIBRARY == "librosa"}
        # Spectral features statistics
        spectral_centroids = librosa.feature.spectral_centroid(y=audio, sr=sr)[0]
        features['spectral_centroid_mean'] = float(np.mean(spectral_centroids))
        features['spectral_centroid_std'] = float(np.std(spectral_centroids))
        
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio, sr=sr)[0]
        features['spectral_bandwidth_mean'] = float(np.mean(spectral_bandwidth))
        features['spectral_bandwidth_std'] = float(np.std(spectral_bandwidth))
        
        # Spectral flatness (Wiener entropy)
        spectral_flatness = librosa.feature.spectral_flatness(y=audio)[0]
        features['spectral_flatness'] = float(np.mean(spectral_flatness))
        
        # Poly features
        poly_features = librosa.feature.poly_features(y=audio, sr=sr)
        for i, poly_feat in enumerate(poly_features):
            features[f'poly_feature_{i}'] = float(np.mean(poly_feat))
        {/if}
        
        return features
    {/if}
    
    {#if FEATURE_VECTORS}
    def _create_feature_vector(self, results: ProcessingResults) -> np.ndarray:
        """Combine all features into a single vector."""
        features = []
        
        {#if TEMPORAL_FEATURES}
        # Add temporal features
        for value in results.temporal_features.values():
            if isinstance(value, (int, float)):
                features.append(float(value))
        {/if}
        
        {#if ENERGY_FEATURES}
        # Add energy features
        for value in results.energy_features.values():
            if isinstance(value, (int, float)):
                features.append(float(value))
        {/if}
        
        {#if TIMBRAL_FEATURES}
        # Add timbral features
        for value in results.timbral_features.values():
            if isinstance(value, (int, float)):
                features.append(float(value))
        {/if}
        
        {#if RHYTHM_FEATURES}
        # Add rhythm features
        for value in results.rhythm_features.values():
            if isinstance(value, (int, float)):
                features.append(float(value))
        {/if}
        
        {#if SPECTRAL_FEATURES}
        # Add spectral feature statistics
        for feature_name, feature_array in results.spectral_features.items():
            if isinstance(feature_array, np.ndarray) and feature_array.ndim >= 1:
                features.extend([
                    float(np.mean(feature_array)),
                    float(np.std(feature_array)),
                    float(np.max(feature_array)),
                    float(np.min(feature_array))
                ])
        {/if}
        
        return np.array(features) if features else np.array([0.0])
    {/if}
    
    {#if SPECTROGRAMS}
    def _generate_spectrograms(self, audio: np.ndarray, sr: int) -> Dict[str, np.ndarray]:
        """Generate various spectrograms."""
        spectrograms = {}
        
        {#if PRIMARY_LIBRARY == "librosa"}
        # STFT spectrogram
        stft = librosa.stft(audio, hop_length=self.config.hop_length)
        spectrograms['magnitude'] = np.abs(stft)
        spectrograms['phase'] = np.angle(stft)
        
        # Log-magnitude spectrogram
        spectrograms['log_magnitude'] = librosa.amplitude_to_db(spectrograms['magnitude'])
        
        # Mel spectrogram
        mel_spec = librosa.feature.melspectrogram(
            y=audio, sr=sr, hop_length=self.config.hop_length
        )
        spectrograms['mel'] = librosa.amplitude_to_db(mel_spec)
        
        # CQT (Constant-Q Transform)
        try:
            cqt = librosa.cqt(audio, sr=sr, hop_length=self.config.hop_length)
            spectrograms['cqt'] = librosa.amplitude_to_db(np.abs(cqt))
        except Exception as e:
            logger.warning(f"CQT calculation failed: {e}")
        {/if}
        
        return spectrograms
    {/if}
    
    {#if BATCH_PROCESSING}
    def process_batch(
        self, 
        file_paths: List[Union[str, Path]], 
        {#if PARALLEL_PROCESSING}
        max_workers: int = 4,
        use_processes: bool = False,
        {/if}
        {#if PROGRESS_TRACKING}
        show_progress: bool = True
        {/if}
    ) -> List[ProcessingResults]:
        """Process multiple audio files in batch."""
        results = []
        
        {#if PARALLEL_PROCESSING}
        # Parallel processing
        executor_class = ProcessPoolExecutor if use_processes else ThreadPoolExecutor
        
        with executor_class(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_path = {
                executor.submit(self._process_single_file, path): path 
                for path in file_paths
            }
            
            # Collect results
            {#if PROGRESS_TRACKING}
            if show_progress:
                futures = tqdm(as_completed(future_to_path), total=len(file_paths))
            else:
                futures = as_completed(future_to_path)
            {/if}
            {#if not PROGRESS_TRACKING}
            futures = as_completed(future_to_path)
            {/if}
            
            for future in futures:
                try:
                    result = future.result()
                    results.append(result)
                    
                    # Update stats
                    if result.success:
                        self.processing_stats["successful"] += 1
                    else:
                        self.processing_stats["failed"] += 1
                        
                except Exception as e:
                    path = future_to_path[future]
                    logger.error(f"Processing failed for {path}: {e}")
                    results.append(ProcessingResults(
                        file_path=Path(path),
                        success=False,
                        error_message=str(e)
                    ))
                    self.processing_stats["failed"] += 1
        {/if}
        {#if not PARALLEL_PROCESSING}
        # Sequential processing
        {#if PROGRESS_TRACKING}
        file_iter = tqdm(file_paths) if show_progress else file_paths
        {/if}
        {#if not PROGRESS_TRACKING}
        file_iter = file_paths
        {/fi}
        
        for file_path in file_iter:
            try:
                result = self._process_single_file(file_path)
                results.append(result)
                
                if result.success:
                    self.processing_stats["successful"] += 1
                else:
                    self.processing_stats["failed"] += 1
                    
            except Exception as e:
                logger.error(f"Processing failed for {file_path}: {e}")
                results.append(ProcessingResults(
                    file_path=Path(file_path),
                    success=False,
                    error_message=str(e)
                ))
                self.processing_stats["failed"] += 1
        {/if}
        
        self.processing_stats["total_processed"] += len(file_paths)
        return results
    
    def _process_single_file(self, file_path: Union[str, Path]) -> ProcessingResults:
        """Process a single audio file."""
        start_time = time.time()
        
        try:
            {#if CACHING}
            # Check cache
            cache_key = str(Path(file_path).absolute())
            if cache_key in self.cache:
                self.cache_hits += 1
                return self.cache[cache_key]
            self.cache_misses += 1
            {/if}
            
            # Load audio
            audio_data = self.load_audio(file_path)
            
            # Extract features
            results = self.extract_features(audio_data)
            
            {#if CACHING}
            # Cache results
            self.cache[cache_key] = results
            {/if}
            
            return results
            
        except Exception as e:
            return ProcessingResults(
                file_path=Path(file_path),
                success=False,
                error_message=str(e),
                processing_time=time.time() - start_time
            )
    {/if}
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get processing statistics."""
        stats = self.processing_stats.copy()
        
        {#if CACHING}
        stats.update({
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "cache_hit_rate": self.cache_hits / max(self.cache_hits + self.cache_misses, 1)
        })
        {/if}
        
        if stats["total_processed"] > 0:
            stats["success_rate"] = stats["successful"] / stats["total_processed"]
            if stats["total_time"] > 0:
                stats["avg_processing_time"] = stats["total_time"] / stats["total_processed"]
        
        return stats

{#if ANALYSIS_REPORTS}
class AudioAnalysisReport:
    """Generate analysis reports from processing results."""
    
    @staticmethod
    def generate_summary_report(results: List[ProcessingResults]) -> Dict[str, Any]:
        """Generate summary report from batch processing results."""
        if not results:
            return {"error": "No results to analyze"}
        
        successful_results = [r for r in results if r.success]
        failed_results = [r for r in results if not r.success]
        
        report = {
            "summary": {
                "total_files": len(results),
                "successful": len(successful_results),
                "failed": len(failed_results),
                "success_rate": len(successful_results) / len(results) if results else 0,
                "total_processing_time": sum(r.processing_time for r in results)
            },
            "quality_analysis": {},
            "feature_statistics": {}
        }
        
        if successful_results:
            # Quality analysis
            quality_scores = [r.quality_score for r in successful_results]
            report["quality_analysis"] = {
                "average_quality": np.mean(quality_scores),
                "quality_std": np.std(quality_scores),
                "min_quality": np.min(quality_scores),
                "max_quality": np.max(quality_scores)
            }
            
            {#if TEMPORAL_FEATURES}
            # Feature statistics
            if successful_results[0].temporal_features:
                temporal_stats = {}
                for feature_name in successful_results[0].temporal_features.keys():
                    values = [r.temporal_features.get(feature_name, 0) for r in successful_results]
                    temporal_stats[feature_name] = {
                        "mean": float(np.mean(values)),
                        "std": float(np.std(values)),
                        "min": float(np.min(values)),
                        "max": float(np.max(values))
                    }
                report["feature_statistics"]["temporal"] = temporal_stats
            {/if}
        
        if failed_results:
            # Error analysis
            error_types = {}
            for result in failed_results:
                error = result.error_message.split(':')[0] if result.error_message else "Unknown"
                error_types[error] = error_types.get(error, 0) + 1
            
            report["errors"] = error_types
        
        return report
{/if}

# Example usage and testing
def main():
    """Example usage of the audio processing pipeline."""
    
    # Configuration
    config = AudioConfig(
        sample_rate={SAMPLE_RATE},
        frame_size={FRAME_SIZE},
        hop_length={HOP_LENGTH},
        max_duration={MAX_DURATION}
    )
    
    # Initialize processor
    processor = AudioProcessor(config)
    
    # Example: Process single file
    try:
        audio_data = processor.load_audio("example.wav")
        results = processor.extract_features(audio_data)
        
        if results.success:
            print(f"Successfully processed: {results.file_path}")
            {#if FEATURE_VECTORS}
            print(f"Feature vector shape: {results.feature_vector.shape}")
            {/if}
            {#if TEMPORAL_FEATURES}
            print(f"Temporal features: {results.temporal_features}")
            {/if}
        else:
            print(f"Processing failed: {results.error_message}")
    
    except Exception as e:
        print(f"Error: {e}")
    
    {#if BATCH_PROCESSING}
    # Example: Batch processing
    file_paths = ["file1.wav", "file2.mp3", "file3.flac"]
    batch_results = processor.process_batch(file_paths)
    
    # Print statistics
    stats = processor.get_statistics()
    print(f"Processing statistics: {stats}")
    {/if}
    
    {#if ANALYSIS_REPORTS}
    # Generate report
    if 'batch_results' in locals():
        report = AudioAnalysisReport.generate_summary_report(batch_results)
        print(f"Analysis report: {report}")
    {/if}

if __name__ == "__main__":
    main()
```

## Dependencies and Installation

```txt
# Core audio processing
{PRIMARY_LIBRARY}>=0.10.0
numpy>=1.21.0
scipy>=1.7.0

{#if SECONDARY_LIBRARY and SECONDARY_LIBRARY != PRIMARY_LIBRARY}
# Secondary library
{SECONDARY_LIBRARY}>=2.0.0
{/if}

{#if METADATA_EXTRACTION}
# Metadata extraction
mutagen>=1.45.0
{/fi}

{#if PROGRESS_TRACKING}
# Progress tracking
tqdm>=4.64.0
{/fi}

{#if PARALLEL_PROCESSING}
# Parallel processing (built-in)
concurrent.futures
{/fi}

# Utility libraries
pathlib
dataclasses
logging
warnings
```

## Configuration Template

```yaml
# {PIPELINE_NAME} Configuration

audio_processing:
  sample_rate: {SAMPLE_RATE}
  frame_size: {FRAME_SIZE}
  hop_length: {HOP_LENGTH}
  max_duration: {MAX_DURATION}
  mono_conversion: {MONO_CONVERSION}
  normalization: {NORMALIZATION}

supported_formats: {SUPPORTED_FORMATS}

{#if QUALITY_GATES}
quality_gates:
  enabled: true
  min_duration: 1.0
  max_silence_ratio: 0.95
  min_snr_db: 10.0
  max_clipping_ratio: 0.01
{/if}

features:
  {#if SPECTRAL_FEATURES}
  spectral: true
  {/if}
  {#if TEMPORAL_FEATURES}
  temporal: true
  {/if}
  {#if HARMONIC_FEATURES}
  harmonic: true
  {/if}
  {#if RHYTHM_FEATURES}
  rhythm: true
  {/if}
  {#if ENERGY_FEATURES}
  energy: true
  {/if}
  {#if TIMBRAL_FEATURES}
  timbral: true
  {/if}

{#if BATCH_PROCESSING}
processing:
  {#if PARALLEL_PROCESSING}
  max_workers: 4
  use_processes: false
  {/if}
  {#if CACHING}
  enable_caching: true
  {/if}
  {#if PROGRESS_TRACKING}
  show_progress: true
  {/if}
{/if}

output:
  {#if FEATURE_VECTORS}
  feature_vectors: true
  {/if}
  {#if SPECTROGRAMS}
  spectrograms: true
  {/if}
  {#if ANALYSIS_REPORTS}
  generate_reports: true
  {/if}
```

## Usage Examples

### Basic Processing
```python
# Initialize processor
processor = AudioProcessor(AudioConfig())

# Process single file
audio_data = processor.load_audio("audio.wav")
results = processor.extract_features(audio_data)
```

### Batch Processing
```python
# Process multiple files
file_paths = ["file1.wav", "file2.mp3", "file3.flac"]
results = processor.process_batch(file_paths, max_workers=4)
```

### Custom Configuration
```python
# Custom configuration
config = AudioConfig(
    sample_rate=44100,
    max_duration=180,
    normalization=True
)
processor = AudioProcessor(config)
```

## Validation Criteria

A successful implementation should demonstrate:

1. **Robust Audio Loading**: Support for multiple formats with error handling
2. **Comprehensive Features**: Rich feature extraction across multiple domains
3. **Quality Assurance**: Effective quality gates and validation
4. **Performance**: Efficient batch processing with parallelization
5. **Extensibility**: Clear architecture for adding new features
6. **Reliability**: Graceful error handling and logging

---

*Generated by Audio Processing Pipeline Generator Meta-Prompt*
*Version 1.0 - Based on MAP4 Audio Processing Architecture*