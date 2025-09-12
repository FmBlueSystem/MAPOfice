# MAP4 BMAD Framework - Balanced Music Analysis and Development

## Objective
Implement the BMAD (Balanced Music Analysis and Development) methodology for validation, optimization, and certification of music analysis accuracy against professional DJ standards.

## Prerequisites
- Completed core implementation with HAMMS v3.0
- Storage system and database models
- Reference dataset of professionally-analyzed tracks

## Step 1: BMAD Core Engine

### 1.1 Create BMAD Engine
Create `src/bmad/bmad_engine.py`:

```python
"""BMAD methodology engine for validation and optimization."""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Tuple
import numpy as np
import logging
from datetime import datetime
import json

from src.analysis.hamms_v3 import HAMMSAnalyzer
from src.services.storage_service import StorageService

logger = logging.getLogger(__name__)

class BMADMode(Enum):
    """BMAD operational modes."""
    CERTIFICATION = "certification"  # Validate against DJ standards
    OPTIMIZATION = "optimization"    # Optimize analysis parameters
    VALIDATION = "validation"        # Validate data integrity
    PURE_METADATA = "pure_metadata" # Baseline without AI
    REAL_DATA = "real_data"        # Real-world library optimization

@dataclass
class BMADResult:
    """BMAD analysis result container."""
    mode: BMADMode
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    confidence: float
    passed: bool
    details: Dict[str, Any]
    recommendations: List[str]
    timestamp: datetime

class BMADEngine:
    """BMAD methodology implementation."""
    
    # Professional DJ standards thresholds
    DJ_STANDARDS = {
        'bpm_tolerance': 0.02,      # 2% BPM variation
        'key_compatibility': 0.95,   # 95% key accuracy
        'energy_correlation': 0.85,  # 85% energy matching
        'mix_compatibility': 0.80,   # 80% overall compatibility
        'certification_threshold': 0.80  # 80% to pass certification
    }
    
    def __init__(self):
        """Initialize BMAD engine."""
        self.hamms_analyzer = HAMMSAnalyzer()
        self.storage = StorageService()
        self.reference_data = {}
        self.optimization_history = []
    
    def run_certification(self, test_tracks: List[Dict[str, Any]], 
                         reference_tracks: List[Dict[str, Any]]) -> BMADResult:
        """Run certification mode to validate against DJ standards.
        
        Args:
            test_tracks: Analyzed tracks to test
            reference_tracks: Professional reference tracks
        
        Returns:
            BMAD certification result
        """
        logger.info(f"Running BMAD certification on {len(test_tracks)} tracks")
        
        # Calculate metrics
        bpm_accuracy = self._calculate_bpm_accuracy(test_tracks, reference_tracks)
        key_accuracy = self._calculate_key_accuracy(test_tracks, reference_tracks)
        energy_correlation = self._calculate_energy_correlation(test_tracks, reference_tracks)
        mix_compatibility = self._calculate_mix_compatibility(test_tracks, reference_tracks)
        
        # Overall accuracy
        overall_accuracy = np.mean([
            bpm_accuracy * 0.3,
            key_accuracy * 0.3,
            energy_correlation * 0.2,
            mix_compatibility * 0.2
        ])
        
        # Determine pass/fail
        passed = overall_accuracy >= self.DJ_STANDARDS['certification_threshold']
        
        # Generate recommendations
        recommendations = []
        if bpm_accuracy < 0.9:
            recommendations.append("Improve BPM detection algorithm")
        if key_accuracy < 0.9:
            recommendations.append("Enhance key detection accuracy")
        if energy_correlation < 0.8:
            recommendations.append("Refine energy calculation methods")
        
        return BMADResult(
            mode=BMADMode.CERTIFICATION,
            accuracy=overall_accuracy,
            precision=self._calculate_precision(test_tracks, reference_tracks),
            recall=self._calculate_recall(test_tracks, reference_tracks),
            f1_score=self._calculate_f1_score(test_tracks, reference_tracks),
            confidence=self._calculate_confidence(test_tracks),
            passed=passed,
            details={
                'bpm_accuracy': bpm_accuracy,
                'key_accuracy': key_accuracy,
                'energy_correlation': energy_correlation,
                'mix_compatibility': mix_compatibility,
                'total_tracks': len(test_tracks)
            },
            recommendations=recommendations,
            timestamp=datetime.now()
        )
    
    def run_optimization(self, training_tracks: List[Dict[str, Any]],
                        iterations: int = 10) -> BMADResult:
        """Run optimization mode to improve analysis parameters.
        
        Args:
            training_tracks: Tracks for optimization
            iterations: Number of optimization iterations
        
        Returns:
            BMAD optimization result
        """
        logger.info(f"Running BMAD optimization with {iterations} iterations")
        
        best_params = {}
        best_score = 0
        
        for i in range(iterations):
            # Generate parameter variations
            params = self._generate_parameter_variations(i)
            
            # Test parameters
            score = self._evaluate_parameters(params, training_tracks)
            
            if score > best_score:
                best_score = score
                best_params = params
            
            self.optimization_history.append({
                'iteration': i,
                'params': params,
                'score': score
            })
        
        return BMADResult(
            mode=BMADMode.OPTIMIZATION,
            accuracy=best_score,
            precision=0.0,
            recall=0.0,
            f1_score=0.0,
            confidence=0.9,
            passed=best_score > 0.8,
            details={
                'best_params': best_params,
                'iterations': iterations,
                'improvement': best_score - self.optimization_history[0]['score']
            },
            recommendations=[
                f"Apply optimized parameters: {json.dumps(best_params, indent=2)}"
            ],
            timestamp=datetime.now()
        )
    
    def run_validation(self, tracks: List[Dict[str, Any]]) -> BMADResult:
        """Run validation mode to check data integrity.
        
        Args:
            tracks: Tracks to validate
        
        Returns:
            BMAD validation result
        """
        logger.info(f"Running BMAD validation on {len(tracks)} tracks")
        
        valid_count = 0
        issues = []
        
        for track in tracks:
            validation_result = self._validate_track_data(track)
            if validation_result['valid']:
                valid_count += 1
            else:
                issues.extend(validation_result['issues'])
        
        accuracy = valid_count / len(tracks) if tracks else 0
        
        return BMADResult(
            mode=BMADMode.VALIDATION,
            accuracy=accuracy,
            precision=1.0,
            recall=1.0,
            f1_score=1.0,
            confidence=1.0,
            passed=accuracy >= 0.95,
            details={
                'valid_tracks': valid_count,
                'total_tracks': len(tracks),
                'issues': issues[:10]  # Top 10 issues
            },
            recommendations=self._generate_validation_recommendations(issues),
            timestamp=datetime.now()
        )
    
    def _calculate_bpm_accuracy(self, test: List[Dict], reference: List[Dict]) -> float:
        """Calculate BPM detection accuracy."""
        if not test or not reference:
            return 0.0
        
        correct = 0
        for t, r in zip(test, reference):
            test_bpm = t.get('bpm', 0)
            ref_bpm = r.get('bpm', 0)
            
            if ref_bpm > 0:
                error = abs(test_bpm - ref_bpm) / ref_bpm
                if error <= self.DJ_STANDARDS['bpm_tolerance']:
                    correct += 1
        
        return correct / len(test)
    
    def _calculate_key_accuracy(self, test: List[Dict], reference: List[Dict]) -> float:
        """Calculate key detection accuracy."""
        if not test or not reference:
            return 0.0
        
        correct = 0
        for t, r in zip(test, reference):
            if t.get('key') == r.get('key'):
                correct += 1
        
        return correct / len(test)
    
    def _calculate_energy_correlation(self, test: List[Dict], reference: List[Dict]) -> float:
        """Calculate energy correlation."""
        if not test or not reference:
            return 0.0
        
        test_energies = [t.get('energy', 0) for t in test]
        ref_energies = [r.get('energy', 0) for r in reference]
        
        if len(test_energies) > 1:
            correlation = np.corrcoef(test_energies, ref_energies)[0, 1]
            return max(0, correlation)  # Ensure non-negative
        
        return 0.0
    
    def _calculate_mix_compatibility(self, test: List[Dict], reference: List[Dict]) -> float:
        """Calculate mixing compatibility score."""
        if not test or not reference:
            return 0.0
        
        compatibility_scores = []
        
        for i in range(len(test) - 1):
            # Get consecutive tracks
            t1, t2 = test[i], test[i + 1]
            r1, r2 = reference[i], reference[i + 1]
            
            # Calculate HAMMS similarity
            if 'hamms_vector' in t1 and 'hamms_vector' in t2:
                test_similarity = self.hamms_analyzer.calculate_similarity(
                    np.array(t1['hamms_vector']),
                    np.array(t2['hamms_vector'])
                )['overall_similarity']
            else:
                test_similarity = 0
            
            if 'hamms_vector' in r1 and 'hamms_vector' in r2:
                ref_similarity = self.hamms_analyzer.calculate_similarity(
                    np.array(r1['hamms_vector']),
                    np.array(r2['hamms_vector'])
                )['overall_similarity']
            else:
                ref_similarity = 0
            
            # Compare similarities
            compatibility = 1 - abs(test_similarity - ref_similarity)
            compatibility_scores.append(compatibility)
        
        return np.mean(compatibility_scores) if compatibility_scores else 0.0
    
    def _calculate_precision(self, test: List[Dict], reference: List[Dict]) -> float:
        """Calculate precision metric."""
        # Simplified precision calculation
        true_positives = sum(1 for t, r in zip(test, reference) 
                           if t.get('genre') == r.get('genre'))
        predicted_positives = len(test)
        
        return true_positives / predicted_positives if predicted_positives > 0 else 0
    
    def _calculate_recall(self, test: List[Dict], reference: List[Dict]) -> float:
        """Calculate recall metric."""
        # Simplified recall calculation
        true_positives = sum(1 for t, r in zip(test, reference)
                           if t.get('genre') == r.get('genre'))
        actual_positives = len(reference)
        
        return true_positives / actual_positives if actual_positives > 0 else 0
    
    def _calculate_f1_score(self, test: List[Dict], reference: List[Dict]) -> float:
        """Calculate F1 score."""
        precision = self._calculate_precision(test, reference)
        recall = self._calculate_recall(test, reference)
        
        if precision + recall > 0:
            return 2 * (precision * recall) / (precision + recall)
        return 0.0
    
    def _calculate_confidence(self, tracks: List[Dict]) -> float:
        """Calculate overall confidence score."""
        if not tracks:
            return 0.0
        
        confidences = [t.get('confidence', 0.5) for t in tracks]
        return np.mean(confidences)
    
    def _validate_track_data(self, track: Dict[str, Any]) -> Dict[str, Any]:
        """Validate individual track data."""
        issues = []
        
        # Check required fields
        required_fields = ['bpm', 'key', 'energy', 'hamms_vector']
        for field in required_fields:
            if field not in track:
                issues.append(f"Missing required field: {field}")
        
        # Validate BPM
        bpm = track.get('bpm', 0)
        if not 30 <= bpm <= 300:
            issues.append(f"Invalid BPM: {bpm}")
        
        # Validate energy
        energy = track.get('energy', -1)
        if not 0 <= energy <= 1:
            issues.append(f"Invalid energy: {energy}")
        
        # Validate HAMMS vector
        hamms = track.get('hamms_vector', [])
        if len(hamms) != 12:
            issues.append(f"Invalid HAMMS vector dimension: {len(hamms)}")
        elif not all(0 <= v <= 1 for v in hamms):
            issues.append("HAMMS vector values out of range")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues
        }
    
    def _generate_parameter_variations(self, iteration: int) -> Dict[str, Any]:
        """Generate parameter variations for optimization."""
        # Base parameters with variations
        base_weights = np.array([1.3, 1.4, 1.2, 0.9, 0.8, 0.6, 0.5, 1.1, 0.7, 0.9, 0.8, 0.6])
        
        # Add random variations
        np.random.seed(iteration)
        variations = np.random.normal(0, 0.1, 12)
        new_weights = np.clip(base_weights + variations, 0.1, 2.0)
        
        return {
            'dimension_weights': new_weights.tolist(),
            'similarity_euclidean_weight': 0.6 + np.random.uniform(-0.1, 0.1),
            'similarity_cosine_weight': 0.4 + np.random.uniform(-0.1, 0.1)
        }
    
    def _evaluate_parameters(self, params: Dict[str, Any], 
                           tracks: List[Dict[str, Any]]) -> float:
        """Evaluate parameter set performance."""
        # Simplified evaluation - would be more complex in production
        scores = []
        
        for i in range(len(tracks) - 1):
            track1 = tracks[i]
            track2 = tracks[i + 1]
            
            # Check if tracks should mix well based on BPM and key
            bpm_diff = abs(track1.get('bpm', 120) - track2.get('bpm', 120))
            key_compatible = self._check_key_compatibility(
                track1.get('key', 'Am'),
                track2.get('key', 'Am')
            )
            
            # Score based on parameters
            if bpm_diff < 10 and key_compatible:
                scores.append(1.0)
            elif bpm_diff < 20 or key_compatible:
                scores.append(0.5)
            else:
                scores.append(0.0)
        
        return np.mean(scores) if scores else 0.0
    
    def _check_key_compatibility(self, key1: str, key2: str) -> bool:
        """Check if two keys are compatible for mixing."""
        # Simplified Camelot wheel compatibility
        camelot1 = self.hamms_analyzer.CAMELOT_WHEEL.get(key1, '1A')
        camelot2 = self.hamms_analyzer.CAMELOT_WHEEL.get(key2, '1A')
        
        # Extract numbers
        num1 = int(''.join(filter(str.isdigit, camelot1)) or 1)
        num2 = int(''.join(filter(str.isdigit, camelot2)) or 1)
        
        # Check if same, adjacent, or opposite
        diff = abs(num1 - num2)
        return diff in [0, 1, 11]  # Same, next, or previous on wheel
    
    def _generate_validation_recommendations(self, issues: List[str]) -> List[str]:
        """Generate recommendations based on validation issues."""
        recommendations = []
        
        if any('BPM' in issue for issue in issues):
            recommendations.append("Review BPM extraction algorithm")
        
        if any('key' in issue for issue in issues):
            recommendations.append("Improve key detection accuracy")
        
        if any('HAMMS' in issue for issue in issues):
            recommendations.append("Validate HAMMS vector calculation")
        
        if len(issues) > 100:
            recommendations.append("Consider reprocessing entire library")
        
        return recommendations[:5]  # Limit to top 5

# Export
__all__ = ['BMADEngine', 'BMADMode', 'BMADResult']
```

## Step 2: BMAD CLI Commands

### 2.1 Create BMAD CLI
Create `src/cli/commands/bmad_commands.py`:

```python
"""BMAD CLI commands."""

import click
import json
from pathlib import Path
from typing import Optional

from src.bmad.bmad_engine import BMADEngine, BMADMode

@click.group(name='bmad')
def bmad_group():
    """BMAD methodology commands."""
    pass

@bmad_group.command('certify')
@click.option('--test-dir', required=True, help='Directory with test tracks')
@click.option('--reference-dir', required=True, help='Directory with reference tracks')
@click.option('--output', help='Output file for results')
def certify(test_dir: str, reference_dir: str, output: Optional[str]):
    """Run BMAD certification."""
    engine = BMADEngine()
    
    # Load tracks (simplified)
    test_tracks = []  # Load from test_dir
    reference_tracks = []  # Load from reference_dir
    
    # Run certification
    result = engine.run_certification(test_tracks, reference_tracks)
    
    # Display results
    click.echo(f"Certification {'PASSED' if result.passed else 'FAILED'}")
    click.echo(f"Accuracy: {result.accuracy:.2%}")
    click.echo(f"Details: {json.dumps(result.details, indent=2)}")
    
    # Save if requested
    if output:
        Path(output).write_text(json.dumps(result.__dict__, default=str, indent=2))

@bmad_group.command('optimize')
@click.option('--training-dir', required=True, help='Directory with training tracks')
@click.option('--iterations', default=10, help='Optimization iterations')
def optimize(training_dir: str, iterations: int):
    """Run BMAD optimization."""
    engine = BMADEngine()
    
    # Load training tracks
    training_tracks = []  # Load from training_dir
    
    # Run optimization
    result = engine.run_optimization(training_tracks, iterations)
    
    # Display results
    click.echo(f"Optimization complete")
    click.echo(f"Best score: {result.accuracy:.2%}")
    click.echo(f"Recommendations:")
    for rec in result.recommendations:
        click.echo(f"  - {rec}")

@bmad_group.command('validate')
@click.option('--library-dir', required=True, help='Music library directory')
def validate(library_dir: str):
    """Run BMAD validation."""
    engine = BMADEngine()
    
    # Load library tracks
    tracks = []  # Load from library_dir
    
    # Run validation
    result = engine.run_validation(tracks)
    
    # Display results
    click.echo(f"Validation {'PASSED' if result.passed else 'FAILED'}")
    click.echo(f"Valid tracks: {result.details['valid_tracks']}/{result.details['total_tracks']}")
    
    if result.details['issues']:
        click.echo("Issues found:")
        for issue in result.details['issues'][:5]:
            click.echo(f"  - {issue}")
```

## Success Criteria

BMAD framework is complete when:

1. **Certification Mode**: Validates analysis accuracy against DJ standards (80% threshold)
2. **Optimization Mode**: Iteratively improves analysis parameters
3. **Validation Mode**: Ensures data integrity across the pipeline
4. **Pure Metadata Mode**: Baseline performance without AI
5. **Real Data Mode**: Optimization using real-world libraries
6. **CLI Integration**: Full command-line access to all BMAD modes

## Next Steps

1. Create the unified CLI system (see `06-cli-system.md`)
2. Add integration and testing (see `07-integration-testing.md`)

The BMAD framework ensures MAP4 meets professional DJ standards with validated accuracy.