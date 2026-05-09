"""
Benchmark: SieveAwarePolicy vs LowBitFirst vs UniformRandom.

Sieve theory predicts that flip masks with high S_xor produce more prime pairs.
If SieveAwarePolicy (which ranks flip sets by S_xor within each Hamming radius)
outperforms the bit-ordering baselines, the singular series is operationally
useful — not just descriptively accurate.

Usage:
    python scripts/run_sieve_aware_search.py --m 48 --n-samples 10000
    python scripts/run_sieve_aware_search.py --ms 32 40 48 --n-samples 5000

Output:
    results/summaries/sieve_aware_comparison.csv
    results/plots/sieve_aware/
"""
from __future__ import annotations

import argparse
import random
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from primecube.policies.hamming_policies import (
    LowBitFirstPolicy,
    HighBitFirstPolicy,
    UniformRandomPolicy,
)
from primecube.policies.sieve_aware_policy import SieveAwarePolicy

RESULTS_DIR = Path(__file__).parent.parent / "results"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Compare SieveAwarePolicy to baselines")
    p.add_argument("--ms", nargs="+", type=int, default=[32, 40, 48],
                   help="Dimensions to test (default: 32 40 48)")
    p.add_argument("--m", type=int, default=None,
                   help="Single dimension shorthand (overrides --ms)")
    p.add_argument("--n-samples", type=int, default=10_000,
                   help="Starting points to sample per (m, policy) (default: 10000)")
    p.add_argument("--max-radius", type=int, default=4,
                   help="Maximum Hamming radius to search (default: 4)")
    p.add_argument("--sieve-m", type=int, default=18,
                   help="Range [1,2^sieve_m) for S_xor estimation (default: 18)")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--show-plots", action="store_true")
    return p.parse_args()


def run_policy(policy, xs: list[int], m: int) -> pd.DataFrame:
    rows = []
    t0 = time.time()
    for i, x in enumerate(xs):
        if i % 5_000 == 0 and i > 0:
            elapsed = time.time() - t0
            eta = elapsed / i * (len(xs) - i)
            print(f"      {i}/{len(xs)}  ({elapsed:.0f}s elapsed, ~{eta:.0f}s left)")
        result = policy.search(x, m)
        rows.append({
            "m": m,
            "strategy": result.strategy,
            "x": result.x,
            "found": result.found_prime is not None,
            "checks": result.checks,
            "hamming_distance": result.hamming_distance,
            "elapsed_sec": result.elapsed_sec,
        })
    return pd.DataFrame(rows)


def summarize_df(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby(["m", "strategy"])
        .agg(
            n=("checks", "count"),
            found_rate=("found", "mean"),
            mean_checks=("checks", "mean"),
            median_checks=("checks", "median"),
            p90_checks=("checks", lambda s: s.quantile(0.90)),
            mean_hamming=("hamming_distance", "mean"),
        )
        .reset_index()
        .sort_values(["m", "mean_checks"])
        .reset_index(drop=True)
    )


def add_speedup(summary: pd.DataFrame, baseline: str = "low_bit_first_no_bit0") -> pd.DataFrame:
    summary = summary.copy()
    summary["speedup_vs_lbf"] = float("nan")
    for m in summary["m"].unique():
        mask_m = summary["m"] == m
        ref = summary.loc[mask_m & (summary["strategy"] == baseline), "mean_checks"]
        if len(ref) == 0:
            continue
        ref_val = float(ref.iloc[0])
        summary.loc[mask_m, "speedup_vs_lbf"] = ref_val / summary.loc[mask_m, "mean_checks"]
    return summary


def plot_mean_checks(summary: pd.DataFrame, out_dir: Path, show: bool) -> None:
    strategies = summary["strategy"].unique()
    ms = sorted(summary["m"].unique())
    colors = {
        "low_bit_first_no_bit0": "steelblue",
        "high_bit_first_no_bit0": "darkorange",
        "uniform_random_no_bit0": "grey",
    }
    fig, ax = plt.subplots(figsize=(8, 5))
    for strat in strategies:
        sub = summary[summary["strategy"] == strat].sort_values("m")
        color = None
        for prefix, c in colors.items():
            if strat.startswith(prefix[:8]):
                color = c
        if "sieve" in strat:
            color = "tomato"
        ax.plot(sub["m"], sub["mean_checks"], marker="o", label=strat, color=color)
    ax.set_xlabel("m (bit dimension)")
    ax.set_ylabel("Mean checks to find prime")
    ax.set_title("SieveAwarePolicy vs baselines: mean checks")
    ax.legend(fontsize=8)
    fig.tight_layout()
    out_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_dir / "sieve_mean_checks.png", dpi=150, bbox_inches="tight")
    if show:
        plt.show()
    plt.close(fig)


def plot_speedup(summary: pd.DataFrame, out_dir: Path, show: bool) -> None:
    sieve_rows = summary[summary["strategy"].str.contains("sieve")]
    if sieve_rows.empty:
        return
    ms = sorted(sieve_rows["m"].unique())
    speedups = [
        float(sieve_rows.loc[sieve_rows["m"] == m, "speedup_vs_lbf"].iloc[0])
        for m in ms
    ]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(ms, speedups, color="tomato", alpha=0.8, width=3)
    ax.axhline(1.0, color="black", linestyle="--", linewidth=1, label="no speedup")
    ax.set_xlabel("m")
    ax.set_ylabel("Speedup vs LowBitFirst  (ratio of mean checks)")
    ax.set_title("SieveAwarePolicy speedup over LowBitFirst")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_dir / "sieve_speedup.png", dpi=150, bbox_inches="tight")
    if show:
        plt.show()
    plt.close(fig)


def main() -> None:
    args = parse_args()
    ms = [args.m] if args.m is not None else args.ms

    policies = [
        LowBitFirstPolicy(max_radius=args.max_radius, seed=args.seed),
        HighBitFirstPolicy(max_radius=args.max_radius, seed=args.seed),
        UniformRandomPolicy(max_radius=args.max_radius, seed=args.seed),
        SieveAwarePolicy(
            max_radius=args.max_radius,
            sieve_m=args.sieve_m,
            small_primes=[3, 5, 7, 11, 13, 17, 19, 23],
        ),
    ]

    all_rows: list[pd.DataFrame] = []
    rng = random.Random(args.seed)

    for m in ms:
        print(f"\n{'='*60}")
        print(f"  m = {m}   n_samples = {args.n_samples}")
        xs = [rng.randrange(1 << (m - 1), 1 << m) for _ in range(args.n_samples)]

        for policy in policies:
            print(f"\n  policy: {policy.name}")
            df_p = run_policy(policy, xs, m)
            all_rows.append(df_p)
            sub = df_p.groupby("strategy").agg(
                found_rate=("found", "mean"),
                mean_checks=("checks", "mean"),
                median_checks=("checks", "median"),
            ).reset_index()
            print(sub.to_string(index=False))

    combined = pd.concat(all_rows, ignore_index=True)
    summary = summarize_df(combined)
    summary = add_speedup(summary)

    sum_dir = RESULTS_DIR / "summaries"
    plot_dir = RESULTS_DIR / "plots" / "sieve_aware"
    sum_dir.mkdir(parents=True, exist_ok=True)

    csv_path = sum_dir / "sieve_aware_comparison.csv"
    summary.to_csv(csv_path, index=False)
    print(f"\nSummary saved to {csv_path}")

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    cols = ["m", "strategy", "found_rate", "mean_checks", "median_checks",
            "p90_checks", "mean_hamming", "speedup_vs_lbf"]
    print(summary[cols].to_string(index=False))

    # Sieve vs LBF head-to-head
    print("\n--- SieveAware vs LowBitFirst speedup ---")
    sieve = summary[summary["strategy"].str.contains("sieve")][["m", "mean_checks", "speedup_vs_lbf"]]
    print(sieve.to_string(index=False))

    plot_mean_checks(summary, plot_dir, args.show_plots)
    plot_speedup(summary, plot_dir, args.show_plots)


if __name__ == "__main__":
    main()
