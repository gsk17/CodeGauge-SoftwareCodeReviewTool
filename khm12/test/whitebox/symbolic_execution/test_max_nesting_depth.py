"""White-box tests for max_nesting_depth - US12, Kasam (khm12).

Technique: symbolic execution with bounded loop unrolling.
Function under test: core.complexity.max_nesting_depth(depths).

Every function analysed in this project so far has been loop-free, so its tree
was finite and complete. This one is not, and that changes the method.

**The tree is infinite.** The input is a list of unknown length, so the loops
can be entered any number of times and the tree has no finite depth. Symbolic
execution handles this by **bounding the unrolling**: analyse lists of length
0, 1 and 2 exhaustively, and argue the general case by induction over the
pattern the bounded cases establish. The bound here is k = 2.

Symbolic inputs D0 and D1, symbolic integers, with the list length n as a
separate case split.

    n = 0
      P1   (no constraints)                              []        -> 0

    n = 1
      P2   D0 < 0                                        [-1]      -> ValueError
      P3   D0 >= 0 and D0 > 0                            [7]       -> D0
      P4   D0 >= 0 and D0 <= 0                           [0]       -> 0

    n = 2
      P5   D0 < 0                                        [-1, 3]   -> ValueError
      P6   D0 >= 0 and D1 < 0                            [3, -1]   -> ValueError
      P7   both >= 0, D0 > 0, D1 > D0                    [2, 5]    -> D1
      P8   both >= 0, D0 > 0, D1 <= D0                   [5, 2]    -> D0
      P9   both >= 0, D0 <= 0, D1 > 0                    [0, 4]    -> D1
      P10  both >= 0, D0 <= 0, D1 <= 0                   [0, 0]    -> 0

Ten paths at k = 2.

**Finding - P4 and P9 are single points, not ranges.** `deepest` is initialised
to 0 and validation has already established D0 >= 0, so the first iteration of
the scan takes its FALSE branch only when `D0 >= 0 and D0 <= 0`, which forces
**D0 = 0 exactly**. Unlike every other path condition in this function, that one
has a unique solution rather than an interval.

The same collapse applies to D1 in P9 and P10. So the false branch of the scan
comparison is, on the first iteration, reachable by exactly one input value -
and a test suite that only sampled positive depths would never execute it at
all. That is the one thing this analysis found that the black-box tests would
not have: the random-based tests generate depths in 0..20 and would hit a
leading zero only by chance.

**Why the bound is sound here.** Both loops are simple iterations over the
input with no early exit and no state carried between elements other than the
running maximum, which is updated by a monotone operation. The k = 2 cases
exhibit every combination of the two decisions, and the n-th case adds no new
decision - only another instance of b2 against a larger `deepest`. So the
bounded analysis generalises, and the inductive step is asserted below as a
property over longer lists rather than left as prose.
"""

import pytest

from core.complexity import max_nesting_depth


# --- n = 0 ---------------------------------------------------------------------

def test_p1_the_empty_list():
    # PC: none. Both loops are skipped and the initial value of deepest is
    # returned, which is the only path where the result comes from no element.
    assert max_nesting_depth([]) == 0


# --- n = 1 ---------------------------------------------------------------------

def test_p2_a_single_negative():
    # PC: D0 < 0. Boundary witness D0 = -1.
    with pytest.raises(ValueError):
        max_nesting_depth([-1])


def test_p3_a_single_positive():
    # PC: D0 >= 0 and D0 > 0. Any positive value; witness D0 = 7.
    assert max_nesting_depth([7]) == 7


def test_p4_a_single_zero_is_the_unique_solution_of_its_path():
    # PC: D0 >= 0 and D0 <= 0, which forces D0 = 0. The only input on this
    # path - see the Finding in the module docstring.
    assert max_nesting_depth([0]) == 0


# --- n = 2 ---------------------------------------------------------------------

def test_p5_the_first_element_is_negative():
    # PC: D0 < 0. Validation rejects before the second element is examined.
    with pytest.raises(ValueError):
        max_nesting_depth([-1, 3])


def test_p6_the_second_element_is_negative():
    # PC: D0 >= 0 and D1 < 0. Reached only because validation is a full pass
    # over the list before the scan begins.
    with pytest.raises(ValueError):
        max_nesting_depth([3, -1])


def test_p7_the_second_element_is_larger():
    # PC: both >= 0, D0 > 0, D1 > D0. Witness (2, 5) -> returns D1.
    assert max_nesting_depth([2, 5]) == 5


def test_p8_the_second_element_is_smaller():
    # PC: both >= 0, D0 > 0, D1 <= D0. Witness (5, 2) -> returns D0.
    assert max_nesting_depth([5, 2]) == 5


def test_p9_a_leading_zero_then_a_positive():
    # PC: both >= 0, D0 <= 0 (so D0 = 0), D1 > 0. Witness (0, 4).
    assert max_nesting_depth([0, 4]) == 4


def test_p10_two_zeros():
    # PC: both >= 0, D0 <= 0, D1 <= 0 - both forced to 0. The only input on
    # this path, and the only n = 2 input where the loop never assigns.
    assert max_nesting_depth([0, 0]) == 0


# --- the inductive step, asserted rather than argued ---------------------------

def test_the_bound_generalises_to_longer_lists():
    """k = 2 covers every combination of the two decisions; a longer list adds
    only further instances of b2. Checked by showing the result for lists of
    length 3 to 8 is always the largest element, whatever the arrangement."""
    cases = ([1, 2, 3], [3, 2, 1], [0, 0, 5], [5, 0, 0], [2, 9, 2, 1],
             [0, 0, 0, 0], [4, 4, 4, 4], [1, 0, 7, 3, 2, 6, 0, 5])
    for depths in cases:
        assert max_nesting_depth(depths) == max(depths)


def test_validation_precedes_the_scan_at_every_length():
    """A negative anywhere raises, regardless of position or of whether a
    larger value precedes it - the property the separate validation loop
    exists to guarantee."""
    for position in range(5):
        depths = [3, 9, 1, 7, 2]
        depths[position] = -4
        with pytest.raises(ValueError):
            max_nesting_depth(depths)
