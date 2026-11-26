"""Black-box tests for parameter_count_rating - US14, Kasam (khm12).

Technique: random testing against invariants.
Function under test: core.complexity.parameter_count_rating(param_count, limit).

No expected rating is written by hand. Each test states a property the rating
must satisfy across the whole domain and samples it randomly, with a fixed seed
so any failure replays.

The two invariants that matter are **monotonicity in the count** - a signature
with more parameters is never rated better - and **monotonicity in the limit** -
a more permissive configuration never rates a signature worse. The second is the
one a banding function written with the comparisons the wrong way round would
break while still passing every single-point test.
"""

import random

import pytest

from core.complexity import parameter_count_rating

SEED = 20261124
TRIALS = 300

#: best to worst, so a worse rating has a higher index
RATINGS = ("OK", "MANY", "EXCESSIVE")


def test_every_result_is_one_of_the_three_ratings():
    rng = random.Random(SEED)
    for _ in range(TRIALS):
        result = parameter_count_rating(rng.randint(0, 60), rng.randint(1, 20))
        assert result in RATINGS


def test_the_rating_never_improves_as_parameters_are_added():
    # monotonic in the count, at a fixed limit
    rng = random.Random(SEED + 1)
    for _ in range(TRIALS):
        limit = rng.randint(1, 15)
        fewer = rng.randint(0, 40)
        more = fewer + rng.randint(1, 20)
        assert (RATINGS.index(parameter_count_rating(more, limit))
                >= RATINGS.index(parameter_count_rating(fewer, limit)))


def test_the_rating_never_worsens_as_the_limit_is_raised():
    # monotonic in the limit, at a fixed count - the invariant a mis-ordered
    # comparison would break while still passing every single-point test
    rng = random.Random(SEED + 2)
    for _ in range(TRIALS):
        count = rng.randint(0, 60)
        strict = rng.randint(1, 15)
        relaxed = strict + rng.randint(1, 15)
        assert (RATINGS.index(parameter_count_rating(count, relaxed))
                <= RATINGS.index(parameter_count_rating(count, strict)))


def test_any_count_within_the_limit_is_always_ok():
    rng = random.Random(SEED + 3)
    for _ in range(TRIALS):
        limit = rng.randint(1, 20)
        assert parameter_count_rating(rng.randint(0, limit), limit) == "OK"


def test_any_count_above_twice_the_limit_is_always_excessive():
    rng = random.Random(SEED + 4)
    for _ in range(TRIALS):
        limit = rng.randint(1, 20)
        count = 2 * limit + rng.randint(1, 50)
        assert parameter_count_rating(count, limit) == "EXCESSIVE"


def test_the_middle_band_is_exactly_the_counts_between_the_two_thresholds():
    rng = random.Random(SEED + 5)
    for _ in range(TRIALS):
        limit = rng.randint(1, 20)
        count = limit + rng.randint(1, limit)      # limit < count <= 2*limit
        assert parameter_count_rating(count, limit) == "MANY"


def test_all_three_ratings_are_reachable_at_every_limit():
    """Unlike the severity bands in US20, no limit makes a rating unreachable
    here - the MANY band always holds exactly `limit` values."""
    rng = random.Random(SEED + 6)
    for _ in range(TRIALS):
        limit = rng.randint(1, 25)
        seen = set(parameter_count_rating(count, limit)
                   for count in range(0, 3 * limit + 2))
        assert seen == set(RATINGS)


def test_scaling_the_count_and_the_limit_together_preserves_the_rating():
    """The bands are defined by ratios to the limit, not by absolute counts, so
    doubling both must give the same rating."""
    rng = random.Random(SEED + 7)
    for _ in range(TRIALS):
        limit = rng.randint(1, 12)
        count = rng.randint(0, 3 * limit)
        expected = parameter_count_rating(count, limit)
        for factor in (2, 3, 5):
            assert parameter_count_rating(count * factor, limit * factor) == expected


def test_the_function_is_deterministic():
    rng = random.Random(SEED + 8)
    for _ in range(TRIALS):
        count, limit = rng.randint(0, 60), rng.randint(1, 20)
        assert (parameter_count_rating(count, limit)
                == parameter_count_rating(count, limit))


def test_invalid_input_always_raises():
    rng = random.Random(SEED + 9)
    for _ in range(TRIALS):
        with pytest.raises(ValueError):
            parameter_count_rating(rng.randint(-60, -1), rng.randint(1, 20))
        with pytest.raises(ValueError):
            parameter_count_rating(rng.randint(0, 60), rng.randint(-20, 0))
