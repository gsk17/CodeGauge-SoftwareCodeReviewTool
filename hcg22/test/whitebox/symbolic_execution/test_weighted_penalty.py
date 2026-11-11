"""Symbolic execution tests for weighted_penalty - US28, Harshita (hcg22).

Technique: symbolic execution. S is a symbolic string and Wc, Wm, Wn, Wi are
symbolic integers. Each test discharges one leaf of the tree in
docs/symbolic/hcg22-symbolic-execution.md.
"""

import pytest

from core.scoring import weighted_penalty


def test_path_p1_first_weight_negative():
    # PC: Wc < 0
    with pytest.raises(ValueError):
        weighted_penalty("CRITICAL", -1, 8, 3, 1)


def test_path_p4_last_weight_negative():
    # PC: Wc>=0 and Wm>=0 and Wn>=0 and Wi<0
    # proves the guard loop continues past three valid weights
    with pytest.raises(ValueError):
        weighted_penalty("INFO", 15, 8, 3, -1)


def test_path_p5_severity_is_critical():
    # PC: all weights >= 0 and S = "CRITICAL"   returns Wc
    assert weighted_penalty("CRITICAL", 15, 8, 3, 1) == 15


def test_path_p6_severity_is_major():
    # PC: all weights >= 0 and S != "CRITICAL" and S = "MAJOR"   returns Wm
    assert weighted_penalty("MAJOR", 15, 8, 3, 1) == 8


def test_path_p8_severity_is_info():
    # PC: all >= 0 and S not in {CRITICAL, MAJOR, MINOR} and S = "INFO"
    # the deepest comparison leaf
    assert weighted_penalty("INFO", 15, 8, 3, 1) == 1


def test_path_p9_severity_matches_nothing():
    # PC: all weights >= 0 and S not in {CRITICAL, MAJOR, MINOR, INFO}
    with pytest.raises(ValueError):
        weighted_penalty("WARNING", 15, 8, 3, 1)
