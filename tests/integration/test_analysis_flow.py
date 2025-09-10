from pathlib import Path

from src.services.storage import Storage
from src.services.analyzer import Analyzer


def test_full_analysis_pipeline(tmp_path: Path):
    # Setup storage (in-memory)
    store = Storage.from_path("sqlite:///:memory:")
    analyzer = Analyzer(store)

    # Create dummy audio file
    audio = tmp_path / "sample.wav"
    audio.write_bytes(b"")

    # Analyze and persist
    result = analyzer.analyze_path(str(audio))
    assert {k for k in result.keys() if k in {"bpm","key","energy","hamms"}} == {"bpm", "key", "energy", "hamms"}
    assert isinstance(result["hamms"], list) and len(result["hamms"]) == 12

    # Verify stored
    rec = store.get_track_by_path(str(audio))
    assert rec is not None
    assert rec.analysis is not None
