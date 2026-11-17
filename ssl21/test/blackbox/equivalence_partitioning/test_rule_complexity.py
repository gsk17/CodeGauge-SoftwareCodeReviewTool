"""Black-box tests for rule_complexity - US19, Saaket (ssl21).

Technique: equivalence partitioning with boundary value analysis.
Function under test: core.rules.rule_complexity(cc, limit, line).

The rule raises an Issue when the cyclomatic complexity of a function exceeds
the configured limit, and returns None when it does not. Partitions:

    R1  cc < limit                 within budget         -> None
    R2  cc == limit                exactly at the limit  -> None
    R3  cc == limit + 1            first violation       -> Issue, severity from
                                                            classify_severity
    R4  cc well above the limit    severe violation      -> Issue, worse severity

The severity is not decided here: it is delegated to
core.severity.classify_severity(cc, limit), already delivered as US26. These
tests therefore assert the delegation rather than re-testing the bands.

Boundaries tested: cc at limit - 1, limit, and limit + 1, which is where an
off-by-one in the comparison shows up.
"""

import pytest

from core.rules import rule_complexity
from core.severity import CRITICAL, INFO, MAJOR, MINOR, RANK_ORDER, classify_severity

LINE = 38


# --- R1, R2: no violation ------------------------------------------------------

def test_r1_complexity_below_the_limit_raises_no_issue():
    assert rule_complexity(5, 10, LINE) is None


def test_r2_complexity_exactly_at_the_limit_raises_no_issue():
    # boundary: the limit is inclusive, so this must NOT be an issue
    assert rule_complexity(10, 10, LINE) is None


def test_r1_one_below_the_limit_raises_no_issue():
    # boundary: just inside the acceptable partition
    assert rule_complexity(9, 10, LINE) is None


def test_r2_the_smallest_possible_complexity_raises_no_issue():
    # cyclomatic complexity is never below 1
    assert rule_complexity(1, 10, LINE) is None


# --- R3: first violation -------------------------------------------------------

def test_r3_one_above_the_limit_raises_an_issue():
    # boundary: the smallest violating value
    assert rule_complexity(11, 10, LINE) is not None


def test_r3_the_issue_carries_the_rule_code():
    issue = rule_complexity(11, 10, LINE)
    assert issue.code == "CC001"


def test_r3_the_issue_carries_the_line_it_was_given():
    issue = rule_complexity(11, 10, LINE)
    assert issue.line == LINE


def test_r3_the_message_names_both_the_complexity_and_the_limit():
    issue = rule_complexity(11, 10, LINE)
    assert "11" in issue.message
    assert "10" in issue.message


def test_r3_the_severity_is_delegated_to_classify_severity():
    # US19 must not re-implement the banding delivered by US26
    issue = rule_complexity(11, 10, LINE)
    assert issue.severity == classify_severity(11, 10)


# --- R4: severe violation ------------------------------------------------------

def test_r4_twice_the_limit_is_critical():
    assert rule_complexity(20, 10, LINE).severity == CRITICAL


def test_r4_a_severe_violation_is_ranked_worse_than_a_marginal_one():
    marginal = rule_complexity(11, 10, LINE).severity
    severe = rule_complexity(20, 10, LINE).severity
    # RANK_ORDER runs worst-first, so a worse severity has a lower index
    assert RANK_ORDER.index(severe) < RANK_ORDER.index(marginal)


def test_r4_every_severity_produced_is_a_known_constant():
    for cc in (11, 14, 16, 20, 50):
        assert rule_complexity(cc, 10, LINE).severity in (INFO, MINOR, MAJOR, CRITICAL)


# --- invalid input -------------------------------------------------------------

def test_a_limit_below_one_is_rejected():
    # boundary: classify_severity requires limit >= 1, and the rule must not
    # swallow that contract
    with pytest.raises(ValueError):
        rule_complexity(5, 0, LINE)


def test_a_negative_complexity_is_rejected():
    with pytest.raises(ValueError):
        rule_complexity(-1, 10, LINE)
