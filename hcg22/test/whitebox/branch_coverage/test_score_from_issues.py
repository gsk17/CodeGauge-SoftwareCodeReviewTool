"""White-box tests for score_from_issues - US29, Harshita (hcg22).

Technique: branch coverage.
Function under test: core.scoring.score_from_issues(critical, major, minor, info).

Three decisions, plus the validation loop:

    L   the validation loop        for name, value in counts
    b1    value < 0                raises
    b2  critical >= 3              the cap applies at all
    b3    score > 40               and only then does it lower the score
    b4  score < 0                  the floor

b3 is nested inside b2, so the two together give three reachable combinations
rather than four: (b2 false), (b2 true, b3 false), (b2 true, b3 true). b4 is
evaluated on every path that reaches it.

    outcome                       covered by
    b1 TRUE                       each of the four negative tests
    b1 FALSE                      every passing test
    b2 TRUE                       three_criticals, four_criticals, ten_criticals
    b2 FALSE                      clean_file, two_criticals, many_majors
    b3 TRUE                       three_criticals
    b3 FALSE                      four_criticals, ten_criticals
    b4 TRUE                       ten_criticals, many_majors
    b4 FALSE                      clean_file, two_criticals, three_criticals

**One combination is unreachable, and it is not a gap in these tests.** After
b3 lowers the score to 40, b4 cannot fire: 40 is not below 0. So the path
"b3 TRUE then b4 TRUE" has no input. That is proved in
`symbolic_execution/test_score_from_issues.py` rather than asserted here, since
no input would exercise it.
"""

import pytest

from core.scoring import score_from_issues


# --- b1: the validation loop ---------------------------------------------------

def test_b1_true_on_each_of_the_four_counts():
    # b1 TRUE once per argument position. The loop checks all four, so each
    # position has to be exercised separately.
    with pytest.raises(ValueError):
        score_from_issues(-1, 0, 0, 0)
    with pytest.raises(ValueError):
        score_from_issues(0, -1, 0, 0)
    with pytest.raises(ValueError):
        score_from_issues(0, 0, -1, 0)
    with pytest.raises(ValueError):
        score_from_issues(0, 0, 0, -1)


def test_b1_false_for_every_count_on_a_clean_file():
    # b1 FALSE four times, then b2 FALSE, then b4 FALSE
    assert score_from_issues(0, 0, 0, 0) == 100


# --- b2 FALSE: the cap does not apply ------------------------------------------

def test_b2_false_with_two_criticals():
    # b2 FALSE - fewer than three criticals, so the cap is not considered
    assert score_from_issues(2, 0, 0, 0) == 70


# --- b2 TRUE, b3 TRUE: the cap lowers the score --------------------------------

def test_b2_true_b3_true_the_cap_lowers_the_score():
    # b2 TRUE, b3 TRUE: raw 55 is above 40, so the cap applies
    assert score_from_issues(3, 0, 0, 0) == 40


# --- b2 TRUE, b3 FALSE: the cap applies but changes nothing --------------------

def test_b2_true_b3_false_at_exactly_the_cap():
    # b2 TRUE, b3 FALSE: raw is exactly 40, which is not *above* 40.
    # This is the outcome a cap written as an assignment would hide.
    assert score_from_issues(4, 0, 0, 0) == 40


def test_b2_true_b3_false_below_the_cap():
    # b2 TRUE, b3 FALSE: raw 25 is already below the cap
    assert score_from_issues(5, 0, 0, 0) == 25


# --- b4 TRUE: the floor --------------------------------------------------------

def test_b4_true_via_the_cap_branch():
    # b2 TRUE, b3 FALSE, b4 TRUE: raw -50, the cap does not fire, the floor does
    assert score_from_issues(10, 0, 0, 0) == 0


def test_b4_true_via_the_uncapped_branch():
    # b2 FALSE, b4 TRUE: no criticals at all, but enough majors to go negative.
    # 100 - (8 * 13) = -4
    assert score_from_issues(0, 13, 0, 0) == 0


def test_b4_false_at_exactly_zero():
    # b4 FALSE at the boundary: a raw score of exactly 0 must not be altered.
    # 100 - (8*12 + 3*1 + 1) = 100 - 100 = 0
    assert score_from_issues(0, 12, 1, 1) == 0
