"""Black-box tests for compare_scores - US31, Harshita (hcg22).

Technique: random testing against invariants.
Function under test: core.history.compare_scores(before, after).

No expected band is written by hand. Each test states a property the
classification must satisfy for every pair of scores and samples the whole
0-100 square, with a fixed seed so any failure replays.

The sharp invariant here is **antisymmetry**: swapping the arguments must
reverse the direction and preserve the magnitude. An implementation using
`abs(after - before)` classifies the size correctly and loses the sign, so it
would pass every test about magnitude and fail this one on roughly half the
sampled pairs.
"""

import random

import pytest

from core.history import compare_scores

SEED = 20261124
TRIALS = 400

BANDS = ("MUCH_REGRESSED", "REGRESSED", "UNCHANGED", "IMPROVED", "MUCH_IMPROVED")

#: the band each one becomes when the two scores are swapped
OPPOSITE = {"MUCH_REGRESSED": "MUCH_IMPROVED", "REGRESSED": "IMPROVED",
            "UNCHANGED": "UNCHANGED", "IMPROVED": "REGRESSED",
            "MUCH_IMPROVED": "MUCH_REGRESSED"}


def _scores(rng):
    return rng.randint(0, 100), rng.randint(0, 100)


def test_every_result_is_one_of_the_five_bands():
    rng = random.Random(SEED)
    for _ in range(TRIALS):
        assert compare_scores(*_scores(rng)) in BANDS


def test_identical_scores_are_always_unchanged():
    rng = random.Random(SEED + 1)
    for _ in range(TRIALS):
        score = rng.randint(0, 100)
        assert compare_scores(score, score) == "UNCHANGED"


def test_unchanged_is_returned_only_for_identical_scores():
    rng = random.Random(SEED + 2)
    for _ in range(TRIALS):
        before, after = _scores(rng)
        if before != after:
            assert compare_scores(before, after) != "UNCHANGED"


def test_swapping_the_arguments_reverses_the_band():
    """Antisymmetry - the invariant an abs()-based implementation fails."""
    rng = random.Random(SEED + 3)
    for _ in range(TRIALS):
        before, after = _scores(rng)
        assert compare_scores(after, before) == OPPOSITE[compare_scores(before, after)]


def test_any_gain_is_classified_as_an_improvement():
    rng = random.Random(SEED + 4)
    for _ in range(TRIALS):
        before = rng.randint(0, 99)
        after = rng.randint(before + 1, 100)
        assert compare_scores(before, after) in ("IMPROVED", "MUCH_IMPROVED")


def test_any_loss_is_classified_as_a_regression():
    rng = random.Random(SEED + 5)
    for _ in range(TRIALS):
        before = rng.randint(1, 100)
        after = rng.randint(0, before - 1)
        assert compare_scores(before, after) in ("REGRESSED", "MUCH_REGRESSED")


def test_a_change_of_ten_or_more_is_always_the_larger_band():
    rng = random.Random(SEED + 6)
    for _ in range(TRIALS):
        before = rng.randint(0, 90)
        after = before + rng.randint(10, 100 - before)
        assert compare_scores(before, after) == "MUCH_IMPROVED"
        assert compare_scores(after, before) == "MUCH_REGRESSED"


def test_a_change_below_ten_is_always_the_smaller_band():
    rng = random.Random(SEED + 7)
    for _ in range(TRIALS):
        before = rng.randint(0, 91)
        after = before + rng.randint(1, 9)
        assert compare_scores(before, after) == "IMPROVED"
        assert compare_scores(after, before) == "REGRESSED"


def test_the_classification_never_weakens_as_the_gain_grows():
    """Monotonicity in the ordered band list: a bigger gain is never reported
    as a smaller improvement."""
    rng = random.Random(SEED + 8)
    for _ in range(TRIALS):
        before = rng.randint(0, 80)
        smaller = rng.randint(before, 90)
        larger = rng.randint(smaller, 100)
        assert (BANDS.index(compare_scores(before, larger))
                >= BANDS.index(compare_scores(before, smaller)))


def test_only_the_difference_matters_not_the_absolute_scores():
    """Shifting both scores by the same amount must not change the band - the
    function classifies a change, not a position on the scale."""
    rng = random.Random(SEED + 9)
    for _ in range(TRIALS):
        before, after = _scores(rng)
        expected = compare_scores(before, after)
        shift = rng.randint(-min(before, after), 100 - max(before, after))
        assert compare_scores(before + shift, after + shift) == expected


def test_all_five_bands_are_reachable():
    rng = random.Random(SEED + 10)
    seen = set()
    for _ in range(3000):
        seen.add(compare_scores(*_scores(rng)))
    assert seen == set(BANDS)


def test_a_score_outside_the_range_always_raises():
    rng = random.Random(SEED + 11)
    for _ in range(TRIALS):
        valid = rng.randint(0, 100)
        invalid = rng.choice((rng.randint(101, 5000), rng.randint(-5000, -1)))
        with pytest.raises(ValueError):
            compare_scores(invalid, valid)
        with pytest.raises(ValueError):
            compare_scores(valid, invalid)
