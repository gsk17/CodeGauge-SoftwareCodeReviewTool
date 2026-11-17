"""White-box tests for rule_complexity - US19, Saaket (ssl21).

Technique: concolic (dynamic symbolic) execution.
Function under test: core.rules.rule_complexity(cc, limit, line).

Seeded with (C, L) = (5, 10) - a complexity comfortably inside the limit, so
the walk starts on the no-finding path and has to work outwards.

    It.  Input     Path  Collected PC                Branch negated      Next
    1    (5, 10)   P3    C>=0, L>=1, C<=L            C <= L -> C > L     (11,10)
    2    (11, 10)  P4    ... C <= L+L//2             -> C > L+L//2       (16,10)
    3    (16, 10)  P5    ... C < 2L                  -> C >= 2L          (20,10)
    4    (20, 10)  P6    ... C >= 2L                 backtrack b2:
                                                     L >= 1 -> L < 1     (20,0)
    5    (20, 0)   P2    C>=0, L<1                   backtrack b1:
                                                     C >= 0 -> C < 0     (-1,10)
    6    (-1, 10)  P1    C < 0                       none left           -

Six iterations, six paths, **100% path coverage**. The tree is finite because
neither rule_complexity nor classify_severity contains a loop.

**Why the walk never produces an INFO issue.** Iteration 1 collects `C <= L`
and the solver negates it, so every subsequent input satisfies `C > L`. The
INFO branch of the inlined classify_severity requires `C <= L`, so the solver
can never be asked for an input reaching it: the constraint was negated away at
the first step and nothing in the walk restores it. Concolic execution
*demonstrates* the unreachability that the symbolic analysis *proves* - the
walk simply never goes there, and the reason is visible in the collected
condition rather than argued separately.

**On the sixth iteration.** Backtracking to b1 negates `C >= 0`, and the solver
is free to pick any L it likes since the remaining conjunction constrains only
C. It returns to L = 10 rather than keeping L = 0, because `L < 1` was the
negation discharged at iteration 5 and is no longer on the path.
"""

import pytest

from core.rules import rule_complexity
from core.severity import CRITICAL, MAJOR, MINOR

LINE = 38

#: the six iterations above, as (iteration, cc, limit, expected severity or None)
WALK = (
    (1, 5, 10, None),
    (2, 11, 10, MINOR),
    (3, 16, 10, MAJOR),
    (4, 20, 10, CRITICAL),
)


def test_iteration_1_the_seed_is_within_the_limit():
    # seed (5, 10). Path P3, no finding.
    assert rule_complexity(5, 10, LINE) is None


def test_iteration_2_negating_the_limit_comparison():
    # PC: C>=0 and L>=1 and NOT (C <= L). Smallest solution at L=10: C = 11.
    assert rule_complexity(11, 10, LINE).severity == MINOR


def test_iteration_3_negating_the_minor_boundary():
    # PC: ... and NOT (C <= L + L//2) -> C > 15. Smallest solution: C = 16.
    assert rule_complexity(16, 10, LINE).severity == MAJOR


def test_iteration_4_negating_the_major_boundary():
    # PC: ... and NOT (C < 2L) -> C >= 20. Smallest solution: C = 20.
    assert rule_complexity(20, 10, LINE).severity == CRITICAL


def test_iteration_5_backtracking_to_the_limit_guard():
    # No branches left in the severity chain, so the walk backtracks to b2 and
    # negates L >= 1. Largest solution: L = 0.
    with pytest.raises(ValueError):
        rule_complexity(20, 0, LINE)


def test_iteration_6_backtracking_to_the_complexity_guard():
    # Backtracks again to b1 and negates C >= 0. Largest solution: C = -1.
    with pytest.raises(ValueError):
        rule_complexity(-1, 10, LINE)


def test_the_returning_walk_in_sequence():
    """The four iterations that return a value, replayed in generated order."""
    for iteration, cc, limit, expected in WALK:
        issue = rule_complexity(cc, limit, LINE)
        if expected is None:
            assert issue is None, "iteration %d" % iteration
        else:
            assert issue.severity == expected, "iteration %d" % iteration


def test_each_generated_input_sits_on_its_boundary():
    """The solver returns the extreme satisfying integer at each step, so one
    less than each generated complexity falls on the previous path."""
    # 11 is the first violation; 10 is the last non-violation
    assert rule_complexity(11, 10, LINE) is not None
    assert rule_complexity(10, 10, LINE) is None
    # 16 is the first MAJOR; 15 is the last MINOR
    assert rule_complexity(16, 10, LINE).severity == MAJOR
    assert rule_complexity(15, 10, LINE).severity == MINOR
    # 20 is the first CRITICAL; 19 is the last MAJOR
    assert rule_complexity(20, 10, LINE).severity == CRITICAL
    assert rule_complexity(19, 10, LINE).severity == MAJOR


def test_no_iteration_of_the_walk_produces_info():
    """Iteration 1 negated `C <= L` and nothing restores it, so the INFO
    branch is unreachable for the whole remainder of the walk."""
    for _, cc, limit, _expected in WALK[1:]:
        issue = rule_complexity(cc, limit, LINE)
        assert issue is not None
        assert issue.severity in (MINOR, MAJOR, CRITICAL)
