import pytest

from src.models.hamms import HAMMSVector


def test_hamms_vector_accepts_12_dimensions():
    vec = HAMMSVector([0.0] * 12)
    assert len(vec.dims) == 12


def test_hamms_vector_rejects_non_12_dimensions():
    with pytest.raises(ValueError):
        HAMMSVector([0.0] * 11)
    with pytest.raises(ValueError):
        HAMMSVector([0.0] * 13)


def test_hamms_vector_normalized_shape():
    vec = HAMMSVector([1.0] * 12)
    n = vec.normalized()
    assert len(n) == 12
    # all components equal in this trivial case
    assert pytest.approx(sum(n)) == 1.0
