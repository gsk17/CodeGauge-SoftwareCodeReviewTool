"""Black-box tests for nesting_penalty - US13, Kasam (khm12).

Technique: equivalence partitioning with boundary value analysis.
Function under test: core.complexity.nesting_penalty(depth, limit).

Penalty points charged for nesting past a limit, so that the score reflects how
far past the limit the code is rather than only that it is past. Five points per
level over, capped at twenty-five.

    R1  no nesting at all          (0, 3)    -> 0
    R2  exactly on the limit       (3, 3)    -> 0
    R3  one level over             (4, 3)    -> 5
    R4  three levels over          (6, 3)    -> 15
    R5  five levels over           (8, 3)    -> 25, the cap value, uncapped
    R6  six levels over            (9, 3)    -> 25, the cap applied
    R7  absurdly nested            (30, 3)   -> 25
    R8  depth negative                       -> ValueError
    R9  limit below 1                        -> ValueError

**Why a penalty and not a rating.** `rule_nesting` already answers "is this
function too deeply nested" and `classify_severity` bands how badly. Neither
produces a number the score can subtract. This function does, and it is charged
per level so that a function six levels deep costs more than one four levels
deep - which the severity bands cannot express, because both land in the same
band at most limits.

**R5 and R6 are the partitions this story exists for, and they return the same
number for different reasons.** Five levels over is 5 x 5 = 25, which equals the
cap but is not produced by it. Six levels over is 30, which the cap reduces to
25. So a returned 25 does not say whether the cap fired, and the two cases are
separate partitions despite being indistinguishable from the result alone. The
white-box tests take different paths through the function for these two inputs;
these tests cannot tell them apart and say so rather than merging them.

**Why cap at all.** Without a cap, a pathological function could charge a
penalty larger than the entire score, and `score_from_issues` floors at 0 - so
everything past some depth would be reported identically anyway, but only after
the arithmetic had gone through a number no reviewer can interpret. Capping at
25 makes the ceiling explicit and keeps the penalty comparable with the issue
weights, where a CRITICAL issue costs 15.

**The cap loses information, deliberately.** A function nested 9 levels deep and
one nested 30 levels deep are charged identically. Once code is that nested the
exact figure stops being actionable, and the nesting issue rather than the
penalty is what a reviewer should read. R6 and R7 pin that.

**R2 is inclusive.** A function sitting exactly on the configured limit is
acceptable and costs nothing, which matches every other limit comparison in the
project - `rule_nesting`, `rule_complexity`, `rule_params` and
`parameter_count_rating` all treat their limit as inclusive.
"""

import pytest

from core.complexity import nesting_penalty


def test_r1_no_nesting_costs_nothing():
    assert nesting_penalty(0, 3) == 0


def test_r2_exactly_on_the_limit_costs_nothing():
    assert nesting_penalty(3, 3) == 0


def test_r3_one_level_over():
    assert nesting_penalty(4, 3) == 5


def test_r4_three_levels_over():
    assert nesting_penalty(6, 3) == 15


def test_r5_five_levels_over_reaches_the_cap_value_without_the_cap():
    # 5 levels x 5 points = 25, which happens to equal the cap
    assert nesting_penalty(8, 3) == 25


def test_r6_six_levels_over_is_reduced_by_the_cap():
    # 6 levels x 5 points = 30, capped to 25
    assert nesting_penalty(9, 3) == 25


def test_r7_absurd_nesting_is_charged_the_same_as_six_levels_over():
    assert nesting_penalty(30, 3) == 25
    assert nesting_penalty(300, 3) == 25


def test_r5_and_r6_are_indistinguishable_from_the_result():
    # Recorded rather than hidden: two separate partitions, one number. The
    # branch taken differs and only a white-box test can see which.
    assert nesting_penalty(8, 3) == nesting_penalty(9, 3)


def test_r8_negative_depth_is_rejected():
    with pytest.raises(ValueError) as caught:
        nesting_penalty(-1, 3)
    assert "depth" in str(caught.value)


def test_r9_a_limit_below_one_is_rejected():
    with pytest.raises(ValueError) as caught:
        nesting_penalty(5, 0)
    assert "limit" in str(caught.value)


# --------------------------------------------------------------------------
# Boundary value analysis.
# --------------------------------------------------------------------------


def test_boundaries_around_the_limit():
    assert nesting_penalty(2, 3) == 0    # under
    assert nesting_penalty(3, 3) == 0    # on it, still free
    assert nesting_penalty(4, 3) == 5    # the first charged level


def test_boundaries_around_the_cap():
    assert nesting_penalty(7, 3) == 20   # four levels over
    assert nesting_penalty(8, 3) == 25   # five, equal to the cap
    assert nesting_penalty(9, 3) == 25   # six, the cap binds
    assert nesting_penalty(10, 3) == 25  # and keeps binding


def test_the_penalty_rises_in_steps_of_five():
    # the whole charged range at the default limit, before the cap
    assert nesting_penalty(4, 3) == 5
    assert nesting_penalty(5, 3) == 10
    assert nesting_penalty(6, 3) == 15
    assert nesting_penalty(7, 3) == 20
    assert nesting_penalty(8, 3) == 25


def test_the_smallest_valid_limit():
    # limit 1: depth 1 is free, and the cap binds from depth 7
    assert nesting_penalty(1, 1) == 0
    assert nesting_penalty(2, 1) == 5
    assert nesting_penalty(6, 1) == 25
    assert nesting_penalty(7, 1) == 25


def test_a_generous_limit_pushes_the_whole_scale_out():
    # the bands are relative to the limit, so a limit of 10 charges nothing
    # until depth 11 and caps from depth 16
    assert nesting_penalty(10, 10) == 0
    assert nesting_penalty(11, 10) == 5
    assert nesting_penalty(15, 10) == 25
    assert nesting_penalty(16, 10) == 25


def test_depth_zero_is_free_at_every_limit():
    for limit in range(1, 12):
        assert nesting_penalty(0, limit) == 0
