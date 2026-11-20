"""White-box tests for rule_nesting - US20, Kasam (khm12).

Technique: concolic (dynamic symbolic) execution.
Function under test: core.rules.rule_nesting(depth, limit, line).

Seeded with `(D, L) = (1, 3)` - a shallow function inside a realistic nesting
limit, so the walk starts on the no-finding path.

    It.  Input    Path  Collected PC              Negated            Next
    1    (1, 3)   P3    D>=0, L>=1, D<=L          D <= L -> D > L    (4, 3)
    2    (4, 3)   P4    ... D <= L+L//2           -> D > L+L//2      (5, 3)
    3    (5, 3)   P5    ... D < 2L                -> D >= 2L         (6, 3)
    4    (6, 3)   P6    ... D >= 2L               backtrack b2:
                                                  L >= 1 -> L < 1    (6, 0)
    5    (6, 0)   P2    D>=0, L<1                 backtrack b1:
                                                  D >= 0 -> D < 0    (-1, 3)
    6    (-1, 3)  P1    D < 0                     none left          -

Six iterations, six paths, **100% path coverage**. The tree is finite because
neither `rule_nesting` nor `classify_severity` contains a loop.

**Every generated input is the tightest solution of its constraint, and at a
limit of 3 that means the bands are single values.** Iteration 1 negates
`D <= 3` and the solver returns 4 - which, since `L + L//2 = 4`, is the entire
MINOR band. Iteration 2 negates `D <= 4` and returns 5, which is the entire
MAJOR band, because `D < 2L = 6` leaves only 5. So the walk does not merely
sample the bands: at this limit it enumerates them exhaustively, because each
one contains exactly one integer.

That is a property of small limits rather than of the technique, and it is why
this walk is worth running separately from US19's despite the identical tree.
US19 seeds at a limit of 10, where each band holds several values and the
solver picks the boundary; here the boundary *is* the band. The two walks
exercise the same six paths under opposite conditions.

**Why the walk never produces an INFO issue.** Iteration 1 collects `D <= L`
and the solver negates it, so every later input satisfies `D > L`. The INFO
branch needs `D <= L`, so the solver is never asked for an input reaching it -
the constraint was negated away at the first step and nothing restores it. The
walk demonstrates what the symbolic analysis proves.

**Iteration 5 keeps D = 6 rather than resetting it.** Backtracking to b2 negates
only `L >= 1`; the rest of the collected condition is discarded along with the
branches below it, but nothing requires D to change, so the solver leaves it
where it was. A solver that minimised every variable would have returned
`(0, 0)` and taken the same path.
"""

import pytest

from core.rules import rule_nesting
from core.severity import CRITICAL, MAJOR, MINOR

LINE = 44

#: the four iterations that return a value, as (iteration, depth, limit, expected)
WALK = (
    (1, 1, 3, None),
    (2, 4, 3, MINOR),
    (3, 5, 3, MAJOR),
    (4, 6, 3, CRITICAL),
)


def test_iteration_1_the_seed_is_within_the_limit():
    # seed (1, 3). Path P3, no finding.
    assert rule_nesting(1, 3, LINE) is None


def test_iteration_2_negating_the_limit_comparison():
    # PC: D>=0, L>=1 and NOT (D <= L). Smallest solution at L=3: D = 4.
    assert rule_nesting(4, 3, LINE).severity == MINOR


def test_iteration_3_negating_the_minor_boundary():
    # PC: ... and NOT (D <= L + L//2) -> D > 4. Smallest solution: D = 5.
    assert rule_nesting(5, 3, LINE).severity == MAJOR


def test_iteration_4_negating_the_major_boundary():
    # PC: ... and NOT (D < 2L) -> D >= 6. Smallest solution: D = 6.
    assert rule_nesting(6, 3, LINE).severity == CRITICAL


def test_iteration_5_backtracking_to_the_limit_guard():
    # No branches left in the severity chain, so the walk backtracks to b2 and
    # negates L >= 1. Largest solution: L = 0. D is left where it was.
    with pytest.raises(ValueError):
        rule_nesting(6, 0, LINE)


def test_iteration_6_backtracking_to_the_depth_guard():
    # Negates D >= 0. Largest solution: D = -1.
    with pytest.raises(ValueError):
        rule_nesting(-1, 3, LINE)


def test_the_returning_walk_in_sequence():
    """The four iterations that return a value, replayed in generated order."""
    for iteration, depth, limit, expected in WALK:
        issue = rule_nesting(depth, limit, LINE)
        if expected is None:
            assert issue is None, "iteration %d" % iteration
        else:
            assert issue.severity == expected, "iteration %d" % iteration


def test_the_walk_enumerated_the_bands_rather_than_sampling_them():
    """At a limit of 3 the MINOR and MAJOR bands hold one integer each, so the
    boundary values the solver returned are the whole bands.

    Checked by confirming no other depth produces MINOR or MAJOR at this limit.
    """
    minors = [d for d in range(0, 40)
              if rule_nesting(d, 3, LINE) is not None
              and rule_nesting(d, 3, LINE).severity == MINOR]
    majors = [d for d in range(0, 40)
              if rule_nesting(d, 3, LINE) is not None
              and rule_nesting(d, 3, LINE).severity == MAJOR]
    assert minors == [4]
    assert majors == [5]


def test_the_same_tree_under_a_large_limit_behaves_differently():
    """US19's walk seeds at a limit of 10, where each band holds several
    values. The same six paths, but the solver returns a boundary *within* a
    band rather than the band itself - which is why both walks are run."""
    minors = [d for d in range(0, 40)
              if rule_nesting(d, 10, LINE) is not None
              and rule_nesting(d, 10, LINE).severity == MINOR]
    majors = [d for d in range(0, 40)
              if rule_nesting(d, 10, LINE) is not None
              and rule_nesting(d, 10, LINE).severity == MAJOR]
    assert minors == [11, 12, 13, 14, 15]
    assert majors == [16, 17, 18, 19]
