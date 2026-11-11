"""Random-based black-box tests for classify_severity - US26, Saaket (ssl21).

Technique: random testing. Pairs of (actual, limit) are generated at random and
checked against invariants. The monotonicity property below is the valuable one:
no single example test can establish it, because it is a statement about the
relationship between two results rather than about either one of them.

The seed is fixed so that any failure can be replayed exactly.
"""

import random

import pytest

from core.severity import classify_severity

SEED = 20261111
RUNS = 500

BANDS = ("INFO", "MINOR", "MAJOR", "CRITICAL")
RANK = {name: index for index, name in enumerate(BANDS)}


def test_result_is_always_one_of_the_four_bands():
    """Invariant: the function is total over its valid domain."""
    rng = random.Random(SEED)
    for _ in range(RUNS):
        actual = rng.randint(0, 500)
        limit = rng.randint(1, 100)
        assert classify_severity(actual, limit) in BANDS


def test_severity_never_decreases_as_the_measurement_grows():
    """Invariant: MONOTONICITY. For a fixed limit, raising the measurement can
    only move the severity to the same band or a worse one, never back.

    This is the property the whole severity scale rests on, and it cannot be
    demonstrated by any single example - it is a claim about every pair of
    inputs at once.
    """
    rng = random.Random(SEED + 1)
    for _ in range(RUNS):
        limit = rng.randint(1, 100)
        lower = rng.randint(0, 400)
        higher = lower + rng.randint(1, 100)
        assert (RANK[classify_severity(higher, limit)]
                >= RANK[classify_severity(lower, limit)]), (lower, higher, limit)


def test_within_the_limit_is_always_info():
    """Invariant: nothing at or below its limit is ever reported as a fault."""
    rng = random.Random(SEED + 2)
    for _ in range(RUNS):
        limit = rng.randint(1, 100)
        assert classify_severity(rng.randint(0, limit), limit) == "INFO"


def test_double_the_limit_or_more_is_always_critical():
    """Invariant: the CRITICAL band is exactly actual >= 2 * limit."""
    rng = random.Random(SEED + 3)
    for _ in range(RUNS):
        limit = rng.randint(1, 100)
        assert classify_severity(2 * limit + rng.randint(0, 200), limit) == "CRITICAL"


def test_invalid_inputs_always_raise():
    """Invariant: a negative measurement, or a limit below one, is rejected."""
    rng = random.Random(SEED + 4)
    for _ in range(RUNS):
        with pytest.raises(ValueError):
            classify_severity(-rng.randint(1, 100), rng.randint(1, 100))
        with pytest.raises(ValueError):
            classify_severity(rng.randint(0, 100), -rng.randint(0, 100))
