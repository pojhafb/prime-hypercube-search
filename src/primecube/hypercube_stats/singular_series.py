"""
XOR singular series  S_xor(a).

S_xor(a) = prod_{q prime, q>=3}  P(q|x AND q|x^a) / (1 - 1/q)^2

The local factor at prime q measures how much the XOR structure of a
reduces (or increases) the chance that both x and x^a avoid q relative
to independent random odd integers.

Exact analytical results:

  Weight-1 (a = 2^j for any j >= 1):
    phi_q(2^j) = q*(q-2)/(q-1)^2   for ALL odd prime q, ALL j.
    Product over all q: S_xor(2^j) = C_2 ~= 0.66016 (Hardy-Littlewood constant).

  Weight-2 (a = 2^j + 2^k, diff = |k-j|):
    phi_q(a) = q*(2q-3)/(2*(q-1)^2)   if 2^diff ≡ ±1 (mod q)  [resonant]
             = q*(q-2)/(q-1)^2          otherwise               [non-resonant]
    For q=3 (ord=2), ALL weight-2 masks are resonant (phi_3 = 9/8 always).
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd


# -----------------------------------------------------------------------
# Small-prime sieve
# -----------------------------------------------------------------------

def _primes_up_to(n: int) -> list[int]:
    sieve = [True] * (n + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(n ** 0.5) + 1):
        if sieve[i]:
            for j in range(i * i, n + 1, i):
                sieve[j] = False
    return [i for i in range(2, n + 1) if sieve[i]]


_SMALL_PRIMES: list[int] = _primes_up_to(200)


# -----------------------------------------------------------------------
# Core computation
# -----------------------------------------------------------------------

def local_factor_xor(q: int, a: int, m: int) -> float:
    """
    Compute the local factor for prime q and mask a:

        phi_q(a) = P(q∤x AND q∤(x⊕a)) / (1 - 1/q)^2

    estimated over all odd x in [1, 2^m) using NumPy.
    Returns the factor relative to the random baseline (1 - 1/q)^2.
    """
    x = np.arange(1, 1 << m, 2, dtype=np.int64)   # all odd integers in [1, 2^m)
    xa = x ^ int(a)
    not_blocked = int(np.sum((x % q != 0) & (xa % q != 0)))
    frac = not_blocked / len(x)
    baseline = (1.0 - 1.0 / q) ** 2
    return frac / baseline if baseline > 0 else float("nan")


def singular_series_xor(
    a: int,
    small_primes: list[int] | None = None,
    m: int = 18,
) -> float:
    """
    S_xor(a) = prod_{q in small_primes, q odd} local_factor_xor(q, a, m).

    Uses all odd x in [1, 2^m) for an exact (non-sampled) result.
    Larger m gives a better approximation of the infinite-range limit.
    """
    if small_primes is None:
        small_primes = [3, 5, 7, 11, 13, 17, 19, 23]

    S = 1.0
    for q in small_primes:
        if q == 2:
            continue
        S *= local_factor_xor(q, int(a), m)
    return S


def batch_singular_series(
    masks: list[int],
    small_primes: list[int] | None = None,
    m: int = 18,
) -> dict[int, float]:
    """
    Compute S_xor for a list of masks efficiently.

    Shares the x array across all primes; iterates masks per prime
    to avoid recomputing x % q for each mask separately.
    Returns dict: mask -> S_xor(mask).
    """
    if small_primes is None:
        small_primes = [3, 5, 7, 11, 13, 17, 19, 23]

    x = np.arange(1, 1 << m, 2, dtype=np.int64)
    N = len(x)

    # S_xor accumulator
    S = {mask: 1.0 for mask in masks}

    for q in small_primes:
        if q == 2:
            continue
        xmod = (x % q).astype(np.int32)
        baseline = (1.0 - 1.0 / q) ** 2
        for mask in masks:
            xa = x ^ int(mask)
            xamod = (xa % q).astype(np.int32)
            not_blocked = int(np.sum((xmod != 0) & (xamod != 0)))
            frac = not_blocked / N
            S[mask] *= frac / baseline
    return S


# -----------------------------------------------------------------------
# Analytical local-factor formulas (exact, weight 1 and 2)
# -----------------------------------------------------------------------

def analytic_local_factor_weight1(q: int) -> float:
    """
    Exact local factor for any weight-1 mask 2^j (j >= 1) at odd prime q.

        phi_q(2^j) = q*(q-2)/(q-1)^2

    Independent of j.  Product over all q gives the Hardy-Littlewood
    twin prime constant C2 ~= 0.66016.
    """
    return q * (q - 2) / (q - 1) ** 2


def analytic_local_factor_weight2(q: int, diff: int) -> float:
    """
    Exact local factor for weight-2 mask 2^j + 2^k (diff = |k-j|) at odd prime q.

    Resonant case (2^diff ≡ ±1 mod q):
        phi_q = q*(2q-3) / (2*(q-1)^2)
    Non-resonant case:
        phi_q = q*(q-2) / (q-1)^2   [same as weight-1]
    """
    r = pow(2, diff, q)
    if r == 1 or r == q - 1:
        return q * (2 * q - 3) / (2 * (q - 1) ** 2)
    return q * (q - 2) / (q - 1) ** 2


def analytic_singular_series_weight2(
    diff: int,
    small_primes: list[int] | None = None,
) -> float:
    """
    Partial S_xor product for a weight-2 mask with bit-difference diff,
    using the exact analytical local-factor formulas.

    Converges (as primes grow) to the true S_xor for such masks.
    """
    if small_primes is None:
        small_primes = [3, 5, 7, 11, 13, 17, 19, 23]
    S = 1.0
    for q in small_primes:
        if q == 2:
            continue
        S *= analytic_local_factor_weight2(q, diff)
    return S


# -----------------------------------------------------------------------
# Obstruction breakdown
# -----------------------------------------------------------------------

def obstruction_breakdown(
    a: int,
    small_primes: list[int] | None = None,
    m: int = 18,
) -> pd.DataFrame:
    """
    Per-prime breakdown of local_factor_xor for mask a.

    Columns: prime, local_factor, log_factor, interpretation.
    """
    if small_primes is None:
        small_primes = [3, 5, 7, 11, 13, 17, 19, 23]

    x = np.arange(1, 1 << m, 2, dtype=np.int64)
    N = len(x)
    xa = x ^ int(a)

    rows = []
    for q in small_primes:
        if q == 2:
            continue
        not_blocked = int(np.sum((x % q != 0) & (xa % q != 0)))
        frac = not_blocked / N
        baseline = (1.0 - 1.0 / q) ** 2
        factor = frac / baseline
        rows.append({
            "prime": q,
            "blocked_fraction": 1.0 - frac,
            "baseline_blocked": 1.0 - baseline,
            "local_factor": factor,
            "log_factor": math.log(factor) if factor > 0 else float("-inf"),
        })
    df = pd.DataFrame(rows)
    df["running_product"] = df["local_factor"].cumprod()
    return df


# -----------------------------------------------------------------------
# Validation: compare S_xor to observed rho
# -----------------------------------------------------------------------

def add_singular_series(
    df: pd.DataFrame,
    small_primes: list[int] | None = None,
    m: int = 18,
) -> pd.DataFrame:
    """
    Add S_xor column to a DataFrame that has a 'mask' column.
    Also adds rho_residual = rho - S_xor if 'rho' column is present.
    """
    masks = df["mask"].tolist()
    s_map = batch_singular_series(masks, small_primes, m)
    df = df.copy()
    df["S_xor"] = df["mask"].map(s_map)
    if "rho" in df.columns:
        df["rho_residual"] = df["rho"] - df["S_xor"]
        df["rho_over_S"] = df["rho"] / df["S_xor"]
    return df
