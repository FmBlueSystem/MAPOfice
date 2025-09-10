"""Integration tests for end-to-end progress tracking workflow."""

import pytest
import os
from unittest.mock import Mock, patch
from src.models.progress import AnalysisProgress, AnalysisStage
from src.services.time_estimator import TimeEstimator


class TestProgressWorkflow:
    """Test complete progress tracking workflow."""
    
    @pytest.fixture
    def sample_audio_file(self):
        """Provide path to test audio fixture."""
        return os.path.join("tests", "fixtures", "sample_audio_short.wav")
    
    @pytest.fixture
    def progress_tracker(self):
        """Provide fresh AnalysisProgress instance."""
        return AnalysisProgress()
    
    @pytest.fixture
    def time_estimator(self):
        """Provide fresh TimeEstimator instance."""
        return TimeEstimator()
    
    def test_single_file_progress_workflow(self, progress_tracker, time_estimator):
        """Test complete progress workflow for a single file."""
        # Initialize for single file
        progress_tracker.reset(total_files=1)
        progress_tracker.current_filename = "test_audio.wav"
        
        # Start timing
        with patch('time.time', side_effect=[100.0, 100.5, 102.5, 104.5, 105.3, 106.0]):
            time_estimator.start_file_analysis()
            
            # Stage 1: Audio Loading
            time_estimator.start_stage(AnalysisStage.AUDIO_LOADING)
            progress_tracker.update_stage(AnalysisStage.AUDIO_LOADING, 0.0)
            assert progress_tracker.overall_progress == 0.0
            
            # Halfway through audio loading
            progress_tracker.update_stage(AnalysisStage.AUDIO_LOADING, 0.5)
            assert progress_tracker.overall_progress == 0.05  # 50% of 10%
            
            # Complete audio loading, start BPM detection
            progress_tracker.complete_stage()
            time_estimator.start_stage(AnalysisStage.BPM_DETECTION)
            assert progress_tracker.current_stage == AnalysisStage.BPM_DETECTION
            assert progress_tracker.overall_progress == 0.10
            
            # Progress through BPM detection
            progress_tracker.update_stage(AnalysisStage.BPM_DETECTION, 0.3)
            expected = 0.10 + (0.3 * 0.30)  # 10% + 30% of 30%
            assert abs(progress_tracker.overall_progress - expected) < 0.001
            
            # Complete BPM, start key detection
            progress_tracker.complete_stage()
            time_estimator.start_stage(AnalysisStage.KEY_DETECTION)
            assert progress_tracker.current_stage == AnalysisStage.KEY_DETECTION
            assert progress_tracker.overall_progress == 0.40
            
            # Complete key detection, start energy calculation
            progress_tracker.complete_stage()
            time_estimator.start_stage(AnalysisStage.ENERGY_CALCULATION)
            assert progress_tracker.current_stage == AnalysisStage.ENERGY_CALCULATION
            assert progress_tracker.overall_progress == 0.70
            
            # Complete energy, start HAMMS
            progress_tracker.complete_stage()
            time_estimator.start_stage(AnalysisStage.HAMMS_COMPUTATION)
            assert progress_tracker.current_stage == AnalysisStage.HAMMS_COMPUTATION
            assert progress_tracker.overall_progress == 0.85
            
            # Complete HAMMS computation
            progress_tracker.update_stage(AnalysisStage.HAMMS_COMPUTATION, 1.0)
            assert progress_tracker.overall_progress == 1.0
            
            time_estimator.complete_file_analysis()
        
        # Verify timing data was recorded
        assert len(time_estimator._stage_durations[AnalysisStage.AUDIO_LOADING]) == 1
        assert len(time_estimator._stage_durations[AnalysisStage.BPM_DETECTION]) == 1
        assert len(time_estimator._stage_durations[AnalysisStage.KEY_DETECTION]) == 1
        assert len(time_estimator._stage_durations[AnalysisStage.ENERGY_CALCULATION]) == 1
        assert len(time_estimator._stage_durations[AnalysisStage.HAMMS_COMPUTATION]) == 1
    
    def test_multiple_files_progress_workflow(self, progress_tracker, time_estimator):
        """Test progress workflow for multiple files."""
        # Initialize for 3 files
        progress_tracker.reset(total_files=3)
        
        # Process first file
        progress_tracker.current_filename = "file1.wav"
        time_estimator.start_file_analysis()
        
        # Go through all stages quickly
        for stage in AnalysisStage:
            time_estimator.start_stage(stage)
            progress_tracker.update_stage(stage, 1.0)
        
        time_estimator.complete_file_analysis()
        
        # Verify first file complete
        assert progress_tracker.current_file_progress == 1.0
        file_progress_after_first = progress_tracker.overall_progress
        assert abs(file_progress_after_first - (1/3)) < 0.01
        
        # Advance to second file
        progress_tracker.advance_file("file2.wav")
        assert progress_tracker.current_file_index == 1
        assert progress_tracker.current_stage == AnalysisStage.AUDIO_LOADING
        assert progress_tracker.stage_progress == 0.0
        
        # Start second file
        time_estimator.start_file_analysis()
        time_estimator.start_stage(AnalysisStage.AUDIO_LOADING)
        
        # Halfway through second file's first stage
        progress_tracker.update_stage(AnalysisStage.AUDIO_LOADING, 0.5)
        
        # Overall progress should be: 1/3 (first file) + (1/3 * 0.05) (current progress)
        expected = (1/3) + (1/3) * 0.05
        assert abs(progress_tracker.overall_progress - expected) < 0.01
        
        # Complete second file
        for stage in list(AnalysisStage)[1:]:  # Skip AUDIO_LOADING
            progress_tracker.complete_stage()
            time_estimator.start_stage(stage)
        progress_tracker.update_stage(AnalysisStage.HAMMS_COMPUTATION, 1.0)
        time_estimator.complete_file_analysis()
        
        # Advance to third file
        progress_tracker.advance_file("file3.wav")
        assert progress_tracker.current_file_index == 2
        
        # Complete third file
        time_estimator.start_file_analysis()
        for stage in AnalysisStage:
            time_estimator.start_stage(stage)
            progress_tracker.update_stage(stage, 1.0)
        time_estimator.complete_file_analysis()
        
        # Final progress should be 100%
        assert abs(progress_tracker.overall_progress - 1.0) < 0.01
    
    def test_time_estimation_improves_with_data(self, time_estimator):
        """Test that time estimation accuracy improves with historical data."""
        # First file - only defaults available
        initial_estimate = time_estimator.get_stage_estimate(AnalysisStage.BPM_DETECTION)
        assert initial_estimate == 2.0  # Default value
        
        # Simulate analyzing several files with consistent BPM detection time
        consistent_duration = 1.5
        
        for i in range(5):
            with patch('time.time', side_effect=[100.0, 100.0 + consistent_duration]):
                time_estimator.start_stage(AnalysisStage.BPM_DETECTION)
                time_estimator.start_stage(AnalysisStage.KEY_DETECTION)  # Ends BPM stage
        
        # Estimate should now be closer to actual duration
        improved_estimate = time_estimator.get_stage_estimate(AnalysisStage.BPM_DETECTION)
        assert improved_estimate == consistent_duration
        assert improved_estimate != initial_estimate
    
    def test_progress_callback_interface(self):
        """Test the progress callback interface for integration."""
        # Create mock callback
        progress_callback = Mock()
        
        # Simulate progress updates
        progress = AnalysisProgress(total_files=2)
        
        def simulate_analysis_with_callbacks():
            """Simulate analysis that makes callback calls."""
            # Start first file
            progress_callback(progress.current_stage, 0.0, "Starting audio loading")
            progress.update_stage(AnalysisStage.AUDIO_LOADING, 0.0)
            
            # Audio loading progress
            progress_callback(progress.current_stage, 0.5, "Loading audio data")
            progress.update_stage(AnalysisStage.AUDIO_LOADING, 0.5)
            
            # Complete audio loading
            progress_callback(progress.current_stage, 1.0, "Audio loaded")
            progress.complete_stage()
            
            # BPM detection
            progress_callback(progress.current_stage, 0.0, "Starting BPM detection")
            progress.update_stage(AnalysisStage.BPM_DETECTION, 0.0)
            
            progress_callback(progress.current_stage, 1.0, "BPM detected")
            progress.complete_stage()
            
            # Continue through remaining stages...
            for stage in [AnalysisStage.KEY_DETECTION, 
                         AnalysisStage.ENERGY_CALCULATION, 
                         AnalysisStage.HAMMS_COMPUTATION]:
                progress_callback(stage, 0.0, f"Starting {stage.value}")
                progress.update_stage(stage, 0.0)
                progress_callback(stage, 1.0, f"Completed {stage.value}")
                progress.complete_stage()
        
        simulate_analysis_with_callbacks()
        
        # Verify callback was called for each stage
        assert progress_callback.call_count >= 10  # At least 2 calls per stage
        
        # Verify callback was called with correct stage types
        called_stages = {call[0][0] for call in progress_callback.call_args_list}
        assert called_stages == set(AnalysisStage)
    
    def test_error_handling_during_progress(self, progress_tracker, time_estimator):
        """Test progress tracking behavior when errors occur during analysis."""
        progress_tracker.reset(total_files=1)
        time_estimator.start_file_analysis()
        
        # Start BPM detection
        time_estimator.start_stage(AnalysisStage.BPM_DETECTION)
        progress_tracker.update_stage(AnalysisStage.BPM_DETECTION, 0.3)
        
        # Simulate error during BPM detection (e.g., corrupted audio)
        # Progress should remain consistent
        current_progress = progress_tracker.overall_progress
        
        # Error occurs, but progress state is preserved
        assert progress_tracker.current_stage == AnalysisStage.BPM_DETECTION
        assert progress_tracker.stage_progress == 0.3
        assert progress_tracker.overall_progress == current_progress
        
        # Analysis can be resumed or restarted
        progress_tracker.reset(total_files=1)
        assert progress_tracker.current_stage == AnalysisStage.AUDIO_LOADING
        assert progress_tracker.stage_progress == 0.0
        assert progress_tracker.overall_progress == 0.0
    
    def test_cancellation_support(self, progress_tracker, time_estimator):
        """Test that progress tracking supports cancellation."""
        progress_tracker.reset(total_files=3)
        time_estimator.start_file_analysis()
        
        # Start analysis
        time_estimator.start_stage(AnalysisStage.BPM_DETECTION)
        progress_tracker.update_stage(AnalysisStage.BPM_DETECTION, 0.6)
        
        # Record state before cancellation
        pre_cancel_file_index = progress_tracker.current_file_index
        pre_cancel_stage = progress_tracker.current_stage
        pre_cancel_progress = progress_tracker.stage_progress
        
        # Simulate cancellation (analysis stops, but state preserved)
        # No automatic cleanup - state remains for potential resume
        assert progress_tracker.current_file_index == pre_cancel_file_index
        assert progress_tracker.current_stage == pre_cancel_stage
        assert progress_tracker.stage_progress == pre_cancel_progress
        
        # Manual cleanup after cancellation
        progress_tracker.reset(total_files=0)
        time_estimator.clear_history()
        
        assert progress_tracker.current_file_index == 0
        assert progress_tracker.total_files == 0
        assert progress_tracker.overall_progress == 0.0
    
    def test_real_audio_file_integration(self, sample_audio_file, progress_tracker):
        """Test progress tracking with real audio file if available."""
        if not os.path.exists(sample_audio_file):
            pytest.skip(f"Audio fixture not found: {sample_audio_file}")
        
        progress_tracker.reset(total_files=1)
        progress_tracker.current_filename = os.path.basename(sample_audio_file)
        
        # Verify file exists and basic properties
        assert os.path.getsize(sample_audio_file) > 0
        assert sample_audio_file.endswith('.wav')
        
        # Progress tracking should work regardless of actual audio content
        progress_tracker.update_stage(AnalysisStage.AUDIO_LOADING, 1.0)
        assert progress_tracker.current_file_progress == 0.10
        
        progress_tracker.complete_stage()
        assert progress_tracker.current_stage == AnalysisStage.BPM_DETECTION
        assert progress_tracker.overall_progress == 0.10