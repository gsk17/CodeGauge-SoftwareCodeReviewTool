"""White-box tests for rule_nesting - US20, Kasam (khm12).

Technique: symbolic execution, inter-procedural.
Function under test: core.rules.rule_nesting(depth, limit, line).

Symbolic inputs D (depth), L (limit) and N (line). `classify_severity` is
inlined, as it was for `rule_complexity` in US19, so the leaves of the combined
tree are:

    Path  Path condition                                    Witness   Returns
    P1    D < 0                                             (-1, 3)   ValueError
    P2    D >= 0 and L < 1                                   (5, 0)   ValueError
    P3    D >= 0 and L >= 1 and D <= L                       (3, 3)   None
    P4    ... and D > L and D <= L + floor(L/2)              (4, 3)   MINOR
    P5    ... and D > L + floor(L/2) and D < 2L              (5, 3)   MAJOR
    P6    ... and D > L + floor(L/2) and D >= 2L             (6, 3)   CRITICAL

Six paths. `N` appears in no path condition - it is carried into the Issue
untouched, so no choice of line number can change which path executes.

**This tree is structurally identical to US19's.** That is the point of the
analysis rather than a shortcut in writing it: the two rules were written
separately by different members, and the trees coming out the same shape is
what shows the shared contract was actually honoured. Had either re-implemented
the banding, the trees would differ below b3.

### The US19 findings are properties of the rule shape, not of that one rule

Both findings from US19 reappear here unchanged, which establishes they belong
to the *pattern* rather than to `rule_complexity`:

**Finding 1 - INFO is unreachable.** The INFO branch of `classify_severity`
needs `D <= L`, and P3 has already returned None under exactly that condition.
`D > L and D <= L` is unsatisfiable, so no issue this rule raises can carry
INFO.

**Finding 2 - at a limit of 1, only CRITICAL survives.** With `L = 1`:
MINOR needs `D <= 1 + floor(1/2) = 1`, which P3 consumes; MAJOR needs
`D > 1 and D < 2`, which has no integer solution.

**Finding 3, which is specific to nesting and new here.** Nesting limits are
small in practice - a configured limit above about 6 would be unusual - and the
band collapse is worse the smaller the limit is. Counting the reachable
severities at each realistic limit:

    L = 1    CRITICAL only                        1 band
    L = 2    MINOR (D=3), CRITICAL (D>=4)         2 bands
    L = 3    MINOR (4), MAJOR (5), CRITICAL (>=6) 3 bands
    L = 4    MINOR (5,6), MAJOR (7), CRITICAL     3 bands

At `L = 2` the MAJOR band is empty: it needs `D > 2 + 1 = 3` and `D < 4`, which
has no integer solution. So **the severity scale does not reach its full three
reachable bands until a nesting limit of 3**, and the project default is exactly
3 - which is the smallest limit at which the rule can express the full range it
was designed for.

That is luck rather than design. The default was chosen in the implementation
plan as a reasonable nesting depth, not by analysing the bands. It is recorded
here because the next person to adjust the default needs to know that lowering
it to 2 silently removes a severity band, and that lowering it to 1 removes two.
"""

import pytest

from core.rules import rule_nesting
from core.severity import CRITICAL, INFO, MAJOR, MINOR

LINE = 44


def test_p1_negative_depth():
    # PC: D < 0. Boundary witness D = -1.
    with pytest.raises(ValueError):
        rule_nesting(-1, 3, LINE)


def test_p2_limit_below_one():
    # PC: D >= 0 and L < 1. Witness (5, 0): D = 5 rather than 0 so the witness
    # also shows the first guard was evaluated and passed.
    with pytest.raises(ValueError):
        rule_nesting(5, 0, LINE)


def test_p3_within_the_limit_returns_none():
    # PC: D >= 0 and L >= 1 and D <= L. Witness (3, 3), solved at the boundary
    # where the constraint is tight.
    assert rule_nesting(3, 3, LINE) is None


def test_p4_minor():
    # PC: ... and D > L and D <= L + floor(L/2).
    # L = 3 gives floor(L/2) = 1, so the MINOR band is D = 4 alone.
    issue = rule_nesting(4, 3, LINE)
    assert issue.severity == MINOR
    assert issue.code == "NEST001"
    assert issue.line == LINE
    assert issue.message == "nesting depth 4 exceeds limit 3"


def test_p5_major():
    # PC: ... and D > L + floor(L/2) and D < 2L.
    # With L = 3: D > 4 and D < 6, so D = 5 is the only solution.
    assert rule_nesting(5, 3, LINE).severity == MAJOR


def test_p6_critical():
    # PC: ... and D >= 2L. With L = 3, D >= 6.
    assert rule_nesting(6, 3, LINE).severity == CRITICAL


# --- Finding 1 ----------------------------------------------------------------

def test_finding_1_info_is_unreachable_through_this_rule():
    """`D > L and D <= L` is unsatisfiable, so no issue can carry INFO."""
    for limit in range(1, 12):
        for depth in range(0, 40):
            issue = rule_nesting(depth, limit, LINE)
            if issue is not None:
                assert issue.severity != INFO


def test_finding_1_holds_identically_for_the_sibling_rule():
    """The same unreachability in `rule_complexity`, checked side by side.

    This is what shows Finding 1 is a property of the rule *shape*: two
    functions written separately by two members exhibit it identically.
    """
    from core.rules import rule_complexity
    for limit in range(1, 12):
        for actual in range(0, 40):
            nesting = rule_nesting(actual, limit, LINE)
            complexity = rule_complexity(actual, limit, LINE)
            # both silent, or both speaking with the same severity
            assert (nesting is None) == (complexity is None)
            if nesting is not None:
                assert nesting.severity == complexity.severity
                assert nesting.severity != INFO


# --- Finding 2 ----------------------------------------------------------------

def test_finding_2_at_a_limit_of_one_only_critical_is_reachable():
    """L = 1 collapses MINOR and MAJOR; Finding 1 removes INFO."""
    assert rule_nesting(1, 1, LINE) is None          # P3 consumes D <= L
    for depth in range(2, 30):
        assert rule_nesting(depth, 1, LINE).severity == CRITICAL


# --- Finding 3: the band count by limit, specific to nesting -------------------

def _reachable_bands(limit):
    found = set()
    for depth in range(0, 60):
        issue = rule_nesting(depth, limit, LINE)
        if issue is not None:
            found.add(issue.severity)
    return found


def test_finding_3_a_limit_of_two_has_an_empty_major_band():
    """At L = 2, MAJOR needs `D > 3 and D < 4` - no integer solution."""
    assert _reachable_bands(2) == {MINOR, CRITICAL}


def test_finding_3_three_is_the_smallest_limit_with_all_three_bands():
    assert _reachable_bands(1) == {CRITICAL}
    assert _reachable_bands(2) == {MINOR, CRITICAL}
    assert _reachable_bands(3) == {MINOR, MAJOR, CRITICAL}


def test_finding_3_the_project_default_is_that_smallest_limit():
    """`Thresholds` defaults `nesting_limit` to 3, which is the smallest value
    at which this rule can express all three bands it can reach. Recorded so
    that anyone lowering the default knows what it costs."""
    from model.thresholds import Thresholds
    assert Thresholds().nesting_limit == 3
    assert _reachable_bands(Thresholds().nesting_limit) == {MINOR, MAJOR, CRITICAL}
    assert len(_reachable_bands(2)) < 3
