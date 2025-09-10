"""Unit tests for progress callback interface and mock analysis functions."""

import pytest
from unittest.mock import Mock, call
from typing import Callable, Optional
from src.models.progress import AnalysisStage


# Define the progress callback protocol
ProgressCallback = Callable[[AnalysisStage, float, str], None]


class MockAnalysisEngine:
    """Mock analysis engine for testing progress callbacks."""
    
    def __init__(self, progress_callback: Optional[ProgressCallback] = None):
        self.progress_callback = progress_callback
        self.should_fail = False
        self.fail_at_stage = None
        
    def analyze_audio_file(self, file_path: str) -> dict:
        """Mock analysis that emits progress callbacks."""
        result = {
            'bpm': None,
            'key': None,
            'energy': None,
            'hamms': None
        }
        
        # Stage 1: Audio Loading
        self._emit_progress(AnalysisStage.AUDIO_LOADING, 0.0, f"Loading {file_path}")
        
        if self._should_fail_at_stage(AnalysisStage.AUDIO_LOADING):
            raise RuntimeError("Failed to load audio file")
        
        self._emit_progress(AnalysisStage.AUDIO_LOADING, 0.5, "Reading audio data")
        self._emit_progress(AnalysisStage.AUDIO_LOADING, 1.0, "Audio loaded successfully")
        
        # Stage 2: BPM Detection
        self._emit_progress(AnalysisStage.BPM_DETECTION, 0.0, "Starting BPM analysis")
        
        if self._should_fail_at_stage(AnalysisStage.BPM_DETECTION):
            raise RuntimeError("BPM detection failed")
        
        self._emit_progress(AnalysisStage.BPM_DETECTION, 0.3, "Analyzing beat patterns")
        self._emit_progress(AnalysisStage.BPM_DETECTION, 0.7, "Refining BPM estimate")
        self._emit_progress(AnalysisStage.BPM_DETECTION, 1.0, "BPM detection complete")
        result['bpm'] = 120.0
        
        # Stage 3: Key Detection
        self._emit_progress(AnalysisStage.KEY_DETECTION, 0.0, "Starting key analysis")
        
        if self._should_fail_at_stage(AnalysisStage.KEY_DETECTION):
            raise RuntimeError("Key detection failed")
        
        self._emit_progress(AnalysisStage.KEY_DETECTION, 0.4, "Analyzing harmonic content")
        self._emit_progress(AnalysisStage.KEY_DETECTION, 0.8, "Determining key signature")
        self._emit_progress(AnalysisStage.KEY_DETECTION, 1.0, "Key detection complete")
        result['key'] = 'C major'
        
        # Stage 4: Energy Calculation
        self._emit_progress(AnalysisStage.ENERGY_CALCULATION, 0.0, "Calculating energy levels")
        
        if self._should_fail_at_stage(AnalysisStage.ENERGY_CALCULATION):
            raise RuntimeError("Energy calculation failed")
        
        self._emit_progress(AnalysisStage.ENERGY_CALCULATION, 0.6, "Analyzing spectral energy")
        self._emit_progress(AnalysisStage.ENERGY_CALCULATION, 1.0, "Energy calculation complete")
        result['energy'] = 0.75
        
        # Stage 5: HAMMS Computation
        self._emit_progress(AnalysisStage.HAMMS_COMPUTATION, 0.0, "Computing HAMMS features")
        
        if self._should_fail_at_stage(AnalysisStage.HAMMS_COMPUTATION):
            raise RuntimeError("HAMMS computation failed")
        
        self._emit_progress(AnalysisStage.HAMMS_COMPUTATION, 0.3, "Extracting harmonic features")
        self._emit_progress(AnalysisStage.HAMMS_COMPUTATION, 0.7, "Building feature vector")
        self._emit_progress(AnalysisStage.HAMMS_COMPUTATION, 1.0, "HAMMS computation complete")
        result['hamms'] = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 0.9, 0.8]
        
        return result
    
    def _emit_progress(self, stage: AnalysisStage, progress: float, message: str):
        """Emit progress callback if available."""
        if self.progress_callback:
            self.progress_callback(stage, progress, message)
    
    def _should_fail_at_stage(self, stage: AnalysisStage) -> bool:
        """Check if analysis should fail at given stage."""
        return self.should_fail and self.fail_at_stage == stage
    
    def set_failure_mode(self, fail_at_stage: AnalysisStage):
        """Configure analysis to fail at specific stage."""
        self.should_fail = True
        self.fail_at_stage = fail_at_stage


class TestProgressCallbacks:
    """Test progress callback interface and mock analysis functions."""
    
    def test_callback_interface_signature(self):
        """Test that callback interface has correct signature."""
        # Create a mock callback
        callback = Mock()
        
        # Should be callable with stage, progress, and message
        callback(AnalysisStage.BPM_DETECTION, 0.5, "Test message")
        
        # Verify call
        callback.assert_called_once_with(
            AnalysisStage.BPM_DETECTION, 0.5, "Test message"
        )
    
    def test_mock_analysis_without_callback(self):
        """Test mock analysis works without progress callback."""
        engine = MockAnalysisEngine()
        
        result = engine.analyze_audio_file("test.wav")
        
        # Should complete successfully
        assert result['bpm'] == 120.0
        assert result['key'] == 'C major'
        assert result['energy'] == 0.75
        assert len(result['hamms']) == 12
    
    def test_mock_analysis_with_callback(self):
        """Test mock analysis emits progress callbacks."""
        callback = Mock()
        engine = MockAnalysisEngine(progress_callback=callback)
        
        result = engine.analyze_audio_file("test.wav")
        
        # Should complete successfully
        assert result['bpm'] == 120.0
        
        # Should have called callback for each stage
        call_args = callback.call_args_list
        assert len(call_args) > 0
        
        # Verify calls for each stage
        stages_called = {call[0][0] for call in call_args}
        assert stages_called == set(AnalysisStage)
        
        # Verify progress values are in range [0.0, 1.0]
        progress_values = [call[0][1] for call in call_args]
        assert all(0.0 <= p <= 1.0 for p in progress_values)
        
        # Verify messages are strings
        messages = [call[0][2] for call in call_args]
        assert all(isinstance(msg, str) for msg in messages)
    
    def test_callback_receives_stage_progression(self):
        """Test that callbacks show proper stage progression."""
        callback = Mock()
        engine = MockAnalysisEngine(progress_callback=callback)
        
        engine.analyze_audio_file("test.wav")
        
        # Extract stages from callback calls
        call_stages = [call[0][0] for call in callback.call_args_list]
        
        # Verify we see all stages in order
        stage_order = list(AnalysisStage)
        stage_indices = []
        
        for call_stage in call_stages:
            stage_indices.append(stage_order.index(call_stage))
        
        # Should not go backwards in stage progression
        for i in range(1, len(stage_indices)):
            assert stage_indices[i] >= stage_indices[i-1]
    
    def test_callback_receives_progress_within_stages(self):
        """Test that progress values increase within each stage."""
        callback = Mock()
        engine = MockAnalysisEngine(progress_callback=callback)
        
        engine.analyze_audio_file("test.wav")
        
        # Group calls by stage
        stage_progress = {}
        for call in callback.call_args_list:
            stage, progress, _ = call[0]
            if stage not in stage_progress:
                stage_progress[stage] = []
            stage_progress[stage].append(progress)
        
        # For each stage, progress should be non-decreasing
        for stage, progress_values in stage_progress.items():
            for i in range(1, len(progress_values)):
                assert progress_values[i] >= progress_values[i-1], \
                    f"Progress decreased in stage {stage}: {progress_values}"
            
            # Each stage should start at 0.0 and end at 1.0
            assert progress_values[0] == 0.0, f"Stage {stage} didn't start at 0.0"
            assert progress_values[-1] == 1.0, f"Stage {stage} didn't end at 1.0"
    
    def test_callback_messages_are_descriptive(self):
        """Test that callback messages are descriptive and stage-specific."""
        callback = Mock()
        engine = MockAnalysisEngine(progress_callback=callback)
        
        engine.analyze_audio_file("test_file.wav")
        
        # Group messages by stage
        stage_messages = {}
        for call in callback.call_args_list:
            stage, _, message = call[0]
            if stage not in stage_messages:
                stage_messages[stage] = []
            stage_messages[stage].append(message)
        
        # Check that each stage has appropriate messages
        audio_messages = stage_messages[AnalysisStage.AUDIO_LOADING]
        assert any("Loading" in msg or "load" in msg.lower() for msg in audio_messages)
        
        bpm_messages = stage_messages[AnalysisStage.BPM_DETECTION]
        assert any("BPM" in msg or "beat" in msg.lower() for msg in bpm_messages)
        
        key_messages = stage_messages[AnalysisStage.KEY_DETECTION]
        assert any("key" in msg.lower() or "harmonic" in msg.lower() for msg in key_messages)
        
        energy_messages = stage_messages[AnalysisStage.ENERGY_CALCULATION]
        assert any("energy" in msg.lower() for msg in energy_messages)
        
        hamms_messages = stage_messages[AnalysisStage.HAMMS_COMPUTATION]
        assert any("HAMMS" in msg or "feature" in msg.lower() for msg in hamms_messages)
    
    def test_failure_during_audio_loading(self):
        """Test callback behavior when analysis fails during audio loading."""
        callback = Mock()
        engine = MockAnalysisEngine(progress_callback=callback)
        engine.set_failure_mode(AnalysisStage.AUDIO_LOADING)
        
        with pytest.raises(RuntimeError, match="Failed to load audio file"):
            engine.analyze_audio_file("corrupt.wav")
        
        # Should have called callback for audio loading start
        call_stages = [call[0][0] for call in callback.call_args_list]
        assert AnalysisStage.AUDIO_LOADING in call_stages
        
        # Should not have progressed to later stages
        assert AnalysisStage.BPM_DETECTION not in call_stages
    
    def test_failure_during_bpm_detection(self):
        """Test callback behavior when analysis fails during BPM detection."""
        callback = Mock()
        engine = MockAnalysisEngine(progress_callback=callback)
        engine.set_failure_mode(AnalysisStage.BPM_DETECTION)
        
        with pytest.raises(RuntimeError, match="BPM detection failed"):
            engine.analyze_audio_file("difficult.wav")
        
        # Should have completed audio loading
        call_stages = [call[0][0] for call in callback.call_args_list]
        assert AnalysisStage.AUDIO_LOADING in call_stages
        assert AnalysisStage.BPM_DETECTION in call_stages
        
        # Should not have progressed to key detection
        assert AnalysisStage.KEY_DETECTION not in call_stages
    
    def test_failure_during_final_stage(self):
        """Test callback behavior when analysis fails during final stage."""
        callback = Mock()
        engine = MockAnalysisEngine(progress_callback=callback)
        engine.set_failure_mode(AnalysisStage.HAMMS_COMPUTATION)
        
        with pytest.raises(RuntimeError, match="HAMMS computation failed"):
            engine.analyze_audio_file("test.wav")
        
        # Should have completed all stages except HAMMS
        call_stages = [call[0][0] for call in callback.call_args_list]
        assert AnalysisStage.AUDIO_LOADING in call_stages
        assert AnalysisStage.BPM_DETECTION in call_stages
        assert AnalysisStage.KEY_DETECTION in call_stages
        assert AnalysisStage.ENERGY_CALCULATION in call_stages
        assert AnalysisStage.HAMMS_COMPUTATION in call_stages  # Started but failed
    
    def test_callback_exception_handling(self):
        """Test that callback exceptions don't break analysis."""
        def failing_callback(stage, progress, message):
            if stage == AnalysisStage.BPM_DETECTION and progress > 0.5:
                raise ValueError("Callback error")
        
        engine = MockAnalysisEngine(progress_callback=failing_callback)
        
        # Analysis should continue despite callback failure
        # Note: In real implementation, callback errors should be caught
        with pytest.raises(ValueError, match="Callback error"):
            engine.analyze_audio_file("test.wav")
    
    def test_multiple_files_callback_pattern(self):
        """Test callback pattern for analyzing multiple files."""
        callback = Mock()
        engine = MockAnalysisEngine(progress_callback=callback)
        
        files = ["file1.wav", "file2.wav", "file3.wav"]
        results = []
        
        for file_path in files:
            result = engine.analyze_audio_file(file_path)
            results.append(result)
        
        # Should have received callbacks for each file
        call_count = callback.call_count
        assert call_count > len(files) * len(AnalysisStage)  # Multiple calls per stage
        
        # Each file should produce the same analysis structure
        for result in results:
            assert 'bpm' in result
            assert 'key' in result
            assert 'energy' in result
            assert 'hamms' in result
    
    def test_callback_timing_information(self):
        """Test that callbacks can be used for timing analysis."""
        call_times = []
        
        def timing_callback(stage, progress, message):
            import time
            call_times.append((time.time(), stage, progress))
        
        engine = MockAnalysisEngine(progress_callback=timing_callback)
        engine.analyze_audio_file("test.wav")
        
        # Should have recorded timing information
        assert len(call_times) > 0
        
        # Times should be increasing (non-decreasing)
        times = [call_time[0] for call_time in call_times]
        for i in range(1, len(times)):
            assert times[i] >= times[i-1]