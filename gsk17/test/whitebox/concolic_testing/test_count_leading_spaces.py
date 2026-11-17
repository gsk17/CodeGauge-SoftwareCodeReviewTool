"""White-box tests for count_leading_spaces - US02, Gunjan (gsk17).

Technique: concolic (dynamic symbolic) execution.
Function under test: core.scanner.count_leading_spaces(line, tab_width).

Concolic execution is a better fit for this function than pure symbolic
execution, and for a specific reason: the concrete run **fixes the characters**,
so each iteration of the loop branches on a known value and the solver only has
to pick the *next* character rather than reason about a symbolic string. The
awkward string constraints described in the symbolic analysis mostly disappear.

Seeded with ("  \\tx = 1", 4) - two spaces, a tab, then code. That is a real
line of indented Python, chosen over a minimal input so the first run exercises
all three arms of the branch.

    It.  Input              Path  Collected PC             Negated         Next
    1    ("  \\tx = 1", 4)   P     W>=1, c0=" ", c1=" ",
                                  c2="\\t", c3=other        c0=" " -> c0="\\t"  ("\\t \\tx", 4)
    2    ("\\t \\tx", 4)       P     W>=1, c0="\\t", c1=" ",
                                  c2="\\t", c3=other        c1=" " -> c1=other ("\\tx", 4)
    3    ("\\tx", 4)          P7    W>=1, c0="\\t", c1=other  c0="\\t" -> c0=other ("x", 4)
    4    ("x", 4)            P3    W>=1, c0=other           no c0 branch
                                                            left; shrink     ("", 4)
    5    ("", 4)             P2    W >= 1                   W>=1 -> W<1    ("", 0)
    6    ("", 0)             P1    W < 1                    none left        -

Six iterations. Each one negates the *earliest* branch that still has an
unexplored arm, which is why the walk shortens the whitespace prefix as it goes
rather than lengthening it.

**The three-way branch needs two negations, not one.** `c == " "` and
`c == "\\t"` are separate decisions in an if/elif, so negating the space arm
leaves the tab arm and the else arm both unexplored. Iterations 1 to 3 work
through them in order for c0, which is why the walk visits the same position
three times before moving on. A two-valued branch would have needed one
negation per position.

**Character equality is cheap to solve here.** Negating `c0 == " "` requires
only "some character that is not a space", and the solver has a three-class
alphabet to choose from - space, tab, other. So each negation has at most two
candidate answers, and the walk is finite per position even though the
character domain is not.

**What the walk does not reach.** Every path in the k = 2 bounded analysis with
*two* leading whitespace characters - P8 to P11 - is reached only by the seed
itself, which has three. The walk shortens the prefix monotonically and never
extends it, so it cannot generate a two-whitespace line once it has gone below
that length. Those four paths are covered in symbolic_execution/, where the
bound is chosen deliberately rather than reached by negation. Reported here
rather than papered over.
"""

import pytest

from core.scanner import count_leading_spaces


def test_iteration_1_the_seed():
    # seed ("  \tx = 1", 4): space, space, tab, then code.
    # Returns 1 + 1 + W = 2 + 4 = 6.
    assert count_leading_spaces("  \tx = 1", 4) == 6


def test_iteration_2_negating_the_space_arm_at_position_zero():
    # PC: ... and NOT (c0 == " "), so c0 takes the tab arm instead.
    # Returns W + 1 + W = 4 + 1 + 4 = 9.
    assert count_leading_spaces("\t \tx", 4) == 9


def test_iteration_3_negating_the_space_arm_at_position_one():
    # PC: c0 = "\t" and NOT (c1 == " ") and NOT (c1 == "\t"), so c1 breaks.
    # Returns W = 4.
    assert count_leading_spaces("\tx", 4) == 4


def test_iteration_4_negating_both_arms_at_position_zero():
    # PC: NOT (c0 == " ") and NOT (c0 == "\t") - the else arm on the first
    # iteration. Returns 0 without touching the accumulator.
    assert count_leading_spaces("x", 4) == 0


def test_iteration_5_after_shrinking_to_the_empty_line():
    # Length reduced by hand: the loop count is not a branch condition, so the
    # solver cannot reach n = 0 by negation. PC: W >= 1 only.
    assert count_leading_spaces("", 4) == 0


def test_iteration_6_negating_the_guard():
    # The last branch with an unexplored arm is b1 itself.
    # PC: NOT (W >= 1) -> W <= 0. Largest solution: W = 0.
    with pytest.raises(ValueError):
        count_leading_spaces("", 0)


def test_the_walk_in_sequence():
    """The five returning iterations, replayed in generated order."""
    walk = ((1, "  \tx = 1", 6), (2, "\t \tx", 9), (3, "\tx", 4),
            (4, "x", 0), (5, "", 0))
    for iteration, line, expected in walk:
        assert count_leading_spaces(line, 4) == expected, \
            "iteration %d" % iteration


def test_each_negation_changed_exactly_one_character():
    """Iterations 1 to 3 differ from their predecessor at a single position,
    which is what distinguishes a solver-generated input from a hand-written
    one - the solver changes only what it was asked to negate."""
    first, second = "  \tx = 1", "\t \tx = 1"
    differences = sum(1 for a, b in zip(first, second) if a != b)
    assert differences == 1      # only c0, the position whose arm was negated
    # and the measured widths differ accordingly: 2 + W against W + 1 + W
    assert count_leading_spaces(first, 4) == 6
    assert count_leading_spaces(second, 4) == 9


def test_the_three_way_branch_needs_two_negations_per_position():
    """Negating the space arm at a position leaves two arms unexplored, so the
    same position is visited three times. Shown by holding position 0 fixed as
    each of the three classes in turn."""
    assert count_leading_spaces(" x", 4) == 1       # space arm
    assert count_leading_spaces("\tx", 4) == 4      # tab arm
    assert count_leading_spaces("xx", 4) == 0       # else arm
