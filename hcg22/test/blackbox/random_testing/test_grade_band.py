"""Black-box tests for grade_band - US30, Harshita (hcg22).

Technique: random testing against invariants.
Function under test: core.scoring.grade_band(score).

No expected grade is written by hand here. Each test states a property that must
hold across the whole 0-100 domain and samples it randomly. The seed is fixed so
a failure replays exactly.

Monotonicity is the interesting one: a banding function built from independent
if statements can pass every single-point test and still be non-monotonic if one
threshold is written the wrong way round. Sampling pairs of scores catches that
without anyone having to guess which threshold is wrong.
"""

import random

import pytest

from core.scoring import grade_band

SEED = 20261115
TRIALS = 300

# ordered best to worst, so a better score must never produce a higher index
GRADES = ("A", "B", "C", "D", "F")


def test_every_valid_score_returns_one_of_the_five_grades():
    rng = random.Random(SEED)
    for _ in range(TRIALS):
        assert grade_band(rng.randint(0, 100)) in GRADES


def test_the_grade_never_gets_worse_as_the_score_rises():
    # monotonicity across the whole domain
    rng = random.Random(SEED + 1)
    for _ in range(TRIALS):
        lower = rng.randint(0, 100)
        higher = rng.randint(lower, 100)
        assert GRADES.index(grade_band(higher)) <= GRADES.index(grade_band(lower))


def test_the_function_is_deterministic():
    # the same score must always give the same grade
    rng = random.Random(SEED + 2)
    for _ in range(TRIALS):
        score = rng.randint(0, 100)
        assert grade_band(score) == grade_band(score)


def test_every_score_of_eighty_five_or_more_is_an_a():
    rng = random.Random(SEED + 3)
    for _ in range(TRIALS):
        assert grade_band(rng.randint(85, 100)) == "A"


def test_every_score_below_fifty_is_an_f():
    rng = random.Random(SEED + 4)
    for _ in range(TRIALS):
        assert grade_band(rng.randint(0, 49)) == "F"


def test_a_passing_band_is_never_returned_for_a_failing_score():
    # the one judgement that matters to a user: did this code pass
    rng = random.Random(SEED + 5)
    for _ in range(TRIALS):
        assert grade_band(rng.randint(0, 49)) not in ("A", "B", "C", "D")
        assert grade_band(rng.randint(50, 100)) != "F"


def test_all_five_grades_are_reachable():
    # a random sweep of the domain must exercise every partition, which proves
    # no band has been made unreachable by a mis-ordered threshold
    rng = random.Random(SEED + 6)
    seen = set()
    for _ in range(2000):
        seen.add(grade_band(rng.randint(0, 100)))
    assert seen == set(GRADES)


def test_any_score_outside_the_domain_always_raises():
    rng = random.Random(SEED + 7)
    for _ in range(TRIALS):
        with pytest.raises(ValueError):
            grade_band(rng.randint(101, 10000))
        with pytest.raises(ValueError):
            grade_band(rng.randint(-10000, -1))
