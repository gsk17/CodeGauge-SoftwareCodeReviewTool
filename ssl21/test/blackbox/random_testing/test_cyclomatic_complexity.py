"""Random-based black-box tests for cyclomatic_complexity - US11, Saaket (ssl21).

Technique: random testing. Inputs are generated at random and checked against
invariants rather than against hand-written expected values. The seed is fixed
so that any failure can be replayed exactly.
"""

import random

import pytest

from core.complexity import cyclomatic_complexity

SEED = 20261112
RUNS = 500


def test_result_is_always_decisions_plus_operators_plus_one():
    """Invariant: the formula holds for every non-negative pair."""
    rng = random.Random(SEED)
    for _ in range(RUNS):
        decisions = rng.randint(0, 200)
        operators = rng.randint(0, 200)
        assert cyclomatic_complexity(decisions, operators) == decisions + operators + 1


def test_complexity_is_never_below_one():
    """Invariant: every function has at least one path through it, so the
    measure can never return zero or a negative number."""
    rng = random.Random(SEED + 1)
    for _ in range(RUNS):
        assert cyclomatic_complexity(rng.randint(0, 200), rng.randint(0, 200)) >= 1


def test_the_two_sources_of_branching_are_interchangeable():
    """Invariant: a decision point and a boolean operator each add exactly one
    independent path, so swapping the two arguments cannot change the result.

    This is the property that makes the measure well defined - if `and` were
    weighted differently from `if`, the number would depend on how a condition
    happened to be written rather than on how many paths exist.
    """
    rng = random.Random(SEED + 2)
    for _ in range(RUNS):
        a = rng.randint(0, 200)
        b = rng.randint(0, 200)
        assert cyclomatic_complexity(a, b) == cyclomatic_complexity(b, a)


def test_adding_a_branch_always_raises_the_complexity_by_exactly_one():
    """Invariant: MONOTONICITY, with a known step. Adding one decision point
    raises the measure by exactly one, never more and never less."""
    rng = random.Random(SEED + 3)
    for _ in range(RUNS):
        decisions = rng.randint(0, 200)
        operators = rng.randint(0, 200)
        before = cyclomatic_complexity(decisions, operators)
        after = cyclomatic_complexity(decisions + 1, operators)
        assert after == before + 1


def test_any_negative_argument_always_raises():
    """Invariant: a negative count is rejected in either position."""
    rng = random.Random(SEED + 4)
    for _ in range(RUNS):
        with pytest.raises(ValueError):
            cyclomatic_complexity(-rng.randint(1, 100), rng.randint(0, 100))
        with pytest.raises(ValueError):
            cyclomatic_complexity(rng.randint(0, 100), -rng.randint(1, 100))
