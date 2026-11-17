"""White-box tests for count_leading_spaces - US02, Gunjan (gsk17).

Technique: symbolic execution with bounded loop unrolling.
Function under test: core.scanner.count_leading_spaces(line, tab_width).

This function is the awkward one in the project, and the reason is worth
stating before the tree.

**Its path conditions are not linear integer constraints.** Every other
function analysed here takes integers and compares them with <, <= and ==, so
each path condition is a conjunction of linear inequalities that solves by
hand. This one branches on *character equality* - `c == " "`, `c == "\\t"` -
over a symbolic string of unknown length. The constraints are therefore over a
sequence of symbolic characters, and the returned value is a symbolic
expression in W = tab_width rather than a constant.

That is not a flaw in the design; it is the boundary of it. `core/scanner.py`
is the only module that reads text, and everything downstream consumes the
integers it produces - which is exactly why the rest of the project's symbolic
analyses are tractable by hand. This module is where the text stops.

**Symbolic inputs.** W for tab_width, and c0, c1, c2 ... for the characters of
the line. Each ci ranges over three equivalence classes, because the code can
only distinguish three: space, tab, and anything else. Bounding the unrolling
at k = 2:

    Path  Path condition                         Witness        Returns
    P1    W < 1                                  ("  x", 0)     ValueError
    P2    W >= 1, line empty                     ("", 4)        0
    P3    W >= 1, c0 = other                     ("x", 4)       0
    P4    W >= 1, c0 = " ", line ends            (" ", 4)       1
    P5    W >= 1, c0 = "\\t", line ends           ("\\t", 4)      W
    P6    W >= 1, c0 = " ", c1 = other           (" x", 4)      1
    P7    W >= 1, c0 = "\\t", c1 = other          ("\\tx", 4)     W
    P8    W >= 1, c0 = " ", c1 = " "              ("  ", 4)      2
    P9    W >= 1, c0 = " ", c1 = "\\t"             (" \\t", 4)     1 + W
    P10   W >= 1, c0 = "\\t", c1 = " "             ("\\t ", 4)     W + 1
    P11   W >= 1, c0 = "\\t", c1 = "\\t"            ("\\t\\t", 4)    2W

Eleven paths at k = 2. The general shape is clear from them: a prefix of m
spaces and n tabs, terminated either by a non-whitespace character or by the
end of the line, returns **m + nW**.

**Finding 1 - the returned value is linear in W, and the two arms commute.**
P9 and P10 are different paths with different path conditions, but both return
1 + W. The accumulation is addition, which is commutative, so the *order* of
spaces and tabs in the prefix cannot affect the result - only the counts can.
That is a property of the returned symbolic expression, not something a set of
examples could establish, and it is what the random-based black-box test
asserts by sampling.

**Finding 2 - no path can return a non-zero width for a line starting with
code.** P3 is the only path reachable when c0 is neither space nor tab, and it
returns 0 before the accumulator is ever touched. So `count_leading_spaces` and
`classify_line` (US01) agree by construction: a line classified as code at
column one always measures 0 indentation. Two functions in the same module,
consistent because of their path structure rather than because anyone tested
the combination.

**Finding 3 - W is unconstrained above 1 on every path.** No path condition
mentions an upper bound on W, so the function is total in its second argument:
there is no tab width, however large, that reaches a different path. The guard
at b1 is the only constraint on W in the entire tree.
"""

import pytest

from core.scanner import count_leading_spaces


# --- P1: the guard -------------------------------------------------------------

def test_p1_the_tab_width_guard():
    # PC: W < 1. Boundary witness W = 0, the largest invalid value.
    with pytest.raises(ValueError):
        count_leading_spaces("  x", 0)


# --- P2, P3: the two ways to return 0 ------------------------------------------

def test_p2_the_empty_line():
    # PC: W >= 1 and the line is empty. The loop never runs.
    assert count_leading_spaces("", 4) == 0


def test_p3_code_in_the_first_column():
    # PC: W >= 1 and c0 is neither space nor tab. Breaks on iteration one.
    assert count_leading_spaces("x", 4) == 0


# --- P4, P5: one whitespace character, then the line ends ----------------------

def test_p4_a_single_space_returns_one():
    # PC: W >= 1, c0 = " ", no c1. Returns 1 - independent of W.
    assert count_leading_spaces(" ", 4) == 1


def test_p5_a_single_tab_returns_w():
    # PC: W >= 1, c0 = "\t", no c1. Returns the symbolic value W itself, so
    # the assertion is written against two different W to show it is W and
    # not the constant 4.
    assert count_leading_spaces("\t", 4) == 4
    assert count_leading_spaces("\t", 7) == 7


# --- P6, P7: one whitespace character, then code -------------------------------

def test_p6_a_space_then_code():
    # PC: W >= 1, c0 = " ", c1 = other. Same return as P4 by a different path.
    assert count_leading_spaces(" x", 4) == 1


def test_p7_a_tab_then_code():
    # PC: W >= 1, c0 = "\t", c1 = other. Returns W.
    assert count_leading_spaces("\tx", 4) == 4


# --- P8 to P11: two whitespace characters --------------------------------------

def test_p8_two_spaces():
    # PC: c0 = c1 = " ". Returns 2.
    assert count_leading_spaces("  ", 4) == 2


def test_p9_a_space_then_a_tab():
    # PC: c0 = " ", c1 = "\t". Returns 1 + W.
    assert count_leading_spaces(" \t", 4) == 5


def test_p10_a_tab_then_a_space():
    # PC: c0 = "\t", c1 = " ". Returns W + 1 - a different path from P9 with
    # the same returned expression. See Finding 1.
    assert count_leading_spaces("\t ", 4) == 5


def test_p11_two_tabs():
    # PC: c0 = c1 = "\t". Returns 2W.
    assert count_leading_spaces("\t\t", 4) == 8
    assert count_leading_spaces("\t\t", 3) == 6


# --- the three findings, asserted rather than only argued ----------------------

def test_finding_1_the_order_of_the_prefix_does_not_matter():
    """P9 and P10 return the same expression because accumulation is addition.

    Every arrangement of two spaces and two tabs must therefore measure
    2 + 2W, whatever order they appear in.
    """
    expected = 2 + 2 * 4
    for prefix in ("  \t\t", "\t\t  ", " \t \t", "\t \t ", " \t\t ", "\t  \t"):
        assert count_leading_spaces(prefix + "x", 4) == expected


def test_finding_2_a_code_line_always_measures_zero():
    """P3 is the only path reachable when the first character is code, and it
    returns before the accumulator is touched. Consistent with US01's
    classify_line by construction."""
    for line in ("x = 1", "def f():", "#comment", "return", "}"):
        assert count_leading_spaces(line, 4) == 0


def test_finding_3_the_function_is_total_in_tab_width_above_one():
    """No path condition bounds W above, so every W >= 1 is valid and the
    result scales linearly in it."""
    for tab_width in (1, 2, 3, 4, 8, 100, 10000):
        assert count_leading_spaces("\t", tab_width) == tab_width
        assert count_leading_spaces(" \t", tab_width) == 1 + tab_width
        assert count_leading_spaces("\t\t", tab_width) == 2 * tab_width


def test_the_general_shape_m_spaces_and_n_tabs():
    """The bounded paths establish the pattern m + nW; checked here beyond the
    k = 2 bound, which is the inductive step the bound leaves open."""
    for spaces in range(0, 5):
        for tabs in range(0, 5):
            prefix = " " * spaces + "\t" * tabs
            assert count_leading_spaces(prefix + "code", 4) == spaces + tabs * 4
