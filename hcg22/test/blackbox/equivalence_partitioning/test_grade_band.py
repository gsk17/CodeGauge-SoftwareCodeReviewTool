"""Black-box tests for grade_band - US30, Harshita (hcg22).

Technique: equivalence partitioning with boundary value analysis.
Function under test: core.scoring.grade_band(score).

A score of 0 to 100 is reduced to a letter grade. The five valid partitions are
closed intervals, so every one of them has two boundaries and both are tested:

    G1  85 - 100   -> "A"
    G2  70 -  84   -> "B"
    G3  60 -  69   -> "C"
    G4  50 -  59   -> "D"
    G5   0 -  49   -> "F"

    G6  score > 100 or score < 0   -> ValueError

Boundary value analysis is the whole of this story. A banding function has no
interesting interior - every defect lives at a threshold, so each cut point is
tested from both sides: 84/85, 69/70, 59/60 and 49/50, plus the domain ends at
0/100 and the first invalid values at -1 and 101.
"""

import pytest

from core.scoring import grade_band


# --- G1: A ---------------------------------------------------------------------

def test_g1_a_perfect_score_is_an_a():
    # boundary: the top of the domain
    assert grade_band(100) == "A"


def test_g1_the_lowest_a_is_eighty_five():
    # boundary: the A/B cut point, from the A side
    assert grade_band(85) == "A"


def test_g1_an_interior_a():
    assert grade_band(92) == "A"


# --- G2: B ---------------------------------------------------------------------

def test_g2_the_highest_b_is_eighty_four():
    # boundary: the A/B cut point, from the B side
    assert grade_band(84) == "B"


def test_g2_the_lowest_b_is_seventy():
    # boundary: the B/C cut point, from the B side
    assert grade_band(70) == "B"


def test_g2_an_interior_b():
    assert grade_band(77) == "B"


# --- G3: C ---------------------------------------------------------------------

def test_g3_the_highest_c_is_sixty_nine():
    # boundary: the B/C cut point, from the C side
    assert grade_band(69) == "C"


def test_g3_the_lowest_c_is_sixty():
    # boundary: the C/D cut point, from the C side
    assert grade_band(60) == "C"


def test_g3_an_interior_c():
    assert grade_band(65) == "C"


# --- G4: D ---------------------------------------------------------------------

def test_g4_the_highest_d_is_fifty_nine():
    # boundary: the C/D cut point, from the D side
    assert grade_band(59) == "D"


def test_g4_the_lowest_d_is_fifty():
    # boundary: the D/F cut point, from the D side
    assert grade_band(50) == "D"


def test_g4_an_interior_d():
    assert grade_band(55) == "D"


# --- G5: F ---------------------------------------------------------------------

def test_g5_the_highest_f_is_forty_nine():
    # boundary: the D/F cut point, from the F side
    assert grade_band(49) == "F"


def test_g5_a_score_of_zero_is_an_f():
    # boundary: the bottom of the domain
    assert grade_band(0) == "F"


def test_g5_an_interior_f():
    assert grade_band(25) == "F"


# --- G6: outside the domain ----------------------------------------------------

def test_g6_a_score_above_one_hundred_is_rejected():
    # boundary: the smallest invalid value above the domain
    with pytest.raises(ValueError):
        grade_band(101)


def test_g6_a_negative_score_is_rejected():
    # boundary: the largest invalid value below the domain
    with pytest.raises(ValueError):
        grade_band(-1)


def test_g6_a_far_out_of_range_score_is_rejected():
    with pytest.raises(ValueError):
        grade_band(1000)
