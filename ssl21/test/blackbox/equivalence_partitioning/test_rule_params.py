"""Black-box tests for rule_params - US22, Saaket (ssl21).

Technique: equivalence partitioning with boundary value analysis.
Function under test: core.rules.rule_params(param_count, limit, line).

The third rule in `core/rules.py`, and the third to use the shape US19
established: `None` when the measurement is within its limit, an `Issue` when it
is over, severity delegated to `classify_severity`. Code `PAR001`.

    R1  count < limit               -> None
    R2  count == limit              -> None
    R3  count == limit + 1          -> Issue, first violation
    R4  count well above the limit  -> Issue, worse severity

    I1  limit < 1                   -> ValueError
    I2  count < 0                   -> ValueError

The bands are not re-tested here; they belong to US26. What this story must
prove is that it **delegates** rather than re-implementing, and that it carries
its own code and message.

**This is the third near-identical rule, and that is now worth something.**
US19 established the shape, US20 showed the two findings were properties of the
shape rather than of one function, and US22 is the test of whether the shape
holds for a third measurement with a different limit scale - parameters, where
the default limit is 4, against complexity at 10 and nesting at 3. The last test
in this file checks all three rules agree on severity for identical numbers.
"""

import pytest

from core.rules import rule_params
from core.severity import CRITICAL, INFO, MAJOR, MINOR, RANK_ORDER, classify_severity

LINE = 38
LIMIT = 4


# --- R1, R2: no violation ------------------------------------------------------

def test_r1_fewer_parameters_than_the_limit_raises_no_issue():
    assert rule_params(2, LIMIT, LINE) is None


def test_r2_exactly_at_the_limit_raises_no_issue():
    # boundary: the limit is inclusive
    assert rule_params(4, LIMIT, LINE) is None


def test_r1_one_below_the_limit_raises_no_issue():
    assert rule_params(3, LIMIT, LINE) is None


def test_r2_a_function_with_no_parameters_raises_no_issue():
    # boundary: the smallest valid count
    assert rule_params(0, LIMIT, LINE) is None


# --- R3: the first violation ---------------------------------------------------

def test_r3_one_above_the_limit_raises_an_issue():
    # boundary: the smallest violating count
    assert rule_params(5, LIMIT, LINE) is not None


def test_r3_the_first_violation_is_minor():
    # limit 4 -> limit + limit//2 = 6, so 5 falls in the MINOR band
    assert rule_params(5, LIMIT, LINE).severity == MINOR


def test_r3_the_issue_carries_the_parameter_rule_code():
    assert rule_params(5, LIMIT, LINE).code == "PAR001"


def test_r3_the_issue_carries_the_line_it_was_given():
    assert rule_params(5, LIMIT, LINE).line == LINE


def test_r3_the_message_is_exactly_as_specified():
    assert rule_params(5, LIMIT, LINE).message == "5 parameters exceeds limit 4"


def test_r3_the_severity_is_delegated_to_classify_severity():
    assert rule_params(5, LIMIT, LINE).severity == classify_severity(5, LIMIT)


# --- R4: severe violations -----------------------------------------------------

def test_r4_twice_the_limit_is_critical():
    assert rule_params(8, LIMIT, LINE).severity == CRITICAL


def test_r4_a_severe_violation_is_ranked_worse_than_a_marginal_one():
    marginal = rule_params(5, LIMIT, LINE).severity
    severe = rule_params(12, LIMIT, LINE).severity
    assert RANK_ORDER.index(severe) < RANK_ORDER.index(marginal)


def test_r4_every_severity_produced_is_a_known_constant():
    for count in (5, 6, 7, 8, 20):
        assert rule_params(count, LIMIT, LINE).severity in (INFO, MINOR, MAJOR, CRITICAL)


# --- I1, I2: invalid input -----------------------------------------------------

def test_i1_a_limit_below_one_is_rejected():
    with pytest.raises(ValueError):
        rule_params(5, 0, LINE)


def test_i2_a_negative_parameter_count_is_rejected():
    with pytest.raises(ValueError):
        rule_params(-1, LIMIT, LINE)


# --- the shape, now checked across all three rules -----------------------------

def test_all_three_rules_agree_on_severity_for_the_same_numbers():
    """`rule_complexity`, `rule_nesting` and `rule_params` all delegate to the
    same banding, so for identical (actual, limit) pairs they must produce
    identical severities. Only the code and the message differ.

    This is the test that fails if any of the three ever re-implements the
    bands, and it is the reason the duplication between them is acceptable:
    the shape is enforced rather than merely intended.
    """
    from core.rules import rule_complexity, rule_nesting
    for actual, limit in ((5, 4), (8, 4), (12, 4), (4, 3), (6, 3),
                          (11, 10), (16, 10), (20, 10)):
        params = rule_params(actual, limit, LINE)
        nesting = rule_nesting(actual, limit, LINE)
        complexity = rule_complexity(actual, limit, LINE)
        # all three silent, or all three speaking with one severity
        assert (params is None) == (nesting is None) == (complexity is None)
        if params is not None:
            assert params.severity == nesting.severity == complexity.severity
            assert len({params.code, nesting.code, complexity.code}) == 3
