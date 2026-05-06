"""
Walsh-Fourier analysis of the centered prime indicator on Q_m^odd.

Computes low-degree Fourier coefficients g_hat(S) and reports the
largest ones.  Feasible only for m <= 20.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pandas as pd

from primecube.hypercube_stats import WalshFourierAnalyzer
from primecube.plotting.hypercube_plots import plot_fourier_coefficients

RESULTS_DIR = Path(__file__).parent.parent / "results"


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Walsh-Fourier analysis of prime indicator")
    p.add_argument("--ms", nargs="+", type=int, default=[12, 14, 16],
                   help="Hypercube dimensions <=20 (default: 12 14 16)")
    p.add_argument("--max-degree", type=int, default=3,
                   help="Maximum Fourier degree (default: 3)")
    p.add_argument("--top-n", type=int, default=30,
                   help="Top-N coefficients to display (default: 30)")
    p.add_argument("--show-plots", action="store_true")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    raw_dir = RESULTS_DIR / "raw"
    plot_dir = RESULTS_DIR / "plots" / "fourier"
    raw_dir.mkdir(parents=True, exist_ok=True)

    for m in args.ms:
        if m > 20:
            print(f"Skipping m={m}: too large for full Fourier analysis (limit: 20)")
            continue
        print(f"\n=== m={m}  max_degree={args.max_degree} ===")
        analyzer = WalshFourierAnalyzer(m, odd_only=True)
        df = analyzer.low_degree_coefficients(max_degree=args.max_degree)
        raw_path = raw_dir / f"fourier_m{m}_deg{args.max_degree}.csv"
        df.to_csv(raw_path, index=False)
        print(f"  Saved {len(df)} coefficients to {raw_path}")
        print(df.head(args.top_n).to_string(index=False))
        plot_fourier_coefficients(df, m, top_n=args.top_n, out_dir=plot_dir, show=args.show_plots)


if __name__ == "__main__":
    main()
