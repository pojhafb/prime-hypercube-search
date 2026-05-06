import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from primecube.policies.standard_odd import StandardOddIncrementPolicy
from primecube.policies.hamming_policies import LowBitFirstPolicy, UniformRandomPolicy


def test_standard_odd_finds_prime():
    policy = StandardOddIncrementPolicy()
    result = policy.search(100, 8)
    assert result.found_prime is not None
    from sympy import isprime
    assert isprime(result.found_prime)


def test_standard_odd_result_is_odd():
    policy = StandardOddIncrementPolicy()
    result = policy.search(200, 9)
    assert result.found_prime % 2 == 1


def test_standard_odd_x_odd_forced():
    policy = StandardOddIncrementPolicy()
    result = policy.search(100, 8)
    assert result.x_odd % 2 == 1


def test_low_bit_first_finds_prime():
    policy = LowBitFirstPolicy(max_radius=4)
    result = policy.search(101, 8)
    assert result.found_prime is not None


def test_low_bit_first_result_is_odd():
    policy = LowBitFirstPolicy(max_radius=4)
    result = policy.search(200, 9)
    assert result.found_prime % 2 == 1


def test_uniform_random_finds_prime():
    policy = UniformRandomPolicy(max_radius=4)
    result = policy.search(101, 8)
    assert result.found_prime is not None


def test_strategy_name_in_result():
    policy = StandardOddIncrementPolicy()
    result = policy.search(100, 8)
    assert result.strategy == "standard_odd_increment"

    policy2 = LowBitFirstPolicy()
    result2 = policy2.search(100, 8)
    assert result2.strategy == "low_bit_first_no_bit0"
