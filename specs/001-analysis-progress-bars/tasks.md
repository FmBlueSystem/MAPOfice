# Tasks: Detailed Analysis Progress Bars

**Input**: Design documents from `/specs/001-analysis-progress-bars/`
**Prerequisites**: plan.md (✅), spec.md (✅)

## Phase 3.1: Setup & Foundation
- [ ] T001 Create test fixtures for progress tracking (`tests/fixtures/sample_audio_short.wav` - 5 second audio file)
- [ ] T002 [P] Create `src/models/progress.py` with `AnalysisProgress` dataclass and `AnalysisStage` enum
- [ ] T003 [P] Create `src/services/time_estimator.py` with `TimeEstimator` class for duration tracking

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
- [ ] T004 [P] Write unit tests in `tests/unit/test_analysis_progress.py` for AnalysisProgress calculations
- [ ] T005 [P] Write unit tests in `tests/unit/test_time_estimator.py` for TimeEstimator algorithms  
- [ ] T006 [P] Write integration test in `tests/integration/test_progress_workflow.py` for end-to-end progress tracking
- [ ] T007 Create mock analysis functions in `tests/unit/test_progress_callbacks.py` to test callback interface

## Phase 3.3: Core Implementation
- [ ] T008 Extend `src/ui/main_window.py` - add new progress UI components (file_progress_bar, stage_progress_bar, stage_label, time_label)
- [ ] T009 Modify `src/ui/main_window.py` - add new signal handlers for detailed progress (on_stage_progress, on_stage_changed, on_time_estimate)
- [ ] T010 Create `src/lib/progress_callback.py` with ProgressCallback protocol interface
- [ ] T011 Instrument `src/lib/audio_processing.py` - add progress callbacks to `_analyze_with_librosa()` function
- [ ] T012 Extend `src/ui/main_window.py` AnalyzeWorker class - add new pyqtSignals (stage_progress, stage_changed, time_estimate)

## Phase 3.4: Integration & Workflow
- [ ] T013 Modify `src/ui/main_window.py` AnalyzeWorker.run() - integrate TimeEstimator and emit detailed progress signals
- [ ] T014 Update `src/services/analyzer.py` - pass progress callback through to audio_processing functions
- [ ] T015 Enhance error handling in `src/lib/audio_processing.py` - emit stage-specific error information
- [ ] T016 Update UI layout in `src/ui/main_window.py` - reorganize progress section with new components

## Phase 3.5: Polish & Refinement  
- [ ] T017 [P] Add progress persistence in `src/services/time_estimator.py` - save/load historical timing data
- [ ] T018 [P] Implement smooth progress animations in `src/ui/main_window.py` - prevent jumpy progress updates
- [ ] T019 [P] Add cancellation support during stages in `src/ui/main_window.py` AnalyzeWorker
- [ ] T020 [P] Create comprehensive integration test in `tests/integration/test_full_analysis_ui.py` using QTest framework
- [ ] T021 Update `CLAUDE.md` - document new progress tracking capabilities and testing approaches

## Dependencies & Execution Strategy

### Sequential Dependencies
```
T001 → T004,T005,T006,T007 (Tests need fixtures)
T002,T003 → T008,T009,T010,T011,T012 (Core needs foundation)  
T008,T009,T010,T011,T012 → T013,T014,T015,T016 (Integration needs core)
T013,T014,T015,T016 → T017,T018,T019,T020,T021 (Polish needs working integration)
```

### Parallel Execution Examples
**Wave 1 - Foundation (after T001)**:
```bash
# Can run simultaneously - different files
T002 & T003 &    # Models and services
T004 & T005 &    # Unit tests  
T006 & T007      # Integration tests
```

**Wave 2 - Core Implementation**:
```bash
# Must be sequential - same files
T008 → T009 → T012  # UI modifications in main_window.py
T010 → T011         # Progress callback integration
```

**Wave 3 - Polish (after integration complete)**:  
```bash
T017 & T018 & T019 & T020 & T021  # All independent enhancements
```

## Testing Strategy
- **Unit Tests**: Test progress calculations, time estimation algorithms
- **Integration Tests**: Test callback flow from audio processing to UI  
- **UI Tests**: Use QTest to verify progress bar updates and user interactions
- **Mock Testing**: Simulate long-running analysis with controllable progress

## Definition of Done
Each task is complete when:
1. ✅ Code passes existing tests (no regressions)
2. ✅ New functionality has corresponding tests
3. ✅ Progress tracking works with test audio files
4. ✅ UI updates smoothly without blocking
5. ✅ Error scenarios handled gracefully
6. ✅ Backward compatibility maintained (existing progress signal still works)

## Risk Mitigation
- **Task T007**: Mock functions prevent dependency on actual audio processing during testing
- **Task T015**: Stage-specific error handling prevents progress UI from breaking on failures
- **Task T019**: Cancellation support ensures UI remains responsive during long operations
- **Backward Compatibility**: Existing `progress` signal maintained alongside new detailed signals

---
**Ready for implementation** - All tasks defined with clear dependencies and parallel execution opportunities