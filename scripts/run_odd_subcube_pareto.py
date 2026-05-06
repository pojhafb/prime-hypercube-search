"""
Main experiment: odd-subcube Pareto analysis.

Quick run (default):
    python scripts/run_odd_subcube_pareto.py

Larger credibility run:
    python scripts/run_odd_subcube_pareto.py --train-m 24 --test-ms 32 40 48 --train-samples 20000 --test-samples 50000
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pandas as pd

from primecube.core.models import ExperimentConfig
from primecube.experiments.runner import ExperimentRunner, build_standard_policy_suite
from primecube.analysis.metrics import summarize
from primecube.analysis.wins import wins_vs_standard, overall_winner_by_x
from primecube.analysis.pareto import pareto_frontier, add_multi_objective_score
from primecube.plotting.charts import (
    plot_avg_checks,
    plot_wins_vs_standard,
    plot_overall_winner_share,
    plot_hamming_vs_arithmetic,
    plot_pareto_checks_vs_hamming,
    plot_pareto_checks_vs_log_arithmetic,
    plot_multi_objective_score,
)

RESULTS_RAW = Path("results/raw")
RESULTS_SUMMARIES = Path("results/summaries")
RESULTS_PLOTS = Path("results/plots")

for d in [RESULTS_RAW, RESULTS_SUMMARIES, RESULTS_PLOTS]:
    d.mkdir(parents=True, exist_ok=True)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--train-m", type=int, default=20)
    p.add_argument("--test-ms", type=int, nargs="+", default=[24, 28, 32])
    p.add_argument("--train-samples", type=int, default=5_000)
    p.add_argument("--test-samples", type=int, default=10_000)
    p.add_argument("--max-radius", type=int, default=4)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--odd-increment-limit", type=int, default=128)
    p.add_argument("--lambda-h", type=float, default=1.0)
    p.add_argument("--lambda-a", type=float, default=0.25)
    p.add_argument("--show-plots", action="store_true")
    return p.parse_args()


def main():
    args = parse_args()

    config = ExperimentConfig(
        train_m=args.train_m,
        test_ms=args.test_ms,
        train_samples=args.train_samples,
        test_samples=args.test_samples,
        max_radius=args.max_radius,
        seed=args.seed,
        odd_increment_limit=args.odd_increment_limit,
    )

    tag = f"train_m{config.train_m}_test_m{'_'.join(map(str, config.test_ms))}"

    print("Building policy suite...")
    policies = build_standard_policy_suite(config)

    print(f"\nRunning {len(policies)} policies across {config.test_ms}...")
    runner = ExperimentRunner(config=config, policies=policies)
    df = runner.run()

    raw_path = RESULTS_RAW / f"raw_{tag}.csv"
    df.to_csv(raw_path, index=False)
    print(f"\nRaw results saved: {raw_path}")

    summary = summarize(df)
    summary.to_csv(RESULTS_SUMMARIES / f"summary_{tag}.csv", index=False)

    w_vs_std = wins_vs_standard(df)
    w_vs_std.to_csv(RESULTS_SUMMARIES / f"wins_vs_standard_{tag}.csv", index=False)

    overall = overall_winner_by_x(df)
    overall.to_csv(RESULTS_SUMMARIES / f"overall_winners_{tag}.csv", index=False)

    scored = add_multi_objective_score(summary, lambda_h=args.lambda_h, lambda_a=args.lambda_a)
    scored.to_csv(RESULTS_SUMMARIES / f"multi_objective_{tag}.csv", index=False)

    pareto_h = pareto_frontier(summary, "avg_checks", "avg_hamming_distance")
    pareto_h.to_csv(RESULTS_SUMMARIES / f"pareto_checks_hamming_{tag}.csv", index=False)

    import math
    summary_a = summary.copy()
    summary_a["log2_avg_arithmetic_distance_plus_1"] = summary_a["avg_arithmetic_distance"].apply(
        lambda x: math.log2(1 + x) if pd.notna(x) else None
    )
    pareto_a = pareto_frontier(summary_a, "avg_checks", "log2_avg_arithmetic_distance_plus_1")
    pareto_a.to_csv(RESULTS_SUMMARIES / f"pareto_checks_log_arithmetic_{tag}.csv", index=False)

    print("\n===== Summary =====")
    print(summary.to_string(index=False))

    print("\n===== Wins vs Standard =====")
    print(w_vs_std.to_string(index=False))

    print("\n===== Overall Winner Share =====")
    print(overall.to_string(index=False))

    print("\n===== Multi-objective Score =====")
    print(scored[["test_m", "strategy", "multi_objective_score"]].to_string(index=False))

    print("\n===== Pareto Frontier: Checks vs Hamming =====")
    frontier = pareto_h[pareto_h["is_pareto_frontier"]]
    print(frontier[["test_m", "strategy", "avg_checks", "avg_hamming_distance"]].to_string(index=False))

    plot_avg_checks(summary, out_dir=RESULTS_PLOTS, show=args.show_plots)
    plot_wins_vs_standard(w_vs_std, out_dir=RESULTS_PLOTS, show=args.show_plots)
    plot_overall_winner_share(overall, out_dir=RESULTS_PLOTS, show=args.show_plots)
    plot_hamming_vs_arithmetic(summary, out_dir=RESULTS_PLOTS, show=args.show_plots)
    plot_pareto_checks_vs_hamming(summary, out_dir=RESULTS_PLOTS, show=args.show_plots)
    plot_pareto_checks_vs_log_arithmetic(summary, out_dir=RESULTS_PLOTS, show=args.show_plots)
    plot_multi_objective_score(scored, out_dir=RESULTS_PLOTS, show=args.show_plots)

    print(f"\nAll plots saved to {RESULTS_PLOTS}/")


if __name__ == "__main__":
    main()
