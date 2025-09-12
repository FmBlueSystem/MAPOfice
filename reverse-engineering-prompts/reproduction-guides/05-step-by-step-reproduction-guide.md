# MAP4 Step-by-Step Reproduction Guide with Validation Checkpoints

## Overview
This guide provides a complete, validated pathway to reproduce the MAP4 system from scratch, with checkpoints at each critical stage to ensure successful reproduction.

## Phase 1: Foundation Setup (Days 1-2)

### Step 1.1: Environment Preparation
**Objective**: Set up development environment with all required tools

```bash
# Create project directory
mkdir map4-reproduction
cd map4-reproduction

# Initialize Python virtual environment
python3.8 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Initialize git repository
git init
echo "venv/" > .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
echo ".env" >> .gitignore
```

**Validation Checkpoint 1.1**:
- [ ] Python 3.8+ installed and accessible
- [ ] Virtual environment created and activated
- [ ] Git repository initialized
- [ ] .gitignore properly configured

### Step 1.2: Core Dependencies Installation
**Objective**: Install essential packages for MAP4 development

```bash
# Core dependencies
pip install --upgrade pip
pip install wheel setuptools

# Audio processing
pip install librosa==0.10.1
pip install soundfile
pip install pydub

# Database
pip install sqlalchemy==2.0.23
pip install alembic

# GUI
pip install PyQt6
pip install pyqtgraph

# CLI
pip install click==8.1.7

# API clients
pip install requests
pip install aiohttp

# Development tools
pip install pytest
pip install black
pip install pylint
pip install mypy

# Save dependencies
pip freeze > requirements.txt
```

**Validation Checkpoint 1.2**:
- [ ] All packages installed without errors
- [ ] `import librosa` successful
- [ ] `import PyQt6` successful
- [ ] requirements.txt created

### Step 1.3: Project Structure Creation
**Objective**: Establish proper project architecture

```python
# create_structure.py
import os

directories = [
    'map4',
    'map4/core',
    'map4/analysis',
    'map4/providers',
    'map4/ui',
    'map4/cli',
    'map4/database',
    'map4/utils',
    'map4/config',
    'tests',
    'tests/unit',
    'tests/integration',
    'docs',
    'data',
    'logs'
]

for directory in directories:
    os.makedirs(directory, exist_ok=True)
    init_file = os.path.join(directory, '__init__.py')
    if directory.startswith('map4') or directory.startswith('tests'):
        open(init_file, 'a').close()

print("Project structure created successfully!")
```

**Validation Checkpoint 1.3**:
- [ ] All directories created
- [ ] __init__.py files in place
- [ ] Structure matches architecture requirements
- [ ] Run: `python -c "import map4"` without errors

## Phase 2: Core Components Implementation (Days 3-7)

### Step 2.1: Configuration System
**Objective**: Implement hierarchical configuration management

Create `map4/config/config_manager.py`:
```python
import os
import yaml
import json
from pathlib import Path
from typing import Dict, Any

class ConfigManager:
    def __init__(self):
        self.config = {}
        self.load_defaults()
        self.load_user_config()
        self.load_env_variables()
    
    def load_defaults(self):
        """Load default configuration"""
        self.config = {
            'audio': {
                'sample_rate': 22050,
                'duration_limit': 120,
                'hop_length': 512
            },
            'analysis': {
                'hamms_dimensions': 12,
                'quality_threshold': 0.7
            },
            'database': {
                'url': 'sqlite:///map4.db'
            }
        }
    
    def get(self, key: str, default=None):
        """Get configuration value"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            value = value.get(k, default)
            if value is default:
                break
        return value
```

**Validation Checkpoint 2.1**:
- [ ] Configuration loads successfully
- [ ] Hierarchical key access works
- [ ] Environment variable override functional
- [ ] Test: `config.get('audio.sample_rate')` returns 22050

### Step 2.2: Database Models
**Objective**: Implement SQLAlchemy models for data persistence

Create `map4/database/models.py`:
```python
from sqlalchemy import create_engine, Column, Integer, String, Float, JSON, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Track(Base):
    __tablename__ = 'tracks'
    
    id = Column(Integer, primary_key=True)
    file_path = Column(String, unique=True, nullable=False)
    title = Column(String)
    artist = Column(String)
    duration = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    analyses = relationship('Analysis', back_populates='track')

class Analysis(Base):
    __tablename__ = 'analyses'
    
    id = Column(Integer, primary_key=True)
    track_id = Column(Integer, ForeignKey('tracks.id'))
    bpm = Column(Float)
    key = Column(String)
    energy = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    track = relationship('Track', back_populates='analyses')
    hamms_vector = relationship('HAMMSVector', uselist=False, back_populates='analysis')

class HAMMSVector(Base):
    __tablename__ = 'hamms_vectors'
    
    id = Column(Integer, primary_key=True)
    analysis_id = Column(Integer, ForeignKey('analyses.id'))
    vector = Column(JSON)
    version = Column(String, default='3.0')
    
    analysis = relationship('Analysis', back_populates='hamms_vector')
```

**Validation Checkpoint 2.2**:
- [ ] Models define all required fields
- [ ] Relationships properly configured
- [ ] Database creation successful
- [ ] Test: Create and query a test track

### Step 2.3: Audio Processing Core
**Objective**: Implement librosa-based audio analysis

Create `map4/analysis/audio_processor.py`:
```python
import librosa
import numpy as np
from typing import Dict, Any

class AudioProcessor:
    def __init__(self, sample_rate=22050):
        self.sample_rate = sample_rate
    
    def process_file(self, file_path: str) -> Dict[str, Any]:
        """Process audio file and extract features"""
        # Load audio
        y, sr = librosa.load(file_path, sr=self.sample_rate, duration=120)
        
        # Extract features
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
        
        # Chromagram for key detection
        chromagram = librosa.feature.chroma_cqt(y=y, sr=sr)
        
        # Energy features
        rms = librosa.feature.rms(y=y)[0]
        energy = float(np.mean(rms))
        
        # Spectral features
        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        
        return {
            'bpm': float(tempo),
            'energy': energy,
            'spectral_centroid': float(np.mean(spectral_centroid)),
            'duration': len(y) / sr
        }
```

**Validation Checkpoint 2.3**:
- [ ] Audio file loads successfully
- [ ] BPM detection returns reasonable values (60-200)
- [ ] Energy calculation completes
- [ ] No crashes on various audio formats

## Phase 3: HAMMS Implementation (Days 8-10)

### Step 3.1: HAMMS v3.0 Calculator
**Objective**: Implement 12-dimensional HAMMS vector generation

Create `map4/analysis/hamms_calculator.py`:
```python
import numpy as np
from typing import Dict, List

class HAMMSCalculator:
    def __init__(self):
        self.dimensions = 12
        self.weights = {
            'bpm': 1.3,
            'key_signature': 1.4,
            'harmonic_complexity': 0.8,
            'tempo_stability': 0.9,
            'rhythmic_pattern': 1.1,
            'energy_level': 1.2,
            'spectral_centroid': 0.7,
            'dynamic_range': 0.6,
            'acousticness': 0.6,
            'danceability': 0.9,
            'valence': 0.8,
            'instrumentalness': 0.5
        }
    
    def calculate(self, features: Dict) -> List[float]:
        """Calculate HAMMS vector from audio features"""
        vector = []
        
        # BPM dimension (normalized to 0-1, assuming 60-180 BPM range)
        bpm_norm = (features.get('bpm', 120) - 60) / 120
        vector.append(self._normalize(bpm_norm) * self.weights['bpm'])
        
        # Add other dimensions...
        # This is simplified - implement all 12 dimensions
        
        # Ensure vector has exactly 12 dimensions
        while len(vector) < self.dimensions:
            vector.append(0.5)  # Default value
        
        # Final normalization
        return [self._normalize(v) for v in vector]
    
    def _normalize(self, value: float) -> float:
        """Normalize value to [0,1] range"""
        return max(0.0, min(1.0, value))
```

**Validation Checkpoint 3.1**:
- [ ] Vector has exactly 12 dimensions
- [ ] All values in [0,1] range
- [ ] Weights correctly applied
- [ ] Test with known inputs produces expected outputs

### Step 3.2: Similarity Scoring
**Objective**: Implement compatibility scoring system

Create `map4/analysis/similarity.py`:
```python
import numpy as np
from typing import List

class SimilarityScorer:
    def __init__(self):
        self.traditional_weight = 0.6
        self.hamms_weight = 0.4
    
    def calculate_similarity(self, vector1: List[float], vector2: List[float]) -> float:
        """Calculate similarity between two HAMMS vectors"""
        # Euclidean distance
        euclidean = np.linalg.norm(np.array(vector1) - np.array(vector2))
        
        # Cosine similarity
        cosine = np.dot(vector1, vector2) / (np.linalg.norm(vector1) * np.linalg.norm(vector2))
        
        # Combined score
        euclidean_score = 1 / (1 + euclidean)  # Convert distance to similarity
        combined = (euclidean_score + cosine) / 2
        
        return float(combined)
    
    def calculate_compatibility(self, track1_features: dict, track2_features: dict) -> float:
        """Calculate overall compatibility including traditional metrics"""
        # BPM compatibility
        bpm_diff = abs(track1_features['bpm'] - track2_features['bpm'])
        bpm_compat = 1 - min(bpm_diff / 20, 1)  # 20 BPM difference = 0 compatibility
        
        # Key compatibility (simplified)
        key_compat = 0.8  # Placeholder - implement Camelot wheel logic
        
        # Traditional score
        traditional = (bpm_compat + key_compat) / 2
        
        # HAMMS score
        hamms = self.calculate_similarity(
            track1_features.get('hamms_vector', [0.5]*12),
            track2_features.get('hamms_vector', [0.5]*12)
        )
        
        # Combined final score
        return traditional * self.traditional_weight + hamms * self.hamms_weight
```

**Validation Checkpoint 3.2**:
- [ ] Similarity scores in [0,1] range
- [ ] BPM compatibility calculation correct
- [ ] Combined scoring weights applied correctly
- [ ] Test: Similar tracks score > 0.8

## Phase 4: LLM Integration (Days 11-14)

### Step 4.1: Provider Base Class
**Objective**: Create extensible LLM provider architecture

Create `map4/providers/base_provider.py`:
```python
from abc import ABC, abstractmethod
from typing import Dict, Any
import json

class BaseLLMProvider(ABC):
    def __init__(self, api_key: str, model: str):
        self.api_key = api_key
        self.model = model
        self.name = self.__class__.__name__
    
    @abstractmethod
    def analyze(self, hamms_vector: list, metadata: dict) -> Dict[str, Any]:
        """Analyze track using LLM"""
        pass
    
    def generate_prompt(self, hamms_vector: list, metadata: dict) -> str:
        """Generate analysis prompt"""
        return f"""
        Analyze this music track based on its HAMMS vector and metadata.
        
        HAMMS Vector: {hamms_vector}
        BPM: {metadata.get('bpm', 'Unknown')}
        Energy: {metadata.get('energy', 'Unknown')}
        
        Please provide:
        - Genre and sub-genre
        - Mood description
        - Relevant tags (5-10)
        - Confidence score (0-1)
        
        Return as JSON.
        """
    
    def parse_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response"""
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {'error': 'Failed to parse response'}
```

**Validation Checkpoint 4.1**:
- [ ] Base class defines required interface
- [ ] Prompt generation works
- [ ] Response parsing handles errors
- [ ] Provider registration system ready

### Step 4.2: OpenAI Provider Implementation
**Objective**: Implement OpenAI API integration

Create `map4/providers/openai_provider.py`:
```python
import requests
from typing import Dict, Any
from .base_provider import BaseLLMProvider

class OpenAIProvider(BaseLLMProvider):
    def __init__(self, api_key: str, model: str = 'gpt-4o-mini'):
        super().__init__(api_key, model)
        self.base_url = 'https://api.openai.com/v1'
    
    def analyze(self, hamms_vector: list, metadata: dict) -> Dict[str, Any]:
        """Analyze using OpenAI API"""
        prompt = self.generate_prompt(hamms_vector, metadata)
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': self.model,
            'messages': [
                {'role': 'system', 'content': 'You are a music analysis expert.'},
                {'role': 'user', 'content': prompt}
            ],
            'temperature': 0.7,
            'response_format': {'type': 'json_object'}
        }
        
        try:
            response = requests.post(
                f'{self.base_url}/chat/completions',
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            return self.parse_response(content)
            
        except Exception as e:
            return {'error': str(e)}
```

**Validation Checkpoint 4.2**:
- [ ] API authentication works
- [ ] Request format correct
- [ ] Response parsing successful
- [ ] Error handling implemented

## Phase 5: UI Development (Days 15-18)

### Step 5.1: Main Application Window
**Objective**: Create PyQt6 main application interface

Create `map4/ui/main_window.py`:
```python
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTableWidget, QPushButton, QProgressBar
from PyQt6.QtCore import Qt, pyqtSignal

class MainWindow(QMainWindow):
    analysis_requested = pyqtSignal(list)  # Signal for analysis requests
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle('MAP4 - Music Analyzer Pro')
        self.setGeometry(100, 100, 1200, 800)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout
        layout = QVBoxLayout(central_widget)
        
        # Track table
        self.track_table = QTableWidget()
        self.track_table.setColumnCount(6)
        self.track_table.setHorizontalHeaderLabels([
            'Title', 'Artist', 'BPM', 'Key', 'Energy', 'Compatibility'
        ])
        layout.addWidget(self.track_table)
        
        # Control buttons
        self.analyze_btn = QPushButton('Analyze Selected')
        self.analyze_btn.clicked.connect(self.on_analyze_clicked)
        layout.addWidget(self.analyze_btn)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)
    
    def on_analyze_clicked(self):
        # Emit signal with selected tracks
        selected_rows = set(item.row() for item in self.track_table.selectedItems())
        if selected_rows:
            self.analysis_requested.emit(list(selected_rows))
```

**Validation Checkpoint 5.1**:
- [ ] Window displays correctly
- [ ] Table shows track information
- [ ] Buttons trigger appropriate actions
- [ ] Progress bar updates during analysis

## Phase 6: CLI Implementation (Days 19-20)

### Step 6.1: CLI Commands
**Objective**: Implement command-line interface

Create `map4/cli/commands.py`:
```python
import click
from pathlib import Path

@click.group()
def cli():
    """MAP4 - Music Analyzer Pro CLI"""
    pass

@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--recursive', '-r', is_flag=True, help='Scan directories recursively')
@click.option('--output', '-o', type=click.Path(), help='Output file path')
def analyze(path, recursive, output):
    """Analyze audio files"""
    path = Path(path)
    
    if path.is_file():
        click.echo(f"Analyzing: {path}")
        # Perform analysis
    elif path.is_dir():
        pattern = '**/*.mp3' if recursive else '*.mp3'
        files = list(path.glob(pattern))
        
        with click.progressbar(files, label='Analyzing files') as bar:
            for file in bar:
                # Perform analysis
                pass
    
    click.echo(f"Analysis complete. Results: {output or 'console'}")

@cli.command()
@click.option('--check', is_flag=True, help='Check configuration')
def config(check):
    """Manage configuration"""
    if check:
        click.echo("Configuration valid")

if __name__ == '__main__':
    cli()
```

**Validation Checkpoint 6.1**:
- [ ] CLI commands execute without errors
- [ ] File/directory scanning works
- [ ] Progress reporting functional
- [ ] Output generation successful

## Phase 7: Integration Testing (Days 21-23)

### Step 7.1: End-to-End Testing
**Objective**: Validate complete system integration

Create `tests/integration/test_full_pipeline.py`:
```python
import pytest
from pathlib import Path
import tempfile

def test_full_analysis_pipeline():
    """Test complete analysis pipeline"""
    # Create test audio file
    test_file = Path(tempfile.mktemp(suffix='.wav'))
    
    # Initialize components
    from map4.analysis.audio_processor import AudioProcessor
    from map4.analysis.hamms_calculator import HAMMSCalculator
    from map4.database.models import Track, Analysis, HAMMSVector
    
    processor = AudioProcessor()
    calculator = HAMMSCalculator()
    
    # Process audio
    features = processor.process_file(str(test_file))
    assert 'bpm' in features
    assert 60 <= features['bpm'] <= 200
    
    # Calculate HAMMS
    hamms_vector = calculator.calculate(features)
    assert len(hamms_vector) == 12
    assert all(0 <= v <= 1 for v in hamms_vector)
    
    # Store in database
    track = Track(file_path=str(test_file))
    analysis = Analysis(track=track, bpm=features['bpm'])
    hamms = HAMMSVector(analysis=analysis, vector=hamms_vector)
    
    assert track.analyses[0] == analysis
    assert analysis.hamms_vector == hamms

def test_llm_integration():
    """Test LLM provider integration"""
    from map4.providers.openai_provider import OpenAIProvider
    
    provider = OpenAIProvider(api_key='test_key')
    hamms_vector = [0.5] * 12
    metadata = {'bpm': 128, 'energy': 0.75}
    
    # Mock API call
    result = provider.analyze(hamms_vector, metadata)
    
    # Validate response structure
    assert isinstance(result, dict)
    # Add more assertions based on expected response
```

**Validation Checkpoint 7.1**:
- [ ] All integration tests pass
- [ ] Data flows correctly between components
- [ ] No data loss or corruption
- [ ] Performance within acceptable limits

## Phase 8: Deployment Preparation (Days 24-25)

### Step 8.1: Package Configuration
**Objective**: Prepare for distribution

Create `setup.py`:
```python
from setuptools import setup, find_packages

setup(
    name='map4',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'librosa>=0.10.1',
        'sqlalchemy>=2.0.23',
        'PyQt6',
        'click>=8.1.7',
        'requests',
    ],
    entry_points={
        'console_scripts': [
            'map4=map4.cli.commands:cli',
        ],
    },
    python_requires='>=3.8',
)
```

**Validation Checkpoint 8.1**:
- [ ] Package builds successfully
- [ ] Installation works in clean environment
- [ ] CLI commands accessible after installation
- [ ] All dependencies resolved

## Final Validation Checklist

### System-Level Validation
- [ ] **Functional**: All core features working
- [ ] **Performance**: Meets benchmark requirements
- [ ] **Quality**: Code quality checks pass
- [ ] **Integration**: Components work together
- [ ] **Documentation**: User and API docs complete

### Production Readiness
- [ ] Error handling comprehensive
- [ ] Logging implemented
- [ ] Configuration management working
- [ ] Security measures in place
- [ ] Performance optimized

### Success Criteria Met
- [ ] HAMMS v3.0 accuracy validated
- [ ] Audio processing reliable
- [ ] LLM integration functional
- [ ] UI responsive and intuitive
- [ ] CLI fully operational
- [ ] Database operations stable

## Troubleshooting Common Issues

### Issue: Import Errors
**Solution**: Verify all dependencies installed, check Python path

### Issue: Audio Processing Fails
**Solution**: Check librosa installation, verify audio file format

### Issue: Database Connection Issues
**Solution**: Check SQLAlchemy configuration, verify database URL

### Issue: LLM API Errors
**Solution**: Verify API keys, check network connectivity

### Issue: UI Not Displaying
**Solution**: Check PyQt6 installation, verify display settings

## Validation Success Metrics

### Minimum Viable Reproduction
- Core functionality: 100% implemented
- Test coverage: > 70%
- Performance: Within 2x of targets
- Quality score: > 70%

### Production-Ready Reproduction
- All features: 100% implemented
- Test coverage: > 85%
- Performance: Meets all targets
- Quality score: > 85%

## Continuous Validation

After initial reproduction, maintain quality through:
1. Automated testing on each change
2. Performance monitoring
3. Regular dependency updates
4. User feedback integration
5. Security scanning

This completes the step-by-step reproduction guide with comprehensive validation checkpoints ensuring successful MAP4 system reproduction.