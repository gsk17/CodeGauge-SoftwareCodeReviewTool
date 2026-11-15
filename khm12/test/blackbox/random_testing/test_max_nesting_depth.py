"""Black-box tests for max_nesting_depth - US12, Kasam (khm12).

Technique: random testing against invariants.
Function under test: core.complexity.max_nesting_depth(depths).

No expected value is written by hand. Each test states a property of a maximum
that must hold for every valid list, and samples lists randomly. The seed is
fixed so a failure replays exactly.
"""

import random

import pytest

from core.complexity import max_nesting_depth

SEED = 20261115
TRIALS = 200


def _random_depths(rng, low=0, high=20, min_len=1, max_len=30):
    return [rng.randint(low, high) for _ in range(rng.randint(min_len, max_len))]


def test_the_result_is_never_negative():
    rng = random.Random(SEED)
    for _ in range(TRIALS):
        assert max_nesting_depth(_random_depths(rng)) >= 0


def test_no_element_ever_exceeds_the_result():
    # the defining property of a maximum
    rng = random.Random(SEED + 1)
    for _ in range(TRIALS):
        depths = _random_depths(rng)
        result = max_nesting_depth(depths)
        for depth in depths:
            assert depth <= result


def test_the_result_is_always_one_of_the_elements():
    # a maximum is attained, not merely an upper bound
    rng = random.Random(SEED + 2)
    for _ in range(TRIALS):
        depths = _random_depths(rng)
        assert max_nesting_depth(depths) in depths


def test_shuffling_the_list_never_changes_the_result():
    # order independence - this is what catches a broken running maximum
    rng = random.Random(SEED + 3)
    for _ in range(TRIALS):
        depths = _random_depths(rng)
        expected = max_nesting_depth(depths)
        shuffled = list(depths)
        rng.shuffle(shuffled)
        assert max_nesting_depth(shuffled) == expected


def test_appending_a_smaller_value_never_changes_the_result():
    rng = random.Random(SEED + 4)
    for _ in range(TRIALS):
        depths = _random_depths(rng, low=5, high=20)
        expected = max_nesting_depth(depths)
        assert max_nesting_depth(depths + [rng.randint(0, 4)]) == expected


def test_appending_a_larger_value_always_becomes_the_result():
    rng = random.Random(SEED + 5)
    for _ in range(TRIALS):
        depths = _random_depths(rng, low=0, high=10)
        bigger = rng.randint(11, 40)
        assert max_nesting_depth(depths + [bigger]) == bigger


def test_duplicating_every_element_never_changes_the_result():
    rng = random.Random(SEED + 6)
    for _ in range(TRIALS):
        depths = _random_depths(rng)
        assert max_nesting_depth(depths * 2) == max_nesting_depth(depths)


def test_a_list_containing_a_negative_always_raises():
    rng = random.Random(SEED + 7)
    for _ in range(TRIALS):
        depths = _random_depths(rng)
        depths.insert(rng.randint(0, len(depths)), rng.randint(-30, -1))
        with pytest.raises(ValueError):
            max_nesting_depth(depths)
