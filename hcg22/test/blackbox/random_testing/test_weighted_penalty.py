"""Random-based black-box tests for weighted_penalty - US28, Harshita (hcg22).

Technique: random testing. Severities and weights are generated at random and
checked against invariants rather than against hand-written expected values.
The seed is fixed so that any failure can be replayed exactly.
"""

import random
import string

import pytest

from core.scoring import weighted_penalty

SEED = 20261111
RUNS = 500

SEVERITIES = ("CRITICAL", "MAJOR", "MINOR", "INFO")


def random_weights(rng):
    """Four non-negative weights, in the order the function expects them."""
    return [rng.randint(0, 100) for _ in range(4)]


def test_each_severity_returns_the_weight_passed_for_it():
    """Invariant: the function selects, it does not compute. Whatever weight is
    supplied for a severity comes back unchanged, for any set of weights."""
    rng = random.Random(SEED)
    for _ in range(RUNS):
        weights = random_weights(rng)
        for index, severity in enumerate(SEVERITIES):
            assert weighted_penalty(severity, *weights) == weights[index]


def test_result_is_always_one_of_the_four_weights_supplied():
    """Invariant: nothing but a supplied weight is ever returned - no default,
    no computed value."""
    rng = random.Random(SEED + 1)
    for _ in range(RUNS):
        weights = random_weights(rng)
        severity = rng.choice(SEVERITIES)
        assert weighted_penalty(severity, *weights) in weights


def test_any_negative_weight_always_raises():
    """Invariant: a negative weight is rejected whichever position it occupies,
    and regardless of which severity is being asked for."""
    rng = random.Random(SEED + 2)
    for _ in range(RUNS):
        weights = random_weights(rng)
        weights[rng.randrange(4)] = -rng.randint(1, 100)
        with pytest.raises(ValueError):
            weighted_penalty(rng.choice(SEVERITIES), *weights)


def test_an_unknown_severity_always_raises():
    """Invariant: only the four names are accepted. Random strings are
    rejected - including case variants of the valid names, since the comparison
    is case-sensitive and a caller lower-casing a severity would otherwise land
    silently on the error path."""
    rng = random.Random(SEED + 3)
    for _ in range(RUNS):
        name = "".join(rng.choice(string.ascii_letters)
                       for _ in range(rng.randint(1, 12)))
        if name in SEVERITIES:
            continue
        with pytest.raises(ValueError):
            weighted_penalty(name, *random_weights(rng))
