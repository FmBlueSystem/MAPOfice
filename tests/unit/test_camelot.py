from src.services.metadata import to_camelot
from src.services.compatibility import camelot_distance, camelot_score


def test_camelot_basic_pairs():
    assert to_camelot("A minor") == "8A"
    assert to_camelot("Am") == "8A"
    assert to_camelot("C major") == "8B"
    assert to_camelot("C") == "8B"
    assert to_camelot("E minor") == "9A"
    assert to_camelot("G major") == "9B"
    assert to_camelot("C# minor") == "12A"
    assert to_camelot("E maj") == "12B"
    # flats
    assert to_camelot("Bb major") == "6B"
    assert to_camelot("Ab minor") == "1A"


def test_camelot_distance_and_score():
    assert camelot_distance("8A", "8A") == 0.0
    assert camelot_score("8A", "8A") == 1.0
    # relative major/minor considered very close
    assert camelot_score("8A", "8B") >= 0.85
    # +/-1 on ring acceptable
    assert camelot_score("8A", "9A") >= 0.85
