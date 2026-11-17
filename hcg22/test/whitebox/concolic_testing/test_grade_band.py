"""White-box tests for grade_band - US30, Harshita (hcg22).

Technique: concolic (dynamic symbolic) execution.
Function under test: core.scoring.grade_band(score).

Concolic execution runs the function on a concrete input while collecting the
path condition symbolically, then negates the last unexplored branch and solves
for the next input. Unlike pure symbolic execution it never has to reason about
a path it has not actually run.

Seeded with S = 100, which is the top of the domain.

    It.  Input  Path  Collected PC              Branch negated       Next input
    1    100    P3    S>=0, S<=100, S>=85       S >= 85 -> S < 85    84
    2     84    P4    ... S<85, S>=70           S >= 70 -> S < 70    69
    3     69    P5    ... S<70, S>=60           S >= 60 -> S < 60    59
    4     59    P6    ... S<60, S>=50           S >= 50 -> S < 50    49
    5     49    P7    ... S<50                  backtrack b2:
                                                S <= 100 -> S > 100  101
    6    101    P2    S>=0, S>100               backtrack b1:
                                                S >= 0  -> S < 0     -1
    7     -1    P1    S < 0                     none left            -

Seven iterations, seven paths, **100% path coverage**.

Two things are worth noting about the sequence.

**The solver always returns a threshold.** Negating `S >= 85` gives `S < 85`
conjoined with everything already collected, and the solver returns the largest
satisfying integer, 84. Every input after the seed is therefore a boundary
value - concolic execution rediscovers, mechanically, the same values boundary
value analysis picks by hand in the black-box tests. That agreement between two
independently derived test sets is the most useful result here.

**Negation order drives the walk downwards.** Because the grade chain is
ordered best-first and each negation pushes the score below the previous
threshold, the walk descends A, B, C, D, F and only then backtracks to the two
guards. A seed of 0 would walk the tree in the opposite order and find the same
seven paths; the ordering is a property of the seed, not of the function.
"""

import pytest

from core.scoring import grade_band

#: the concolic walk above, as (iteration, input, expected outcome)
WALK = (
    (1, 100, "A"),
    (2, 84, "B"),
    (3, 69, "C"),
    (4, 59, "D"),
    (5, 49, "F"),
)


def test_iteration_1_the_seed():
    # seed S = 100, the top of the domain. Path P3.
    assert grade_band(100) == "A"


def test_iteration_2_negating_the_a_threshold():
    # PC: S>=0 and S<=100 and NOT (S >= 85). Largest solution: 84.
    assert grade_band(84) == "B"


def test_iteration_3_negating_the_b_threshold():
    # PC: ... and NOT (S >= 70). Largest solution: 69.
    assert grade_band(69) == "C"


def test_iteration_4_negating_the_c_threshold():
    # PC: ... and NOT (S >= 60). Largest solution: 59.
    assert grade_band(59) == "D"


def test_iteration_5_negating_the_d_threshold():
    # PC: ... and NOT (S >= 50). Largest solution: 49.
    assert grade_band(49) == "F"


def test_iteration_6_backtracking_to_the_upper_guard():
    # No branches left on the grade chain, so the walk backtracks to b2 and
    # negates S <= 100. Smallest solution: 101.
    with pytest.raises(ValueError):
        grade_band(101)


def test_iteration_7_backtracking_to_the_lower_guard():
    # Backtracks again to b1 and negates S >= 0. Largest solution: -1.
    with pytest.raises(ValueError):
        grade_band(-1)


def test_the_whole_walk_in_sequence():
    """The five returning iterations, replayed in the order concolic execution
    generated them. Keeping the sequence as data makes the walk itself the
    test, rather than seven unrelated assertions that happen to use the values
    it produced."""
    for iteration, score, expected in WALK:
        assert grade_band(score) == expected, "iteration %d" % iteration


def test_every_input_after_the_seed_is_a_threshold_value():
    """The solver returns the extreme satisfying integer at each step, so each
    generated input sits one away from a decision boundary. Checked by showing
    the neighbour above each one grades differently."""
    for _, score, expected in WALK[1:]:
        assert grade_band(score) == expected
        assert grade_band(score + 1) != expected
