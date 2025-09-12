# MAP4 Automated Testing Framework

## Overview
This framework provides comprehensive automated testing for reproduced MAP4 applications, ensuring continuous validation and quality assurance throughout development and deployment.

## 1. Test Suite Architecture

### Test Categories and Coverage

```python
# test_suite_structure.py
"""
MAP4 Test Suite Organization
"""

TEST_CATEGORIES = {
    'unit': {
        'path': 'tests/unit/',
        'coverage_target': 0.85,
        'modules': [
            'audio_processor',
            'hamms_calculator',
            'similarity_scorer',
            'config_manager',
            'database_models'
        ]
    },
    'integration': {
        'path': 'tests/integration/',
        'coverage_target': 0.75,
        'flows': [
            'audio_to_hamms',
            'hamms_to_llm',
            'database_operations',
            'ui_backend_sync'
        ]
    },
    'end_to_end': {
        'path': 'tests/e2e/',
        'coverage_target': 0.70,
        'scenarios': [
            'complete_analysis',
            'batch_processing',
            'playlist_generation',
            'export_operations'
        ]
    },
    'performance': {
        'path': 'tests/performance/',
        'benchmarks': [
            'single_track_speed',
            'batch_throughput',
            'memory_usage',
            'database_queries'
        ]
    },
    'security': {
        'path': 'tests/security/',
        'checks': [
            'api_key_handling',
            'input_validation',
            'sql_injection',
            'path_traversal'
        ]
    }
}
```

## 2. Unit Testing Framework

### Core Component Tests

```python
# tests/unit/test_audio_processor.py
import pytest
import numpy as np
from unittest.mock import Mock, patch
from map4.analysis.audio_processor import AudioProcessor

class TestAudioProcessor:
    """Unit tests for AudioProcessor"""
    
    @pytest.fixture
    def processor(self):
        """Create AudioProcessor instance"""
        return AudioProcessor(sample_rate=22050)
    
    @pytest.fixture
    def mock_audio_data(self):
        """Create mock audio data"""
        duration = 3  # seconds
        sample_rate = 22050
        samples = duration * sample_rate
        return np.random.randn(samples), sample_rate
    
    def test_initialization(self, processor):
        """Test processor initialization"""
        assert processor.sample_rate == 22050
        assert processor.hop_length == 512
        assert processor.n_fft == 2048
    
    @patch('librosa.load')
    def test_load_audio_file(self, mock_load, processor, mock_audio_data):
        """Test audio file loading"""
        mock_load.return_value = mock_audio_data
        
        audio, sr = processor.load_audio('test.mp3')
        
        mock_load.assert_called_once()
        assert sr == 22050
        assert len(audio) > 0
    
    @patch('librosa.beat.beat_track')
    def test_bpm_detection(self, mock_beat_track, processor, mock_audio_data):
        """Test BPM detection"""
        mock_beat_track.return_value = (128.0, np.array([]))
        
        bpm = processor.detect_bpm(mock_audio_data[0], mock_audio_data[1])
        
        assert 60 <= bpm <= 200
        assert isinstance(bpm, float)
    
    def test_energy_calculation(self, processor, mock_audio_data):
        """Test energy level calculation"""
        energy = processor.calculate_energy(mock_audio_data[0])
        
        assert 0 <= energy <= 1
        assert isinstance(energy, float)
    
    @pytest.mark.parametrize("invalid_input", [
        None,
        [],
        np.array([]),
        "not_an_array"
    ])
    def test_invalid_input_handling(self, processor, invalid_input):
        """Test handling of invalid inputs"""
        with pytest.raises((ValueError, TypeError)):
            processor.calculate_energy(invalid_input)
```

### HAMMS Calculator Tests

```python
# tests/unit/test_hamms_calculator.py
import pytest
import numpy as np
from map4.analysis.hamms_calculator import HAMMSCalculator

class TestHAMMSCalculator:
    """Unit tests for HAMMS Calculator"""
    
    @pytest.fixture
    def calculator(self):
        return HAMMSCalculator()
    
    @pytest.fixture
    def sample_features(self):
        return {
            'bpm': 128.0,
            'key': 'C_major',
            'energy': 0.75,
            'spectral_centroid': 2000.0,
            'tempo_stability': 0.95,
            'dynamic_range': 0.6
        }
    
    def test_vector_dimensions(self, calculator, sample_features):
        """Test HAMMS vector has correct dimensions"""
        vector = calculator.calculate(sample_features)
        
        assert len(vector) == 12
        assert all(isinstance(v, float) for v in vector)
    
    def test_normalization(self, calculator, sample_features):
        """Test vector normalization to [0,1]"""
        vector = calculator.calculate(sample_features)
        
        assert all(0 <= v <= 1 for v in vector)
        assert not any(np.isnan(v) for v in vector)
        assert not any(np.isinf(v) for v in vector)
    
    def test_weight_application(self, calculator):
        """Test dimension weight application"""
        features_high_bpm = {'bpm': 180.0}
        features_low_bpm = {'bpm': 60.0}
        
        vector_high = calculator.calculate(features_high_bpm)
        vector_low = calculator.calculate(features_low_bpm)
        
        # BPM dimension should differ significantly
        assert abs(vector_high[0] - vector_low[0]) > 0.3
    
    @pytest.mark.parametrize("missing_feature", [
        'bpm', 'energy', 'spectral_centroid'
    ])
    def test_missing_features(self, calculator, sample_features, missing_feature):
        """Test handling of missing features"""
        del sample_features[missing_feature]
        
        vector = calculator.calculate(sample_features)
        
        assert len(vector) == 12
        assert all(0 <= v <= 1 for v in vector)
    
    def test_deterministic_output(self, calculator, sample_features):
        """Test deterministic output for same input"""
        vector1 = calculator.calculate(sample_features)
        vector2 = calculator.calculate(sample_features)
        
        assert vector1 == vector2
```

## 3. Integration Testing Framework

### Component Integration Tests

```python
# tests/integration/test_pipeline_integration.py
import pytest
import tempfile
from pathlib import Path
from map4.analysis.audio_processor import AudioProcessor
from map4.analysis.hamms_calculator import HAMMSCalculator
from map4.analysis.similarity import SimilarityScorer
from map4.database.models import Track, Analysis, HAMMSVector
from map4.database.session import get_session

class TestPipelineIntegration:
    """Integration tests for analysis pipeline"""
    
    @pytest.fixture
    def temp_audio_file(self):
        """Create temporary audio file"""
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            # Write minimal WAV header and data
            import wave
            with wave.open(f.name, 'wb') as wav:
                wav.setnchannels(1)
                wav.setsampwidth(2)
                wav.setframerate(22050)
                wav.writeframes(b'\x00' * 44100)  # 2 seconds of silence
            yield Path(f.name)
    
    @pytest.fixture
    def pipeline_components(self):
        """Initialize pipeline components"""
        return {
            'processor': AudioProcessor(),
            'calculator': HAMMSCalculator(),
            'scorer': SimilarityScorer()
        }
    
    def test_audio_to_hamms_flow(self, pipeline_components, temp_audio_file):
        """Test audio processing to HAMMS calculation flow"""
        processor = pipeline_components['processor']
        calculator = pipeline_components['calculator']
        
        # Process audio
        features = processor.process_file(str(temp_audio_file))
        assert 'bpm' in features
        assert 'energy' in features
        
        # Calculate HAMMS
        hamms_vector = calculator.calculate(features)
        assert len(hamms_vector) == 12
        assert all(0 <= v <= 1 for v in hamms_vector)
    
    def test_database_persistence(self, pipeline_components, temp_audio_file):
        """Test database storage integration"""
        processor = pipeline_components['processor']
        calculator = pipeline_components['calculator']
        
        # Process and calculate
        features = processor.process_file(str(temp_audio_file))
        hamms_vector = calculator.calculate(features)
        
        # Store in database
        with get_session() as session:
            track = Track(
                file_path=str(temp_audio_file),
                title="Test Track"
            )
            session.add(track)
            session.flush()
            
            analysis = Analysis(
                track_id=track.id,
                bpm=features['bpm'],
                energy=features['energy']
            )
            session.add(analysis)
            session.flush()
            
            hamms = HAMMSVector(
                analysis_id=analysis.id,
                vector=hamms_vector
            )
            session.add(hamms)
            session.commit()
            
            # Verify persistence
            retrieved_track = session.query(Track).filter_by(id=track.id).first()
            assert retrieved_track is not None
            assert len(retrieved_track.analyses) == 1
            assert retrieved_track.analyses[0].hamms_vector is not None
    
    def test_similarity_calculation(self, pipeline_components):
        """Test similarity scoring between tracks"""
        calculator = pipeline_components['calculator']
        scorer = pipeline_components['scorer']
        
        # Create two similar tracks
        features1 = {'bpm': 128, 'energy': 0.75}
        features2 = {'bpm': 130, 'energy': 0.73}
        
        vector1 = calculator.calculate(features1)
        vector2 = calculator.calculate(features2)
        
        similarity = scorer.calculate_similarity(vector1, vector2)
        
        assert 0 <= similarity <= 1
        assert similarity > 0.7  # Should be similar
    
    @pytest.mark.asyncio
    async def test_concurrent_processing(self, pipeline_components, temp_audio_file):
        """Test concurrent track processing"""
        import asyncio
        
        processor = pipeline_components['processor']
        calculator = pipeline_components['calculator']
        
        async def process_track(file_path):
            features = await asyncio.to_thread(processor.process_file, file_path)
            vector = calculator.calculate(features)
            return vector
        
        # Process multiple tracks concurrently
        tasks = [process_track(str(temp_audio_file)) for _ in range(5)]
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 5
        assert all(len(v) == 12 for v in results)
```

## 4. End-to-End Testing

### Complete Workflow Tests

```python
# tests/e2e/test_complete_workflow.py
import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from map4.cli.commands import analyze_command
from map4.ui.main_window import MainWindow

class TestCompleteWorkflow:
    """End-to-end workflow tests"""
    
    def test_cli_analysis_workflow(self, tmp_path):
        """Test complete CLI analysis workflow"""
        # Create test directory with mock audio files
        test_dir = tmp_path / "music"
        test_dir.mkdir()
        
        for i in range(3):
            (test_dir / f"track_{i}.mp3").touch()
        
        # Run analysis command
        from click.testing import CliRunner
        runner = CliRunner()
        
        result = runner.invoke(analyze_command, [
            str(test_dir),
            '--recursive',
            '--output', str(tmp_path / 'results.json')
        ])
        
        assert result.exit_code == 0
        assert 'Analysis complete' in result.output
        assert (tmp_path / 'results.json').exists()
    
    @pytest.mark.gui
    def test_gui_analysis_workflow(self, qtbot):
        """Test GUI analysis workflow"""
        window = MainWindow()
        qtbot.addWidget(window)
        
        # Add test track to table
        window.add_track({
            'file_path': '/test/track.mp3',
            'title': 'Test Track',
            'artist': 'Test Artist'
        })
        
        # Select track
        window.track_table.selectRow(0)
        
        # Trigger analysis
        with qtbot.waitSignal(window.analysis_requested):
            qtbot.mouseClick(window.analyze_btn, Qt.LeftButton)
        
        # Verify progress bar updates
        assert window.progress_bar.value() > 0
    
    def test_batch_processing_workflow(self, tmp_path):
        """Test batch processing of large library"""
        # Create mock library
        library_dir = tmp_path / "library"
        library_dir.mkdir()
        
        for i in range(100):
            (library_dir / f"track_{i:03d}.mp3").touch()
        
        # Process batch
        from map4.core.batch_processor import BatchProcessor
        
        processor = BatchProcessor(workers=4)
        results = processor.process_directory(library_dir)
        
        assert len(results) == 100
        assert all('hamms_vector' in r for r in results)
        assert processor.get_statistics()['success_rate'] > 0.95
```

## 5. Performance Testing

### Benchmark Tests

```python
# tests/performance/test_benchmarks.py
import pytest
import time
import psutil
import numpy as np
from memory_profiler import profile

class TestPerformanceBenchmarks:
    """Performance benchmark tests"""
    
    @pytest.mark.benchmark
    def test_single_track_performance(self, benchmark):
        """Benchmark single track analysis"""
        from map4.analysis.audio_processor import AudioProcessor
        from map4.analysis.hamms_calculator import HAMMSCalculator
        
        processor = AudioProcessor()
        calculator = HAMMSCalculator()
        
        def analyze_track():
            features = processor.process_file('test.mp3')
            vector = calculator.calculate(features)
            return vector
        
        result = benchmark(analyze_track)
        
        # Assert performance requirements
        assert benchmark.stats['mean'] < 5.0  # Less than 5 seconds
        assert benchmark.stats['stddev'] < 1.0  # Consistent performance
    
    @pytest.mark.benchmark
    def test_batch_throughput(self, benchmark):
        """Benchmark batch processing throughput"""
        from map4.core.batch_processor import BatchProcessor
        
        processor = BatchProcessor(workers=4)
        test_files = ['test.mp3'] * 100
        
        def process_batch():
            return processor.process_files(test_files)
        
        result = benchmark(process_batch)
        
        # Calculate throughput
        throughput = 100 / benchmark.stats['mean']  # tracks per second
        assert throughput > 0.5  # At least 30 tracks per minute
    
    @profile
    def test_memory_usage(self):
        """Test memory usage during processing"""
        from map4.analysis.audio_processor import AudioProcessor
        
        processor = AudioProcessor()
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        # Process multiple tracks
        for i in range(10):
            processor.process_file(f'test_{i}.mp3')
        
        final_memory = psutil.Process().memory_info().rss / 1024 / 1024
        memory_increase = final_memory - initial_memory
        
        assert memory_increase < 500  # Less than 500MB increase
    
    def test_database_query_performance(self):
        """Test database query performance"""
        from map4.database.queries import TrackQueries
        import time
        
        queries = TrackQueries()
        
        # Test single track fetch
        start = time.perf_counter()
        track = queries.get_track_by_id(1)
        single_fetch_time = time.perf_counter() - start
        
        assert single_fetch_time < 0.01  # Less than 10ms
        
        # Test compatibility search
        start = time.perf_counter()
        results = queries.find_compatible_tracks(track, limit=100)
        search_time = time.perf_counter() - start
        
        assert search_time < 0.5  # Less than 500ms
```

## 6. Security Testing

### Security Validation Tests

```python
# tests/security/test_security.py
import pytest
from map4.utils.validators import InputValidator
from map4.providers.base_provider import BaseLLMProvider

class TestSecurityValidation:
    """Security validation tests"""
    
    def test_api_key_not_logged(self, caplog):
        """Test API keys are never logged"""
        import logging
        logging.basicConfig(level=logging.DEBUG)
        
        provider = BaseLLMProvider(api_key="sk-secret123", model="test")
        provider.analyze({}, {})
        
        # Check logs don't contain API key
        assert "sk-secret123" not in caplog.text
        assert "secret" not in caplog.text.lower()
    
    @pytest.mark.parametrize("malicious_path", [
        "../../../etc/passwd",
        "..\\..\\..\\windows\\system32",
        "/etc/passwd",
        "C:\\Windows\\System32\\config\\sam",
        "file:///etc/passwd"
    ])
    def test_path_traversal_prevention(self, malicious_path):
        """Test path traversal attack prevention"""
        validator = InputValidator()
        
        with pytest.raises(ValueError):
            validator.validate_file_path(malicious_path)
    
    @pytest.mark.parametrize("sql_injection", [
        "'; DROP TABLE tracks; --",
        "1' OR '1'='1",
        "admin'--",
        "' UNION SELECT * FROM users--"
    ])
    def test_sql_injection_prevention(self, sql_injection):
        """Test SQL injection prevention"""
        from map4.database.queries import TrackQueries
        
        queries = TrackQueries()
        
        # Should safely handle malicious input
        result = queries.search_tracks(sql_injection)
        
        # Query should execute safely and return empty or filtered results
        assert isinstance(result, list)
        assert len(result) == 0 or all(sql_injection not in str(r) for r in result)
    
    def test_input_size_limits(self):
        """Test input size validation"""
        validator = InputValidator()
        
        # Test oversized inputs
        huge_string = "A" * 1000000  # 1MB string
        
        with pytest.raises(ValueError):
            validator.validate_track_title(huge_string)
    
    def test_file_type_validation(self):
        """Test file type validation"""
        validator = InputValidator()
        
        # Valid file types
        assert validator.validate_audio_file("test.mp3") == True
        assert validator.validate_audio_file("test.wav") == True
        
        # Invalid file types
        with pytest.raises(ValueError):
            validator.validate_audio_file("test.exe")
        with pytest.raises(ValueError):
            validator.validate_audio_file("test.sh")
```

## 7. Continuous Integration Configuration

### GitHub Actions Workflow

```yaml
# .github/workflows/test.yml
name: MAP4 Automated Testing

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
        python-version: [3.8, 3.9, 3.10, 3.11]
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Install system dependencies
      run: |
        sudo apt-get update
        sudo apt-get install -y ffmpeg libsndfile1
    
    - name: Install Python dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run linting
      run: |
        black --check map4/
        pylint map4/
        mypy map4/
    
    - name: Run security checks
      run: |
        bandit -r map4/
        safety check
    
    - name: Run unit tests
      run: |
        pytest tests/unit/ -v --cov=map4 --cov-report=xml
    
    - name: Run integration tests
      run: |
        pytest tests/integration/ -v
    
    - name: Run performance tests
      run: |
        pytest tests/performance/ -v --benchmark-only
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: true
```

## 8. Test Automation Scripts

### Master Test Runner

```python
#!/usr/bin/env python3
"""
MAP4 Master Test Runner
Executes all test suites with reporting
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

class TestRunner:
    def __init__(self):
        self.results = {}
        self.start_time = None
        self.end_time = None
    
    def run_test_suite(self, suite_name, command):
        """Run a test suite and capture results"""
        print(f"\n{'='*50}")
        print(f"Running {suite_name} Tests")
        print('='*50)
        
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True
        )
        
        self.results[suite_name] = {
            'exit_code': result.returncode,
            'passed': result.returncode == 0,
            'output': result.stdout,
            'errors': result.stderr
        }
        
        if result.returncode == 0:
            print(f"✅ {suite_name} tests PASSED")
        else:
            print(f"❌ {suite_name} tests FAILED")
            print(result.stderr)
        
        return result.returncode == 0
    
    def run_all_tests(self):
        """Run all test suites"""
        self.start_time = datetime.now()
        
        test_suites = [
            ('Linting', 'black --check map4/ && pylint map4/'),
            ('Type Checking', 'mypy map4/'),
            ('Security', 'bandit -r map4/'),
            ('Unit', 'pytest tests/unit/ -v --cov=map4'),
            ('Integration', 'pytest tests/integration/ -v'),
            ('E2E', 'pytest tests/e2e/ -v'),
            ('Performance', 'pytest tests/performance/ -v'),
        ]
        
        all_passed = True
        for suite_name, command in test_suites:
            passed = self.run_test_suite(suite_name, command)
            all_passed = all_passed and passed
        
        self.end_time = datetime.now()
        return all_passed
    
    def generate_report(self):
        """Generate test report"""
        duration = (self.end_time - self.start_time).total_seconds()
        
        report = {
            'timestamp': self.start_time.isoformat(),
            'duration': duration,
            'suites': self.results,
            'summary': {
                'total': len(self.results),
                'passed': sum(1 for r in self.results.values() if r['passed']),
                'failed': sum(1 for r in self.results.values() if not r['passed'])
            }
        }
        
        # Save JSON report
        with open('test_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        # Generate HTML report
        self._generate_html_report(report)
        
        return report
    
    def _generate_html_report(self, report):
        """Generate HTML test report"""
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>MAP4 Test Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .passed {{ color: green; }}
                .failed {{ color: red; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h1>MAP4 Automated Test Report</h1>
            <p>Generated: {report['timestamp']}</p>
            <p>Duration: {report['duration']:.2f} seconds</p>
            
            <h2>Summary</h2>
            <p>Total Suites: {report['summary']['total']}</p>
            <p class="passed">Passed: {report['summary']['passed']}</p>
            <p class="failed">Failed: {report['summary']['failed']}</p>
            
            <h2>Test Suites</h2>
            <table>
                <tr>
                    <th>Suite</th>
                    <th>Status</th>
                </tr>
        """
        
        for suite, result in report['suites'].items():
            status_class = 'passed' if result['passed'] else 'failed'
            status_text = 'PASSED' if result['passed'] else 'FAILED'
            html += f"""
                <tr>
                    <td>{suite}</td>
                    <td class="{status_class}">{status_text}</td>
                </tr>
            """
        
        html += """
            </table>
        </body>
        </html>
        """
        
        with open('test_report.html', 'w') as f:
            f.write(html)

if __name__ == '__main__':
    runner = TestRunner()
    all_passed = runner.run_all_tests()
    report = runner.generate_report()
    
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    print(f"Total Suites: {report['summary']['total']}")
    print(f"Passed: {report['summary']['passed']}")
    print(f"Failed: {report['summary']['failed']}")
    print(f"Duration: {report['duration']:.2f} seconds")
    print(f"\nDetailed reports saved to:")
    print("  - test_report.json")
    print("  - test_report.html")
    
    sys.exit(0 if all_passed else 1)
```

## 9. Test Coverage Requirements

### Coverage Configuration

```ini
# .coveragerc
[run]
source = map4
omit = 
    */tests/*
    */test_*.py
    */__init__.py
    */config.py

[report]
precision = 2
show_missing = True
skip_covered = False

[html]
directory = htmlcov

[xml]
output = coverage.xml
```

### Coverage Enforcement

```python
# coverage_check.py
"""
Coverage enforcement script
"""

import xml.etree.ElementTree as ET
import sys

def check_coverage(xml_file, threshold=80):
    """Check if coverage meets threshold"""
    tree = ET.parse(xml_file)
    root = tree.getroot()
    
    coverage = float(root.attrib['line-rate']) * 100
    
    print(f"Current coverage: {coverage:.2f}%")
    print(f"Required threshold: {threshold}%")
    
    if coverage >= threshold:
        print("✅ Coverage threshold met!")
        return 0
    else:
        print(f"❌ Coverage below threshold by {threshold - coverage:.2f}%")
        return 1

if __name__ == '__main__':
    exit_code = check_coverage('coverage.xml', threshold=80)
    sys.exit(exit_code)
```

## Pass/Fail Criteria

### Test Suite Requirements
1. **Unit Tests**: > 85% code coverage
2. **Integration Tests**: All component boundaries tested
3. **E2E Tests**: All user workflows validated
4. **Performance Tests**: Meet benchmark requirements
5. **Security Tests**: No critical vulnerabilities

### Automated Validation Gates
- All tests must pass for deployment
- Coverage must exceed thresholds
- No security vulnerabilities allowed
- Performance benchmarks must be met
- Code quality checks must pass

## Continuous Monitoring

### Test Health Dashboard
- Real-time test status monitoring
- Historical trend analysis
- Failure pattern detection
- Performance regression alerts
- Coverage trend tracking

This automated testing framework ensures comprehensive validation of reproduced MAP4 applications through continuous testing and quality assurance.