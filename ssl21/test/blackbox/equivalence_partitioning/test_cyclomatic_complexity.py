"""Black-box tests for cyclomatic_complexity - US11, Saaket (ssl21).

Technique: equivalence partitioning with boundary values. Each of the two
parameters has two valid classes - zero and positive - and one invalid class,
negative. The partitions are therefore "both counts valid" and "at least one
negative", with the boundary between them at zero.

The lower boundary is worth testing on its own: a function with no decisions at
all still has complexity 1, because there is always one path through it.
"""

import pytest

from core.complexity import cyclomatic_complexity


def test_a_straight_line_function_has_complexity_one():
    # Boundary: zero decisions, zero operators. There is still one path.
    assert cyclomatic_complexity(0, 0) == 1


def test_decision_points_each_add_one():
    assert cyclomatic_complexity(1, 0) == 2
    assert cyclomatic_complexity(10, 0) == 11


def test_boolean_operators_each_add_one():
    assert cyclomatic_complexity(0, 1) == 2
    assert cyclomatic_complexity(0, 4) == 5


def test_decisions_and_operators_contribute_equally():
    # 7 + 3 + 1 and 10 + 0 + 1 must both give 11 - neither source of branching
    # is weighted more heavily than the other.
    assert cyclomatic_complexity(7, 3) == 11
    assert cyclomatic_complexity(10, 0) == 11


def test_a_negative_count_is_rejected():
    with pytest.raises(ValueError):
        cyclomatic_complexity(-1, 0)
    with pytest.raises(ValueError):
        cyclomatic_complexity(0, -1)
