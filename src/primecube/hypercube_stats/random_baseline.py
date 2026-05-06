from __future__ import annotations

import random


class RandomPrimeLikeSet:
    """
    A randomly chosen subset of odd-hypercube vertices with the same density
    as the real prime set, used as a null-model baseline.
    """

    def __init__(self, vertices: list[int], density: float, seed: int = 42):
        rng = random.Random(seed)
        self._chosen: set[int] = {v for v in vertices if rng.random() < density}
        self.density = density

    def is_member(self, x: int) -> bool:
        return x in self._chosen

    def member_set(self) -> set[int]:
        return self._chosen

    def actual_density(self, vertices: list[int]) -> float:
        return len(self._chosen) / len(vertices)
