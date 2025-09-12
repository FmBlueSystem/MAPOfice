# Memory System for LLM Consistency

## 1. Context Injection Headers
Every prompt must start with:

```markdown
## CONTEXT RECALL
Project: MAP4 Music Analyzer
Language: Python 3.8+
Framework: PyQt6 + SQLAlchemy
Current Phase: [PHASE_NAME]
Previous Output: [LAST_CREATED_FILE]
Working Dir: ~/MAP4
Venv Active: YES
```

## 2. Variable Persistence File
Create `memory.json` that persists between prompts:

```json
{
  "constants": {
    "PROJECT_NAME": "MAP4",
    "PYTHON_VERSION": "3.8",
    "DB_PATH": "data/map4.db",
    "MAIN_CLASS": "HAMMSAnalyzer"
  },
  "last_created": {
    "file": "src/analysis/hamms_base.py",
    "class": "HAMMSAnalyzer",
    "methods": ["create_vector", "normalize_bpm"]
  },
  "naming_conventions": {
    "files": "snake_case",
    "classes": "PascalCase",
    "functions": "snake_case",
    "constants": "UPPER_CASE"
  },
  "imports_available": [
    "numpy",
    "librosa",
    "sqlalchemy",
    "click"
  ]
}
```

## 3. Validation Anchors
Each prompt ends with validation that prevents drift:

```python
# VALIDATE: Must match these EXACT values
assert PROJECT_NAME == "MAP4"
assert os.path.exists("data/map4.db")
assert HAMMSAnalyzer.dimensions == 12
```

## 4. Code Signature Blocks
Prevent hallucination with explicit signatures:

```python
# SIGNATURE: DO NOT MODIFY
class HAMMSAnalyzer:  # <-- EXACT NAME
    def __init__(self):
        self.dimensions = 12  # <-- MUST BE 12
        self.weights = WEIGHTS  # <-- FROM hamms_constants.py
```

## 5. Incremental Code Addition
Never show full code, only additions:

```markdown
## ADD TO EXISTING FILE: src/analysis/hamms_base.py
## AFTER LINE: 25
## ADD THIS METHOD:
def new_method(self):
    return True
## END ADDITION
```

## 6. Checkpoint Verification Questions
Force LLM to confirm understanding:

```markdown
## CONFIRM BEFORE PROCEEDING:
1. What is the main class name? [Expected: HAMMSAnalyzer]
2. How many dimensions? [Expected: 12]
3. Database location? [Expected: data/map4.db]
```

## 7. Error Recovery Templates
Pre-defined recovery for common issues:

```markdown
## IF ERROR: "Import not found"
CHECK: Is venv activated? Run: source venv/bin/activate
CHECK: Package installed? Run: pip list | grep [package]
FIX: pip install [package]

## IF ERROR: "File not found"
CHECK: Working directory? Run: pwd
CHECK: File exists? Run: ls -la [path]
FIX: cd ~/MAP4
```

## 8. State Lock File
Prevent configuration drift:

```json
// state.lock
{
  "locked_values": {
    "hamms_dimensions": 12,
    "camelot_wheel_size": 24,
    "max_bpm": 200,
    "min_bpm": 60
  },
  "immutable": true,
  "error_if_changed": true
}
```

## 9. Breadcrumb Trail
Track execution path:

```json
// breadcrumbs.json
{
  "trail": [
    {"step": 1, "prompt": "01.1", "success": true, "timestamp": "10:00"},
    {"step": 2, "prompt": "01.2", "success": true, "timestamp": "10:05"},
    {"step": 3, "prompt": "01.3", "success": false, "error": "missing dep"},
    {"step": 4, "prompt": "01.3", "success": true, "timestamp": "10:08"}
  ]
}
```

## 10. Semantic Anchors
Use unique markers that LLM won't forget:

```python
# 🎵 MUSIC_ANALYZER_START 🎵
class HAMMSAnalyzer:
    # 🔢 TWELVE_DIMENSIONS 🔢
    dimensions = 12
    
    # 🎹 CAMELOT_WHEEL 🎹
    camelot = CAMELOT_WHEEL
# 🎵 MUSIC_ANALYZER_END 🎵
```