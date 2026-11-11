"""White-box tests for classify_severity - US26, Saaket (ssl21).

Technique: branch coverage. Five decisions:

    b1  actual < 0
    b2  limit < 1
    b3  actual <= limit
    b4  actual <= limit + limit//2
    b5  actual < 2*limit

Each returns immediately when true, so the five tests below take each decision
true once and the preceding ones false, covering every branch outcome.
"""

import pytest

from core.severity import classify_severity


def test_b1_true_rejects_negative_actual():
    with pytest.raises(ValueError):
        classify_severity(-1, 10)


def test_b2_true_rejects_a_limit_below_one():
    # b1 FALSE, b2 TRUE
    with pytest.raises(ValueError):
        classify_severity(5, 0)


def test_b3_true_returns_info():
    # b1,b2 FALSE; b3 TRUE
    assert classify_severity(10, 10) == "INFO"


def test_b4_true_returns_minor():
    # b1,b2,b3 FALSE; b4 TRUE
    assert classify_severity(11, 10) == "MINOR"


def test_b5_true_returns_major():
    # b1,b2,b3,b4 FALSE; b5 TRUE
    assert classify_severity(16, 10) == "MAJOR"


def test_all_decisions_false_returns_critical():
    # every decision FALSE - the implicit else
    assert classify_severity(20, 10) == "CRITICAL"
