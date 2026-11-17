"""White-box tests for rule_complexity - US19, Saaket (ssl21).

Technique: branch coverage.
Function under test: core.rules.rule_complexity(cc, limit, line).

Three decisions in the function itself:

    b1  cc < 0          guard, raises
    b2  limit < 1       guard, raises
    b3  cc <= limit     returns None

Each returns immediately when true, so the four outcomes below are the four
leaves of the function proper:

    test                        b1     b2     b3
    negative_complexity         TRUE   -      -
    limit_below_one             FALSE  TRUE   -
    within_the_limit            FALSE  FALSE  TRUE
    over_the_limit              FALSE  FALSE  FALSE

But the fourth leaf is not one path. Falling through b3 calls
classify_severity, which has decisions of its own, so the branches of the
callee are reachable from here and have to be covered too. Inlining it:

    b4  cc <= limit + limit // 2        -> MINOR
    b5  cc < 2 * limit                  -> MAJOR
    (else)                              -> CRITICAL

That gives **six branch outcomes to cover, not four**, and the three severity
tests below exist for b4 and b5 rather than to re-test US26.

**One outcome in the callee is unreachable from this caller.** classify_severity
returns INFO when `actual <= limit`, but b3 has already returned None in
exactly that case. So no input to rule_complexity can reach the INFO branch of
the callee. That is covered as an infeasible-path proof in the symbolic
execution tests, not as a branch here - there is no input that would exercise
it, and asserting otherwise would be asserting a falsehood.
"""

import pytest

from core.rules import rule_complexity
from core.severity import CRITICAL, INFO, MAJOR, MINOR

LINE = 38


def test_b1_true_rejects_a_negative_complexity():
    # b1 TRUE - returns before b2 is evaluated
    with pytest.raises(ValueError):
        rule_complexity(-1, 10, LINE)


def test_b2_true_rejects_a_limit_below_one():
    # b1 FALSE, b2 TRUE - proves the first guard passed a valid cc through
    with pytest.raises(ValueError):
        rule_complexity(5, 0, LINE)


def test_b3_true_returns_none_within_the_limit():
    # b1 FALSE, b2 FALSE, b3 TRUE - the no-finding path
    assert rule_complexity(10, 10, LINE) is None


def test_b3_false_b4_true_gives_minor():
    # b3 FALSE so an Issue is built; b4 TRUE inside classify_severity.
    # limit 10 -> limit + limit//2 = 15, so cc = 11 lands in 11..15
    assert rule_complexity(11, 10, LINE).severity == MINOR


def test_b4_false_b5_true_gives_major():
    # b4 FALSE, b5 TRUE: cc > 15 and cc < 20
    assert rule_complexity(16, 10, LINE).severity == MAJOR


def test_b4_false_b5_false_gives_critical():
    # b4 FALSE, b5 FALSE: the implicit else in the callee
    assert rule_complexity(20, 10, LINE).severity == CRITICAL


def test_the_info_branch_of_the_callee_is_never_reached():
    """b3 consumes every input that would make classify_severity return INFO.

    Not a branch test - a proof that one branch outcome of the callee has no
    reaching input through this caller. Swept over a wide domain because the
    claim is universal, and a single example would not support it.
    """
    for limit in range(1, 40):
        for cc in range(0, 120):
            issue = rule_complexity(cc, limit, LINE)
            if issue is not None:
                assert issue.severity != INFO
