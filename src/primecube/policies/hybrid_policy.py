from __future__ import annotations

import time
from typing import Dict, List

from primecube.core.bit_ops import BitOps, FlipSet
from primecube.core.flip_sets import FlipSetFactory
from primecube.core.models import SearchResult
from primecube.core.prime_tester import PrimeTester
from primecube.policies.base import SearchPolicy


class HybridStandardPlusLearnedPolicy(SearchPolicy):
    """
    Interleaves standard odd-increment candidates with learned Hamming candidates.

    At each step i:
      - if i < odd_increment_limit: add x0 + 2*i
      - if i < len(learned_flip_sets): add x0 XOR flip_mask_i

    Candidates are deduplicated. Stops at first prime found.
    """

    name = "hybrid_standard_plus_learned"

    def __init__(
        self,
        bit_score: Dict[int, float],
        max_radius: int = 4,
        odd_increment_limit: int = 128,
    ):
        self.bit_score = bit_score
        self.max_radius = max_radius
        self.odd_increment_limit = odd_increment_limit
        self._cache: Dict[int, List[FlipSet]] = {}

    def _get_flip_sets(self, m: int) -> List[FlipSet]:
        if m not in self._cache:
            self._cache[m] = FlipSetFactory.make_learned(m, self.max_radius, self.bit_score)
        return self._cache[m]

    def search(self, x: int, m: int) -> SearchResult:
        start = time.time()
        x0 = BitOps.force_odd(x)
        learned_flip_sets = self._get_flip_sets(m)

        seen: set = set()
        checks = 0
        max_len = max(self.odd_increment_limit, len(learned_flip_sets))

        for i in range(max_len):
            candidates = []

            if i < self.odd_increment_limit:
                candidates.append((x0 + 2 * i, None))

            if i < len(learned_flip_sets):
                positions = learned_flip_sets[i]
                candidates.append((BitOps.flip_bits(x0, positions), positions))

            for candidate, positions in candidates:
                if candidate in seen:
                    continue

                seen.add(candidate)
                checks += 1

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
