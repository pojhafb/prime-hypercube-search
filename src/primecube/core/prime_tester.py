from __future__ import annotations

from functools import lru_cache

from sympy import isprime


class PrimeTester:
    @staticmethod
    @lru_cache(maxsize=2_000_000)
    def is_prime(n: int) -> bool:
        if n < 2:
            return False
        return bool(isprime(n))
