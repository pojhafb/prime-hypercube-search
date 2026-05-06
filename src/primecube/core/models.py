from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Tuple

FlipSet = Tuple[int, ...]


@dataclass
class SearchResult:
    strategy: str
    x: int
    x_odd: int
    found_prime: Optional[int]
    checks: int
    hamming_distance: Optional[int]
    arithmetic_distance: Optional[int]
    flip_positions: Optional[FlipSet]
    elapsed_sec: float


@dataclass
class ExperimentConfig:
    train_m: int
    test_ms: List[int]
    train_samples: int = 10_000
    test_samples: int = 20_000
    max_radius: int = 4
    seed: int = 42
    odd_increment_limit: int = 128
