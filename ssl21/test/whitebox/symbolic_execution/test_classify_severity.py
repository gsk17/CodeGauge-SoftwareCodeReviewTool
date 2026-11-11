"""Symbolic execution tests for classify_severity - US26, Saaket (ssl21).

Technique: symbolic execution. A and L are symbolic integers standing for
actual and limit. Each test discharges one leaf of the tree in
docs/symbolic/ssl21-symbolic-execution.md; every path condition is a
conjunction of linear integer constraints, solved by hand.
"""

import pytest

from core.severity import classify_severity


def test_path_p1_negative_actual():
    # PC: A < 0                                   witness A=-1, L=10
    with pytest.raises(ValueError):
        classify_severity(-1, 10)


def test_path_p2_limit_below_one():
    # PC: A >= 0 and L < 1                        witness A=5, L=0
    with pytest.raises(ValueError):
        classify_severity(5, 0)


def test_path_p3_info():
    # PC: A >= 0 and L >= 1 and A <= L            witness A=10, L=10
    assert classify_severity(10, 10) == "INFO"


def test_path_p4_minor():
    # PC: ... and A > L and A <= L + floor(L/2)   witness A=11, L=10
    assert classify_severity(11, 10) == "MINOR"


def test_path_p5_major():
    # PC: ... and A > L + floor(L/2) and A < 2L   witness A=16, L=10
    # Feasible set with L=10 is A in 16..19. NOTE: this path is INFEASIBLE
    # when L = 1, since A > 1 and A < 2 has no integer solution - which is why
    # the witness fixes L = 10. See the write-up, section 4.
    assert classify_severity(16, 10) == "MAJOR"


def test_path_p6_critical():
    # PC: ... and A >= 2L                         witness A=20, L=10
    assert classify_severity(20, 10) == "CRITICAL"
