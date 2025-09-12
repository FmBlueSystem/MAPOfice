# MAP4 - Music Analyzer Pro

## 📁 Organized Project Structure

```
MAP4/
├── src/                    # Core application code
│   ├── ui/                # User interface components
│   ├── analysis/          # Music analysis and LLM providers
│   ├── services/          # Business logic services
│   └── models/           # Data models
├── tests/                 # Test suite
├── docs/                  # All documentation
│   ├── api/              # API documentation
│   ├── user/             # User guides
│   └── development/      # Development docs and BMAD methodology
├── data/                  # Data files and results
│   ├── playlists/        # Music playlists (*.m3u)
│   ├── analysis/         # Analysis results (*.csv, *.json)
│   ├── samples/          # Test music and samples
│   └── databases/        # Database files
├── tools/                 # Utility scripts and tools
│   ├── cli/              # CLI implementations
│   ├── debug/            # Debug and diagnostic scripts
│   ├── validation/       # Test and validation scripts
│   └── bmad/             # BMAD methodology tools
├── config/                # Configuration files and templates
├── scripts/              # Build and deployment scripts
└── temp/                 # Temporary and experimental files
```

## 🚀 Quick Start

```bash
# Setup environment
source .venv/bin/activate

# Launch main application
python -m src.ui.enhanced_main_window

# Run CLI tools (examples)
python tools/cli/playlist_cli_final.py
python tools/bmad/bmad_100_certification_validator.py

# Validate organization
python scripts/validate_organization.py
```

## 📖 Documentation

- **[User Guide](docs/user/)** - How to use MAP4
- **[API Documentation](docs/api/)** - Technical specifications
- **[Development Guide](docs/development/)** - Contributing and setup
- **[BMAD Methodology](docs/development/bmad/)** - Build-Measure-Analyze-Decide framework

## 🧪 Testing

```bash
# Run organized test suite
python -m pytest tests/ -v

# Run validation tools
python tools/validation/test_implementation_status.py

# Validate project organization
python scripts/validate_organization.py
```