"""Concolic testing for decision_points - US10, Kasam (khm12).

Technique: concolic (dynamic symbolic) execution. From one arbitrary seed each
iteration runs the function concretely, collects the path condition taken, then
negates the last unexplored branch and solves for the next input.

Full derivation: docs/symbolic/khm12-symbolic-execution.md, section 5.
"""

import pytest

from core.complexity import decision_points


def test_iteration_1_seed_takes_the_all_valid_path():
    # seed: (1,1,1,1,1,1) - arbitrary
    # path: P0, PC: all six symbols >= 0
    # negate the LAST conjunct, C >= 0  ->  next input needs C < 0
    assert decision_points(1, 1, 1, 1, 1, 1) == 6


def test_iteration_2_negate_the_last_guard():
    # solved: (1,1,1,1,1,-1), path P6
    # frontier at position 6 exhausted; backtrack and negate X >= 0
    with pytest.raises(ValueError):
        decision_points(1, 1, 1, 1, 1, -1)


def test_iteration_3_negate_the_fifth_guard():
    # solved: (1,1,1,1,-1,0), path P5
    with pytest.raises(ValueError):
        decision_points(1, 1, 1, 1, -1, 0)


def test_iteration_7_negate_the_first_guard():
    # continuing to backtrack reaches position 1 and exhausts the frontier.
    # Seven iterations cover all seven paths; the loop is bounded at six, so
    # the execution tree is finite.
    with pytest.raises(ValueError):
        decision_points(-1, 0, 0, 0, 0, 0)
