"""Black-box tests for rule_nesting - US20, Kasam (khm12).

Technique: random testing against invariants.
Function under test: core.rules.rule_nesting(depth, limit, line).

No expected Issue is built by hand. Each test states a property the rule must
satisfy for every input pair and samples the domain randomly. The seed is fixed
so a failure replays exactly.

Nesting limits in practice are small - a limit above about 6 would never be
configured - so the sampled range is deliberately narrow and dense rather than
wide and sparse. That is the opposite choice from US19's complexity rule, where
limits of 10 to 15 are normal, and it is made for the same reason: sample where
the function will actually be used.
"""

import random

import pytest

from core.rules import rule_nesting
from core.severity import CRITICAL, INFO, MAJOR, MINOR, RANK_ORDER, classify_severity

SEED = 20261118
TRIALS = 200
BANDS = (INFO, MINOR, MAJOR, CRITICAL)


def test_within_the_limit_the_rule_is_always_silent():
    rng = random.Random(SEED)
    for _ in range(TRIALS):
        limit = rng.randint(1, 8)
        depth = rng.randint(0, limit)        # depth <= limit, never a violation
        assert rule_nesting(depth, limit, rng.randint(1, 500)) is None


def test_above_the_limit_the_rule_always_speaks():
    rng = random.Random(SEED + 1)
    for _ in range(TRIALS):
        limit = rng.randint(1, 8)
        depth = limit + rng.randint(1, 20)
        assert rule_nesting(depth, limit, rng.randint(1, 500)) is not None


def test_every_issue_carries_the_nesting_code():
    rng = random.Random(SEED + 2)
    for _ in range(TRIALS):
        limit = rng.randint(1, 8)
        issue = rule_nesting(limit + rng.randint(1, 20), limit, rng.randint(1, 500))
        assert issue.code == "NEST001"


def test_the_reported_line_is_always_the_line_passed_in():
    rng = random.Random(SEED + 3)
    for _ in range(TRIALS):
        limit = rng.randint(1, 8)
        line = rng.randint(1, 10000)
        assert rule_nesting(limit + rng.randint(1, 20), limit, line).line == line


def test_the_message_always_names_both_numbers_in_order():
    rng = random.Random(SEED + 4)
    for _ in range(TRIALS):
        limit = rng.randint(1, 8)
        depth = limit + rng.randint(1, 20)
        message = rule_nesting(depth, limit, rng.randint(1, 500)).message
        assert message == "nesting depth %d exceeds limit %d" % (depth, limit)


def test_every_severity_is_one_of_the_four_known_bands():
    rng = random.Random(SEED + 5)
    for _ in range(TRIALS):
        limit = rng.randint(1, 8)
        issue = rule_nesting(limit + rng.randint(1, 30), limit, rng.randint(1, 500))
        assert issue.severity in BANDS


def test_the_severity_always_matches_classify_severity():
    # the delegation must hold across the whole domain, not just at the
    # examples chosen in the partition tests
    rng = random.Random(SEED + 6)
    for _ in range(TRIALS):
        limit = rng.randint(1, 8)
        depth = limit + rng.randint(1, 30)
        issue = rule_nesting(depth, limit, rng.randint(1, 500))
        assert issue.severity == classify_severity(depth, limit)


def test_severity_never_improves_as_nesting_deepens():
    # monotonicity: a worse-nested function is never reported more kindly
    rng = random.Random(SEED + 7)
    for _ in range(TRIALS):
        limit = rng.randint(1, 6)
        shallower = limit + rng.randint(1, 10)
        deeper = shallower + rng.randint(1, 10)
        first = rule_nesting(shallower, limit, 1).severity
        second = rule_nesting(deeper, limit, 1).severity
        assert RANK_ORDER.index(second) <= RANK_ORDER.index(first)


def test_raising_the_limit_never_makes_a_finding_worse():
    # a more permissive configuration cannot produce a more severe result,
    # and may silence the finding altogether
    rng = random.Random(SEED + 8)
    for _ in range(TRIALS):
        limit = rng.randint(1, 6)
        depth = limit + rng.randint(1, 15)
        strict = rule_nesting(depth, limit, 1)
        relaxed = rule_nesting(depth, limit + rng.randint(1, 5), 1)
        if relaxed is not None:
            assert RANK_ORDER.index(relaxed.severity) >= RANK_ORDER.index(strict.severity)


def test_invalid_input_always_raises():
    rng = random.Random(SEED + 9)
    for _ in range(TRIALS):
        with pytest.raises(ValueError):
            rule_nesting(rng.randint(0, 20), rng.randint(-20, 0), rng.randint(1, 500))
        with pytest.raises(ValueError):
            rule_nesting(rng.randint(-20, -1), rng.randint(1, 8), rng.randint(1, 500))
