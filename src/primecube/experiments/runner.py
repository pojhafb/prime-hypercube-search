from __future__ import annotations

import random
import time
from typing import List

import pandas as pd

from primecube.core.models import ExperimentConfig, SearchResult
from primecube.policies.base import SearchPolicy
from primecube.training.trainer import LearnedPolicyTrainer
from primecube.training.transfer import PolicyTransfer
from primecube.policies.hamming_policies import LearnedBitOrderPolicy
from primecube.policies.hybrid_policy import HybridStandardPlusLearnedPolicy


class ExperimentRunner:
    """
    Runs a set of search policies across one or more test dimensions.

    Usage:
        runner = ExperimentRunner(config=cfg, policies=[...])
        df = runner.run()
    """

    def __init__(
        self,
        config: ExperimentConfig,
        policies: List[SearchPolicy],
    ):
        self.config = config
        self.policies = policies

    def run(self) -> pd.DataFrame:
        all_rows = []

        for test_m in self.config.test_ms:
            print(f"\n===== test m={test_m} =====")
            rng = random.Random(self.config.seed + 999 + test_m)

            test_xs = [
                rng.randrange(1 << (test_m - 1), 1 << test_m)
                for _ in range(self.config.test_samples)
            ]

            for policy in self.policies:
                print(f"\n  strategy: {policy.name}")
                wall = time.time()

                for i, x in enumerate(test_xs):
                    if i % 10_000 == 0:
                        print(f"    {i}/{self.config.test_samples}")

                    result = policy.search(x, test_m)
                    all_rows.append(self._to_row(result, test_m))

                print(f"  finished in {time.time() - wall:.1f}s")

        return pd.DataFrame(all_rows)

    @staticmethod
    def _to_row(result: SearchResult, test_m: int) -> dict:
        return {
            "test_m": test_m,
            "x": result.x,
            "x_odd": result.x_odd,
            "strategy": result.strategy,
            "found_prime": result.found_prime,
            "checks": result.checks,
            "hamming_distance": result.hamming_distance,
            "arithmetic_distance": result.arithmetic_distance,
            "flip_positions": result.flip_positions,
            "elapsed_sec": result.elapsed_sec,
        }


def build_standard_policy_suite(config: ExperimentConfig) -> List[SearchPolicy]:
    """
    Trains a learned policy on config.train_m and returns the full suite:

      - standard_odd_increment
      - low_bit_first_no_bit0
      - high_bit_first_no_bit0
      - uniform_random_no_bit0
      - learned_bit_order_no_bit0 (transferred)
      - hybrid_standard_plus_learned (transferred)
    """
    from primecube.policies.standard_odd import StandardOddIncrementPolicy
    from primecube.policies.hamming_policies import (
        LowBitFirstPolicy,
        HighBitFirstPolicy,
        UniformRandomPolicy,
    )

    trainer = LearnedPolicyTrainer(
        train_m=config.train_m,
        max_radius=config.max_radius,
        train_samples=config.train_samples,
        seed=config.seed,
    )

    learned_scores = trainer.train()
    label = f"{config.train_m}_to_test"

    policies: List[SearchPolicy] = [
        StandardOddIncrementPolicy(),
        LowBitFirstPolicy(max_radius=config.max_radius, seed=config.seed),
        HighBitFirstPolicy(max_radius=config.max_radius, seed=config.seed),
        UniformRandomPolicy(max_radius=config.max_radius, seed=config.seed),
    ]

    for test_m in config.test_ms:
        transferred = PolicyTransfer.transfer(learned_scores, config.train_m, test_m)

        policies.append(
            LearnedBitOrderPolicy(
                bit_score=transferred,
                max_radius=config.max_radius,
                label=f"{config.train_m}_to_{test_m}",
            )
        )

        policies.append(
            HybridStandardPlusLearnedPolicy(
                bit_score=transferred,
                max_radius=config.max_radius,
                odd_increment_limit=config.odd_increment_limit,
            )
        )

    return policies
