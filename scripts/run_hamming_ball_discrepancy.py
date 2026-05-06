"""
Hamming-ball prime-count discrepancy experiment.

For each m and radius r, sample N random center vertices x from Q_m^odd,
count primes inside B(x,r), compare to density * |B(x,r)|, and report
the normalized z-score.  Outputs raw CSV + summary CSV + plots.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pandas as pd

from primecube.hypercube_stats import PrimeIndicator, HammingBallDiscrepancy, RandomPrimeLikeSet
from primecube.plotting.hypercube_plots import plot_z_score_histogram, plot_discrepancy_by_radius

RESULTS_DIR = Path(__file__).parent.parent / "results"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Hamming-ball discrepancy experiment")
    p.add_argument("--ms", nargs="+", type=int, default=[16, 18, 20],
                   help="Hypercube dimensions (default: 16 18 20)")
    p.add_argument("--radii", nargs="+", type=int, default=[1, 2, 3, 4],
                   help="Hamming radii (default: 1 2 3 4)")
    p.add_argument("--samples", type=int, default=2000,
                   help="Center samples per m (default: 2000)")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--show-plots", action="store_true")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    raw_dir = RESULTS_DIR / "raw"
    sum_dir = RESULTS_DIR / "summaries"
    plot_dir = RESULTS_DIR / "plots" / "discrepancy"
    raw_dir.mkdir(parents=True, exist_ok=True)
    sum_dir.mkdir(parents=True, exist_ok=True)

    all_frames: list[pd.DataFrame] = []

    for m in args.ms:
        print(f"\n=== m={m} ===")
        pi = PrimeIndicator(m, odd_only=True)
        prime_set = pi.prime_set()
        density = len(prime_set) / len(pi.vertices())
        print(f"  Prime density: {density:.6f}  ({len(prime_set)} primes / {len(pi.vertices())} vertices)")

        # Real primes
        exp_real = HammingBallDiscrepancy(m, args.radii, args.samples, args.seed, source="primes")
        df_real = exp_real.run(prime_set=prime_set, density=density)

        # Random baseline with same density
        rng_set = RandomPrimeLikeSet(pi.vertices(), density, seed=args.seed + 1)
        exp_rnd = HammingBallDiscrepancy(m, args.radii, args.samples, args.seed + 2, source="random_baseline")
        df_rnd = exp_rnd.run(prime_set=rng_set.member_set(), density=density)

        df_m = pd.concat([df_real, df_rnd], ignore_index=True)
        all_frames.append(df_m)

        plot_z_score_histogram(df_m, out_dir=plot_dir, show=args.show_plots)
        plot_discrepancy_by_radius(df_m, out_dir=plot_dir, show=args.show_plots)

    all_df = pd.concat(all_frames, ignore_index=True)
    raw_path = raw_dir / "hamming_ball_discrepancy.csv"
    all_df.to_csv(raw_path, index=False)
    print(f"\nRaw results saved to {raw_path}")

    summary = (
        all_df.groupby(["m", "radius", "source"])
        .agg(
            mean_z=("z_score", "mean"),
            std_z=("z_score", "std"),
            mean_disc=("discrepancy", "mean"),
            std_disc=("discrepancy", "std"),
            samples=("z_score", "count"),
        )
        .reset_index()
    )
    sum_path = sum_dir / "hamming_ball_discrepancy_summary.csv"
    summary.to_csv(sum_path, index=False)
    print(f"Summary saved to {sum_path}")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
