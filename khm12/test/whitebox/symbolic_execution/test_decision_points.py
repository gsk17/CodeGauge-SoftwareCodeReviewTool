"""Symbolic execution tests for decision_points - US10, Kasam (khm12).

Technique: symbolic execution. Each test discharges one leaf of the symbolic
execution tree in docs/symbolic/khm12-symbolic-execution.md. The symbolic
inputs are I, E, F, W, X, C; the guard loop produces one leaf per position at
which the first negative value appears, plus one leaf where none is negative.
"""

import pytest

from core.complexity import decision_points


def test_path_p0_all_non_negative():
    # PC: I>=0 and E>=0 and F>=0 and W>=0 and X>=0 and C>=0
    # returns I+E+F+W+X+C
    assert decision_points(3, 2, 1, 1, 1, 2) == 10


def test_path_p0_at_the_lower_boundary():
    # PC: same, with every symbol at its boundary value 0
    assert decision_points(0, 0, 0, 0, 0, 0) == 0


def test_path_p1_first_argument_negative():
    # PC: I < 0
    with pytest.raises(ValueError):
        decision_points(-1, 0, 0, 0, 0, 0)


def test_path_p3_third_argument_negative():
    # PC: I >= 0 and E >= 0 and F < 0
    with pytest.raises(ValueError):
        decision_points(0, 0, -5, 0, 0, 0)


def test_path_p6_last_argument_negative():
    # PC: I>=0 and E>=0 and F>=0 and W>=0 and X>=0 and C<0
    # the deepest feasible leaf of the guard chain
    with pytest.raises(ValueError):
        decision_points(1, 1, 1, 1, 1, -1)
