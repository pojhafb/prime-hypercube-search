from __future__ import annotations

import pandas as pd

from .prime_indicator import PrimeIndicator


class SpectralPrimeStats:
    """
    Spectral adjacency energy of the prime indicator in Q_m^odd.

    f^T A f  =  2 * (number of prime-prime Hamming-1 edges)

    Random model baseline:
        E[f^T A f] ≈ delta^2 * 2 * |E(Q_m^odd)|
        |E(Q_m^odd)| = (m-1) * 2^(m-2)
    """

    def __init__(self, m: int, odd_only: bool = True):
        self.m = m
        self.odd_only = odd_only

    def adjacency_energy_r1(self, prime_set: set[int] | None = None) -> dict:
        pi = PrimeIndicator(self.m, self.odd_only)
        if prime_set is None:
            prime_set = pi.prime_set()
        density = len(prime_set) / len(pi.vertices())

        free_bits = list(range(1, self.m)) if self.odd_only else list(range(self.m))
        edge_count = 0
        for p in prime_set:
            for bit in free_bits:
                neighbor = p ^ (1 << bit)
                if neighbor in prime_set:
                    edge_count += 1
        # edge_count counts each edge twice (once from each end)
        prime_prime_edges = edge_count // 2
        ftAf = edge_count  # = 2 * edges

        total_edges = len(free_bits) * (2 ** (self.m - 2)) if self.odd_only else self.m * (2 ** (self.m - 1))
        expected_ftAf = density ** 2 * 2 * total_edges

        return {
            "m": self.m,
            "prime_prime_edges": prime_prime_edges,
            "fTAf_observed": ftAf,
            "fTAf_expected_random": expected_ftAf,
            "ratio_observed_to_expected": ftAf / expected_ftAf if expected_ftAf > 0 else float("nan"),
            "density": density,
        }

    def adjacency_energy_by_bit(self, prime_set: set[int] | None = None) -> pd.DataFrame:
        pi = PrimeIndicator(self.m, self.odd_only)
        if prime_set is None:
            prime_set = pi.prime_set()
        density = len(prime_set) / len(pi.vertices())
        free_bits = list(range(1, self.m)) if self.odd_only else list(range(self.m))
        edges_per_bit = 2 ** (self.m - 2) if self.odd_only else 2 ** (self.m - 1)

        rows = []
        for bit in free_bits:
            mask = 1 << bit
            count = sum(1 for p in prime_set if (p ^ mask) in prime_set and (p ^ mask) > p)
            rows.append({
                "m": self.m,
                "bit": bit,
                "prime_prime_edges": count,
                "expected": density ** 2 * edges_per_bit,
                "ratio": count / (density ** 2 * edges_per_bit) if edges_per_bit > 0 else float("nan"),
            })
        return pd.DataFrame(rows)
