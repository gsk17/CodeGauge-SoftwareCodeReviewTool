"""Black-box tests for classify_severity - US26, Saaket (ssl21).

Technique: equivalence partitioning with boundary values. The specification
divides the input domain into four valid classes and two invalid ones:

    INVALID   actual < 0
    INVALID   limit < 1
    INFO      0 <= actual <= limit
    MINOR     limit < actual <= limit + limit//2
    MAJOR     limit + limit//2 < actual < 2*limit
    CRITICAL  actual >= 2*limit

With limit = 10 the boundaries fall at 10, 15, 19 and 20, so each is tested on
both sides.
"""

import pytest

from core.severity import classify_severity


def test_info_partition_within_the_limit():
    assert classify_severity(0, 10) == "INFO"
    assert classify_severity(10, 10) == "INFO"


def test_minor_partition_up_to_half_again_over():
    assert classify_severity(11, 10) == "MINOR"
    assert classify_severity(15, 10) == "MINOR"


def test_major_partition_below_twice_the_limit():
    assert classify_severity(16, 10) == "MAJOR"
    assert classify_severity(19, 10) == "MAJOR"


def test_critical_partition_at_or_beyond_twice_the_limit():
    assert classify_severity(20, 10) == "CRITICAL"
    assert classify_severity(100, 10) == "CRITICAL"


def test_invalid_partitions_are_rejected():
    with pytest.raises(ValueError):
        classify_severity(-1, 10)
    with pytest.raises(ValueError):
        classify_severity(5, 0)
