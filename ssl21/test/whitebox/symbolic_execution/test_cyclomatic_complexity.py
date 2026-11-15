"""Symbolic execution tests for cyclomatic_complexity - US11, Saaket (ssl21).

Technique: symbolic execution. D and B are symbolic integers standing for
decision_point_count and bool_operators. Each test discharges one leaf of the
tree in docs/symbolic/ssl21-symbolic-execution.md; every path condition is a
conjunction of linear integer constraints.
"""

import pytest

from core.complexity import cyclomatic_complexity


def test_path_p1_negative_decision_count():
    # PC: D < 0                     witness D=-1, B=0
    with pytest.raises(ValueError):
        cyclomatic_complexity(-1, 0)


def test_path_p2_negative_operator_count():
    # PC: D >= 0 and B < 0          witness D=5, B=-1
    # D is non-zero so the witness also proves the first guard was passed
    # rather than skipped.
    with pytest.raises(ValueError):
        cyclomatic_complexity(5, -1)


def test_path_p3_both_valid():
    # PC: D >= 0 and B >= 0         returns D + B + 1
    assert cyclomatic_complexity(7, 3) == 11


def test_path_p3_at_the_lower_boundary():
    # PC: D >= 0 and B >= 0, with both symbols at their boundary value 0.
    # The returned expression D + B + 1 evaluates to 1 - the constant term is
    # what makes a decision-free function complexity 1 rather than 0.
    assert cyclomatic_complexity(0, 0) == 1
