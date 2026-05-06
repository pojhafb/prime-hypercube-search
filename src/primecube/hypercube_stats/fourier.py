from __future__ import annotations

from itertools import combinations

import pandas as pd

from .prime_indicator import PrimeIndicator


class WalshFourierAnalyzer:
    """
    Compute low-degree Walsh-Fourier coefficients of the centered prime indicator:
        g(x) = f(x) - delta
    where f(x) = 1 if x is prime, delta = density.

    The Walsh-Fourier coefficient for subset S ⊆ [m] is:
        g_hat(S) = (1/N) * sum_x g(x) * chi_S(x)
        chi_S(x) = (-1)^{popcount(x & mask_S)}

    Only feasible for small m (<=20) since vertices = 2^(m-1).
    """

    def __init__(self, m: int, odd_only: bool = True):
        if m > 20:
            raise ValueError(f"Fourier analysis only feasible for m <= 20 (got m={m})")
        self.m = m
        self.odd_only = odd_only

    def low_degree_coefficients(self, max_degree: int = 3) -> pd.DataFrame:
        pi = PrimeIndicator(self.m, self.odd_only)
        vertices = pi.vertices()
        prime_set = pi.prime_set()
        density = len(prime_set) / len(vertices)
        N = len(vertices)

        free_bits = list(range(1, self.m)) if self.odd_only else list(range(self.m))

        rows = []
        for degree in range(0, max_degree + 1):
            for subset in combinations(free_bits, degree):
                mask = 0
                for b in subset:
                    mask |= (1 << b)
                coeff = 0.0
                for x in vertices:
                    g_x = (1.0 if x in prime_set else 0.0) - density
                    parity = bin(x & mask).count("1") % 2
                    chi = 1 if parity == 0 else -1
                    coeff += g_x * chi
                coeff /= N
                rows.append({
                    "m": self.m,
                    "degree": degree,
                    "bit_set": str(subset),
                    "coefficient": coeff,
                    "abs_coefficient": abs(coeff),
                })

        df = pd.DataFrame(rows)
        return df.sort_values("abs_coefficient", ascending=False).reset_index(drop=True)
