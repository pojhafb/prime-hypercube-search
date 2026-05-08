from __future__ import annotations

from itertools import combinations

import numpy as np
import pandas as pd

from .prime_indicator import PrimeIndicator


def _wht(a: np.ndarray) -> np.ndarray:
    """Walsh-Hadamard Transform (in-place, unnormalized). O(m * 2^m)."""
    n = len(a)
    h = 1
    while h < n:
        view = a.reshape(-1, 2 * h)
        left = view[:, :h].copy()
        right = view[:, h:].copy()
        view[:, :h] = left + right
        view[:, h:] = left - right
        h *= 2
    return a


class XORAutocorrelation:
    """
    Computes C(a) = |{x ∈ P_m : x ⊕ a ∈ P_m}| for all masks a.

    Uses the identity:  C = IWHT(WHT(f)²),  time O(m * 2^m).

    For popcount(a) = 1 this reduces to Hamming-1 prime-prime edge counts.
    For general even a (bit 0 not flipped) this gives the XOR difference
    distribution of primes across the full odd subcube.
    """

    MAX_M = 26  # WHT on 2^26 floats ≈ 512 MB

    def __init__(self, m: int):
        if m > self.MAX_M:
            raise ValueError(f"m={m} exceeds MAX_M={self.MAX_M}")
        self.m = m

    # ------------------------------------------------------------------
    # Core computation
    # ------------------------------------------------------------------

    def compute_all(self, prime_set: set[int] | None = None) -> np.ndarray:
        """Return C[a] for every a in [0, 2^m).  Only even a matter."""
        pi = PrimeIndicator(self.m, odd_only=True)
        if prime_set is None:
            prime_set = pi.prime_set()

        N = 2 ** self.m
        f = np.zeros(N, dtype=np.float64)
        for p in prime_set:
            f[p] = 1.0

        F = _wht(f.copy())
        F2 = F * F
        C = _wht(F2) / N
        return C  # C[a] = number of prime pairs (p, p XOR a)

    # ------------------------------------------------------------------
    # Analysis
    # ------------------------------------------------------------------

    def analyze(
        self,
        C: np.ndarray,
        prime_set: set[int],
        max_weight: int = 4,
        small_primes: list[int] | None = None,
    ) -> pd.DataFrame:
        """
        For every even mask a of popcount <= max_weight, compute:
          rho(a) = C(a) / E[C(a)]
        where E[C(a)] = delta^2 * |Q_m^odd|  (random-subset null model).
        """
        if small_primes is None:
            small_primes = [3, 5, 7, 11]

        N_odd = 2 ** (self.m - 1)
        delta = len(prime_set) / N_odd
        expected = delta ** 2 * N_odd

        rows: list[dict] = []
        free_bits = list(range(1, self.m))  # bit 0 excluded

        for weight in range(1, max_weight + 1):
            for positions in combinations(free_bits, weight):
                mask = sum(1 << p for p in positions)
                c_val = float(C[mask])
                rho = c_val / expected if expected > 0 else 0.0
                row: dict = {
                    "mask": mask,
                    "bit_positions": str(positions),
                    "popcount": weight,
                    "C_a": int(round(c_val)),
                    "expected": round(expected, 2),
                    "rho": rho,
                    "is_single_bit": weight == 1,
                }
                for q in small_primes:
                    row[f"mask_mod{q}"] = mask % q
                rows.append(row)

        return pd.DataFrame(rows)

    def summary_by_weight(self, df: pd.DataFrame) -> pd.DataFrame:
        """Mean / std / range of rho grouped by Hamming weight of mask."""
        return (
            df.groupby("popcount")
            .agg(
                n_masks=("rho", "count"),
                mean_rho=("rho", "mean"),
                std_rho=("rho", "std"),
                min_rho=("rho", "min"),
                max_rho=("rho", "max"),
                median_rho=("rho", "median"),
            )
            .reset_index()
        )

    def summary_by_mod(
        self, df: pd.DataFrame, q: int, weight: int | None = None
    ) -> pd.DataFrame:
        """Mean rho grouped by mask mod q, optionally filtered to one weight."""
        sub = df if weight is None else df[df["popcount"] == weight].copy()
        col = f"mask_mod{q}"
        if col not in sub.columns:
            raise ValueError(f"prime {q} not in small_primes used at analyze() time")
        return (
            sub.groupby(col)
            .agg(
                n=("rho", "count"),
                mean_rho=("rho", "mean"),
                std_rho=("rho", "std"),
            )
            .reset_index()
            .rename(columns={col: f"mod{q}"})
        )

    def top_masks(
        self, df: pd.DataFrame, n: int = 20, by: str = "rho", ascending: bool = False
    ) -> pd.DataFrame:
        """Return the n masks with highest (or lowest) rho."""
        return df.nlargest(n, by) if not ascending else df.nsmallest(n, by)
