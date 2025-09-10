# Implementation Plan: Detailed Analysis Progress Bars

**Branch**: `001-analysis-progress-bars` | **Date**: 2025-09-09 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-analysis-progress-bars/spec.md`

## Summary
Add detailed progress tracking to the Music Analyzer Pro PyQt6 application, showing individual analysis stages (Audio Loading, BPM Detection, Key Detection, Energy Calculation, HAMMS Computation) with accurate progress percentages, time estimates, and cancellation support. Technical approach: Extend existing AnalyzeWorker thread with stage-aware progress callbacks and enhance main window UI with multi-level progress displays.

## Technical Context
**Language/Version**: Python 3.11+  
**Primary Dependencies**: PyQt6, librosa, numpy (existing)  
**Storage**: SQLite (existing - no changes needed)  
**Testing**: pytest (existing test framework)  
**Target Platform**: macOS/Linux desktop (existing)
**Project Type**: Single desktop application  
**Performance Goals**: Progress updates < 250ms lag, no UI blocking  
**Constraints**: Single-threaded analysis (existing), memory efficient progress tracking  
**Scale/Scope**: Individual user, small-medium music libraries (100-10k files)

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Simplicity**:
- Projects: 1 (desktop UI application - existing)
- Using framework directly? ✅ (Direct PyQt6 usage, no wrappers)
- Adding complexity? ⚠️ (Enhanced progress tracking - justified by significant UX improvement)

**Performance**:
- Measuring before optimizing? ✅ (Current progress is too basic, clear user pain point)
- Avoiding premature abstraction? ✅ (Extending existing AnalyzeWorker pattern)

**Maintainability**:
- Single responsibility? ✅ (Progress tracking separated from analysis logic)
- Clear interfaces? ✅ (Callback-based progress reporting)
- Testing strategy? ✅ (Unit tests for progress calculation, integration tests for UI)

**User Value**:
- Solves real problem? ✅ (Users cannot see analysis progress details currently)
- Simplest solution first? ✅ (Building on existing thread architecture)

✅ **Constitution Check: PASSED** - Feature adds clear user value with minimal architectural complexity

## Phase 0: Research & Investigation

### Current Architecture Analysis
**Existing Components**:
- `AnalyzeWorker(QThread)`: Background analysis thread with basic progress signals
- `MainWindow`: UI coordinator with simple progress bar
- `src/lib/audio_processing.py`: Core analysis functions (analyze_track)
- `src/services/analyzer.py`: Business logic wrapper

**Current Progress Flow**:
1. `AnalyzeWorker.run()` → iterates through files
2. Calls `analyzer.analyze_path()` for each file  
3. Emits `progress.emit(i, total)` after each file completion
4. `MainWindow.on_progress()` updates single progress bar

**Limitations Identified**:
- No visibility into individual file analysis stages
- No time estimation capabilities
- Progress jumps after each file (not smooth)
- Cannot determine which stage is running or failing

### Stage Identification & Timing
**Analysis Pipeline in `_analyze_with_librosa()`**:
1. **Audio Loading**: `librosa.load()` - ~10% of time, I/O bound
2. **BPM Detection**: `librosa.beat.beat_track()` - ~30% of time, CPU intensive
3. **Key Detection**: `librosa.feature.chroma_cqt()` + processing - ~30% of time
4. **Energy Calculation**: `librosa.feature.rms()` - ~15% of time, lightweight
5. **HAMMS Computation**: Chroma processing + normalization - ~15% of time

**Time Estimation Strategy**:
- Use weighted stage durations based on empirical measurements
- Maintain running average of stage completion times
- Account for file size and sample rate in estimates

### PyQt6 Progress Patterns
**Multi-level Progress Options**:
- Nested `QProgressBar` widgets (file + stage level)
- `QLabel` for stage names and time estimates
- `QGroupBox` to organize progress sections
- Real-time updates via existing signal/slot pattern

### Error Handling Integration
**Current Error Pattern**: Exceptions caught in worker thread, logged
**Enhancement Needed**: Stage-specific error reporting with recovery options

## Phase 1: Design & Contracts

### Data Model Extensions

#### AnalysisProgress Class
```python
@dataclass
class AnalysisProgress:
    # File-level tracking
    file_count_total: int
    file_count_current: int
    current_filename: str
    
    # Stage-level tracking
    stage_name: str
    stage_progress: float  # 0.0 to 1.0
    stage_index: int       # 0-based stage number
    total_stages: int      # Usually 5
    
    # Time tracking
    time_elapsed: float    # seconds
    time_remaining: float  # estimated seconds
    
    # Overall progress (computed property)
    @property
    def overall_progress(self) -> float:
        file_progress = (self.file_count_current - 1) / self.file_count_total
        stage_progress = self.stage_progress / self.total_stages
        return file_progress + (stage_progress / self.file_count_total)
```

#### AnalysisStage Enum
```python
class AnalysisStage(Enum):
    AUDIO_LOADING = ("Loading audio", 0.10)
    BPM_DETECTION = ("Detecting BPM", 0.30) 
    KEY_DETECTION = ("Detecting key", 0.30)
    ENERGY_CALCULATION = ("Calculating energy", 0.15)
    HAMMS_COMPUTATION = ("Computing HAMMS", 0.15)
    
    def __init__(self, display_name: str, weight: float):
        self.display_name = display_name
        self.weight = weight  # Relative computational weight
```

### Interface Contracts

#### Enhanced Progress Signals
```python
class AnalyzeWorker(QThread):
    # Existing signals
    progress = pyqtSignal(int, int)  # Keep for compatibility
    log = pyqtSignal(str)
    done = pyqtSignal(int, int)
    
    # New detailed progress signals
    stage_progress = pyqtSignal(AnalysisProgress)  # Detailed progress info
    stage_changed = pyqtSignal(str, int, int)      # (stage_name, stage_num, total_stages)
    time_estimate = pyqtSignal(float, float)       # (elapsed, remaining)
```

#### Progress Callback Interface
```python
class ProgressCallback(Protocol):
    def on_stage_start(self, stage: AnalysisStage) -> None: ...
    def on_stage_progress(self, stage: AnalysisStage, progress: float) -> None: ...
    def on_stage_complete(self, stage: AnalysisStage) -> None: ...
```

### UI Component Design

#### Enhanced MainWindow Layout
```
┌─ Analysis Progress ────────────────────────┐
│ Files: [██████████        ] 3 of 8         │
│ Current: song.mp3                          │  
│                                            │
│ Stage: [████████          ] Detecting BPM  │
│ Time: 00:45 elapsed, ~02:30 remaining      │
│                                            │
│ [Cancel] [Pause] [Details]                 │
└────────────────────────────────────────────┘
```

**New UI Components**:
- `file_progress_bar`: Overall file completion
- `stage_progress_bar`: Current stage completion  
- `stage_label`: Current stage name
- `time_label`: Elapsed/remaining time display
- `current_file_label`: Current file being processed

### Modified Audio Processing Integration

#### Instrumented Analysis Functions
```python
def _analyze_with_librosa(path: str, progress_callback: ProgressCallback = None) -> Dict[str, object]:
    # Stage 1: Audio Loading
    if progress_callback:
        progress_callback.on_stage_start(AnalysisStage.AUDIO_LOADING)
    
    y, sr = librosa.load(path, sr=None, mono=True)
    
    if progress_callback:
        progress_callback.on_stage_complete(AnalysisStage.AUDIO_LOADING)
        progress_callback.on_stage_start(AnalysisStage.BPM_DETECTION)
    
    # Stage 2: BPM Detection (with internal progress if possible)
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
    
    # Continue for remaining stages...
```

### Time Estimation Algorithm

#### Weighted Stage Duration Tracking
```python
class TimeEstimator:
    def __init__(self):
        self.stage_durations: Dict[AnalysisStage, List[float]] = defaultdict(list)
        
    def record_stage_time(self, stage: AnalysisStage, duration: float):
        self.stage_durations[stage].append(duration)
        # Keep rolling window of last 10 measurements
        if len(self.stage_durations[stage]) > 10:
            self.stage_durations[stage].pop(0)
    
    def estimate_remaining(self, current_stage: AnalysisStage, 
                          stage_progress: float, 
                          remaining_files: int) -> float:
        # Calculate based on historical stage times + remaining files
        pass
```

## Constitution Check (Post-Design)
**Re-evaluation after detailed design**:

**Simplicity**: ✅ PASSED
- Still single project, no additional frameworks
- Extends existing patterns (QThread signals, callback interfaces)
- No unnecessary abstractions added

**Performance**: ✅ PASSED  
- Progress tracking adds minimal computational overhead
- No blocking operations in UI thread
- Time estimation uses lightweight calculations

**Maintainability**: ✅ PASSED
- Clear separation: progress tracking vs. analysis logic
- Testable components with defined interfaces
- Backward compatible (existing progress signal maintained)

✅ **Final Constitution Check: PASSED**

## Phase 2: Task Generation Approach

### Task Breakdown Strategy
**Sequential Implementation Approach**:
1. **Foundation**: Data models and core progress tracking logic
2. **Integration**: Modify existing AnalyzeWorker and audio processing  
3. **UI Enhancement**: Add progress components to MainWindow
4. **Refinement**: Time estimation and error handling
5. **Testing**: Unit tests for progress logic, integration tests for UI

**Task Granularity**: 
- Each task should be completable in 30-60 minutes
- Focus on incremental functionality (can test after each task)
- Maintain working state throughout development

**Testing Strategy**:
- Unit tests for AnalysisProgress calculations
- Mock-based tests for TimeEstimator
- Integration tests with actual audio files (small test files)
- UI tests using QTest framework

**Risk Mitigation**:
- Maintain backward compatibility with existing progress system
- Graceful degradation if progress tracking fails
- Comprehensive error handling for edge cases

---
*Ready for `/tasks` command to generate detailed implementation tasks*