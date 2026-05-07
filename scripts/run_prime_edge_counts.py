"""
Prime-prime Hamming-1 edge count experiment.

Counts how many pairs of primes in Q_m^odd differ in exactly one bit,
compared to the random-set expectation: density^2 * |E(Q_m^odd)|.

Multiple random baseline seeds give a confidence interval on the
null-model ratio, making the prime deficit clearly visible.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import numpy as np
import pandas as pd

from primecube.hypercube_stats import PrimeIndicator, PrimeEdgeCounter, RandomPrimeLikeSet
from primecube.plotting.hypercube_plots import plot_edge_ratio_by_bit

RESULTS_DIR = Path(__file__).parent.parent / "results"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Prime-prime Hamming-1 edge count experiment")
    p.add_argument("--ms", nargs="+", type=int, default=[10, 12, 14, 16, 18, 20, 22],
                   help="Hypercube dimensions (default: 10 12 14 16 18 20 22)")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--n-baselines", type=int, default=20,
                   help="Number of random baseline seeds for CI (default: 20)")
    p.add_argument("--show-plots", action="store_true")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    raw_dir = RESULTS_DIR / "raw"
    sum_dir = RESULTS_DIR / "summaries"
    plot_dir = RESULTS_DIR / "plots" / "edge_counts"
    raw_dir.mkdir(parents=True, exist_ok=True)
    sum_dir.mkdir(parents=True, exist_ok=True)

    all_bit_frames: list[pd.DataFrame] = []
    summary_rows: list[dict] = []

    for m in args.ms:
        print(f"\n=== m={m} ===")
        pi = PrimeIndicator(m, odd_only=True)
        prime_set = pi.prime_set()
        vertices = pi.vertices()
        density = len(prime_set) / len(vertices)
        print(f"  {len(prime_set)} primes / {len(vertices)} vertices  density={density:.5f}")

        # --- Real primes ---
        counter = PrimeEdgeCounter(m, odd_only=True)
        bit_df, summary = counter.hamming_one_edges(prime_set=prime_set)
        bit_df["source"] = "primes"
        obs_edges = summary["total_prime_prime_edges"]
        exp_edges = summary["total_expected_edges"]
        prime_ratio = obs_edges / exp_edges

        # --- Multiple random baselines for CI ---
        baseline_ratios: list[float] = []
        for k in range(args.n_baselines):
            rng_set = RandomPrimeLikeSet(vertices, density, seed=args.seed + k)
            _, rnd_summary = PrimeEdgeCounter(m, odd_only=True).hamming_one_edges(
                prime_set=rng_set.member_set()
            )
            r = rnd_summary["total_prime_prime_edges"] / rnd_summary["total_expected_edges"]
            baseline_ratios.append(r)

        bl_mean = float(np.mean(baseline_ratios))
        bl_std  = float(np.std(baseline_ratios, ddof=1))
        ci_lo   = bl_mean - 1.96 * bl_std
        ci_hi   = bl_mean + 1.96 * bl_std

        print(f"  Prime ratio:         {prime_ratio:.4f}")
        print(f"  Random baseline:     {bl_mean:.4f} ± {bl_std:.4f}  (95% CI [{ci_lo:.4f}, {ci_hi:.4f}])")
        print(f"  Z vs baseline mean:  {(prime_ratio - bl_mean) / bl_std:.2f}σ")

        all_bit_frames.append(bit_df)
        summary_rows.append({
            "m": m,
            "prime_count": summary["prime_count"],
            "density": density,
            "obs_edges": obs_edges,
            "exp_edges": exp_edges,
            "prime_ratio": prime_ratio,
            "baseline_mean": bl_mean,
            "baseline_std": bl_std,
            "ci_lo_95": ci_lo,
            "ci_hi_95": ci_hi,
            "sigma_from_baseline": (prime_ratio - bl_mean) / bl_std if bl_std > 0 else float("nan"),
        })

        plot_edge_ratio_by_bit(bit_df, m, out_dir=plot_dir, show=args.show_plots)

    all_df = pd.concat(all_bit_frames, ignore_index=True)
    raw_path = raw_dir / "prime_edge_counts.csv"
    all_df.to_csv(raw_path, index=False)

    sum_df = pd.DataFrame(summary_rows)
    sum_path = sum_dir / "prime_edge_counts_summary.csv"
    sum_df.to_csv(sum_path, index=False)

    print(f"\n{'='*70}")
    print("SUMMARY")
    print(sum_df[["m", "prime_ratio", "baseline_mean", "baseline_std",
                   "ci_lo_95", "ci_hi_95", "sigma_from_baseline"]].to_string(index=False))
    print(f"\nRaw saved to {raw_path}")
    print(f"Summary saved to {sum_path}")


if __name__ == "__main__":
    main()
