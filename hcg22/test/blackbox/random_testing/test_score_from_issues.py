"""Black-box tests for score_from_issues - US29, Harshita (hcg22).

Technique: random testing against invariants.
Function under test: core.scoring.score_from_issues(critical, major, minor, info).

No expected score is computed by hand here - that would just be reimplementing
the function in the test, which proves nothing. Each test states a property the
scoring must satisfy for every combination of counts and samples the space
randomly. The seed is fixed so a failure replays exactly.

The counts are sampled in two ranges deliberately. Most tests use 0..6, where
the raw score is usually inside the range and the cap and floor rarely fire;
the floor tests use much larger counts, because a property about the floor is
untestable in a region where the floor never applies.
"""

import random

import pytest

from core.scoring import score_from_issues

SEED = 20261118
TRIALS = 300


def _counts(rng, high=6):
    return (rng.randint(0, high), rng.randint(0, high),
            rng.randint(0, high), rng.randint(0, high))


def test_the_score_is_always_within_zero_and_one_hundred():
    # the cap and the floor together must keep the result in range for every
    # combination, including ones where the raw arithmetic goes far outside it
    rng = random.Random(SEED)
    for _ in range(TRIALS):
        for high in (3, 6, 20, 200):
            score = score_from_issues(*_counts(rng, high))
            assert 0 <= score <= 100


def test_a_clean_file_always_scores_one_hundred():
    # the only input with no penalty, asserted as a property rather than as a
    # single example
    assert score_from_issues(0, 0, 0, 0) == 100


def test_adding_an_issue_never_improves_the_score():
    """Monotonicity in every argument independently.

    This is the property most at risk from the cap: a cap written as an
    assignment rather than a minimum makes the score *rise* when the third
    critical issue is added to an already-bad file.
    """
    rng = random.Random(SEED + 1)
    positions = range(4)
    for _ in range(TRIALS):
        counts = list(_counts(rng, 8))
        before = score_from_issues(*counts)
        for position in positions:
            worse = list(counts)
            worse[position] = worse[position] + rng.randint(1, 5)
            assert score_from_issues(*worse) <= before, \
                "%r -> %r" % (counts, worse)


def test_three_or_more_criticals_never_score_above_forty():
    # the cap, stated as the property it exists to enforce
    rng = random.Random(SEED + 2)
    for _ in range(TRIALS):
        _, major, minor, info = _counts(rng)
        critical = rng.randint(3, 15)
        assert score_from_issues(critical, major, minor, info) <= 40


def test_fewer_than_three_criticals_is_not_capped_by_the_cap_rule():
    """With 0, 1 or 2 criticals and no other issues the score must be the raw
    arithmetic, which is above 40 in every such case (100, 85, 70). If the cap
    fired early, one of these would come back as 40."""
    for critical in (0, 1, 2):
        assert score_from_issues(critical, 0, 0, 0) > 40


def test_enough_issues_always_reaches_the_floor():
    # sampled where the floor actually applies - a floor property tested only
    # on small counts would never exercise the floor at all
    rng = random.Random(SEED + 3)
    for _ in range(TRIALS):
        counts = (rng.randint(10, 60), rng.randint(10, 60),
                  rng.randint(10, 60), rng.randint(10, 60))
        assert score_from_issues(*counts) == 0


def test_a_worse_file_never_scores_better_than_a_strictly_better_one():
    """If every count in file B is at least that of file A, B cannot score
    higher. Stronger than per-argument monotonicity: it holds when several
    counts rise at once, which is where cap-and-floor interactions live."""
    rng = random.Random(SEED + 4)
    for _ in range(TRIALS):
        better = _counts(rng, 10)
        worse = tuple(c + rng.randint(0, 6) for c in better)
        assert score_from_issues(*worse) <= score_from_issues(*better)


def test_severities_are_ordered_by_cost():
    """One issue of a worse severity must cost at least as much as one of a
    milder severity. Checked by comparing single-issue scores rather than by
    reading the weights, so the test does not depend on their values."""
    critical = score_from_issues(1, 0, 0, 0)
    major = score_from_issues(0, 1, 0, 0)
    minor = score_from_issues(0, 0, 1, 0)
    info = score_from_issues(0, 0, 0, 1)
    assert critical <= major <= minor <= info < 100


def test_the_arguments_are_not_interchangeable():
    """The four severities carry different weights, so swapping counts between
    positions must generally change the answer. A function that summed the
    counts without weighting them would pass every other test in this file."""
    rng = random.Random(SEED + 5)
    differences = 0
    for _ in range(TRIALS):
        a, b = rng.randint(0, 5), rng.randint(0, 5)
        if a == b:
            continue
        if score_from_issues(a, b, 0, 0) != score_from_issues(b, a, 0, 0):
            differences = differences + 1
    assert differences > 0


def test_the_function_is_deterministic():
    rng = random.Random(SEED + 6)
    for _ in range(TRIALS):
        counts = _counts(rng, 12)
        assert score_from_issues(*counts) == score_from_issues(*counts)


def test_any_negative_count_always_raises():
    rng = random.Random(SEED + 7)
    for _ in range(TRIALS):
        counts = list(_counts(rng))
        counts[rng.randint(0, 3)] = rng.randint(-50, -1)
        with pytest.raises(ValueError):
            score_from_issues(*counts)
