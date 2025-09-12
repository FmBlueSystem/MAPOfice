# MAP4 CLI Migration Guide

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
