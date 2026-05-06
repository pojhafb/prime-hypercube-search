"""
Experiment: Hamming distance distribution from integers to nearest prime.

Full scan for small m, sampling for larger m.
Reproduces the Chapter 2 result (m=14 full scan).

Usage:
    python scripts/run_distance_distribution.py
    python scripts/run_distance_distribution.py --full-m 14 --sample-ms 16 18 20 --samples 20000
"""
from __future__ import annotations

import argparse
import random
import sys
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pandas as pd

from primecube.core.bit_ops import BitOps


RESULTS = Path("results")


def sieve(limit: int) -> set:
    is_prime = bytearray([1]) * limit
    is_prime[0] = is_prime[1] = 0

    for i in range(2, int(limit**0.5) + 1):
        if is_prime[i]:
            is_prime[i * i :: i] = bytearray(len(is_prime[i * i :: i]))

    return {i for i, v in enumerate(is_prime) if v}


def nearest_prime_hamming(x: int, m: int, prime_set: set, max_radius: int = 4):
    if x in prime_set:
        return 0, x, ()

    for r in range(1, max_radius + 1):
        for positions in combinations(range(m), r):
            y = BitOps.flip_bits(x, positions)
            if y in prime_set:
                return r, y, positions

    return None, None, None


def run(m: int, prime_set: set, xs, max_radius: int = 4):
    rows = []

    for i, x in enumerate(xs):
        if i % 5000 == 0:
            print(f"  {i}/{len(xs) if hasattr(xs, '__len__') else '?'}")

        d, p, pos = nearest_prime_hamming(x, m, prime_set, max_radius)
        rows.append({
            "m": m,
            "x": x,
            "distance_to_prime": d,
            "nearest_prime": p,
            "flip_positions": pos,
        })

    return pd.DataFrame(rows)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--full-m", type=int, default=14)
    p.add_argument("--sample-ms", type=int, nargs="+", default=[16, 18, 20])
    p.add_argument("--samples", type=int, default=20_000)
    p.add_argument("--max-radius", type=int, default=4)
    p.add_argument("--seed", type=int, default=42)
    return p.parse_args()


def main():
    args = parse_args()
    rng = random.Random(args.seed)
    out_dir = RESULTS / "summaries"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Full scan
    m = args.full_m
    print(f"\nFull scan: m={m} ({1 << m} numbers)")
    prime_set = sieve(1 << m)
    df = run(m, prime_set, range(1 << m), args.max_radius)
    df.to_csv(out_dir / f"distance_dist_m{m}_full.csv", index=False)

    counts = df["distance_to_prime"].value_counts().sort_index()
    print(f"\nDistance distribution for m={m}:")
    print(counts.to_string())
    print(f"\nAs %:\n{(counts / len(df) * 100).round(2).to_string()}")

    # Sampled
    for m in args.sample_ms:
        print(f"\nSampled: m={m}, n={args.samples}")
        prime_set = sieve(1 << m)
        xs = [rng.randrange(0, 1 << m) for _ in range(args.samples)]
        df = run(m, prime_set, xs, args.max_radius)
        df.to_csv(out_dir / f"distance_dist_m{m}_sampled.csv", index=False)

        counts = df["distance_to_prime"].value_counts().sort_index()
        print(f"\nDistance distribution for m={m} (sampled):")
        print(counts.to_string())


if __name__ == "__main__":
    main()
