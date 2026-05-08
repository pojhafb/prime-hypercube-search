"""
XOR autocorrelation experiment.

Computes C(a) = |{p prime : p XOR a prime}| for all even masks of small
Hamming weight, via Walsh-Hadamard Transform in O(m * 2^m) time.

Key question: does rho(a) = C(a) / E[C(a)] depend on the Hamming weight
of the mask, or on a mod small_primes?  Expected ~0.664 for weight-1 masks
(consistent with Hamming-1 edge experiments).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import numpy as np
import pandas as pd

from primecube.hypercube_stats import PrimeIndicator
from primecube.hypercube_stats.xor_autocorr import XORAutocorrelation
from primecube.hypercube_stats.random_baseline import RandomPrimeLikeSet
from primecube.plotting.xor_plots import (
    plot_rho_by_weight,
    plot_rho_histogram,
    plot_rho_by_mod,
    plot_rho_vs_weight_trend,
)

RESULTS_DIR = Path(__file__).parent.parent / "results"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="XOR autocorrelation of primes in Q_m^odd")
    p.add_argument("--ms", nargs="+", type=int, default=[16, 18, 20],
                   help="Dimensions (WHT limit: m<=26). Default: 16 18 20")
    p.add_argument("--max-weight", type=int, default=4,
                   help="Max Hamming weight of XOR mask (default: 4)")
    p.add_argument("--small-primes", nargs="+", type=int, default=[3, 5, 7, 11])
    p.add_argument("--n-baselines", type=int, default=10,
                   help="Random baseline seeds for CI on rho (default: 10)")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--show-plots", action="store_true")
    return p.parse_args()


def run_one(
    m: int,
    max_weight: int,
    small_primes: list[int],
    n_baselines: int,
    seed: int,
    out_dir: Path,
    show: bool,
) -> pd.DataFrame:
    print(f"\n{'='*60}")
    print(f"  m = {m}")
    pi = PrimeIndicator(m, odd_only=True)
    prime_set = pi.prime_set()
    vertices = pi.vertices()
    delta = len(prime_set) / len(vertices)
    print(f"  {len(prime_set)} primes  delta={delta:.5f}")

    xac = XORAutocorrelation(m)

    # --- Prime autocorrelation ---
    print("  Computing WHT autocorrelation for primes...")
    C_prime = xac.compute_all(prime_set)
    df_prime = xac.analyze(C_prime, prime_set, max_weight, small_primes)

    # --- Random baseline autocorrelations ---
    bl_rho_by_mask: dict[int, list[float]] = {row["mask"]: [] for _, row in df_prime.iterrows()}
    N_odd = 2 ** (m - 1)
    expected = delta ** 2 * N_odd

    print(f"  Computing {n_baselines} random baseline WHT autocorrelations...")
    for k in range(n_baselines):
        rnd = RandomPrimeLikeSet(vertices, delta, seed=seed + k)
        C_rnd = xac.compute_all(rnd.member_set())
        for mask in bl_rho_by_mask:
            bl_rho_by_mask[mask].append(float(C_rnd[mask]) / expected)

    df_prime["baseline_mean_rho"] = df_prime["mask"].map(
        lambda a: float(np.mean(bl_rho_by_mask[a]))
    )
    df_prime["baseline_std_rho"] = df_prime["mask"].map(
        lambda a: float(np.std(bl_rho_by_mask[a], ddof=1))
    )
    df_prime["sigma_from_baseline"] = (
        (df_prime["rho"] - df_prime["baseline_mean_rho"])
        / df_prime["baseline_std_rho"]
    ).replace([float("inf"), float("-inf")], float("nan"))
    df_prime["m"] = m

    # --- Summary by weight ---
    summary = xac.summary_by_weight(df_prime)
    print("\n  ρ by Hamming weight of mask:")
    print(summary.to_string(index=False))

    # --- Mod-q groupings for weight-1 and weight-2 ---
    for q in small_primes:
        for w in [1, 2]:
            if len(df_prime[df_prime["popcount"] == w]) == 0:
                continue
            mod_summary = xac.summary_by_mod(df_prime, q, weight=w)
            print(f"\n  ρ by mask mod {q}  (weight={w}):")
            print(mod_summary.to_string(index=False))

    # --- Top and bottom masks ---
    print("\n  Top-10 masks by rho (most prime-friendly):")
    print(xac.top_masks(df_prime, 10).to_string(index=False))
    print("\n  Bottom-10 masks by rho (most sieve-repelled):")
    print(xac.top_masks(df_prime, 10, ascending=True).to_string(index=False))

    # --- Plots ---
    weights_to_show = sorted(df_prime["popcount"].unique())
    plot_rho_by_weight(df_prime, m, out_dir=out_dir, show=show)
    plot_rho_histogram(df_prime, m, weights=weights_to_show, out_dir=out_dir, show=show)
    for q in small_primes[:2]:
        plot_rho_by_mod(df_prime, m, q, weights=[1, 2], out_dir=out_dir, show=show)
    plot_rho_vs_weight_trend(summary, m, out_dir=out_dir, show=show)

    return df_prime


def main() -> None:
    args = parse_args()
    raw_dir = RESULTS_DIR / "raw"
    sum_dir = RESULTS_DIR / "summaries"
    plot_dir = RESULTS_DIR / "plots" / "xor_autocorr"
    for d in [raw_dir, sum_dir, plot_dir]:
        d.mkdir(parents=True, exist_ok=True)

    all_frames: list[pd.DataFrame] = []
    for m in args.ms:
        if m > XORAutocorrelation.MAX_M:
            print(f"Skipping m={m}: exceeds MAX_M={XORAutocorrelation.MAX_M}")
            continue
        df = run_one(m, args.max_weight, args.small_primes,
                     args.n_baselines, args.seed, plot_dir, args.show_plots)
        all_frames.append(df)

    if all_frames:
        all_df = pd.concat(all_frames, ignore_index=True)
        raw_path = raw_dir / "xor_autocorr.csv"
        all_df.to_csv(raw_path, index=False)
        print(f"\nAll raw results saved to {raw_path}")

        # Aggregated weight summary across all m
        agg = (
            all_df.groupby(["m", "popcount"])
            .agg(
                n_masks=("rho", "count"),
                mean_rho=("rho", "mean"),
                std_rho=("rho", "std"),
                mean_sigma=("sigma_from_baseline", "mean"),
            )
            .reset_index()
        )
        sum_path = sum_dir / "xor_autocorr_by_weight.csv"
        agg.to_csv(sum_path, index=False)
        print(f"Weight summary saved to {sum_path}")
        print("\nWeight summary across all m:")
        print(agg.to_string(index=False))


if __name__ == "__main__":
    main()
