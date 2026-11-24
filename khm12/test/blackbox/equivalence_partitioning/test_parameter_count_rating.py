"""Black-box tests for parameter_count_rating - US14, Kasam (khm12).

Technique: equivalence partitioning with boundary value analysis.
Function under test: core.complexity.parameter_count_rating(param_count, limit).

Three bands over the parameter count, cut at the limit and at twice the limit:

    P1  count <= limit              "OK"
    P2  limit < count <= 2*limit    "MANY"
    P3  count > 2*limit             "EXCESSIVE"

    I1  count < 0                   ValueError
    I2  limit < 1                   ValueError

Like US30 `grade_band`, this is a banding function and **boundary value
analysis is the whole of the story** - there is no interesting interior. Every
defect lives at a threshold, so each cut point is tested from both sides:
`limit` and `limit + 1`, then `2*limit` and `2*limit + 1`.

**The bands are not evenly sized**, which is worth noticing. At a limit of 4,
"OK" covers 0-4 (five values), "MANY" covers 5-8 (four), and "EXCESSIVE" is
everything from 9 up (unbounded). A function with twelve parameters and one
with ninety are reported identically. That is intended - once a signature is
excessive the exact count stops mattering - but it means the rating cannot be
used to rank two bad signatures against each other.
"""

import pytest

from core.complexity import parameter_count_rating

LIMIT = 4


# --- P1: within the limit ------------------------------------------------------

def test_p1_no_parameters_is_ok():
    # boundary: the smallest valid count
    assert parameter_count_rating(0, LIMIT) == "OK"


def test_p1_exactly_at_the_limit_is_ok():
    # boundary: the limit is inclusive
    assert parameter_count_rating(4, LIMIT) == "OK"


def test_p1_one_below_the_limit_is_ok():
    assert parameter_count_rating(3, LIMIT) == "OK"


# --- P2: over the limit, up to twice it ---------------------------------------

def test_p2_one_above_the_limit_is_many():
    # boundary: the smallest count that is not OK
    assert parameter_count_rating(5, LIMIT) == "MANY"


def test_p2_exactly_twice_the_limit_is_still_many():
    # boundary: the top of the MANY band, inclusive
    assert parameter_count_rating(8, LIMIT) == "MANY"


def test_p2_the_interior_of_the_many_band():
    for count in (6, 7):
        assert parameter_count_rating(count, LIMIT) == "MANY"


# --- P3: above twice the limit -------------------------------------------------

def test_p3_one_above_twice_the_limit_is_excessive():
    # boundary: the smallest EXCESSIVE count
    assert parameter_count_rating(9, LIMIT) == "EXCESSIVE"


def test_p3_a_very_large_count_is_excessive():
    assert parameter_count_rating(90, LIMIT) == "EXCESSIVE"


def test_p3_the_band_does_not_distinguish_between_bad_signatures():
    # intended, and recorded: twelve parameters and ninety read the same
    assert parameter_count_rating(12, LIMIT) == parameter_count_rating(90, LIMIT)


# --- the bands at other limits -------------------------------------------------

def test_the_bands_follow_the_limit_rather_than_fixed_numbers():
    # at a limit of 1: OK is {0,1}, MANY is {2}, EXCESSIVE is 3 upwards
    assert parameter_count_rating(1, 1) == "OK"
    assert parameter_count_rating(2, 1) == "MANY"
    assert parameter_count_rating(3, 1) == "EXCESSIVE"
    # at a limit of 10: OK to 10, MANY to 20, EXCESSIVE from 21
    assert parameter_count_rating(10, 10) == "OK"
    assert parameter_count_rating(20, 10) == "MANY"
    assert parameter_count_rating(21, 10) == "EXCESSIVE"


def test_the_many_band_is_never_empty():
    """Unlike the severity bands in US20, which collapse at small limits, the
    MANY band here always contains at least `limit` values - so no limit makes
    a rating unreachable. Checked across every realistic limit."""
    for limit in range(1, 21):
        assert parameter_count_rating(limit, limit) == "OK"
        assert parameter_count_rating(limit + 1, limit) == "MANY"
        assert parameter_count_rating(2 * limit, limit) == "MANY"
        assert parameter_count_rating(2 * limit + 1, limit) == "EXCESSIVE"


# --- I1, I2: invalid input -----------------------------------------------------

def test_i1_a_negative_parameter_count_is_rejected():
    # boundary: the largest invalid count
    with pytest.raises(ValueError):
        parameter_count_rating(-1, LIMIT)


def test_i2_a_limit_of_zero_is_rejected():
    # boundary: the largest invalid limit
    with pytest.raises(ValueError):
        parameter_count_rating(4, 0)


def test_i2_a_negative_limit_is_rejected():
    with pytest.raises(ValueError):
        parameter_count_rating(4, -2)
