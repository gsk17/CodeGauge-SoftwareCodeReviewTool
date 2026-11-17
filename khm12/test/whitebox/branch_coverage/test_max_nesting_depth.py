"""White-box tests for max_nesting_depth - US12, Kasam (khm12).

Technique: branch coverage.
Function under test: core.complexity.max_nesting_depth(depths).

This is the first function in the project with loops, so the branch structure
is not a chain. Two sequential loops, each with a decision inside:

    L1  the validation loop       for depth in depths
    b1    depth < 0               raises
    L2  the scan loop             for depth in depths
    b2    depth > deepest         updates the running maximum

A loop header is itself a two-outcome decision - taken, or exhausted - so there
are four decisions and eight outcomes to cover:

    outcome                          covered by
    L1 not taken (empty list)        empty_list
    L1 taken                         every other test
    b1 TRUE                          negative_first, negative_not_the_maximum
    b1 FALSE                         every passing test
    L2 not taken (empty list)        empty_list
    L2 taken                         every passing non-empty test
    b2 TRUE                          ascending_order (every element updates)
    b2 FALSE                         descending_order (no element updates
                                     after the first)

**b2 FALSE on the first iteration is a special case.** `deepest` starts at 0 and
every validated element is >= 0, so `depth > deepest` is false on the first
iteration only when the element is exactly 0. That outcome is covered
separately by the single-zero test, because no list of positive values can
reach it.

**Why validation is a separate loop.** Both loops iterate the same list. Fusing
them would be faster, but b1 would then only be evaluated for elements reached
before the function returns - and since the scan has no early exit that is
every element, so the behaviour would be the same. They are kept separate
because the separation is what makes "a negative value anywhere is rejected,
even when it is not the maximum" true by construction rather than by argument,
and that is the property the test below pins down.
"""

import pytest

from core.complexity import max_nesting_depth


def test_both_loops_not_taken_on_an_empty_list():
    # L1 not taken, L2 not taken - the only input that skips both loop bodies
    assert max_nesting_depth([]) == 0


def test_b1_true_on_the_first_element():
    # L1 taken, b1 TRUE immediately
    with pytest.raises(ValueError):
        max_nesting_depth([-1])


def test_b1_true_when_the_negative_is_not_the_maximum():
    # L1 taken several times, b1 FALSE then TRUE. This is the outcome a fused
    # validate-and-scan loop would get wrong: 9 is already the running maximum,
    # so a scan that only validated candidates would never inspect -2.
    with pytest.raises(ValueError):
        max_nesting_depth([9, -2, 4])


def test_b2_true_on_every_iteration():
    # L2 taken, b2 TRUE each time - an ascending list updates the maximum at
    # every step
    assert max_nesting_depth([1, 2, 3, 4]) == 4


def test_b2_false_after_the_first_iteration():
    # L2 taken, b2 TRUE once then FALSE for the rest - a descending list never
    # updates again after the first element
    assert max_nesting_depth([5, 3, 2, 1]) == 5


def test_b2_false_on_the_first_iteration():
    # The special case: deepest starts at 0, so b2 is false on iteration one
    # only when the element is exactly 0
    assert max_nesting_depth([0]) == 0


def test_b2_false_on_every_iteration():
    # A list of zeros takes b2 FALSE throughout, and the returned value is the
    # initial value of deepest rather than anything the loop assigned
    assert max_nesting_depth([0, 0, 0]) == 0


def test_b2_mixed_outcomes_with_the_maximum_in_the_middle():
    # b2 FALSE, TRUE, FALSE - the update happens at an interior position
    assert max_nesting_depth([1, 5, 2]) == 5
