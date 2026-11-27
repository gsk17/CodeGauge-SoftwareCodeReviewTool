"""Black-box tests for depth_from_indent - US03, Gunjan (gsk17).

Technique: random testing against invariants.
Function under test: core.line_metrics.depth_from_indent(indent_spaces,
spaces_per_level).

No expected depth is computed by hand - that would reimplement the function in
the test. Each test states a property the depth must satisfy for every width
and convention, and samples the space randomly. The seed is fixed so a failure
replays exactly.

The strongest invariant here is the **division identity**: the depth must
satisfy

    depth * spaces_per_level  <=  indent_spaces  <  (depth + 1) * spaces_per_level

That is the definition of floor division written as a bracket, and it pins the
result from both sides at once. An implementation that rounded to nearest, that
rounded up, or that was off by one anywhere would break the upper bound or the
lower bound immediately - which no single-sided property would catch.

The second invariant worth stating is **monotonicity in opposite directions**:
depth never falls as the width grows, and never rises as the convention widens.
Both are properties of the family of inputs rather than of any one of them, so
random sampling is the right technique for them.
"""

import random

import pytest

from core.line_metrics import depth_from_indent

SEED = 20261127
TRIALS = 400


def _inputs(rng, width_high=120, level_high=8):
    return rng.randint(0, width_high), rng.randint(1, level_high)


def test_the_depth_is_never_negative():
    rng = random.Random(SEED)
    for _ in range(TRIALS):
        assert depth_from_indent(*_inputs(rng)) >= 0


def test_the_division_identity_holds_from_both_sides():
    # depth * level <= width < (depth + 1) * level
    rng = random.Random(SEED)
    for _ in range(TRIALS):
        width, level = _inputs(rng)
        depth = depth_from_indent(width, level)
        assert depth * level <= width
        assert width < (depth + 1) * level


def test_the_depth_never_exceeds_the_width():
    # true because the convention is at least 1 space per level
    rng = random.Random(SEED)
    for _ in range(TRIALS):
        width, level = _inputs(rng)
        assert depth_from_indent(width, level) <= width


def test_depth_never_falls_as_the_width_grows():
    rng = random.Random(SEED)
    for _ in range(TRIALS):
        level = rng.randint(1, 8)
        start = rng.randint(0, 60)
        previous = depth_from_indent(start, level)
        for width in range(start + 1, start + 10):
            current = depth_from_indent(width, level)
            assert current >= previous
            previous = current


def test_depth_never_rises_as_the_convention_widens():
    rng = random.Random(SEED)
    for _ in range(TRIALS):
        width = rng.randint(0, 120)
        previous = depth_from_indent(width, 1)
        for level in range(2, 10):
            current = depth_from_indent(width, level)
            assert current <= previous
            previous = current


def test_a_whole_number_of_levels_round_trips():
    # if the width is built from a depth, the depth comes back exactly
    rng = random.Random(SEED)
    for _ in range(TRIALS):
        level = rng.randint(1, 8)
        depth = rng.randint(0, 20)
        assert depth_from_indent(depth * level, level) == depth


def test_a_partial_level_never_rounds_up():
    # adding anything less than a full level to a whole multiple must not
    # change the depth. This is the property that distinguishes flooring from
    # rounding to nearest, and it is checked at every offset including the
    # halfway point where the two disagree most.
    rng = random.Random(SEED)
    for _ in range(TRIALS):
        level = rng.randint(2, 8)
        depth = rng.randint(0, 20)
        base = depth * level
        for extra in range(0, level):
            assert depth_from_indent(base + extra, level) == depth


def test_one_space_per_level_is_the_identity():
    rng = random.Random(SEED)
    for _ in range(TRIALS):
        width = rng.randint(0, 500)
        assert depth_from_indent(width, 1) == width


def test_scaling_both_arguments_leaves_the_depth_unchanged():
    # multiplying the width and the convention by the same factor cannot
    # change the depth, because the factor cancels inside the division before
    # the floor is taken. An implementation that floored either argument
    # first, or that subtracted rather than divided, would break this.
    rng = random.Random(SEED)
    for _ in range(TRIALS):
        width, level = _inputs(rng, 60, 6)
        expected = depth_from_indent(width, level)
        for factor in (2, 3, 5):
            assert depth_from_indent(width * factor, level * factor) == expected


def test_negative_widths_are_always_rejected():
    rng = random.Random(SEED)
    for _ in range(TRIALS):
        width = -rng.randint(1, 200)
        level = rng.randint(1, 8)
        with pytest.raises(ValueError):
            depth_from_indent(width, level)


def test_conventions_below_one_are_always_rejected():
    rng = random.Random(SEED)
    for _ in range(TRIALS):
        width = rng.randint(0, 200)
        level = -rng.randint(0, 20)      # includes 0
        with pytest.raises(ValueError):
            depth_from_indent(width, level)
