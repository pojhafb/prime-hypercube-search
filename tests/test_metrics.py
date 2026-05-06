import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pandas as pd

from primecube.analysis.metrics import summarize
from primecube.analysis.wins import wins_vs_standard, overall_winner_by_x
from primecube.analysis.pareto import pareto_frontier, add_multi_objective_score


def _make_df():
    rows = []
    for x in [101, 103, 107, 109, 113]:
        rows.append(dict(
            test_m=8, x=x, x_odd=x,
            strategy="standard_odd_increment",
            found_prime=x + 2, checks=2,
            hamming_distance=3, arithmetic_distance=2,
            elapsed_sec=0.001,
        ))
        rows.append(dict(
            test_m=8, x=x, x_odd=x,
            strategy="low_bit_first_no_bit0",
            found_prime=x + 4, checks=5,
            hamming_distance=1, arithmetic_distance=4,
            elapsed_sec=0.001,
        ))
        rows.append(dict(
            test_m=8, x=x, x_odd=x,
            strategy="uniform_random_no_bit0",
            found_prime=x + 6, checks=8,
            hamming_distance=2, arithmetic_distance=6,
            elapsed_sec=0.001,
        ))
    return pd.DataFrame(rows)


def test_summarize_columns():
    df = _make_df()
    summary = summarize(df)
    assert "avg_checks" in summary.columns
    assert "avg_hamming_distance" in summary.columns
    assert "speedup_vs_standard_odd" in summary.columns


def test_summarize_row_count():
    df = _make_df()
    summary = summarize(df)
    assert len(summary) == 3  # 3 strategies × 1 test_m


def test_wins_vs_standard_columns():
    df = _make_df()
    wins = wins_vs_standard(df)
    assert "strategy_win_rate" in wins.columns
    assert "standard_wins" in wins.columns


def test_overall_winner_all_standard():
    df = _make_df()
    overall = overall_winner_by_x(df)
    # standard has fewest checks (2 vs 5 vs 8)
    top = overall[overall["test_m"] == 8].sort_values("winner_share", ascending=False)
    assert top.iloc[0]["strategy"] == "standard_odd_increment"


def test_pareto_frontier_no_crashes():
    df = _make_df()
    summary = summarize(df)
    pareto = pareto_frontier(summary, "avg_checks", "avg_hamming_distance")
    assert "is_pareto_frontier" in pareto.columns


def test_multi_objective_score_exists():
    df = _make_df()
    summary = summarize(df)
    scored = add_multi_objective_score(summary)
    assert "multi_objective_score" in scored.columns
    assert scored["multi_objective_score"].notna().all()
