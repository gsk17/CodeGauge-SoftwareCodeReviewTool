"""White-box tests for grade_band - US30, Harshita (hcg22).

Technique: branch coverage.
Function under test: core.scoring.grade_band(score).

Six decisions, evaluated in order:

    b1  score < 0            guard, returns via raise
    b2  score > 100          guard, returns via raise
    b3  score >= 85          returns "A"
    b4  score >= 70          returns "B"
    b5  score >= 60          returns "C"
    b6  score >= 50          returns "D"
    (implicit else)          returns "F"

Each decision returns immediately when true, so the branches form a chain: b4
is only reachable when b3 was false, b5 only when b4 was false, and so on. That
means a single test can only ever take one TRUE outcome, and the FALSE outcomes
of every earlier decision come along with it for free.

Seven tests therefore give full branch coverage - one per leaf. The table below
records which outcome each test is responsible for.

    test                          b1     b2     b3     b4     b5     b6
    negative_score                TRUE   -      -      -      -      -
    score_above_one_hundred       FALSE  TRUE   -      -      -      -
    grade_a                       FALSE  FALSE  TRUE   -      -      -
    grade_b                       FALSE  FALSE  FALSE  TRUE   -      -
    grade_c                       FALSE  FALSE  FALSE  FALSE  TRUE   -
    grade_d                       FALSE  FALSE  FALSE  FALSE  FALSE  TRUE
    grade_f                       FALSE  FALSE  FALSE  FALSE  FALSE  FALSE

A dash means the decision is not reached on that path, which is a property of
the code rather than a gap in the tests.
"""

import pytest

from core.scoring import grade_band


def test_b1_true_a_negative_score_is_rejected():
    # b1 TRUE - the only path that returns before b2 is evaluated
    with pytest.raises(ValueError):
        grade_band(-1)


def test_b2_true_a_score_above_one_hundred_is_rejected():
    # b1 FALSE, b2 TRUE - proves the first guard lets a valid-signed value past
    with pytest.raises(ValueError):
        grade_band(101)


def test_b3_true_returns_a():
    # b1 FALSE, b2 FALSE, b3 TRUE
    assert grade_band(85) == "A"


def test_b4_true_returns_b():
    # b3 FALSE, b4 TRUE
    assert grade_band(70) == "B"


def test_b5_true_returns_c():
    # b3 FALSE, b4 FALSE, b5 TRUE
    assert grade_band(60) == "C"


def test_b6_true_returns_d():
    # b3 FALSE, b4 FALSE, b5 FALSE, b6 TRUE
    assert grade_band(50) == "D"


def test_all_decisions_false_returns_f():
    # every decision FALSE - the implicit else, the only path with no return of
    # its own in the source
    assert grade_band(49) == "F"
