import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from primecube.core.flip_sets import FlipSetFactory


def test_low_bit_first_starts_empty():
    flip_sets = FlipSetFactory.make_static(m=8, max_radius=2, strategy="low_bit_first")
    assert flip_sets[0] == ()


def test_low_bit_first_excludes_bit0():
    flip_sets = FlipSetFactory.make_static(m=8, max_radius=2, strategy="low_bit_first")
    for fs in flip_sets:
        assert 0 not in fs, f"bit 0 found in {fs}"


def test_high_bit_first_excludes_bit0():
    flip_sets = FlipSetFactory.make_static(m=8, max_radius=2, strategy="high_bit_first")
    for fs in flip_sets:
        assert 0 not in fs


def test_uniform_random_excludes_bit0():
    flip_sets = FlipSetFactory.make_static(m=8, max_radius=2, strategy="uniform_random")
    for fs in flip_sets:
        assert 0 not in fs


def test_learned_excludes_bit0():
    bit_score = {i: float(8 - i) for i in range(8)}
    bit_score[0] = 0.0
    flip_sets = FlipSetFactory.make_learned(m=8, max_radius=2, bit_score=bit_score)
    for fs in flip_sets:
        assert 0 not in fs


def test_low_bit_first_radius_order():
    flip_sets = FlipSetFactory.make_static(m=6, max_radius=2, strategy="low_bit_first")
    radii = [len(fs) for fs in flip_sets]
    # radii must be non-decreasing (radius 0 before 1 before 2)
    for i in range(len(radii) - 1):
        assert radii[i] <= radii[i + 1]
