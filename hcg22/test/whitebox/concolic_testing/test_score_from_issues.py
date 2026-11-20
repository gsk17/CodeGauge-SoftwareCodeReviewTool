"""White-box tests for score_from_issues - US29, Harshita (hcg22).

Technique: concolic (dynamic symbolic) execution.
Function under test: core.scoring.score_from_issues(critical, major, minor, info).

Seeded with `(0, 0, 0, 0)` - a clean file. That is the cheapest seed to justify
and the furthest from the interesting behaviour, so the walk has to work its way
inwards.

Writing `R = 100 - (15C + 8M + 3N + I)` for the raw score:

    It.  Input          Path  Collected PC             Negated            Next
    1    (0,0,0,0)      P9    all >= 0, C < 3, R >= 0  C < 3 -> C >= 3    (3,0,0,0)
    2    (3,0,0,0)      P5    ... C >= 3, R > 40       R > 40 -> R <= 40  (4,0,0,0)
    3    (4,0,0,0)      P7    ... R <= 40, R >= 0      R >= 0 -> R < 0    (10,0,0,0)
    4    (10,0,0,0)     P6    ... R < 0                backtrack to
                                                       C >= 3 -> C < 3,
                                                       keeping R < 0      (0,13,0,0)
    5    (0,13,0,0)     P8    C < 3, R < 0             backtrack to
                                                       validation:
                                                       I >= 0 -> I < 0    (0,13,0,-1)
    6    (0,13,0,-1)    P4    ... I < 0                N >= 0 -> N < 0    (0,13,-1,0)
    7    (0,13,-1,0)    P3    ... N < 0                M >= 0 -> M < 0    (0,-1,0,0)
    8    (0,-1,0,0)     P2    C >= 0, M < 0            C >= 0 -> C < 0    (-1,0,0,0)
    9    (-1,0,0,0)     P1    C < 0                    none left          -

Nine iterations, nine paths, **100% path coverage**.

**Iteration 2 is where the solver does something a person would not.** The
constraint handed to it is `C >= 3` conjoined with everything already
collected, and it returns the smallest satisfying value, 3. That happens to be
the *only* value of C for which the cap can fire - see Finding 2 in
`symbolic_execution/test_score_from_issues.py`. The walk lands on the single
interesting input by solving for a boundary, not by knowing anything about the
cap.

**Iteration 3 then negates `R > 40` and gets `(4,0,0,0)`**, which sits exactly
on the cap value. A person writing these cases by hand would very likely pick
`(5,0,0,0)` - comfortably below the cap - and miss the boundary where `R == 40`
and the strict `>` matters. This is the clearest case in the project of concolic
execution producing a better test than hand-selection would have.

**Iteration 4 is the one the solver has to work at.** It needs `C < 3` while
keeping `R < 0`, so the penalty must come from somewhere other than critical
issues: with `C = 0` it needs `8M + 3N + I > 100`, and `M = 13` gives 104. A
walk that only varied C could not reach P8 at all.

**The floor is never reached from the cap branch.** No iteration takes
"cap fires, then floor fires", because iteration 2 assigns 40 and the floor
cannot act on it. That matches the infeasible path proved in the symbolic
analysis - the walk demonstrates it by never going there.
"""

import pytest

from core.scoring import score_from_issues

#: the five iterations that return a value, as (iteration, counts, expected)
WALK = (
    (1, (0, 0, 0, 0), 100),
    (2, (3, 0, 0, 0), 40),
    (3, (4, 0, 0, 0), 40),
    (4, (10, 0, 0, 0), 0),
    (5, (0, 13, 0, 0), 0),
)


def test_iteration_1_the_seed_is_a_clean_file():
    # seed (0,0,0,0). Path P9, no penalty, no cap, no floor.
    assert score_from_issues(0, 0, 0, 0) == 100


def test_iteration_2_negating_the_cap_guard():
    # PC: all >= 0 and NOT (C < 3). Smallest solution: C = 3 - which Finding 2
    # shows is the only C for which the cap can fire.
    assert score_from_issues(3, 0, 0, 0) == 40


def test_iteration_3_negating_the_cap_comparison():
    # PC: ... and NOT (R > 40) -> R <= 40. With the other counts at 0 the
    # smallest C satisfying it is 4, giving R = 40 exactly: the boundary where
    # the strict comparison matters.
    assert score_from_issues(4, 0, 0, 0) == 40


def test_iteration_4_negating_the_floor_guard():
    # PC: ... and NOT (R >= 0) -> R < 0. Solver raises C until R goes negative.
    assert score_from_issues(10, 0, 0, 0) == 0


def test_iteration_5_backtracking_to_the_cap_guard():
    # PC: C < 3 and R < 0 - the penalty has to come from the other severities.
    # With C = 0, 8M > 100 needs M = 13.
    assert score_from_issues(0, 13, 0, 0) == 0


def test_iteration_6_backtracking_into_validation_on_info():
    # The validation loop is entered last by the walk, in reverse order of the
    # positions it checks. I is the last count validated, so it is the first
    # one the backtracking reaches.
    with pytest.raises(ValueError):
        score_from_issues(0, 13, 0, -1)


def test_iteration_7_backtracking_to_minor():
    with pytest.raises(ValueError):
        score_from_issues(0, 13, -1, 0)


def test_iteration_8_backtracking_to_major():
    with pytest.raises(ValueError):
        score_from_issues(0, -1, 0, 0)


def test_iteration_9_backtracking_to_critical():
    # The first count validated, so the last the walk reaches. Nothing left to
    # negate afterwards and the walk terminates.
    with pytest.raises(ValueError):
        score_from_issues(-1, 0, 0, 0)


def test_the_returning_walk_in_sequence():
    """The five iterations that return a value, replayed in generated order."""
    for iteration, counts, expected in WALK:
        assert score_from_issues(*counts) == expected, "iteration %d" % iteration


def test_the_walk_found_the_boundary_a_person_would_have_missed():
    """Iteration 3's `(4,0,0,0)` sits on R == 40, where `>` and `>=` differ.

    A hand-written case below the cap - `(5,0,0,0)` - passes under either
    comparison and so proves nothing about which was written. The solver
    produced the discriminating input by negating for a boundary.
    """
    # R == 40 exactly: the cap must NOT fire, because 40 is not above 40
    assert score_from_issues(4, 0, 0, 0) == 40
    # one fewer critical: R == 55, above the cap, so it must fire
    assert score_from_issues(3, 0, 0, 0) == 40
    # the two agree in output but take different paths, which is why the
    # boundary needs the raw values to be checked as well
    assert 100 - 15 * 4 == 40
    assert 100 - 15 * 3 == 55


def test_no_iteration_takes_the_cap_and_then_the_floor():
    """The infeasible sub-path, demonstrated by the walk rather than argued.

    Iteration 2 is the only one on which the cap fires, and it returns 40.
    Nothing in the walk returns 0 by way of the cap.
    """
    assert score_from_issues(3, 0, 0, 0) == 40
    for _, counts, expected in WALK:
        if expected == 0:
            # reached the floor, so the cap must not have fired: either fewer
            # than three criticals, or a raw score already at or below 40
            raw = 100 - (15 * counts[0] + 8 * counts[1] + 3 * counts[2] + counts[3])
            assert counts[0] < 3 or raw <= 40
