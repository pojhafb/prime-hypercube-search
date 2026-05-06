from __future__ import annotations

from sympy import isprime


class PrimeIndicator:
    """Prime subset of the odd hypercube Q_m^odd = {x in {0,1}^m : bit 0 = 1}."""

    def __init__(self, m: int, odd_only: bool = True):
        self.m = m
        self.odd_only = odd_only
        self._primes: set[int] | None = None
        self._vertices: list[int] | None = None

    def _all_vertices(self) -> list[int]:
        if self._vertices is None:
            if self.odd_only:
                self._vertices = list(range(1, 2**self.m, 2))
            else:
                self._vertices = list(range(0, 2**self.m))
        return self._vertices

    def vertices(self) -> list[int]:
        return self._all_vertices()

    def prime_set(self) -> set[int]:
        if self._primes is None:
            self._primes = {x for x in self._all_vertices() if isprime(x)}
        return self._primes

    def is_prime_vertex(self, x: int) -> bool:
        return isprime(x)

    def density(self) -> float:
        return len(self.prime_set()) / len(self._all_vertices())

    def indicator_dict(self) -> dict[int, int]:
        primes = self.prime_set()
        return {x: (1 if x in primes else 0) for x in self._all_vertices()}
