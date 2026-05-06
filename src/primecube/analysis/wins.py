from __future__ import annotations

from typing import Dict

import pandas as pd


def wins_vs_standard(df: pd.DataFrame) -> pd.DataFrame:
    """
    Per-x pairwise comparison of each strategy against standard_odd_increment.

    For each starting point x, counts:
      - how often the strategy uses fewer checks (strategy_wins)
      - how often standard uses fewer checks (standard_wins)
      - ties

    Also records average check delta and average distance deltas.
    """
    rows = []

    for test_m in sorted(df["test_m"].unique()):
        df_m = df[df["test_m"] == test_m]

        standard = (
            df_m[df_m["strategy"] == "standard_odd_increment"]
            [["x", "checks", "hamming_distance", "arithmetic_distance"]]
            .rename(columns={
                "checks": "standard_checks",
                "hamming_distance": "standard_hamming",
                "arithmetic_distance": "standard_arithmetic",
            })
        )

        for strategy in sorted(df_m["strategy"].unique()):
            if strategy == "standard_odd_increment":
                continue

            candidate = (
                df_m[df_m["strategy"] == strategy]
                [["x", "checks", "hamming_distance", "arithmetic_distance"]]
                .rename(columns={
                    "checks": "strategy_checks",
                    "hamming_distance": "strategy_hamming",
                    "arithmetic_distance": "strategy_arithmetic",
                })
            )

            merged = standard.merge(candidate, on="x", how="inner")
            total = len(merged)
            if total == 0:
                continue

            s_wins = int((merged["strategy_checks"] < merged["standard_checks"]).sum())
            t_wins = int((merged["strategy_checks"] > merged["standard_checks"]).sum())
            ties = int((merged["strategy_checks"] == merged["standard_checks"]).sum())

            rows.append({
                "test_m": test_m,
                "strategy": strategy,
                "total_cases": total,
                "strategy_wins": s_wins,
                "standard_wins": t_wins,
                "ties": ties,
                "strategy_win_rate": s_wins / total,
                "standard_win_rate": t_wins / total,
                "tie_rate": ties / total,
                "avg_check_delta": (merged["strategy_checks"] - merged["standard_checks"]).mean(),
                "median_check_delta": (merged["strategy_checks"] - merged["standard_checks"]).median(),
                "avg_hamming_delta": (merged["strategy_hamming"] - merged["standard_hamming"]).mean(),
                "avg_arithmetic_delta": (merged["strategy_arithmetic"] - merged["standard_arithmetic"]).mean(),
            })

    return pd.DataFrame(rows).sort_values(
        ["test_m", "strategy_win_rate"], ascending=[True, False]
    ).reset_index(drop=True)


def overall_winner_by_x(df: pd.DataFrame) -> pd.DataFrame:
    """
    For each x, finds which strategy(ies) achieved the minimum check count.
    Ties are split fractionally.

    Returns winner_share: fraction of starting points where each strategy is best.
    """
    rows = []

    for test_m in sorted(df["test_m"].unique()):
        df_m = df[df["test_m"] == test_m]
        total_x = df_m["x"].nunique()
        win_counter: Dict[str, float] = {}

        for _, group in df_m.groupby("x"):
            min_checks = group["checks"].min()
            winners = group[group["checks"] == min_checks]["strategy"].tolist()

            for winner in winners:
                win_counter[winner] = win_counter.get(winner, 0.0) + 1.0 / len(winners)

        for strategy, wins in win_counter.items():
            rows.append({
                "test_m": test_m,
                "strategy": strategy,
                "weighted_wins": wins,
                "winner_share": wins / total_x if total_x else None,
                "total_x": total_x,
            })

    return pd.DataFrame(rows).sort_values(
        ["test_m", "winner_share"], ascending=[True, False]
    ).reset_index(drop=True)
