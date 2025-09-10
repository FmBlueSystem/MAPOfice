import os
from pathlib import Path

from src.lib.audio_processing import analyze_track


def test_audio_analyze_minimal_contract(tmp_path: Path):
    # create an empty dummy file to satisfy path existence check
    f = tmp_path / "dummy.wav"
    f.write_bytes(b"")

    result = analyze_track(str(f))
    assert set(result.keys()) == {"bpm", "key", "energy", "hamms"}
    # Accept placeholder None/values for now; HAMMS must be length 12 list
    assert isinstance(result["hamms"], list) and len(result["hamms"]) == 12
