"""Black-box tests for count_leading_spaces - US02, Gunjan (gsk17).

Technique: equivalence partitioning with boundary value analysis.
Function under test: core.scanner.count_leading_spaces(line, tab_width).

The input domain is partitioned on the two arguments independently.

`line`, by its leading whitespace:

    L1  no leading whitespace          "x = 1"        -> 0
    L2  spaces only                    "    x = 1"    -> count of spaces
    L3  tabs only                      "\tx = 1"      -> tabs x tab_width
    L4  mixed spaces and tabs          "  \tx = 1"    -> sum of both
    L5  whitespace only, no code       "    "         -> count of spaces
    L6  the empty string               ""             -> 0

`tab_width`, by validity:

    T1  tab_width >= 1                 valid
    T2  tab_width <= 0                 invalid, ValueError

Boundaries tested: the empty line, a single leading space, a single leading tab,
and tab_width at 1 (smallest valid) and 0 (largest invalid).
"""

import pytest

from core.scanner import count_leading_spaces


# --- L1: no leading whitespace -------------------------------------------------

def test_l1_a_line_starting_in_column_one_has_no_indentation():
    assert count_leading_spaces("x = 1", 4) == 0


def test_l1_trailing_whitespace_is_not_counted():
    # only LEADING whitespace is indentation
    assert count_leading_spaces("x = 1    ", 4) == 0


# --- L2: spaces only -----------------------------------------------------------

def test_l2_four_leading_spaces():
    assert count_leading_spaces("    x = 1", 4) == 4


def test_l2_one_leading_space_is_the_lower_boundary():
    # boundary: the smallest non-zero indentation
    assert count_leading_spaces(" x = 1", 4) == 1


# --- L3: tabs only -------------------------------------------------------------

def test_l3_one_tab_counts_as_tab_width():
    assert count_leading_spaces("\tx = 1", 4) == 4


def test_l3_two_tabs_count_as_twice_tab_width():
    assert count_leading_spaces("\t\tx = 1", 4) == 8


def test_l3_tab_width_of_one_is_the_lower_valid_boundary():
    # boundary: smallest valid tab_width, so a tab counts as a single column
    assert count_leading_spaces("\tx = 1", 1) == 1


# --- L4: mixed -----------------------------------------------------------------

def test_l4_two_spaces_then_a_tab():
    # 2 spaces + one 4-wide tab = 6
    assert count_leading_spaces("  \tx = 1", 4) == 6


def test_l4_a_tab_then_two_spaces():
    assert count_leading_spaces("\t  x = 1", 4) == 6


# --- L5, L6: degenerate lines --------------------------------------------------

def test_l5_a_line_of_whitespace_only_still_reports_its_width():
    assert count_leading_spaces("    ", 4) == 4


def test_l6_the_empty_line_has_no_indentation():
    # boundary: the shortest possible input
    assert count_leading_spaces("", 4) == 0


# --- T2: invalid tab_width -----------------------------------------------------

def test_t2_a_tab_width_of_zero_is_rejected():
    # boundary: the largest invalid tab_width
    with pytest.raises(ValueError):
        count_leading_spaces("x", 0)


def test_t2_a_negative_tab_width_is_rejected():
    with pytest.raises(ValueError):
        count_leading_spaces("x", -1)
