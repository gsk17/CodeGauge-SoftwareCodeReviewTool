"""Black-box tests for rule_length - US21, Saaket (ssl21).

Technique: random testing against invariants.
Function under test: core.rules.rule_length(loc, limit, line).

No expected severity is computed by hand - that would reimplement
`classify_severity` in the test. Each test states a property every rule of this
shape must satisfy, and samples the space randomly. The seed is fixed so a
failure replays exactly.

The strongest invariant available is **agreement with the other three rules**.
`rule_length`, `rule_params`, `rule_nesting` and `rule_complexity` are
structurally identical after renaming the measurement, so for any pair of
numbers all four must produce the same severity while carrying four different
codes. Sampling that over the whole plane is a sharper test than checking this
rule alone, because a rule tested in isolation is self-consistent whatever
bands it uses - the divergence only shows up in the comparison.

The second invariant is the **limit-relative scaling property**: multiplying
both the measurement and the limit by the same factor must not change the
severity.

That it holds at all is worth a sentence, because it looks as though it should
not. The CRITICAL boundary is `2 * limit`, which scales exactly. The MINOR
boundary is `limit + limit // 2`, and integer halving **truncates**, so the
scaled bound is not the scaled original bound:

    limit 3   MINOR ends at 3 + 1 = 4;  doubled, that is 8
    limit 6   MINOR ends at 6 + 3 = 9

The scaled band is one wider than the bound it was scaled from. The property
survives anyway because **no integer measurement ever falls in the gap**: for
odd `limit` the original bound is already `(3*limit - 1) / 2`, which is the
largest integer below `3*limit / 2`, so the slack the truncation opens up is
less than one. Checked exhaustively below rather than assumed.
"""

import random

import pytest

from core.rules import (
    rule_complexity,
    rule_length,
    rule_nesting,
    rule_params,
)
from core.severity import CRITICAL, INFO, MAJOR, MINOR, RANK_ORDER

SEED = 20261127
TRIALS = 400


def _inputs(rng, loc_high=400, limit_high=120):
    return rng.randint(0, loc_high), rng.randint(1, limit_high), rng.randint(1, 5000)


def test_within_the_limit_is_always_none():
    rng = random.Random(SEED)
    for _ in range(TRIALS):
        limit = rng.randint(1, 120)
        loc = rng.randint(0, limit)            # inclusive of the limit
        assert rule_length(loc, limit, rng.randint(1, 5000)) is None


def test_over_the_limit_always_produces_an_issue():
    rng = random.Random(SEED)
    for _ in range(TRIALS):
        limit = rng.randint(1, 120)
        loc = limit + rng.randint(1, 400)
        assert rule_length(loc, limit, 7) is not None


def test_the_severity_is_always_one_of_the_three_reachable_bands():
    rng = random.Random(SEED)
    for _ in range(TRIALS):
        limit = rng.randint(1, 120)
        loc = limit + rng.randint(1, 400)
        severity = rule_length(loc, limit, 7).severity
        assert severity in (MINOR, MAJOR, CRITICAL)
        assert severity != INFO
        assert severity in RANK_ORDER


def test_the_issue_always_carries_the_line_it_was_given():
    rng = random.Random(SEED)
    for _ in range(TRIALS):
        limit = rng.randint(1, 120)
        line = rng.randint(1, 100000)
        assert rule_length(limit + 1, limit, line).line == line


def test_the_message_always_contains_both_numbers():
    rng = random.Random(SEED)
    for _ in range(TRIALS):
        limit = rng.randint(1, 120)
        loc = limit + rng.randint(1, 400)
        message = rule_length(loc, limit, 7).message
        assert str(loc) in message
        assert str(limit) in message


def test_all_four_rules_always_agree_on_severity():
    # The sharpest property in this file. Four rules, one banding.
    rng = random.Random(SEED)
    for _ in range(TRIALS):
        limit = rng.randint(1, 120)
        measurement = limit + rng.randint(1, 400)
        severities = {
            rule_length(measurement, limit, 7).severity,
            rule_params(measurement, limit, 7).severity,
            rule_nesting(measurement, limit, 7).severity,
            rule_complexity(measurement, limit, 7).severity,
        }
        assert len(severities) == 1


def test_all_four_rules_always_carry_distinct_codes():
    rng = random.Random(SEED)
    for _ in range(TRIALS):
        limit = rng.randint(1, 120)
        measurement = limit + rng.randint(1, 400)
        codes = {
            rule_length(measurement, limit, 7).code,
            rule_params(measurement, limit, 7).code,
            rule_nesting(measurement, limit, 7).code,
            rule_complexity(measurement, limit, 7).code,
        }
        assert len(codes) == 4


def test_the_severity_never_improves_as_the_function_grows():
    rank = {CRITICAL: 0, MAJOR: 1, MINOR: 2}
    rng = random.Random(SEED)
    for _ in range(TRIALS):
        limit = rng.randint(1, 60)
        previous = 99
        for loc in range(limit + 1, limit * 3 + 2):
            current = rank[rule_length(loc, limit, 7).severity]
            assert current <= previous
            previous = current


def test_raising_the_limit_never_worsens_the_outcome():
    # With the measurement fixed, a more generous limit must give a kinder
    # result, and eventually None.
    rank = {CRITICAL: 0, MAJOR: 1, MINOR: 2, None: 3}
    rng = random.Random(SEED)
    for _ in range(TRIALS):
        loc = rng.randint(2, 200)
        previous = -1
        for limit in range(1, loc + 2):
            issue = rule_length(loc, limit, 7)
            current = rank[issue.severity if issue else None]
            assert current >= previous
            previous = current


def test_scaling_both_numbers_preserves_the_severity():
    # Holds for every factor, odd ones included, despite `limit // 2`
    # truncating - see the module docstring.
    rng = random.Random(SEED)
    for _ in range(TRIALS):
        limit = rng.randint(1, 40)
        loc = limit + rng.randint(1, 120)
        expected = rule_length(loc, limit, 7).severity
        for factor in (2, 3, 4, 5, 6, 7):
            scaled = rule_length(loc * factor, limit * factor, 7)
            assert scaled.severity == expected


def test_the_truncation_opens_a_gap_that_no_integer_can_occupy():
    # The MINOR bound does not scale: at limit 3 it is 4, and doubling the
    # limit to 6 puts it at 9 rather than 8. The band is genuinely one wider.
    # It changes no outcome because the measurement that would exploit it
    # would have to be fractional. Exhaustive over the plausible range.
    for limit in range(1, 30):
        for measurement in range(limit + 1, 4 * limit + 6):
            expected = rule_length(measurement, limit, 7).severity
            for factor in range(2, 9):
                scaled = rule_length(measurement * factor, limit * factor, 7)
                assert scaled.severity == expected


def test_negative_measurements_are_always_rejected():
    rng = random.Random(SEED)
    for _ in range(TRIALS):
        with pytest.raises(ValueError):
            rule_length(-rng.randint(1, 400), rng.randint(1, 120), 7)


def test_limits_below_one_are_always_rejected():
    rng = random.Random(SEED)
    for _ in range(TRIALS):
        with pytest.raises(ValueError):
            rule_length(rng.randint(0, 400), -rng.randint(0, 50), 7)
