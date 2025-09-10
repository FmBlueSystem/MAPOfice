from __future__ import annotations

from typing import Iterable, List


class HAMMSVector:
    """12-dimensional harmonic analysis vector.

    Minimal implementation to support early TDD. Provides validation and
    a simple L1 normalization helper.
    """

    def __init__(self, dims: Iterable[float]):
        values = list(dims)
        if len(values) != 12:
            raise ValueError("HAMMSVector requires 12 dimensions")
        self.dims: List[float] = [float(x) for x in values]

    def normalized(self) -> List[float]:
        total = sum(abs(x) for x in self.dims)
        if total == 0:
            # equal distribution if vector is zero
            return [1.0 / 12.0] * 12
        return [abs(x) / total for x in self.dims]
