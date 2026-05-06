from __future__ import annotations

from typing import Dict


class PolicyTransfer:
    """
    Transfers learned bit scores from train_m to a larger test_m.

    Bits that existed during training keep their learned scores.
    New higher-order bits get a small fallback score so they are visited
    last rather than never.
    Bit 0 is always forced to 0.0 (excluded from odd-subcube search).
    """

    @staticmethod
    def transfer(
        source_scores: Dict[int, float],
        train_m: int,
        test_m: int,
    ) -> Dict[int, float]:
        if test_m < train_m:
            raise ValueError(f"test_m ({test_m}) must be >= train_m ({train_m})")

        positives = [
            score for bit, score in source_scores.items()
            if bit != 0 and score > 0
        ]
        fallback = min(positives) * 0.25 if positives else 0.01

        transferred: Dict[int, float] = {}

        for bit in range(test_m):
            if bit == 0:
                transferred[bit] = 0.0
            elif bit in source_scores:
                transferred[bit] = source_scores[bit]
            else:
                transferred[bit] = fallback

        return transferred
