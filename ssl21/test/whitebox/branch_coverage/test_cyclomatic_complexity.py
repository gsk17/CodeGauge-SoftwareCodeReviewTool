"""White-box tests for cyclomatic_complexity - US11, Saaket (ssl21).

Technique: branch coverage. Two decisions:

    b1  decision_point_count < 0
    b2  bool_operators < 0

Each returns immediately when true, so b2 is only reachable when b1 is false.
The three tests below take every branch outcome at least once.
"""

import pytest

from core.complexity import cyclomatic_complexity


def test_b1_true_rejects_a_negative_decision_count():
    # b1 TRUE - returns before b2 is evaluated
    with pytest.raises(ValueError):
        cyclomatic_complexity(-1, 0)


def test_b1_false_b2_true_rejects_a_negative_operator_count():
    # b1 FALSE, b2 TRUE - proves the first guard passes a valid value through
    with pytest.raises(ValueError):
        cyclomatic_complexity(5, -1)


def test_both_false_reaches_the_return():
    # b1 FALSE, b2 FALSE - the only path that computes a result
    assert cyclomatic_complexity(7, 3) == 11
