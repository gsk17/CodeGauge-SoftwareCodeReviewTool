"""Black-box tests for rule_params - US22, Saaket (ssl21).

Technique: random testing against invariants.
Function under test: core.rules.rule_params(param_count, limit, line).

No expected Issue is built by hand. Each test states a property the rule must
satisfy over its domain and samples randomly, with a fixed seed.

Parameter limits sit between the other two rules in scale - the project default
is 4, against 3 for nesting and 10 for complexity - so the sampled range is
1..10. Sampling where a function will actually be used is a deliberate choice
made separately for each of the three rules.
"""

import random

import pytest

from core.rules import rule_params
from core.severity import CRITICAL, INFO, MAJOR, MINOR, RANK_ORDER, classify_severity

SEED = 20261124
TRIALS = 250
BANDS = (INFO, MINOR, MAJOR, CRITICAL)


def test_within_the_limit_the_rule_is_always_silent():
    rng = random.Random(SEED)
    for _ in range(TRIALS):
        limit = rng.randint(1, 10)
        assert rule_params(rng.randint(0, limit), limit, rng.randint(1, 500)) is None


def test_above_the_limit_the_rule_always_speaks():
    rng = random.Random(SEED + 1)
    for _ in range(TRIALS):
        limit = rng.randint(1, 10)
        count = limit + rng.randint(1, 30)
        assert rule_params(count, limit, rng.randint(1, 500)) is not None


def test_every_issue_carries_the_parameter_code():
    rng = random.Random(SEED + 2)
    for _ in range(TRIALS):
        limit = rng.randint(1, 10)
        issue = rule_params(limit + rng.randint(1, 30), limit, rng.randint(1, 500))
        assert issue.code == "PAR001"


def test_the_reported_line_is_always_the_line_passed_in():
    rng = random.Random(SEED + 3)
    for _ in range(TRIALS):
        limit = rng.randint(1, 10)
        line = rng.randint(1, 10000)
        assert rule_params(limit + rng.randint(1, 30), limit, line).line == line


def test_the_message_always_names_both_numbers_in_order():
    rng = random.Random(SEED + 4)
    for _ in range(TRIALS):
        limit = rng.randint(1, 10)
        count = limit + rng.randint(1, 30)
        message = rule_params(count, limit, rng.randint(1, 500)).message
        assert message == "%d parameters exceeds limit %d" % (count, limit)


def test_every_severity_is_one_of_the_four_known_bands():
    rng = random.Random(SEED + 5)
    for _ in range(TRIALS):
        limit = rng.randint(1, 10)
        issue = rule_params(limit + rng.randint(1, 40), limit, rng.randint(1, 500))
        assert issue.severity in BANDS


def test_the_severity_always_matches_classify_severity():
    rng = random.Random(SEED + 6)
    for _ in range(TRIALS):
        limit = rng.randint(1, 10)
        count = limit + rng.randint(1, 40)
        issue = rule_params(count, limit, rng.randint(1, 500))
        assert issue.severity == classify_severity(count, limit)


def test_severity_never_improves_as_parameters_are_added():
    rng = random.Random(SEED + 7)
    for _ in range(TRIALS):
        limit = rng.randint(1, 8)
        fewer = limit + rng.randint(1, 20)
        more = fewer + rng.randint(1, 20)
        first = rule_params(fewer, limit, 1).severity
        second = rule_params(more, limit, 1).severity
        assert RANK_ORDER.index(second) <= RANK_ORDER.index(first)


def test_the_three_rules_never_disagree_on_severity():
    """`rule_params`, `rule_nesting` and `rule_complexity` share one banding.
    Swept over the whole domain rather than the handful of examples in the
    partition tests, because the claim is universal: if any of the three ever
    re-implements the bands, this is what catches it."""
    from core.rules import rule_complexity, rule_nesting
    rng = random.Random(SEED + 8)
    for _ in range(TRIALS):
        limit = rng.randint(1, 12)
        actual = rng.randint(0, 60)
        params = rule_params(actual, limit, 1)
        nesting = rule_nesting(actual, limit, 1)
        complexity = rule_complexity(actual, limit, 1)
        assert (params is None) == (nesting is None) == (complexity is None)
        if params is not None:
            assert params.severity == nesting.severity == complexity.severity


def test_no_rule_ever_emits_info():
    """The finding from US19, now checked on the third rule built to that
    shape. `count > limit and count <= limit` is unsatisfiable."""
    rng = random.Random(SEED + 9)
    for _ in range(TRIALS):
        limit = rng.randint(1, 12)
        issue = rule_params(rng.randint(0, 60), limit, 1)
        if issue is not None:
            assert issue.severity != INFO


def test_invalid_input_always_raises():
    rng = random.Random(SEED + 10)
    for _ in range(TRIALS):
        with pytest.raises(ValueError):
            rule_params(rng.randint(0, 30), rng.randint(-20, 0), rng.randint(1, 500))
        with pytest.raises(ValueError):
            rule_params(rng.randint(-30, -1), rng.randint(1, 10), rng.randint(1, 500))
