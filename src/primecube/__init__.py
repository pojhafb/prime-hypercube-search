"""
primecube — prime search in the binary hypercube.

Top-level re-exports for convenience:

    from primecube import ExperimentConfig, ExperimentRunner, summarize
"""
from primecube.core import ExperimentConfig, SearchResult
from primecube.experiments import ExperimentRunner, build_standard_policy_suite
from primecube.analysis import summarize, wins_vs_standard, overall_winner_by_x
from primecube.analysis import pareto_frontier, add_multi_objective_score

__all__ = [
    "ExperimentConfig",
    "ExperimentRunner",
    "SearchResult",
    "add_multi_objective_score",
    "build_standard_policy_suite",
    "overall_winner_by_x",
    "pareto_frontier",
    "summarize",
    "wins_vs_standard",
]
