import os
import sys
from pathlib import Path


def pytest_configure(config):
    # Ensure fixtures directory exists; users should place small audio clips here
    fixtures = Path(__file__).parent / "fixtures"
    fixtures.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("AUDIO_FIXTURES", str(fixtures))
    # Add project root to sys.path so tests can import src/*
    repo_root = Path(__file__).resolve().parents[1]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
