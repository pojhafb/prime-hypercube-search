from __future__ import annotations

from itertools import combinations
from math import comb


class HammingBall:
    """Generate Hamming-ball neighborhoods in the odd subcube."""

    @staticmethod
    def generate_neighbors(x: int, m: int, radius: int, odd_only: bool = True) -> list[int]:
        """Return all vertices within Hamming distance <= radius of x (excluding x itself)."""
        # Bit positions available to flip (exclude bit 0 when odd_only)
        available = list(range(1, m)) if odd_only else list(range(0, m))
        result: list[int] = []
        for r in range(1, radius + 1):
            for positions in combinations(available, r):
                mask = 0
                for p in positions:
                    mask |= (1 << p)
                neighbor = x ^ mask
                result.append(neighbor)
        return result

    @staticmethod
    def ball_vertices(x: int, m: int, radius: int, odd_only: bool = True) -> list[int]:
        """Return all vertices within Hamming distance <= radius including x."""
        return [x] + HammingBall.generate_neighbors(x, m, radius, odd_only)

    @staticmethod
    def ball_size(m: int, radius: int, odd_only: bool = True) -> int:
        """Number of vertices in a Hamming ball of given radius."""
        dim = m - 1 if odd_only else m
        return sum(comb(dim, i) for i in range(0, radius + 1))
