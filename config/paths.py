"""Centralized path configuration for reorganized MAP4 project"""

from pathlib import Path
import os

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

# Tools subdirectories
CLI_TOOLS_DIR = TOOLS_DIR / "cli"
DEBUG_TOOLS_DIR = TOOLS_DIR / "debug"
VALIDATION_TOOLS_DIR = TOOLS_DIR / "validation"
BMAD_TOOLS_DIR = TOOLS_DIR / "bmad"

# Ensure critical directories exist
for directory in [DATA_DIR, PLAYLISTS_DIR, ANALYSIS_DIR, SAMPLES_DIR, DATABASES_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

def get_data_file(filename: str, subdir: str = None) -> Path:
    """Get path to data file with optional subdirectory"""
    if subdir:
        return DATA_DIR / subdir / filename
    return DATA_DIR / filename

def get_config_file(filename: str) -> Path:
    """Get path to configuration file"""
    return CONFIG_DIR / filename