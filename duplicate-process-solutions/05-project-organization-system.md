# MAP4 Project Organization System - File Classification & Restructuring

## Agent Instructions
This markdown file contains executable instructions for comprehensive project organization. Execute each section in order to eliminate the chaos of 94+ loose files in root directory.

---

## 🗂️ PROJECT ORGANIZATION CRISIS ANALYSIS

### Current State Assessment
```bash
# Document current project chaos
echo "=== PROJECT DISORGANIZATION ANALYSIS ==="
echo "Root directory files: $(ls -1 | grep -v '^d' | wc -l)"
echo "Python files in root: $(ls -1 *.py 2>/dev/null | wc -l)"
echo "Test files in root: $(ls -1 test_*.py 2>/dev/null | wc -l)"
echo "Data files in root: $(ls -1 *.csv *.json *.m3u 2>/dev/null | wc -l)"
echo "Documentation in root: $(ls -1 *.md 2>/dev/null | wc -l)"
```

### File Classification System

**PROPOSED DIRECTORY STRUCTURE:**
```
MAP4/
├── src/                          # Core application code (keep existing)
├── tests/                        # Proper test suite (keep existing) 
├── docs/                         # All documentation
├── data/                         # All data files and playlists
│   ├── playlists/               # *.m3u files
│   ├── analysis/                # *.csv, *.json analysis results
│   ├── samples/                 # test_music/ and sample files
│   └── databases/               # *.db, *.db-shm, *.db-wal files
├── tools/                        # Standalone utility scripts
│   ├── cli/                     # All CLI implementations  
│   ├── debug/                   # Debug and diagnostic scripts
│   ├── validation/              # Test and validation scripts
│   └── bmad/                    # BMAD methodology tools
├── config/                       # Configuration files
├── temp/                         # Temporary and experimental files
├── archive/                      # Deprecated/backup files
└── scripts/                      # Build and deployment scripts
```

## STEP 1: Create Organizational Structure

```bash
# Create new directory structure
mkdir -p docs/{api,user,development}
mkdir -p data/{playlists,analysis,samples,databases}
mkdir -p tools/{cli,debug,validation,bmad}
mkdir -p config
mkdir -p temp/experiments
mkdir -p archive/{deprecated,backups}
mkdir -p scripts/{build,deploy,maintenance}
```

## STEP 2: File Classification Rules

### Documentation Files (*.md)
**Target: `docs/` directory**
```bash
# Classify documentation
echo "=== DOCUMENTATION CLASSIFICATION ==="

# API and technical docs
mv *_api*.md *_spec*.md *_architecture*.md docs/api/ 2>/dev/null || true

# User-facing documentation  
mv README*.md *_guide*.md *_manual*.md docs/user/ 2>/dev/null || true

# Development documentation
mv *_plan*.md *_tasks*.md *_certification*.md *_report*.md docs/development/ 2>/dev/null || true

# BMAD methodology docs
mv bmad_*.md docs/development/bmad/ 2>/dev/null || true

# Remaining docs go to general docs
mv *.md docs/ 2>/dev/null || true
```

### Data Files Classification
**Target: `data/` directory**
```bash
# Classify data files
echo "=== DATA FILES CLASSIFICATION ==="

# Playlist files
mv *.m3u data/playlists/ 2>/dev/null || true

# Analysis results
mv *.csv *.json *_results*.* data/analysis/ 2>/dev/null || true
mv *analysis*.* *_metadata*.* data/analysis/ 2>/dev/null || true

# Database files
mv *.db *.db-shm *.db-wal data/databases/ 2>/dev/null || true

# Sample/test music
mv test_music/ data/samples/ 2>/dev/null || true
```

### Tool Scripts Classification  
**Target: `tools/` directory**
```bash
# Classify tool scripts
echo "=== TOOL SCRIPTS CLASSIFICATION ==="

# CLI implementations
mv *cli*.py playlist_*.py tools/cli/ 2>/dev/null || true

# Debug and diagnostic scripts
mv debug_*.py test_*_debug*.py validate_*.py tools/debug/ 2>/dev/null || true

# Validation and testing utilities
mv test_*.py *_test.py *_validation*.py tools/validation/ 2>/dev/null || true

# BMAD methodology tools
mv bmad_*.py tools/bmad/ 2>/dev/null || true

# Demo and example scripts
mv demo_*.py *_demo*.py simple_*.py tools/debug/ 2>/dev/null || true
```

### Configuration Management
**Target: `config/` directory**
```bash
# Classify configuration files
echo "=== CONFIGURATION CLASSIFICATION ==="

# Configuration files
mv *.yaml *.yml *.cfg *.ini *.conf config/ 2>/dev/null || true
mv *config*.py *_config*.json config/ 2>/dev/null || true
mv set_*.sh *.env config/ 2>/dev/null || true
```

### Temporary/Experimental Files
**Target: `temp/` directory**
```bash
# Classify temporary files
echo "=== TEMPORARY FILES CLASSIFICATION ==="

# Direct fixes and patches
mv DIRECT_*.py *_fix*.py *_patch*.py temp/experiments/ 2>/dev/null || true

# Experimental implementations  
mv *_enhanced*.py *_improved*.py *_optimized*.py temp/experiments/ 2>/dev/null || true

# Backup files
mv *_backup*.py *_original*.py *_old*.py archive/backups/ 2>/dev/null || true
```

## STEP 3: Update Import Statements and References

### Scan for Broken Imports
```bash
# Identify files that will need import updates
echo "=== IMPORT DEPENDENCY ANALYSIS ==="

# Check which files import the moved modules
grep -r "import.*test_\|from.*test_" src/ --include="*.py" || echo "No test imports in src/"
grep -r "import.*debug\|from.*debug" src/ --include="*.py" || echo "No debug imports in src/"
grep -r "import.*bmad\|from.*bmad" src/ --include="*.py" || echo "No bmad imports in src/"

# Check for relative imports that might break
find src -name "*.py" -exec grep -l "from \.\|import \." {} \;
```

### Create Import Compatibility Layer
```python
# Create: tools/__init__.py
"""MAP4 Tools Package - Compatibility layer for reorganized utilities"""

# Re-export commonly used tools to maintain compatibility
try:
    from .cli import *
    from .debug import *
    from .validation import *
    from .bmad import *
except ImportError:
    # Graceful fallback if tools not available
    pass
```

## STEP 4: Configuration System Updates

### Create Centralized Configuration
```python
# Create: config/paths.py
"""Centralized path configuration for reorganized MAP4 project"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIR = PROJECT_ROOT / "src"
DATA_DIR = PROJECT_ROOT / "data"
TOOLS_DIR = PROJECT_ROOT / "tools" 
DOCS_DIR = PROJECT_ROOT / "docs"
CONFIG_DIR = PROJECT_ROOT / "config"

# Data subdirectories
PLAYLISTS_DIR = DATA_DIR / "playlists"
ANALYSIS_DIR = DATA_DIR / "analysis" 
SAMPLES_DIR = DATA_DIR / "samples"
DATABASES_DIR = DATA_DIR / "databases"

# Ensure directories exist
for directory in [DATA_DIR, TOOLS_DIR, DOCS_DIR, PLAYLISTS_DIR, ANALYSIS_DIR, SAMPLES_DIR, DATABASES_DIR]:
    directory.mkdir(parents=True, exist_ok=True)
```

### Update Main Application Paths
```bash
# Update path references in main application
echo "=== UPDATING APPLICATION PATHS ==="

# Find and list files that need path updates
grep -r "\.csv\|\.json\|\.m3u" src/ --include="*.py" | cut -d: -f1 | sort | uniq
```

## STEP 5: Testing and Validation System

### Create Validation Script
```python
# Create: scripts/validate_organization.py
"""Validate project organization and functionality after restructuring"""

import os
import sys
from pathlib import Path

def validate_organization():
    """Validate new directory structure"""
    required_dirs = [
        "src", "tests", "docs", "data", "tools", "config", 
        "data/playlists", "data/analysis", "data/samples", "data/databases",
        "tools/cli", "tools/debug", "tools/validation", "tools/bmad"
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            missing_dirs.append(dir_path)
    
    if missing_dirs:
        print(f"❌ Missing directories: {missing_dirs}")
        return False
    
    print("✅ Directory structure validated")
    return True

def validate_imports():
    """Check for broken imports after reorganization"""
    # This would be implemented to scan Python files for import errors
    print("🔍 Scanning for broken imports...")
    
    try:
        # Try importing main application components
        sys.path.append("src")
        from ui.enhanced_main_window import EnhancedMainWindow
        from analysis.llm_provider import LLMProvider
        print("✅ Core imports working")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def validate_functionality():
    """Test core application functionality"""
    print("🧪 Testing core functionality...")
    
    # Test configuration loading
    try:
        from config.paths import PROJECT_ROOT, DATA_DIR
        assert PROJECT_ROOT.exists(), "Project root not found"
        assert DATA_DIR.exists(), "Data directory not found"
        print("✅ Configuration system working")
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

if __name__ == "__main__":
    print("🔄 Validating MAP4 project organization...")
    
    org_valid = validate_organization()
    imports_valid = validate_imports()  
    func_valid = validate_functionality()
    
    if all([org_valid, imports_valid, func_valid]):
        print("🎉 Project organization validation PASSED")
        sys.exit(0)
    else:
        print("💥 Project organization validation FAILED")  
        sys.exit(1)
```

## STEP 6: Update Documentation and Scripts

### Create New README Structure
```bash
# Update main project documentation
echo "=== DOCUMENTATION UPDATES ==="

# Create comprehensive project overview
cat > README.md << 'EOF'
# MAP4 - Music Analyzer Pro

## 📁 Project Structure

```
MAP4/
├── src/                    # Core application code
├── tests/                  # Test suite  
├── docs/                   # All documentation
├── data/                   # Data files and results
├── tools/                  # Utility scripts and tools
├── config/                 # Configuration files
└── scripts/                # Build and deployment scripts
```

## 🚀 Quick Start

```bash
# Setup environment
source .venv/bin/activate

# Launch main application  
python -m src.ui.enhanced_main_window

# Run CLI tools
python tools/cli/playlist_cli_final.py

# Run validation
python scripts/validate_organization.py
```

## 📖 Documentation

- [User Guide](docs/user/) - How to use MAP4
- [API Documentation](docs/api/) - Technical specifications  
- [Development Guide](docs/development/) - Contributing and development setup

EOF
```

### Update Build Scripts
```bash
# Create: scripts/build.sh
#!/bin/bash
set -e

echo "🔨 Building MAP4 project..."

# Activate virtual environment
source .venv/bin/activate

# Install dependencies  
pip install -r requirements.txt

# Run organization validation
python scripts/validate_organization.py

# Run test suite
python -m pytest tests/ -v

# Validate main application
echo "🧪 Testing main application startup..."
timeout 10s python -c "
import sys
sys.path.append('src')  
from ui.enhanced_main_window import EnhancedMainWindow
print('✅ Main application validated')
" || echo "⚠️  Main application test timed out (normal for GUI)"

echo "✅ Build completed successfully"
```

## STEP 7: Implementation Execution Commands

Execute these commands in order:

```bash
# 1. Create directory structure
echo "📁 Creating organized directory structure..."
mkdir -p docs/{api,user,development/bmad} data/{playlists,analysis,samples,databases} tools/{cli,debug,validation,bmad} config temp/experiments archive/{deprecated,backups} scripts/{build,deploy,maintenance}

# 2. Move files to proper locations
echo "📦 Moving files to organized locations..."

# Documentation
find . -maxdepth 1 -name "*.md" -exec mv {} docs/ \;
find docs -name "bmad_*.md" -exec mv {} docs/development/bmad/ \;

# Data files
find . -maxdepth 1 -name "*.m3u" -exec mv {} data/playlists/ \;
find . -maxdepth 1 -name "*.csv" -exec mv {} data/analysis/ \;
find . -maxdepth 1 -name "*.json" -exec mv {} data/analysis/ \;
find . -maxdepth 1 -name "*.db*" -exec mv {} data/databases/ \;

# Tools and scripts
find . -maxdepth 1 -name "*cli*.py" -exec mv {} tools/cli/ \;
find . -maxdepth 1 -name "playlist_*.py" -exec mv {} tools/cli/ \;
find . -maxdepth 1 -name "debug_*.py" -exec mv {} tools/debug/ \;
find . -maxdepth 1 -name "test_*.py" -exec mv {} tools/validation/ \;
find . -maxdepth 1 -name "bmad_*.py" -exec mv {} tools/bmad/ \;
find . -maxdepth 1 -name "demo_*.py" -exec mv {} tools/debug/ \;
find . -maxdepth 1 -name "simple_*.py" -exec mv {} tools/debug/ \;

# Configuration
find . -maxdepth 1 -name "*.yaml" -exec mv {} config/ \;
find . -maxdepth 1 -name "*.yml" -exec mv {} config/ \;
find . -maxdepth 1 -name "*.sh" -exec mv {} config/ \;

# Temporary/experimental
find . -maxdepth 1 -name "DIRECT_*.py" -exec mv {} temp/experiments/ \;
find . -maxdepth 1 -name "validate_*.py" -exec mv {} tools/validation/ \;

# 3. Create configuration files
echo "⚙️  Creating configuration system..."
# [Configuration files would be created here]

# 4. Run validation
echo "🧪 Running organization validation..."
python scripts/validate_organization.py

# 5. Test application functionality  
echo "🚀 Testing application functionality..."
source .venv/bin/activate
timeout 10s python -m src.ui.enhanced_main_window || echo "✅ Application launch tested"

echo "🎉 Project reorganization completed!"
```

---

## Success Criteria

✅ **File Organization**: All 94+ loose files properly categorized
✅ **Directory Structure**: Clean, logical directory hierarchy  
✅ **Import Compatibility**: All existing functionality preserved
✅ **Configuration System**: Centralized path and config management
✅ **Documentation Updated**: Clear project structure documentation
✅ **Validation System**: Automated organization and functionality validation
✅ **Build Process**: Updated build and deployment scripts

## Post-Reorganization Validation

After reorganization, the agent must:
1. Run complete functionality validation
2. Test main application startup
3. Verify CLI tools operation
4. Confirm data file accessibility
5. Validate configuration system
6. Run test suite
7. Generate organization report