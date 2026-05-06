from __future__ import annotations

import time

from primecube.core.bit_ops import BitOps
from primecube.core.models import SearchResult
from primecube.core.prime_tester import PrimeTester
from primecube.policies.base import SearchPolicy


class StandardOddIncrementPolicy(SearchPolicy):
    """
    Number-line prime search: force x odd, then test x, x+2, x+4, ...

    This is the arithmetic-locality baseline.
    """

    name = "standard_odd_increment"

    def __init__(self, max_checks: int = 1_000_000):
        self.max_checks = max_checks

    def search(self, x: int, m: int) -> SearchResult:
        start = time.time()
        x0 = BitOps.force_odd(x)
        candidate = x0
        checks = 0

        while checks < self.max_checks:
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
                    flip_positions=None,
                    elapsed_sec=time.time() - start,
                )

            candidate += 2

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
