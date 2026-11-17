"""White-box tests for max_nesting_depth - US12, Kasam (khm12).

Technique: concolic (dynamic symbolic) execution.
Function under test: core.complexity.max_nesting_depth(depths).

Concolic execution suits a looping function better than pure symbolic execution
does, and this walk shows why. The concrete run **fixes the list length**, so
the loops are unrolled exactly as many times as the real input demands and no
bound has to be chosen in advance. The length only changes when the walk
deliberately changes it.

Seeded with [3, 1] - two elements, descending, both valid.

    It.  Input      Path  Collected PC                 Negated          Next
    1    [3, 1]     P8    D0>=0, D1>=0, D0>0, D1<=D0   D1<=D0 -> D1>D0  [3, 5]
    2    [3, 5]     P7    ... D1 > D0                  D0>0 -> D0<=0    [0, 5]
    3    [0, 5]     P9    ... D0<=0, D1>0              D1>0 -> D1<=0    [0, 0]
    4    [0, 0]     P10   ... D0<=0, D1<=0             backtrack to
                                                       validation:
                                                       D1>=0 -> D1<0    [0, -1]
    5    [0, -1]    P6    D0>=0, D1<0                  backtrack:
                                                       D0>=0 -> D0<0    [-1, -1]
    6    [-1, -1]   P5    D0 < 0                       no branch left
                                                       at n=2; shrink    [0]
    7    [0]        P4    D0>=0, D0<=0                 D0<=0 -> D0>0    [7]
    8    [7]        P3    D0>=0, D0>0                  shrink again      []
    9    []         P1    (no constraints)             none left         -

Nine iterations, nine of the ten bounded paths. P2 - a single negative element
- is the one the walk does not reach, because iteration 7 arrives at length 1
with `D0 >= 0` already on the path and the solver has no reason to drop it. It
is covered explicitly at the end, which is the honest way to report partial
coverage from a walk rather than claiming 100% and quietly adding a test.

**The length is not a symbolic variable.** Concolic execution can only negate
branch conditions, and the number of loop iterations is not a branch condition
- it is a property of the concrete input. So the walk cannot *solve* its way
from n = 2 to n = 1; the shrink steps at iterations 6 and 8 are a decision made
by the test designer, not by the solver.

That is the honest limitation of the technique on looping code, and it is worth
stating plainly: concolic execution explores the paths *within* a given
unrolling exhaustively, but moving between unrollings is manual. The bounded
symbolic analysis in symbolic_execution/ is what covers the choice of n;
this walk covers everything else.
"""

import pytest

from core.complexity import max_nesting_depth

#: the returning iterations of the walk, as (iteration, input, expected)
WALK = (
    (1, [3, 1], 3),
    (2, [3, 5], 5),
    (3, [0, 5], 5),
    (4, [0, 0], 0),
    (7, [0], 0),
    (8, [7], 7),
    (9, [], 0),
)


def test_iteration_1_the_seed():
    # seed [3, 1]. Path P8: the second element does not update the maximum.
    assert max_nesting_depth([3, 1]) == 3


def test_iteration_2_negating_the_scan_comparison():
    # PC: ... and NOT (D1 <= D0) -> D1 > 3. Solver returns 5.
    assert max_nesting_depth([3, 5]) == 5


def test_iteration_3_negating_the_first_comparison():
    # PC: ... and NOT (D0 > 0), which with D0 >= 0 forces D0 = 0 exactly.
    # The solver has no freedom here - see the single-point finding in the
    # symbolic analysis.
    assert max_nesting_depth([0, 5]) == 5


def test_iteration_4_negating_the_second_comparison():
    # PC: ... and NOT (D1 > 0) -> D1 = 0. Both elements now forced.
    assert max_nesting_depth([0, 0]) == 0


def test_iteration_5_backtracking_into_validation():
    # No branches left in the scan, so the walk backtracks to the validation
    # loop and negates D1 >= 0. Largest solution: D1 = -1.
    with pytest.raises(ValueError):
        max_nesting_depth([0, -1])


def test_iteration_6_backtracking_to_the_first_validation():
    # Negates D0 >= 0. Validation rejects on the first element, so the second
    # is never examined.
    with pytest.raises(ValueError):
        max_nesting_depth([-1, -1])


def test_iteration_7_after_shrinking_to_one_element():
    # Length reduced by hand, not by the solver. PC: D0 >= 0 and D0 <= 0.
    assert max_nesting_depth([0]) == 0


def test_iteration_8_negating_the_only_comparison():
    # PC: D0 >= 0 and NOT (D0 <= 0) -> D0 > 0. Solver returns 7.
    assert max_nesting_depth([7]) == 7


def test_iteration_9_after_shrinking_to_empty():
    # Both loops skipped. The walk terminates: no branch was executed, so
    # there is nothing left to negate.
    assert max_nesting_depth([]) == 0


def test_the_walk_in_sequence():
    """The seven returning iterations, replayed in generated order."""
    for iteration, depths, expected in WALK:
        assert max_nesting_depth(depths) == expected, "iteration %d" % iteration


def test_p2_the_path_the_walk_did_not_reach():
    """A single negative element - the one bounded path the walk misses.

    Reported rather than hidden: iteration 7 reaches length 1 carrying
    `D0 >= 0`, and nothing in the remaining walk negates it at that length.
    Covered here directly so the path set is complete even though the walk
    did not generate it.
    """
    with pytest.raises(ValueError):
        max_nesting_depth([-1])
