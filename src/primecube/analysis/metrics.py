from __future__ import annotations

import pandas as pd


def summarize(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate per-strategy statistics across all starting points x.

    Returns one row per (test_m, strategy) with:
      avg/median/p90/p95/p99/max checks
      avg/median Hamming and arithmetic distance
      found_rate, avg_elapsed_ms
      speedup_vs_random_no_bit0, speedup_vs_standard_odd
    """
    summary = (
        df.groupby(["test_m", "strategy"])
        .agg(
            avg_checks=("checks", "mean"),
            median_checks=("checks", "median"),
            p90_checks=("checks", lambda s: s.quantile(0.90)),
            p95_checks=("checks", lambda s: s.quantile(0.95)),
            p99_checks=("checks", lambda s: s.quantile(0.99)),
            max_checks=("checks", "max"),
            avg_hamming_distance=("hamming_distance", "mean"),
            median_hamming_distance=("hamming_distance", "median"),
            avg_arithmetic_distance=("arithmetic_distance", "mean"),
            median_arithmetic_distance=("arithmetic_distance", "median"),
            found_rate=("found_prime", lambda s: s.notna().mean()),
            avg_elapsed_ms=("elapsed_sec", lambda s: 1000.0 * s.mean()),
        )
        .reset_index()
    )

    summary["speedup_vs_random_no_bit0"] = None
    summary["speedup_vs_standard_odd"] = None

    for test_m in summary["test_m"].unique():
        mask = summary["test_m"] == test_m
        sub = summary[mask]

        random_row = sub[sub["strategy"] == "uniform_random_no_bit0"]
        standard_row = sub[sub["strategy"] == "standard_odd_increment"]

        random_avg = float(random_row["avg_checks"].iloc[0]) if len(random_row) > 0 else None
        standard_avg = float(standard_row["avg_checks"].iloc[0]) if len(standard_row) > 0 else None

        if random_avg:
            summary.loc[mask, "speedup_vs_random_no_bit0"] = (
                random_avg / summary.loc[mask, "avg_checks"]
            )

        if standard_avg:
            summary.loc[mask, "speedup_vs_standard_odd"] = (
                standard_avg / summary.loc[mask, "avg_checks"]
            )

    return summary.sort_values(["test_m", "avg_checks"]).reset_index(drop=True)
