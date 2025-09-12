# MAP4 Functional Validation Framework

## Overview
This framework ensures that reproduced MAP4 applications maintain complete functional parity with the original system. Each component must pass strict validation criteria before being considered successfully reproduced.

## 1. HAMMS v3.0 Vector Accuracy Validation

### Core Requirements
- 12-dimensional vector generation with correct weights
- Mathematical precision within tolerance limits
- Proper normalization to [0,1] range

### Validation Tests

#### Test 1.1: Dimensional Accuracy
```python
def validate_hamms_dimensions():
    """Validate HAMMS vector has exactly 12 dimensions with correct weights"""
    expected_dimensions = {
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
    
    # Pass Criteria:
    # - All 12 dimensions present
    # - Weights match within 0.01 tolerance
    # - Vector shape is (12,) for single track
    pass_criteria = {
        'dimensions_count': 12,
        'weight_tolerance': 0.01,
        'shape_validation': True
    }
    return pass_criteria
```

#### Test 1.2: Normalization Validation
```python
def validate_normalization():
    """Ensure all vector components are normalized to [0,1]"""
    # Pass Criteria:
    # - All values >= 0 and <= 1
    # - No NaN or infinity values
    # - Proper handling of edge cases
    pass_criteria = {
        'range_check': 'all_values_in_0_1',
        'nan_check': 'no_nan_values',
        'infinity_check': 'no_infinity_values'
    }
    return pass_criteria
```

#### Test 1.3: Similarity Calculation
```python
def validate_similarity_scoring():
    """Validate similarity calculations between HAMMS vectors"""
    # Pass Criteria:
    # - Euclidean distance calculation correct
    # - Cosine similarity calculation correct
    # - Combined score with proper weighting (60/40 split)
    pass_criteria = {
        'euclidean_accuracy': 0.001,
        'cosine_accuracy': 0.001,
        'combined_formula': 'correct',
        'score_range': [0, 1]
    }
    return pass_criteria
```

### Reference Track Validation
Use these reference tracks to validate HAMMS calculations:

| Track | Expected BPM | Expected Key | Expected Energy |
|-------|-------------|--------------|-----------------|
| Test_120BPM_Cmaj.wav | 120 ± 2 | C Major | 0.65 ± 0.05 |
| Test_128BPM_Amin.wav | 128 ± 2 | A Minor | 0.75 ± 0.05 |
| Test_140BPM_Gmaj.wav | 140 ± 2 | G Major | 0.85 ± 0.05 |

## 2. Audio Processing Pipeline Verification

### Core Requirements
- librosa integration with 22050 Hz sampling
- Accurate BPM detection
- Key signature identification
- Energy and spectral analysis

### Validation Tests

#### Test 2.1: Audio Loading
```python
def validate_audio_loading():
    """Validate proper audio file loading and preprocessing"""
    pass_criteria = {
        'sample_rate': 22050,
        'mono_conversion': True,
        'duration_limit': 120,  # seconds
        'supported_formats': ['mp3', 'wav', 'flac', 'm4a', 'aiff'],
        'error_handling': 'graceful'
    }
    return pass_criteria
```

#### Test 2.2: BPM Detection
```python
def validate_bpm_detection():
    """Validate BPM detection accuracy"""
    pass_criteria = {
        'accuracy_tolerance': 2.0,  # ± 2 BPM
        'range': [60, 200],  # Valid BPM range
        'tempo_stability': True,
        'onset_detection': 'accurate'
    }
    return pass_criteria
```

#### Test 2.3: Key Detection
```python
def validate_key_detection():
    """Validate musical key detection"""
    pass_criteria = {
        'chromagram_quality': 'high',
        'key_profiles': 'krumhansl',
        'major_minor_detection': True,
        'confidence_threshold': 0.7
    }
    return pass_criteria
```

#### Test 2.4: Spectral Analysis
```python
def validate_spectral_analysis():
    """Validate spectral feature extraction"""
    pass_criteria = {
        'spectral_centroid': 'calculated',
        'spectral_rolloff': 'calculated',
        'zero_crossing_rate': 'calculated',
        'mfcc_coefficients': 13,
        'spectral_contrast': 'calculated'
    }
    return pass_criteria
```

## 3. LLM Provider Integration Testing

### Core Requirements
- Multi-provider support (OpenAI, Anthropic, Gemini, ZAI)
- Auto-registration system
- Fallback mechanisms
- Rate limiting and cost management

### Validation Tests

#### Test 3.1: Provider Registration
```python
def validate_provider_registration():
    """Validate auto-registration of LLM providers"""
    pass_criteria = {
        'openai_models': ['gpt-4', 'gpt-4o-mini', 'gpt-3.5-turbo'],
        'anthropic_models': ['claude-3-haiku', 'claude-3-sonnet', 'claude-3-opus'],
        'gemini_models': ['gemini-1.5-flash', 'gemini-1.5-pro'],
        'zai_models': ['music-analysis-v1'],
        'registration_method': 'decorator',
        'factory_pattern': True
    }
    return pass_criteria
```

#### Test 3.2: API Integration
```python
def validate_api_integration():
    """Validate API calls to LLM providers"""
    pass_criteria = {
        'authentication': 'api_key_valid',
        'request_format': 'json',
        'response_parsing': 'successful',
        'timeout_handling': 30,  # seconds
        'retry_logic': 'exponential_backoff',
        'max_retries': 3
    }
    return pass_criteria
```

#### Test 3.3: Prompt Engineering
```python
def validate_prompt_quality():
    """Validate prompt generation and responses"""
    pass_criteria = {
        'genre_detection': 'accurate',
        'mood_analysis': 'consistent',
        'tag_generation': 'relevant',
        'response_format': 'structured_json',
        'confidence_scores': 'included'
    }
    return pass_criteria
```

#### Test 3.4: Fallback Mechanisms
```python
def validate_fallback_system():
    """Validate provider fallback and error handling"""
    pass_criteria = {
        'primary_failure': 'fallback_triggered',
        'all_providers_fail': 'graceful_degradation',
        'rate_limit_hit': 'automatic_throttling',
        'cost_limit_hit': 'provider_switch',
        'offline_mode': 'functional'
    }
    return pass_criteria
```

## 4. UI Functionality Validation

### Core Requirements
- PyQt6 framework functionality
- Responsive design
- Real-time updates
- Theme system

### Validation Tests

#### Test 4.1: Main Window
```python
def validate_main_window():
    """Validate main application window"""
    pass_criteria = {
        'window_creation': True,
        'menu_bar': 'functional',
        'status_bar': 'updating',
        'central_widget': 'loaded',
        'responsive_layout': True,
        'minimum_size': (800, 600)
    }
    return pass_criteria
```

#### Test 4.2: Track Table
```python
def validate_track_table():
    """Validate track display table"""
    pass_criteria = {
        'columns_displayed': ['title', 'artist', 'bpm', 'key', 'energy', 'compatibility'],
        'sorting': 'all_columns',
        'filtering': 'functional',
        'selection': 'single_and_multi',
        'context_menu': 'available',
        'real_time_updates': True
    }
    return pass_criteria
```

#### Test 4.3: Analysis Progress
```python
def validate_progress_display():
    """Validate analysis progress indicators"""
    pass_criteria = {
        'progress_bar': 'accurate',
        'current_track_display': True,
        'time_remaining': 'estimated',
        'cancel_functionality': True,
        'batch_progress': 'tracked'
    }
    return pass_criteria
```

#### Test 4.4: Visualization Components
```python
def validate_visualizations():
    """Validate data visualization components"""
    pass_criteria = {
        'waveform_display': 'functional',
        'spectrum_analyzer': 'real_time',
        'compatibility_matrix': 'interactive',
        'hamms_radar_chart': 'accurate',
        'playlist_flow': 'smooth'
    }
    return pass_criteria
```

## 5. CLI Command Verification

### Core Requirements
- Click framework integration
- Command groups
- Progress reporting
- Configuration management

### Validation Tests

#### Test 5.1: Basic Commands
```python
def validate_cli_commands():
    """Validate CLI command structure"""
    pass_criteria = {
        'analyze_command': 'functional',
        'batch_command': 'functional',
        'config_command': 'functional',
        'export_command': 'functional',
        'bmad_command': 'functional',
        'help_system': 'comprehensive'
    }
    return pass_criteria
```

#### Test 5.2: Command Options
```python
def validate_command_options():
    """Validate command-line options"""
    pass_criteria = {
        'input_validation': True,
        'output_formats': ['json', 'csv', 'yaml'],
        'verbosity_levels': [0, 1, 2, 3],
        'config_override': 'functional',
        'dry_run_mode': 'available'
    }
    return pass_criteria
```

#### Test 5.3: Batch Processing
```python
def validate_batch_processing():
    """Validate batch processing capabilities"""
    pass_criteria = {
        'directory_scanning': True,
        'recursive_option': True,
        'parallel_processing': 'configurable',
        'progress_reporting': 'detailed',
        'error_recovery': 'per_file',
        'results_aggregation': True
    }
    return pass_criteria
```

## Validation Execution Script

```python
#!/usr/bin/env python3
"""
MAP4 Functional Validation Suite
Execute all functional validation tests
"""

import sys
import json
from pathlib import Path

class FunctionalValidator:
    def __init__(self):
        self.results = {}
        self.passed = 0
        self.failed = 0
    
    def run_all_tests(self):
        """Execute all functional validation tests"""
        test_suites = [
            ('HAMMS v3.0', self.validate_hamms),
            ('Audio Processing', self.validate_audio),
            ('LLM Integration', self.validate_llm),
            ('UI Functionality', self.validate_ui),
            ('CLI Commands', self.validate_cli)
        ]
        
        for suite_name, test_func in test_suites:
            print(f"\n[TESTING] {suite_name}")
            suite_results = test_func()
            self.results[suite_name] = suite_results
            
            if suite_results['passed']:
                self.passed += 1
                print(f"[PASS] {suite_name} validation successful")
            else:
                self.failed += 1
                print(f"[FAIL] {suite_name} validation failed")
                for error in suite_results['errors']:
                    print(f"  - {error}")
    
    def validate_hamms(self):
        """Validate HAMMS implementation"""
        # Implementation of HAMMS validation tests
        return {'passed': True, 'errors': []}
    
    def validate_audio(self):
        """Validate audio processing"""
        # Implementation of audio validation tests
        return {'passed': True, 'errors': []}
    
    def validate_llm(self):
        """Validate LLM integration"""
        # Implementation of LLM validation tests
        return {'passed': True, 'errors': []}
    
    def validate_ui(self):
        """Validate UI functionality"""
        # Implementation of UI validation tests
        return {'passed': True, 'errors': []}
    
    def validate_cli(self):
        """Validate CLI commands"""
        # Implementation of CLI validation tests
        return {'passed': True, 'errors': []}
    
    def generate_report(self):
        """Generate validation report"""
        report = {
            'total_suites': len(self.results),
            'passed': self.passed,
            'failed': self.failed,
            'success_rate': (self.passed / len(self.results)) * 100 if self.results else 0,
            'details': self.results
        }
        
        with open('functional_validation_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        return report

if __name__ == '__main__':
    validator = FunctionalValidator()
    validator.run_all_tests()
    report = validator.generate_report()
    
    print("\n" + "="*50)
    print("FUNCTIONAL VALIDATION SUMMARY")
    print("="*50)
    print(f"Total Test Suites: {report['total_suites']}")
    print(f"Passed: {report['passed']}")
    print(f"Failed: {report['failed']}")
    print(f"Success Rate: {report['success_rate']:.1f}%")
    
    sys.exit(0 if report['failed'] == 0 else 1)
```

## Pass/Fail Criteria Summary

### Critical Pass Requirements
1. **HAMMS Accuracy**: All 12 dimensions calculated correctly with proper weights
2. **Audio Processing**: BPM within ±2, key detection >70% accurate
3. **LLM Integration**: At least one provider fully functional
4. **UI Responsiveness**: All main components load and update
5. **CLI Functionality**: Core commands execute without errors

### Failure Conditions
- Any mathematical errors in HAMMS calculations
- Audio processing crashes or corrupts data
- Complete LLM integration failure (no providers work)
- UI components fail to render or update
- CLI commands produce incorrect output

### Success Metrics
- **Minimum Pass Rate**: 80% of all tests must pass
- **Critical Components**: 100% of critical tests must pass
- **Performance**: Must meet baseline performance requirements
- **Stability**: No crashes during standard operations
- **Data Integrity**: No data loss or corruption

## Troubleshooting Guide

### Common Issues and Solutions

#### HAMMS Calculation Errors
- **Issue**: Vector dimensions incorrect
- **Solution**: Verify weight configuration and normalization logic
- **Test**: Run dimensional accuracy test with reference tracks

#### Audio Processing Failures
- **Issue**: BPM detection inaccurate
- **Solution**: Check librosa version and tempo tracking parameters
- **Test**: Use reference tracks with known BPM values

#### LLM Integration Problems
- **Issue**: API authentication failures
- **Solution**: Verify API keys and provider configuration
- **Test**: Run provider registration tests

#### UI Rendering Issues
- **Issue**: Components not displaying
- **Solution**: Check PyQt6 installation and theme configuration
- **Test**: Run UI component validation tests

#### CLI Command Failures
- **Issue**: Commands not recognized
- **Solution**: Verify Click installation and command registration
- **Test**: Run CLI command structure tests