"""Black-box tests for depth_from_indent - US03, Gunjan (gsk17).

Technique: equivalence partitioning with boundary value analysis.
Function under test: core.line_metrics.depth_from_indent(indent_spaces,
spaces_per_level).

Converts an indentation width, as `count_leading_spaces` measured it, into a
nesting depth. The second argument is the project's indentation convention -
four spaces per level by default - so the same width means different depths in
differently formatted code.

    R1  no indentation            (0, 4)    -> 0
    R2  exactly one level         (4, 4)    -> 1
    R3  several whole levels      (12, 4)    -> 3
    R4  a partial level           (6, 4)    -> 1, not 2 and not an error
    R5  less than one level       (2, 4)    -> 0
    R6  a two-space convention    (6, 2)    -> 3
    R7  indent_spaces negative              -> ValueError
    R8  spaces_per_level below 1            -> ValueError

**R4 and R5 are the partitions this story exists for.** Real source is not
always indented in exact multiples: a continuation line, a hand-aligned
argument list or a file mixing conventions produces a width that is not a
whole number of levels. The alternatives were to raise, to round to nearest,
or to floor.

**Flooring is the specification.** A width of 6 against a 4-space convention is
reported as depth 1, not 2. The reason is the same one behind flooring the
comment ratio in US04: a derived measure must never overstate what it measured.
Depth feeds `rule_nesting`, which raises an issue when depth exceeds a limit, so
rounding up would let a hand-aligned continuation line trigger a nesting
finding against code that is not nested at all. Under-reporting a depth risks
missing a finding; over-reporting invents one, and an invented finding is worse
because it costs a reviewer's time and credibility.

**R5 is the sharpest case.** Two spaces against a 4-space convention is depth 0
- the line is treated as not indented. Returning 1 would be a defensible
"something is indented here" reading, and it is not what this function means:
depth 0 is "top level", and a line that has not completed one level of
indentation is still at top level.

**R8 rejects rather than defaults.** A `spaces_per_level` of zero would divide
by zero, and one of a negative number is meaningless. The function does not
quietly substitute 4, because a caller passing 0 has a bug and a silent default
hides it - the same argument `Thresholds.validate` makes for rejecting a limit
below 1 rather than clamping it.
"""

import pytest

from core.line_metrics import depth_from_indent


def test_r1_no_indentation_is_depth_zero():
    assert depth_from_indent(0, 4) == 0


def test_r2_exactly_one_level():
    assert depth_from_indent(4, 4) == 1


def test_r3_several_whole_levels():
    assert depth_from_indent(12, 4) == 3


def test_r4_a_partial_level_floors_down():
    # 6 spaces is one and a half levels. Reported as 1, never 2.
    assert depth_from_indent(6, 4) == 1


def test_r5_less_than_one_level_is_top_level():
    # 2 spaces has not completed a level, so the line is at depth 0
    assert depth_from_indent(2, 4) == 0


def test_r6_a_two_space_convention():
    # the same width means a different depth under a different convention
    assert depth_from_indent(6, 2) == 3
    assert depth_from_indent(6, 4) == 1


def test_r7_negative_indentation_is_rejected():
    with pytest.raises(ValueError) as caught:
        depth_from_indent(-1, 4)
    assert "indent_spaces" in str(caught.value)


def test_r8_a_zero_width_convention_is_rejected():
    # would divide by zero; rejected rather than defaulted to 4
    with pytest.raises(ValueError) as caught:
        depth_from_indent(8, 0)
    assert "spaces_per_level" in str(caught.value)


def test_r8_a_negative_width_convention_is_rejected():
    with pytest.raises(ValueError) as caught:
        depth_from_indent(8, -2)
    assert "spaces_per_level" in str(caught.value)


# --------------------------------------------------------------------------
# Boundary value analysis, around each level boundary at the default width.
# --------------------------------------------------------------------------


def test_boundaries_around_the_first_level():
    assert depth_from_indent(3, 4) == 0    # just below
    assert depth_from_indent(4, 4) == 1    # on it
    assert depth_from_indent(5, 4) == 1    # just above


def test_boundaries_around_the_second_level():
    assert depth_from_indent(7, 4) == 1
    assert depth_from_indent(8, 4) == 2
    assert depth_from_indent(9, 4) == 2


def test_the_smallest_valid_convention():
    # one space per level, so the width and the depth are the same number
    for width in range(0, 8):
        assert depth_from_indent(width, 1) == width


def test_the_boundary_of_the_convention_argument():
    # 1 is accepted, 0 is not - the boundary of R8
    assert depth_from_indent(4, 1) == 4
    with pytest.raises(ValueError):
        depth_from_indent(4, 0)


def test_a_width_far_beyond_any_plausible_nesting():
    # no upper bound is imposed. 200 spaces at 4 per level is depth 50, which
    # is absurd code and a real measurement of it. Clamping here would hide
    # the very thing the nesting rule exists to report.
    assert depth_from_indent(200, 4) == 50
