"""
Singular series validation experiment.

Computes S_xor(a) for all even masks of Hamming weight 1-4 and compares
against the observed rho(a) = C(a) / E[C(a)] from the WHT.

Key question: does S_xor(a) predict rho(a)?  If yes, the XOR prime-pair
count is explained by a product of local sieve factors — an XOR analog of
the Hardy-Littlewood conjectural formula for prime pairs (p, p+d).

Conjecture:  C_m(a)  ~  S_xor(a)  *  2^(m-1) / (m * ln 2)^2

Output:
  results/summaries/singular_series_validation.csv   (per-mask comparison)
  results/summaries/singular_series_by_weight.csv    (per-weight statistics)
  results/plots/singular_series/                     (scatter + residual plots)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from primecube.hypercube_stats import PrimeIndicator, XORAutocorrelation
from primecube.hypercube_stats.singular_series import add_singular_series, obstruction_breakdown

RESULTS_DIR = Path(__file__).parent.parent / "results"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Validate S_xor(a) against observed rho(a)")
    p.add_argument("--ms", nargs="+", type=int, default=[16, 18],
                   help="Dimensions to run (default: 16 18)")
    p.add_argument("--max-weight", type=int, default=4,
                   help="Max Hamming weight of XOR mask (default: 4)")
    p.add_argument("--small-primes", nargs="+", type=int,
                   default=[3, 5, 7, 11, 13, 17, 19, 23],
                   help="Primes for S_xor product")
    p.add_argument("--sieve-m", type=int, default=18,
                   help="Odd-integer range [1,2^sieve_m) for local factor estimation")
    p.add_argument("--show-plots", action="store_true")
    return p.parse_args()


def run_one(
    m: int,
    max_weight: int,
    small_primes: list[int],
    sieve_m: int,
    plot_dir: Path,
    show: bool,
) -> pd.DataFrame:
    print(f"\n{'='*60}")
    print(f"  m = {m}")

    pi = PrimeIndicator(m, odd_only=True)
    prime_set = pi.prime_set()
    vertices = pi.vertices()
    delta = len(prime_set) / len(vertices)
    print(f"  {len(prime_set)} primes  delta={delta:.5f}")

    # WHT autocorrelation
    xac = XORAutocorrelation(m)
    print("  Computing WHT autocorrelation...")
    C = xac.compute_all(prime_set)
    df = xac.analyze(C, prime_set, max_weight=max_weight, small_primes=small_primes[:4])

    # Add singular series
    print(f"  Computing S_xor for {len(df)} masks (sieve_m={sieve_m})...")
    df = add_singular_series(df, small_primes=small_primes, m=sieve_m)
    df["m"] = m

    # Correlation statistics
    corr = df[["rho", "S_xor"]].corr().iloc[0, 1]
    print(f"\n  Pearson r(rho, S_xor) = {corr:.4f}")

    # By weight
    by_weight = (
        df.groupby("popcount")
        .agg(
            n=("rho", "count"),
            mean_rho=("rho", "mean"),
            mean_S_xor=("S_xor", "mean"),
            mean_ratio=("rho_over_S", "mean"),
            std_ratio=("rho_over_S", "std"),
            pearson_r=("rho", lambda x: x.corr(df.loc[x.index, "S_xor"])),
        )
        .reset_index()
    )
    print("\n  By weight:")
    print(by_weight.to_string(index=False))

    # Best and worst predicted masks
    df_sorted = df.sort_values("rho_residual", key=abs, ascending=False)
    print("\n  Largest residuals |rho - S_xor|:")
    cols = ["mask", "popcount", "rho", "S_xor", "rho_residual", "rho_over_S"]
    print(df_sorted[cols].head(10).to_string(index=False))

    # --- Obstruction breakdown for top weight-1 and weight-2 masks ---
    print("\n  Obstruction breakdown for weight-1 mask a=2 (bit flip j=1):")
    bd = obstruction_breakdown(2, small_primes=small_primes, m=sieve_m)
    print(bd.to_string(index=False))

    # --- Plots ---
    _plot_rho_vs_s(df, m, plot_dir, show)
    _plot_residual_by_weight(df, m, plot_dir, show)
    _plot_ratio_by_weight(df, m, plot_dir, show)

    return df


def _plot_rho_vs_s(df: pd.DataFrame, m: int, out_dir: Path, show: bool) -> None:
    """Scatter plot: observed rho vs predicted S_xor, coloured by weight."""
    fig, ax = plt.subplots(figsize=(7, 6))
    colors = {1: "tomato", 2: "steelblue", 3: "seagreen", 4: "darkorange"}
    for w in sorted(df["popcount"].unique()):
        sub = df[df["popcount"] == w]
        ax.scatter(sub["S_xor"], sub["rho"], alpha=0.6, s=20,
                   color=colors.get(w, "grey"), label=f"weight {w}")
    lo = min(df["S_xor"].min(), df["rho"].min()) * 0.98
    hi = max(df["S_xor"].max(), df["rho"].max()) * 1.02
    ax.plot([lo, hi], [lo, hi], "k--", linewidth=1, label="perfect prediction")
    ax.set_xlabel("S_xor(a)  (singular series prediction)")
    ax.set_ylabel("ρ(a)  (observed)")
    ax.set_title(f"Observed ρ vs S_xor prediction  (m={m})")
    ax.legend(fontsize=9)
    fig.tight_layout()
    out_dir.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_dir / f"s_xor_scatter_m{m}.png", dpi=150, bbox_inches="tight")
    if show:
        plt.show()
    plt.close(fig)


def _plot_residual_by_weight(df: pd.DataFrame, m: int, out_dir: Path, show: bool) -> None:
    """Box plot of residuals rho - S_xor by weight."""
    weights = sorted(df["popcount"].unique())
    fig, ax = plt.subplots(figsize=(8, 4))
    data = [df[df["popcount"] == w]["rho_residual"].values for w in weights]
    bp = ax.boxplot(data, positions=weights, widths=0.4, patch_artist=True)
    for patch in bp["boxes"]:
        patch.set_facecolor("steelblue")
        patch.set_alpha(0.7)
    ax.axhline(0, color="black", linestyle="--", linewidth=1)
    ax.set_xticks(weights)
    ax.set_xticklabels([f"weight {w}" for w in weights])
    ax.set_ylabel("ρ(a) − S_xor(a)")
    ax.set_title(f"Residuals of singular series prediction  (m={m})")
    fig.tight_layout()
    fig.savefig(out_dir / f"s_xor_residual_m{m}.png", dpi=150, bbox_inches="tight")
    if show:
        plt.show()
    plt.close(fig)


def _plot_ratio_by_weight(df: pd.DataFrame, m: int, out_dir: Path, show: bool) -> None:
    """Bar chart of mean rho/S_xor by weight — should be ~1 if S_xor predicts well."""
    weights = sorted(df["popcount"].unique())
    means = [df[df["popcount"] == w]["rho_over_S"].mean() for w in weights]
    stds = [df[df["popcount"] == w]["rho_over_S"].std() for w in weights]
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(weights, means, yerr=stds, capsize=5, color="steelblue", alpha=0.8)
    ax.axhline(1.0, color="black", linestyle="--", linewidth=1, label="perfect (ratio=1)")
    ax.set_xticks(weights)
    ax.set_xticklabels([f"weight {w}" for w in weights])
    ax.set_ylabel("ρ(a) / S_xor(a)")
    ax.set_title(f"Ratio ρ / S_xor by mask weight  (m={m})")
    ax.legend()
    fig.tight_layout()
    fig.savefig(out_dir / f"s_xor_ratio_m{m}.png", dpi=150, bbox_inches="tight")
    if show:
        plt.show()
    plt.close(fig)


def main() -> None:
    args = parse_args()
    sum_dir = RESULTS_DIR / "summaries"
    plot_dir = RESULTS_DIR / "plots" / "singular_series"
    sum_dir.mkdir(parents=True, exist_ok=True)
    plot_dir.mkdir(parents=True, exist_ok=True)

    all_frames: list[pd.DataFrame] = []
    for m in args.ms:
        df = run_one(
            m, args.max_weight, args.small_primes,
            args.sieve_m, plot_dir, args.show_plots,
        )
        all_frames.append(df)

    if all_frames:
        combined = pd.concat(all_frames, ignore_index=True)
        val_path = sum_dir / "singular_series_validation.csv"
        combined.to_csv(val_path, index=False)
        print(f"\nPer-mask validation saved to {val_path}")

        agg = (
            combined.groupby(["m", "popcount"])
            .agg(
                n=("rho", "count"),
                mean_rho=("rho", "mean"),
                mean_S_xor=("S_xor", "mean"),
                mean_ratio=("rho_over_S", "mean"),
                std_ratio=("rho_over_S", "std"),
            )
            .reset_index()
        )
        wt_path = sum_dir / "singular_series_by_weight.csv"
        agg.to_csv(wt_path, index=False)
        print(f"Weight summary saved to {wt_path}")
        print("\nWeight summary:")
        print(agg.to_string(index=False))

        # Overall assessment
        all_corr = combined[["rho", "S_xor"]].corr().iloc[0, 1]
        mean_resid = combined["rho_residual"].abs().mean()
        print(f"\nOverall: Pearson r(rho, S_xor) = {all_corr:.4f}")
        print(f"         Mean |rho - S_xor|     = {mean_resid:.4f}")
        overall_ratio = combined["rho_over_S"].mean()
        print(f"         Mean rho / S_xor        = {overall_ratio:.4f}")

        if abs(all_corr) > 0.8:
            print("\n  => Strong correlation: S_xor(a) is a good predictor of rho(a).")
            print("     Conjecture supported: C_m(a) ~ S_xor(a) * 2^(m-1) / (m ln 2)^2")
        elif abs(all_corr) > 0.5:
            print("\n  => Moderate correlation: S_xor(a) partially explains rho(a).")
        else:
            print("\n  => Weak correlation: residual structure beyond S_xor.")


if __name__ == "__main__":
    main()
