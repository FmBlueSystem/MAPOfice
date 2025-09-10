"""Progress tracking models for audio analysis."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class AnalysisStage(Enum):
    """Stages of audio analysis with their expected time allocation."""
    
    AUDIO_LOADING = "Audio Loading"
    BPM_DETECTION = "BPM Detection"
    KEY_DETECTION = "Key Detection"
    ENERGY_CALCULATION = "Energy Calculation"
    HAMMS_COMPUTATION = "HAMMS Computation"
    
    @property
    def time_allocation(self) -> float:
        """Expected percentage of total analysis time for this stage."""
        allocations = {
            AnalysisStage.AUDIO_LOADING: 0.10,      # 10%
            AnalysisStage.BPM_DETECTION: 0.30,      # 30%
            AnalysisStage.KEY_DETECTION: 0.30,      # 30%
            AnalysisStage.ENERGY_CALCULATION: 0.15, # 15%
            AnalysisStage.HAMMS_COMPUTATION: 0.15,   # 15%
        }
        return allocations[self]
    
    @property
    def progress_start(self) -> float:
        """Starting progress percentage for this stage (0.0-1.0)."""
        stage_starts = {
            AnalysisStage.AUDIO_LOADING: 0.0,      # 0-10%
            AnalysisStage.BPM_DETECTION: 0.10,     # 10-40%
            AnalysisStage.KEY_DETECTION: 0.40,     # 40-70%
            AnalysisStage.ENERGY_CALCULATION: 0.70, # 70-85%
            AnalysisStage.HAMMS_COMPUTATION: 0.85,  # 85-100%
        }
        return stage_starts[self]
    
    @property
    def progress_end(self) -> float:
        """Ending progress percentage for this stage (0.0-1.0)."""
        return self.progress_start + self.time_allocation


@dataclass
class AnalysisProgress:
    """Tracks detailed progress for audio analysis operations."""
    
    # File-level progress
    current_file_index: int = 0
    total_files: int = 1
    current_filename: str = ""
    
    # Stage-level progress
    current_stage: AnalysisStage = AnalysisStage.AUDIO_LOADING
    stage_progress: float = 0.0  # 0.0-1.0 within current stage
    
    # Time tracking
    elapsed_seconds: float = 0.0
    estimated_remaining_seconds: Optional[float] = None
    
    @property
    def file_progress(self) -> float:
        """Overall progress across all files (0.0-1.0)."""
        if self.total_files == 0:
            return 0.0
        return self.current_file_index / self.total_files
    
    @property
    def current_file_progress(self) -> float:
        """Progress for the current file being analyzed (0.0-1.0)."""
        stage_start = self.current_stage.progress_start
        stage_range = self.current_stage.time_allocation
        return stage_start + (self.stage_progress * stage_range)
    
    @property
    def overall_progress(self) -> float:
        """Overall progress including file and stage progress (0.0-1.0)."""
        if self.total_files == 0:
            return 0.0
        
        # Progress from completed files
        completed_files_progress = self.current_file_index / self.total_files
        
        # Progress from current file
        current_file_contribution = (1.0 / self.total_files) * self.current_file_progress
        
        return completed_files_progress + current_file_contribution
    
    def update_stage(self, stage: AnalysisStage, progress: float = 0.0):
        """Update the current stage and its progress."""
        self.current_stage = stage
        self.stage_progress = max(0.0, min(1.0, progress))
    
    def complete_stage(self):
        """Mark current stage as complete and advance to next."""
        stages = list(AnalysisStage)
        current_index = stages.index(self.current_stage)
        
        if current_index < len(stages) - 1:
            self.current_stage = stages[current_index + 1]
            self.stage_progress = 0.0
        else:
            self.stage_progress = 1.0
    
    def advance_file(self, filename: str = ""):
        """Advance to next file and reset stage progress."""
        self.current_file_index += 1
        self.current_filename = filename
        self.current_stage = AnalysisStage.AUDIO_LOADING
        self.stage_progress = 0.0
    
    def reset(self, total_files: int = 1):
        """Reset progress tracking for new analysis batch."""
        self.current_file_index = 0
        self.total_files = total_files
        self.current_filename = ""
        self.current_stage = AnalysisStage.AUDIO_LOADING
        self.stage_progress = 0.0
        self.elapsed_seconds = 0.0
        self.estimated_remaining_seconds = None