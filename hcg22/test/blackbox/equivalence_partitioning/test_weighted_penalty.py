"""Black-box tests for weighted_penalty - US28, Harshita (hcg22).

Technique: equivalence partitioning. The severity parameter has five classes -
the four valid severity names and everything else - and each weight has a valid
class, zero or above, and an invalid one, negative.
"""

import pytest

from core.scoring import weighted_penalty


def test_each_valid_severity_returns_its_own_weight():
    assert weighted_penalty("CRITICAL", 15, 8, 3, 1) == 15
    assert weighted_penalty("MAJOR", 15, 8, 3, 1) == 8
    assert weighted_penalty("MINOR", 15, 8, 3, 1) == 3
    assert weighted_penalty("INFO", 15, 8, 3, 1) == 1


def test_zero_weights_are_valid():
    assert weighted_penalty("CRITICAL", 0, 0, 0, 0) == 0


def test_an_unknown_severity_is_rejected():
    with pytest.raises(ValueError):
        weighted_penalty("WARNING", 15, 8, 3, 1)
    with pytest.raises(ValueError):
        weighted_penalty("critical", 15, 8, 3, 1)   # names are case sensitive


def test_a_negative_weight_is_rejected():
    with pytest.raises(ValueError):
        weighted_penalty("MAJOR", 15, -1, 3, 1)
