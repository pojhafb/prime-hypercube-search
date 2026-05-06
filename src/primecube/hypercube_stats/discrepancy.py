from __future__ import annotations

import math
import random

import pandas as pd

from .prime_indicator import PrimeIndicator
from .hamming_balls import HammingBall
from .models import DiscrepancyResult


class HammingBallDiscrepancy:
    """
    For each sampled center x and each radius r, compute:
      delta(x, r) = |P_m ∩ B(x,r)| - density * |B(x,r)|
      z(x, r)     = delta / sqrt(density * (1-density) * |B(x,r)|)
    """

    def __init__(self, m: int, radii: list[int], samples: int, seed: int = 42, source: str = "primes"):
        self.m = m
        self.radii = radii
        self.samples = samples
        self.seed = seed
        self.source = source

    def run(self, prime_set: set[int] | None = None, density: float | None = None) -> pd.DataFrame:
        pi = PrimeIndicator(self.m, odd_only=True)
        if prime_set is None:
            prime_set = pi.prime_set()
        if density is None:
            density = len(prime_set) / len(pi.vertices())

        rng = random.Random(self.seed)
        centers = rng.choices(pi.vertices(), k=self.samples)

        rows: list[DiscrepancyResult] = []
        for x in centers:
            for r in self.radii:
                ball = HammingBall.ball_vertices(x, self.m, r, odd_only=True)
                prime_count = sum(1 for v in ball if v in prime_set)
                ball_size = len(ball)
                expected = density * ball_size
                disc = prime_count - expected
                var = density * (1 - density) * ball_size
                z = disc / math.sqrt(var) if var > 0 else 0.0
                rows.append(DiscrepancyResult(
                    m=self.m,
                    radius=r,
                    x=x,
                    ball_size=ball_size,
                    prime_count=prime_count,
                    expected_count=expected,
                    discrepancy=disc,
                    z_score=z,
                    density=density,
                    source=self.source,
                ))

        return pd.DataFrame([r.__dict__ for r in rows])
