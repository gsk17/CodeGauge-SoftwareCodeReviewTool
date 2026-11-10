"""Concolic testing for classify_severity - US26, Saaket (ssl21).

Technique: concolic (dynamic symbolic) execution. Six iterations from one
arbitrary seed reach all six paths.

Full derivation: docs/symbolic/ssl21-symbolic-execution.md, section 5.
"""

import pytest

from core.severity import classify_severity


def test_iteration_1_seed():
    # seed (5, 10) - arbitrary. Path P3 -> INFO
    # PC: A>=0 and L>=1 and A<=L ; negate A<=L -> need A > L
    assert classify_severity(5, 10) == "INFO"


def test_iteration_2_negate_the_within_limit_clause():
    # solved (11, 10). Path P4 -> MINOR
    # negate A <= L + floor(L/2) -> need A > 15
    assert classify_severity(11, 10) == "MINOR"


def test_iteration_3_negate_the_minor_clause():
    # solved (16, 10). Path P5 -> MAJOR ; negate A < 2L -> need A >= 20
    assert classify_severity(16, 10) == "MAJOR"


def test_iteration_4_negate_the_major_clause():
    # solved (20, 10). Path P6 -> CRITICAL
    # frontier at b3..b5 exhausted; backtrack to b2 and negate L >= 1
    assert classify_severity(20, 10) == "CRITICAL"


def test_iteration_5_negate_the_limit_guard():
    # solved (5, 0). Path P2 ; backtrack to b1 and negate A >= 0
    with pytest.raises(ValueError):
        classify_severity(5, 0)


def test_iteration_6_negate_the_actual_guard():
    # solved (-1, 10). Path P1. Frontier empty - no loops, finite tree.
    with pytest.raises(ValueError):
        classify_severity(-1, 10)
