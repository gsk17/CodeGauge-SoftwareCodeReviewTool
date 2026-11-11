"""White-box tests for weighted_penalty - US28, Harshita (hcg22).

Technique: branch coverage. The guard loop holds one decision, "weight < 0",
and the body holds four severity comparisons plus an implicit else. Branch
coverage requires the guard both taken and not taken, and each comparison true
once and false at least once.
"""

import pytest

from core.scoring import weighted_penalty


def test_guard_fires_on_a_negative_weight():
    # guard TRUE - the loop exits early by raising
    with pytest.raises(ValueError):
        weighted_penalty("MAJOR", 15, -1, 3, 1)


def test_guard_never_fires_and_first_comparison_is_true():
    # guard FALSE on all four; b_critical TRUE
    assert weighted_penalty("CRITICAL", 15, 8, 3, 1) == 15


def test_second_comparison_true():
    # b_critical FALSE, b_major TRUE
    assert weighted_penalty("MAJOR", 15, 8, 3, 1) == 8


def test_third_comparison_true():
    assert weighted_penalty("MINOR", 15, 8, 3, 1) == 3


def test_fourth_comparison_true():
    assert weighted_penalty("INFO", 15, 8, 3, 1) == 1


def test_all_comparisons_false_reaches_the_raise():
    # the implicit else - the only path that falls past every comparison
    with pytest.raises(ValueError):
        weighted_penalty("WARNING", 15, 8, 3, 1)
