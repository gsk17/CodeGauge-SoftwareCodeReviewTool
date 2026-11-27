"""Tests for the Thresholds.validate fix and reachable_severities - Saaket (ssl21).

**Not a user story.** This is the defect fix agreed at the Sprint 1
retrospective on 24 November 2026 and amended at the stand-up on 27 November.
It earns no story points and must not count toward velocity.

Functions under test:
  * `model.thresholds.Thresholds.validate(name, value)`
  * `core.severity.reachable_severities(limit)`

### The defect

`classify_severity` bands a measurement with `limit + limit // 2` and
`2 * limit`. Integer halving truncates, so at small limits the bands collapse:

    limit 1   MINOR { }        MAJOR { }        CRITICAL {2, ...}
    limit 2   MINOR {3}        MAJOR { }        CRITICAL {4, ...}
    limit 3   MINOR {4}        MAJOR {5}        CRITICAL {6, ...}

`validate` previously accepted any integer of 1 or more, so a project could
configure a limit of 1 and get a report in which **every** finding was
CRITICAL. The severity scale would convey nothing, and nothing in the tool
would say so.

Found by symbolic execution in US19 and US26, confirmed for the rule shape in
US22, and fixed here.

### What was decided, and what was not

**Agreed at the retrospective: reject a severity limit below 2.** Nothing is
lost by forbidding a configuration no user wants.

**Not agreed: raising the floor to 3.** US22's analysis showed 3 is the
smallest limit at which all three reachable bands are non-empty, so a limit of 2
still produces an empty MAJOR band. The stand-up on 27 November decided against
raising it, on the ground that a limit of 2 is a legitimate strict setting - a
project insisting on at most two levels of nesting is not misconfigured - and
refusing it to keep a band non-empty would trade a real capability for a
cosmetic one. `reachable_severities` reports the limitation instead of
forbidding it.

### The partition the fix nearly got wrong

The floor applies only to the names passed to `classify_severity` as a limit.
`comment_ratio_min` is **not** one of them: it is a minimum percentage compared
directly, never banded. A single floor across every name would have refused
`comment_ratio_min = 1`, which is a project asking for at least 1% comments and
is a sensible request. R6 and R7 below are that partition.

    R1  a severity limit of 1                -> False, the defect
    R2  a severity limit of 2                -> True, permitted with a caveat
    R3  a severity limit of 3 or more        -> True
    R4  any threshold of 0 or less           -> False
    R5  an unknown name                      -> False
    R6  comment_ratio_min of 1               -> True, the floor does not apply
    R7  comment_ratio_min of 0               -> False, the general floor does
    R8  a bool, or a non-integer             -> False
"""

import pytest

from core.severity import (
    CRITICAL,
    INFO,
    MAJOR,
    MIN_SOUND_LIMIT,
    MINOR,
    RANK_ORDER,
    reachable_severities,
)
from model.thresholds import Thresholds

SEVERITY_LIMITS = Thresholds.SEVERITY_LIMITS


def test_r1_a_severity_limit_of_one_is_now_rejected():
    # the defect. Every one of these would previously have returned True.
    for name in SEVERITY_LIMITS:
        assert Thresholds.validate(name, 1) is False


def test_r2_a_severity_limit_of_two_is_permitted():
    for name in SEVERITY_LIMITS:
        assert Thresholds.validate(name, 2) is True


def test_r3_a_severity_limit_of_three_or_more_is_permitted():
    for name in SEVERITY_LIMITS:
        for value in (3, 4, 10, 100, 5000):
            assert Thresholds.validate(name, value) is True


def test_r4_zero_and_negative_are_rejected_for_every_name():
    for name in Thresholds.NAMES:
        for value in (0, -1, -100):
            assert Thresholds.validate(name, value) is False


def test_r5_an_unknown_name_is_rejected_whatever_the_value():
    for name in ("", "nesting", "NESTING_LIMIT", "max_depth", "limit"):
        assert Thresholds.validate(name, 5) is False


def test_r6_comment_ratio_min_keeps_the_floor_of_one():
    # not a severity limit: a minimum percentage, compared directly. A project
    # asking for at least 1% comments is making a sensible request.
    assert "comment_ratio_min" not in SEVERITY_LIMITS
    assert Thresholds.validate("comment_ratio_min", 1) is True
    assert Thresholds.validate("comment_ratio_min", 2) is True
    assert Thresholds.validate("comment_ratio_min", 100) is True


def test_r7_comment_ratio_min_is_still_subject_to_the_general_floor():
    assert Thresholds.validate("comment_ratio_min", 0) is False
    assert Thresholds.validate("comment_ratio_min", -5) is False


def test_r8_bools_and_non_integers_are_rejected():
    # True is an int in Python and 1 is now below the floor anyway, so this
    # guard matters most for the names where 1 is still valid
    assert Thresholds.validate("comment_ratio_min", True) is False
    assert Thresholds.validate("nesting_limit", True) is False
    assert Thresholds.validate("nesting_limit", 3.0) is False
    assert Thresholds.validate("nesting_limit", "3") is False
    assert Thresholds.validate("nesting_limit", None) is False


def test_the_two_name_tuples_are_consistent():
    # SEVERITY_LIMITS must be a subset of NAMES, or validate would apply a
    # floor to a name the menu cannot set
    for name in SEVERITY_LIMITS:
        assert name in Thresholds.NAMES
    # and exactly one name is excluded
    assert set(Thresholds.NAMES) - set(SEVERITY_LIMITS) == {"comment_ratio_min"}


def test_every_default_passes_its_own_validation():
    # the defaults must not be a configuration the menu would refuse
    defaults = Thresholds()
    for name in Thresholds.NAMES:
        assert Thresholds.validate(name, getattr(defaults, name)) is True


# --------------------------------------------------------------------------
# reachable_severities - reporting the limitation the floor does not remove.
# --------------------------------------------------------------------------


def test_the_bands_a_limit_of_one_can_produce():
    # still computable, even though validate now refuses to configure it
    assert reachable_severities(1) == (CRITICAL,)


def test_the_bands_a_limit_of_two_can_produce():
    # the configuration the agreed fix still permits. MAJOR is absent.
    assert reachable_severities(2) == (CRITICAL, MINOR)
    assert MAJOR not in reachable_severities(2)


def test_three_is_the_smallest_limit_with_all_three_bands():
    assert reachable_severities(3) == (CRITICAL, MAJOR, MINOR)
    assert MIN_SOUND_LIMIT == 3


def test_every_limit_from_three_upward_has_all_three_bands():
    for limit in range(3, 60):
        assert reachable_severities(limit) == (CRITICAL, MAJOR, MINOR)


def test_info_is_never_reachable_at_any_limit():
    # the measurement must be over the limit to reach classify_severity at all
    for limit in range(1, 60):
        assert INFO not in reachable_severities(limit)


def test_critical_is_reachable_at_every_limit():
    for limit in range(1, 60):
        assert CRITICAL in reachable_severities(limit)


def test_the_result_is_ordered_worst_first():
    for limit in range(1, 30):
        bands = reachable_severities(limit)
        positions = [RANK_ORDER.index(b) for b in bands]
        assert positions == sorted(positions)


def test_the_result_never_shrinks_as_the_limit_grows():
    previous = set()
    for limit in range(1, 40):
        current = set(reachable_severities(limit))
        assert previous <= current
        previous = current


def test_a_limit_below_one_is_rejected():
    for limit in (0, -1, -50):
        with pytest.raises(ValueError) as caught:
            reachable_severities(limit)
        assert "limit" in str(caught.value)


def test_the_permitted_floor_and_the_sound_floor_differ_by_one():
    # The substance of the 27 November decision, pinned so that the gap is
    # visible in the test suite rather than only in the write-up.
    assert Thresholds.MIN_SEVERITY_LIMIT == 2
    assert MIN_SOUND_LIMIT == 3
    assert Thresholds.validate("nesting_limit", Thresholds.MIN_SEVERITY_LIMIT) is True
    assert len(reachable_severities(Thresholds.MIN_SEVERITY_LIMIT)) == 2
    assert len(reachable_severities(MIN_SOUND_LIMIT)) == 3
