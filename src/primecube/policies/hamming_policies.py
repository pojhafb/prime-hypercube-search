from __future__ import annotations

import time
from typing import Dict, List

from primecube.core.bit_ops import BitOps, FlipSet
from primecube.core.flip_sets import FlipSetFactory
from primecube.core.models import SearchResult
from primecube.core.prime_tester import PrimeTester
from primecube.policies.base import SearchPolicy


class _FlipSetPolicy(SearchPolicy):
    """
    Base for all flip-set Hamming policies.

    Subclasses implement _build_flip_sets(m) and set self.name.
    The search loop is shared.

    Flip sets are cached per m: at m=64 with max_radius=4 there are 637k tuples
    that take ~350ms to sort. Rebuilding them on every search() call would make
    a 50k-sample run take hours instead of minutes.
    """

    def __init__(self):
        self._cache: Dict[int, List[FlipSet]] = {}

    def _build_flip_sets(self, m: int) -> List[FlipSet]:
        raise NotImplementedError

    def _get_flip_sets(self, m: int) -> List[FlipSet]:
        if m not in self._cache:
            self._cache[m] = self._build_flip_sets(m)
        return self._cache[m]

    def search(self, x: int, m: int) -> SearchResult:
        start = time.time()
        x0 = BitOps.force_odd(x)
        flip_sets = self._get_flip_sets(m)
        checks = 0

        for positions in flip_sets:
            checks += 1
            candidate = BitOps.flip_bits(x0, positions)

            if PrimeTester.is_prime(candidate):
                return SearchResult(
                    strategy=self.name,
                    x=x,
                    x_odd=x0,
                    found_prime=candidate,
                    checks=checks,
                    hamming_distance=BitOps.hamming_distance(x0, candidate),
                    arithmetic_distance=abs(candidate - x0),
                    flip_positions=positions,
                    elapsed_sec=time.time() - start,
                )

        return SearchResult(
            strategy=self.name,
            x=x,
            x_odd=x0,
            found_prime=None,
            checks=checks,
            hamming_distance=None,
            arithmetic_distance=None,
            flip_positions=None,
            elapsed_sec=time.time() - start,
        )


class LowBitFirstPolicy(_FlipSetPolicy):
    """Prefers flipping lower-order bits first (excluding bit 0)."""

    name = "low_bit_first_no_bit0"

    def __init__(self, max_radius: int = 4, seed: int = 42):
        super().__init__()
        self.max_radius = max_radius
        self.seed = seed

    def _build_flip_sets(self, m: int) -> List[FlipSet]:
        return FlipSetFactory.make_static(m, self.max_radius, "low_bit_first", self.seed)


class HighBitFirstPolicy(_FlipSetPolicy):
    """Prefers flipping higher-order bits first (excluding bit 0)."""

    name = "high_bit_first_no_bit0"

    def __init__(self, max_radius: int = 4, seed: int = 42):
        super().__init__()
        self.max_radius = max_radius
        self.seed = seed

    def _build_flip_sets(self, m: int) -> List[FlipSet]:
        return FlipSetFactory.make_static(m, self.max_radius, "high_bit_first", self.seed)


class UniformRandomPolicy(_FlipSetPolicy):
    """Visits odd-subcube candidates in random Hamming order (excluding bit 0)."""

    name = "uniform_random_no_bit0"

    def __init__(self, max_radius: int = 4, seed: int = 42):
        super().__init__()
        self.max_radius = max_radius
        self.seed = seed

    def _build_flip_sets(self, m: int) -> List[FlipSet]:
        return FlipSetFactory.make_static(m, self.max_radius, "uniform_random", self.seed)


class LearnedBitOrderPolicy(_FlipSetPolicy):
    """
    Uses a learned bit-score ranking to order flip sets.

    Bits with higher learned usefulness scores are tried first.
    Bit 0 is excluded (score forced to 0.0).
    """

    def __init__(self, bit_score: Dict[int, float], max_radius: int = 4, label: str = ""):
        super().__init__()
        self.bit_score = bit_score
        self.max_radius = max_radius
        self.name = f"learned_bit_order_no_bit0{('_' + label) if label else ''}"

    def _build_flip_sets(self, m: int) -> List[FlipSet]:
        return FlipSetFactory.make_learned(m, self.max_radius, self.bit_score)
