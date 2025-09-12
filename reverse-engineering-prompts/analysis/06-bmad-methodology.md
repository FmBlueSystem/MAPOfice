# BMAD Methodology Integration

## Overview
BMAD (Balanced Music Analysis and Development) is MAP4's core methodology for systematic music analysis validation, optimization, and certification. It provides a framework for ensuring analysis quality, optimizing prompts for AI providers, and validating results against professional standards.

## BMAD Core Philosophy
BMAD operates on the principle of **"Measure, Analyze, Develop"** with emphasis on:
- **Balanced Analysis**: Multiple validation approaches for robust results
- **Iterative Optimization**: Continuous improvement through feedback loops
- **Professional Standards**: Meeting DJ and music industry requirements
- **Data-Driven Decisions**: Evidence-based analysis refinement

## Architecture Overview

### BMAD Engine (`src/bmad/core.py`)
```python
class BMADEngine:
    """
    Central BMAD methodology engine
    
    Consolidates functionality from:
    - BMADPlaylistCertificationDemo
    - BMAD100PercentValidator  
    - BMADPromptOptimizer
    - BMADRealDataOptimizer
    - BMADPureMetadataOptimizer
    """
    
    def __init__(self, config: BMADConfig):
        self.config = config
        self.current_cycle = 0
        self.llm_provider = None
        self.results_cache = {}
```

### BMAD Operation Modes
```python
class BMADMode(Enum):
    """BMAD operation modes"""
    CERTIFICATION = "certification"    # Validate analysis accuracy
    OPTIMIZATION = "optimization"      # Improve prompt performance  
    VALIDATION = "validation"          # Check data integrity
    PURE_METADATA = "pure_metadata"    # Non-AI metadata analysis
    REAL_DATA = "real_data"           # Real-world data optimization
```

### Configuration System
```python
@dataclass
class BMADConfig:
    """BMAD engine configuration"""
    mode: BMADMode
    llm_provider: Optional[LLMConfig] = None
    certification_threshold: float = 0.80      # 80% accuracy required
    max_optimization_cycles: int = 3           # Maximum improvement iterations
    batch_size: int = 10                       # Tracks per batch
    enable_caching: bool = True                # Cache optimization results
    output_format: str = "json"               # Result format
    metadata_only: bool = False               # Skip AI analysis
```

## BMAD Modes Deep Dive

### 1. Certification Mode
Validates that analysis meets professional DJ standards with required accuracy thresholds.

```python
def _execute_certification(self, tracks: List[Dict]) -> BMADResult:
    """Execute BMAD certification methodology"""
    from .certification import CertificationValidator
    
    validator = CertificationValidator(
        threshold=self.config.certification_threshold,
        max_cycles=self.config.max_optimization_cycles
    )
    
    certification_report = validator.validate_tracks(tracks, self.llm_provider)
    
    return BMADResult(
        success=certification_report.certified,
        mode=BMADMode.CERTIFICATION,
        results={
            'certification_report': certification_report.to_dict(),
            'tracks_analyzed': len(tracks),
            'certification_rate': certification_report.certification_rate
        },
        metrics={
            'accuracy': certification_report.accuracy,
            'precision': certification_report.precision,
            'recall': certification_report.recall,
            'f1_score': certification_report.f1_score
        }
    )
```

#### Certification Criteria
- **BPM Accuracy**: ±2 BPM tolerance for DJ mixing
- **Key Detection**: Must match Camelot wheel standards
- **Genre Classification**: 80% agreement with expert validation
- **Energy Levels**: Consistent across similar tracks
- **HAMMS Vectors**: Must pass mathematical validation

#### Certification Process
1. **Ground Truth Establishment**: Use expert-validated reference tracks
2. **Analysis Execution**: Run MAP4 analysis on certification set
3. **Accuracy Calculation**: Compare results against ground truth
4. **Threshold Validation**: Check if accuracy meets 80% threshold
5. **Report Generation**: Detailed certification report with recommendations

### 2. Optimization Mode
Iteratively improves AI prompt performance through systematic testing and refinement.

```python
def _execute_optimization(self, tracks: List[Dict]) -> BMADResult:
    """Execute BMAD optimization methodology"""
    from .optimization import PromptOptimizer, OptimizationCycle
    
    optimizer = PromptOptimizer(
        max_cycles=self.config.max_optimization_cycles,
        target_accuracy=self.config.certification_threshold
    )
    
    optimization_results = optimizer.optimize(tracks, self.llm_provider)
    
    return BMADResult(
        success=optimization_results['final_accuracy'] >= self.config.certification_threshold,
        mode=BMADMode.OPTIMIZATION,
        results=optimization_results,
        metrics={
            'initial_accuracy': optimization_results.get('initial_accuracy', 0.0),
            'final_accuracy': optimization_results.get('final_accuracy', 0.0),
            'improvement': optimization_results.get('improvement', 0.0)
        },
        cycles_completed=optimization_results.get('cycles_completed', 0)
    )
```

#### Optimization Cycle Process
1. **Baseline Measurement**: Establish current prompt performance
2. **Hypothesis Generation**: Identify potential improvements
3. **Prompt Modification**: Implement systematic changes
4. **A/B Testing**: Compare new vs. old prompt performance
5. **Statistical Validation**: Ensure improvements are significant
6. **Implementation**: Deploy improved prompt if validated

#### Optimization Strategies
- **Context Enhancement**: Add more relevant HAMMS vector information
- **Format Standardization**: Improve JSON response consistency
- **Example Addition**: Include few-shot learning examples
- **Constraint Clarification**: Better specify output requirements
- **Provider Adaptation**: Customize prompts for specific LLM providers

### 3. Validation Mode
Ensures data integrity and consistency across the analysis pipeline.

```python
def _execute_validation(self, tracks: List[Dict]) -> BMADResult:
    """Execute BMAD validation methodology"""
    validation_results = {
        'tracks_processed': 0,
        'tracks_validated': 0,
        'validation_errors': [],
        'track_results': []
    }
    
    for track in tracks:
        try:
            validation_result = self._validate_single_track(track)
            validation_results['track_results'].append(validation_result)
            validation_results['tracks_processed'] += 1
            
            if validation_result.success:
                validation_results['tracks_validated'] += 1
                
        except Exception as e:
            validation_results['validation_errors'].append({
                'track': track.get('filename', 'unknown'),
                'error': str(e)
            })
    
    validation_rate = validation_results['tracks_validated'] / max(validation_results['tracks_processed'], 1)
    
    return BMADResult(
        success=validation_rate >= 0.8,  # 80% validation success rate
        mode=BMADMode.VALIDATION,
        results=validation_results,
        metrics={
            'validation_rate': validation_rate,
            'error_rate': len(validation_results['validation_errors']) / max(len(tracks), 1)
        }
    )
```

#### Validation Checks
```python
def _validate_single_track(self, track: Dict[str, Any]) -> TrackAnalysisResult:
    """Validate a single track"""
    try:
        # Basic validation checks
        required_fields = ['title', 'artist']
        optional_fields = ['bpm', 'key', 'energy', 'genre']
        
        missing_required = [field for field in required_fields if not track.get(field)]
        if missing_required:
            return TrackAnalysisResult(
                filename=track.get('filename', 'unknown'),
                success=False,
                analysis_data={},
                confidence=0.0,
                processing_time=0.0,
                error_message=f"Missing required fields: {missing_required}"
            )
        
        # Calculate completeness score
        present_optional = sum(1 for field in optional_fields if track.get(field))
        completeness = present_optional / len(optional_fields)
        
        analysis_data = {
            'title': track['title'],
            'artist': track['artist'],
            'completeness': completeness,
            'has_bpm': bool(track.get('bpm')),
            'has_key': bool(track.get('key')),
            'has_energy': bool(track.get('energy')),
            'has_genre': bool(track.get('genre'))
        }
        
        return TrackAnalysisResult(
            filename=track.get('filename', 'unknown'),
            success=True,
            analysis_data=analysis_data,
            confidence=completeness,
            processing_time=0.01
        )
```

### 4. Pure Metadata Mode
Analyzes metadata without AI inference for baseline performance measurement.

```python
def _execute_pure_metadata(self, tracks: List[Dict]) -> BMADResult:
    """Execute pure metadata analysis (no LLM inference)"""
    from .metadata import MetadataAnalyzer
    
    analyzer = MetadataAnalyzer()
    metadata_results = []
    
    for track in tracks:
        metadata_result = analyzer.analyze_pure_metadata(track)
        metadata_results.append(metadata_result)
    
    success_count = sum(1 for result in metadata_results if result.get('success', False))
    success_rate = success_count / len(tracks) if tracks else 0
    
    return BMADResult(
        success=success_rate >= 0.7,  # 70% success rate for metadata
        mode=BMADMode.PURE_METADATA,
        results={
            'metadata_results': metadata_results,
            'tracks_analyzed': len(tracks),
            'successful_extractions': success_count
        },
        metrics={
            'success_rate': success_rate,
            'metadata_completeness': self._calculate_metadata_completeness(metadata_results)
        }
    )
```

#### Pure Metadata Analysis
- **File Metadata Extraction**: ID3, FLAC, MP4 tags
- **HAMMS Vector Calculation**: Librosa-based audio analysis
- **Basic Feature Extraction**: BPM, key, energy without AI
- **Completeness Assessment**: How much data is available

### 5. Real Data Mode
Optimizes analysis performance using real-world music library data.

```python
def _execute_real_data(self, tracks: List[Dict]) -> BMADResult:
    """Execute real data optimization methodology"""
    from .optimization import DataOptimizer
    
    optimizer = DataOptimizer(
        llm_provider=self.llm_provider,
        max_cycles=self.config.max_optimization_cycles
    )
    
    real_data_results = optimizer.optimize_with_real_data(tracks)
    
    return BMADResult(
        success=real_data_results.get('optimization_success', False),
        mode=BMADMode.REAL_DATA,
        results=real_data_results,
        metrics={
            'optimization_improvement': real_data_results.get('improvement', 0.0),
            'real_data_accuracy': real_data_results.get('final_accuracy', 0.0)
        },
        cycles_completed=real_data_results.get('cycles', 0)
    )
```

## BMAD Certification Framework

### Certification Validator (`src/bmad/certification.py`)
```python
@dataclass
class CertificationReport:
    """BMAD certification report"""
    certified: bool
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    certification_rate: float
    failed_tests: List[str]
    recommendations: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'certified': self.certified,
            'accuracy': self.accuracy,
            'precision': self.precision, 
            'recall': self.recall,
            'f1_score': self.f1_score,
            'certification_rate': self.certification_rate,
            'failed_tests': self.failed_tests,
            'recommendations': self.recommendations
        }

class CertificationValidator:
    """Validates analysis results against professional standards"""
    
    def __init__(self, threshold: float = 0.8, max_cycles: int = 3):
        self.threshold = threshold
        self.max_cycles = max_cycles
        
    def validate_tracks(self, tracks: List[Dict], provider: LLMProvider) -> CertificationReport:
        """Validate tracks and generate certification report"""
        
        results = []
        for track in tracks:
            result = self.validate_single_track(track, provider)
            results.append(result)
        
        # Calculate metrics
        accuracy = self.calculate_accuracy(results)
        precision = self.calculate_precision(results) 
        recall = self.calculate_recall(results)
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        certification_rate = sum(1 for r in results if r.success) / len(results)
        certified = certification_rate >= self.threshold
        
        failed_tests = [r.error_message for r in results if not r.success and r.error_message]
        recommendations = self.generate_recommendations(results)
        
        return CertificationReport(
            certified=certified,
            accuracy=accuracy,
            precision=precision,
            recall=recall,
            f1_score=f1_score,
            certification_rate=certification_rate,
            failed_tests=failed_tests,
            recommendations=recommendations
        )
```

### Professional Standards Validation
```python
def validate_professional_standards(self, track_analysis: Dict) -> List[str]:
    """Validate against professional DJ/producer standards"""
    issues = []
    
    # BPM validation
    bpm = track_analysis.get('bpm')
    if bpm:
        if not (60 <= bpm <= 200):
            issues.append(f"BPM {bpm} outside typical range (60-200)")
        if bpm % 1 != 0 and abs(bpm - round(bpm)) < 0.1:
            issues.append(f"BPM {bpm} should be rounded to nearest integer")
    
    # Key validation
    key = track_analysis.get('key')
    if key:
        valid_keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        if key not in valid_keys:
            issues.append(f"Key '{key}' not in standard chromatic scale")
    
    # Energy validation
    energy = track_analysis.get('energy')
    if energy is not None:
        if not (0 <= energy <= 1):
            issues.append(f"Energy {energy} outside valid range (0-1)")
    
    # HAMMS vector validation
    hamms = track_analysis.get('hamms')
    if hamms:
        if len(hamms) != 12:
            issues.append(f"HAMMS vector has {len(hamms)} dimensions, expected 12")
        if not all(0 <= x <= 1 for x in hamms):
            issues.append("HAMMS vector contains values outside [0,1] range")
    
    return issues
```

## BMAD Optimization Framework

### Prompt Optimization Engine (`src/bmad/optimization.py`)
```python
class PromptOptimizer:
    """Optimizes LLM prompts for better music analysis performance"""
    
    def __init__(self, max_cycles: int = 3, target_accuracy: float = 0.8):
        self.max_cycles = max_cycles
        self.target_accuracy = target_accuracy
        self.optimization_history = []
    
    def optimize(self, tracks: List[Dict], provider: LLMProvider) -> Dict[str, Any]:
        """Run optimization cycles to improve prompt performance"""
        
        # Baseline measurement
        initial_accuracy = self.measure_baseline_performance(tracks, provider)
        
        best_accuracy = initial_accuracy
        best_prompt = provider.get_current_prompt()
        
        for cycle in range(self.max_cycles):
            # Generate improved prompt
            new_prompt = self.generate_improved_prompt(
                current_prompt=best_prompt,
                performance_data=self.optimization_history,
                cycle=cycle
            )
            
            # Test new prompt
            provider.update_prompt(new_prompt)
            new_accuracy = self.measure_performance(tracks, provider)
            
            # Keep if better
            if new_accuracy > best_accuracy:
                best_accuracy = new_accuracy
                best_prompt = new_prompt
            
            self.optimization_history.append({
                'cycle': cycle,
                'prompt': new_prompt,
                'accuracy': new_accuracy,
                'improvement': new_accuracy - initial_accuracy
            })
            
            # Stop if target reached
            if new_accuracy >= self.target_accuracy:
                break
        
        # Set best prompt
        provider.update_prompt(best_prompt)
        
        return {
            'initial_accuracy': initial_accuracy,
            'final_accuracy': best_accuracy,
            'improvement': best_accuracy - initial_accuracy,
            'cycles_completed': len(self.optimization_history),
            'optimization_history': self.optimization_history,
            'best_prompt': best_prompt
        }
```

### Optimization Strategies
```python
def generate_improved_prompt(self, current_prompt: str, performance_data: List[Dict], cycle: int) -> str:
    """Generate improved prompt based on performance data"""
    
    improvements = []
    
    # Analyze common failure patterns
    if cycle == 0:
        # First cycle: Add more context
        improvements.append("Enhanced HAMMS vector interpretation guidelines")
        improvements.append("Specific genre classification examples")
        improvements.append("BPM and key relationship emphasis")
    
    elif cycle == 1:
        # Second cycle: Improve structure
        improvements.append("Stricter JSON output format requirements")
        improvements.append("Confidence scoring guidelines")
        improvements.append("Error case handling instructions")
    
    elif cycle == 2:
        # Third cycle: Fine-tune specifics
        improvements.append("Genre hierarchy clarifications")
        improvements.append("Mood vs energy distinction guidelines")
        improvements.append("Era classification refinements")
    
    # Apply improvements to prompt
    return self.apply_prompt_improvements(current_prompt, improvements)
```

## BMAD Metadata Analysis

### Metadata Analyzer (`src/bmad/metadata.py`)
```python
class MetadataAnalyzer:
    """Analyzes pure metadata without LLM inference"""
    
    def analyze_pure_metadata(self, track: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze track using only available metadata"""
        
        result = {
            'success': True,
            'completeness': 0.0,
            'available_fields': [],
            'missing_fields': [],
            'quality_score': 0.0
        }
        
        # Define expected metadata fields
        expected_fields = [
            'title', 'artist', 'album', 'year', 'genre',
            'bpm', 'key', 'energy', 'duration', 'isrc'
        ]
        
        available = []
        missing = []
        
        for field in expected_fields:
            if track.get(field) and str(track[field]).strip():
                available.append(field)
            else:
                missing.append(field)
        
        result['available_fields'] = available
        result['missing_fields'] = missing
        result['completeness'] = len(available) / len(expected_fields)
        
        # Calculate quality score based on critical fields
        critical_fields = ['title', 'artist', 'bpm', 'key']
        critical_available = sum(1 for field in critical_fields if field in available)
        result['quality_score'] = critical_available / len(critical_fields)
        
        # Professional metadata assessment
        professional_fields = ['isrc', 'bpm', 'key', 'energy']
        professional_available = sum(1 for field in professional_fields if field in available)
        result['professional_readiness'] = professional_available / len(professional_fields)
        
        return result
```

## BMAD CLI Integration

### BMAD Command Group (`src/cli/commands/bmad.py`)
```python
@click.group(name='bmad')
def bmad_group():
    """BMAD methodology commands for analysis validation and optimization."""
    pass

@bmad_group.command()
@click.option('--mode', type=click.Choice(['certification', 'optimization', 'validation', 'pure_metadata', 'real_data']), 
              required=True, help='BMAD operation mode')
@click.option('--input', '-i', type=click.Path(exists=True), required=True, 
              help='Input directory or file for analysis')
@click.option('--threshold', type=float, default=0.80, 
              help='Certification threshold (default: 0.80)')
@click.option('--max-cycles', type=int, default=3, 
              help='Maximum optimization cycles (default: 3)')
@click.option('--provider', type=str, default='anthropic',
              help='LLM provider for AI analysis')
@click.option('--output', '-o', type=click.Path(), 
              help='Output file for results')
@click.pass_context
def run(ctx, mode: str, input: str, threshold: float, max_cycles: int, provider: str, output: str):
    """Run BMAD analysis with specified mode and parameters."""
    
    # Create BMAD configuration
    bmad_config = BMADConfig(
        mode=BMADMode(mode),
        certification_threshold=threshold,
        max_optimization_cycles=max_cycles,
        output_format="json"
    )
    
    # Initialize LLM provider if needed
    if mode in ['certification', 'optimization', 'real_data']:
        try:
            llm_config = LLMConfig.from_env(provider)
            bmad_config.llm_provider = llm_config
        except Exception as e:
            click.echo(f"Error initializing LLM provider: {e}", err=True)
            return
    
    # Create BMAD engine
    engine = BMADEngine(bmad_config)
    
    # Load track data
    tracks = load_track_data(input)
    
    # Execute BMAD analysis
    click.echo(f"Running BMAD {mode} analysis on {len(tracks)} tracks...")
    result = engine.execute(tracks)
    
    # Display results
    display_bmad_results(result, output)
```

## BMAD Result Reporting

### Comprehensive Result Structure
```python
@dataclass
class BMADResult:
    """BMAD engine result"""
    success: bool
    mode: BMADMode
    results: Dict[str, Any]
    metrics: Dict[str, float]
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    processing_time: float = 0.0
    cycles_completed: int = 0
    
    def to_report(self) -> Dict[str, Any]:
        """Generate comprehensive report"""
        return {
            'bmad_analysis': {
                'mode': self.mode.value,
                'success': self.success,
                'processing_time_seconds': self.processing_time,
                'cycles_completed': self.cycles_completed
            },
            'metrics': self.metrics,
            'results': self.results,
            'issues': {
                'errors': self.errors,
                'warnings': self.warnings
            },
            'recommendations': self._generate_recommendations()
        }
    
    def _generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations based on results"""
        recommendations = []
        
        if self.mode == BMADMode.CERTIFICATION:
            accuracy = self.metrics.get('accuracy', 0)
            if accuracy < 0.8:
                recommendations.append(f"Accuracy {accuracy:.1%} below 80% threshold - consider prompt optimization")
            if accuracy < 0.6:
                recommendations.append("Critical accuracy issues - review training data and prompt engineering")
        
        elif self.mode == BMADMode.OPTIMIZATION:
            improvement = self.metrics.get('improvement', 0)
            if improvement < 0.05:
                recommendations.append("Limited optimization improvement - consider alternative strategies")
            if improvement > 0.1:
                recommendations.append(f"Significant improvement achieved ({improvement:.1%}) - consider deployment")
        
        return recommendations
```

## Factory Function and Utilities

### BMAD Engine Factory
```python
def create_bmad_engine(mode: Union[str, BMADMode], **kwargs) -> BMADEngine:
    """Create BMAD engine with specified mode and options"""
    
    if isinstance(mode, str):
        mode = BMADMode(mode)
    
    config = BMADConfig(mode=mode, **kwargs)
    return BMADEngine(config)

# Usage examples:
certification_engine = create_bmad_engine(
    'certification', 
    certification_threshold=0.85,
    max_optimization_cycles=5
)

optimization_engine = create_bmad_engine(
    'optimization',
    llm_provider=LLMConfig.from_env('anthropic'),
    target_accuracy=0.9
)
```

### BMAD Utilities
```python
def bmad_batch_analyze(track_paths: List[str], mode: BMADMode) -> BMADResult:
    """Batch analyze tracks using BMAD methodology"""
    
    engine = create_bmad_engine(mode)
    tracks = [{'path': path} for path in track_paths]
    
    return engine.execute(tracks)

def bmad_compare_providers(tracks: List[Dict], providers: List[str]) -> Dict[str, BMADResult]:
    """Compare multiple LLM providers using BMAD certification"""
    
    results = {}
    
    for provider in providers:
        try:
            engine = create_bmad_engine(
                'certification',
                llm_provider=LLMConfig.from_env(provider)
            )
            
            result = engine.execute(tracks)
            results[provider] = result
            
        except Exception as e:
            results[provider] = BMADResult(
                success=False,
                mode=BMADMode.CERTIFICATION,
                results={},
                metrics={},
                errors=[f"Provider {provider} failed: {str(e)}"]
            )
    
    return results
```

The BMAD methodology provides a comprehensive framework for maintaining and improving analysis quality in MAP4, ensuring that the system meets professional standards while continuously evolving to better serve DJ and music production workflows. Through systematic validation, optimization, and certification processes, BMAD enables data-driven improvements to the entire analysis pipeline.