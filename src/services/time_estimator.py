"""Time estimation utilities for audio analysis progress tracking."""

import time
from typing import Dict, List, Optional
from statistics import mean, median
from ..models.progress import AnalysisStage


class TimeEstimator:
    """Estimates remaining time for audio analysis based on historical data."""
    
    def __init__(self):
        self._stage_durations: Dict[AnalysisStage, List[float]] = {
            stage: [] for stage in AnalysisStage
        }
        self._file_start_time: Optional[float] = None
        self._stage_start_time: Optional[float] = None
        self._current_stage: Optional[AnalysisStage] = None
        
    def start_file_analysis(self):
        """Mark the start of analysis for a new file."""
        self._file_start_time = time.time()
        self._stage_start_time = None
        self._current_stage = None
    
    def start_stage(self, stage: AnalysisStage):
        """Mark the start of a specific analysis stage."""
        if self._current_stage is not None and self._stage_start_time is not None:
            # Record duration of previous stage
            duration = time.time() - self._stage_start_time
            self._stage_durations[self._current_stage].append(duration)
        
        self._current_stage = stage
        self._stage_start_time = time.time()
    
    def complete_file_analysis(self):
        """Mark the completion of file analysis and record final stage."""
        if self._current_stage is not None and self._stage_start_time is not None:
            duration = time.time() - self._stage_start_time
            self._stage_durations[self._current_stage].append(duration)
        
        self._file_start_time = None
        self._stage_start_time = None
        self._current_stage = None
    
    def get_stage_estimate(self, stage: AnalysisStage) -> float:
        """Get estimated duration for a stage based on historical data."""
        durations = self._stage_durations[stage]
        
        if not durations:
            # Default estimates based on typical analysis times (seconds)
            defaults = {
                AnalysisStage.AUDIO_LOADING: 0.5,
                AnalysisStage.BPM_DETECTION: 2.0,
                AnalysisStage.KEY_DETECTION: 2.0,
                AnalysisStage.ENERGY_CALCULATION: 0.8,
                AnalysisStage.HAMMS_COMPUTATION: 0.7,
            }
            return defaults[stage]
        
        # Use median to avoid outliers affecting estimates
        return median(durations)
    
    def get_remaining_time_estimate(
        self, 
        current_stage: AnalysisStage, 
        stage_progress: float,
        remaining_files: int = 0
    ) -> Optional[float]:
        """
        Estimate remaining time for current file and remaining files.
        
        Args:
            current_stage: Current analysis stage
            stage_progress: Progress within current stage (0.0-1.0)
            remaining_files: Number of files remaining after current file
            
        Returns:
            Estimated remaining seconds, or None if insufficient data
        """
        if self._stage_start_time is None:
            return None
        
        # Estimate remaining time for current stage
        stage_elapsed = time.time() - self._stage_start_time
        stage_estimate = self.get_stage_estimate(current_stage)
        
        if stage_progress > 0:
            # Adjust estimate based on actual progress
            total_stage_estimate = stage_elapsed / stage_progress
            remaining_stage_time = max(0, total_stage_estimate - stage_elapsed)
        else:
            remaining_stage_time = stage_estimate - stage_elapsed
        
        # Add estimates for remaining stages in current file
        stages = list(AnalysisStage)
        current_index = stages.index(current_stage)
        remaining_stages_time = sum(
            self.get_stage_estimate(stage) 
            for stage in stages[current_index + 1:]
        )
        
        current_file_remaining = remaining_stage_time + remaining_stages_time
        
        # Add estimates for remaining files
        if remaining_files > 0:
            avg_file_duration = self.get_average_file_duration()
            remaining_files_time = remaining_files * avg_file_duration
        else:
            remaining_files_time = 0
        
        return current_file_remaining + remaining_files_time
    
    def get_average_file_duration(self) -> float:
        """Get average duration for analyzing a complete file."""
        total_durations = []
        
        for stage in AnalysisStage:
            stage_durations = self._stage_durations[stage]
            if stage_durations:
                total_durations.extend(stage_durations)
        
        if total_durations:
            # Estimate total file duration as sum of stage medians
            return sum(self.get_stage_estimate(stage) for stage in AnalysisStage)
        
        # Default estimate for complete file analysis (seconds)
        return 6.0
    
    def get_elapsed_time(self) -> float:
        """Get elapsed time since file analysis started."""
        if self._file_start_time is None:
            return 0.0
        return time.time() - self._file_start_time
    
    def clear_history(self):
        """Clear historical timing data."""
        for stage in AnalysisStage:
            self._stage_durations[stage].clear()
    
    def get_statistics(self) -> Dict[str, any]:
        """Get timing statistics for debugging and optimization."""
        stats = {}
        
        for stage in AnalysisStage:
            durations = self._stage_durations[stage]
            if durations:
                stats[stage.value] = {
                    'count': len(durations),
                    'mean': mean(durations),
                    'median': median(durations),
                    'min': min(durations),
                    'max': max(durations)
                }
            else:
                stats[stage.value] = {'count': 0}
        
        stats['total_files_analyzed'] = min(
            len(durations) for durations in self._stage_durations.values()
        )
        stats['average_file_duration'] = self.get_average_file_duration()
        
        return stats