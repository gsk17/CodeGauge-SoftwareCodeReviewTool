"""White-box tests for rule_complexity - US19, Saaket (ssl21).

Technique: symbolic execution, inter-procedural.
Function under test: core.rules.rule_complexity(cc, limit, line).

Symbolic inputs C (complexity), L (limit) and N (line). N is carried into the
Issue untouched and appears in no path condition, so the tree branches on C and
L alone.

This is the first function in the project whose tree crosses a call boundary.
classify_severity is inlined, so its decisions become part of these path
conditions, and the leaves of the combined tree are:

    Path  Path condition                                    Witness   Returns
    P1    C < 0                                             (-1, 10)  ValueError
    P2    C >= 0 and L < 1                                   (5, 0)   ValueError
    P3    C >= 0 and L >= 1 and C <= L                      (10, 10)  None
    P4    ... and C > L and C <= L + floor(L/2)             (11, 10)  MINOR
    P5    ... and C > L + floor(L/2) and C < 2L             (16, 10)  MAJOR
    P6    ... and C > L + floor(L/2) and C >= 2L            (20, 10)  CRITICAL

Six paths. The two findings below are the point of doing this analysis at all.

**Finding 1 - INFO is unreachable.** classify_severity has four outcomes, but
its INFO branch is guarded by `C <= L`, and P3 has already returned None under
exactly that condition. Conjoining the two gives `C > L and C <= L`, which is
unsatisfiable. **rule_complexity can therefore never produce an INFO issue** -
one quarter of the severity scale is dead code as reached from this rule.

This is not a defect. It is the correct consequence of a rule that only speaks
when a limit is exceeded: "within the limit" is represented by returning None,
not by an INFO-severity issue. But it is worth knowing, and it is only visible
by composing the two trees - neither function alone shows it.

**Finding 2 - at a limit of 1, only CRITICAL survives.** US26's analysis
already showed that with L = 1 the MINOR and MAJOR bands collapse: `C <= 1 +
floor(1/2) = 1` is consumed by the INFO branch, and `C > 1 and C < 2` has no
integer solution. Compose that with Finding 1 and every issue this rule raises
at a limit of 1 is CRITICAL, for every complexity above 1. Three of the four
bands are unreachable at that setting.

Taken together: the number of severities this rule can emit depends on the
configured limit - three for L >= 2, one for L = 1. That is a genuine
configuration hazard, derived rather than observed, and it belongs in the
README's known limitations.

**On floor(L/2).** Integer division makes P4 and P5 piecewise rather than
strictly linear, since floor(L/2) = k means L = 2k or L = 2k+1. Each witness is
solved by first fixing the parity of L; with L fixed to a concrete even value
every remaining constraint is linear in C.
"""

import pytest

from core.rules import CODE_COMPLEXITY, rule_complexity
from core.severity import CRITICAL, INFO, MAJOR, MINOR

LINE = 38


def test_p1_negative_complexity():
    # PC: C < 0. Boundary witness: C = -1.
    with pytest.raises(ValueError):
        rule_complexity(-1, 10, LINE)


def test_p2_limit_below_one():
    # PC: C >= 0 and L < 1. Witness (5, 0): C = 5 rather than 0 so the witness
    # also shows the first guard was evaluated and passed.
    with pytest.raises(ValueError):
        rule_complexity(5, 0, LINE)


def test_p3_within_the_limit_returns_none():
    # PC: C >= 0 and L >= 1 and C <= L. Witness (10, 10), solved at the
    # boundary where the constraint is tight.
    assert rule_complexity(10, 10, LINE) is None


def test_p4_minor():
    # PC: ... and C > L and C <= L + floor(L/2).
    # Fixing L = 10 gives floor(L/2) = 5, so C in 11..15. Witness C = 11.
    issue = rule_complexity(11, 10, LINE)
    assert issue.severity == MINOR
    assert issue.code == CODE_COMPLEXITY
    assert issue.line == LINE


def test_p5_major():
    # PC: ... and C > L + floor(L/2) and C < 2L.
    # With L = 10 the constraints collapse to C > 15 and C < 20, so
    # C in {16,17,18,19}. Witness C = 16, adjacent to the lower boundary.
    assert rule_complexity(16, 10, LINE).severity == MAJOR


def test_p6_critical():
    # PC: ... and C >= 2L. With L = 10, C >= 20. Witness C = 20.
    assert rule_complexity(20, 10, LINE).severity == CRITICAL


def test_finding_1_info_is_unreachable_through_this_rule():
    """`C > L and C <= L` is unsatisfiable, so no issue can carry INFO.

    The conjunction that would be needed is contradictory, so this is a proof
    over the whole domain rather than a sample. Swept broadly to match.
    """
    for limit in range(1, 40):
        for cc in range(0, 120):
            issue = rule_complexity(cc, limit, LINE)
            if issue is not None:
                assert issue.severity != INFO


def test_finding_2_at_a_limit_of_one_only_critical_is_reachable():
    """L = 1 collapses MINOR and MAJOR, and Finding 1 removes INFO.

    MINOR needs C <= 1 + floor(1/2) = 1, which P3 has consumed.
    MAJOR needs C > 1 and C < 2, which has no integer solution.
    So every issue raised at a limit of 1 is CRITICAL.
    """
    assert rule_complexity(1, 1, LINE) is None          # P3 consumes C <= L
    for cc in range(2, 60):
        assert rule_complexity(cc, 1, LINE).severity == CRITICAL


def test_the_reachable_band_count_depends_on_the_limit():
    """Three severities for L >= 2, one for L = 1 - the configuration hazard
    the composed analysis exposed."""
    def bands(limit):
        found = set()
        for cc in range(0, 200):
            issue = rule_complexity(cc, limit, LINE)
            if issue is not None:
                found.add(issue.severity)
        return found

    assert bands(1) == {CRITICAL}
    assert bands(10) == {MINOR, MAJOR, CRITICAL}
