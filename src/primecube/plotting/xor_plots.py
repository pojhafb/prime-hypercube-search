from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def _save(fig: plt.Figure, out_dir: Path | None, filename: str, show: bool) -> None:
    if out_dir is not None:
        out_dir.mkdir(parents=True, exist_ok=True)
        fig.savefig(out_dir / filename, dpi=150, bbox_inches="tight")
    if show:
        plt.show()
    plt.close(fig)


def plot_rho_by_weight(
    df: pd.DataFrame,
    m: int,
    out_dir: Path | None = None,
    show: bool = False,
) -> None:
    """Box plot of rho(a) distribution by Hamming weight of mask."""
    weights = sorted(df["popcount"].unique())
    fig, ax = plt.subplots(figsize=(9, 5))
    data = [df[df["popcount"] == w]["rho"].values for w in weights]
    bp = ax.boxplot(data, positions=weights, widths=0.4, patch_artist=True,
                    manage_ticks=False)
    for patch in bp["boxes"]:
        patch.set_facecolor("steelblue")
        patch.set_alpha(0.7)

    ax.axhline(1.0, color="black", linestyle="--", linewidth=1.2, label="random baseline (ρ=1)")
    ax.axhline(0.664, color="tomato", linestyle=":", linewidth=1.5,
               label="ρ≈0.664 (weight-1 empirical)")
    ax.set_xticks(weights)
    ax.set_xticklabels([f"weight {w}\n(n={len(d)})" for w, d in zip(weights, data)])
    ax.set_ylabel("ρ(a) = C(a) / E[C(a)]")
    ax.set_title(f"XOR autocorrelation ratio ρ by mask weight  (m={m})")
    ax.legend()
    fig.tight_layout()
    _save(fig, out_dir, f"xor_rho_by_weight_m{m}.png", show)


def plot_rho_histogram(
    df: pd.DataFrame,
    m: int,
    weights: list[int] | None = None,
    out_dir: Path | None = None,
    show: bool = False,
) -> None:
    """Histograms of rho(a) for each specified weight, one column each."""
    if weights is None:
        weights = sorted(df["popcount"].unique())
    fig, axes = plt.subplots(1, len(weights), figsize=(5 * len(weights), 4), sharey=False)
    if len(weights) == 1:
        axes = [axes]
    for ax, w in zip(axes, weights):
        sub = df[df["popcount"] == w]["rho"]
        ax.hist(sub, bins=min(40, len(sub)), color="steelblue", alpha=0.8)
        ax.axvline(1.0, color="black", linestyle="--", label="random")
        ax.axvline(float(sub.mean()), color="tomato", linestyle="-",
                   label=f"mean={sub.mean():.3f}")
        ax.set_title(f"weight={w}  (n={len(sub)})")
        ax.set_xlabel("ρ(a)")
        ax.legend(fontsize=8)
    axes[0].set_ylabel("count")
    fig.suptitle(f"ρ(a) distributions by mask weight  (m={m})", fontsize=13)
    fig.tight_layout()
    _save(fig, out_dir, f"xor_rho_hist_m{m}.png", show)


def plot_rho_by_mod(
    df: pd.DataFrame,
    m: int,
    q: int,
    weights: list[int] | None = None,
    out_dir: Path | None = None,
    show: bool = False,
) -> None:
    """Bar chart of mean rho by mask mod q, one panel per weight."""
    col = f"mask_mod{q}"
    if col not in df.columns:
        print(f"  [skip] {col} not in DataFrame")
        return
    if weights is None:
        weights = sorted(df["popcount"].unique())

    fig, axes = plt.subplots(1, len(weights), figsize=(5 * len(weights), 4), sharey=True)
    if len(weights) == 1:
        axes = [axes]

    for ax, w in zip(axes, weights):
        sub = df[df["popcount"] == w]
        grouped = sub.groupby(col)["rho"].agg(["mean", "std"]).reset_index()
        ax.bar(grouped[col], grouped["mean"], yerr=grouped["std"],
               capsize=4, color="steelblue", alpha=0.8)
        ax.axhline(1.0, color="black", linestyle="--", linewidth=1, label="random")
        ax.set_xlabel(f"mask mod {q}")
        ax.set_title(f"weight={w}")
        ax.legend(fontsize=8)

    axes[0].set_ylabel("mean ρ(a)")
    fig.suptitle(f"ρ(a) by mask mod {q}  (m={m})", fontsize=13)
    fig.tight_layout()
    _save(fig, out_dir, f"xor_rho_mod{q}_m{m}.png", show)


def plot_rho_vs_weight_trend(
    summary_df: pd.DataFrame,
    m: int,
    out_dir: Path | None = None,
    show: bool = False,
) -> None:
    """Line plot of mean rho ± 1 std by weight."""
    fig, ax = plt.subplots(figsize=(7, 4))
    weights = summary_df["popcount"].values
    means = summary_df["mean_rho"].values
    stds = summary_df["std_rho"].fillna(0).values
    ax.errorbar(weights, means, yerr=stds, fmt="o-", capsize=5,
                color="steelblue", label="prime indicator")
    ax.axhline(1.0, color="black", linestyle="--", linewidth=1, label="random baseline")
    ax.set_xlabel("Hamming weight of XOR mask")
    ax.set_ylabel("mean ρ(a)")
    ax.set_title(f"ρ trend vs mask weight  (m={m})")
    ax.legend()
    ax.set_xticks(weights)
    fig.tight_layout()
    _save(fig, out_dir, f"xor_rho_trend_m{m}.png", show)


def plot_component_sizes(
    result: dict,
    out_dir: Path | None = None,
    show: bool = False,
) -> None:
    """Log-scale bar chart of prime-induced graph component size distribution."""
    m = result["m"]
    dist = result["size_distribution"]
    ks = sorted(dist.keys())
    n_comp = [dist[k] for k in ks]
    n_prime = [k * dist[k] for k in ks]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    ax1.bar(ks, n_comp, color="steelblue", alpha=0.8)
    ax1.set_xlabel("Component size (# primes)")
    ax1.set_ylabel("# components")
    ax1.set_yscale("log")
    ax1.set_title(f"Component size distribution  (m={m})")

    ax2.bar(ks, n_prime, color="steelblue", alpha=0.8)
    ax2.set_xlabel("Component size")
    ax2.set_ylabel("# primes in components of this size")
    ax2.set_title(f"Primes by component size  (m={m})")

    largest_pct = result["largest_fraction"] * 100
    isolated_pct = result["isolated_fraction"] * 100
    note = (
        f"Largest: {result['largest_component']} primes ({largest_pct:.1f}%)\n"
        f"Isolated: {result['isolated_count']} ({isolated_pct:.1f}%)\n"
        f"Components: {result['n_components']}"
    )
    ax2.text(0.98, 0.97, note, transform=ax2.transAxes, fontsize=8,
             va="top", ha="right",
             bbox=dict(boxstyle="round", fc="white", alpha=0.8))

    fig.tight_layout()
    _save(fig, out_dir, f"prime_graph_components_m{m}.png", show)


def plot_degree_distribution(
    result: dict,
    out_dir: Path | None = None,
    show: bool = False,
) -> None:
    """Bar chart of degree distribution in prime-induced graph vs expected."""
    m = result["m"]
    dist = result["degree_distribution"]
    degrees = sorted(dist.keys())
    counts = [dist[d] for d in degrees]

    fig, ax = plt.subplots(figsize=(9, 4))
    ax.bar(degrees, counts, color="steelblue", alpha=0.8, label="primes")
    ax.axvline(result["avg_degree"], color="tomato", linestyle="--",
               linewidth=1.5, label=f"avg degree = {result['avg_degree']:.2f}")
    ax.set_xlabel("Degree in G_m^prime")
    ax.set_ylabel("# prime vertices")
    ax.set_title(f"Prime-induced graph degree distribution  (m={m})")
    ax.legend()
    fig.tight_layout()
    _save(fig, out_dir, f"prime_graph_degrees_m{m}.png", show)


def plot_graph_metrics_vs_m(
    results: list[dict],
    out_dir: Path | None = None,
    show: bool = False,
) -> None:
    """Multi-panel plot of graph connectivity metrics across m values."""
    ms = [r["m"] for r in results]
    fig, axes = plt.subplots(2, 2, figsize=(12, 8))

    axes[0, 0].plot(ms, [r["largest_fraction"] for r in results], "o-", color="steelblue")
    axes[0, 0].set_ylabel("Largest component fraction")
    axes[0, 0].set_title("Giant component growth")

    axes[0, 1].plot(ms, [r["isolated_fraction"] for r in results], "o-", color="tomato")
    axes[0, 1].set_ylabel("Isolated vertex fraction")
    axes[0, 1].set_title("Isolated primes")

    axes[1, 0].plot(ms, [r["avg_degree"] for r in results], "o-", color="seagreen")
    axes[1, 0].set_ylabel("Average degree")
    axes[1, 0].set_title("Average degree in G_m^prime")

    axes[1, 1].plot(ms, [r["n_components"] for r in results], "o-", color="darkorange")
    axes[1, 1].set_ylabel("# components")
    axes[1, 1].set_yscale("log")
    axes[1, 1].set_title("Number of components (log scale)")

    for ax in axes.flat:
        ax.set_xlabel("m")

    fig.suptitle("Prime-induced graph connectivity vs m", fontsize=13)
    fig.tight_layout()
    _save(fig, out_dir, "prime_graph_metrics_vs_m.png", show)
