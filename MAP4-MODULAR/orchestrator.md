# MAP4 Build Orchestrator

## Session Management System

### Initialize Session
```python
# Create this file: build_session.py
import json
import os
from datetime import datetime

class BuildSession:
    def __init__(self):
        self.checkpoint_dir = "checkpoints"
        os.makedirs(self.checkpoint_dir, exist_ok=True)
        self.status_file = f"{self.checkpoint_dir}/status.json"
        self.memory_file = f"{self.checkpoint_dir}/memory.json"
        self.load_or_create()
    
    def load_or_create(self):
        if os.path.exists(self.status_file):
            with open(self.status_file, 'r') as f:
                self.status = json.load(f)
        else:
            self.status = {
                "session_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
                "started": datetime.now().isoformat(),
                "current_prompt": "01.1-python-setup.md",
                "completed": [],
                "failed": [],
                "warnings": [],
                "variables": {}
            }
            self.save()
    
    def checkpoint(self, prompt_id, success=True, output=None):
        if success:
            self.status["completed"].append(prompt_id)
        else:
            self.status["failed"].append(prompt_id)
        
        if output:
            self.status["variables"][prompt_id] = output
        
        self.status["last_checkpoint"] = datetime.now().isoformat()
        self.save()
    
    def save(self):
        with open(self.status_file, 'w') as f:
            json.dump(self.status, f, indent=2)

# Initialize
session = BuildSession()
print(f"Session: {session.status['session_id']}")
print(f"Ready to start with: {session.status['current_prompt']}")
```

### Validate & Run
```bash
python build_session.py
```

## Execution Order

### Phase 1: Foundation [5 prompts, ~10k tokens total]
| Order | Prompt | Tokens | Time |
|-------|--------|--------|------|
| 1.1 | 01.1-python-setup.md | 2000 | 5 min |
| 1.2 | 01.2-dependencies.md | 2000 | 5 min |
| 1.3 | 01.3-structure.md | 1500 | 3 min |
| 1.4 | 01.4-database.md | 2500 | 5 min |
| 1.5 | 01.5-validation.md | 2000 | 5 min |

**Checkpoint: Foundation Complete ✓**

### Phase 2: Core System [15 prompts, ~35k tokens total]
| Order | Component | Prompts | Tokens |
|-------|-----------|---------|--------|
| 2.1-2.5 | HAMMS Engine | 5 | 10k |
| 2.6-2.8 | LLM Integration | 3 | 7k |
| 2.9-2.11 | UI Development | 3 | 8k |
| 2.12-2.13 | CLI System | 2 | 5k |
| 2.14-2.15 | Testing | 2 | 5k |

**Checkpoint: Core Complete ✓**

### Phase 3: Features [20 prompts, ~40k tokens total]
| Order | Feature | Prompts | Priority |
|-------|---------|---------|----------|
| 3.1-3.4 | Export System | 4 | CRITICAL |
| 3.5-3.8 | Batch Processing | 4 | CRITICAL |
| 3.9-3.12 | Search & Cache | 4 | HIGH |
| 3.13-3.16 | Analysis Tools | 4 | MEDIUM |
| 3.17-3.20 | Optimization | 4 | LOW |

**Checkpoint: Features Complete ✓**

## Recovery Procedures

### If prompt fails:
```python
# Check last successful checkpoint
with open('checkpoints/status.json', 'r') as f:
    status = json.load(f)
    print(f"Last success: {status['completed'][-1]}")
    print(f"Failed at: {status['failed'][-1]}")

# Resume from last good state
next_prompt = status['current_prompt']
```

### If context lost:
```python
# Load memory context
with open('checkpoints/memory.json', 'r') as f:
    memory = json.load(f)
    print("Available context:", memory.keys())
```

## State Persistence

### After each prompt completion:
```json
{
  "checkpoint": "01.2",
  "action": "save",
  "data": {
    "files_created": ["requirements.txt"],
    "variables": {
      "project_root": "/home/user/MAP4",
      "venv_path": "/home/user/MAP4/venv"
    }
  }
}
```

## Token Budget Management

| Phase | Budget | Actual | Remaining |
|-------|--------|--------|-----------|
| Foundation | 10k | 0 | 10k |
| Core | 35k | 0 | 35k |
| Features | 40k | 0 | 40k |
| **Total** | **85k** | **0** | **85k** |

## Success Criteria

- [ ] All checkpoints passed
- [ ] Total tokens < 100k
- [ ] No prompt > 3000 tokens
- [ ] Recovery possible from any point
- [ ] Complete in < 8 hours

## Next Step

**Execute: `01-foundation/01.1-python-setup.md`**

---
*Orchestrator v1.0 | Max tokens: 2000 | Checkpoints: Enabled*