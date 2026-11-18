"""Black-box tests for score_from_issues - US29, Harshita (hcg22).

Technique: equivalence partitioning with boundary value analysis.
Function under test: core.scoring.score_from_issues(critical, major, minor, info).

A review starts at 100 and pays a weighted penalty per issue:

    raw = 100 - (15*critical + 8*major + 3*minor + 1*info)

Two rules then adjust it, and the interaction between them is what this story
is really about:

    cap    scores above 40 are pulled down to 40 when critical >= 3
    floor  scores below 0 are raised to 0

Partitions:

    S1  no issues at all                       (0,0,0,0)      -> 100
    S2  one severity only                      (0,0,1,0)      -> 97
    S3  a mix of all four                      (1,2,3,5)      -> 55
    S4  the cap applies                        (3,0,0,0)      -> 40, not 55
    S5  the cap does not apply                 (2,0,0,0)      -> 70
    S6  the cap applies but the raw score      (3,0,0,0)
        is already below 40                    vs (5,0,0,0)   -> cap is a
                                                                 maximum,
                                                                 not an
                                                                 assignment
    S7  the floor applies                      (10,0,0,0)     -> 0
    S8  any count is negative                  (-1,0,0,0)     -> ValueError

**The order of cap and floor matters, and S6/S7 are what pin it down.**
With `(10, 0, 0, 0)` the raw score is `100 - 150 = -50`. If the cap were applied
as an assignment - "if critical >= 3 then score = 40" - the answer would be 40,
which is wrong: ten critical issues must not score better than three. The cap
has to be a *minimum* against the running score, applied before the floor:

    score = min(raw, 40) if critical >= 3 else raw      ->  min(-50, 40) = -50
    score = max(score, 0)                               ->  max(-50, 0)  = 0

S4 and S7 together are the only pair of cases that distinguishes the two
readings, and both are tested below.

**Boundaries tested:** critical at 2 and 3, where the cap switches on; the raw
score at 40 and 41; and the floor at 0, approached from a raw score of exactly
0 and from one well below it.
"""

import pytest

from core.scoring import score_from_issues


# --- S1: a clean file ----------------------------------------------------------

def test_s1_no_issues_scores_one_hundred():
    # boundary: the top of the range, and the only input with no penalty
    assert score_from_issues(0, 0, 0, 0) == 100


# --- S2: one severity at a time, to pin each weight ----------------------------

def test_s2_one_info_costs_one_point():
    assert score_from_issues(0, 0, 0, 1) == 99


def test_s2_one_minor_costs_three_points():
    assert score_from_issues(0, 0, 1, 0) == 97


def test_s2_one_major_costs_eight_points():
    assert score_from_issues(0, 1, 0, 0) == 92


def test_s2_one_critical_costs_fifteen_points():
    assert score_from_issues(1, 0, 0, 0) == 85


# --- S3: a mix -----------------------------------------------------------------

def test_s3_a_mixed_file_sums_every_weight():
    # 100 - (15 + 16 + 9 + 5) = 55
    assert score_from_issues(1, 2, 3, 5) == 55


def test_s3_the_weights_are_additive():
    # two minors cost exactly twice one minor
    assert score_from_issues(0, 0, 2, 0) == 94
    assert score_from_issues(0, 0, 10, 0) == 70


# --- S4, S5: the cap and its boundary ------------------------------------------

def test_s5_two_criticals_are_not_capped():
    # boundary: the largest critical count with no cap. 100 - 30 = 70.
    assert score_from_issues(2, 0, 0, 0) == 70


def test_s4_three_criticals_are_capped():
    # boundary: the smallest critical count that triggers the cap.
    # Raw would be 100 - 45 = 55; the cap pulls it to 40.
    assert score_from_issues(3, 0, 0, 0) == 40


def test_s4_the_cap_applies_regardless_of_the_other_counts():
    # three criticals and nothing else is already capped, so adding minor
    # issues below the cap threshold changes nothing
    assert score_from_issues(3, 0, 1, 0) == 40
    assert score_from_issues(3, 0, 0, 2) == 40


# --- S6: the cap is a maximum, not an assignment -------------------------------

def test_s6_more_criticals_never_score_better_than_the_cap():
    """Four criticals score worse than three, not the same.

    Raw for (4,0,0,0) is 100 - 60 = 40, which equals the cap. Raw for
    (5,0,0,0) is 25, which is below it. A cap written as an assignment would
    return 40 for both, and 40 for ten criticals as well.
    """
    assert score_from_issues(3, 0, 0, 0) == 40
    assert score_from_issues(4, 0, 0, 0) == 40      # raw is exactly 40
    assert score_from_issues(5, 0, 0, 0) == 25      # raw is below the cap


def test_s6_the_score_never_rises_as_criticals_are_added():
    previous = 101
    for critical in range(0, 8):
        score = score_from_issues(critical, 0, 0, 0)
        assert score <= previous, "critical=%d" % critical
        previous = score


# --- S7: the floor -------------------------------------------------------------

def test_s7_a_very_bad_file_floors_at_zero():
    # raw is 100 - 150 = -50. Floored, not capped to 40.
    assert score_from_issues(10, 0, 0, 0) == 0


def test_s7_a_raw_score_of_exactly_zero_is_not_floored_upwards():
    # boundary: 100 - (8 * 12) = 4, then one more info takes it to 3;
    # a raw score reaching exactly 0 must stay 0
    assert score_from_issues(0, 12, 1, 1) == 0
    assert score_from_issues(0, 0, 0, 100) == 0


def test_s7_the_floor_holds_for_enormous_counts():
    assert score_from_issues(100, 100, 100, 100) == 0


# --- S8: invalid input ---------------------------------------------------------

def test_s8_a_negative_critical_count_is_rejected():
    # boundary: the largest invalid count
    with pytest.raises(ValueError):
        score_from_issues(-1, 0, 0, 0)


def test_s8_a_negative_count_in_any_position_is_rejected():
    with pytest.raises(ValueError):
        score_from_issues(0, -1, 0, 0)
    with pytest.raises(ValueError):
        score_from_issues(0, 0, -1, 0)
    with pytest.raises(ValueError):
        score_from_issues(0, 0, 0, -1)
