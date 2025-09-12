# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Quick Start Commands

### Launch Application
```bash
# IMPORTANT: ALWAYS activate virtual environment first
source .venv/bin/activate

# Launch the PyQt6 Enhanced UI with tabs and full features (recommended)
python -m src.ui.enhanced_main_window

# OR launch basic UI
make ui
# OR directly:
./scripts/ui
```

### Testing
```bash
# IMPORTANT: ALWAYS activate virtual environment first
source .venv/bin/activate

# Run all tests using pytest
python -m pytest tests/

# Run specific test categories
python -m pytest tests/unit/           # Unit tests only  
python -m pytest tests/integration/   # Integration tests only

# Run with coverage
python -m pytest --cov=src tests/
```

### Development Setup
```bash
# Setup Python virtual environment (if needed)
cd spec-kit
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
pip install -e .

# Install specify CLI tool for SDD workflow
uvx --from git+https://github.com/github/spec-kit.git specify init
```

### BMAD-METHOD Integration
```bash
# Build agents and teams
cd BMAD-METHOD
npm run build
npm run build:agents
npm run build:teams

# Lint and format BMAD code
npm run lint
npm run format
npm run validate
```

## Project Architecture

This is a Music Analyzer Pro project that implements spec-driven development using SpecKit methodology. The project combines multiple frameworks:

### Core Components

**Main Application** (`src/`)
- **UI Layer**: PyQt6-based desktop interface (`src/ui/enhanced_main_window.py`) with tabs, background analysis threads and visualization support. Basic interface also available at (`src/ui/main_window.py`)
- **Audio Analysis**: Core audio processing using librosa (`src/lib/audio_processing.py`) with BPM, key detection, and HAMMS vector generation
- **Services**: Modular services for analysis (`src/services/analyzer.py`), storage, metadata handling, and compatibility suggestions
- **Models**: Data models for tracks (`src/models/track.py`), playlists, and HAMMS feature vectors (`src/models/hamms.py`)

**SpecKit Integration** (`spec-kit/`)
- Spec-driven development CLI tool with Python 3.11+ and typer/rich dependencies
- Templates for `/specify`, `/plan`, `/tasks` commands in POML format
- Constitution-based development guardrails in `memory/constitution.md`

**BMAD-METHOD** (`BMAD-METHOD/`)
- Node.js-based agile development methodology framework
- Agent orchestration tools and templates for structured development workflows
- Quality gates, checklists, and story templates for enhanced development process

### Key Architectural Patterns

**Audio Processing Pipeline**: Track → Analyzer → HAMMS Vector → Compatibility/Playlist Services
- Graceful fallbacks when audio libraries unavailable (returns placeholder data)
- Support for multiple audio formats: wav, mp3, flac, aac, ogg, m4a

**UI Architecture**: Enhanced main window with tabbed interface coordinates background analysis threads with progress tracking and cancellation support

**Service Layer**: Clean separation between analysis, storage, metadata extraction, and business logic (compatibility, playlists)

**Testing Strategy**: pytest-based with unit tests for core algorithms and integration tests for full analysis workflows

## Development Workflow Integration - ENHANCED

This project uses **Enhanced Spec-Driven Development** methodology with critical validation layers:

### **Phase 1: Specify + Input Validation**
- Use `/specify` command to define what and why (not tech stack)
- **NEW**: Define **data completeness requirements** explicitly
- **NEW**: Specify **input validation rules** and preconditions
- **NEW**: Document **failure scenarios** and edge cases

### **Phase 2: Plan + Defensive Architecture** 
- Use `/plan` command for technical architecture and implementation details
- **NEW**: Plan **input validation pipeline** as first-class component
- **NEW**: Design **fail-fast mechanisms** at each integration point
- **NEW**: Plan **configuration validation** between UI and backend

### **Phase 3: Tasks + Quality Gates**
- Use `/tasks` command to break down into actionable, parallelizable tasks
- **NEW**: Include **data validation tasks** as mandatory first steps
- **NEW**: Add **integration testing** with corrupted/incomplete data
- **NEW**: Include **end-to-end validation** tasks

### **Phase 4: Implementation + Continuous Validation**
- Build incrementally with continuous validation against specifications
- **NEW**: Implement **input validation BEFORE** business logic
- **NEW**: Add **runtime quality checks** and alarm systems
- **NEW**: Validate **UI state consistency** with backend logic

### **Enhanced BMAD-METHOD Integration**

**Quality Gates Enhanced:**
- **Gate 1**: Data Completeness Validation
- **Gate 2**: Input/Output Contract Verification  
- **Gate 3**: Configuration State Validation
- **Gate 4**: End-to-End Integration Testing
- **Gate 5**: Production Readiness Review

**Alarm Systems:**
- **Data Quality Alarms**: Incomplete/missing critical data
- **Configuration Drift Alarms**: UI vs backend inconsistencies
- **Business Logic Alarms**: Rule violations or unexpected results

## Critical Lessons Learned - BPM Tolerance Case Study

### **Root Cause Analysis**

**Problem**: Generated playlists violated user-specified 2% BPM tolerance, including tracks without calculated BPM values.

**Primary Failures Identified:**
1. **Input Validation Gap**: No validation of BPM data completeness before playlist generation
2. **Configuration Drift**: UI default value (8%) != user expectation (2%)
3. **Fallback Logic Flaw**: `cand_list = filtered or ranked` bypassed all filters when no matches found
4. **Testing Gap**: No integration testing with real incomplete data

### **Methodology Enhancements Applied**

**1. Defensive Programming Protocol**
```python
# BEFORE: Assumed data completeness
for c in candidates:
    score = calculate_score(c)

# AFTER: Validate input data first  
for c in candidates:
    if not c.get("bpm"):
        print(f"SKIPPING track without BPM: {c.get('path')}")
        continue
    score = calculate_score(c)
```

**2. Fail-Fast Input Validation**
```python
# NEW: Pre-flight validation
if not base_bpm:
    print(f"ERROR: Seed track has no BPM calculated")
    return []
```

**3. Post-Generation Quality Assurance**
```python
# NEW: Validation reporting
validation = validate_playlist_tolerance(playlist, tolerance)
if validation['violations'] > 0:
    print(f"❌ PLAYLIST FAILS BPM tolerance requirements!")
```

### **Mandatory Development Checklist**

**Before ANY implementation:**
- [ ] ✅ Validate all input data completeness
- [ ] ✅ Implement explicit preconditions  
- [ ] ✅ Test with corrupted/incomplete real data
- [ ] ✅ Verify UI configuration matches backend logic
- [ ] ✅ Implement runtime validation and alerts
- [ ] ✅ Add post-execution quality verification

**This case demonstrates why input validation and defensive programming are non-negotiable in production systems.**

## File Structure Context

- `src/`: Core Python application code with clear separation of concerns
- `tests/`: pytest test suite (8 test files) covering unit and integration scenarios
- `spec-kit/`: SpecKit CLI tool for structured development workflow
- `BMAD-METHOD/`: Node.js methodology framework with agents and templates
- `docs/`: Spanish documentation explaining BMAD integration with SpecKit
- `scripts/`: Utility scripts including UI launcher
- `poml_site/`: POML (Prompt Orchestration Markup Language) web interface

## Audio Analysis Capabilities

The application performs sophisticated music analysis including:
- BPM (tempo) detection using librosa beat tracking
- Musical key detection with confidence scoring
- Energy level analysis from spectral features
- HAMMS (12-dimensional harmonic feature vector) for similarity analysis
- Compatibility suggestions based on key relationships and BPM ranges
- Playlist generation with smooth transitions between tracks

## Technical Dependencies

**Python Stack**: PyQt6 (UI), librosa (audio), numpy (computation), pytest (testing)
**Node.js Stack**: Commander (CLI), chalk (output), fs-extra (filesystem), js-yaml (config)
**Development**: ESLint, Prettier, Husky (git hooks), semantic-release (versioning)

# Critical Development Reminders - Enhanced Methodology

## MANDATORY INPUT VALIDATION
- **ALWAYS** validate data completeness BEFORE processing
- **NEVER** assume upstream systems provide complete data  
- **IMPLEMENT** fail-fast mechanisms at integration boundaries
- **VALIDATE** UI configuration matches backend logic

## DEFENSIVE PROGRAMMING REQUIREMENTS
- **CHECK** for None/NULL values in all critical data fields
- **IMPLEMENT** explicit preconditions for all functions
- **ADD** runtime quality checks and validation reporting
- **PROVIDE** clear error messages for data quality issues

## TESTING REQUIREMENTS ENHANCED  
- **ALWAYS** test with incomplete/corrupted real data
- **VERIFY** end-to-end workflows with edge cases
- **TEST** configuration drift scenarios (UI vs backend)
- **IMPLEMENT** integration tests with realistic failure scenarios

## POST-IMPLEMENTATION VALIDATION
- **VERIFY** results meet specified requirements
- **IMPLEMENT** quality assurance reporting  
- **ADD** monitoring for configuration drift
- **PROVIDE** clear success/failure feedback to users

## Quality Gate Checklist
- [ ] ✅ Input data completeness validated
- [ ] ✅ Preconditions explicitly implemented
- [ ] ✅ Edge cases tested with real data
- [ ] ✅ UI/backend configuration verified
- [ ] ✅ Runtime validation implemented
- [ ] ✅ Post-execution quality checks added

# CRITICAL: Python Virtual Environment Requirements

## MANDATORY: Always Activate Virtual Environment

**BEFORE running ANY Python command, ALWAYS execute:**
```bash
source .venv/bin/activate
```

### Why This Is Critical:
- **zai-sdk** and other AI packages are installed ONLY in `.venv`
- Running without virtual environment = **AI features disabled**
- Recent incident: App launched without venv showed "No LLM providers configured"

### Virtual Environment Commands:
```bash
# Check if venv is active (should show (.venv) in prompt)
echo $VIRTUAL_ENV

# Activate virtual environment
source .venv/bin/activate

# Deactivate (if needed)
deactivate

# Install packages in venv
source .venv/bin/activate && pip install package_name
```

### All Python Operations Require Virtual Environment:
- ✅ `source .venv/bin/activate && python -m src.ui.enhanced_main_window`
- ✅ `source .venv/bin/activate && python -m pytest tests/`
- ✅ `source .venv/bin/activate && pip install zai-sdk`
- ❌ `python -m src.ui.enhanced_main_window` (will fail with AI disabled)

**This instruction overrides all previous Python command examples. NEVER run Python commands without activating the virtual environment first.**