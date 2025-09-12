"""
BMAD Core Engine
================

Central BMAD methodology engine that coordinates all components.
Consolidates core functionality from all BMAD tools.
"""

import json
import time
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import os
import sys

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from src.analysis.llm_provider import LLMConfig, LLMProvider, LLMProviderFactory

class BMADMode(Enum):
    """BMAD operation modes"""
    CERTIFICATION = "certification"
    OPTIMIZATION = "optimization" 
    VALIDATION = "validation"
    PURE_METADATA = "pure_metadata"
    REAL_DATA = "real_data"

@dataclass
class BMADConfig:
    """BMAD engine configuration"""
    mode: BMADMode
    llm_provider: Optional[LLMConfig] = None
    certification_threshold: float = 0.80
    max_optimization_cycles: int = 3
    batch_size: int = 10
    enable_caching: bool = True
    output_format: str = "json"
    metadata_only: bool = False
    
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

@dataclass
class TrackAnalysisResult:
    """Individual track analysis result"""
    filename: str
    success: bool
    analysis_data: Dict[str, Any]
    confidence: float
    processing_time: float
    error_message: Optional[str] = None

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
        
        # Initialize LLM provider if provided
        if config.llm_provider:
            self.llm_provider = LLMProviderFactory.create_provider(config.llm_provider)
    
    def execute(self, data: Union[List[Dict], Dict]) -> BMADResult:
        """
        Execute BMAD methodology based on configuration
        
        Args:
            data: Track data (single track or list of tracks)
            
        Returns:
            BMADResult with analysis results
        """
        start_time = time.time()
        
        try:
            # Normalize input data
            tracks = self._normalize_input_data(data)
            
            # Execute based on mode
            if self.config.mode == BMADMode.CERTIFICATION:
                result = self._execute_certification(tracks)
            elif self.config.mode == BMADMode.OPTIMIZATION:
                result = self._execute_optimization(tracks)
            elif self.config.mode == BMADMode.VALIDATION:
                result = self._execute_validation(tracks)
            elif self.config.mode == BMADMode.PURE_METADATA:
                result = self._execute_pure_metadata(tracks)
            elif self.config.mode == BMADMode.REAL_DATA:
                result = self._execute_real_data(tracks)
            else:
                raise ValueError(f"Unsupported BMAD mode: {self.config.mode}")
            
            # Add timing
            result.processing_time = time.time() - start_time
            result.cycles_completed = self.current_cycle
            
            return result
            
        except Exception as e:
            return BMADResult(
                success=False,
                mode=self.config.mode,
                results={},
                metrics={},
                errors=[str(e)],
                processing_time=time.time() - start_time
            )
    
    def _normalize_input_data(self, data: Union[List[Dict], Dict]) -> List[Dict]:
        """Normalize input data to list of tracks"""
        if isinstance(data, dict):
            return [data]
        elif isinstance(data, list):
            return data
        else:
            raise ValueError("Input data must be dict or list of dicts")
    
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
                # Perform basic validation
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
                processing_time=0.01  # Minimal processing time for validation
            )
            
        except Exception as e:
            return TrackAnalysisResult(
                filename=track.get('filename', 'unknown'),
                success=False,
                analysis_data={},
                confidence=0.0,
                processing_time=0.0,
                error_message=str(e)
            )
    
    def _calculate_metadata_completeness(self, metadata_results: List[Dict]) -> float:
        """Calculate average metadata completeness across results"""
        if not metadata_results:
            return 0.0
            
        total_completeness = 0.0
        valid_results = 0
        
        for result in metadata_results:
            if result.get('success') and 'completeness' in result:
                total_completeness += result['completeness']
                valid_results += 1
        
        return total_completeness / valid_results if valid_results > 0 else 0.0
    
    def get_status(self) -> Dict[str, Any]:
        """Get current BMAD engine status"""
        return {
            'mode': self.config.mode.value,
            'current_cycle': self.current_cycle,
            'max_cycles': self.config.max_optimization_cycles,
            'llm_provider_available': self.llm_provider is not None,
            'caching_enabled': self.config.enable_caching,
            'cached_results': len(self.results_cache)
        }

# Factory function for easy BMAD engine creation
def create_bmad_engine(mode: Union[str, BMADMode], **kwargs) -> BMADEngine:
    """Create BMAD engine with specified mode and options"""
    
    if isinstance(mode, str):
        mode = BMADMode(mode)
    
    config = BMADConfig(mode=mode, **kwargs)
    return BMADEngine(config)