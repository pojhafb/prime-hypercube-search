"""
Full random-baseline comparison.

Runs both Hamming-ball discrepancy and edge-count experiments on:
  - real primes
  - a random subset of the odd subcube with the same density

Produces a unified comparison summary.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pandas as pd

from primecube.hypercube_stats import (
    PrimeIndicator, HammingBallDiscrepancy, PrimeEdgeCounter, RandomPrimeLikeSet
)
from primecube.plotting.hypercube_plots import (
    plot_z_score_histogram, plot_discrepancy_by_radius, plot_edge_ratio_by_bit
)

RESULTS_DIR = Path(__file__).parent.parent / "results"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Full prime vs random-baseline comparison")
    p.add_argument("--ms", nargs="+", type=int, default=[16, 18, 20])
    p.add_argument("--radii", nargs="+", type=int, default=[1, 2, 3, 4])
    p.add_argument("--samples", type=int, default=2000)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--show-plots", action="store_true")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    raw_dir = RESULTS_DIR / "raw"
    sum_dir = RESULTS_DIR / "summaries"
    plot_dir = RESULTS_DIR / "plots" / "baseline_comparison"
    for d in [raw_dir, sum_dir, plot_dir]:
        d.mkdir(parents=True, exist_ok=True)

    disc_frames: list[pd.DataFrame] = []
    edge_summaries: list[dict] = []

    for m in args.ms:
        print(f"\n=== m={m} ===")
        pi = PrimeIndicator(m, odd_only=True)
        prime_set = pi.prime_set()
        density = len(prime_set) / len(pi.vertices())
        rng_set = RandomPrimeLikeSet(pi.vertices(), density, seed=args.seed)

        # --- Discrepancy ---
        for src, pset in [("primes", prime_set), ("random_baseline", rng_set.member_set())]:
            exp = HammingBallDiscrepancy(m, args.radii, args.samples, args.seed, source=src)
            df = exp.run(prime_set=pset, density=density)
            disc_frames.append(df)

        combined_disc = pd.concat(
            [f for f in disc_frames if f["m"].iloc[0] == m], ignore_index=True
        )
        plot_z_score_histogram(combined_disc, out_dir=plot_dir, show=args.show_plots)
        plot_discrepancy_by_radius(combined_disc, out_dir=plot_dir, show=args.show_plots)

        # --- Edge counts ---
        for src, pset in [("primes", prime_set), ("random_baseline", rng_set.member_set())]:
            bit_df, summary = PrimeEdgeCounter(m, odd_only=True).hamming_one_edges(prime_set=pset)
            edge_summaries.append({**summary, "m": m, "source": src})
            if src == "primes":
                plot_edge_ratio_by_bit(bit_df, m, out_dir=plot_dir, show=args.show_plots)

        # Print quick comparison
        primes_edges = next(s for s in edge_summaries if s["m"] == m and s["source"] == "primes")
        rnd_edges    = next(s for s in edge_summaries if s["m"] == m and s["source"] == "random_baseline")
        print(f"  Prime-prime edges (observed): {primes_edges['total_prime_prime_edges']}")
        print(f"  Random-set edges (observed):  {rnd_edges['total_prime_prime_edges']}")
        print(f"  Expected (random model):      {primes_edges['total_expected_edges']:.1f}")

    # Save combined results
    all_disc = pd.concat(disc_frames, ignore_index=True)
    all_disc.to_csv(raw_dir / "baseline_comparison_discrepancy.csv", index=False)
    pd.DataFrame(edge_summaries).to_csv(sum_dir / "baseline_comparison_edges.csv", index=False)
    print(f"\nResults saved to {raw_dir} and {sum_dir}")


if __name__ == "__main__":
    main()
