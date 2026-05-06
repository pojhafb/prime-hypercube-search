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


def plot_z_score_histogram(
    df: pd.DataFrame,
    out_dir: Path | None = None,
    show: bool = False,
) -> None:
    """Histogram of z-scores per radius, overlaid with N(0,1) curve."""
    radii = sorted(df["radius"].unique())
    fig, axes = plt.subplots(1, len(radii), figsize=(5 * len(radii), 4), sharey=True)
    if len(radii) == 1:
        axes = [axes]
    xs = np.linspace(-4, 4, 300)
    normal_curve = np.exp(-0.5 * xs ** 2) / np.sqrt(2 * np.pi)

    for ax, r in zip(axes, radii):
        sub = df[df["radius"] == r]
        for src, color in [("primes", "steelblue"), ("random_baseline", "tomato")]:
            data = sub[sub["source"] == src]["z_score"].dropna()
            if len(data) == 0:
                continue
            ax.hist(data, bins=40, density=True, alpha=0.5, color=color, label=src)
        ax.plot(xs, normal_curve, "k--", linewidth=1, label="N(0,1)")
        ax.set_title(f"radius={r}")
        ax.set_xlabel("Z-score")
        ax.legend(fontsize=8)

    axes[0].set_ylabel("Density")
    m_val = df["m"].iloc[0]
    fig.suptitle(f"Hamming-ball discrepancy z-scores  (m={m_val})", fontsize=13)
    fig.tight_layout()
    _save(fig, out_dir, f"z_score_histogram_m{m_val}.png", show)


def plot_discrepancy_by_radius(
    df: pd.DataFrame,
    out_dir: Path | None = None,
    show: bool = False,
) -> None:
    """Box plot of raw discrepancy Δ(x,r) per radius."""
    fig, ax = plt.subplots(figsize=(8, 5))
    m_val = df["m"].iloc[0]
    sources = df["source"].unique()
    colors = {"primes": "steelblue", "random_baseline": "tomato"}
    radii = sorted(df["radius"].unique())

    for i, src in enumerate(sources):
        sub = df[df["source"] == src]
        data = [sub[sub["radius"] == r]["discrepancy"].values for r in radii]
        positions = [r + (i - 0.5) * 0.3 for r in radii]
        bp = ax.boxplot(data, positions=positions, widths=0.25,
                        patch_artist=True, manage_ticks=False)
        for patch in bp["boxes"]:
            patch.set_facecolor(colors.get(src, "grey"))
            patch.set_alpha(0.6)

    ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
    ax.set_xticks(radii)
    ax.set_xticklabels([f"r={r}" for r in radii])
    ax.set_xlabel("Hamming radius")
    ax.set_ylabel("Discrepancy Δ(x,r)")
    ax.set_title(f"Prime-count discrepancy in Hamming balls  (m={m_val})")
    handles = [plt.Rectangle((0, 0), 1, 1, fc=colors.get(s, "grey"), alpha=0.6) for s in sources]
    ax.legend(handles, sources)
    fig.tight_layout()
    _save(fig, out_dir, f"discrepancy_boxplot_m{m_val}.png", show)


def plot_edge_ratio_by_bit(
    df: pd.DataFrame,
    m: int,
    out_dir: Path | None = None,
    show: bool = False,
) -> None:
    """Bar chart of observed/expected prime-prime edge ratio per bit position."""
    fig, ax = plt.subplots(figsize=(max(8, len(df) // 2), 4))
    ax.bar(df["bit_position"], df["ratio"], color="steelblue", alpha=0.8)
    ax.axhline(1.0, color="black", linewidth=1, linestyle="--", label="random baseline")
    ax.set_xlabel("Bit position")
    ax.set_ylabel("Observed / Expected edges")
    ax.set_title(f"Prime-prime Hamming-1 edge ratio by bit  (m={m})")
    ax.legend()
    fig.tight_layout()
    _save(fig, out_dir, f"edge_ratio_by_bit_m{m}.png", show)


def plot_fourier_coefficients(
    df: pd.DataFrame,
    m: int,
    top_n: int = 30,
    out_dir: Path | None = None,
    show: bool = False,
) -> None:
    """Bar chart of top-N absolute Walsh-Fourier coefficients."""
    top = df.head(top_n)
    fig, ax = plt.subplots(figsize=(12, 5))
    colors = {0: "grey", 1: "steelblue", 2: "darkorange", 3: "seagreen"}
    bar_colors = [colors.get(d, "purple") for d in top["degree"]]
    ax.bar(range(len(top)), top["abs_coefficient"], color=bar_colors, alpha=0.8)
    ax.set_xticks(range(len(top)))
    ax.set_xticklabels(top["bit_set"], rotation=90, fontsize=7)
    ax.set_xlabel("Bit subset S")
    ax.set_ylabel("|ĝ(S)|")
    ax.set_title(f"Top-{top_n} Walsh-Fourier coefficients of prime indicator  (m={m})")
    from matplotlib.patches import Patch
    legend = [Patch(fc=c, label=f"degree {d}") for d, c in colors.items() if d <= 3]
    ax.legend(handles=legend, fontsize=8)
    fig.tight_layout()
    _save(fig, out_dir, f"fourier_coefficients_m{m}.png", show)


def plot_spectral_energy_by_m(
    results: list[dict],
    out_dir: Path | None = None,
    show: bool = False,
) -> None:
    """Line plot comparing observed vs expected fTAf across m values."""
    ms = [r["m"] for r in results]
    observed = [r["fTAf_observed"] for r in results]
    expected = [r["fTAf_expected_random"] for r in results]
    ratios = [r["ratio_observed_to_expected"] for r in results]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    ax1.plot(ms, observed, "o-", label="observed", color="steelblue")
    ax1.plot(ms, expected, "s--", label="random baseline", color="tomato")
    ax1.set_xlabel("m")
    ax1.set_ylabel("f^T A f")
    ax1.set_title("Spectral adjacency energy vs random model")
    ax1.legend()
    ax1.set_yscale("log")

    ax2.plot(ms, ratios, "D-", color="darkorange")
    ax2.axhline(1.0, color="black", linewidth=0.8, linestyle="--")
    ax2.set_xlabel("m")
    ax2.set_ylabel("observed / expected")
    ax2.set_title("Edge ratio (observed vs random)")
    fig.tight_layout()
    _save(fig, out_dir, "spectral_energy_vs_m.png", show)
