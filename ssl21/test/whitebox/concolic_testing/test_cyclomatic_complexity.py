"""Concolic testing for cyclomatic_complexity - US11, Saaket (ssl21).

Technique: concolic (dynamic symbolic) execution. From one arbitrary seed each
iteration runs the function concretely, collects the path condition taken, then
negates the last unexplored branch and solves for the next input.

Full derivation: docs/symbolic/ssl21-symbolic-execution.md, section 5.
"""

import pytest

from core.complexity import cyclomatic_complexity


def test_iteration_1_seed_takes_the_valid_path():
    # seed (4, 2) - arbitrary. Path P3, returns 7
    # PC: D >= 0 and B >= 0 ; negate B >= 0 -> next input needs B < 0
    assert cyclomatic_complexity(4, 2) == 7


def test_iteration_2_negate_the_operator_guard():
    # solved (4, -1). Path P2
    # frontier at b2 exhausted; backtrack to b1 and negate D >= 0
    with pytest.raises(ValueError):
        cyclomatic_complexity(4, -1)


def test_iteration_3_negate_the_decision_guard():
    # solved (-1, 0). Path P1. Frontier empty - the function has no loops, so
    # the execution tree is finite and of depth two.
    with pytest.raises(ValueError):
        cyclomatic_complexity(-1, 0)
