import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from primecube.core.bit_ops import BitOps


def test_force_odd_already_odd():
    assert BitOps.force_odd(7) == 7


def test_force_odd_even():
    assert BitOps.force_odd(8) == 9


def test_flip_bits_single():
    assert BitOps.flip_bits(0b1010, (0,)) == 0b1011
    assert BitOps.flip_bits(0b1010, (1,)) == 0b1000


def test_flip_bits_multiple():
    assert BitOps.flip_bits(0b1010, (0, 3)) == 0b0011


def test_flip_bits_empty():
    assert BitOps.flip_bits(42, ()) == 42


def test_hamming_distance_same():
    assert BitOps.hamming_distance(7, 7) == 0


def test_hamming_distance_one():
    assert BitOps.hamming_distance(0b0100, 0b0000) == 1


def test_hamming_distance_four():
    assert BitOps.hamming_distance(0b0000, 0b1111) == 4
