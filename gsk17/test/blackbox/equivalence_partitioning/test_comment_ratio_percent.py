"""Black-box tests for comment_ratio_percent - US04, Gunjan (gsk17).

Technique: equivalence partitioning with boundary value analysis.
Function under test: core.line_metrics.comment_ratio_percent(comment_lines, code_lines).

Comment density as a whole-number percentage of the lines that are either
comments or code. Blank lines are counted as neither and never reach this
function.

    R1  both counts zero           (0, 0)      -> 0, and NOT a ZeroDivisionError
    R2  no comments                (0, 10)     -> 0
    R3  no code                    (10, 0)     -> 100
    R4  equal counts               (5, 5)      -> 50
    R5  an ordinary mix            (28, 142)   -> 16
    R6  either count negative                  -> ValueError

**R1 is the partition this story exists for.** An empty file, or a file of
nothing but blank lines, gives both counts as zero. The obvious implementation
divides by their sum and raises `ZeroDivisionError` - which is a crash, not a
measurement. The specification requires 0, and this is the first case in the
test file for that reason.

**The result is floored, not rounded.** `28 * 100 // 170` is 16.47, reported as
16. That is a deliberate choice: a reported percentage should never overstate
the documentation present, so the fractional part is discarded rather than
rounded up. The tests below pin it at a value where rounding and flooring
differ.
"""

import pytest

from core.line_metrics import comment_ratio_percent


# --- R1: the empty file --------------------------------------------------------

def test_r1_both_counts_zero_is_zero_not_an_error():
    # the partition this story exists for: no division by zero
    assert comment_ratio_percent(0, 0) == 0


# --- R2: no comments -----------------------------------------------------------

def test_r2_code_with_no_comments_is_zero_percent():
    assert comment_ratio_percent(0, 10) == 0


def test_r2_a_single_code_line_with_no_comments():
    # boundary: the smallest non-empty file
    assert comment_ratio_percent(0, 1) == 0


# --- R3: no code ---------------------------------------------------------------

def test_r3_comments_with_no_code_is_one_hundred_percent():
    # boundary: the top of the range
    assert comment_ratio_percent(10, 0) == 100


def test_r3_a_single_comment_line_with_no_code():
    assert comment_ratio_percent(1, 0) == 100


# --- R4: equal counts ----------------------------------------------------------

def test_r4_equal_counts_are_fifty_percent():
    assert comment_ratio_percent(5, 5) == 50


def test_r4_one_of_each():
    # boundary: the smallest file containing both kinds of line
    assert comment_ratio_percent(1, 1) == 50


# --- R5: an ordinary mix, and the flooring ------------------------------------

def test_r5_an_ordinary_file():
    # 28 * 100 // 170 = 16.47 -> 16
    assert comment_ratio_percent(28, 142) == 16


def test_r5_the_result_is_floored_and_not_rounded():
    # 2 of 3 lines is 66.67%, which rounds to 67 and floors to 66
    assert comment_ratio_percent(2, 1) == 66
    # 1 of 3 is 33.33%, where rounding and flooring agree
    assert comment_ratio_percent(1, 2) == 33


def test_r5_a_ratio_just_below_a_whole_percent_does_not_round_up():
    # 99 of 100 lines is 99%, 199 of 200 is 99.5% - which must not become 100,
    # because 100 is reserved for a file with no code at all
    assert comment_ratio_percent(99, 1) == 99
    assert comment_ratio_percent(199, 1) == 99


# --- R6: invalid input ---------------------------------------------------------

def test_r6_a_negative_comment_count_is_rejected():
    # boundary: the largest invalid value
    with pytest.raises(ValueError):
        comment_ratio_percent(-1, 10)


def test_r6_a_negative_code_count_is_rejected():
    with pytest.raises(ValueError):
        comment_ratio_percent(10, -1)


def test_r6_both_negative_is_rejected():
    with pytest.raises(ValueError):
        comment_ratio_percent(-1, -1)
