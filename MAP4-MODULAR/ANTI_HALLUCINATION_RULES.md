# Anti-Hallucination Rules for LLMs

## 🛡️ Defense Mechanisms Against LLM Issues

### Rule 1: NO ASSUMPTIONS
```markdown
❌ NEVER ASSUME:
- Package versions
- File locations  
- Variable names
- Import statements
- Configuration values

✅ ALWAYS VERIFY:
- Check file exists: `ls -la [file]`
- Check import works: `python -c "import [module]"`
- Check variable value: `print([variable])`
```

### Rule 2: EXPLICIT EVERYTHING
```python
# ❌ BAD: Ambiguous
def process(data):
    return analyze(data)

# ✅ GOOD: Explicit
def process_audio_track(track_dict: dict) -> numpy.ndarray:
    """Process track_dict with keys: 'bpm', 'key', 'energy'"""
    return hamms_analyzer.calculate_vector(track_dict)
```

### Rule 3: IMMUTABLE CONSTANTS
```python
# constants_lock.py - NEVER CHANGE THESE
LOCKED_CONSTANTS = {
    'PROJECT_NAME': 'MAP4',
    'HAMMS_DIMENSIONS': 12,
    'BPM_MIN': 60,
    'BPM_MAX': 200,
    'DATABASE_NAME': 'map4.db'
}

def verify_constants():
    """Run this EVERY prompt"""
    assert HAMMS_DIMENSIONS == 12, "CRITICAL: Dimensions changed!"
```

### Rule 4: TYPE CONTRACTS
```python
from typing import TypedDict, Literal

class TrackData(TypedDict):
    """EXACT structure - no deviations"""
    bpm: float  # MUST be float
    key: str    # MUST be string
    energy: float  # MUST be 0.0-1.0

# Enforce types
def process(data: TrackData) -> None:
    assert 0 <= data['energy'] <= 1, "Energy out of range"
```

### Rule 5: CHECKSUM VALIDATION
```python
# After creating any file
import hashlib

def validate_file(filepath: str, expected_hash: str):
    """Ensure file wasn't corrupted/hallucinated"""
    with open(filepath, 'rb') as f:
        actual = hashlib.md5(f.read()).hexdigest()
    assert actual == expected_hash, f"File corrupted: {filepath}"
```

### Rule 6: BOUNDARY GUARDS
```python
# Prevent value drift
class BoundaryGuard:
    @staticmethod
    def check_bpm(bpm: float) -> float:
        if not 60 <= bpm <= 200:
            raise ValueError(f"BPM {bpm} outside valid range")
        return bpm
    
    @staticmethod
    def check_vector(vector: np.ndarray) -> np.ndarray:
        if len(vector) != 12:
            raise ValueError(f"Vector size {len(vector)}, must be 12")
        if not all(0 <= v <= 1 for v in vector):
            raise ValueError("Vector values must be normalized 0-1")
        return vector
```

### Rule 7: SEMANTIC MARKERS
```python
# Use unique markers LLM can't ignore
# 🚨 CRITICAL_START 🚨
DATABASE_PATH = "data/map4.db"  # NEVER CHANGE
# 🚨 CRITICAL_END 🚨

# 🔒 LOCKED_CODE_START 🔒
class HAMMSAnalyzer:  # DO NOT RENAME
    dimensions = 12   # DO NOT CHANGE
# 🔒 LOCKED_CODE_END 🔒
```

### Rule 8: VALIDATION GATES
```python
# validation_gates.py
def gate_1_foundation():
    """Must pass before Phase 2"""
    checks = {
        'venv_exists': os.path.exists('venv'),
        'db_exists': os.path.exists('data/map4.db'),
        'imports_work': can_import(['numpy', 'librosa']),
        'structure_valid': all(os.path.exists(d) for d in ['src', 'tests', 'data'])
    }
    
    if not all(checks.values()):
        print("❌ FAILED CHECKS:", [k for k,v in checks.items() if not v])
        raise SystemExit("Cannot proceed to Phase 2")
    print("✅ Gate 1 passed")
```

### Rule 9: CONTEXT INJECTION
```markdown
## EVERY PROMPT MUST START WITH:
System: MAP4 Music Analyzer
State: Building Phase 2
Dependencies: numpy, librosa, sqlalchemy ALREADY installed
Database: data/map4.db EXISTS
Class: HAMMSAnalyzer EXISTS with 12 dimensions
DO NOT: Create new project, change names, modify constants
```

### Rule 10: OUTPUT VERIFICATION
```python
# After EVERY code generation
def verify_output(expected, actual):
    """Ensure LLM didn't hallucinate"""
    checks = [
        ('line_count', abs(len(actual) - len(expected)) < 10),
        ('has_class', 'class HAMMSAnalyzer' in actual),
        ('has_imports', 'import numpy' in actual),
        ('no_hallucination', 'tensorflow' not in actual),  # We don't use TF
    ]
    
    failed = [name for name, passed in checks if not passed]
    if failed:
        raise ValueError(f"Output verification failed: {failed}")
```

## 🎯 Critical Success Factors

1. **NEVER trust LLM memory** - Always re-inject context
2. **VERIFY everything** - Test after each step
3. **LOCK critical values** - Use constants that can't change
4. **GUARD boundaries** - Validate all inputs/outputs
5. **MARK critical code** - Use visual markers
6. **GATE progress** - Don't proceed if previous step failed
7. **INJECT context** - Remind LLM of state constantly
8. **VERIFY output** - Check for hallucinations

## 🚨 Red Flags to Watch For

- LLM suddenly changes naming conventions
- New dependencies appear without being requested
- Dimension counts change (must always be 12)
- File paths become relative instead of absolute
- Configuration values drift from original
- Methods get renamed or signatures change
- New frameworks appear (TensorFlow, Django, etc.)
- Database schema modifications without request

## 💊 Recovery Protocol

If LLM starts hallucinating:
1. STOP immediately
2. Load last checkpoint
3. Re-inject full context
4. Use smaller prompt
5. Add more validation
6. Verify output manually

---
**Remember: LLMs have no memory. Every prompt is a fresh start. Defend accordingly.**