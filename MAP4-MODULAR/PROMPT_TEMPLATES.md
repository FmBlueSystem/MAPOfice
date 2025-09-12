# Optimized Prompt Templates for LLMs

## 🎯 Template 1: Context-First Prompt
```markdown
## CONTEXT INJECTION
Project: MAP4 | Phase: [X] | Step: [Y]
Previous: [LAST_FILE_CREATED]
Constants: HAMMS=12 dimensions, DB=map4.db
Working Dir: ~/MAP4 (venv activated)

## TASK
[Specific task in <50 words]

## CODE TO ADD
```python
# File: [exact/path/to/file.py]
# After line: [X]
[Max 100 lines of code]
```

## VALIDATE
- [ ] File exists at [path]
- [ ] Import [module] works
- [ ] [Specific test command]

## CHECKPOINT
Save: {"step": "[X.Y]", "created": "[file]"}
```

## 🎯 Template 2: Incremental Addition
```markdown
## DO NOT CREATE NEW FILES
## ADD TO: src/existing/file.py

## CURRENT STATE
```python
class ExistingClass:
    def existing_method(self):
        pass
    # INSERT NEW METHOD HERE
```

## ADD THIS METHOD ONLY
```python
    def new_method(self):
        """Single purpose"""
        return True
```

## TEST
python -c "from src.existing.file import ExistingClass; e=ExistingClass(); print(e.new_method())"
```

## 🎯 Template 3: Validation-Heavy Prompt
```markdown
## PRE-VALIDATION
```bash
ls -la src/  # Must show: analysis/ models/ services/
python -c "import numpy; print(numpy.__version__)"  # Must work
cat data/map4.db  # Must exist
```

## TASK
[Task description]

## POST-VALIDATION
```python
# validation.py
assert os.path.exists('NEW_FILE')
assert 'HAMMSAnalyzer' in open('NEW_FILE').read()
assert dimensions == 12
print("✅ All validations passed")
```
```

## 🎯 Template 4: Recovery Prompt
```markdown
## ERROR RECOVERY
Last Error: [ERROR_MESSAGE]
Failed at: Step [X.Y]

## DIAGNOSIS
```bash
pwd  # Check directory
ls -la  # Check files
pip list | grep [package]  # Check dependencies
```

## FIX
[Specific fix instructions <50 lines]

## VERIFY FIX
[Test command to confirm fix worked]

## RESUME FROM
Continue with: [NEXT_STEP]
```

## 🎯 Template 5: State Machine Prompt
```markdown
## STATE MACHINE
Current State: [STATE_NAME]
Valid Transitions: [STATE_A, STATE_B]
Invalid States: [STATE_X, STATE_Y]

## TRANSITION TO: [NEXT_STATE]
Requirements:
- [ ] Condition 1 met
- [ ] Condition 2 met

## ACTION
[Specific action for state transition]

## NEW STATE VALIDATION
```python
assert current_state == '[NEXT_STATE]'
assert previous_state == '[STATE_NAME]'
```
```

## 🔥 Power Patterns

### Pattern 1: Three-Line Context
```markdown
WHAT: Building MAP4 analyzer with 12-D HAMMS vectors
WHERE: ~/MAP4/src/analysis/hamms_base.py exists
NEXT: Add calculate_similarity method
```

### Pattern 2: Diff-Style Changes
```diff
# src/models/track.py
class Track:
    def __init__(self):
        self.bpm = None
+       self.energy = None  # ADD THIS LINE
+       self.key = None     # ADD THIS LINE
```

### Pattern 3: Contract-First
```python
# CONTRACT: This function signature CANNOT change
def analyze_track(filepath: str) -> dict:
    """
    Args:
        filepath: Absolute path to audio file
    Returns:
        dict with keys: 'bpm', 'key', 'energy', 'hamms_vector'
    """
    # Implementation here
```

### Pattern 4: Checkpoint Chains
```markdown
✅ Checkpoint 2.1: HAMMSAnalyzer class created
✅ Checkpoint 2.2: 12 dimensions confirmed
⏳ Checkpoint 2.3: Add calculation methods <- YOU ARE HERE
⏹ Checkpoint 2.4: Add validation
⏹ Checkpoint 2.5: Add tests
```

## 🛡️ Defensive Patterns

### Guard Pattern
```python
# GUARD: Prevent dimension drift
if self.dimensions != 12:
    raise RuntimeError(f"CRITICAL: Dimensions changed to {self.dimensions}")
```

### Lock Pattern
```python
# LOCK: These values are immutable
@property
def dimensions(self):
    return 12  # Cannot be changed

@dimensions.setter
def dimensions(self, value):
    raise AttributeError("Dimensions are locked at 12")
```

### Assertion Pattern
```python
# Every method starts with assertions
def process(self, data):
    assert isinstance(data, dict), "Data must be dict"
    assert 'bpm' in data, "BPM required"
    assert 60 <= data['bpm'] <= 200, "BPM out of range"
    # Now safe to process
```

## 📊 Optimal Prompt Sizes

| Type | Lines | Tokens | Success Rate |
|------|-------|--------|--------------|
| Context injection | 10-20 | 200-400 | 95% |
| Code addition | 50-100 | 1000-2000 | 90% |
| Validation | 20-30 | 400-600 | 95% |
| Full prompt | <200 | <3000 | 85% |

## ⚡ Quick Templates

### One-Liner Additions
```markdown
ADD to config.py: `CACHE_DIR = "data/cache"`
```

### Simple Test
```markdown
TEST: `python -c "from src.models.track import Track; t=Track(); print('OK')"`
```

### Quick Validation
```markdown
CHECK: File exists? `ls -la [FILE]` → Expected: [FILE] shown
```

---
**Remember: Shorter prompts = Better results = Less hallucination**