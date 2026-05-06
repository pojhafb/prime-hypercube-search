"""
Prime-prime Hamming-1 edge count experiment.

Counts how many pairs of primes in Q_m^odd differ in exactly one bit,
compared to the random-set expectation: density^2 * |E(Q_m^odd)|.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pandas as pd

from primecube.hypercube_stats import PrimeIndicator, PrimeEdgeCounter, RandomPrimeLikeSet
from primecube.plotting.hypercube_plots import plot_edge_ratio_by_bit

RESULTS_DIR = Path(__file__).parent.parent / "results"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Prime-prime Hamming-1 edge count experiment")
    p.add_argument("--ms", nargs="+", type=int, default=[14, 16, 18, 20],
                   help="Hypercube dimensions (default: 14 16 18 20)")
    p.add_argument("--seed", type=int, default=42)
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
    summaries: list[dict] = []

    for m in args.ms:
        print(f"\n=== m={m} ===")
        pi = PrimeIndicator(m, odd_only=True)
        prime_set = pi.prime_set()
        density = len(prime_set) / len(pi.vertices())

        counter = PrimeEdgeCounter(m, odd_only=True)
        bit_df, summary = counter.hamming_one_edges(prime_set=prime_set)
        bit_df["source"] = "primes"

        # Random baseline
        rng_set = RandomPrimeLikeSet(pi.vertices(), density, seed=args.seed)
        rnd_df, rnd_summary = PrimeEdgeCounter(m, odd_only=True).hamming_one_edges(prime_set=rng_set.member_set())
        rnd_df["source"] = "random_baseline"

        print(f"  Primes: {summary['prime_count']} primes, density={density:.5f}")
        print(f"  Observed prime-prime edges: {summary['total_prime_prime_edges']}")
        print(f"  Expected (random):          {summary['total_expected_edges']:.1f}")
        print(f"  Ratio: {summary['total_prime_prime_edges'] / summary['total_expected_edges']:.4f}")

        combined = pd.concat([bit_df, rnd_df], ignore_index=True)
        all_bit_frames.append(combined)
        summaries.append({**summary, "source": "primes"})
        summaries.append({**rnd_summary, "source": "random_baseline"})

        plot_edge_ratio_by_bit(bit_df, m, out_dir=plot_dir, show=args.show_plots)

    all_df = pd.concat(all_bit_frames, ignore_index=True)
    raw_path = raw_dir / "prime_edge_counts.csv"
    all_df.to_csv(raw_path, index=False)
    print(f"\nRaw bit-level results saved to {raw_path}")

    sum_df = pd.DataFrame(summaries)
    sum_path = sum_dir / "prime_edge_counts_summary.csv"
    sum_df.to_csv(sum_path, index=False)
    print(f"Summary saved to {sum_path}")
    print(sum_df.to_string(index=False))


if __name__ == "__main__":
    main()
