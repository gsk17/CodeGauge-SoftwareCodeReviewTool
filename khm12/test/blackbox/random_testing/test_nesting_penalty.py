"""Black-box tests for nesting_penalty - US13, Kasam (khm12).

Technique: random testing against invariants.
Function under test: core.complexity.nesting_penalty(depth, limit).

No expected penalty is computed by hand - that would reimplement the function
in the test. Each test states a property the penalty must satisfy for every
pair of depth and limit, and samples the space randomly. The seed is fixed so a
failure replays exactly.

Three invariants carry most of the weight here:

**The penalty depends only on the overshoot.** `nesting_penalty(d, l)` must
equal `nesting_penalty(d + k, l + k)` for every k, because both describe the
same number of levels past the limit. That is a strong property: it says the
function may not look at the absolute depth at all, only at the difference. An
implementation that charged by depth and merely gated on the limit would break
it at once.

**The penalty is a multiple of five, and never more than twenty-five.** Two
cheap bounds that between them pin the shape of the result without
reimplementing the arithmetic.

**Monotone in both arguments, in opposite directions.** Nesting deeper never
costs less; raising the limit never costs more. Properties of the family of
inputs rather than of any single one, which is what random sampling is for.
"""

import random

import pytest

from core.complexity import nesting_penalty

SEED = 20261127
TRIALS = 400

MAX = 25
STEP = 5


def _inputs(rng, depth_high=40, limit_high=12):
    return rng.randint(0, depth_high), rng.randint(1, limit_high)


def test_the_penalty_is_never_negative():
    rng = random.Random(SEED)
    for _ in range(TRIALS):
        assert nesting_penalty(*_inputs(rng)) >= 0


def test_the_penalty_never_exceeds_the_cap():
    rng = random.Random(SEED)
    for _ in range(TRIALS):
        assert nesting_penalty(*_inputs(rng, 500, 12)) <= MAX


def test_the_penalty_is_always_a_multiple_of_five():
    rng = random.Random(SEED)
    for _ in range(TRIALS):
        assert nesting_penalty(*_inputs(rng, 500, 12)) % STEP == 0


def test_within_the_limit_is_always_free():
    rng = random.Random(SEED)
    for _ in range(TRIALS):
        limit = rng.randint(1, 12)
        depth = rng.randint(0, limit)          # inclusive of the limit itself
        assert nesting_penalty(depth, limit) == 0


def test_over_the_limit_always_costs_something():
    rng = random.Random(SEED)
    for _ in range(TRIALS):
        limit = rng.randint(1, 12)
        depth = limit + rng.randint(1, 20)
        assert nesting_penalty(depth, limit) > 0


def test_only_the_overshoot_matters():
    # shifting depth and limit together by the same amount describes the same
    # number of levels past the limit, so the penalty must not move
    rng = random.Random(SEED)
    for _ in range(TRIALS):
        depth, limit = _inputs(rng, 30, 8)
        expected = nesting_penalty(depth, limit)
        for shift in (1, 3, 7, 20):
            assert nesting_penalty(depth + shift, limit + shift) == expected


def test_the_penalty_never_falls_as_the_depth_grows():
    rng = random.Random(SEED)
    for _ in range(TRIALS):
        limit = rng.randint(1, 10)
        start = rng.randint(0, 20)
        previous = nesting_penalty(start, limit)
        for depth in range(start + 1, start + 12):
            current = nesting_penalty(depth, limit)
            assert current >= previous
            previous = current


def test_the_penalty_never_rises_as_the_limit_grows():
    rng = random.Random(SEED)
    for _ in range(TRIALS):
        depth = rng.randint(0, 40)
        previous = nesting_penalty(depth, 1)
        for limit in range(2, 14):
            current = nesting_penalty(depth, limit)
            assert current <= previous
            previous = current


def test_each_charged_level_adds_exactly_five_until_the_cap():
    # the step is constant where the cap is not binding, which distinguishes a
    # linear charge from an escalating one
    rng = random.Random(SEED)
    for _ in range(TRIALS):
        limit = rng.randint(1, 10)
        for over in range(1, 5):
            below = nesting_penalty(limit + over, limit)
            above = nesting_penalty(limit + over + 1, limit)
            assert above - below == STEP


def test_the_cap_once_reached_is_never_left():
    # beyond the point where the cap binds, every deeper input returns the cap
    rng = random.Random(SEED)
    for _ in range(TRIALS):
        limit = rng.randint(1, 10)
        for depth in range(limit + 6, limit + 30):
            assert nesting_penalty(depth, limit) == MAX


def test_negative_depths_are_always_rejected():
    rng = random.Random(SEED)
    for _ in range(TRIALS):
        with pytest.raises(ValueError):
            nesting_penalty(-rng.randint(1, 50), rng.randint(1, 12))


def test_limits_below_one_are_always_rejected():
    rng = random.Random(SEED)
    for _ in range(TRIALS):
        with pytest.raises(ValueError):
            nesting_penalty(rng.randint(0, 40), -rng.randint(0, 20))
