from __future__ import annotations

import math

import pandas as pd


def pareto_frontier(
    summary: pd.DataFrame,
    x_col: str,
    y_col: str,
    lower_is_better_x: bool = True,
    lower_is_better_y: bool = True,
) -> pd.DataFrame:
    """
    Marks each (test_m, strategy) as Pareto-frontier or dominated.

    A strategy is dominated if another strategy is at least as good on both
    axes and strictly better on one axis.
    """
    rows = []

    for test_m in sorted(summary["test_m"].unique()):
        sub = summary[summary["test_m"] == test_m].copy().dropna(subset=[x_col, y_col])

        for _, row in sub.iterrows():
            dominated = False

            for _, other in sub.iterrows():
                if row["strategy"] == other["strategy"]:
                    continue

                def ge(a, b, lower_better):
                    return a <= b if lower_better else a >= b

                def gt(a, b, lower_better):
                    return a < b if lower_better else a > b

                x_ok = ge(other[x_col], row[x_col], lower_is_better_x)
                y_ok = ge(other[y_col], row[y_col], lower_is_better_y)
                x_strict = gt(other[x_col], row[x_col], lower_is_better_x)
                y_strict = gt(other[y_col], row[y_col], lower_is_better_y)

                if x_ok and y_ok and (x_strict or y_strict):
                    dominated = True
                    break

            out = row.to_dict()
            out["pareto_x_col"] = x_col
            out["pareto_y_col"] = y_col
            out["is_pareto_frontier"] = not dominated
            rows.append(out)

    return pd.DataFrame(rows).sort_values(
        ["test_m", "is_pareto_frontier", x_col],
        ascending=[True, False, True],
    ).reset_index(drop=True)


def add_multi_objective_score(
    summary: pd.DataFrame,
    lambda_h: float = 1.0,
    lambda_a: float = 0.25,
) -> pd.DataFrame:
    """
    Adds a combined score (lower is better):

        score = avg_checks
                + lambda_h * avg_hamming_distance
                + lambda_a * log2(1 + avg_arithmetic_distance)

    lambda_h weights bit-space locality.
    lambda_a weights number-line locality (log-compressed).
    """
    summary = summary.copy()

    summary["log2_avg_arithmetic_distance_plus_1"] = summary[
        "avg_arithmetic_distance"
    ].apply(lambda x: math.log2(1 + x) if pd.notna(x) else None)

    summary["multi_objective_score"] = (
        summary["avg_checks"]
        + lambda_h * summary["avg_hamming_distance"]
        + lambda_a * summary["log2_avg_arithmetic_distance_plus_1"]
    )

    summary["lambda_h"] = lambda_h
    summary["lambda_a"] = lambda_a

    return summary.sort_values(["test_m", "multi_objective_score"]).reset_index(drop=True)
