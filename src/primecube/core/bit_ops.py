from __future__ import annotations

from typing import Tuple

FlipSet = Tuple[int, ...]


class BitOps:
    @staticmethod
    def force_odd(x: int) -> int:
        return x | 1

    @staticmethod
    def flip_bits(x: int, positions: FlipSet) -> int:
        y = x
        for pos in positions:
            y ^= 1 << pos
        return y

    @staticmethod
    def hamming_distance(a: int, b: int) -> int:
        return bin(a ^ b).count("1")
