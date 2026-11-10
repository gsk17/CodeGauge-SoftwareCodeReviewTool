"""Black-box tests for decision_points - US10, Kasam (khm12).

Technique: equivalence partitioning. Each of the six parameters has two valid
classes - zero and positive - and one invalid class, negative. The partitions
are therefore "all counts valid" and "at least one count negative", with the
boundary between them at zero.
"""

import pytest

from core.complexity import decision_points


def test_all_zero_gives_no_decision_points():
    assert decision_points(0, 0, 0, 0, 0, 0) == 0


def test_mixed_counts_are_summed():
    assert decision_points(3, 2, 1, 1, 1, 2) == 10


def test_a_single_keyword_counts_once():
    assert decision_points(1, 0, 0, 0, 0, 0) == 1
    assert decision_points(0, 0, 0, 0, 0, 1) == 1


def test_a_negative_count_is_rejected():
    with pytest.raises(ValueError):
        decision_points(-1, 0, 0, 0, 0, 0)
    with pytest.raises(ValueError):
        decision_points(0, 0, 0, 0, 0, -1)
