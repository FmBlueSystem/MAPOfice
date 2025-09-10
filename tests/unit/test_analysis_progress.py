"""Unit tests for AnalysisProgress and AnalysisStage models."""

import pytest
from src.models.progress import AnalysisProgress, AnalysisStage


class TestAnalysisStage:
    """Test AnalysisStage enum properties."""
    
    def test_stage_time_allocations_sum_to_one(self):
        """Time allocations across all stages should sum to 1.0."""
        total_allocation = sum(stage.time_allocation for stage in AnalysisStage)
        assert abs(total_allocation - 1.0) < 0.001
    
    def test_stage_progress_ranges_are_sequential(self):
        """Progress ranges should be sequential without gaps or overlaps."""
        stages = list(AnalysisStage)
        
        for i, stage in enumerate(stages):
            if i > 0:
                prev_stage = stages[i - 1]
                assert stage.progress_start == prev_stage.progress_end
    
    def test_stage_progress_start_values(self):
        """Verify expected progress start values for each stage."""
        expected_starts = {
            AnalysisStage.AUDIO_LOADING: 0.0,
            AnalysisStage.BPM_DETECTION: 0.10,
            AnalysisStage.KEY_DETECTION: 0.40,
            AnalysisStage.ENERGY_CALCULATION: 0.70,
            AnalysisStage.HAMMS_COMPUTATION: 0.85,
        }
        
        for stage, expected_start in expected_starts.items():
            assert stage.progress_start == expected_start
    
    def test_stage_progress_end_calculation(self):
        """Progress end should equal start + allocation."""
        for stage in AnalysisStage:
            expected_end = stage.progress_start + stage.time_allocation
            assert stage.progress_end == expected_end


class TestAnalysisProgress:
    """Test AnalysisProgress dataclass methods."""
    
    def test_default_initialization(self):
        """Test default initialization values."""
        progress = AnalysisProgress()
        
        assert progress.current_file_index == 0
        assert progress.total_files == 1
        assert progress.current_filename == ""
        assert progress.current_stage == AnalysisStage.AUDIO_LOADING
        assert progress.stage_progress == 0.0
        assert progress.elapsed_seconds == 0.0
        assert progress.estimated_remaining_seconds is None
    
    def test_file_progress_calculation(self):
        """Test file progress calculation across multiple files."""
        progress = AnalysisProgress(current_file_index=2, total_files=5)
        assert progress.file_progress == 0.4  # 2/5
        
        # Edge case: no files
        progress = AnalysisProgress(total_files=0)
        assert progress.file_progress == 0.0
    
    def test_current_file_progress_calculation(self):
        """Test progress calculation within current file."""
        progress = AnalysisProgress()
        
        # At start of audio loading (0% stage progress)
        progress.current_stage = AnalysisStage.AUDIO_LOADING
        progress.stage_progress = 0.0
        assert progress.current_file_progress == 0.0
        
        # Halfway through audio loading (50% stage progress)
        progress.stage_progress = 0.5
        expected = 0.0 + (0.5 * 0.10)  # start + (progress * allocation)
        assert progress.current_file_progress == expected
        
        # Complete audio loading, start BPM detection
        progress.current_stage = AnalysisStage.BPM_DETECTION
        progress.stage_progress = 0.0
        assert progress.current_file_progress == 0.10
        
        # Halfway through BPM detection
        progress.stage_progress = 0.5
        expected = 0.10 + (0.5 * 0.30)
        assert progress.current_file_progress == expected
        
        # Complete all stages
        progress.current_stage = AnalysisStage.HAMMS_COMPUTATION
        progress.stage_progress = 1.0
        expected = 0.85 + (1.0 * 0.15)
        assert progress.current_file_progress == expected
        assert progress.current_file_progress == 1.0
    
    def test_overall_progress_single_file(self):
        """Test overall progress calculation for single file."""
        progress = AnalysisProgress(total_files=1)
        
        # At start
        assert progress.overall_progress == 0.0
        
        # Halfway through first stage
        progress.stage_progress = 0.5
        assert progress.overall_progress == 0.05  # 0.5 * 0.10 * 1.0
        
        # Complete first stage
        progress.current_stage = AnalysisStage.BPM_DETECTION
        progress.stage_progress = 0.0
        assert progress.overall_progress == 0.10
        
        # Complete analysis
        progress.current_stage = AnalysisStage.HAMMS_COMPUTATION
        progress.stage_progress = 1.0
        assert progress.overall_progress == 1.0
    
    def test_overall_progress_multiple_files(self):
        """Test overall progress calculation for multiple files."""
        progress = AnalysisProgress(total_files=4)
        
        # Halfway through first file, first stage
        progress.stage_progress = 0.5
        expected = (0 / 4) + ((1 / 4) * 0.05)  # completed + current contribution
        assert progress.overall_progress == expected
        
        # Complete first file, start second
        progress.advance_file("file2.wav")
        expected = (1 / 4) + ((1 / 4) * 0.0)
        assert progress.overall_progress == expected
        
        # Halfway through second file, halfway through BPM detection
        progress.current_stage = AnalysisStage.BPM_DETECTION
        progress.stage_progress = 0.5
        current_file_prog = 0.10 + (0.5 * 0.30)  # 0.25
        expected = (1 / 4) + ((1 / 4) * current_file_prog)
        assert abs(progress.overall_progress - expected) < 0.001
    
    def test_update_stage(self):
        """Test stage update functionality."""
        progress = AnalysisProgress()
        
        # Update to new stage
        progress.update_stage(AnalysisStage.BPM_DETECTION, 0.3)
        assert progress.current_stage == AnalysisStage.BPM_DETECTION
        assert progress.stage_progress == 0.3
        
        # Test clamping
        progress.update_stage(AnalysisStage.KEY_DETECTION, 1.5)
        assert progress.stage_progress == 1.0
        
        progress.update_stage(AnalysisStage.KEY_DETECTION, -0.1)
        assert progress.stage_progress == 0.0
    
    def test_complete_stage(self):
        """Test stage completion and advancement."""
        progress = AnalysisProgress()
        
        # Start at audio loading
        assert progress.current_stage == AnalysisStage.AUDIO_LOADING
        
        # Complete audio loading
        progress.complete_stage()
        assert progress.current_stage == AnalysisStage.BPM_DETECTION
        assert progress.stage_progress == 0.0
        
        # Complete BPM detection
        progress.complete_stage()
        assert progress.current_stage == AnalysisStage.KEY_DETECTION
        
        # Complete all stages
        stages = list(AnalysisStage)
        while progress.current_stage != stages[-1]:
            progress.complete_stage()
        
        # Complete final stage
        progress.complete_stage()
        assert progress.current_stage == AnalysisStage.HAMMS_COMPUTATION
        assert progress.stage_progress == 1.0
    
    def test_advance_file(self):
        """Test file advancement functionality."""
        progress = AnalysisProgress(total_files=3)
        
        # Start with first file
        assert progress.current_file_index == 0
        assert progress.current_filename == ""
        
        # Advance to second file
        progress.advance_file("file2.wav")
        assert progress.current_file_index == 1
        assert progress.current_filename == "file2.wav"
        assert progress.current_stage == AnalysisStage.AUDIO_LOADING
        assert progress.stage_progress == 0.0
        
        # Set some progress and advance again
        progress.current_stage = AnalysisStage.BPM_DETECTION
        progress.stage_progress = 0.7
        progress.advance_file("file3.wav")
        assert progress.current_file_index == 2
        assert progress.current_filename == "file3.wav"
        assert progress.current_stage == AnalysisStage.AUDIO_LOADING
        assert progress.stage_progress == 0.0
    
    def test_reset(self):
        """Test progress reset functionality."""
        progress = AnalysisProgress()
        
        # Set some progress
        progress.current_file_index = 2
        progress.current_filename = "test.wav"
        progress.current_stage = AnalysisStage.KEY_DETECTION
        progress.stage_progress = 0.5
        progress.elapsed_seconds = 10.0
        progress.estimated_remaining_seconds = 5.0
        
        # Reset
        progress.reset(total_files=5)
        
        assert progress.current_file_index == 0
        assert progress.total_files == 5
        assert progress.current_filename == ""
        assert progress.current_stage == AnalysisStage.AUDIO_LOADING
        assert progress.stage_progress == 0.0
        assert progress.elapsed_seconds == 0.0
        assert progress.estimated_remaining_seconds is None
    
    def test_edge_case_zero_files(self):
        """Test behavior with zero files."""
        progress = AnalysisProgress(total_files=0)
        
        assert progress.file_progress == 0.0
        assert progress.overall_progress == 0.0
        
        # Reset with zero files
        progress.reset(total_files=0)
        assert progress.total_files == 0
        assert progress.overall_progress == 0.0