"""Black-box tests for max_nesting_depth - US12, Kasam (khm12).

Technique: equivalence partitioning with boundary value analysis.
Function under test: core.complexity.max_nesting_depth(depths).

The input is a list of per-line nesting depths for one function. Partitions:

    D1  the empty list                  []            -> 0 by definition
    D2  a single element                [0], [7]      -> that element
    D3  several, maximum at the start    [5, 1, 2]    -> 5
    D4  several, maximum in the middle   [1, 5, 2]    -> 5
    D5  several, maximum at the end      [1, 2, 5]    -> 5
    D6  all elements equal               [3, 3, 3]    -> 3
    D7  contains a negative element      [1, -2]      -> ValueError

D3, D4 and D5 are kept apart deliberately: a scan that tracks a running maximum
incorrectly can pass for one position and fail for another.

Boundaries tested: the empty list, a one-element list, the value 0 as the
smallest valid depth, and -1 as the largest invalid depth.
"""

import pytest

from core.complexity import max_nesting_depth


# --- D1: empty -----------------------------------------------------------------

def test_d1_an_empty_list_has_zero_depth():
    # boundary: the shortest possible input. A function with no lines is not
    # nested, so the answer is 0 rather than an error.
    assert max_nesting_depth([]) == 0


# --- D2: single element --------------------------------------------------------

def test_d2_a_single_zero_is_zero():
    # boundary: smallest valid element in the shortest non-empty list
    assert max_nesting_depth([0]) == 0


def test_d2_a_single_element_is_its_own_maximum():
    assert max_nesting_depth([7]) == 7


# --- D3, D4, D5: maximum at each position --------------------------------------

def test_d3_maximum_at_the_start():
    assert max_nesting_depth([5, 1, 2, 3]) == 5


def test_d4_maximum_in_the_middle():
    assert max_nesting_depth([1, 5, 3, 2]) == 5


def test_d5_maximum_at_the_end():
    assert max_nesting_depth([1, 2, 3, 5]) == 5


# --- D6: all equal -------------------------------------------------------------

def test_d6_a_list_of_equal_depths_returns_that_depth():
    assert max_nesting_depth([3, 3, 3]) == 3


def test_d6_a_list_of_zeros_returns_zero():
    assert max_nesting_depth([0, 0, 0]) == 0


# --- D7: invalid ---------------------------------------------------------------

def test_d7_a_negative_element_is_rejected():
    # boundary: -1 is the largest invalid depth
    with pytest.raises(ValueError):
        max_nesting_depth([1, -1])


def test_d7_a_negative_element_is_rejected_even_when_it_is_not_the_maximum():
    # the guard must inspect every element, not just the running maximum
    with pytest.raises(ValueError):
        max_nesting_depth([9, -2, 4])


def test_d7_a_list_of_one_negative_is_rejected():
    with pytest.raises(ValueError):
        max_nesting_depth([-5])
