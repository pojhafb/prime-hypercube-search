"""
Prime-induced subgraph analysis.

Builds G_m^prime: vertices = P_m ∩ Q_m^odd, edges = Hamming-1 prime pairs.
Analyzes connectivity (components, giant component, isolated vertices),
degree distribution, and comparison to a random same-density null model.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pandas as pd

from primecube.hypercube_stats import PrimeIndicator
from primecube.hypercube_stats.prime_graph import PrimeInducedGraph
from primecube.plotting.xor_plots import (
    plot_component_sizes,
    plot_degree_distribution,
    plot_graph_metrics_vs_m,
)

RESULTS_DIR = Path(__file__).parent.parent / "results"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Prime-induced hypercube subgraph analysis")
    p.add_argument("--ms", nargs="+", type=int, default=[12, 14, 16, 18, 20],
                   help="Dimensions (default: 12 14 16 18 20)")
    p.add_argument("--n-baselines", type=int, default=10,
                   help="Random baseline seeds for comparison (default: 10)")
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--show-plots", action="store_true")
    return p.parse_args()


def print_result(result: dict) -> None:
    m = result["m"]
    n = result["n_primes"]
    print(f"\n  m={m}  |P_m|={n}  edges={result['n_edges']}")
    print(f"  Components:       {result['n_components']}")
    print(f"  Largest:          {result['largest_component']} primes "
          f"({100*result['largest_fraction']:.1f}%)")
    if result["second_largest"]:
        print(f"  2nd largest:      {result['second_largest']} primes")
    print(f"  Isolated (deg=0): {result['isolated_count']} "
          f"({100*result['isolated_fraction']:.1f}%)")
    print(f"  Avg degree:       {result['avg_degree']:.4f}")
    print(f"  Max degree:       {result['max_degree']}")


def main() -> None:
    args = parse_args()
    raw_dir = RESULTS_DIR / "raw"
    sum_dir = RESULTS_DIR / "summaries"
    plot_dir = RESULTS_DIR / "plots" / "prime_graph"
    for d in [raw_dir, sum_dir, plot_dir]:
        d.mkdir(parents=True, exist_ok=True)

    all_results: list[dict] = []
    all_comp_frames: list[pd.DataFrame] = []
    all_degree_frames: list[pd.DataFrame] = []
    comparison_frames: list[pd.DataFrame] = []

    for m in args.ms:
        print(f"\n{'='*60}")
        print(f"  m = {m}")
        pi = PrimeIndicator(m, odd_only=True)
        prime_set = pi.prime_set()
        print(f"  {len(prime_set)} primes in Q_{m}^odd")

        graph = PrimeInducedGraph(m)

        print("  Building prime-induced graph and analyzing connectivity...")
        result = graph.analyze(prime_set)
        print_result(result)

        comp_df = graph.component_size_df(result)
        comp_df["m"] = m
        deg_df = graph.degree_df(result)
        deg_df["m"] = m

        all_results.append(result)
        all_comp_frames.append(comp_df)
        all_degree_frames.append(deg_df)

        # Random baseline comparison
        print(f"  Comparing against {args.n_baselines} random baselines...")
        cdf = graph.compare_to_random(prime_set, n_seeds=args.n_baselines, seed=args.seed)
        cdf["m"] = m
        comparison_frames.append(cdf)
        print("  Metric comparison (prime vs random baseline):")
        print(cdf[["metric", "prime_value", "baseline_mean", "baseline_std",
                    "ratio", "sigma"]].to_string(index=False))

        # Plots
        plot_component_sizes(result, out_dir=plot_dir, show=args.show_plots)
        plot_degree_distribution(result, out_dir=plot_dir, show=args.show_plots)

    # Cross-m plot
    plot_graph_metrics_vs_m(all_results, out_dir=plot_dir, show=args.show_plots)

    # Save outputs
    comp_all = pd.concat(all_comp_frames, ignore_index=True)
    comp_all.to_csv(raw_dir / "prime_graph_components.csv", index=False)

    deg_all = pd.concat(all_degree_frames, ignore_index=True)
    deg_all.to_csv(raw_dir / "prime_graph_degrees.csv", index=False)

    cmp_all = pd.concat(comparison_frames, ignore_index=True)
    cmp_all.to_csv(sum_dir / "prime_graph_vs_random.csv", index=False)

    # Summary table across m
    summary_rows = [
        {
            "m": r["m"],
            "n_primes": r["n_primes"],
            "n_edges": r["n_edges"],
            "n_components": r["n_components"],
            "largest_pct": round(100 * r["largest_fraction"], 1),
            "isolated_pct": round(100 * r["isolated_fraction"], 1),
            "avg_degree": round(r["avg_degree"], 4),
        }
        for r in all_results
    ]
    sum_df = pd.DataFrame(summary_rows)
    sum_df.to_csv(sum_dir / "prime_graph_summary.csv", index=False)

    print(f"\n{'='*60}")
    print("SUMMARY ACROSS m:")
    print(sum_df.to_string(index=False))
    print(f"\nResults saved to {raw_dir} and {sum_dir}")


if __name__ == "__main__":
    main()
