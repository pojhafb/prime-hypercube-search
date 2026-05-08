"""
Sieve-aware Hamming search policy.

Ranks flip-set masks by S_xor(mask) — the XOR singular series — so that
masks predicted by the Hardy-Littlewood-style sieve to produce more prime
pairs are tried first.

Within each Hamming radius the flip sets are sorted by S_xor(mask) descending.
The singular series is computed once and cached per (m, max_radius) pair using
the batch_singular_series function, which evaluates local factors numerically
over all odd integers in [1, 2^sieve_m).

The sieve_m parameter controls accuracy of S_xor estimation:
  - sieve_m=16: fast, good for radii up to 4
  - sieve_m=18: default, accurate for all radii
  - sieve_m=20: slower, minimal gain in practice
"""
from __future__ import annotations

from itertools import combinations
from typing import Dict, List, Tuple

from primecube.core.flip_sets import FlipSet
from primecube.core.models import SearchResult
from primecube.hypercube_stats.singular_series import batch_singular_series
from primecube.policies.hamming_policies import _FlipSetPolicy


class SieveAwarePolicy(_FlipSetPolicy):
    """
    Hamming search policy that prioritises flip sets with high S_xor(mask).

    Within each radius r, flip sets are sorted by their XOR singular series
    S_xor(mask) descending — favouring masks where sieve theory predicts the
    most prime pairs at XOR distance mask from a typical prime.
    """

    def __init__(
        self,
        max_radius: int = 4,
        sieve_m: int = 18,
        small_primes: List[int] | None = None,
    ):
        super().__init__()
        self.max_radius = max_radius
        self.sieve_m = sieve_m
        self.small_primes = small_primes or [3, 5, 7, 11, 13, 17, 19, 23]
        self.name = f"sieve_aware_r{max_radius}_sm{sieve_m}"

    def _build_flip_sets(self, m: int) -> List[FlipSet]:
        allowed = list(range(1, m))
        all_masks_by_radius: Dict[int, List[Tuple[int, FlipSet]]] = {}

        for r in range(0, self.max_radius + 1):
            combos = list(combinations(allowed, r))
            masks = [sum(1 << p for p in c) for c in combos]
            all_masks_by_radius[r] = list(zip(masks, combos))

        # Collect all unique non-zero masks for batch S_xor computation
        unique_masks = list({
            mask
            for r, pairs in all_masks_by_radius.items()
            for mask, _ in pairs
            if mask > 0
        })

        print(f"    [SieveAware] Computing S_xor for {len(unique_masks)} masks"
              f" at sieve_m={self.sieve_m}...")
        s_map = batch_singular_series(unique_masks, self.small_primes, self.sieve_m)
        s_map[0] = 1.0  # empty flip set (identity): neutral score

        flip_sets: List[FlipSet] = []
        for r in range(0, self.max_radius + 1):
            pairs = all_masks_by_radius[r]
            # Sort by S_xor descending within each radius
            pairs.sort(key=lambda x: s_map.get(x[0], 1.0), reverse=True)
            flip_sets.extend(combo for _, combo in pairs)

        return flip_sets
