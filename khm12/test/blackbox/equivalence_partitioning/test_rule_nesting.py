"""Black-box tests for rule_nesting - US20, Kasam (khm12).

Technique: equivalence partitioning with boundary value analysis.
Function under test: core.rules.rule_nesting(depth, limit, line).

The second rule in `core/rules.py`, and deliberately the same shape as US19's
`rule_complexity`: return None when the measurement is within its limit, an
Issue when it is over, and let `core.severity.classify_severity` decide how bad
it is. Partitions:

    R1  depth < limit              within budget         -> None
    R2  depth == limit             exactly at the limit  -> None
    R3  depth == limit + 1         first violation       -> Issue
    R4  depth well above the limit severe violation      -> Issue, worse severity

    Invalid
    I1  limit < 1                                        -> ValueError
    I2  depth < 0                                        -> ValueError

The severity bands are **not** re-tested here. They belong to US26 and are
already covered by that story's own black-box tests; what this story has to
prove is that it *delegates* rather than re-implementing, and that it carries
its own rule code and message.

**Why the duplication with US19 is deliberate.** `rule_nesting` and
`rule_complexity` could have been one parameterised function taking a code and a
message template. They are kept separate because each rule is a graded user
story owned by a different member, and because a shared helper would put two
members' marks in one function. The cost is a near-identical test file; the
benefit is that the two stories can be assessed independently.
"""

import pytest

from core.rules import rule_nesting
from core.severity import CRITICAL, INFO, MAJOR, MINOR, RANK_ORDER, classify_severity

LINE = 44


# --- R1, R2: no violation ------------------------------------------------------

def test_r1_nesting_below_the_limit_raises_no_issue():
    assert rule_nesting(1, 3, LINE) is None


def test_r2_nesting_exactly_at_the_limit_raises_no_issue():
    # boundary: the limit is inclusive, so this must NOT be an issue
    assert rule_nesting(3, 3, LINE) is None


def test_r1_one_below_the_limit_raises_no_issue():
    # boundary: just inside the acceptable partition
    assert rule_nesting(2, 3, LINE) is None


def test_r2_zero_nesting_raises_no_issue():
    # boundary: the smallest valid depth. A flat function is never a finding.
    assert rule_nesting(0, 3, LINE) is None


# --- R3: the first violation ---------------------------------------------------

def test_r3_one_above_the_limit_raises_an_issue():
    # boundary: the smallest violating value
    assert rule_nesting(4, 3, LINE) is not None


def test_r3_the_issue_carries_the_nesting_rule_code():
    # NEST001, not CC001 - the code identifies which rule spoke
    assert rule_nesting(4, 3, LINE).code == "NEST001"


def test_r3_the_issue_carries_the_line_it_was_given():
    assert rule_nesting(4, 3, LINE).line == LINE


def test_r3_the_message_is_exactly_as_specified():
    assert rule_nesting(4, 3, LINE).message == "nesting depth 4 exceeds limit 3"


def test_r3_the_severity_is_delegated_to_classify_severity():
    # US20 must not re-implement the banding delivered by US26
    assert rule_nesting(4, 3, LINE).severity == classify_severity(4, 3)


# --- R4: severe violations -----------------------------------------------------

def test_r4_twice_the_limit_is_critical():
    assert rule_nesting(6, 3, LINE).severity == CRITICAL


def test_r4_a_severe_violation_is_ranked_worse_than_a_marginal_one():
    marginal = rule_nesting(4, 3, LINE).severity
    severe = rule_nesting(9, 3, LINE).severity
    # RANK_ORDER runs worst-first, so a worse severity has a lower index
    assert RANK_ORDER.index(severe) < RANK_ORDER.index(marginal)


def test_r4_every_severity_produced_is_a_known_constant():
    for depth in (4, 5, 6, 9, 20):
        assert rule_nesting(depth, 3, LINE).severity in (INFO, MINOR, MAJOR, CRITICAL)


# --- I1, I2: invalid input -----------------------------------------------------

def test_i1_a_limit_below_one_is_rejected():
    # boundary: the largest invalid limit
    with pytest.raises(ValueError):
        rule_nesting(5, 0, LINE)


def test_i1_a_negative_limit_is_rejected():
    with pytest.raises(ValueError):
        rule_nesting(5, -2, LINE)


def test_i2_a_negative_depth_is_rejected():
    # boundary: the largest invalid depth
    with pytest.raises(ValueError):
        rule_nesting(-1, 3, LINE)


# --- the shared shape, checked against the sibling rule ------------------------

def test_the_two_rules_agree_on_severity_for_the_same_numbers():
    """`rule_nesting` and `rule_complexity` both delegate to the same banding,
    so for identical (actual, limit) pairs they must produce identical
    severities. Only the code and the message should differ.

    This is the test that would fail if either story quietly re-implemented
    the bands instead of calling `classify_severity`.
    """
    from core.rules import rule_complexity
    for actual, limit in ((4, 3), (6, 3), (9, 3), (11, 10), (16, 10), (20, 10)):
        nesting = rule_nesting(actual, limit, LINE)
        complexity = rule_complexity(actual, limit, LINE)
        assert nesting.severity == complexity.severity
        assert nesting.code != complexity.code
