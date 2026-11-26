"""White-box tests for comment_ratio_percent - US04, Gunjan (gsk17).

Technique: branch coverage.
Function under test: core.line_metrics.comment_ratio_percent(comment_lines,
code_lines).

Three decisions, each returning or raising immediately when true:

    b1  comment_lines < 0   -> ValueError
    b2  code_lines < 0      -> ValueError
    b3  counted == 0        -> 0
    (implicit else)         -> comment_lines * 100 // counted

Four leaves, so four tests give full branch coverage:

    test                        b1     b2     b3
    negative_comments           TRUE   -      -
    negative_code               FALSE  TRUE   -
    empty_file                  FALSE  FALSE  TRUE
    ordinary_file               FALSE  FALSE  FALSE

A dash means the decision is not reached on that path.

**b3 is satisfied by exactly one input.** Reaching it requires
`comment_lines >= 0`, `code_lines >= 0` and `comment_lines + code_lines == 0`,
and over the integers that system has the single solution `(0, 0)`. Every
other leaf in this function is reachable by infinitely many inputs; this one
is reachable by one. The test below is therefore not a representative of its
partition - it *is* its partition. See
`symbolic_execution/test_comment_ratio_percent.py` finding 1.

**There is no division-by-zero guard, and none is needed.** b3 is that guard,
and it is written as an equality rather than a `<= 0` because the two
validations above it have already ruled out a negative total. The tests at the
bottom of this file pin that dependency, because removing either validation
would make the equality and the inequality behave differently.
"""

import pytest

from core.line_metrics import comment_ratio_percent


def test_b1_true_negative_comment_count():
    # b1 TRUE - returns before b2 is evaluated, so the equally invalid
    # code_lines is never looked at and never mentioned in the message
    with pytest.raises(ValueError) as caught:
        comment_ratio_percent(-1, -1)
    assert "comment_lines" in str(caught.value)


def test_b2_true_negative_code_count():
    # b1 FALSE, b2 TRUE
    with pytest.raises(ValueError) as caught:
        comment_ratio_percent(0, -1)
    assert "code_lines" in str(caught.value)


def test_b3_true_the_empty_file():
    # b1 FALSE, b2 FALSE, b3 TRUE - the only input that reaches this leaf
    assert comment_ratio_percent(0, 0) == 0


def test_all_decisions_false_an_ordinary_file():
    # every decision FALSE - the implicit else, the only leaf that divides.
    # 28 comments among 170 counted lines is 16.47%, floored to 16.
    assert comment_ratio_percent(28, 142) == 16


def test_b1_takes_precedence_over_b2():
    # Both arguments are invalid. The order of the two validations is what
    # decides which fault is reported, and the caller learns about one of the
    # two faults only. Pinned because a reader fixing the reported fault and
    # re-running would meet the second error, not a result.
    with pytest.raises(ValueError) as caught:
        comment_ratio_percent(-5, -5)
    assert "code_lines" not in str(caught.value)


def test_b3_is_not_reachable_with_a_positive_comment_count():
    # The equality at b3 cannot fire once either count is positive, because
    # both are known non-negative by then. A comments-only file goes to the
    # division leaf and divides by comment_lines alone.
    assert comment_ratio_percent(7, 0) == 100


def test_the_division_leaf_never_divides_by_zero():
    # The one-value partition at b3 is the whole of the protection. Every
    # input that reaches the division has counted >= 1, so the floor division
    # is total on this leaf. Smallest two such inputs:
    assert comment_ratio_percent(1, 0) == 100
    assert comment_ratio_percent(0, 1) == 0
