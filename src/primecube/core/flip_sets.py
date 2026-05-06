from __future__ import annotations

import random
from itertools import combinations
from typing import Dict, List, Tuple

FlipSet = Tuple[int, ...]


class FlipSetFactory:
    """
    Builds ordered lists of bit-flip position tuples for the odd subcube.

    All factories exclude bit 0 so every candidate remains odd.
    """

    @staticmethod
    def make_static(
        m: int,
        max_radius: int,
        strategy: str,
        seed: int = 42,
    ) -> List[FlipSet]:
        allowed = list(range(1, m))
        flip_sets: List[FlipSet] = []

        for r in range(0, max_radius + 1):
            combos = list(combinations(allowed, r))

            if strategy == "low_bit_first":
                combos.sort(key=lambda c: (sum(c), max(c) if c else -1))

            elif strategy == "high_bit_first":
                combos.sort(key=lambda c: (-sum(c), -(max(c) if c else -1)))

            elif strategy == "uniform_random":
                rng = random.Random(seed + 1009 * r + m)
                rng.shuffle(combos)

            else:
                raise ValueError(f"Unknown strategy: {strategy!r}")

            flip_sets.extend(combos)

        return flip_sets

    @staticmethod
    def make_learned(
        m: int,
        max_radius: int,
        bit_score: Dict[int, float],
    ) -> List[FlipSet]:
        allowed = list(range(1, m))
        flip_sets: List[FlipSet] = []

        for r in range(0, max_radius + 1):
            combos = list(combinations(allowed, r))

            combos.sort(
                key=lambda c: (
                    -sum(bit_score.get(bit, 0.0) for bit in c),
                    sum(c),
                    max(c) if c else -1,
                )
            )

            flip_sets.extend(combos)

        return flip_sets
