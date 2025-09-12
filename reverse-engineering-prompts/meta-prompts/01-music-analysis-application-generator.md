# Music Analysis Application Generator Meta-Prompt

## Overview
This meta-prompt generates comprehensive reproduction prompts for creating sophisticated music analysis applications similar to MAP4. It extracts patterns from the MAP4 architecture to create customizable templates for various music analysis approaches.

## Meta-Prompt Template

### Application Configuration Parameters
Use this template with the following configurable parameters:

```yaml
# Music Analysis Application Configuration
APPLICATION_CONFIG:
  name: "{APPLICATION_NAME}"                    # e.g., "DJ Mixer Pro", "Studio Analyzer"
  focus: "{ANALYSIS_FOCUS}"                     # e.g., "DJ_MIXING", "PRODUCTION", "BROADCAST", "RESEARCH"
  complexity: "{COMPLEXITY_LEVEL}"              # "BASIC", "INTERMEDIATE", "ADVANCED", "PROFESSIONAL"
  vector_dimensions: {VECTOR_DIMENSIONS}        # 6, 12, 24, 48 (complexity-based)
  
ANALYSIS_FEATURES:
  harmonic_analysis: {INCLUDE_HARMONIC}         # true/false
  rhythmic_analysis: {INCLUDE_RHYTHMIC}         # true/false
  timbral_analysis: {INCLUDE_TIMBRAL}           # true/false
  semantic_analysis: {INCLUDE_SEMANTIC}         # true/false (requires AI)
  compatibility_scoring: {INCLUDE_COMPATIBILITY} # true/false
  playlist_generation: {INCLUDE_PLAYLIST}       # true/false

AUDIO_PROCESSING:
  primary_library: "{AUDIO_LIBRARY}"           # "librosa", "essentia", "audioflux", "custom"
  sample_rate: {SAMPLE_RATE}                   # 22050, 44100, 48000
  analysis_window: {WINDOW_SIZE}               # 1024, 2048, 4096
  supported_formats: [{AUDIO_FORMATS}]         # ["mp3", "wav", "flac", "m4a"]
  quality_gates: {INCLUDE_QUALITY_GATES}       # true/false

STORAGE_SYSTEM:
  database_type: "{DB_TYPE}"                   # "sqlite", "postgresql", "mysql"
  enable_migrations: {ENABLE_MIGRATIONS}       # true/false
  enable_caching: {ENABLE_CACHING}             # true/false
  metadata_integration: {METADATA_INTEGRATION} # true/false

UI_FRAMEWORK:
  gui_framework: "{GUI_FRAMEWORK}"             # "PyQt6", "tkinter", "kivy", "web"
  theme_system: {INCLUDE_THEMES}               # true/false
  real_time_updates: {REAL_TIME_UPDATES}       # true/false
  progress_tracking: {PROGRESS_TRACKING}       # true/false
```

## Generated Prompt Template

Based on the configuration above, this meta-prompt generates a complete reproduction prompt:

---

# {APPLICATION_NAME} - {ANALYSIS_FOCUS} Music Analysis Application

## Application Overview
Create a {COMPLEXITY_LEVEL}-level music analysis application focused on {ANALYSIS_FOCUS} with {VECTOR_DIMENSIONS}-dimensional analysis vectors. This application provides comprehensive music analysis capabilities including:

{#if INCLUDE_HARMONIC}
- **Harmonic Analysis**: BPM detection, key signature identification, harmonic complexity analysis
{/if}
{#if INCLUDE_RHYTHMIC}
- **Rhythmic Analysis**: Tempo stability, rhythmic patterns, beat tracking
{/if}
{#if INCLUDE_TIMBRAL}
- **Timbral Analysis**: Spectral features, dynamic range, acoustic properties
{/if}
{#if INCLUDE_SEMANTIC}
- **Semantic Analysis**: AI-powered genre, mood, and tag classification
{/if}
{#if INCLUDE_COMPATIBILITY}
- **Compatibility Scoring**: Track compatibility for {ANALYSIS_FOCUS} applications
{/if}
{#if INCLUDE_PLAYLIST}
- **Playlist Generation**: Intelligent playlist creation based on analysis results
{/if}

## Technical Architecture

### Core Analysis Engine
Implement a {VECTOR_DIMENSIONS}-dimensional analysis system with the following components:

```python
# Analysis Vector Structure
ANALYSIS_DIMENSIONS = {
{#if INCLUDE_HARMONIC}
    # Harmonic Features (Weight: High Priority)
    "bpm": 1.3,
    "key_signature": 1.4,
    "harmonic_complexity": 0.8,
{/if}
{#if INCLUDE_RHYTHMIC}
    # Rhythmic Features (Weight: Medium-High Priority)
    "tempo_stability": 0.9,
    "rhythmic_pattern": 1.1,
{/if}
{#if INCLUDE_TIMBRAL}
    # Timbral Features (Weight: Medium Priority)
    "energy_level": 1.2,
    "spectral_centroid": 0.7,
    "dynamic_range": 0.6,
{/if}
{#if INCLUDE_SEMANTIC}
    # Semantic Features (Weight: Context-Dependent)
    "danceability": 0.9,
    "valence": 0.8,
    "acousticness": 0.6,
    "instrumentalness": 0.5,
{/if}
}
```

### Audio Processing Pipeline
Using {AUDIO_LIBRARY} as the primary audio processing library:

```python
# Audio Processing Configuration
AUDIO_CONFIG = {
    "sample_rate": {SAMPLE_RATE},
    "window_size": {WINDOW_SIZE},
    "supported_formats": {AUDIO_FORMATS},
    "max_duration": 300,  # 5 minutes max per track
    "mono_conversion": True,
}

{#if INCLUDE_QUALITY_GATES}
# Quality Gate Framework
QUALITY_GATES = {
    "min_duration": 10,  # seconds
    "max_duration": 600,  # 10 minutes
    "min_sample_rate": 8000,
    "corruption_check": True,
    "silence_threshold": 0.01,
}
{/if}
```

### Database Schema Design
{#if DB_TYPE == "sqlite"}
SQLite-based storage with the following core tables:
{/if}
{#if DB_TYPE == "postgresql"}
PostgreSQL-based storage with advanced features:
{/if}

```sql
-- Core track information
CREATE TABLE tracks (
    id INTEGER PRIMARY KEY,
    file_path TEXT UNIQUE NOT NULL,
    file_name TEXT NOT NULL,
    file_size INTEGER,
    duration REAL,
    sample_rate INTEGER,
    channels INTEGER,
    format TEXT,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

-- Analysis results with {VECTOR_DIMENSIONS}-dimensional vectors
CREATE TABLE analysis_results (
    id INTEGER PRIMARY KEY,
    track_id INTEGER REFERENCES tracks(id),
    analysis_vector JSON,  -- {VECTOR_DIMENSIONS} dimensions
    {#if INCLUDE_HARMONIC}
    bpm REAL,
    key_signature TEXT,
    harmonic_complexity REAL,
    {/if}
    {#if INCLUDE_RHYTHMIC}
    tempo_stability REAL,
    rhythmic_pattern REAL,
    {/if}
    {#if INCLUDE_TIMBRAL}
    energy_level REAL,
    spectral_centroid REAL,
    dynamic_range REAL,
    {/if}
    confidence_score REAL,
    analysis_version TEXT,
    created_at TIMESTAMP
);

{#if INCLUDE_SEMANTIC}
-- AI-generated semantic metadata
CREATE TABLE semantic_analysis (
    id INTEGER PRIMARY KEY,
    track_id INTEGER REFERENCES tracks(id),
    genre TEXT,
    subgenres JSON,
    mood TEXT,
    moods JSON,
    tags JSON,
    instruments JSON,
    era TEXT,
    confidence REAL,
    provider TEXT,
    model TEXT,
    created_at TIMESTAMP
);
{/if}

{#if INCLUDE_COMPATIBILITY}
-- Compatibility scoring cache
CREATE TABLE compatibility_scores (
    id INTEGER PRIMARY KEY,
    track1_id INTEGER REFERENCES tracks(id),
    track2_id INTEGER REFERENCES tracks(id),
    compatibility_score REAL,
    {#if ANALYSIS_FOCUS == "DJ_MIXING"}
    bpm_compatibility REAL,
    key_compatibility REAL,
    energy_compatibility REAL,
    {/if}
    calculation_method TEXT,
    created_at TIMESTAMP,
    UNIQUE(track1_id, track2_id)
);
{/if}
```

### Analysis Algorithm Implementation

#### Core Analyzer Class
```python
"""
{APPLICATION_NAME} - {VECTOR_DIMENSIONS}D Music Analysis Engine
"""

import numpy as np
import {AUDIO_LIBRARY}
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

class {APPLICATION_NAME.replace(' ', '')}Analyzer:
    """Main analysis engine for {APPLICATION_NAME}."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize analyzer with configuration."""
        self.config = config
        self.sample_rate = config.get('sample_rate', {SAMPLE_RATE})
        self.window_size = config.get('window_size', {WINDOW_SIZE})
        {#if INCLUDE_QUALITY_GATES}
        self.quality_gates = config.get('quality_gates', True)
        {/if}
    
    def analyze_track(self, file_path: str) -> Dict[str, Any]:
        """Perform complete {VECTOR_DIMENSIONS}D analysis on audio track."""
        try:
            # Load audio file
            audio_data = self._load_audio(file_path)
            
            {#if INCLUDE_QUALITY_GATES}
            # Apply quality gates
            if not self._validate_audio_quality(audio_data):
                raise ValueError("Audio quality validation failed")
            {/if}
            
            # Extract features
            features = {}
            
            {#if INCLUDE_HARMONIC}
            # Harmonic analysis
            features.update(self._extract_harmonic_features(audio_data))
            {/if}
            
            {#if INCLUDE_RHYTHMIC}
            # Rhythmic analysis  
            features.update(self._extract_rhythmic_features(audio_data))
            {/if}
            
            {#if INCLUDE_TIMBRAL}
            # Timbral analysis
            features.update(self._extract_timbral_features(audio_data))
            {/if}
            
            # Generate analysis vector
            analysis_vector = self._create_analysis_vector(features)
            
            return {
                'analysis_vector': analysis_vector,
                'features': features,
                'confidence': self._calculate_confidence(features),
                'analysis_version': '1.0'
            }
            
        except Exception as e:
            logger.error(f"Analysis failed for {file_path}: {e}")
            raise
    
    def _load_audio(self, file_path: str) -> np.ndarray:
        """Load and preprocess audio file."""
        {#if AUDIO_LIBRARY == "librosa"}
        y, sr = librosa.load(
            file_path,
            sr=self.sample_rate,
            mono=True,
            duration=300  # Max 5 minutes
        )
        return y
        {/if}
        {#if AUDIO_LIBRARY == "essentia"}
        loader = essentia.standard.MonoLoader(
            filename=file_path,
            sampleRate=self.sample_rate
        )
        return loader()
        {/if}
    
    {#if INCLUDE_QUALITY_GATES}
    def _validate_audio_quality(self, audio_data: np.ndarray) -> bool:
        """Apply quality gates to audio data."""
        # Check minimum duration
        min_duration = self.config.get('min_duration', 10)
        if len(audio_data) / self.sample_rate < min_duration:
            return False
        
        # Check for silence
        if np.max(np.abs(audio_data)) < 0.01:
            return False
        
        # Check for corruption (NaN, inf values)
        if np.any(np.isnan(audio_data)) or np.any(np.isinf(audio_data)):
            return False
        
        return True
    {/if}
    
    {#if INCLUDE_HARMONIC}
    def _extract_harmonic_features(self, audio_data: np.ndarray) -> Dict[str, float]:
        """Extract harmonic features from audio."""
        features = {}
        
        {#if AUDIO_LIBRARY == "librosa"}
        # BPM detection
        tempo, beats = librosa.beat.beat_track(
            y=audio_data, 
            sr=self.sample_rate
        )
        features['bpm'] = float(tempo)
        
        # Key detection using chroma features
        chroma = librosa.feature.chroma_stft(y=audio_data, sr=self.sample_rate)
        key = self._estimate_key(chroma)
        features['key_signature'] = key
        
        # Harmonic complexity (spectral rolloff variance)
        rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=self.sample_rate)
        features['harmonic_complexity'] = float(np.var(rolloff))
        {/if}
        
        return features
    {/if}
    
    {#if INCLUDE_RHYTHMIC}
    def _extract_rhythmic_features(self, audio_data: np.ndarray) -> Dict[str, float]:
        """Extract rhythmic features from audio."""
        features = {}
        
        {#if AUDIO_LIBRARY == "librosa"}
        # Tempo stability
        tempo, beats = librosa.beat.beat_track(y=audio_data, sr=self.sample_rate)
        beat_intervals = np.diff(beats) / self.sample_rate
        features['tempo_stability'] = float(1.0 / (1.0 + np.std(beat_intervals)))
        
        # Rhythmic pattern complexity
        onset_env = librosa.onset.onset_strength(y=audio_data, sr=self.sample_rate)
        features['rhythmic_pattern'] = float(np.std(onset_env))
        {/if}
        
        return features
    {/if}
    
    {#if INCLUDE_TIMBRAL}
    def _extract_timbral_features(self, audio_data: np.ndarray) -> Dict[str, float]:
        """Extract timbral features from audio."""
        features = {}
        
        {#if AUDIO_LIBRARY == "librosa"}
        # Energy level (RMS)
        rms = librosa.feature.rms(y=audio_data)
        features['energy_level'] = float(np.mean(rms))
        
        # Spectral centroid
        centroid = librosa.feature.spectral_centroid(y=audio_data, sr=self.sample_rate)
        features['spectral_centroid'] = float(np.mean(centroid))
        
        # Dynamic range
        features['dynamic_range'] = float(np.max(audio_data) - np.min(audio_data))
        {/if}
        
        return features
    {/if}
    
    def _create_analysis_vector(self, features: Dict[str, float]) -> List[float]:
        """Create normalized {VECTOR_DIMENSIONS}D analysis vector."""
        vector = []
        
        {#if INCLUDE_HARMONIC}
        # Harmonic dimensions
        vector.extend([
            self._normalize_bpm(features.get('bpm', 120)),
            self._normalize_key(features.get('key_signature', 'C')),
            self._normalize_feature(features.get('harmonic_complexity', 0.5), 0, 1),
        ])
        {/if}
        
        {#if INCLUDE_RHYTHMIC}
        # Rhythmic dimensions
        vector.extend([
            self._normalize_feature(features.get('tempo_stability', 0.5), 0, 1),
            self._normalize_feature(features.get('rhythmic_pattern', 0.5), 0, 2),
        ])
        {/if}
        
        {#if INCLUDE_TIMBRAL}
        # Timbral dimensions
        vector.extend([
            self._normalize_feature(features.get('energy_level', 0.1), 0, 1),
            self._normalize_feature(features.get('spectral_centroid', 2000), 0, 8000),
            self._normalize_feature(features.get('dynamic_range', 1.0), 0, 2),
        ])
        {/if}
        
        # Ensure exactly {VECTOR_DIMENSIONS} dimensions
        while len(vector) < {VECTOR_DIMENSIONS}:
            vector.append(0.5)  # Default neutral value
        
        return vector[:{VECTOR_DIMENSIONS}]
    
    def _normalize_bpm(self, bpm: float) -> float:
        """Normalize BPM to [0, 1] range."""
        return np.clip((bpm - 60) / 140, 0, 1)  # 60-200 BPM range
    
    def _normalize_key(self, key: str) -> float:
        """Convert key signature to numeric value."""
        key_mapping = {
            'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5,
            'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11
        }
        return key_mapping.get(key, 0) / 11.0
    
    def _normalize_feature(self, value: float, min_val: float, max_val: float) -> float:
        """Normalize feature to [0, 1] range."""
        return np.clip((value - min_val) / (max_val - min_val), 0, 1)
    
    def _calculate_confidence(self, features: Dict[str, float]) -> float:
        """Calculate overall confidence score for analysis."""
        # Simple confidence based on feature completeness
        expected_features = {VECTOR_DIMENSIONS}
        actual_features = len([v for v in features.values() if v is not None])
        return actual_features / expected_features
```

{#if INCLUDE_COMPATIBILITY}
### Compatibility Scoring System
For {ANALYSIS_FOCUS} applications, implement compatibility scoring:

```python
class CompatibilityScorer:
    """Calculate track compatibility for {ANALYSIS_FOCUS} use cases."""
    
    def __init__(self):
        self.weights = {
            {#if ANALYSIS_FOCUS == "DJ_MIXING"}
            'bpm_compatibility': 0.4,
            'key_compatibility': 0.3,
            'energy_compatibility': 0.2,
            'vector_similarity': 0.1
            {/if}
            {#if ANALYSIS_FOCUS == "PRODUCTION"}
            'vector_similarity': 0.5,
            'key_compatibility': 0.3,
            'energy_compatibility': 0.2
            {/if}
        }
    
    def calculate_compatibility(self, track1: Dict, track2: Dict) -> float:
        """Calculate compatibility score between two tracks."""
        scores = {}
        
        {#if ANALYSIS_FOCUS == "DJ_MIXING"}
        # BPM compatibility
        bpm1, bmp2 = track1.get('bpm', 120), track2.get('bpm', 120)
        scores['bpm_compatibility'] = self._bpm_compatibility(bpm1, bpm2)
        
        # Key compatibility (Camelot wheel)
        key1, key2 = track1.get('key_signature'), track2.get('key_signature')
        scores['key_compatibility'] = self._key_compatibility(key1, key2)
        
        # Energy compatibility
        energy1 = track1.get('energy_level', 0.5)
        energy2 = track2.get('energy_level', 0.5)
        scores['energy_compatibility'] = 1.0 - abs(energy1 - energy2)
        {/if}
        
        # Vector similarity
        vec1 = np.array(track1.get('analysis_vector', [0.5] * {VECTOR_DIMENSIONS}))
        vec2 = np.array(track2.get('analysis_vector', [0.5] * {VECTOR_DIMENSIONS}))
        scores['vector_similarity'] = self._cosine_similarity(vec1, vec2)
        
        # Weighted final score
        final_score = sum(
            scores[key] * self.weights[key] 
            for key in scores if key in self.weights
        )
        
        return np.clip(final_score, 0, 1)
```
{/if}

### User Interface Implementation
{#if GUI_FRAMEWORK == "PyQt6"}
PyQt6-based desktop application with professional styling:

```python
"""
{APPLICATION_NAME} - Main Application Window
"""

import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
    QWidget, QTabWidget, QTableWidget, QTableWidgetItem,
    QProgressBar, QLabel, QPushButton, QFileDialog, QStatusBar
)
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QFont, QPalette, QColor

class {APPLICATION_NAME.replace(' ', '')}MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("{APPLICATION_NAME}")
        self.setGeometry(100, 100, 1200, 800)
        
        {#if INCLUDE_THEMES}
        self.setup_theme()
        {/if}
        self.setup_ui()
        
        # Analysis engine
        self.analyzer = {APPLICATION_NAME.replace(' ', '')}Analyzer({})
        
    {#if INCLUDE_THEMES}
    def setup_theme(self):
        """Apply professional dark theme."""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QTabWidget::pane {
                border: 1px solid #555555;
                background-color: #3c3c3c;
            }
            QTabBar::tab {
                background-color: #4a4a4a;
                color: white;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: #0078d4;
            }
            QTableWidget {
                background-color: #3c3c3c;
                alternate-background-color: #454545;
                gridline-color: #555555;
            }
            QPushButton {
                background-color: #0078d4;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)
    {/if}
    
    def setup_ui(self):
        """Setup main user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Tab widget for different views
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Library tab
        self.setup_library_tab()
        
        {#if INCLUDE_COMPATIBILITY}
        # Compatibility tab
        self.setup_compatibility_tab()
        {/if}
        
        {#if INCLUDE_PLAYLIST}
        # Playlist tab
        self.setup_playlist_tab()
        {/if}
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        {#if PROGRESS_TRACKING}
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)
        {/if}
    
    def setup_library_tab(self):
        """Setup music library tab."""
        library_widget = QWidget()
        layout = QVBoxLayout(library_widget)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        add_button = QPushButton("Add Tracks")
        add_button.clicked.connect(self.add_tracks)
        controls_layout.addWidget(add_button)
        
        analyze_button = QPushButton("Analyze Selected")
        analyze_button.clicked.connect(self.analyze_selected)
        controls_layout.addWidget(analyze_button)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Track table
        self.track_table = QTableWidget()
        self.track_table.setColumnCount(6 + {VECTOR_DIMENSIONS})
        
        headers = [
            "Track", "Artist", "BPM", "Key", "Energy", "Analysis"
        ]
        
        # Add dimension headers
        for i in range({VECTOR_DIMENSIONS}):
            headers.append(f"D{i+1}")
        
        self.track_table.setHorizontalHeaderLabels(headers)
        layout.addWidget(self.track_table)
        
        self.tab_widget.addTab(library_widget, "Music Library")
    
    def add_tracks(self):
        """Add tracks to library."""
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select Audio Files", "",
            "Audio Files (*.mp3 *.wav *.flac *.m4a)"
        )
        
        if files:
            self.load_tracks(files)
    
    def load_tracks(self, file_paths: List[str]):
        """Load tracks into table."""
        for file_path in file_paths:
            row = self.track_table.rowCount()
            self.track_table.insertRow(row)
            
            # Basic info
            filename = Path(file_path).name
            self.track_table.setItem(row, 0, QTableWidgetItem(filename))
            self.track_table.setItem(row, 5, QTableWidgetItem("Pending"))
    
    {#if REAL_TIME_UPDATES}
    def analyze_selected(self):
        """Analyze selected tracks with real-time updates."""
        selected_rows = set()
        for item in self.track_table.selectedItems():
            selected_rows.add(item.row())
        
        if not selected_rows:
            return
        
        # Start analysis thread
        self.analysis_thread = AnalysisThread(
            list(selected_rows), self.track_table, self.analyzer
        )
        self.analysis_thread.progress_updated.connect(self.update_progress)
        self.analysis_thread.analysis_completed.connect(self.analysis_complete)
        self.analysis_thread.start()
        
        {#if PROGRESS_TRACKING}
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(len(selected_rows))
        {/if}

class AnalysisThread(QThread):
    """Background thread for track analysis."""
    
    progress_updated = pyqtSignal(int, dict)
    analysis_completed = pyqtSignal()
    
    def __init__(self, rows, table, analyzer):
        super().__init__()
        self.rows = rows
        self.table = table
        self.analyzer = analyzer
    
    def run(self):
        """Run analysis in background."""
        for i, row in enumerate(self.rows):
            try:
                # Get file path from table
                filename_item = self.table.item(row, 0)
                if not filename_item:
                    continue
                
                # Perform analysis (placeholder)
                results = {
                    'bpm': 128.0,
                    'key_signature': 'C',
                    'energy_level': 0.7,
                    'analysis_vector': [0.5] * {VECTOR_DIMENSIONS}
                }
                
                # Emit progress update
                self.progress_updated.emit(row, results)
                
            except Exception as e:
                print(f"Analysis error: {e}")
        
        self.analysis_completed.emit()
    {/if}
```
{/if}

### Installation and Setup Requirements

#### Dependencies
```txt
# Core audio processing
{AUDIO_LIBRARY}=={AUDIO_LIBRARY == "librosa" and "0.10.1" or "2.7.0"}
numpy>=1.21.0
scipy>=1.7.0

{#if DB_TYPE == "sqlite"}
# Database (SQLite built-in)
sqlalchemy>=2.0.0
{/if}
{#if DB_TYPE == "postgresql"}
# Database (PostgreSQL)
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.0
{/if}

{#if ENABLE_MIGRATIONS}
# Database migrations
alembic>=1.8.0
{/if}

{#if GUI_FRAMEWORK == "PyQt6"}
# GUI Framework
PyQt6>=6.4.0
{/if}

{#if INCLUDE_SEMANTIC}
# AI/LLM Integration
openai>=1.0.0
anthropic>=0.3.0
google-generativeai>=0.3.0
{/if}

# Utility libraries
click>=8.0.0
pyyaml>=6.0
python-dotenv>=0.19.0
mutagen>=1.45.0  # Audio metadata
pathlib>=1.0.1
dataclasses>=0.6
```

#### Project Structure
```
{APPLICATION_NAME.lower().replace(' ', '_')}/
├── src/
│   ├── __init__.py
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── analyzer.py          # Main {VECTOR_DIMENSIONS}D analyzer
│   │   ├── audio_processor.py   # {AUDIO_LIBRARY} integration
│   │   ├── quality_gates.py     # Audio quality validation
│   │   {#if INCLUDE_COMPATIBILITY}
│   │   ├── compatibility.py     # Compatibility scoring
│   │   {/if}
│   │   {#if INCLUDE_SEMANTIC}
│   │   └── providers/           # AI provider integrations
│   │       ├── __init__.py
│   │       ├── base_provider.py
│   │       └── openai_provider.py
│   │   {/if}
│   ├── database/
│   │   ├── __init__.py
│   │   ├── models.py           # SQLAlchemy models
│   │   ├── connection.py       # Database connection
│   │   {#if ENABLE_MIGRATIONS}
│   │   └── migrations/         # Alembic migrations
│   │   {/if}
│   ├── ui/
│   │   ├── __init__.py
│   │   {#if GUI_FRAMEWORK == "PyQt6"}
│   │   ├── main_window.py      # Main PyQt6 window
│   │   ├── widgets/            # Custom widgets
│   │   {#if INCLUDE_THEMES}
│   │   └── themes.py           # UI themes
│   │   {/if}
│   │   {/if}
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── main.py             # Click CLI interface
│   │   └── commands/           # CLI commands
│   └── config/
│       ├── __init__.py
│       └── settings.py         # Configuration management
├── tests/
│   ├── __init__.py
│   ├── test_analyzer.py
│   ├── test_audio_processor.py
│   └── test_database.py
├── config/
│   ├── config.yaml             # Default configuration
│   └── config.example.yaml     # Example configuration
├── requirements.txt
├── setup.py
├── README.md
└── {APPLICATION_NAME.lower().replace(' ', '_')}_cli.py  # Entry point
```

#### Configuration Template
```yaml
# {APPLICATION_NAME} Configuration

# Application settings
application:
  name: "{APPLICATION_NAME}"
  version: "1.0.0"
  log_level: "INFO"

# Audio processing
audio:
  sample_rate: {SAMPLE_RATE}
  window_size: {WINDOW_SIZE}
  max_duration: 300
  supported_formats: {AUDIO_FORMATS}
  
{#if INCLUDE_QUALITY_GATES}
# Quality gates
quality_gates:
  enabled: true
  min_duration: 10
  max_duration: 600
  silence_threshold: 0.01
  corruption_check: true
{/if}

# Analysis configuration
analysis:
  vector_dimensions: {VECTOR_DIMENSIONS}
  {#if INCLUDE_HARMONIC}
  harmonic_analysis: true
  {/if}
  {#if INCLUDE_RHYTHMIC}
  rhythmic_analysis: true
  {/if}
  {#if INCLUDE_TIMBRAL}
  timbral_analysis: true
  {/if}
  {#if INCLUDE_SEMANTIC}
  semantic_analysis: true
  {/if}

# Database configuration
database:
  type: "{DB_TYPE}"
  {#if DB_TYPE == "sqlite"}
  path: "data/{APPLICATION_NAME.lower().replace(' ', '_')}.db"
  {/if}
  {#if DB_TYPE == "postgresql"}
  host: "localhost"
  port: 5432
  name: "{APPLICATION_NAME.lower().replace(' ', '_')}"
  user: "user"
  password: "password"
  {/if}

{#if INCLUDE_SEMANTIC}
# AI providers (optional)
ai_providers:
  openai:
    enabled: false
    api_key: "${OPENAI_API_KEY}"
    model: "gpt-3.5-turbo"
    max_tokens: 500
  
  anthropic:
    enabled: false
    api_key: "${ANTHROPIC_API_KEY}"
    model: "claude-3-haiku-20240307"
    max_tokens: 500
{/if}

{#if GUI_FRAMEWORK == "PyQt6"}
# UI configuration
ui:
  theme: "dark"
  window_size: [1200, 800]
  {#if REAL_TIME_UPDATES}
  real_time_updates: true
  {/if}
  {#if PROGRESS_TRACKING}
  show_progress: true
  {/if}
{/if}
```

## Usage Examples

### Basic Implementation
```bash
# Generate a basic DJ mixing application
python meta_prompt_generator.py \
  --name "DJ Mix Analyzer" \
  --focus "DJ_MIXING" \
  --complexity "INTERMEDIATE" \
  --vector-dimensions 12 \
  --audio-library "librosa" \
  --gui-framework "PyQt6"
```

### Advanced Production Tool
```bash
# Generate an advanced production analysis tool
python meta_prompt_generator.py \
  --name "Studio Pro Analyzer" \
  --focus "PRODUCTION" \
  --complexity "PROFESSIONAL" \
  --vector-dimensions 24 \
  --audio-library "essentia" \
  --include-semantic \
  --gui-framework "PyQt6"
```

### Research Application
```bash
# Generate a research-focused music analysis tool
python meta_prompt_generator.py \
  --name "Music Research Suite" \
  --focus "RESEARCH" \
  --complexity "ADVANCED" \
  --vector-dimensions 48 \
  --audio-library "librosa" \
  --db-type "postgresql" \
  --include-all-features
```

## Validation Criteria

A successful implementation should demonstrate:

1. **Core Analysis Pipeline**: {VECTOR_DIMENSIONS}D analysis with all specified features
2. **Audio Processing**: Robust {AUDIO_LIBRARY} integration with quality gates
3. **Data Persistence**: Properly normalized database schema with relationships
4. **User Interface**: Professional {GUI_FRAMEWORK} interface with real-time updates
5. **Performance**: Capable of analyzing 30+ tracks per minute
6. **Extensibility**: Clear plugin architecture for future enhancements

## Customization Points

This meta-prompt can be adapted for various music analysis applications by adjusting:

- **Analysis Focus**: DJ mixing, music production, broadcast, research
- **Complexity Level**: Basic (6D), Intermediate (12D), Advanced (24D), Professional (48D+)
- **Audio Libraries**: librosa, essentia, audioflux for different analysis approaches
- **UI Frameworks**: PyQt6, tkinter, web-based for different deployment targets
- **Database Systems**: SQLite for simplicity, PostgreSQL for scale
- **AI Integration**: Optional semantic analysis with multiple LLM providers

The generated applications maintain the professional quality and architectural patterns demonstrated in MAP4 while being fully customizable for specific use cases and requirements.

---

*Generated by MAP4 Music Analysis Application Generator Meta-Prompt*
*Version 1.0 - Based on MAP4 Architecture Analysis*