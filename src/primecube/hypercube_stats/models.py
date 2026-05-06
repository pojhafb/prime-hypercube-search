from dataclasses import dataclass


@dataclass(frozen=True)
class DiscrepancyResult:
    m: int
    radius: int
    x: int
    ball_size: int
    prime_count: int
    expected_count: float
    discrepancy: float
    z_score: float
    density: float
    source: str  # "primes" or "random_baseline"
