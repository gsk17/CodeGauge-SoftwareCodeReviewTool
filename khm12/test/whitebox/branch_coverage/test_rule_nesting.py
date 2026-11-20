"""White-box tests for rule_nesting - US20, Kasam (khm12).

Technique: branch coverage.
Function under test: core.rules.rule_nesting(depth, limit, line).

Three decisions in the function itself:

    b1  depth < 0        guard, raises
    b2  limit < 1        guard, raises
    b3  depth <= limit   returns None

Each returns immediately when true, so those are three of the four leaves. The
fourth falls through to `classify_severity`, whose decisions are reachable from
here and therefore have to be covered too:

    b4  depth <= limit + limit // 2    -> MINOR
    b5  depth < 2 * limit              -> MAJOR
    (else)                             -> CRITICAL

Six branch outcomes, not four.

**The INFO outcome of the callee is unreachable from here**, for exactly the
reason it is unreachable from `rule_complexity`: b3 has already returned None
for every input that would produce it. It is proved in
`symbolic_execution/test_rule_nesting.py` rather than covered here, because no
input exercises it.

**Nesting limits are small in practice**, so the witnesses below use a limit of
3 rather than the 10 used for complexity. That changes which depths fall in
which band - `limit + limit // 2` is 4 rather than 15 - and it is worth checking
the bands at a realistic limit rather than reusing US19's numbers.
"""

import pytest

from core.rules import rule_nesting
from core.severity import CRITICAL, INFO, MAJOR, MINOR

LINE = 44


def test_b1_true_rejects_a_negative_depth():
    # b1 TRUE - returns before b2 is evaluated
    with pytest.raises(ValueError):
        rule_nesting(-1, 3, LINE)


def test_b2_true_rejects_a_limit_below_one():
    # b1 FALSE, b2 TRUE - proves the first guard passed a valid depth through
    with pytest.raises(ValueError):
        rule_nesting(5, 0, LINE)


def test_b3_true_returns_none_within_the_limit():
    # b1 FALSE, b2 FALSE, b3 TRUE - the no-finding path
    assert rule_nesting(3, 3, LINE) is None


def test_b3_false_b4_true_gives_minor():
    # b3 FALSE so an Issue is built; b4 TRUE in the callee.
    # limit 3 -> limit + limit//2 = 4, so depth 4 is the MINOR band entire
    assert rule_nesting(4, 3, LINE).severity == MINOR


def test_b4_false_b5_true_gives_major():
    # b4 FALSE, b5 TRUE: depth > 4 and depth < 6, so depth = 5 is the only
    # MAJOR depth at a limit of 3
    assert rule_nesting(5, 3, LINE).severity == MAJOR


def test_b4_false_b5_false_gives_critical():
    # b4 FALSE, b5 FALSE: depth >= 6, the implicit else in the callee
    assert rule_nesting(6, 3, LINE).severity == CRITICAL


def test_the_info_outcome_of_the_callee_is_never_reached():
    """b3 consumes every input that would make classify_severity return INFO.

    Not a branch test - a proof that one outcome of the callee has no reaching
    input through this caller. Swept over the whole realistic domain for a
    nesting limit, because the claim is universal.
    """
    for limit in range(1, 12):
        for depth in range(0, 40):
            issue = rule_nesting(depth, limit, LINE)
            if issue is not None:
                assert issue.severity != INFO


def test_the_rule_code_is_fixed_across_every_severity_branch():
    """The code identifies which rule spoke, not how badly. Every one of the
    three reachable severity outcomes must carry NEST001."""
    for depth in (4, 5, 6, 20):
        assert rule_nesting(depth, 3, LINE).code == "NEST001"
