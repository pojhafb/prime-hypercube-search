"""
Mersenne Corner Neighborhood Test.

For prime exponent p, the all-ones vertex M_p = 2^p - 1 is special:
  M_p XOR a  =  M_p - a      (since M_p has all p bits set)

So Hamming moves from the Mersenne corner are ordinary subtraction of sparse
binary masks.  We ask:

  Is the prime density near the Mersenne corner higher, lower, or equal
  to random odd p-bit centers — and does the primality of M_p matter?

Comparison groups (prime exponents p only):
  A: M_p prime   (Mersenne primes)
  B: M_p composite
  C: random odd p-bit centers (baseline)

For each (group, p, radius r), count primes in the Hamming shell of radius r
excluding bit 0 (to keep candidates odd), excluding the center itself.

Since M_p XOR a = M_p - a, candidates are:
  { M_p - a : popcount(a) = r, bit_0(a) = 0, a < M_p }

Output:
  results/summaries/mersenne_corner.csv
  results/plots/mersenne_corner/
"""
from __future__ import annotations

import sys
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import sys
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sympy import isprime

# Force line-buffered output so progress appears during background runs.
sys.stdout.reconfigure(line_buffering=True)

RESULTS_DIR = Path(__file__).parent.parent / "results"

# Known Mersenne prime exponents (complete list through 2024).
MERSENNE_PRIME_EXPONENTS = {
    2, 3, 5, 7, 13, 17, 19, 31, 61, 89, 107, 127,
    521, 607, 1279, 2203, 2281, 3217, 4253, 4423,
    9689, 9941, 11213, 19937, 21701, 23209, 44497,
    86243, 110503, 132049, 216091, 756839, 859433,
    1257787, 1398269, 2976221, 3021377, 6972593,
    13466917, 20996011, 24036583, 25964951, 30402457,
    32582657, 37156667, 42643801, 43112609, 57885161,
    74207281, 77232917, 82589933,
}


def sieve_primes_up_to(n: int) -> list[int]:
    if n < 2:
        return []
    sieve = bytearray([1]) * (n + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(n**0.5) + 1):
        if sieve[i]:
            sieve[i*i::i] = bytearray(len(sieve[i*i::i]))
    return [i for i in range(2, n+1) if sieve[i]]


PRIMES_UP_TO_200 = sieve_primes_up_to(200)


def prime_shell_count(center: int, p: int, r: int) -> tuple[int, int]:
    """
    Count primes among Hamming-shell-r neighbors of center (excluding bit 0,
    keeping candidates odd, excluding the center itself).

    Returns (prime_count, shell_size).
    center XOR a = center - a  only when center = 2^p-1 (all-ones).
    For arbitrary center we still use XOR.
    """
    bits = list(range(1, p))  # exclude bit 0
    combos = list(combinations(bits, r))
    prime_count = 0
    for pos_tuple in combos:
        mask = sum(1 << b for b in pos_tuple)
        cand = center ^ mask
        if cand > 1 and isprime(cand):
            prime_count += 1
    return prime_count, len(combos)


def random_center_stats(
    p: int, r: int, n_centers: int, seed: int = 42
) -> tuple[float, float]:
    """
    Sample n_centers random odd p-bit integers (excluding 2^p-1 itself),
    compute the fraction of shell-r neighbors that are prime,
    and return (mean_fraction, std_fraction).
    """
    rng = random.Random(seed)
    bits = list(range(1, p))
    combos = list(combinations(bits, r))
    if not combos:
        return 0.0, 0.0

    fractions = []
    for _ in range(n_centers):
        # Random odd p-bit integer (bit 0 = 1, bit p-1 = 1 for p bits, rest random)
        x = (1 << (p - 1)) | 1  # ensure p-bit and odd
        x |= rng.getrandbits(p - 2) << 1  # fill middle bits randomly
        x &= (1 << p) - 1
        count = 0
        for pos_tuple in combos:
            mask = sum(1 << b for b in pos_tuple)
            cand = x ^ mask
            if cand > 1 and isprime(cand):
                count += 1
        fractions.append(count / len(combos))
    return float(np.mean(fractions)), float(np.std(fractions))


def expected_count(p: int, r: int) -> float:
    """Expected prime count in radius-r shell under prime-density model."""
    bits = list(range(1, p))
    shell_size = len(list(combinations(bits, r)))
    # PNT density near 2^p: delta ≈ 1/(p * ln 2)
    delta = 1.0 / (p * 0.6931471805599453)
    return shell_size * delta


def run_experiment(
    prime_exponents: list[int],
    max_radius: int = 3,
    n_random_centers: int = 200,
    seed: int = 42,
) -> pd.DataFrame:
    rows = []

    for p in prime_exponents:
        M_p = (1 << p) - 1
        is_mp = p in MERSENNE_PRIME_EXPONENTS
        group = "mersenne_prime" if is_mp else "mersenne_composite"

        print(f"\n  p={p:4d}  M_p={'prime' if is_mp else 'composite'}"
              f"  ({p}-bit, {len(str(M_p))}-digit)")

        for r in range(1, max_radius + 1):
            # Mersenne corner
            mc, shell = prime_shell_count(M_p, p, r)
            exp = expected_count(p, r)
            ratio = mc / exp if exp > 0 else float("nan")

            # Random baseline for this (p, r)
            print(f"    r={r}: shell={shell}, Mersenne primes={mc}"
                  f"  (exp={exp:.1f}, ratio={ratio:.3f})")
            rand_mean, rand_std = random_center_stats(p, r, n_random_centers, seed)
            rand_abs_mean = rand_mean * shell
            rand_abs_std = rand_std * shell
            z = (mc - rand_abs_mean) / rand_abs_std if rand_abs_std > 0 else float("nan")

            rows.append({
                "p": p,
                "group": group,
                "is_mersenne_prime": is_mp,
                "radius": r,
                "shell_size": shell,
                "prime_count": mc,
                "expected_density": exp,
                "ratio_to_density": ratio,
                "random_mean": rand_abs_mean,
                "random_std": rand_abs_std,
                "z_score": z,
            })
            print(f"        random baseline: mean={rand_abs_mean:.1f}±{rand_abs_std:.1f}"
                  f"  z={z:.2f}")

    return pd.DataFrame(rows)


def plot_results(df: pd.DataFrame, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)

    # Z-score comparison by group
    for r in df["radius"].unique():
        sub = df[df["radius"] == r]
        fig, ax = plt.subplots(figsize=(9, 4))
        colors = {"mersenne_prime": "tomato", "mersenne_composite": "steelblue"}
        for g, grp in sub.groupby("group"):
            ax.scatter(grp["p"], grp["z_score"],
                       label=g.replace("_", " "), color=colors[g], s=60, zorder=3)
        ax.axhline(0, color="black", linestyle="--", linewidth=1)
        ax.axhline(2, color="grey", linestyle=":", linewidth=1, label="z=±2")
        ax.axhline(-2, color="grey", linestyle=":", linewidth=1)
        ax.set_xlabel("Exponent p")
        ax.set_ylabel("Z-score vs random centers")
        ax.set_title(f"Mersenne corner prime density, radius r={r}")
        ax.legend()
        fig.tight_layout()
        fig.savefig(out_dir / f"mersenne_z_r{r}.png", dpi=150, bbox_inches="tight")
        plt.close(fig)

    # Ratio to expected density
    for r in df["radius"].unique():
        sub = df[df["radius"] == r]
        fig, ax = plt.subplots(figsize=(9, 4))
        for g, grp in sub.groupby("group"):
            ax.scatter(grp["p"], grp["ratio_to_density"],
                       label=g.replace("_", " "), color=colors[g], s=60, zorder=3)
        ax.axhline(1.0, color="black", linestyle="--", linewidth=1, label="ratio=1")
        ax.set_xlabel("Exponent p")
        ax.set_ylabel("Prime count / expected by density")
        ax.set_title(f"Mersenne corner ratio to PNT density, radius r={r}")
        ax.legend()
        fig.tight_layout()
        fig.savefig(out_dir / f"mersenne_ratio_r{r}.png", dpi=150, bbox_inches="tight")
        plt.close(fig)


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Mersenne corner neighborhood test")
    parser.add_argument("--max-p", type=int, default=127,
                        help="Maximum exponent p to test (default: 127)")
    parser.add_argument("--max-radius", type=int, default=3,
                        help="Maximum Hamming radius (default: 3)")
    parser.add_argument("--n-random", type=int, default=200,
                        help="Random centers per (p, r) for baseline (default: 200)")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    print(f"Mersenne Corner Neighborhood Test")
    print(f"  max_p={args.max_p}, max_radius={args.max_radius}, "
          f"n_random={args.n_random}")

    # Collect prime exponents p <= max_p
    prime_exps = [q for q in PRIMES_UP_TO_200 if q <= args.max_p]
    # Also add p=2 trivially (M_2=3, prime)
    prime_exps = sorted(set(prime_exps) | {2})

    print(f"\nPrime exponents to test: {prime_exps}")
    print(f"Mersenne-prime exponents in range: "
          f"{[p for p in prime_exps if p in MERSENNE_PRIME_EXPONENTS]}")

    df = run_experiment(
        prime_exps,
        max_radius=args.max_radius,
        n_random_centers=args.n_random,
        seed=args.seed,
    )

    sum_dir = RESULTS_DIR / "summaries"
    plot_dir = RESULTS_DIR / "plots" / "mersenne_corner"
    sum_dir.mkdir(parents=True, exist_ok=True)

    csv_path = sum_dir / "mersenne_corner.csv"
    df.to_csv(csv_path, index=False)
    print(f"\nResults saved to {csv_path}")

    print("\n" + "="*70)
    print("SUMMARY TABLE")
    print("="*70)
    cols = ["p", "group", "radius", "shell_size", "prime_count",
            "expected_density", "ratio_to_density", "z_score"]
    pd.set_option("display.float_format", "{:.3f}".format)
    print(df[cols].to_string(index=False))

    # Group-level summary
    print("\n--- Group averages by radius ---")
    grp_summary = (
        df.groupby(["group", "radius"])
        .agg(
            n_exponents=("p", "count"),
            mean_ratio=("ratio_to_density", "mean"),
            mean_z=("z_score", "mean"),
            std_z=("z_score", "std"),
        )
        .reset_index()
    )
    print(grp_summary.to_string(index=False))

    plot_results(df, plot_dir)
    print(f"\nPlots saved to {plot_dir}")


if __name__ == "__main__":
    main()
