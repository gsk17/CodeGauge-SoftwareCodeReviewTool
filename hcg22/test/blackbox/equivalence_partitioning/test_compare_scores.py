"""Black-box tests for compare_scores - US31, Harshita (hcg22).

Technique: equivalence partitioning with boundary value analysis.
Function under test: core.history.compare_scores(before, after).

The first function in the project to classify a **change** rather than a value.
Everything delivered so far takes a measurement and bands it; this takes two and
bands the difference, which makes the direction as significant as the size.

Five partitions, symmetric about zero:

    C1  after == before             "UNCHANGED"
    C2  gain of 1 to 9              "IMPROVED"
    C3  gain of 10 or more          "MUCH_IMPROVED"
    C4  loss of 1 to 9              "REGRESSED"
    C5  loss of 10 or more          "MUCH_REGRESSED"

    I1  either score outside 0-100  ValueError

**The partitions are symmetric and the tests are written to match**, because an
implementation that compares the magnitude of the difference without carrying
its sign - using `abs(after - before)` and then branching - will get one side
right and the other wrong. Every boundary below is therefore tested in both
directions: gains of 9 and 10, and losses of 9 and 10.

Boundaries tested: a difference of 0, ±1 (the smallest change), ±9 (the largest
small change), ±10 (the smallest large change), and the extreme cases 0 to 100
and 100 to 0.
"""

import pytest

from core.history import compare_scores


# --- C1: no change -------------------------------------------------------------

def test_c1_identical_scores_are_unchanged():
    assert compare_scores(62, 62) == "UNCHANGED"


def test_c1_unchanged_at_both_ends_of_the_range():
    # boundary: the two extreme scores, where a difference of 0 still holds
    assert compare_scores(0, 0) == "UNCHANGED"
    assert compare_scores(100, 100) == "UNCHANGED"


# --- C2: a small gain ----------------------------------------------------------

def test_c2_a_gain_of_one_is_improved():
    # boundary: the smallest possible improvement
    assert compare_scores(62, 63) == "IMPROVED"


def test_c2_a_gain_of_nine_is_improved():
    # boundary: the largest gain that is not MUCH_IMPROVED
    assert compare_scores(62, 71) == "IMPROVED"


def test_c2_an_ordinary_gain():
    assert compare_scores(62, 70) == "IMPROVED"


# --- C3: a large gain ----------------------------------------------------------

def test_c3_a_gain_of_ten_is_much_improved():
    # boundary: the smallest gain that counts as large
    assert compare_scores(62, 72) == "MUCH_IMPROVED"


def test_c3_the_largest_possible_gain():
    # boundary: 0 to 100, the extreme case
    assert compare_scores(0, 100) == "MUCH_IMPROVED"


# --- C4: a small loss ----------------------------------------------------------

def test_c4_a_loss_of_one_is_regressed():
    # boundary: the smallest possible regression, mirroring C2
    assert compare_scores(63, 62) == "REGRESSED"


def test_c4_a_loss_of_nine_is_regressed():
    # boundary: the largest loss that is not MUCH_REGRESSED
    assert compare_scores(71, 62) == "REGRESSED"


def test_c4_an_ordinary_loss():
    assert compare_scores(70, 62) == "REGRESSED"


# --- C5: a large loss ----------------------------------------------------------

def test_c5_a_loss_of_ten_is_much_regressed():
    # boundary: the smallest loss that counts as large
    assert compare_scores(72, 62) == "MUCH_REGRESSED"


def test_c5_the_largest_possible_loss():
    # boundary: 100 to 0
    assert compare_scores(100, 0) == "MUCH_REGRESSED"


# --- the symmetry, tested as a property ---------------------------------------

def test_the_bands_are_symmetric_about_zero():
    """Equal magnitudes in opposite directions must land in matching bands.

    The test an `abs()`-based implementation would fail: it would classify the
    size correctly and lose the direction, so one of each pair below would come
    back with the wrong name.
    """
    pairs = ((1, "IMPROVED", "REGRESSED"),
             (9, "IMPROVED", "REGRESSED"),
             (10, "MUCH_IMPROVED", "MUCH_REGRESSED"),
             (30, "MUCH_IMPROVED", "MUCH_REGRESSED"))
    for magnitude, gain_band, loss_band in pairs:
        assert compare_scores(50, 50 + magnitude) == gain_band
        assert compare_scores(50, 50 - magnitude) == loss_band


def test_swapping_the_arguments_reverses_the_direction():
    """`compare_scores(a, b)` and `compare_scores(b, a)` must be opposites, and
    never the same unless the scores are equal."""
    opposite = {"IMPROVED": "REGRESSED", "REGRESSED": "IMPROVED",
                "MUCH_IMPROVED": "MUCH_REGRESSED",
                "MUCH_REGRESSED": "MUCH_IMPROVED", "UNCHANGED": "UNCHANGED"}
    for before, after in ((62, 63), (62, 71), (62, 72), (0, 100), (50, 50)):
        assert compare_scores(after, before) == opposite[compare_scores(before, after)]


# --- I1: invalid input ---------------------------------------------------------

def test_i1_a_before_score_above_one_hundred_is_rejected():
    # boundary: the smallest invalid value
    with pytest.raises(ValueError):
        compare_scores(101, 50)


def test_i1_an_after_score_above_one_hundred_is_rejected():
    with pytest.raises(ValueError):
        compare_scores(50, 101)


def test_i1_a_negative_before_score_is_rejected():
    # boundary: the largest invalid value below the range
    with pytest.raises(ValueError):
        compare_scores(-1, 50)


def test_i1_a_negative_after_score_is_rejected():
    with pytest.raises(ValueError):
        compare_scores(50, -1)
