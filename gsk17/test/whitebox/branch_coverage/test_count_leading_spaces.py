"""White-box tests for count_leading_spaces - US02, Gunjan (gsk17).

Technique: branch coverage.
Function under test: core.scanner.count_leading_spaces(line, tab_width).

One guard, one loop and a three-way branch inside it:

    b1  tab_width < 1              guard, raises
    L   the character loop         for character in line
    b2    character == " "         add one column
    b3    character == "\\t"        add tab_width columns
    (else)                         break - indentation has ended

b2 and b3 are an if/elif/else, so the three arms are mutually exclusive and
each iteration takes exactly one. Together with the two loop-header outcomes
and the guard, there are seven outcomes to cover:

    outcome                        covered by
    b1 TRUE                        tab_width_zero, tab_width_negative
    b1 FALSE                       every other test
    L not taken                    the_empty_line
    L taken                        every non-empty test
    b2 (space arm)                 leading_spaces
    b3 (tab arm)                   leading_tabs
    else arm (break)               code_in_column_one

**The else arm is the loop's only exit other than exhaustion.** A line of pure
whitespace leaves the loop by running out of characters; any line with code in
it leaves through the break. Both exits are covered, because a function that
returned the right answer for `"    x"` but looped off the end of `"    "`
would pass one and fail the other.

**Why the arms are written out rather than looked up.** A dict mapping " " to 1
and "\\t" to tab_width would be shorter, but it would collapse b2, b3 and the
else arm into a single `.get()` with a default - one branch instead of three,
and nothing for a symbolic execution tree to fork on. The explicit form is a
deliberate project decision, recorded in the design notes.
"""

import pytest

from core.scanner import count_leading_spaces


def test_b1_true_a_tab_width_of_zero_is_rejected():
    # b1 TRUE - returns before the loop is entered
    with pytest.raises(ValueError):
        count_leading_spaces("    x", 0)


def test_b1_true_a_negative_tab_width_is_rejected():
    with pytest.raises(ValueError):
        count_leading_spaces("    x", -4)


def test_loop_not_taken_on_the_empty_line():
    # L not taken - the only input where the loop body never runs, so the
    # returned value is the initial width rather than anything accumulated
    assert count_leading_spaces("", 4) == 0


def test_b2_the_space_arm():
    # b2 taken four times, then the else arm breaks
    assert count_leading_spaces("    x = 1", 4) == 4


def test_b3_the_tab_arm():
    # b3 taken twice, then the else arm breaks
    assert count_leading_spaces("\t\tx = 1", 4) == 8


def test_the_else_arm_breaks_immediately():
    # else arm on the first iteration - neither b2 nor b3 ever taken
    assert count_leading_spaces("x = 1", 4) == 0


def test_all_three_arms_in_one_line():
    # b2, then b3, then the else arm: 2 spaces + one 4-wide tab = 6
    assert count_leading_spaces("  \tx", 4) == 6


def test_the_loop_exits_by_exhaustion_not_by_break():
    # Whitespace only, so the else arm is never reached and the loop ends by
    # running out of characters. The complement of test_the_else_arm_breaks.
    assert count_leading_spaces("    ", 4) == 4


def test_the_break_stops_accumulation():
    # Whitespace after the break must not be counted - proves the else arm
    # exits the loop rather than merely skipping the iteration
    assert count_leading_spaces("  x    ", 4) == 2
