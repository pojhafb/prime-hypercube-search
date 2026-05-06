from __future__ import annotations

import math
from pathlib import Path
from typing import Optional

import matplotlib.pyplot as plt
import pandas as pd

from primecube.analysis.pareto import pareto_frontier


def _save_or_show(fig: plt.Figure, path: Optional[Path], show: bool):
    if path:
        path.parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(path, bbox_inches="tight", dpi=150)
    if show:
        plt.show()
    plt.close(fig)


def plot_avg_checks(
    summary: pd.DataFrame,
    out_dir: Optional[Path] = None,
    show: bool = False,
):
    for test_m in sorted(summary["test_m"].unique()):
        sub = summary[summary["test_m"] == test_m].sort_values("avg_checks")

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(sub["strategy"], sub["avg_checks"])
        ax.set_title(f"Average Candidate Checks by Strategy  (m={test_m})")
        ax.set_xlabel("Strategy")
        ax.set_ylabel("Average checks")
        ax.tick_params(axis="x", rotation=45)
        fig.tight_layout()

        path = (out_dir / f"avg_checks_m{test_m}.png") if out_dir else None
        _save_or_show(fig, path, show)


def plot_wins_vs_standard(
    wins_df: pd.DataFrame,
    out_dir: Optional[Path] = None,
    show: bool = False,
):
    for test_m in sorted(wins_df["test_m"].unique()):
        sub = wins_df[wins_df["test_m"] == test_m].sort_values(
            "strategy_win_rate", ascending=False
        )

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(sub["strategy"], sub["strategy_win_rate"])
        ax.set_title(f"Win Rate vs Standard Odd Increment  (m={test_m})")
        ax.set_xlabel("Strategy")
        ax.set_ylabel("Fraction of x where strategy wins")
        ax.tick_params(axis="x", rotation=45)
        fig.tight_layout()

        path = (out_dir / f"wins_vs_standard_m{test_m}.png") if out_dir else None
        _save_or_show(fig, path, show)


def plot_overall_winner_share(
    winner_df: pd.DataFrame,
    out_dir: Optional[Path] = None,
    show: bool = False,
):
    for test_m in sorted(winner_df["test_m"].unique()):
        sub = winner_df[winner_df["test_m"] == test_m].sort_values(
            "winner_share", ascending=False
        )

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(sub["strategy"], sub["winner_share"])
        ax.set_title(f"Overall Winner Share by x  (m={test_m})")
        ax.set_xlabel("Strategy")
        ax.set_ylabel("Winner share")
        ax.tick_params(axis="x", rotation=45)
        fig.tight_layout()

        path = (out_dir / f"winner_share_m{test_m}.png") if out_dir else None
        _save_or_show(fig, path, show)


def plot_hamming_vs_arithmetic(
    summary: pd.DataFrame,
    out_dir: Optional[Path] = None,
    show: bool = False,
):
    for test_m in sorted(summary["test_m"].unique()):
        sub = summary[summary["test_m"] == test_m]

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.scatter(sub["avg_arithmetic_distance"], sub["avg_hamming_distance"])

        for _, row in sub.iterrows():
            ax.annotate(
                row["strategy"],
                (row["avg_arithmetic_distance"], row["avg_hamming_distance"]),
                fontsize=7,
            )

        ax.set_title(f"Hamming vs Arithmetic Distance  (m={test_m})")
        ax.set_xlabel("Average arithmetic distance |p - x|")
        ax.set_ylabel("Average Hamming distance")
        fig.tight_layout()

        path = (out_dir / f"hamming_vs_arithmetic_m{test_m}.png") if out_dir else None
        _save_or_show(fig, path, show)


def plot_pareto_checks_vs_hamming(
    summary: pd.DataFrame,
    out_dir: Optional[Path] = None,
    show: bool = False,
):
    for test_m in sorted(summary["test_m"].unique()):
        sub = summary[summary["test_m"] == test_m].copy()
        pareto = pareto_frontier(sub, "avg_checks", "avg_hamming_distance")

        fig, ax = plt.subplots(figsize=(10, 6))

        for _, row in pareto.iterrows():
            marker = "o" if row["is_pareto_frontier"] else "x"
            size = 90 if row["is_pareto_frontier"] else 50
            ax.scatter(row["avg_checks"], row["avg_hamming_distance"], marker=marker, s=size)
            label = row["strategy"] + (" *" if row["is_pareto_frontier"] else "")
            ax.annotate(label, (row["avg_checks"], row["avg_hamming_distance"]), fontsize=7)

        ax.set_title(f"Pareto: Checks vs Hamming Distance  (m={test_m})  (* = frontier)")
        ax.set_xlabel("Average candidate checks")
        ax.set_ylabel("Average Hamming distance")
        fig.tight_layout()

        path = (out_dir / f"pareto_checks_hamming_m{test_m}.png") if out_dir else None
        _save_or_show(fig, path, show)


def plot_pareto_checks_vs_log_arithmetic(
    summary: pd.DataFrame,
    out_dir: Optional[Path] = None,
    show: bool = False,
):
    summary = summary.copy()
    summary["log2_arith"] = summary["avg_arithmetic_distance"].apply(
        lambda x: math.log2(1 + x) if pd.notna(x) else None
    )

    for test_m in sorted(summary["test_m"].unique()):
        sub = summary[summary["test_m"] == test_m].copy()
        pareto = pareto_frontier(sub, "avg_checks", "log2_arith")

        fig, ax = plt.subplots(figsize=(10, 6))

        for _, row in pareto.iterrows():
            marker = "o" if row["is_pareto_frontier"] else "x"
            size = 90 if row["is_pareto_frontier"] else 50
            ax.scatter(row["avg_checks"], row["log2_arith"], marker=marker, s=size)
            label = row["strategy"] + (" *" if row["is_pareto_frontier"] else "")
            ax.annotate(label, (row["avg_checks"], row["log2_arith"]), fontsize=7)

        ax.set_title(f"Pareto: Checks vs log2(Arithmetic+1)  (m={test_m})  (* = frontier)")
        ax.set_xlabel("Average candidate checks")
        ax.set_ylabel("log2(avg arithmetic distance + 1)")
        fig.tight_layout()

        path = (out_dir / f"pareto_checks_log_arithmetic_m{test_m}.png") if out_dir else None
        _save_or_show(fig, path, show)


def plot_multi_objective_score(
    scored_summary: pd.DataFrame,
    out_dir: Optional[Path] = None,
    show: bool = False,
):
    for test_m in sorted(scored_summary["test_m"].unique()):
        sub = scored_summary[scored_summary["test_m"] == test_m].sort_values(
            "multi_objective_score"
        )

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(sub["strategy"], sub["multi_objective_score"])
        ax.set_title(
            f"Multi-objective Score  (m={test_m})\n"
            f"score = checks + λH·Hamming + λA·log2(1+arithmetic)  (lower is better)"
        )
        ax.set_xlabel("Strategy")
        ax.set_ylabel("Score")
        ax.tick_params(axis="x", rotation=45)
        fig.tight_layout()

        path = (out_dir / f"multi_objective_m{test_m}.png") if out_dir else None
        _save_or_show(fig, path, show)


def plot_bit_score_distribution(
    bit_score: dict,
    train_m: int,
    out_dir: Optional[Path] = None,
    show: bool = False,
):
    bits = sorted(bit_score.keys())
    scores = [bit_score[b] for b in bits]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(bits, scores)
    ax.set_title(f"Learned Bit Usefulness Scores  (train m={train_m})")
    ax.set_xlabel("Bit position  (0 = least significant)")
    ax.set_ylabel("Score")
    fig.tight_layout()

    path = (out_dir / f"bit_scores_train_m{train_m}.png") if out_dir else None
    _save_or_show(fig, path, show)
