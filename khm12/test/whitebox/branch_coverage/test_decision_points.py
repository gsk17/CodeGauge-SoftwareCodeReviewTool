"""White-box tests for decision_points - US10, Kasam (khm12).

Technique: branch coverage. The guard loop runs once per parameter and holds a
single decision, "value < 0". Branch coverage needs that decision both taken
and not taken, and the loop itself both entered and completed.
"""

import pytest

from core.complexity import decision_points


def test_guard_never_fires_loop_completes():
    # b1 FALSE on all six iterations - the loop runs to completion and the
    # function reaches its return statement.
    assert decision_points(1, 1, 1, 1, 1, 1) == 6


def test_guard_fires_on_the_first_iteration():
    # b1 TRUE on iteration 1 - the loop exits early by raising.
    with pytest.raises(ValueError):
        decision_points(-1, 0, 0, 0, 0, 0)


def test_guard_fires_on_the_last_iteration():
    # b1 FALSE five times, then TRUE - proves the loop continues past a valid
    # value rather than stopping at the first one it checks.
    with pytest.raises(ValueError):
        decision_points(0, 0, 0, 0, 0, -1)
