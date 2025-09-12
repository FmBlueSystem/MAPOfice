# BMAD Phase 1: BUILD - Consolidated Architecture Design

## Agent Instructions
This markdown file contains executable instructions for the architecture design agent. Execute each section in order.

---

## 🏗️ BUILD Phase Execution Plan

### Step 1: Analyze Current CLI Duplication
```bash
# Inventory all CLI files and their functionality
find . -maxdepth 1 -name "*cli*.py" -exec echo "=== {} ===" \; -exec head -20 {} \;

# Extract unique functionality from each CLI
grep -n "def main\|if __name__\|argparse\|click\|typer" playlist_cli_*.py simple_cli.py
```

### Step 2: Design Unified CLI Architecture
Create a single entry point that consolidates all CLI functionality:

**Architecture Requirements:**
1. **Single Entry Point**: `src/cli/unified_main.py`
2. **Command Structure**: Using Click/Typer for professional CLI
3. **Module Organization**: Separate commands into logical groups
4. **Configuration Management**: Unified config system
5. **Plugin Architecture**: Extensible command registration

**Proposed CLI Structure:**
```
map4 <command> <subcommand> [options]

Commands:
├── analyze
│   ├── track <file>     (single file analysis)
│   ├── library <path>   (batch analysis)
│   └── playlist <file>  (playlist analysis)
├── playlist
│   ├── create           (generate new playlist)
│   ├── optimize         (improve existing playlist)
│   └── export           (export to various formats)
├── provider
│   ├── list             (available LLM providers)
│   ├── configure        (setup provider credentials)
│   └── test             (validate provider connection)
└── bmad
    ├── certify          (run BMAD certification)
    ├── validate         (validate implementation)
    └── report           (generate compliance report)
```

### Step 3: Design Provider Factory Pattern
Eliminate the 7 duplicate provider files with a clean factory pattern:

**Factory Architecture:**
```python
# src/analysis/provider_factory.py
class LLMProviderFactory:
    _providers = {}
    
    @classmethod
    def register_provider(cls, name: str, provider_class):
        cls._providers[name] = provider_class
    
    @classmethod
    def create_provider(cls, name: str, **kwargs):
        if name not in cls._providers:
            raise ValueError(f"Unknown provider: {name}")
        return cls._providers[name](**kwargs)
    
    @classmethod
    def list_providers(cls):
        return list(cls._providers.keys())

# Auto-registration pattern
@register_provider("zai")
class ZAIProvider(BaseLLMProvider):
    pass

@register_provider("claude")  
class ClaudeProvider(BaseLLMProvider):
    pass
```

### Step 4: Create Implementation Files

#### 4a. Create Base Provider Interface
```python
# File: src/analysis/base_provider.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List

class BaseLLMProvider(ABC):
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._validate_config()
    
    @abstractmethod
    def _validate_config(self):
        """Validate provider-specific configuration"""
        pass
    
    @abstractmethod
    def analyze_track(self, track_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze single track and return enriched metadata"""
        pass
    
    @abstractmethod
    def batch_analyze(self, tracks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze multiple tracks efficiently"""
        pass
    
    @abstractmethod
    def test_connection(self) -> bool:
        """Test if provider is accessible and configured correctly"""
        pass
```

#### 4b. Create Unified CLI Entry Point
```python
# File: src/cli/unified_main.py
import click
from .commands import analyze, playlist, provider, bmad

@click.group()
@click.version_option()
def cli():
    """MAP4 - Music Analyzer Pro - Unified CLI Interface"""
    pass

# Register command groups
cli.add_command(analyze.analyze)
cli.add_command(playlist.playlist) 
cli.add_command(provider.provider)
cli.add_command(bmad.bmad)

if __name__ == '__main__':
    cli()
```

### Step 5: Create Migration Strategy

**File Migration Plan:**
1. **Preserve**: Keep one representative from each CLI variant
2. **Extract**: Pull unique functionality into unified commands
3. **Archive**: Move duplicates to `archive/` directory  
4. **Update**: Update all references to use unified entry point

**Files to Consolidate:**
- `playlist_cli_*.py` → `src/cli/commands/playlist.py`
- `simple_cli.py` → `src/cli/commands/analyze.py`
- `*provider*.py` → `src/analysis/providers/` + factory pattern
- `test_*provider*.py` → `tests/providers/test_provider_factory.py`

### Step 6: Create Configuration System
```yaml
# config/default.yaml
cli:
  default_provider: "zai"
  output_format: "json"
  verbose: false

providers:
  zai:
    api_key_env: "ZAI_API_KEY"
    base_url: "https://api.zai.com/v1"
    timeout: 30
  claude:
    api_key_env: "ANTHROPIC_API_KEY" 
    model: "claude-3-haiku-20240307"
    timeout: 30
  gemini:
    api_key_env: "GEMINI_API_KEY"
    model: "gemini-1.5-flash"
    timeout: 30

analysis:
  batch_size: 10
  retry_attempts: 3
  cache_results: true

bmad:
  certification_threshold: 0.95
  validation_strict: true
  report_format: "markdown"
```

### Step 7: Quality Assurance Checklist
- [ ] All CLI functionality preserved in unified interface
- [ ] Provider factory supports all existing providers  
- [ ] Configuration system handles all current settings
- [ ] Migration path documented for existing users
- [ ] Backward compatibility maintained where possible
- [ ] Test coverage plan for new architecture
- [ ] Performance benchmarks defined
- [ ] Documentation updated for unified CLI

---

## Expected Deliverables from BUILD Phase

1. **Architecture Documents**
   - `unified_cli_architecture.md`
   - `provider_factory_design.md` 
   - `configuration_system_spec.md`

2. **Implementation Blueprints**
   - `src/cli/unified_main.py` (skeleton)
   - `src/analysis/provider_factory.py` (interface)
   - `config/schema.yaml` (configuration definition)

3. **Migration Strategy**
   - `migration_plan.md`
   - `file_consolidation_map.md`
   - `backward_compatibility_matrix.md`

## Success Criteria for BUILD Phase
✅ **Architecture Approved**: Technical leadership sign-off on consolidated design
✅ **Interface Defined**: Clear API contracts for all components  
✅ **Migration Planned**: Step-by-step consolidation roadmap
✅ **Quality Gates Set**: Testing and validation requirements established
✅ **Configuration Unified**: Single source of truth for all settings

**Next Phase**: Proceed to `03-bmad-phase2-measure.md` for current state quantification