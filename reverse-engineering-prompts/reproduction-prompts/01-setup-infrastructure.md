# MAP4 Infrastructure Setup - Reproduction Prompt

## Objective
Create the foundational infrastructure for MAP4 (Music Analyzer Pro), a professional music analysis application with Python environment setup, directory structure, database initialization, and configuration system.

## Step 1: Python Environment Setup

### 1.1 Create Virtual Environment
```bash
# Create project directory
mkdir MAP4
cd MAP4

# Create Python virtual environment (Python 3.8+ required)
python3 -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate
```

### 1.2 Create Requirements File
Create `requirements.txt` with the following dependencies:

```txt
# Core dependencies
click>=8.1.0
PyQt6>=6.4.0
SQLAlchemy>=2.0.0
alembic>=1.9.0
pyyaml>=6.0
python-dotenv>=1.0.0

# Audio processing
librosa>=0.10.0
mutagen>=1.46.0
numpy>=1.24.0
scipy>=1.10.0
soundfile>=0.12.0

# LLM providers
openai>=1.0.0
anthropic>=0.8.0
google-generativeai>=0.3.0
requests>=2.31.0

# Data processing
pandas>=2.0.0
python-dateutil>=2.8.0

# Development tools
pytest>=7.3.0
pytest-cov>=4.0.0
black>=23.0.0
pylint>=2.17.0
mypy>=1.3.0

# Visualization
matplotlib>=3.7.0
plotly>=5.14.0
```

### 1.3 Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Step 2: Directory Structure Creation

### 2.1 Create Complete Project Structure
```bash
# Create main source directories
mkdir -p src/{analysis,bmad,cli,lib,models,services,ui}
mkdir -p src/analysis/{providers,engines}
mkdir -p src/cli/commands
mkdir -p src/ui/{styles,layouts,visualizers}
mkdir -p src/ui/styles/{themes,components}

# Create configuration and data directories
mkdir -p config/providers
mkdir -p data/{database,cache,exports,logs}

# Create test directories
mkdir -p tests/{unit,integration,fixtures}
mkdir -p tests/unit/{analysis,bmad,cli,lib,models,services,ui}

# Create documentation directories
mkdir -p docs/{api,user-guide,developer}

# Create tools and scripts directories
mkdir -p tools/{bmad,validation,scripts}
```

### 2.2 Create __init__.py Files
```bash
# Create __init__.py files for all Python packages
touch src/__init__.py
touch src/analysis/__init__.py
touch src/analysis/providers/__init__.py
touch src/analysis/engines/__init__.py
touch src/bmad/__init__.py
touch src/cli/__init__.py
touch src/cli/commands/__init__.py
touch src/lib/__init__.py
touch src/models/__init__.py
touch src/services/__init__.py
touch src/ui/__init__.py
touch src/ui/styles/__init__.py
touch src/ui/styles/themes/__init__.py
touch src/ui/styles/components/__init__.py
touch src/ui/layouts/__init__.py
touch src/ui/visualizers/__init__.py
touch tests/__init__.py
```

## Step 3: Configuration System Implementation

### 3.1 Create Configuration Data Class
Create `src/config.py`:

```python
"""MAP4 Configuration System with hierarchical loading and validation."""

import os
import json
import yaml
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class ProviderConfig:
    """Configuration for LLM providers."""
    api_key: str = ""
    model: str = ""
    max_tokens: int = 1000
    temperature: float = 0.7
    timeout: int = 30
    rate_limit: int = 60
    enabled: bool = True
    
@dataclass
class AnalysisConfig:
    """Configuration for analysis settings."""
    sample_rate: int = 22050
    hop_length: int = 512
    n_fft: int = 2048
    max_duration: int = 120  # seconds
    cache_enabled: bool = True
    cache_ttl: int = 86400  # seconds
    quality_gates: bool = True
    
@dataclass
class StorageConfig:
    """Configuration for storage settings."""
    database_url: str = "sqlite:///data/database/map4.db"
    backup_enabled: bool = True
    backup_interval: int = 3600
    transaction_timeout: int = 30
    pool_size: int = 5
    
@dataclass
class PlaylistConfig:
    """Configuration for playlist generation."""
    compatibility_threshold: float = 0.7
    max_tracks: int = 100
    energy_curve: str = "progressive"  # progressive, stable, peak
    harmonic_mixing: bool = True
    bpm_tolerance: float = 0.08
    
@dataclass
class BMADConfig:
    """Configuration for BMAD methodology."""
    certification_threshold: float = 0.8
    optimization_iterations: int = 10
    validation_samples: int = 100
    modes: List[str] = field(default_factory=lambda: [
        "certification", "optimization", "validation", "pure_metadata", "real_data"
    ])
    
@dataclass
class LoggingConfig:
    """Configuration for logging."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_enabled: bool = True
    file_path: str = "data/logs/map4.log"
    rotation: str = "daily"
    retention_days: int = 30
    
@dataclass
class ExportConfig:
    """Configuration for export settings."""
    formats: List[str] = field(default_factory=lambda: ["json", "csv", "m3u", "xlsx"])
    include_metadata: bool = True
    include_hamms: bool = True
    include_ai_analysis: bool = True
    compression: bool = False

@dataclass
class Config:
    """Main configuration container for MAP4."""
    
    # Sub-configurations
    analysis: AnalysisConfig = field(default_factory=AnalysisConfig)
    storage: StorageConfig = field(default_factory=StorageConfig)
    playlist: PlaylistConfig = field(default_factory=PlaylistConfig)
    bmad: BMADConfig = field(default_factory=BMADConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    export: ExportConfig = field(default_factory=ExportConfig)
    
    # Provider configurations
    providers: Dict[str, ProviderConfig] = field(default_factory=dict)
    
    # CLI configurations
    cli: Dict[str, Any] = field(default_factory=lambda: {
        "debug": False,
        "verbose": False,
        "progress": True,
        "color": True,
        "parallel": True,
        "max_workers": 4
    })
    
    @classmethod
    def load(cls, config_path: Optional[str] = None) -> 'Config':
        """Load configuration from file and environment variables.
        
        Loading hierarchy:
        1. Default values
        2. Configuration file (YAML or JSON)
        3. Environment variables (override)
        """
        config = cls()
        
        # Load from file if provided
        if config_path:
            config_file = Path(config_path)
            if config_file.exists():
                with open(config_file) as f:
                    if config_file.suffix in ['.yaml', '.yml']:
                        file_config = yaml.safe_load(f)
                    elif config_file.suffix == '.json':
                        file_config = json.load(f)
                    else:
                        raise ValueError(f"Unsupported config format: {config_file.suffix}")
                
                config._merge_config(file_config)
        
        # Override with environment variables
        config._load_env_overrides()
        
        # Load provider configurations
        config._load_providers()
        
        return config
    
    def _merge_config(self, file_config: Dict[str, Any]):
        """Merge file configuration with defaults."""
        if 'analysis' in file_config:
            self.analysis = AnalysisConfig(**file_config['analysis'])
        if 'storage' in file_config:
            self.storage = StorageConfig(**file_config['storage'])
        if 'playlist' in file_config:
            self.playlist = PlaylistConfig(**file_config['playlist'])
        if 'bmad' in file_config:
            self.bmad = BMADConfig(**file_config['bmad'])
        if 'logging' in file_config:
            self.logging = LoggingConfig(**file_config['logging'])
        if 'export' in file_config:
            self.export = ExportConfig(**file_config['export'])
        if 'cli' in file_config:
            self.cli.update(file_config['cli'])
    
    def _load_env_overrides(self):
        """Load environment variable overrides."""
        # Analysis settings
        if env_val := os.getenv('MAP4_SAMPLE_RATE'):
            self.analysis.sample_rate = int(env_val)
        if env_val := os.getenv('MAP4_MAX_DURATION'):
            self.analysis.max_duration = int(env_val)
        
        # Storage settings
        if env_val := os.getenv('MAP4_DATABASE_URL'):
            self.storage.database_url = env_val
        
        # Logging settings
        if env_val := os.getenv('MAP4_LOG_LEVEL'):
            self.logging.level = env_val
        
        # CLI settings
        if env_val := os.getenv('MAP4_DEBUG'):
            self.cli['debug'] = env_val.lower() == 'true'
    
    def _load_providers(self):
        """Load provider configurations from environment and files."""
        provider_names = ['openai', 'anthropic', 'gemini', 'zai']
        
        for provider in provider_names:
            config = ProviderConfig()
            
            # Load API key from environment
            env_key = f"{provider.upper()}_API_KEY"
            if api_key := os.getenv(env_key):
                config.api_key = api_key
            
            # Load provider-specific config file if exists
            provider_config_file = Path(f"config/providers/{provider}.yaml")
            if provider_config_file.exists():
                with open(provider_config_file) as f:
                    provider_config = yaml.safe_load(f)
                    for key, value in provider_config.items():
                        if hasattr(config, key):
                            setattr(config, key, value)
            
            self.providers[provider] = config
    
    def save(self, config_path: str):
        """Save current configuration to file."""
        config_dict = asdict(self)
        
        config_file = Path(config_path)
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_file, 'w') as f:
            if config_file.suffix in ['.yaml', '.yml']:
                yaml.dump(config_dict, f, default_flow_style=False)
            elif config_file.suffix == '.json':
                json.dump(config_dict, f, indent=2)
            else:
                raise ValueError(f"Unsupported config format: {config_file.suffix}")
    
    def validate(self) -> List[str]:
        """Validate configuration and return list of issues."""
        issues = []
        
        # Validate analysis settings
        if self.analysis.sample_rate < 8000:
            issues.append("Sample rate too low (minimum 8000 Hz)")
        if self.analysis.max_duration < 10:
            issues.append("Max duration too short (minimum 10 seconds)")
        
        # Validate storage settings
        if not self.storage.database_url:
            issues.append("Database URL not configured")
        
        # Validate playlist settings
        if not 0 <= self.playlist.compatibility_threshold <= 1:
            issues.append("Compatibility threshold must be between 0 and 1")
        if self.playlist.bpm_tolerance < 0:
            issues.append("BPM tolerance must be positive")
        
        # Validate BMAD settings
        if not 0 <= self.bmad.certification_threshold <= 1:
            issues.append("Certification threshold must be between 0 and 1")
        
        # Validate provider settings
        for name, provider in self.providers.items():
            if provider.enabled and not provider.api_key:
                issues.append(f"Provider {name} enabled but no API key configured")
        
        return issues

# Global configuration instance
_config: Optional[Config] = None

def get_config(config_path: Optional[str] = None) -> Config:
    """Get or create global configuration instance."""
    global _config
    if _config is None:
        _config = Config.load(config_path or "config/map4.yaml")
    return _config

def reset_config():
    """Reset global configuration (mainly for testing)."""
    global _config
    _config = None
```

## Step 4: Database Schema and Initialization

### 4.1 Create Database Models
Create `src/models/database.py`:

```python
"""Database models for MAP4 using SQLAlchemy ORM."""

from datetime import datetime
from typing import Optional, Dict, Any, List
import json
import numpy as np
from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime, Text, ForeignKey, JSON, Boolean, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.pool import StaticPool

Base = declarative_base()

class TrackORM(Base):
    """Core track table with file system integration."""
    __tablename__ = 'tracks'
    
    id = Column(Integer, primary_key=True)
    file_path = Column(String(500), unique=True, nullable=False, index=True)
    file_hash = Column(String(64), index=True)  # SHA-256 hash for duplicate detection
    
    # Basic metadata
    title = Column(String(200))
    artist = Column(String(200))
    album = Column(String(200))
    year = Column(Integer)
    genre = Column(String(100))
    
    # File information
    duration = Column(Float)  # seconds
    file_size = Column(Integer)  # bytes
    file_format = Column(String(10))  # mp3, wav, flac, etc.
    sample_rate = Column(Integer)
    bit_rate = Column(Integer)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    analyzed_at = Column(DateTime)
    
    # Relationships
    analysis_results = relationship("AnalysisResultORM", back_populates="track", cascade="all, delete-orphan")
    hamms_vectors = relationship("HAMMSVectorORM", back_populates="track", cascade="all, delete-orphan")
    ai_analyses = relationship("AIAnalysis", back_populates="track", cascade="all, delete-orphan")
    hamms_advanced = relationship("HAMMSAdvanced", back_populates="track", cascade="all, delete-orphan")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_track_artist_title', 'artist', 'title'),
        Index('idx_track_genre', 'genre'),
        Index('idx_track_analyzed', 'analyzed_at'),
    )

class AnalysisResultORM(Base):
    """Core analysis results with HAMMS vector references."""
    __tablename__ = 'analysis_results'
    
    id = Column(Integer, primary_key=True)
    track_id = Column(Integer, ForeignKey('tracks.id'), nullable=False, index=True)
    
    # Basic audio features
    bpm = Column(Float)
    key = Column(String(10))  # Musical key (e.g., "C", "Am")
    camelot_key = Column(String(5))  # Camelot notation (e.g., "8A", "1B")
    energy = Column(Float)  # 0-1 normalized
    
    # Advanced features
    danceability = Column(Float)  # 0-1
    valence = Column(Float)  # 0-1 (mood positivity)
    acousticness = Column(Float)  # 0-1
    instrumentalness = Column(Float)  # 0-1
    
    # Quality metrics
    confidence_score = Column(Float)  # 0-1 overall confidence
    analysis_version = Column(String(20))  # e.g., "3.0.0"
    provider = Column(String(50))  # Which analysis engine was used
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    track = relationship("TrackORM", back_populates="analysis_results")

class HAMMSVectorORM(Base):
    """12-dimensional HAMMS vector storage."""
    __tablename__ = 'hamms_vectors'
    
    id = Column(Integer, primary_key=True)
    track_id = Column(Integer, ForeignKey('tracks.id'), nullable=False, index=True)
    
    # 12-dimensional vector stored as JSON array
    vector_data = Column(JSON, nullable=False)
    
    # Individual dimensions for querying
    dim_bpm = Column(Float, index=True)  # Dimension 0
    dim_key = Column(Float, index=True)  # Dimension 1
    dim_energy = Column(Float, index=True)  # Dimension 2
    dim_danceability = Column(Float)  # Dimension 3
    dim_valence = Column(Float)  # Dimension 4
    dim_acousticness = Column(Float)  # Dimension 5
    dim_instrumentalness = Column(Float)  # Dimension 6
    dim_rhythmic_pattern = Column(Float)  # Dimension 7
    dim_spectral_centroid = Column(Float)  # Dimension 8
    dim_tempo_stability = Column(Float)  # Dimension 9
    dim_harmonic_complexity = Column(Float)  # Dimension 10
    dim_dynamic_range = Column(Float)  # Dimension 11
    
    # Vector metadata
    version = Column(String(10), default="3.0")
    confidence = Column(Float)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    track = relationship("TrackORM", back_populates="hamms_vectors")
    
    def set_vector(self, vector: np.ndarray):
        """Set the HAMMS vector and individual dimensions."""
        if len(vector) != 12:
            raise ValueError(f"HAMMS vector must be 12-dimensional, got {len(vector)}")
        
        self.vector_data = vector.tolist()
        self.dim_bpm = float(vector[0])
        self.dim_key = float(vector[1])
        self.dim_energy = float(vector[2])
        self.dim_danceability = float(vector[3])
        self.dim_valence = float(vector[4])
        self.dim_acousticness = float(vector[5])
        self.dim_instrumentalness = float(vector[6])
        self.dim_rhythmic_pattern = float(vector[7])
        self.dim_spectral_centroid = float(vector[8])
        self.dim_tempo_stability = float(vector[9])
        self.dim_harmonic_complexity = float(vector[10])
        self.dim_dynamic_range = float(vector[11])
    
    def get_vector(self) -> np.ndarray:
        """Get the HAMMS vector as numpy array."""
        return np.array(self.vector_data, dtype=np.float64)

class AIAnalysis(Base):
    """AI-generated semantic metadata with confidence scoring."""
    __tablename__ = 'ai_analysis'
    
    id = Column(Integer, primary_key=True)
    track_id = Column(Integer, ForeignKey('tracks.id'), nullable=False, index=True)
    
    # Provider information
    provider = Column(String(50), nullable=False)  # openai, anthropic, gemini, zai
    model = Column(String(100))  # Specific model used
    
    # Generated metadata
    genre_primary = Column(String(100))
    genre_secondary = Column(String(100))
    subgenres = Column(JSON)  # List of subgenres
    
    mood_primary = Column(String(100))
    mood_secondary = Column(String(100))
    moods = Column(JSON)  # List of all moods
    
    tags = Column(JSON)  # List of descriptive tags
    instruments = Column(JSON)  # Detected instruments
    
    # Scene and context
    scene = Column(String(200))  # e.g., "Late night club"
    cultural_context = Column(Text)
    lyrical_themes = Column(JSON)  # If vocals present
    
    # Production analysis
    production_era = Column(String(50))  # e.g., "1990s", "Modern"
    production_style = Column(String(100))
    mixing_notes = Column(Text)
    
    # Confidence scores
    overall_confidence = Column(Float)  # 0-1
    genre_confidence = Column(Float)
    mood_confidence = Column(Float)
    
    # Raw response for debugging
    raw_response = Column(JSON)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    track = relationship("TrackORM", back_populates="ai_analyses")
    
    @classmethod
    def from_llm_response(cls, track_id: int, response: Dict[str, Any], provider: str, model: str) -> 'AIAnalysis':
        """Create AIAnalysis from LLM response."""
        analysis = cls(
            track_id=track_id,
            provider=provider,
            model=model,
            raw_response=response
        )
        
        # Parse response based on provider format
        if 'genre' in response:
            analysis.genre_primary = response.get('genre')
        if 'subgenres' in response:
            analysis.subgenres = response.get('subgenres', [])
        if 'mood' in response:
            analysis.mood_primary = response.get('mood')
        if 'tags' in response:
            analysis.tags = response.get('tags', [])
        if 'confidence' in response:
            analysis.overall_confidence = response.get('confidence', 0.5)
        
        return analysis

class HAMMSAdvanced(Base):
    """Enhanced HAMMS v3.0 analysis with dimension breakdowns."""
    __tablename__ = 'hamms_advanced'
    
    id = Column(Integer, primary_key=True)
    track_id = Column(Integer, ForeignKey('tracks.id'), nullable=False, index=True)
    
    # 12-dimensional vector
    vector_12d = Column(JSON, nullable=False)
    
    # Dimension scores with weights
    dimension_scores = Column(JSON)  # Dict with dimension names and values
    dimension_weights = Column(JSON)  # Applied weights for each dimension
    
    # Compatibility scores
    dj_compatibility_score = Column(Float)  # Traditional DJ metrics
    hamms_compatibility_score = Column(Float)  # HAMMS-based score
    overall_compatibility = Column(Float)  # Combined score
    
    # Analysis metadata
    analysis_timestamp = Column(DateTime, default=datetime.utcnow)
    calculation_time_ms = Column(Integer)  # Processing time
    quality_gates_passed = Column(Boolean, default=True)
    validation_errors = Column(JSON)  # Any validation issues
    
    # Relationships
    track = relationship("TrackORM", back_populates="hamms_advanced")
    
    def set_vector_12d(self, vector: np.ndarray):
        """Set the 12-dimensional HAMMS vector."""
        if len(vector) != 12:
            raise ValueError(f"Vector must be 12-dimensional, got {len(vector)}")
        self.vector_12d = vector.tolist()
    
    def get_vector_12d(self) -> np.ndarray:
        """Get the 12-dimensional HAMMS vector."""
        return np.array(self.vector_12d, dtype=np.float64)
    
    def set_dimension_scores(self, scores: Dict[str, float]):
        """Set individual dimension scores."""
        self.dimension_scores = scores

class DatabaseManager:
    """Database connection and session management."""
    
    def __init__(self, database_url: str = "sqlite:///data/database/map4.db"):
        """Initialize database manager."""
        self.database_url = database_url
        
        # Create engine with appropriate settings for SQLite
        if database_url.startswith("sqlite"):
            self.engine = create_engine(
                database_url,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool,
                echo=False
            )
        else:
            self.engine = create_engine(database_url, echo=False)
        
        # Create session factory
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Create tables
        self.init_database()
    
    def init_database(self):
        """Initialize database schema."""
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self):
        """Get a new database session."""
        return self.SessionLocal()
    
    def drop_all(self):
        """Drop all tables (use with caution)."""
        Base.metadata.drop_all(bind=self.engine)
    
    def backup_database(self, backup_path: str):
        """Create a backup of the SQLite database."""
        import shutil
        if self.database_url.startswith("sqlite:///"):
            db_path = self.database_url.replace("sqlite:///", "")
            shutil.copy2(db_path, backup_path)

# Export models and manager
__all__ = [
    'Base',
    'TrackORM',
    'AnalysisResultORM', 
    'HAMMSVectorORM',
    'AIAnalysis',
    'HAMMSAdvanced',
    'DatabaseManager'
]
```

## Step 5: Create Main Entry Point

### 5.1 Create Main Application Entry
Create `main.py`:

```python
#!/usr/bin/env python3
"""MAP4 - Music Analyzer Pro - Main Entry Point"""

import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.config import get_config
from src.cli.unified_main import cli as cli_main
from src.ui.enhanced_main_window import main as gui_main

def setup_logging(config):
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, config.logging.level),
        format=config.logging.format,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(config.logging.file_path) if config.logging.file_enabled else None
        ]
    )

def main():
    """Main entry point for MAP4."""
    # Load configuration
    config = get_config()
    
    # Setup logging
    setup_logging(config)
    
    # Check command line arguments
    if len(sys.argv) > 1:
        # CLI mode
        cli_main()
    else:
        # GUI mode
        gui_main()

if __name__ == "__main__":
    main()
```

## Step 6: Create Default Configuration Files

### 6.1 Create Default Configuration
Create `config/map4.yaml`:

```yaml
# MAP4 Default Configuration

analysis:
  sample_rate: 22050
  hop_length: 512
  n_fft: 2048
  max_duration: 120
  cache_enabled: true
  cache_ttl: 86400
  quality_gates: true

storage:
  database_url: sqlite:///data/database/map4.db
  backup_enabled: true
  backup_interval: 3600
  transaction_timeout: 30
  pool_size: 5

playlist:
  compatibility_threshold: 0.7
  max_tracks: 100
  energy_curve: progressive
  harmonic_mixing: true
  bpm_tolerance: 0.08

bmad:
  certification_threshold: 0.8
  optimization_iterations: 10
  validation_samples: 100
  modes:
    - certification
    - optimization
    - validation
    - pure_metadata
    - real_data

logging:
  level: INFO
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  file_enabled: true
  file_path: data/logs/map4.log
  rotation: daily
  retention_days: 30

export:
  formats:
    - json
    - csv
    - m3u
    - xlsx
  include_metadata: true
  include_hamms: true
  include_ai_analysis: true
  compression: false

cli:
  debug: false
  verbose: false
  progress: true
  color: true
  parallel: true
  max_workers: 4
```

### 6.2 Create Environment Template
Create `.env.template`:

```bash
# MAP4 Environment Variables Template
# Copy to .env and fill in your values

# LLM Provider API Keys
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
ZAI_API_KEY=your_zai_api_key_here

# Database Configuration (optional, defaults to SQLite)
# MAP4_DATABASE_URL=postgresql://user:password@localhost/map4

# Analysis Settings (optional overrides)
# MAP4_SAMPLE_RATE=22050
# MAP4_MAX_DURATION=120

# Logging (optional overrides)
# MAP4_LOG_LEVEL=INFO

# Debug Mode
# MAP4_DEBUG=false
```

## Step 7: Initialize Git Repository

### 7.1 Create .gitignore
Create `.gitignore`:

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
ENV/
.venv

# IDE
.vscode/
.idea/
*.swp
*.swo
*~
.DS_Store

# Project specific
.env
data/database/*.db
data/cache/*
data/logs/*.log
data/exports/*
!data/cache/.gitkeep
!data/logs/.gitkeep
!data/exports/.gitkeep

# Testing
.coverage
htmlcov/
.pytest_cache/
.tox/

# Distribution
dist/
build/
*.egg-info/
```

### 7.2 Initialize Repository
```bash
git init
git add .
git commit -m "Initial MAP4 infrastructure setup"
```

## Step 8: Verify Installation

### 8.1 Create Verification Script
Create `tools/scripts/verify_setup.py`:

```python
#!/usr/bin/env python3
"""Verify MAP4 infrastructure setup."""

import sys
import importlib
from pathlib import Path

def verify_setup():
    """Verify all components are properly installed."""
    
    print("MAP4 Infrastructure Verification")
    print("=" * 50)
    
    # Check Python version
    print(f"Python Version: {sys.version}")
    if sys.version_info < (3, 8):
        print("ERROR: Python 3.8+ required")
        return False
    
    # Check required packages
    required_packages = [
        'click', 'PyQt6', 'sqlalchemy', 'librosa',
        'numpy', 'yaml', 'dotenv'
    ]
    
    print("\nChecking packages:")
    for package in required_packages:
        try:
            if package == 'PyQt6':
                importlib.import_module('PyQt6.QtCore')
            elif package == 'yaml':
                importlib.import_module('yaml')
            elif package == 'dotenv':
                importlib.import_module('dotenv')
            else:
                importlib.import_module(package)
            print(f"  ✓ {package}")
        except ImportError:
            print(f"  ✗ {package} - NOT INSTALLED")
            return False
    
    # Check directory structure
    print("\nChecking directory structure:")
    required_dirs = [
        'src', 'src/analysis', 'src/bmad', 'src/cli',
        'src/lib', 'src/models', 'src/services', 'src/ui',
        'config', 'data', 'tests', 'tools'
    ]
    
    for dir_path in required_dirs:
        path = Path(dir_path)
        if path.exists():
            print(f"  ✓ {dir_path}")
        else:
            print(f"  ✗ {dir_path} - NOT FOUND")
            return False
    
    # Check configuration
    print("\nChecking configuration:")
    config_file = Path("config/map4.yaml")
    if config_file.exists():
        print(f"  ✓ Configuration file exists")
    else:
        print(f"  ✗ Configuration file not found")
        return False
    
    # Test database initialization
    print("\nTesting database initialization:")
    try:
        from src.models.database import DatabaseManager
        db = DatabaseManager()
        print("  ✓ Database initialized successfully")
    except Exception as e:
        print(f"  ✗ Database initialization failed: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("✓ All checks passed! MAP4 infrastructure is ready.")
    return True

if __name__ == "__main__":
    success = verify_setup()
    sys.exit(0 if success else 1)
```

### 8.2 Run Verification
```bash
python tools/scripts/verify_setup.py
```

## Success Criteria

The infrastructure setup is complete when:

1. **Environment**: Python 3.8+ virtual environment with all dependencies installed
2. **Structure**: Complete directory structure created with proper Python packages
3. **Configuration**: Hierarchical configuration system with environment variable support
4. **Database**: SQLAlchemy models defined with proper relationships and indexes
5. **Entry Points**: Main entry point supporting both CLI and GUI modes
6. **Verification**: All verification checks pass successfully

## Next Steps

After completing the infrastructure setup:

1. Implement the HAMMS v3.0 analysis engine (see `02-core-implementation.md`)
2. Create the multi-LLM provider system (see `03-llm-integration.md`)
3. Build the PyQt6 user interface (see `04-ui-development.md`)
4. Implement the BMAD methodology (see `05-bmad-framework.md`)
5. Create the unified CLI system (see `06-cli-system.md`)
6. Add integration and testing (see `07-integration-testing.md`)

This infrastructure provides the solid foundation needed for the MAP4 music analysis system, with professional-grade configuration management, database design, and extensible architecture.