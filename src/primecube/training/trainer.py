from __future__ import annotations

import random
from collections import Counter
from typing import Dict

from primecube.core.bit_ops import BitOps
from primecube.core.flip_sets import FlipSetFactory
from primecube.core.prime_tester import PrimeTester
from primecube.policies.hamming_policies import LowBitFirstPolicy


class LearnedPolicyTrainer:
    """
    Learns per-bit usefulness scores inside the odd subcube.

    Uses low-bit-first as the teacher policy and counts which bit positions
    appear in successful prime-reaching paths. Bit 0 is always excluded.
    """

    def __init__(
        self,
        train_m: int,
        max_radius: int = 4,
        train_samples: int = 10_000,
        seed: int = 42,
    ):
        self.train_m = train_m
        self.max_radius = max_radius
        self.train_samples = train_samples
        self.seed = seed

    def train(self) -> Dict[int, float]:
        rng = random.Random(self.seed)
        teacher = LowBitFirstPolicy(max_radius=self.max_radius, seed=self.seed)
        bit_counter: Counter = Counter()

        print(
            f"\nTraining learned policy: "
            f"m={self.train_m}, samples={self.train_samples}, radius={self.max_radius}"
        )

        for i in range(self.train_samples):
            if i % 5000 == 0:
                print(f"  sample {i}/{self.train_samples}")

            x = self._sample(rng, self.train_m)
            result = teacher.search(x, self.train_m)

            if result.flip_positions:
                bit_counter.update(result.flip_positions)

        bit_score: Dict[int, float] = {
            bit: float(bit_counter[bit]) for bit in range(1, self.train_m)
        }

        positives = [s for s in bit_score.values() if s > 0]
        fallback = min(positives) * 0.25 if positives else 1.0

        for bit in range(1, self.train_m):
            if bit_score[bit] == 0:
                bit_score[bit] = fallback

        bit_score[0] = 0.0

        print("\nLearned bit ranking (top 20):")
        for bit, score in sorted(bit_score.items(), key=lambda kv: -kv[1])[:20]:
            print(f"  bit {bit:2d}: {score:.1f}")

        return bit_score

    @staticmethod
    def _sample(rng: random.Random, m: int) -> int:
        return rng.randrange(1 << (m - 1), 1 << m)
