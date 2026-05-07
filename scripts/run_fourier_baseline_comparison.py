"""
Fourier baseline comparison experiment.

For each Walsh-Fourier coefficient of the prime indicator, compare its
magnitude against the distribution of the same coefficient over many
random baseline sets of the same density.  Reports the percentile rank
of each prime coefficient and flags those that are anomalously large.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import numpy as np
import pandas as pd

from primecube.hypercube_stats import PrimeIndicator, WalshFourierAnalyzer, RandomPrimeLikeSet

RESULTS_DIR = Path(__file__).parent.parent / "results"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Fourier baseline comparison for prime indicator")
    p.add_argument("--ms", nargs="+", type=int, default=[12, 14, 16],
                   help="Hypercube dimensions <=20 (default: 12 14 16)")
    p.add_argument("--max-degree", type=int, default=3)
    p.add_argument("--n-baselines", type=int, default=30,
                   help="Random baseline sets per m (default: 30)")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--top-n", type=int, default=20)
    return p.parse_args()


def _fourier_abs(m: int, prime_set: set[int] | None, vertices: list[int],
                 density: float, max_degree: int) -> dict[str, float]:
    """Return {bit_set_str: abs_coefficient} for a given prime-like set."""
    from itertools import combinations
    N = len(vertices)
    free_bits = list(range(1, m))
    result: dict[str, float] = {}
    for degree in range(0, max_degree + 1):
        for subset in combinations(free_bits, degree):
            mask = sum(1 << b for b in subset)
            coeff = 0.0
            for x in vertices:
                g_x = (1.0 if (prime_set is not None and x in prime_set) else 0.0) - density
                parity = bin(x & mask).count("1") % 2
                chi = 1 if parity == 0 else -1
                coeff += g_x * chi
            result[str(subset)] = abs(coeff / N)
    return result


def main() -> None:
    args = parse_args()
    raw_dir = RESULTS_DIR / "raw"
    sum_dir = RESULTS_DIR / "summaries"
    raw_dir.mkdir(parents=True, exist_ok=True)
    sum_dir.mkdir(parents=True, exist_ok=True)

    for m in args.ms:
        if m > 20:
            print(f"Skipping m={m}: too large for full Fourier (limit 20)")
            continue
        print(f"\n=== m={m}  max_degree={args.max_degree}  n_baselines={args.n_baselines} ===")

        pi = PrimeIndicator(m, odd_only=True)
        vertices = pi.vertices()
        prime_set = pi.prime_set()
        density = len(prime_set) / len(vertices)

        # Prime coefficients
        print("  Computing prime indicator Fourier coefficients...")
        prime_coeffs = _fourier_abs(m, prime_set, vertices, density, args.max_degree)

        # Baseline distributions
        print(f"  Computing {args.n_baselines} random baseline Fourier spectra...")
        baseline_data: dict[str, list[float]] = {k: [] for k in prime_coeffs}
        for k in range(args.n_baselines):
            rng_set = RandomPrimeLikeSet(vertices, density, seed=args.seed + k)
            bl_coeffs = _fourier_abs(m, rng_set.member_set(), vertices, density, args.max_degree)
            for key in prime_coeffs:
                baseline_data[key].append(bl_coeffs[key])

        rows = []
        for key, prime_val in prime_coeffs.items():
            bl_arr = np.array(baseline_data[key])
            percentile = float(np.mean(bl_arr <= prime_val) * 100)
            rows.append({
                "m": m,
                "bit_set": key,
                "degree": key.count(",") + (0 if key == "()" else 1) if key != "()" else 0,
                "prime_abs_coeff": prime_val,
                "baseline_mean": float(bl_arr.mean()),
                "baseline_std": float(bl_arr.std(ddof=1)),
                "percentile_vs_baseline": percentile,
                "anomalous_95": percentile >= 95,
            })

        df = pd.DataFrame(rows).sort_values("prime_abs_coeff", ascending=False).reset_index(drop=True)
        path = sum_dir / f"fourier_baseline_m{m}_deg{args.max_degree}.csv"
        df.to_csv(path, index=False)

        top = df.head(args.top_n)
        anomalous = df[df["anomalous_95"]]
        print(f"  Top-{args.top_n} by |ĝ(S)|:")
        print(top[["bit_set", "degree", "prime_abs_coeff", "baseline_mean",
                    "baseline_std", "percentile_vs_baseline"]].to_string(index=False))
        print(f"\n  Anomalous (>=95th pct vs baseline): {len(anomalous)} coefficients")
        if len(anomalous):
            print(anomalous[["bit_set", "degree", "prime_abs_coeff",
                              "percentile_vs_baseline"]].to_string(index=False))
        print(f"\n  Saved to {path}")


if __name__ == "__main__":
    main()
