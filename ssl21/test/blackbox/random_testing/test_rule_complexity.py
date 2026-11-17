"""Black-box tests for rule_complexity - US19, Saaket (ssl21).

Technique: random testing against invariants.
Function under test: core.rules.rule_complexity(cc, limit, line).

No expected Issue is constructed by hand. Each test states a property the rule
must satisfy for every input pair and samples the domain randomly. The seed is
fixed so a failure replays exactly.
"""

import random

import pytest

from core.rules import rule_complexity
from core.severity import CRITICAL, INFO, MAJOR, MINOR, RANK_ORDER, classify_severity

SEED = 20261115
TRIALS = 200
BANDS = (INFO, MINOR, MAJOR, CRITICAL)


def test_within_the_limit_the_rule_is_always_silent():
    rng = random.Random(SEED)
    for _ in range(TRIALS):
        limit = rng.randint(1, 50)
        cc = rng.randint(1, limit)          # cc <= limit, so never a violation
        assert rule_complexity(cc, limit, rng.randint(1, 500)) is None


def test_above_the_limit_the_rule_always_speaks():
    rng = random.Random(SEED + 1)
    for _ in range(TRIALS):
        limit = rng.randint(1, 50)
        cc = limit + rng.randint(1, 100)
        assert rule_complexity(cc, limit, rng.randint(1, 500)) is not None


def test_every_issue_carries_the_same_rule_code():
    # one rule, one code - the code identifies the rule, not the severity
    rng = random.Random(SEED + 2)
    for _ in range(TRIALS):
        limit = rng.randint(1, 50)
        issue = rule_complexity(limit + rng.randint(1, 100), limit, rng.randint(1, 500))
        assert issue.code == "CC001"


def test_the_reported_line_is_always_the_line_passed_in():
    # the rule must not compute or alter the location
    rng = random.Random(SEED + 3)
    for _ in range(TRIALS):
        limit = rng.randint(1, 50)
        line = rng.randint(1, 10000)
        issue = rule_complexity(limit + rng.randint(1, 100), limit, line)
        assert issue.line == line


def test_every_severity_is_one_of_the_four_known_bands():
    rng = random.Random(SEED + 4)
    for _ in range(TRIALS):
        limit = rng.randint(1, 50)
        issue = rule_complexity(limit + rng.randint(1, 200), limit, rng.randint(1, 500))
        assert issue.severity in BANDS


def test_the_severity_always_matches_classify_severity():
    # the delegation to US26 must hold across the whole domain, not just at
    # the examples chosen in the partition tests
    rng = random.Random(SEED + 5)
    for _ in range(TRIALS):
        limit = rng.randint(1, 50)
        cc = limit + rng.randint(1, 200)
        issue = rule_complexity(cc, limit, rng.randint(1, 500))
        assert issue.severity == classify_severity(cc, limit)


def test_severity_never_improves_as_complexity_grows():
    # monotonicity: a worse function is never reported more kindly.
    # RANK_ORDER runs worst-first, so the index must never increase.
    rng = random.Random(SEED + 6)
    for _ in range(TRIALS):
        limit = rng.randint(1, 30)
        lower = limit + rng.randint(1, 50)
        higher = lower + rng.randint(1, 50)
        first = rule_complexity(lower, limit, 1).severity
        second = rule_complexity(higher, limit, 1).severity
        assert RANK_ORDER.index(second) <= RANK_ORDER.index(first)


def test_the_message_always_contains_both_numbers():
    rng = random.Random(SEED + 7)
    for _ in range(TRIALS):
        limit = rng.randint(1, 50)
        cc = limit + rng.randint(1, 100)
        message = rule_complexity(cc, limit, rng.randint(1, 500)).message
        assert str(cc) in message
        assert str(limit) in message


def test_an_invalid_limit_always_raises():
    rng = random.Random(SEED + 8)
    for _ in range(TRIALS):
        with pytest.raises(ValueError):
            rule_complexity(rng.randint(0, 50), rng.randint(-50, 0), rng.randint(1, 500))
