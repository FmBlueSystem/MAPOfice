# MAP4 Core Architecture Overview

## Application Summary
MAP4 (Music Analyzer Pro) is a comprehensive music analysis application that combines audio processing, AI-powered semantic analysis, and advanced harmonic analysis to provide professional music library management and playlist generation capabilities.

## Architecture Pattern
**Layered Architecture with Plugin System**
- **Presentation Layer**: PyQt6 GUI with multiple themes, CLI interface
- **Service Layer**: Analysis services, storage services, provider factory
- **Business Logic Layer**: HAMMS v3.0, compatibility scoring, BMAD methodology
- **Data Layer**: SQLAlchemy ORM with SQLite, metadata extraction
- **Integration Layer**: Multi-LLM providers (OpenAI, Gemini, Anthropic, ZAI)

## Core Technologies
- **Language**: Python 3.8+
- **GUI Framework**: PyQt6 with custom themes and responsive layouts
- **Database**: SQLite with SQLAlchemy ORM
- **Audio Processing**: librosa, mutagen
- **AI Integration**: Multiple LLM providers via unified factory pattern
- **Configuration**: YAML/JSON with environment variable overrides

## Main Entry Points

### 1. Unified CLI (`src/cli/unified_main.py`)
```python
# Main CLI entry point with command groups
@click.group()
def cli(ctx, debug: bool, config: Optional[str]):
    """MAP4 - Music Analyzer Pro - Unified CLI Interface"""

# Command groups:
- analyze_group: Track and library analysis
- playlist_group: Playlist generation and management  
- provider_group: LLM provider management
- bmad_group: BMAD methodology operations
```

### 2. Enhanced GUI (`src/ui/enhanced_main_window.py`)
```python
class EnhancedMainWindow(QMainWindow):
    """Enhanced main window with HAMMS v3.0 and Multi-LLM integration"""
    
    # Features:
    - Legacy mode (original analysis workflow)
    - Enhanced mode (HAMMS v3.0 + Multi-LLM enrichment)
    - Interactive HAMMS radar chart visualization
    - Side-by-side track comparison
    - Enhanced progress tracking and logging
```

### 3. Configuration System (`src/config.py`)
```python
@dataclass
class Config:
    """Configuration container for MAP4"""
    cli: Dict[str, Any]
    providers: Dict[str, Dict[str, Any]]
    analysis: Dict[str, Any]
    storage: Dict[str, Any]
    playlist: Dict[str, Any]
    bmad: Dict[str, Any]
    logging: Dict[str, Any]
    export: Dict[str, Any]
```

## Directory Structure
```
MAP4/
├── src/
│   ├── analysis/          # LLM providers and analysis engines
│   │   ├── providers/     # Unified LLM provider implementations
│   │   ├── hamms_v3.py   # 12-dimensional harmonic analysis
│   │   └── provider_factory.py # Auto-registration factory
│   ├── bmad/             # BMAD methodology implementation
│   ├── cli/              # Command-line interface
│   │   ├── commands/     # CLI command groups
│   │   └── unified_main.py
│   ├── lib/              # Core libraries (audio processing)
│   ├── models/           # Data models and schemas
│   ├── services/         # Business logic services
│   └── ui/               # PyQt6 user interface
│       ├── styles/       # Theme system
│       └── layouts/      # Responsive layout management
├── config/               # Configuration files
├── data/                 # Database and cached data
├── docs/                 # Documentation
└── tests/               # Test suites
```

## Key Design Patterns

### 1. Factory Pattern - LLM Provider System
```python
class ProviderFactory:
    """Enhanced factory with auto-registration for LLM providers"""
    
    @classmethod
    def register_provider(cls, name: str = None):
        """Decorator for auto-registering providers"""
        
    @classmethod
    def create_provider(cls, name: str, config: ProviderConfig):
        """Create or retrieve a provider instance"""
```

### 2. Repository Pattern - Storage System
```python
class Storage:
    """SQLite storage wrapper using SQLAlchemy ORM"""
    
    def get_track_by_path(self, path: str) -> Optional[TrackORM]
    def add_analysis(self, track_path: str, analysis: Dict[str, Any])
    def get_analysis_by_path(self, track_path: str) -> Optional[Dict[str, Any]]
```

### 3. Strategy Pattern - Analysis Pipeline
```python
class EnhancedAnalyzer:
    """Enhanced music analyzer combining HAMMS v3.0 and Multi-LLM enrichment"""
    
    def analyze_track(self, track_path: str) -> EnhancedAnalysisResult:
        # 1. Extract basic audio features
        # 2. Calculate 12-dimensional HAMMS vectors  
        # 3. Optionally enrich with AI-generated metadata
        # 4. Store all results in database
```

## Quality Gates and Validation

### Audio Processing Quality Gates
1. **Input validation**: File existence, format validation, size checks
2. **Supported format validation**: `.wav`, `.mp3`, `.flac`, `.aac`, `.ogg`, `.m4a`
3. **File size and corruption checks**: Minimum viable audio file size
4. **Result validation**: Contract enforcement for BPM, key, energy, HAMMS

### HAMMS Vector Quality Gates
- All vectors must be exactly 12 dimensions
- All values must be normalized to [0, 1] range
- No NaN or infinite values allowed
- Similarity scores must be between 0 and 1

### Database Quality Gates
- Input validation and error handling
- Database transaction management  
- Analysis result validation
- Performance monitoring and logging

## Integration Points

### 1. Audio Processing → HAMMS Analysis
```python
# Audio features feed into HAMMS calculation
basic_result = analyze_track(track_path)  # librosa processing
hamms_vector = hamms_analyzer.calculate_extended_vector(track_data)
```

### 2. HAMMS Analysis → AI Enrichment
```python
# HAMMS data provides context for AI analysis
track_data = {
    'hamms_vector': hamms_result.get('hamms_vector'),
    'bmp': hamms_result.get('bpm'),
    'key': hamms_result.get('key'),
    'energy': hamms_result.get('energy')
}
ai_result = ai_enricher.analyze_track(track_data)
```

### 3. Analysis Results → Storage
```python
# Unified storage of all analysis data
with storage.session() as session:
    # Store HAMMS analysis
    hamms_record = HAMMSAdvanced()
    hamms_record.set_vector_12d(result.hamms_vector)
    
    # Store AI analysis
    ai_record = AIAnalysis.from_llm_response(track_id, ai_data)
```

## Performance Characteristics
- **Audio Analysis**: ~2-5 seconds per track (librosa processing)
- **HAMMS Calculation**: ~0.1 seconds per track (vector math)
- **AI Enrichment**: ~1-3 seconds per track (LLM API call)
- **Database Operations**: ~0.01 seconds per track (SQLite)
- **Overall Throughput**: ~30-60 tracks per minute (with AI enrichment)

## Extensibility Points
1. **New LLM Providers**: Auto-registration decorator system
2. **New Analysis Algorithms**: Plugin architecture in analysis services
3. **New UI Themes**: Theme system with component inheritance
4. **New Export Formats**: Pluggable export system
5. **New BMAD Modes**: Extensible BMAD engine with mode enum

This architecture provides a solid foundation for music analysis with clear separation of concerns, robust error handling, and extensible design patterns that support the complex requirements of professional music library management.