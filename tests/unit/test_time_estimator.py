"""Unit tests for TimeEstimator utility class."""

import pytest
import time
from unittest.mock import patch
from src.services.time_estimator import TimeEstimator
from src.models.progress import AnalysisStage


class TestTimeEstimator:
    """Test TimeEstimator functionality."""
    
    def test_initialization(self):
        """Test proper initialization of TimeEstimator."""
        estimator = TimeEstimator()
        
        # Should have empty duration history for all stages
        for stage in AnalysisStage:
            assert estimator._stage_durations[stage] == []
        
        assert estimator._file_start_time is None
        assert estimator._stage_start_time is None
        assert estimator._current_stage is None
    
    def test_start_file_analysis(self):
        """Test file analysis start tracking."""
        estimator = TimeEstimator()
        
        with patch('time.time', return_value=100.0):
            estimator.start_file_analysis()
        
        assert estimator._file_start_time == 100.0
        assert estimator._stage_start_time is None
        assert estimator._current_stage is None
    
    def test_start_stage_first_stage(self):
        """Test starting the first stage of analysis."""
        estimator = TimeEstimator()
        
        with patch('time.time', return_value=100.0):
            estimator.start_stage(AnalysisStage.AUDIO_LOADING)
        
        assert estimator._current_stage == AnalysisStage.AUDIO_LOADING
        assert estimator._stage_start_time == 100.0
        assert len(estimator._stage_durations[AnalysisStage.AUDIO_LOADING]) == 0
    
    def test_start_stage_records_previous_duration(self):
        """Test that starting a new stage records the previous stage duration."""
        estimator = TimeEstimator()
        
        # Start first stage
        with patch('time.time', return_value=100.0):
            estimator.start_stage(AnalysisStage.AUDIO_LOADING)
        
        # Start second stage (should record first stage duration)
        with patch('time.time', return_value=102.5):
            estimator.start_stage(AnalysisStage.BPM_DETECTION)
        
        # Check that audio loading duration was recorded
        assert len(estimator._stage_durations[AnalysisStage.AUDIO_LOADING]) == 1
        assert estimator._stage_durations[AnalysisStage.AUDIO_LOADING][0] == 2.5
        
        # Check new stage is set correctly
        assert estimator._current_stage == AnalysisStage.BPM_DETECTION
        assert estimator._stage_start_time == 102.5
    
    def test_complete_file_analysis(self):
        """Test completion of file analysis."""
        estimator = TimeEstimator()
        
        # Start file and stage
        with patch('time.time', return_value=100.0):
            estimator.start_file_analysis()
            estimator.start_stage(AnalysisStage.AUDIO_LOADING)
        
        # Complete analysis
        with patch('time.time', return_value=103.0):
            estimator.complete_file_analysis()
        
        # Should record final stage duration
        assert len(estimator._stage_durations[AnalysisStage.AUDIO_LOADING]) == 1
        assert estimator._stage_durations[AnalysisStage.AUDIO_LOADING][0] == 3.0
        
        # Should reset tracking variables
        assert estimator._file_start_time is None
        assert estimator._stage_start_time is None
        assert estimator._current_stage is None
    
    def test_get_stage_estimate_with_no_history(self):
        """Test stage estimation with no historical data."""
        estimator = TimeEstimator()
        
        # Should return default estimates
        expected_defaults = {
            AnalysisStage.AUDIO_LOADING: 0.5,
            AnalysisStage.BPM_DETECTION: 2.0,
            AnalysisStage.KEY_DETECTION: 2.0,
            AnalysisStage.ENERGY_CALCULATION: 0.8,
            AnalysisStage.HAMMS_COMPUTATION: 0.7,
        }
        
        for stage, expected in expected_defaults.items():
            assert estimator.get_stage_estimate(stage) == expected
    
    def test_get_stage_estimate_with_history(self):
        """Test stage estimation with historical data."""
        estimator = TimeEstimator()
        
        # Add some test data
        test_durations = [1.0, 2.0, 3.0, 10.0, 1.5]  # Includes outlier
        estimator._stage_durations[AnalysisStage.BPM_DETECTION] = test_durations
        
        # Should return median (2.0) to avoid outlier bias
        assert estimator.get_stage_estimate(AnalysisStage.BPM_DETECTION) == 2.0
    
    def test_get_remaining_time_estimate_no_stage_start(self):
        """Test time estimation when no stage is started."""
        estimator = TimeEstimator()
        
        result = estimator.get_remaining_time_estimate(
            AnalysisStage.BPM_DETECTION, 0.5, 2
        )
        
        assert result is None
    
    def test_get_remaining_time_estimate_with_progress(self):
        """Test time estimation with stage progress."""
        estimator = TimeEstimator()
        
        # Start a stage
        with patch('time.time', return_value=100.0):
            estimator.start_stage(AnalysisStage.BPM_DETECTION)
        
        # Test with 50% progress after 1 second
        with patch('time.time', return_value=101.0):
            result = estimator.get_remaining_time_estimate(
                AnalysisStage.BPM_DETECTION, 0.5, 0
            )
        
        # Should estimate 1 more second for current stage (50% done, 1s elapsed)
        # Plus remaining stages (key:2.0 + energy:0.8 + hamms:0.7 = 3.5)
        expected = 1.0 + 3.5  # 4.5 seconds
        assert abs(result - expected) < 0.1
    
    def test_get_remaining_time_estimate_with_remaining_files(self):
        """Test time estimation including remaining files."""
        estimator = TimeEstimator()
        
        # Add some historical data
        for stage in AnalysisStage:
            estimator._stage_durations[stage] = [1.0, 2.0, 1.5]
        
        with patch('time.time', return_value=100.0):
            estimator.start_stage(AnalysisStage.KEY_DETECTION)
        
        with patch('time.time', return_value=101.0):
            result = estimator.get_remaining_time_estimate(
                AnalysisStage.KEY_DETECTION, 0.5, 2
            )
        
        # Current stage remaining: ~1 second (50% of 2 seconds done)
        # Remaining stages: energy (1.5) + hamms (1.5) = 3.0
        # Remaining files: 2 * avg_file_duration
        # avg_file_duration = sum of stage medians = 1.5 * 5 = 7.5
        expected_current = 1.0 + 3.0  # 4.0
        expected_files = 2 * 7.5      # 15.0
        expected_total = expected_current + expected_files  # 19.0
        
        assert abs(result - expected_total) < 1.0  # Allow some variance
    
    def test_get_average_file_duration_no_history(self):
        """Test average file duration calculation with no history."""
        estimator = TimeEstimator()
        
        # Should return default total (6.0 seconds)
        assert estimator.get_average_file_duration() == 6.0
    
    def test_get_average_file_duration_with_history(self):
        """Test average file duration calculation with history."""
        estimator = TimeEstimator()
        
        # Add test data for each stage
        test_durations = {
            AnalysisStage.AUDIO_LOADING: [0.5, 0.6],
            AnalysisStage.BPM_DETECTION: [2.0, 2.2],
            AnalysisStage.KEY_DETECTION: [1.8, 2.0],
            AnalysisStage.ENERGY_CALCULATION: [0.7, 0.9],
            AnalysisStage.HAMMS_COMPUTATION: [0.6, 0.8],
        }
        
        for stage, durations in test_durations.items():
            estimator._stage_durations[stage] = durations
        
        # Should sum the medians of each stage
        expected = 0.55 + 2.1 + 1.9 + 0.8 + 0.7  # 6.05
        result = estimator.get_average_file_duration()
        assert abs(result - expected) < 0.1
    
    def test_get_elapsed_time(self):
        """Test elapsed time calculation."""
        estimator = TimeEstimator()
        
        # No file started
        assert estimator.get_elapsed_time() == 0.0
        
        # File started
        with patch('time.time', return_value=100.0):
            estimator.start_file_analysis()
        
        with patch('time.time', return_value=103.5):
            assert estimator.get_elapsed_time() == 3.5
    
    def test_clear_history(self):
        """Test clearing historical timing data."""
        estimator = TimeEstimator()
        
        # Add some test data
        for stage in AnalysisStage:
            estimator._stage_durations[stage] = [1.0, 2.0, 3.0]
        
        estimator.clear_history()
        
        # All durations should be cleared
        for stage in AnalysisStage:
            assert estimator._stage_durations[stage] == []
    
    def test_get_statistics_no_data(self):
        """Test statistics with no historical data."""
        estimator = TimeEstimator()
        
        stats = estimator.get_statistics()
        
        # All stages should have count 0
        for stage in AnalysisStage:
            assert stats[stage.value]['count'] == 0
        
        assert stats['total_files_analyzed'] == 0
        assert stats['average_file_duration'] == 6.0
    
    def test_get_statistics_with_data(self):
        """Test statistics with historical data."""
        estimator = TimeEstimator()
        
        # Add test data
        test_data = [1.0, 2.0, 3.0]
        estimator._stage_durations[AnalysisStage.AUDIO_LOADING] = test_data
        estimator._stage_durations[AnalysisStage.BPM_DETECTION] = test_data
        
        stats = estimator.get_statistics()
        
        # Check audio loading stats
        audio_stats = stats[AnalysisStage.AUDIO_LOADING.value]
        assert audio_stats['count'] == 3
        assert audio_stats['mean'] == 2.0
        assert audio_stats['median'] == 2.0
        assert audio_stats['min'] == 1.0
        assert audio_stats['max'] == 3.0
        
        # Check total files (minimum count across stages)
        assert stats['total_files_analyzed'] == 0  # Other stages have 0 data
    
    def test_full_analysis_workflow(self):
        """Test a complete analysis workflow."""
        estimator = TimeEstimator()
        
        # Test workflow without mocking time to avoid complexity
        estimator.start_file_analysis()
        
        # Manually add some test durations
        estimator._stage_durations[AnalysisStage.AUDIO_LOADING].append(0.5)
        estimator._stage_durations[AnalysisStage.BPM_DETECTION].append(2.0)
        estimator._stage_durations[AnalysisStage.KEY_DETECTION].append(1.8)
        estimator._stage_durations[AnalysisStage.ENERGY_CALCULATION].append(0.8)
        estimator._stage_durations[AnalysisStage.HAMMS_COMPUTATION].append(0.7)
        
        # Test that estimates use recorded data
        assert estimator.get_stage_estimate(AnalysisStage.AUDIO_LOADING) == 0.5
        assert estimator.get_stage_estimate(AnalysisStage.BPM_DETECTION) == 2.0
        assert estimator.get_stage_estimate(AnalysisStage.KEY_DETECTION) == 1.8
        assert estimator.get_stage_estimate(AnalysisStage.ENERGY_CALCULATION) == 0.8
        assert estimator.get_stage_estimate(AnalysisStage.HAMMS_COMPUTATION) == 0.7
    
    def test_edge_cases(self):
        """Test edge cases and error conditions."""
        estimator = TimeEstimator()
        
        # Complete file without starting one
        estimator.complete_file_analysis()  # Should not crash
        
        # Start stage without starting file
        estimator.start_stage(AnalysisStage.BPM_DETECTION)
        assert estimator._current_stage == AnalysisStage.BPM_DETECTION
        
        # Get estimate for stage with empty list (edge case of median)
        estimator._stage_durations[AnalysisStage.BPM_DETECTION] = []
        estimate = estimator.get_stage_estimate(AnalysisStage.BPM_DETECTION)
        assert estimate == 2.0  # Should return default