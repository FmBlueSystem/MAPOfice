# MAP4 Integration and Testing - Complete System Validation

## Objective
Implement comprehensive testing framework, system integration, performance optimization, and deployment preparation for the complete MAP4 music analysis system.

## Prerequisites
- All components implemented (infrastructure through CLI)
- pytest and testing libraries installed
- Sample audio files for testing

## Step 1: Unit Testing Framework

### 1.1 Create Test Configuration
Create `tests/conftest.py`:

```python
"""Pytest configuration and fixtures."""

import pytest
import tempfile
import shutil
from pathlib import Path
import numpy as np

from src.config import Config, AnalysisConfig
from src.models.database import DatabaseManager
from src.analysis.hamms_v3 import HAMMSAnalyzer

@pytest.fixture
def test_config():
    """Create test configuration."""
    config = Config()
    config.storage.database_url = "sqlite:///:memory:"
    config.analysis.cache_enabled = False
    return config

@pytest.fixture
def test_db():
    """Create test database."""
    db = DatabaseManager("sqlite:///:memory:")
    yield db
    # Cleanup handled by in-memory database

@pytest.fixture
def test_track_data():
    """Sample track data for testing."""
    return {
        'title': 'Test Track',
        'artist': 'Test Artist',
        'bpm': 128.0,
        'key': 'Am',
        'energy': 0.7,
        'genre': 'house',
        'duration': 240.0
    }

@pytest.fixture
def test_hamms_vector():
    """Sample HAMMS vector for testing."""
    return np.array([0.5] * 12, dtype=np.float64)

@pytest.fixture
def temp_audio_file():
    """Create temporary audio file."""
    # Would create actual audio file in production
    temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
    temp_file.close()
    
    yield temp_file.name
    
    # Cleanup
    Path(temp_file.name).unlink(missing_ok=True)
```

## Step 2: Unit Tests

### 2.1 Test HAMMS v3.0
Create `tests/unit/test_hamms_v3.py`:

```python
"""Unit tests for HAMMS v3.0 engine."""

import pytest
import numpy as np

from src.analysis.hamms_v3 import HAMMSAnalyzer, HAMMSDimensions

class TestHAMMSAnalyzer:
    """Test HAMMS analyzer functionality."""
    
    def test_initialization(self):
        """Test HAMMS analyzer initialization."""
        analyzer = HAMMSAnalyzer()
        assert analyzer is not None
        assert len(analyzer.CAMELOT_WHEEL) > 0
    
    def test_calculate_extended_vector(self, test_track_data):
        """Test 12-dimensional vector calculation."""
        analyzer = HAMMSAnalyzer()
        result = analyzer.calculate_extended_vector(test_track_data)
        
        assert 'hamms_vector' in result
        assert 'dimension_scores' in result
        assert 'confidence' in result
        assert 'camelot_key' in result
        
        vector = result['hamms_vector']
        assert len(vector) == 12
        assert all(0 <= v <= 1 for v in vector)
    
    def test_similarity_calculation(self, test_hamms_vector):
        """Test similarity calculation between vectors."""
        analyzer = HAMMSAnalyzer()
        
        # Test identical vectors
        similarity = analyzer.calculate_similarity(
            test_hamms_vector,
            test_hamms_vector
        )
        
        assert similarity['overall_similarity'] == pytest.approx(1.0, rel=1e-3)
        assert similarity['compatibility_rating'] == 'Excellent'
        
        # Test different vectors
        other_vector = np.array([0.8] * 12)
        similarity = analyzer.calculate_similarity(
            test_hamms_vector,
            other_vector
        )
        
        assert 0 <= similarity['overall_similarity'] <= 1
    
    def test_quality_gates(self):
        """Test quality gate validation."""
        analyzer = HAMMSAnalyzer()
        
        # Test invalid vector dimensions
        with pytest.raises(ValueError, match="12 dimensions"):
            analyzer._validate_vector(np.array([0.5] * 10))
        
        # Test out of range values
        with pytest.raises(ValueError, match="range"):
            analyzer._validate_vector(np.array([1.5] * 12))
        
        # Test NaN values
        with pytest.raises(ValueError, match="NaN"):
            invalid_vector = np.array([0.5] * 12)
            invalid_vector[0] = np.nan
            analyzer._validate_vector(invalid_vector)
    
    def test_camelot_conversion(self):
        """Test Camelot wheel conversion."""
        analyzer = HAMMSAnalyzer()
        
        # Test major key
        value = analyzer._camelot_to_numeric('C')
        assert 0 <= value <= 1
        
        # Test minor key
        value = analyzer._camelot_to_numeric('Am')
        assert 0 <= value <= 1
        
        # Major should be higher than minor for same position
        major_val = analyzer._camelot_to_numeric('C')
        minor_val = analyzer._camelot_to_numeric('Am')
        assert major_val > minor_val
```

### 2.2 Test Storage Service
Create `tests/unit/test_storage_service.py`:

```python
"""Unit tests for storage service."""

import pytest
import numpy as np

from src.services.storage_service import StorageService

class TestStorageService:
    """Test storage service functionality."""
    
    def test_track_creation(self, test_db):
        """Test track creation and retrieval."""
        storage = StorageService("sqlite:///:memory:")
        
        # Create track
        track_id = storage.get_or_create_track(
            "/test/file.mp3",
            {'title': 'Test', 'artist': 'Artist'}
        )
        
        assert track_id > 0
        
        # Retrieve track
        track = storage.get_track_by_path("/test/file.mp3")
        assert track is not None
        assert track['title'] == 'Test'
    
    def test_analysis_storage(self, test_db):
        """Test analysis result storage."""
        storage = StorageService("sqlite:///:memory:")
        
        # Create track
        track_id = storage.get_or_create_track("/test/file.mp3")
        
        # Store analysis
        analysis_data = {
            'bpm': 128.0,
            'key': 'Am',
            'energy': 0.7,
            'confidence': 0.9
        }
        
        analysis_id = storage.store_analysis_result(track_id, analysis_data)
        assert analysis_id > 0
        
        # Retrieve analysis
        result = storage.get_analysis_by_track(track_id)
        assert result is not None
        assert result['analysis']['bpm'] == 128.0
    
    def test_hamms_vector_storage(self, test_db, test_hamms_vector):
        """Test HAMMS vector storage."""
        storage = StorageService("sqlite:///:memory:")
        
        # Create track
        track_id = storage.get_or_create_track("/test/file.mp3")
        
        # Store HAMMS vector
        hamms_data = {
            'hamms_vector': test_hamms_vector,
            'confidence': 0.85,
            'version': '3.0'
        }
        
        hamms_id = storage.store_hamms_vector(track_id, hamms_data)
        assert hamms_id > 0
        
        # Retrieve and verify
        result = storage.get_analysis_by_track(track_id)
        assert result['hamms'] is not None
        assert len(result['hamms']['vector']) == 12
```

## Step 3: Integration Tests

### 3.1 Test End-to-End Analysis
Create `tests/integration/test_analysis_pipeline.py`:

```python
"""Integration tests for complete analysis pipeline."""

import pytest
from pathlib import Path

from src.analysis.enhanced_analyzer import EnhancedAnalyzer

class TestAnalysisPipeline:
    """Test complete analysis pipeline."""
    
    @pytest.mark.integration
    def test_complete_analysis(self, test_config, temp_audio_file):
        """Test complete track analysis pipeline."""
        analyzer = EnhancedAnalyzer(test_config)
        
        # Analyze track (without AI for testing)
        result = analyzer.analyze_track(
            temp_audio_file,
            use_ai=False,
            store_results=True
        )
        
        assert result is not None
        assert result.file_path == temp_audio_file
        assert len(result.hamms_vector) == 12
        assert result.confidence > 0
    
    @pytest.mark.integration
    def test_library_analysis(self, test_config, temp_dir):
        """Test library analysis."""
        analyzer = EnhancedAnalyzer(test_config)
        
        # Create test files
        test_files = []
        for i in range(3):
            file_path = temp_dir / f"test_{i}.wav"
            file_path.touch()
            test_files.append(str(file_path))
        
        # Analyze library
        results = analyzer.analyze_library(
            str(temp_dir),
            use_ai=False,
            parallel=False
        )
        
        assert len(results) == 3
        for result in results:
            assert result.file_path in test_files
```

### 3.2 Test LLM Integration
Create `tests/integration/test_llm_integration.py`:

```python
"""Integration tests for LLM providers."""

import pytest
from unittest.mock import Mock, patch

from src.analysis.providers.provider_manager import ProviderManager, SelectionStrategy
from src.analysis.providers.base_provider import AnalysisRequest, AnalysisResponse

class TestLLMIntegration:
    """Test LLM provider integration."""
    
    @pytest.mark.integration
    def test_provider_manager(self, test_config):
        """Test provider manager initialization."""
        manager = ProviderManager(test_config)
        assert manager is not None
        
        stats = manager.get_provider_statistics()
        assert 'registered' in stats
    
    @pytest.mark.integration
    @patch('src.analysis.providers.openai_provider.OpenAI')
    def test_provider_fallback(self, mock_openai, test_config, test_track_data):
        """Test provider fallback mechanism."""
        # Mock OpenAI to fail
        mock_openai.side_effect = Exception("API Error")
        
        manager = ProviderManager(test_config)
        
        # Should fallback to next provider
        response = manager.analyze(
            test_track_data,
            preferences=None
        )
        
        # Verify fallback attempted
        assert response is not None
```

## Step 4: Performance Tests

### 4.1 Create Performance Tests
Create `tests/performance/test_performance.py`:

```python
"""Performance tests for MAP4."""

import pytest
import time
import numpy as np

from src.analysis.hamms_v3 import HAMMSAnalyzer

class TestPerformance:
    """Test system performance."""
    
    @pytest.mark.performance
    def test_hamms_calculation_speed(self):
        """Test HAMMS calculation performance."""
        analyzer = HAMMSAnalyzer()
        
        # Generate test data
        test_data = {
            'bpm': 128,
            'key': 'Am',
            'energy': 0.7,
            'genre': 'house'
        }
        
        # Measure time for 1000 calculations
        start = time.time()
        for _ in range(1000):
            result = analyzer.calculate_extended_vector(test_data)
        elapsed = time.time() - start
        
        # Should complete 1000 calculations in under 1 second
        assert elapsed < 1.0, f"Too slow: {elapsed:.2f}s for 1000 calculations"
        
        # Calculate throughput
        throughput = 1000 / elapsed
        print(f"HAMMS throughput: {throughput:.0f} vectors/second")
    
    @pytest.mark.performance
    def test_similarity_calculation_speed(self):
        """Test similarity calculation performance."""
        analyzer = HAMMSAnalyzer()
        
        # Generate test vectors
        vectors = [np.random.random(12) for _ in range(100)]
        
        # Measure pairwise similarity calculation
        start = time.time()
        for v1 in vectors:
            for v2 in vectors:
                analyzer.calculate_similarity(v1, v2)
        elapsed = time.time() - start
        
        # 10,000 comparisons should complete in under 5 seconds
        assert elapsed < 5.0, f"Too slow: {elapsed:.2f}s for 10,000 comparisons"
        
        throughput = 10000 / elapsed
        print(f"Similarity throughput: {throughput:.0f} comparisons/second")
```

## Step 5: System Integration

### 5.1 Create Integration Script
Create `scripts/integrate_system.py`:

```python
#!/usr/bin/env python3
"""System integration and validation script."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def verify_components():
    """Verify all components are properly integrated."""
    print("MAP4 System Integration Check")
    print("=" * 50)
    
    components = []
    
    # Check core components
    try:
        from src.analysis.hamms_v3 import HAMMSAnalyzer
        components.append(("HAMMS v3.0 Engine", True))
    except ImportError as e:
        components.append(("HAMMS v3.0 Engine", False, str(e)))
    
    try:
        from src.lib.audio_processing import AudioProcessor
        components.append(("Audio Processing", True))
    except ImportError as e:
        components.append(("Audio Processing", False, str(e)))
    
    try:
        from src.services.storage_service import StorageService
        components.append(("Storage Service", True))
    except ImportError as e:
        components.append(("Storage Service", False, str(e)))
    
    try:
        from src.analysis.providers.provider_manager import ProviderManager
        components.append(("LLM Integration", True))
    except ImportError as e:
        components.append(("LLM Integration", False, str(e)))
    
    try:
        from src.ui.enhanced_main_window import EnhancedMainWindow
        components.append(("GUI Interface", True))
    except ImportError as e:
        components.append(("GUI Interface", False, str(e)))
    
    try:
        from src.cli.unified_main import cli
        components.append(("CLI System", True))
    except ImportError as e:
        components.append(("CLI System", False, str(e)))
    
    try:
        from src.bmad.bmad_engine import BMADEngine
        components.append(("BMAD Framework", True))
    except ImportError as e:
        components.append(("BMAD Framework", False, str(e)))
    
    # Display results
    all_ok = True
    for component in components:
        if component[1]:
            print(f"✓ {component[0]}")
        else:
            print(f"✗ {component[0]}: {component[2] if len(component) > 2 else 'Failed'}")
            all_ok = False
    
    return all_ok

def test_basic_workflow():
    """Test basic analysis workflow."""
    print("\nTesting Basic Workflow")
    print("-" * 50)
    
    try:
        from src.analysis.hamms_v3 import HAMMSAnalyzer
        
        # Test HAMMS calculation
        analyzer = HAMMSAnalyzer()
        test_data = {
            'bpm': 128,
            'key': 'Am',
            'energy': 0.7,
            'genre': 'house'
        }
        
        result = analyzer.calculate_extended_vector(test_data)
        
        if len(result['hamms_vector']) == 12:
            print("✓ HAMMS vector calculation successful")
        else:
            print("✗ HAMMS vector calculation failed")
            return False
        
        # Test similarity
        similarity = analyzer.calculate_similarity(
            result['hamms_vector'],
            result['hamms_vector']
        )
        
        if similarity['overall_similarity'] > 0.99:
            print("✓ Similarity calculation successful")
        else:
            print("✗ Similarity calculation failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Workflow test failed: {e}")
        return False

def main():
    """Main integration test."""
    # Verify components
    components_ok = verify_components()
    
    # Test workflow
    workflow_ok = test_basic_workflow()
    
    # Summary
    print("\n" + "=" * 50)
    if components_ok and workflow_ok:
        print("✓ System integration successful!")
        print("MAP4 is ready for use.")
        return 0
    else:
        print("✗ Integration issues detected.")
        print("Please review the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

## Step 6: Deployment Preparation

### 6.1 Create Setup Script
Create `setup.py`:

```python
"""Setup script for MAP4."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="map4-music-analyzer",
    version="3.0.0",
    author="MAP4 Development Team",
    description="Professional music analysis with HAMMS v3.0 and AI enrichment",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/map4/music-analyzer-pro",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Sound/Audio :: Analysis",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "map4=src.cli.unified_main:main",
            "map4-gui=src.ui.enhanced_main_window:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.json"],
    },
)
```

### 6.2 Create Docker Configuration
Create `Dockerfile`:

```dockerfile
# MAP4 Docker image
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY src/ ./src/
COPY config/ ./config/

# Create data directories
RUN mkdir -p data/database data/cache data/logs data/exports

# Set environment variables
ENV PYTHONPATH=/app
ENV MAP4_CONFIG=/app/config/map4.yaml

# Entry point
ENTRYPOINT ["python", "-m", "src.cli.unified_main"]
```

## Step 7: Continuous Integration

### 7.1 Create GitHub Actions Workflow
Create `.github/workflows/ci.yml`:

```yaml
name: MAP4 CI

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, "3.10", 3.11]

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov
    
    - name: Run tests
      run: |
        pytest tests/unit -v --cov=src
    
    - name: Run integration tests
      run: |
        pytest tests/integration -v -m integration
    
    - name: Check code quality
      run: |
        pip install black pylint mypy
        black --check src/
        pylint src/
        mypy src/
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

## Success Criteria

Integration and testing is complete when:

1. **Unit Tests**: >80% code coverage with all critical paths tested
2. **Integration Tests**: End-to-end workflows validated
3. **Performance Tests**: Meeting throughput requirements
4. **System Integration**: All components working together
5. **CI/CD Pipeline**: Automated testing on commits
6. **Deployment Ready**: Docker image and setup script functional
7. **Documentation**: Complete API and user documentation

## Running Tests

```bash
# Run all tests
pytest

# Run unit tests only
pytest tests/unit -v

# Run integration tests
pytest tests/integration -v -m integration

# Run performance tests
pytest tests/performance -v -m performance

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/unit/test_hamms_v3.py -v

# Run system integration check
python scripts/integrate_system.py
```

## Deployment

```bash
# Install locally
pip install -e .

# Build Docker image
docker build -t map4:latest .

# Run Docker container
docker run -v /music:/music map4:latest analyze library /music

# Create distribution
python setup.py sdist bdist_wheel

# Upload to PyPI (requires credentials)
twine upload dist/*
```

## Final Validation Checklist

- [ ] All unit tests passing
- [ ] Integration tests successful
- [ ] Performance benchmarks met
- [ ] CLI commands functional
- [ ] GUI launches without errors
- [ ] BMAD certification passes
- [ ] Docker image builds
- [ ] Documentation complete
- [ ] CI/CD pipeline green

This completes the MAP4 reproduction guide with full testing and deployment preparation.