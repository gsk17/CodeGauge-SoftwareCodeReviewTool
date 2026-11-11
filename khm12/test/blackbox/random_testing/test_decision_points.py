"""Random-based black-box tests for decision_points - US10, Kasam (khm12).

Technique: random testing. Counts are generated at random and checked against
invariants rather than against hand-written expected values. The seed is fixed
so that any failure can be replayed exactly.
"""

import random

import pytest

from core.complexity import decision_points

SEED = 20261111
RUNS = 500


def test_result_always_equals_the_sum_of_the_inputs():
    """Invariant: the function is addition, for any non-negative inputs."""
    rng = random.Random(SEED)
    for _ in range(RUNS):
        counts = [rng.randint(0, 50) for _ in range(6)]
        assert decision_points(*counts) == sum(counts), counts


def test_any_negative_count_always_raises():
    """Invariant: one negative anywhere among the six rejects the whole call,
    whichever position it occupies."""
    rng = random.Random(SEED + 1)
    for _ in range(RUNS):
        counts = [rng.randint(0, 50) for _ in range(6)]
        counts[rng.randrange(6)] = -rng.randint(1, 50)
        with pytest.raises(ValueError):
            decision_points(*counts)


def test_result_is_never_negative_and_never_below_any_input():
    """Invariant: a sum of non-negative terms dominates each of its terms."""
    rng = random.Random(SEED + 2)
    for _ in range(RUNS):
        counts = [rng.randint(0, 50) for _ in range(6)]
        total = decision_points(*counts)
        assert total >= 0
        assert total >= max(counts)


def test_order_of_the_counts_does_not_change_the_total():
    """Invariant: addition is commutative, so shuffling the six keyword counts
    must not change the result. This catches a parameter accidentally being
    dropped, doubled or read in the wrong position."""
    rng = random.Random(SEED + 3)
    for _ in range(RUNS):
        counts = [rng.randint(0, 50) for _ in range(6)]
        shuffled = counts[:]
        rng.shuffle(shuffled)
        assert decision_points(*counts) == decision_points(*shuffled)
