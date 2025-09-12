# BMAD Methodology Framework Generator Meta-Prompt

## Overview
This meta-prompt generates comprehensive reproduction prompts for creating robust validation methodologies similar to BMAD (Balanced Music Analysis and Development). It provides certification systems, quality assurance frameworks, validation modes, and professional standards compliance patterns.

## Meta-Prompt Template

### BMAD Framework Configuration Parameters
Configure your validation methodology framework:

```yaml
# BMAD Methodology Framework Configuration
FRAMEWORK_CONFIG:
  methodology_name: "{METHODOLOGY_NAME}"          # e.g., "BMAD", "AVAT", "QUAL-GATE"
  domain_focus: "{DOMAIN_FOCUS}"                  # "MUSIC", "SPEECH", "GENERAL_AUDIO", "DATA_SCIENCE"
  validation_depth: "{VALIDATION_DEPTH}"          # "BASIC", "COMPREHENSIVE", "PROFESSIONAL", "RESEARCH"
  
VALIDATION_MODES:
  certification_mode: {CERTIFICATION_MODE}        # true/false - 80% accuracy validation
  optimization_mode: {OPTIMIZATION_MODE}          # true/false - iterative improvement
  validation_mode: {VALIDATION_MODE}              # true/false - data integrity checks
  baseline_mode: {BASELINE_MODE}                  # true/false - performance baseline
  real_data_mode: {REAL_DATA_MODE}               # true/false - real-world testing
  benchmarking_mode: {BENCHMARKING_MODE}         # true/false - comparative analysis

QUALITY_STANDARDS:
  accuracy_threshold: {ACCURACY_THRESHOLD}        # 0.8 (80%)
  consistency_threshold: {CONSISTENCY_THRESHOLD}  # 0.9 (90%)
  reliability_threshold: {RELIABILITY_THRESHOLD}  # 0.95 (95%)
  performance_threshold: {PERFORMANCE_THRESHOLD}  # response time thresholds
  
TESTING_FRAMEWORK:
  unit_testing: {UNIT_TESTING}                   # true/false
  integration_testing: {INTEGRATION_TESTING}      # true/false
  performance_testing: {PERFORMANCE_TESTING}      # true/false
  regression_testing: {REGRESSION_TESTING}        # true/false
  stress_testing: {STRESS_TESTING}               # true/false
  user_acceptance_testing: {UAT_TESTING}         # true/false

METRICS_TRACKING:
  accuracy_metrics: {ACCURACY_METRICS}            # true/false
  performance_metrics: {PERFORMANCE_METRICS}      # true/false
  reliability_metrics: {RELIABILITY_METRICS}      # true/false
  cost_metrics: {COST_METRICS}                   # true/false
  user_satisfaction: {USER_SATISFACTION}         # true/false

REPORTING:
  automated_reporting: {AUTOMATED_REPORTING}      # true/false
  dashboard_metrics: {DASHBOARD_METRICS}          # true/false
  compliance_reports: {COMPLIANCE_REPORTS}        # true/false
  trend_analysis: {TREND_ANALYSIS}               # true/false
  
CERTIFICATION:
  professional_certification: {PROFESSIONAL_CERT} # true/false
  industry_standards: {INDUSTRY_STANDARDS}        # true/false
  compliance_validation: {COMPLIANCE_VALIDATION}  # true/false
  audit_trail: {AUDIT_TRAIL}                     # true/false
```

## Generated BMAD Framework Template

Based on the configuration, this meta-prompt generates:

---

# {METHODOLOGY_NAME} - Professional Validation Methodology Framework

## Methodology Overview
Implement a {VALIDATION_DEPTH}-level validation methodology for {DOMAIN_FOCUS} applications with comprehensive quality assurance, certification systems, and professional standards compliance.

### Core Principles
- **Accuracy First**: {ACCURACY_THRESHOLD*100}% minimum accuracy requirement
- **Consistency**: {CONSISTENCY_THRESHOLD*100}% reproducibility across runs
- **Reliability**: {RELIABILITY_THRESHOLD*100}% system uptime and correctness
- **Transparency**: Complete audit trail and explainable results
- **Continuous Improvement**: Iterative optimization through systematic testing

## Framework Architecture

### 1. Core Validation Engine
Foundation validation system with multiple operational modes:

```python
"""
{METHODOLOGY_NAME} - Professional Validation Methodology Framework
Comprehensive quality assurance and certification system
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Tuple, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum, IntEnum
import logging
import time
import json
import uuid
from datetime import datetime
from pathlib import Path
import numpy as np
import statistics
{#if AUTOMATED_REPORTING}
import matplotlib.pyplot as plt
import seaborn as sns
{/if}
{#if PERFORMANCE_TESTING}
import psutil
import threading
{/if}

logger = logging.getLogger(__name__)

class ValidationMode(Enum):
    """Available validation modes."""
    {#if CERTIFICATION_MODE}
    CERTIFICATION = "certification"
    {/if}
    {#if OPTIMIZATION_MODE}
    OPTIMIZATION = "optimization"
    {/if}
    {#if VALIDATION_MODE}
    VALIDATION = "validation"
    {/if}
    {#if BASELINE_MODE}
    BASELINE = "baseline"
    {/if}
    {#if REAL_DATA_MODE}
    REAL_DATA = "real_data"
    {/if}
    {#if BENCHMARKING_MODE}
    BENCHMARKING = "benchmarking"
    {/if}

class ValidationStatus(IntEnum):
    """Validation status levels."""
    FAILED = 0
    PASSED = 1
    EXCELLENT = 2
    CERTIFIED = 3

class MetricType(Enum):
    """Types of metrics tracked."""
    ACCURACY = "accuracy"
    PERFORMANCE = "performance"
    RELIABILITY = "reliability"
    CONSISTENCY = "consistency"
    COST = "cost"
    USER_SATISFACTION = "user_satisfaction"

@dataclass
class ValidationConfig:
    """Configuration for validation framework."""
    methodology_name: str = "{METHODOLOGY_NAME}"
    domain_focus: str = "{DOMAIN_FOCUS}"
    
    # Thresholds
    accuracy_threshold: float = {ACCURACY_THRESHOLD}
    consistency_threshold: float = {CONSISTENCY_THRESHOLD}
    reliability_threshold: float = {RELIABILITY_THRESHOLD}
    performance_threshold: float = {PERFORMANCE_THRESHOLD}
    
    # Testing configuration
    test_iterations: int = 100
    sample_size_min: int = 50
    statistical_confidence: float = 0.95
    
    # Reporting
    generate_reports: bool = {AUTOMATED_REPORTING}
    save_raw_data: bool = True
    export_metrics: bool = True
    
    def validate(self) -> bool:
        """Validate configuration parameters."""
        if not (0 <= self.accuracy_threshold <= 1):
            return False
        if not (0 <= self.consistency_threshold <= 1):
            return False
        if not (0 <= self.reliability_threshold <= 1):
            return False
        if self.test_iterations <= 0:
            return False
        if self.sample_size_min <= 0:
            return False
        return True

@dataclass
class TestCase:
    """Individual test case definition."""
    test_id: str
    name: str
    description: str
    input_data: Any
    expected_output: Any
    tolerance: float = 0.01
    weight: float = 1.0
    category: str = "general"
    tags: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.test_id:
            self.test_id = str(uuid.uuid4())

@dataclass
class ValidationResult:
    """Result of validation testing."""
    test_id: str
    test_name: str
    mode: ValidationMode
    status: ValidationStatus
    accuracy: float
    performance_time: float
    consistency_score: float
    reliability_score: float
    
    # Detailed metrics
    metrics: Dict[str, float] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    # Metadata
    timestamp: datetime = field(default_factory=datetime.now)
    duration: float = 0.0
    iteration_count: int = 1
    
    # Raw data for analysis
    raw_results: List[Dict[str, Any]] = field(default_factory=list)
    
    def is_certified(self) -> bool:
        """Check if result meets certification standards."""
        return (
            self.accuracy >= {ACCURACY_THRESHOLD} and
            self.consistency_score >= {CONSISTENCY_THRESHOLD} and
            self.reliability_score >= {RELIABILITY_THRESHOLD} and
            self.status >= ValidationStatus.PASSED
        )
    
    def get_overall_score(self) -> float:
        """Calculate overall validation score."""
        weights = {
            'accuracy': 0.4,
            'consistency': 0.3,
            'reliability': 0.2,
            'performance': 0.1
        }
        
        performance_score = 1.0 / (1.0 + self.performance_time)  # Inverse time
        
        overall = (
            weights['accuracy'] * self.accuracy +
            weights['consistency'] * self.consistency_score +
            weights['reliability'] * self.reliability_score +
            weights['performance'] * performance_score
        )
        
        return min(overall, 1.0)

class BaseValidator(ABC):
    """Abstract base class for all validators."""
    
    def __init__(self, config: ValidationConfig):
        """Initialize validator with configuration."""
        self.config = config
        if not self.config.validate():
            raise ValueError("Invalid validation configuration")
        
        self.test_cases: List[TestCase] = []
        self.results_history: List[ValidationResult] = []
        self.current_session_id = str(uuid.uuid4())
        
        logger.info(f"Initialized {self.__class__.__name__} validator")
    
    @abstractmethod
    def run_test(self, test_case: TestCase, system_under_test: Any) -> Dict[str, Any]:
        """Run individual test case. Must be implemented by subclasses."""
        pass
    
    def add_test_case(self, test_case: TestCase):
        """Add test case to validation suite."""
        self.test_cases.append(test_case)
        logger.debug(f"Added test case: {test_case.name}")
    
    def add_test_cases(self, test_cases: List[TestCase]):
        """Add multiple test cases."""
        for test_case in test_cases:
            self.add_test_case(test_case)
    
    {#if CERTIFICATION_MODE}
    def run_certification_mode(self, system_under_test: Any) -> ValidationResult:
        """Run certification validation (80% accuracy requirement)."""
        logger.info("Starting certification mode validation")
        
        start_time = time.time()
        results = []
        errors = []
        
        # Run all test cases
        for test_case in self.test_cases:
            try:
                result = self.run_test(test_case, system_under_test)
                results.append(result)
            except Exception as e:
                error_msg = f"Test {test_case.name} failed: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)
        
        # Calculate certification metrics
        accuracy = self._calculate_accuracy(results)
        consistency = self._calculate_consistency(results)
        reliability = len(results) / len(self.test_cases) if self.test_cases else 0
        performance_time = (time.time() - start_time) / len(results) if results else 0
        
        # Determine certification status
        if accuracy >= self.config.accuracy_threshold:
            status = ValidationStatus.CERTIFIED
        elif accuracy >= 0.6:
            status = ValidationStatus.PASSED
        else:
            status = ValidationStatus.FAILED
        
        validation_result = ValidationResult(
            test_id=f"cert_{self.current_session_id}",
            test_name="Certification Validation",
            mode=ValidationMode.CERTIFICATION,
            status=status,
            accuracy=accuracy,
            performance_time=performance_time,
            consistency_score=consistency,
            reliability_score=reliability,
            errors=errors,
            duration=time.time() - start_time,
            iteration_count=len(results),
            raw_results=results
        )
        
        self.results_history.append(validation_result)
        
        logger.info(f"Certification validation completed: {status.name} (Accuracy: {accuracy:.1%})")
        return validation_result
    {/if}
    
    {#if OPTIMIZATION_MODE}
    def run_optimization_mode(
        self, 
        system_under_test: Any, 
        optimization_target: str = "accuracy",
        max_iterations: int = 10
    ) -> ValidationResult:
        """Run optimization validation with iterative improvement."""
        logger.info("Starting optimization mode validation")
        
        start_time = time.time()
        optimization_results = []
        best_result = None
        best_score = 0.0
        
        for iteration in range(max_iterations):
            logger.info(f"Optimization iteration {iteration + 1}/{max_iterations}")
            
            # Run validation
            results = []
            for test_case in self.test_cases:
                try:
                    result = self.run_test(test_case, system_under_test)
                    results.append(result)
                except Exception as e:
                    logger.warning(f"Test failed in iteration {iteration}: {e}")
            
            # Calculate metrics
            accuracy = self._calculate_accuracy(results)
            consistency = self._calculate_consistency(results)
            
            # Determine if this is the best result
            if optimization_target == "accuracy":
                score = accuracy
            elif optimization_target == "consistency":
                score = consistency
            else:
                score = (accuracy + consistency) / 2
            
            if score > best_score:
                best_score = score
                best_result = results
            
            optimization_results.append({
                'iteration': iteration + 1,
                'accuracy': accuracy,
                'consistency': consistency,
                'score': score,
                'results': results
            })
            
            # Early stopping if target achieved
            if score >= 0.95:
                logger.info(f"Target score achieved at iteration {iteration + 1}")
                break
        
        # Create final result
        final_accuracy = self._calculate_accuracy(best_result)
        final_consistency = self._calculate_consistency(best_result)
        
        validation_result = ValidationResult(
            test_id=f"opt_{self.current_session_id}",
            test_name="Optimization Validation",
            mode=ValidationMode.OPTIMIZATION,
            status=ValidationStatus.PASSED if final_accuracy >= 0.6 else ValidationStatus.FAILED,
            accuracy=final_accuracy,
            performance_time=(time.time() - start_time) / len(optimization_results),
            consistency_score=final_consistency,
            reliability_score=1.0,  # All iterations completed
            duration=time.time() - start_time,
            iteration_count=len(optimization_results),
            raw_results=optimization_results
        )
        
        self.results_history.append(validation_result)
        
        logger.info(f"Optimization completed: Best score {best_score:.1%}")
        return validation_result
    {/if}
    
    {#if VALIDATION_MODE}
    def run_validation_mode(self, system_under_test: Any) -> ValidationResult:
        """Run data integrity validation."""
        logger.info("Starting validation mode (data integrity)")
        
        start_time = time.time()
        validation_checks = []
        
        # Run comprehensive validation checks
        for test_case in self.test_cases:
            try:
                # Run test multiple times for consistency
                test_results = []
                for _ in range(5):  # 5 iterations for consistency check
                    result = self.run_test(test_case, system_under_test)
                    test_results.append(result)
                
                # Analyze consistency
                consistency = self._analyze_test_consistency(test_results)
                validation_checks.append({
                    'test_case': test_case.name,
                    'results': test_results,
                    'consistency': consistency
                })
                
            except Exception as e:
                logger.error(f"Validation check failed for {test_case.name}: {e}")
        
        # Calculate overall validation metrics
        overall_consistency = np.mean([check['consistency'] for check in validation_checks])
        accuracy = self._calculate_accuracy([
            result for check in validation_checks 
            for result in check['results']
        ])
        
        validation_result = ValidationResult(
            test_id=f"val_{self.current_session_id}",
            test_name="Data Integrity Validation",
            mode=ValidationMode.VALIDATION,
            status=ValidationStatus.PASSED if overall_consistency >= 0.9 else ValidationStatus.FAILED,
            accuracy=accuracy,
            performance_time=(time.time() - start_time) / len(validation_checks),
            consistency_score=overall_consistency,
            reliability_score=1.0,
            duration=time.time() - start_time,
            raw_results=validation_checks
        )
        
        self.results_history.append(validation_result)
        return validation_result
    {/if}
    
    {#if BASELINE_MODE}
    def run_baseline_mode(self, system_under_test: Any) -> ValidationResult:
        """Run baseline performance validation."""
        logger.info("Starting baseline mode validation")
        
        start_time = time.time()
        baseline_results = []
        
        # Run baseline tests without any optimizations
        for test_case in self.test_cases:
            test_start = time.time()
            try:
                result = self.run_test(test_case, system_under_test)
                result['processing_time'] = time.time() - test_start
                baseline_results.append(result)
            except Exception as e:
                logger.warning(f"Baseline test failed: {e}")
        
        # Calculate baseline metrics
        accuracy = self._calculate_accuracy(baseline_results)
        avg_processing_time = np.mean([r.get('processing_time', 0) for r in baseline_results])
        
        validation_result = ValidationResult(
            test_id=f"base_{self.current_session_id}",
            test_name="Baseline Validation",
            mode=ValidationMode.BASELINE,
            status=ValidationStatus.PASSED,  # Baseline always passes
            accuracy=accuracy,
            performance_time=avg_processing_time,
            consistency_score=1.0,  # Single run, perfect consistency
            reliability_score=1.0,
            duration=time.time() - start_time,
            raw_results=baseline_results
        )
        
        self.results_history.append(validation_result)
        return validation_result
    {/if}
    
    {#if REAL_DATA_MODE}
    def run_real_data_mode(self, system_under_test: Any, real_data_path: str) -> ValidationResult:
        """Run validation with real-world data."""
        logger.info("Starting real data mode validation")
        
        start_time = time.time()
        
        # Load real-world test data
        real_test_cases = self._load_real_world_data(real_data_path)
        
        real_results = []
        for test_case in real_test_cases:
            try:
                result = self.run_test(test_case, system_under_test)
                real_results.append(result)
            except Exception as e:
                logger.warning(f"Real data test failed: {e}")
        
        # Calculate real-world performance
        accuracy = self._calculate_accuracy(real_results)
        consistency = self._calculate_consistency(real_results)
        
        validation_result = ValidationResult(
            test_id=f"real_{self.current_session_id}",
            test_name="Real Data Validation",
            mode=ValidationMode.REAL_DATA,
            status=ValidationStatus.PASSED if accuracy >= 0.7 else ValidationStatus.FAILED,
            accuracy=accuracy,
            performance_time=(time.time() - start_time) / len(real_results) if real_results else 0,
            consistency_score=consistency,
            reliability_score=len(real_results) / len(real_test_cases) if real_test_cases else 0,
            duration=time.time() - start_time,
            raw_results=real_results
        )
        
        self.results_history.append(validation_result)
        return validation_result
    
    def _load_real_world_data(self, data_path: str) -> List[TestCase]:
        """Load real-world test data from file."""
        # Implementation would load actual test data
        # This is a placeholder
        return self.test_cases[:10]  # Use first 10 test cases as example
    {/if}
    
    {#if BENCHMARKING_MODE}
    def run_benchmarking_mode(
        self, 
        systems: Dict[str, Any], 
        reference_system: str = None
    ) -> Dict[str, ValidationResult]:
        """Run comparative benchmarking between systems."""
        logger.info("Starting benchmarking mode validation")
        
        benchmark_results = {}
        
        for system_name, system in systems.items():
            logger.info(f"Benchmarking system: {system_name}")
            
            start_time = time.time()
            results = []
            
            for test_case in self.test_cases:
                try:
                    result = self.run_test(test_case, system)
                    result['system_name'] = system_name
                    results.append(result)
                except Exception as e:
                    logger.warning(f"Benchmark test failed for {system_name}: {e}")
            
            # Calculate benchmark metrics
            accuracy = self._calculate_accuracy(results)
            consistency = self._calculate_consistency(results)
            performance_time = (time.time() - start_time) / len(results) if results else 0
            
            validation_result = ValidationResult(
                test_id=f"bench_{system_name}_{self.current_session_id}",
                test_name=f"Benchmark: {system_name}",
                mode=ValidationMode.BENCHMARKING,
                status=ValidationStatus.PASSED,
                accuracy=accuracy,
                performance_time=performance_time,
                consistency_score=consistency,
                reliability_score=1.0,
                duration=time.time() - start_time,
                raw_results=results
            )
            
            benchmark_results[system_name] = validation_result
        
        # Store all benchmark results
        self.results_history.extend(benchmark_results.values())
        
        return benchmark_results
    {/fi}
    
    def _calculate_accuracy(self, results: List[Dict[str, Any]]) -> float:
        """Calculate accuracy from test results."""
        if not results:
            return 0.0
        
        accurate_results = 0
        for result in results:
            # Implementation depends on result structure
            # This is a placeholder calculation
            if result.get('success', False):
                accurate_results += 1
        
        return accurate_results / len(results)
    
    def _calculate_consistency(self, results: List[Dict[str, Any]]) -> float:
        """Calculate consistency score from results."""
        if len(results) < 2:
            return 1.0
        
        # Calculate coefficient of variation as consistency measure
        values = [result.get('score', 0.5) for result in results]
        if not values or statistics.stdev(values) == 0:
            return 1.0
        
        cv = statistics.stdev(values) / statistics.mean(values)
        consistency = 1.0 / (1.0 + cv)  # Inverse relationship
        
        return min(consistency, 1.0)
    
    def _analyze_test_consistency(self, test_results: List[Dict[str, Any]]) -> float:
        """Analyze consistency across multiple test runs."""
        if len(test_results) < 2:
            return 1.0
        
        # Extract key metrics for consistency analysis
        scores = []
        for result in test_results:
            if 'accuracy' in result:
                scores.append(result['accuracy'])
            elif 'score' in result:
                scores.append(result['score'])
            else:
                scores.append(0.5)  # Default neutral score
        
        if not scores:
            return 0.0
        
        # Calculate consistency as inverse of coefficient of variation
        if len(set(scores)) == 1:  # All scores identical
            return 1.0
        
        mean_score = statistics.mean(scores)
        if mean_score == 0:
            return 0.0
        
        cv = statistics.stdev(scores) / mean_score
        consistency = 1.0 / (1.0 + cv)
        
        return consistency
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """Generate comprehensive validation report."""
        if not self.results_history:
            return {"error": "No validation results available"}
        
        report = {
            "methodology": self.config.methodology_name,
            "domain": self.config.domain_focus,
            "session_id": self.current_session_id,
            "generated_at": datetime.now().isoformat(),
            "summary": {},
            "detailed_results": {},
            "recommendations": [],
            "certification_status": {}
        }
        
        # Summary statistics
        total_tests = len(self.results_history)
        certified_results = [r for r in self.results_history if r.is_certified()]
        passed_results = [r for r in self.results_history if r.status >= ValidationStatus.PASSED]
        
        report["summary"] = {
            "total_validations": total_tests,
            "passed_validations": len(passed_results),
            "certified_validations": len(certified_results),
            "pass_rate": len(passed_results) / total_tests if total_tests else 0,
            "certification_rate": len(certified_results) / total_tests if total_tests else 0,
            "average_accuracy": statistics.mean([r.accuracy for r in self.results_history]),
            "average_consistency": statistics.mean([r.consistency_score for r in self.results_history]),
            "average_reliability": statistics.mean([r.reliability_score for r in self.results_history])
        }
        
        # Detailed results by mode
        for result in self.results_history:
            mode_name = result.mode.value
            if mode_name not in report["detailed_results"]:
                report["detailed_results"][mode_name] = []
            
            report["detailed_results"][mode_name].append({
                "test_name": result.test_name,
                "status": result.status.name,
                "accuracy": result.accuracy,
                "consistency": result.consistency_score,
                "reliability": result.reliability_score,
                "performance_time": result.performance_time,
                "overall_score": result.get_overall_score(),
                "certified": result.is_certified(),
                "timestamp": result.timestamp.isoformat()
            })
        
        # Certification status
        latest_cert_result = None
        for result in reversed(self.results_history):
            if result.mode == ValidationMode.CERTIFICATION:
                latest_cert_result = result
                break
        
        if latest_cert_result:
            report["certification_status"] = {
                "certified": latest_cert_result.is_certified(),
                "accuracy": latest_cert_result.accuracy,
                "meets_threshold": latest_cert_result.accuracy >= self.config.accuracy_threshold,
                "certification_date": latest_cert_result.timestamp.isoformat(),
                "overall_score": latest_cert_result.get_overall_score()
            }
        
        # Generate recommendations
        recommendations = self._generate_recommendations(self.results_history)
        report["recommendations"] = recommendations
        
        return report
    
    def _generate_recommendations(self, results: List[ValidationResult]) -> List[str]:
        """Generate improvement recommendations based on results."""
        recommendations = []
        
        if not results:
            return ["No validation results available for analysis"]
        
        # Analyze accuracy
        avg_accuracy = statistics.mean([r.accuracy for r in results])
        if avg_accuracy < self.config.accuracy_threshold:
            recommendations.append(
                f"Accuracy ({avg_accuracy:.1%}) below threshold ({self.config.accuracy_threshold:.1%}). "
                "Consider algorithm improvements or additional training data."
            )
        
        # Analyze consistency
        avg_consistency = statistics.mean([r.consistency_score for r in results])
        if avg_consistency < self.config.consistency_threshold:
            recommendations.append(
                f"Consistency ({avg_consistency:.1%}) below threshold ({self.config.consistency_threshold:.1%}). "
                "Consider implementing deterministic algorithms or fixing randomness issues."
            )
        
        # Analyze performance
        avg_performance = statistics.mean([r.performance_time for r in results])
        if avg_performance > self.config.performance_threshold:
            recommendations.append(
                f"Average performance time ({avg_performance:.2f}s) exceeds threshold ({self.config.performance_threshold:.2f}s). "
                "Consider optimization or caching strategies."
            )
        
        # Analyze error patterns
        all_errors = []
        for result in results:
            all_errors.extend(result.errors)
        
        if all_errors:
            common_errors = {}
            for error in all_errors:
                error_type = error.split(':')[0] if ':' in error else error
                common_errors[error_type] = common_errors.get(error_type, 0) + 1
            
            most_common = max(common_errors.items(), key=lambda x: x[1])
            recommendations.append(
                f"Most common error: '{most_common[0]}' ({most_common[1]} occurrences). "
                "Focus debugging efforts on this issue."
            )
        
        if not recommendations:
            recommendations.append("All validation metrics meet or exceed thresholds. System is performing well.")
        
        return recommendations
    
    {#if AUTOMATED_REPORTING}
    def generate_visual_report(self, output_path: str = "validation_report.png"):
        """Generate visual report with charts and graphs."""
        if not self.results_history:
            logger.warning("No results available for visual report")
            return
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(f"{self.config.methodology_name} Validation Report", fontsize=16)
        
        # Accuracy over time
        timestamps = [r.timestamp for r in self.results_history]
        accuracies = [r.accuracy for r in self.results_history]
        
        axes[0, 0].plot(timestamps, accuracies, marker='o')
        axes[0, 0].axhline(y=self.config.accuracy_threshold, color='r', linestyle='--', label='Threshold')
        axes[0, 0].set_title('Accuracy Over Time')
        axes[0, 0].set_ylabel('Accuracy')
        axes[0, 0].legend()
        axes[0, 0].grid(True)
        
        # Consistency scores
        consistency_scores = [r.consistency_score for r in self.results_history]
        axes[0, 1].plot(timestamps, consistency_scores, marker='s', color='green')
        axes[0, 1].axhline(y=self.config.consistency_threshold, color='r', linestyle='--', label='Threshold')
        axes[0, 1].set_title('Consistency Over Time')
        axes[0, 1].set_ylabel('Consistency Score')
        axes[0, 1].legend()
        axes[0, 1].grid(True)
        
        # Performance time distribution
        performance_times = [r.performance_time for r in self.results_history]
        axes[1, 0].hist(performance_times, bins=10, alpha=0.7, color='orange')
        axes[1, 0].axvline(x=self.config.performance_threshold, color='r', linestyle='--', label='Threshold')
        axes[1, 0].set_title('Performance Time Distribution')
        axes[1, 0].set_xlabel('Time (seconds)')
        axes[1, 0].set_ylabel('Frequency')
        axes[1, 0].legend()
        
        # Overall scores by mode
        mode_scores = {}
        for result in self.results_history:
            mode = result.mode.value
            if mode not in mode_scores:
                mode_scores[mode] = []
            mode_scores[mode].append(result.get_overall_score())
        
        modes = list(mode_scores.keys())
        avg_scores = [statistics.mean(mode_scores[mode]) for mode in modes]
        
        bars = axes[1, 1].bar(modes, avg_scores, color='skyblue')
        axes[1, 1].set_title('Average Overall Score by Mode')
        axes[1, 1].set_ylabel('Overall Score')
        axes[1, 1].set_ylim(0, 1)
        
        # Add value labels on bars
        for bar, score in zip(bars, avg_scores):
            axes[1, 1].text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                           f'{score:.2f}', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Visual report saved to {output_path}")
    {/if}
    
    def export_results(self, output_path: str = "validation_results.json"):
        """Export validation results to JSON file."""
        export_data = {
            "methodology": self.config.methodology_name,
            "session_id": self.current_session_id,
            "exported_at": datetime.now().isoformat(),
            "configuration": {
                "accuracy_threshold": self.config.accuracy_threshold,
                "consistency_threshold": self.config.consistency_threshold,
                "reliability_threshold": self.config.reliability_threshold,
                "performance_threshold": self.config.performance_threshold
            },
            "results": []
        }
        
        for result in self.results_history:
            export_data["results"].append({
                "test_id": result.test_id,
                "test_name": result.test_name,
                "mode": result.mode.value,
                "status": result.status.name,
                "accuracy": result.accuracy,
                "consistency_score": result.consistency_score,
                "reliability_score": result.reliability_score,
                "performance_time": result.performance_time,
                "overall_score": result.get_overall_score(),
                "certified": result.is_certified(),
                "timestamp": result.timestamp.isoformat(),
                "duration": result.duration,
                "errors": result.errors,
                "warnings": result.warnings
            })
        
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        logger.info(f"Results exported to {output_path}")
    
    def get_certification_status(self) -> Dict[str, Any]:
        """Get current certification status."""
        cert_results = [r for r in self.results_history if r.mode == ValidationMode.CERTIFICATION]
        
        if not cert_results:
            return {
                "certified": False,
                "reason": "No certification validation performed"
            }
        
        latest_cert = max(cert_results, key=lambda x: x.timestamp)
        
        return {
            "certified": latest_cert.is_certified(),
            "accuracy": latest_cert.accuracy,
            "consistency": latest_cert.consistency_score,
            "reliability": latest_cert.reliability_score,
            "overall_score": latest_cert.get_overall_score(),
            "certification_date": latest_cert.timestamp.isoformat(),
            "meets_accuracy_threshold": latest_cert.accuracy >= self.config.accuracy_threshold,
            "meets_consistency_threshold": latest_cert.consistency_score >= self.config.consistency_threshold,
            "meets_reliability_threshold": latest_cert.reliability_score >= self.config.reliability_threshold
        }

{#if DOMAIN_FOCUS == "MUSIC"}
class MusicAnalysisValidator(BaseValidator):
    """Specialized validator for music analysis systems."""
    
    def run_test(self, test_case: TestCase, system_under_test: Any) -> Dict[str, Any]:
        """Run music analysis test case."""
        try:
            start_time = time.time()
            
            # Run the analysis
            result = system_under_test.analyze(test_case.input_data)
            
            processing_time = time.time() - start_time
            
            # Evaluate result accuracy
            accuracy = self._evaluate_music_result(result, test_case.expected_output, test_case.tolerance)
            
            return {
                'success': True,
                'accuracy': accuracy,
                'processing_time': processing_time,
                'result': result,
                'test_case_id': test_case.test_id
            }
            
        except Exception as e:
            return {
                'success': False,
                'accuracy': 0.0,
                'processing_time': 0.0,
                'error': str(e),
                'test_case_id': test_case.test_id
            }
    
    def _evaluate_music_result(self, result: Dict, expected: Dict, tolerance: float) -> float:
        """Evaluate music analysis result accuracy."""
        if not result or not expected:
            return 0.0
        
        accuracy_scores = []
        
        # Check BPM accuracy
        if 'bpm' in result and 'bpm' in expected:
            bpm_diff = abs(result['bpm'] - expected['bpm'])
            bpm_accuracy = max(0, 1 - (bpm_diff / expected['bpm']))
            accuracy_scores.append(bmp_accuracy)
        
        # Check key accuracy
        if 'key' in result and 'key' in expected:
            key_accuracy = 1.0 if result['key'] == expected['key'] else 0.0
            accuracy_scores.append(key_accuracy)
        
        # Check energy level
        if 'energy' in result and 'energy' in expected:
            energy_diff = abs(result['energy'] - expected['energy'])
            energy_accuracy = max(0, 1 - energy_diff)
            accuracy_scores.append(energy_accuracy)
        
        return statistics.mean(accuracy_scores) if accuracy_scores else 0.0
{/if}

{#if DOMAIN_FOCUS == "SPEECH"}
class SpeechAnalysisValidator(BaseValidator):
    """Specialized validator for speech analysis systems."""
    
    def run_test(self, test_case: TestCase, system_under_test: Any) -> Dict[str, Any]:
        """Run speech analysis test case."""
        try:
            start_time = time.time()
            
            # Run speech analysis
            result = system_under_test.analyze_speech(test_case.input_data)
            
            processing_time = time.time() - start_time
            
            # Evaluate result
            accuracy = self._evaluate_speech_result(result, test_case.expected_output)
            
            return {
                'success': True,
                'accuracy': accuracy,
                'processing_time': processing_time,
                'result': result,
                'test_case_id': test_case.test_id
            }
            
        except Exception as e:
            return {
                'success': False,
                'accuracy': 0.0,
                'processing_time': 0.0,
                'error': str(e),
                'test_case_id': test_case.test_id
            }
    
    def _evaluate_speech_result(self, result: Dict, expected: Dict) -> float:
        """Evaluate speech analysis result accuracy."""
        # Implementation for speech-specific validation
        return 0.8  # Placeholder
{/if}

# Example usage and test implementation
def create_sample_test_suite() -> List[TestCase]:
    """Create sample test suite for demonstration."""
    test_cases = []
    
    {#if DOMAIN_FOCUS == "MUSIC"}
    # Music analysis test cases
    test_cases.extend([
        TestCase(
            test_id="music_001",
            name="BPM Detection Test",
            description="Test BPM detection accuracy",
            input_data={"audio_file": "test_120bpm.wav"},
            expected_output={"bpm": 120.0, "key": "C", "energy": 0.7},
            tolerance=0.05,
            category="rhythm"
        ),
        TestCase(
            test_id="music_002", 
            name="Key Detection Test",
            description="Test musical key detection",
            input_data={"audio_file": "test_c_major.wav"},
            expected_output={"bpm": 128.0, "key": "C", "energy": 0.6},
            tolerance=0.1,
            category="harmony"
        )
    ])
    {/if}
    
    return test_cases

def main():
    """Example usage of BMAD validation framework."""
    
    # Create configuration
    config = ValidationConfig(
        methodology_name="{METHODOLOGY_NAME}",
        accuracy_threshold={ACCURACY_THRESHOLD},
        consistency_threshold={CONSISTENCY_THRESHOLD}
    )
    
    {#if DOMAIN_FOCUS == "MUSIC"}
    # Initialize validator
    validator = MusicAnalysisValidator(config)
    {/if}
    {#if DOMAIN_FOCUS == "SPEECH"}
    validator = SpeechAnalysisValidator(config)
    {/if}
    {#if DOMAIN_FOCUS not in ["MUSIC", "SPEECH"]}
    # Generic validator would need custom implementation
    class CustomValidator(BaseValidator):
        def run_test(self, test_case, system_under_test):
            # Custom test implementation
            return {'success': True, 'accuracy': 0.8, 'processing_time': 0.1}
    
    validator = CustomValidator(config)
    {/if}
    
    # Add test cases
    test_cases = create_sample_test_suite()
    validator.add_test_cases(test_cases)
    
    # Mock system under test
    class MockSystem:
        def analyze(self, input_data):
            # Mock analysis results
            return {"bpm": 119.5, "key": "C", "energy": 0.68}
    
    system = MockSystem()
    
    # Run different validation modes
    {#if CERTIFICATION_MODE}
    print("Running certification mode...")
    cert_result = validator.run_certification_mode(system)
    print(f"Certification result: {cert_result.status.name} (Accuracy: {cert_result.accuracy:.1%})")
    {/if}
    
    {#if OPTIMIZATION_MODE}
    print("Running optimization mode...")
    opt_result = validator.run_optimization_mode(system)
    print(f"Optimization completed: {opt_result.get_overall_score():.1%} overall score")
    {/if}
    
    # Generate comprehensive report
    report = validator.generate_comprehensive_report()
    print("\nValidation Report Summary:")
    print(f"Total validations: {report['summary']['total_validations']}")
    print(f"Pass rate: {report['summary']['pass_rate']:.1%}")
    print(f"Certification rate: {report['summary']['certification_rate']:.1%}")
    
    # Export results
    validator.export_results("bmad_results.json")
    
    {#if AUTOMATED_REPORTING}
    # Generate visual report
    validator.generate_visual_report("bmad_report.png")
    {/if}
    
    # Check certification status
    cert_status = validator.get_certification_status()
    print(f"\nCertification Status: {'CERTIFIED' if cert_status['certified'] else 'NOT CERTIFIED'}")

if __name__ == "__main__":
    main()
```

## Configuration Template

```yaml
# {METHODOLOGY_NAME} Framework Configuration

methodology:
  name: "{METHODOLOGY_NAME}"
  domain: "{DOMAIN_FOCUS}"
  validation_depth: "{VALIDATION_DEPTH}"

thresholds:
  accuracy: {ACCURACY_THRESHOLD}
  consistency: {CONSISTENCY_THRESHOLD}
  reliability: {RELIABILITY_THRESHOLD}
  performance: {PERFORMANCE_THRESHOLD}

validation_modes:
  {#if CERTIFICATION_MODE}
  certification:
    enabled: true
    min_accuracy: {ACCURACY_THRESHOLD}
    test_iterations: 100
  {/if}
  
  {#if OPTIMIZATION_MODE}
  optimization:
    enabled: true
    max_iterations: 10
    target_metric: "accuracy"
    early_stopping: true
  {/if}
  
  {#if VALIDATION_MODE}
  validation:
    enabled: true
    consistency_runs: 5
    data_integrity_checks: true
  {/fi}
  
  {#if BASELINE_MODE}
  baseline:
    enabled: true
    performance_tracking: true
  {/if}

testing:
  {#if UNIT_TESTING}
  unit_tests: true
  {/if}
  {#if INTEGRATION_TESTING}
  integration_tests: true
  {/if}
  {#if PERFORMANCE_TESTING}
  performance_tests: true
  {/if}
  {#if REGRESSION_TESTING}
  regression_tests: true
  {/if}

reporting:
  {#if AUTOMATED_REPORTING}
  automated: true
  visual_reports: true
  {/if}
  {#if DASHBOARD_METRICS}
  dashboard: true
  {/if}
  export_format: "json"
  include_raw_data: true

{#if PROFESSIONAL_CERT}
certification:
  professional_standards: true
  audit_trail: {AUDIT_TRAIL}
  compliance_validation: {COMPLIANCE_VALIDATION}
{/if}
```

## Usage Examples

### Basic Validation
```python
# Initialize framework
config = ValidationConfig(accuracy_threshold=0.8)
validator = MusicAnalysisValidator(config)

# Add test cases
validator.add_test_cases(test_cases)

# Run certification
result = validator.run_certification_mode(system)
print(f"Certified: {result.is_certified()}")
```

### Multi-Mode Validation
```python
# Run comprehensive validation
cert_result = validator.run_certification_mode(system)
opt_result = validator.run_optimization_mode(system)
base_result = validator.run_baseline_mode(system)

# Generate report
report = validator.generate_comprehensive_report()
```

### Benchmarking
```python
# Compare systems
systems = {"system_a": system_a, "system_b": system_b}
benchmark_results = validator.run_benchmarking_mode(systems)

for name, result in benchmark_results.items():
    print(f"{name}: {result.accuracy:.1%}")
```

## Validation Criteria

A successful implementation should demonstrate:

1. **Comprehensive Testing**: Multiple validation modes with thorough coverage
2. **Professional Standards**: {ACCURACY_THRESHOLD*100}%+ accuracy certification requirement
3. **Consistency**: Reproducible results across multiple runs
4. **Performance**: Meets response time and throughput requirements
5. **Audit Trail**: Complete documentation of all validation activities
6. **Continuous Improvement**: Optimization mode for iterative enhancement

---

*Generated by BMAD Methodology Framework Generator Meta-Prompt*
*Version 1.0 - Based on MAP4 BMAD Validation System*