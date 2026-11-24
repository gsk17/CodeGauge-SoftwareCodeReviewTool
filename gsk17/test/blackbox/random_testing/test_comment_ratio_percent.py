"""Black-box tests for comment_ratio_percent - US04, Gunjan (gsk17).

Technique: random testing against invariants.
Function under test: core.line_metrics.comment_ratio_percent(comment_lines, code_lines).

No expected percentage is computed by hand - that would reimplement the function
in the test. Each test states a property the ratio must satisfy for every pair
of counts and samples the space randomly. The seed is fixed so a failure
replays exactly.

The strongest invariant here is **scale invariance**: multiplying both counts by
the same factor cannot change the percentage. It holds exactly despite the
integer division, because

    (k*c * 100) // (k*c + k*d)  =  floor( k*c*100 / (k*(c+d)) )  =  floor( c*100 / (c+d) )

The factor cancels inside the division before the floor is taken, so the two
results are equal rather than merely close. That makes it a sharp test: an
implementation that floored each count before dividing, or that divided before
multiplying by 100, would break it immediately.
"""

import random

import pytest

from core.line_metrics import comment_ratio_percent

SEED = 20261124
TRIALS = 300


def _counts(rng, high=200):
    return rng.randint(0, high), rng.randint(0, high)


def test_the_result_is_always_a_percentage():
    rng = random.Random(SEED)
    for _ in range(TRIALS):
        for high in (5, 50, 2000):
            assert 0 <= comment_ratio_percent(*_counts(rng, high)) <= 100


def test_an_empty_file_is_always_zero():
    # the only input where the denominator vanishes
    assert comment_ratio_percent(0, 0) == 0


def test_a_file_with_no_comments_is_always_zero():
    rng = random.Random(SEED + 1)
    for _ in range(TRIALS):
        assert comment_ratio_percent(0, rng.randint(0, 500)) == 0


def test_a_file_with_no_code_is_always_one_hundred():
    rng = random.Random(SEED + 2)
    for _ in range(TRIALS):
        assert comment_ratio_percent(rng.randint(1, 500), 0) == 100


def test_scaling_both_counts_never_changes_the_result():
    """The sharp one - see the module docstring. The factor cancels inside the
    division, so the results are equal and not merely close."""
    rng = random.Random(SEED + 3)
    for _ in range(TRIALS):
        comments, code = _counts(rng, 60)
        if comments == 0 and code == 0:
            continue
        expected = comment_ratio_percent(comments, code)
        for factor in (2, 3, 7, 10, 100):
            assert comment_ratio_percent(comments * factor, code * factor) == expected


def test_adding_comments_never_lowers_the_ratio():
    # monotonic increasing in the first argument
    rng = random.Random(SEED + 4)
    for _ in range(TRIALS):
        comments, code = _counts(rng, 100)
        before = comment_ratio_percent(comments, code)
        after = comment_ratio_percent(comments + rng.randint(1, 50), code)
        assert after >= before


def test_adding_code_never_raises_the_ratio():
    # monotonic decreasing in the second argument
    rng = random.Random(SEED + 5)
    for _ in range(TRIALS):
        comments, code = _counts(rng, 100)
        before = comment_ratio_percent(comments, code)
        after = comment_ratio_percent(comments, code + rng.randint(1, 50))
        assert after <= before


def test_the_ratio_is_never_rounded_up():
    """Flooring, checked without recomputing the function: the reported
    percentage of the total must never exceed the actual comment count."""
    rng = random.Random(SEED + 6)
    for _ in range(TRIALS):
        comments, code = _counts(rng, 300)
        total = comments + code
        if total == 0:
            continue
        reported = comment_ratio_percent(comments, code)
        assert reported * total <= comments * 100


def test_one_hundred_is_reserved_for_files_with_no_code():
    """A file containing even one line of code cannot report 100%, however
    many comments it has - otherwise the top of the scale would be ambiguous."""
    rng = random.Random(SEED + 7)
    for _ in range(TRIALS):
        assert comment_ratio_percent(rng.randint(1, 5000), rng.randint(1, 10)) < 100


def test_the_function_is_deterministic():
    rng = random.Random(SEED + 8)
    for _ in range(TRIALS):
        counts = _counts(rng)
        assert comment_ratio_percent(*counts) == comment_ratio_percent(*counts)


def test_a_negative_count_always_raises():
    rng = random.Random(SEED + 9)
    for _ in range(TRIALS):
        with pytest.raises(ValueError):
            comment_ratio_percent(rng.randint(-200, -1), rng.randint(0, 200))
        with pytest.raises(ValueError):
            comment_ratio_percent(rng.randint(0, 200), rng.randint(-200, -1))
