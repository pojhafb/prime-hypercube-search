from __future__ import annotations

import pandas as pd

from .prime_indicator import PrimeIndicator


class PrimeEdgeCounter:
    """
    Count Hamming-1 edges between prime vertices in Q_m^odd.

    Expected under random model:
        E[edges] ≈ density² × |E(Q_m^odd)|
        |E(Q_m^odd)| = (m-1) × 2^(m-2)   (odd subcube has m-1 free bits)
    """

    def __init__(self, m: int, odd_only: bool = True):
        self.m = m
        self.odd_only = odd_only

    def hamming_one_edges(self, prime_set: set[int] | None = None) -> pd.DataFrame:
        pi = PrimeIndicator(self.m, self.odd_only)
        if prime_set is None:
            prime_set = pi.prime_set()
        density = len(prime_set) / len(pi.vertices())

        free_bits = list(range(1, self.m)) if self.odd_only else list(range(self.m))
        total_edges_in_subcube = len(free_bits) * (2 ** (self.m - 2)) if self.odd_only else self.m * (2 ** (self.m - 1))

        rows = []
        for bit in free_bits:
            mask = 1 << bit
            observed = 0
            for p in prime_set:
                neighbor = p ^ mask
                if neighbor in prime_set and neighbor > p:
                    observed += 1
            # Expected edges along this bit = density^2 × (subcube edges along this bit)
            edges_along_bit = 2 ** (self.m - 2) if self.odd_only else 2 ** (self.m - 1)
            expected = density ** 2 * edges_along_bit
            rows.append({
                "m": self.m,
                "bit_position": bit,
                "observed_edges": observed,
                "expected_edges": expected,
                "ratio": observed / expected if expected > 0 else float("nan"),
            })

        summary = {
            "m": self.m,
            "total_prime_prime_edges": sum(r["observed_edges"] for r in rows),
            "total_expected_edges": density ** 2 * total_edges_in_subcube,
            "density": density,
            "prime_count": len(prime_set),
        }
        return pd.DataFrame(rows), summary

    def edge_summary(self) -> dict:
        _, summary = self.hamming_one_edges()
        return summary
