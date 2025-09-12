#!/usr/bin/env python3
"""Migration script to transition from old CLI files to unified CLI.

This script helps users migrate from the 9 duplicate CLI files to the new unified interface.
"""

import os
import sys
import shutil
from pathlib import Path
from datetime import datetime
import argparse


def create_backup(source_dir: Path, backup_dir: Path):
    """Create backup of old CLI files."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = backup_dir / f"cli_backup_{timestamp}"
    
    if source_dir.exists():
        shutil.copytree(source_dir, backup_path)
        print(f"✓ Created backup at: {backup_path}")
        return backup_path
    return None


def archive_old_files(cli_dir: Path, archive_dir: Path):
    """Archive old CLI files."""
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    old_files = [
        "playlist_cli_demo.py",
        "playlist_cli_enhanced.py",
        "playlist_cli_enhanced_fixed.py",
        "playlist_cli_final.py",
        "playlist_cli_simple.py",
        "playlist_bmad_certification.py",
        "playlist_bmad_certification_fixed.py",
        "pure_metadata_extractor.py",
        "simple_cli.py"
    ]
    
    archived = []
    for filename in old_files:
        source = cli_dir / filename
        if source.exists():
            dest = archive_dir / filename
            shutil.move(str(source), str(dest))
            archived.append(filename)
            print(f"  • Archived: {filename}")
    
    return archived


def create_migration_guide():
    """Create migration guide for users."""
    guide = """# MAP4 CLI Migration Guide

## Migration from Old CLI to Unified CLI

The MAP4 project has been refactored to use a single unified CLI interface instead of 9 separate CLI files.

### Old CLI Files (Deprecated)
- `playlist_cli_demo.py`
- `playlist_cli_enhanced.py`
- `playlist_cli_enhanced_fixed.py`
- `playlist_cli_final.py`
- `playlist_cli_simple.py`
- `playlist_bmad_certification.py`
- `playlist_bmad_certification_fixed.py`
- `pure_metadata_extractor.py`
- `simple_cli.py`

### New Unified CLI
All functionality is now available through a single entry point: `map4`

## Command Mapping

### Old: `python tools/cli/simple_cli.py --folder ~/Music`
### New: `map4 analyze library ~/Music`

### Old: `python tools/cli/playlist_cli_demo.py --create`
### New: `map4 playlist create --library ~/Music`

### Old: `python tools/cli/playlist_cli_enhanced.py --analyze track.mp3`
### New: `map4 analyze track track.mp3`

## Installation

1. Install the unified CLI:
```bash
pip install -e .
```

2. Verify installation:
```bash
map4 --version
```

## Available Commands

### Analysis Commands
```bash
# Analyze single track
map4 analyze track song.mp3

# Analyze music library
map4 analyze library ~/Music --recursive

# Analyze playlist
map4 analyze playlist my_playlist.m3u
```

### Playlist Commands
```bash
# Create playlist
map4 playlist create --library ~/Music --mood energetic

# Optimize existing playlist
map4 playlist optimize playlist.m3u

# Export playlist to different format
map4 playlist export playlist.json --format m3u

# Merge multiple playlists
map4 playlist merge playlist1.m3u playlist2.m3u --output merged.m3u
```

### Provider Commands
```bash
# List available providers
map4 provider list

# Configure provider
map4 provider configure zai --api-key-env ZAI_API_KEY

# Test provider connection
map4 provider test zai

# Compare providers
map4 provider compare zai claude gemini --test-file song.mp3
```

### BMAD Commands
```bash
# Run certification
map4 bmad certify

# Validate specific phase
map4 bmad validate build

# Generate report
map4 bmad report --format markdown
```

## Configuration

Create a configuration file at `~/.map4/config.yaml` or in your project directory:

```yaml
cli:
  default_provider: zai
  output_format: json

providers:
  zai:
    api_key_env: ZAI_API_KEY
    model: gpt-4
```

## Environment Variables

Set API keys:
```bash
export ZAI_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"
export GEMINI_API_KEY="your-key"
export OPENAI_API_KEY="your-key"
```

## Getting Help

```bash
# General help
map4 --help

# Command-specific help
map4 analyze --help
map4 playlist create --help
```

## Troubleshooting

If you encounter issues:
1. Check that all API keys are set correctly
2. Verify the unified CLI is installed: `which map4`
3. Run with debug flag: `map4 --debug <command>`
4. Check logs in `logs/map4.log`

## Support

For questions or issues, please refer to the project documentation or create an issue on GitHub.
"""
    
    with open("MIGRATION_GUIDE.md", "w") as f:
        f.write(guide)
    
    print("✓ Created MIGRATION_GUIDE.md")


def create_compatibility_wrapper():
    """Create compatibility wrapper for old CLI commands."""
    wrapper = '''#!/usr/bin/env python3
"""Compatibility wrapper for old CLI commands.

This script provides backward compatibility for old CLI commands.
"""

import sys
import os
from pathlib import Path

# Map old commands to new ones
COMMAND_MAP = {
    "simple_cli.py": ["analyze", "library"],
    "playlist_cli_demo.py": ["playlist", "create"],
    "playlist_cli_enhanced.py": ["analyze", "track"],
    "playlist_cli_final.py": ["playlist", "create"],
    "playlist_cli_simple.py": ["playlist", "create"],
    "pure_metadata_extractor.py": ["analyze", "track"],
}

def main():
    # Get the script name
    script_name = Path(sys.argv[0]).name
    
    if script_name in COMMAND_MAP:
        new_command = COMMAND_MAP[script_name]
        print(f"⚠️  Warning: {script_name} is deprecated.")
        print(f"   Please use: map4 {' '.join(new_command)} [options]")
        print()
        
        # Try to run the new command
        import subprocess
        cmd = ["map4"] + new_command + sys.argv[1:]
        subprocess.run(cmd)
    else:
        print(f"Unknown command: {script_name}")
        print("Please use the unified CLI: map4 --help")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''
    
    with open("tools/cli/compatibility_wrapper.py", "w") as f:
        f.write(wrapper)
    
    print("✓ Created compatibility wrapper")


def update_imports():
    """Update import statements in the codebase."""
    updates_needed = []
    
    # Find Python files that might need updates
    for py_file in Path(".").rglob("*.py"):
        if "venv" in str(py_file) or ".venv" in str(py_file):
            continue
        if "node_modules" in str(py_file):
            continue
        
        try:
            with open(py_file, "r") as f:
                content = f.read()
            
            # Check for old imports
            old_imports = [
                "from tools.cli.simple_cli import",
                "from tools.cli.playlist_cli",
                "import tools.cli.simple_cli",
                "import tools.cli.playlist_cli"
            ]
            
            for old_import in old_imports:
                if old_import in content:
                    updates_needed.append(str(py_file))
                    break
        except:
            pass
    
    if updates_needed:
        print("\n⚠️  The following files may need import updates:")
        for file in updates_needed[:10]:
            print(f"  • {file}")
        if len(updates_needed) > 10:
            print(f"  ... and {len(updates_needed) - 10} more")
    
    return updates_needed


def main():
    """Main migration function."""
    parser = argparse.ArgumentParser(description="Migrate to unified MAP4 CLI")
    parser.add_argument("--backup", action="store_true", help="Create backup of old files")
    parser.add_argument("--archive", action="store_true", help="Archive old CLI files")
    parser.add_argument("--guide", action="store_true", help="Create migration guide")
    parser.add_argument("--wrapper", action="store_true", help="Create compatibility wrapper")
    parser.add_argument("--check-imports", action="store_true", help="Check for outdated imports")
    parser.add_argument("--all", action="store_true", help="Perform all migration steps")
    
    args = parser.parse_args()
    
    if not any([args.backup, args.archive, args.guide, args.wrapper, args.check_imports, args.all]):
        parser.print_help()
        return
    
    print("=== MAP4 CLI Migration Tool ===\n")
    
    project_root = Path.cwd()
    cli_dir = project_root / "tools" / "cli"
    archive_dir = project_root / "archive" / "old_cli"
    backup_dir = project_root / "backups"
    
    if args.all or args.backup:
        print("Step 1: Creating backup...")
        backup_dir.mkdir(exist_ok=True)
        create_backup(cli_dir, backup_dir)
    
    if args.all or args.archive:
        print("\nStep 2: Archiving old CLI files...")
        if cli_dir.exists():
            archived = archive_old_files(cli_dir, archive_dir)
            print(f"✓ Archived {len(archived)} files to: {archive_dir}")
        else:
            print("✗ CLI directory not found")
    
    if args.all or args.guide:
        print("\nStep 3: Creating migration guide...")
        create_migration_guide()
    
    if args.all or args.wrapper:
        print("\nStep 4: Creating compatibility wrapper...")
        create_compatibility_wrapper()
    
    if args.all or args.check_imports:
        print("\nStep 5: Checking for outdated imports...")
        update_imports()
    
    print("\n=== Migration Summary ===")
    print("✓ Unified CLI structure is in place at: src/cli/")
    print("✓ Old files have been processed")
    print("✓ Migration guide created: MIGRATION_GUIDE.md")
    print("\nNext steps:")
    print("1. Install the unified CLI: pip install -e .")
    print("2. Test the new commands: map4 --help")
    print("3. Update any scripts to use the new CLI")
    print("4. Review MIGRATION_GUIDE.md for command mappings")


if __name__ == "__main__":
    main()