"""White-box tests for compare_scores - US31, Harshita (hcg22).

Technique: branch coverage, and condition coverage alongside it.
Function under test: core.history.compare_scores(before, after).

Six decisions, two of which are **compound**:

    b1  before < 0 or before > 100   -> ValueError      two conditions
    b2  after < 0 or after > 100     -> ValueError      two conditions
    b3  difference == 0              -> UNCHANGED
    b4  difference >= 10             -> MUCH_IMPROVED
    b5  difference > 0               -> IMPROVED
    b6  difference <= -10            -> MUCH_REGRESSED
    (implicit else)                  -> REGRESSED

Seven leaves, so seven tests give full branch coverage:

    test                    b1     b2     b3     b4     b5     b6
    before_invalid          TRUE   -      -      -      -      -
    after_invalid           FALSE  TRUE   -      -      -      -
    unchanged               FALSE  FALSE  TRUE   -      -      -
    much_improved           FALSE  FALSE  FALSE  TRUE   -      -
    improved                FALSE  FALSE  FALSE  FALSE  TRUE   -
    much_regressed          FALSE  FALSE  FALSE  FALSE  FALSE  TRUE
    regressed               FALSE  FALSE  FALSE  FALSE  FALSE  FALSE

A dash means the decision is not reached on that path.

**This is the first function in the project with a compound decision, so it is
the first where branch coverage and condition coverage differ.** b1 is true
when `before < 0`, when `before > 100`, or in principle when both - and `or`
short-circuits, so a true first operand means the second is never evaluated at
all.

    criterion              what it demands of b1               tests
    branch coverage        the decision both ways              2
    condition coverage     each operand both ways              2, if chosen well
    MC/DC                  each operand shown to decide alone  3

Seven tests chosen for branch coverage can easily leave `before < 0` never
evaluated true: a suite that only ever uses 101 as its invalid score covers
both branches of b1 and never runs the first operand to true. The tests marked
*condition coverage* below exist for that reason, and the four invalid cases
are deliberately split across the low and high ends of both parameters.

**Branch coverage of this function is 7 tests; honest coverage is 11.** The
difference is entirely in the two validations and is invisible to the coverage
tool, which reports 100% for either set.

**b5 looks redundant and is not.** `difference > 0` would alone catch every
improvement including large ones; it catches only the small ones because b4
precedes it. The guard order is load-bearing here, unlike US07 where the
guards form a conjunction and may be freely reordered - see
`symbolic_execution/test_compare_scores.py` finding 5.
"""

import pytest

from core.history import (
    IMPROVED,
    MUCH_IMPROVED,
    MUCH_REGRESSED,
    REGRESSED,
    UNCHANGED,
    compare_scores,
)

# --------------------------------------------------------------------------
# Branch coverage: one test per leaf.
# --------------------------------------------------------------------------


def test_b1_true_before_out_of_range():
    # b1 TRUE - returns before b2, so an equally invalid `after` is not seen
    with pytest.raises(ValueError) as caught:
        compare_scores(-1, 200)
    assert "before" in str(caught.value)


def test_b2_true_after_out_of_range():
    # b1 FALSE, b2 TRUE
    with pytest.raises(ValueError) as caught:
        compare_scores(50, 101)
    assert "after" in str(caught.value)


def test_b3_true_no_change():
    # b1 FALSE, b2 FALSE, b3 TRUE
    assert compare_scores(72, 72) == UNCHANGED


def test_b4_true_a_large_gain():
    # b1 FALSE, b2 FALSE, b3 FALSE, b4 TRUE
    assert compare_scores(72, 85) == MUCH_IMPROVED


def test_b5_true_a_small_gain():
    # b4 FALSE, b5 TRUE. Reached only with 0 < difference < 10, because b4
    # has already taken everything at 10 or above.
    assert compare_scores(72, 78) == IMPROVED


def test_b6_true_a_large_loss():
    # b4 FALSE, b5 FALSE, b6 TRUE
    assert compare_scores(72, 60) == MUCH_REGRESSED


def test_all_decisions_false_a_small_loss():
    # every decision FALSE - the implicit else, the only leaf with no return
    # of its own in the source
    assert compare_scores(72, 66) == REGRESSED


# --------------------------------------------------------------------------
# Condition coverage: the operands branch coverage leaves unexercised.
# --------------------------------------------------------------------------


def test_condition_coverage_before_below_zero():
    # b1's FIRST operand true. The test above used 200, which makes the
    # first operand false and the second true, so without this case
    # `before < 0` is never evaluated true by the suite.
    with pytest.raises(ValueError) as caught:
        compare_scores(-1, 50)
    assert "before" in str(caught.value)


def test_condition_coverage_before_above_one_hundred():
    # b1's SECOND operand true, with the first false
    with pytest.raises(ValueError) as caught:
        compare_scores(101, 50)
    assert "before" in str(caught.value)


def test_condition_coverage_after_below_zero():
    # b2's first operand true
    with pytest.raises(ValueError) as caught:
        compare_scores(50, -1)
    assert "after" in str(caught.value)


def test_condition_coverage_after_above_one_hundred():
    # b2's second operand true, with the first false
    with pytest.raises(ValueError) as caught:
        compare_scores(50, 101)
    assert "after" in str(caught.value)


def test_both_operands_false_at_the_valid_boundaries():
    # The only pair of values that exercises both operands of both
    # validations as false at their extremes. 0 and 100 are valid scores,
    # and a 100-point swing is the largest possible change.
    assert compare_scores(0, 100) == MUCH_IMPROVED
    assert compare_scores(100, 0) == MUCH_REGRESSED
    assert compare_scores(0, 0) == UNCHANGED
    assert compare_scores(100, 100) == UNCHANGED


# --------------------------------------------------------------------------
# The band boundaries, all inside the four returning leaves.
# --------------------------------------------------------------------------


def test_the_large_change_boundary_in_both_directions():
    # LARGE_CHANGE is 10, and both tests that use it are inclusive of it,
    # so a swing of exactly 10 is large and 9 is small.
    assert compare_scores(50, 59) == IMPROVED
    assert compare_scores(50, 60) == MUCH_IMPROVED
    assert compare_scores(50, 41) == REGRESSED
    assert compare_scores(50, 40) == MUCH_REGRESSED


def test_the_smallest_detectable_change_either_way():
    assert compare_scores(50, 51) == IMPROVED
    assert compare_scores(50, 49) == REGRESSED
