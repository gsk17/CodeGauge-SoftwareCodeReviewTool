"""White-box tests for compare_scores - US31, Harshita (hcg22).

Technique: symbolic execution.
Function under test: core.history.compare_scores(before, after).

**Symbolic inputs.** Two symbolic integers, B for before and A for after, with
the derived term `D = A - B`. Every decision after the two validations
constrains D alone, which is why the seven path conditions reduce to intervals
on a single line.

    Path  Path condition                      Witness     Returns
    P1    B < 0 or B > 100                    (-1, 200)   ValueError, before
    P2    0 <= B <= 100, A < 0 or A > 100      (50, 101)   ValueError, after
    P3    valid, D == 0                        (72, 72)    UNCHANGED
    P4    valid, D >= 10                       (72, 85)    MUCH_IMPROVED
    P5    valid, 0 < D < 10                    (72, 78)    IMPROVED
    P6    valid, D <= -10                      (72, 60)    MUCH_REGRESSED
    P7    valid, -10 < D < 0                   (72, 66)    REGRESSED

Seven leaves. P1 and P2 each cover **two condition-paths**, since `or`
short-circuits: the first operand true, or the first false and the second true.
Counting those separately gives nine paths through the function, and the
distinction matters - see finding 6.

### Finding 1 - every path condition is satisfiable, which no other function in this member's set can say

Seven leaves, seven feasible paths, **no infeasible combinations at all.** That
is unusual in this project:

  * US29's score cap produced a branch reachable at exactly one issue count;
  * US22's inlined severity call has three unsatisfiable leaves out of seven;
  * US07's tree is missing a sixth leaf because two string prefixes exclude
    each other.

Full feasibility here is a consequence of the bands being **nested and tested
in order**. Each guard's condition is weaker than the last, so each one's
negation leaves a non-empty remainder for the next. A version that tested five
disjoint conditions independently would be no more correct and would introduce
the possibility of an unsatisfiable combination - which is to say the shape
that makes finding 5 a hazard is the same shape that makes this finding hold.

### Finding 2 - the bands are wildly unequal, and "much" is the common case

The valid domain is `0 <= B, A <= 100`, so `D` ranges over `[-100, 100]` - 201
values. Counting them per band:

    MUCH_REGRESSED   D in [-100, -10]     91 values
    REGRESSED        D in [-9, -1]         9 values
    UNCHANGED        D == 0                1 value
    IMPROVED         D in [1, 9]           9 values
    MUCH_IMPROVED    D in [10, 100]       91 values

**182 of the 201 possible differences are "much" something.** Counting input
pairs rather than differences sharpens it, since extreme differences need
extreme scores. Over all 101 x 101 = 10,201 valid pairs:

    MUCH_IMPROVED    4,186    41.0%
    IMPROVED           864     8.5%
    UNCHANGED          101     1.0%
    REGRESSED          864     8.5%
    MUCH_REGRESSED   4,186    41.0%

(The five sum to 10,201, which is the check that the bands partition the
domain exactly.) So **82% of all possible score pairs are classified as a large
change**, and the two bands named for the ordinary case cover 17% between them.

LARGE_CHANGE is 10 on a 0-100 scale, which sounds conservative and is not: a
quality score moving 10 points is a tenth of the scale, and on the scale
`score_from_issues` actually produces - where a single CRITICAL issue costs 15
points - it is less than one issue. **One critical issue appearing or being
fixed is always MUCH_IMPROVED or MUCH_REGRESSED.** The wording will overstate
routine change in almost every real report, and the threshold rather than the
implementation is what would have to move.

### Finding 3 - UNCHANGED is one value of D and 101 inputs

P3's path condition is `D == 0` conjoined with the two range checks, which in
the original inputs is the **diagonal** `B == A`, 0 through 100 - 101 solutions.

Worth separating from finding 1 of US04, where the one-value path condition had
exactly one solution in the inputs too. Here the derived variable collapses and
the inputs do not, so the partition is a singleton in D and a 101-member set in
(B, A). A test of this leaf is exhaustive over the derived space and a sample
of the input space, and only the second of those matters if the function is
ever changed to look at B or A directly rather than only at their difference.

### Finding 4 - the antisymmetry is provable, not merely apparent

Substituting `D -> -D` in the five banding conditions maps them onto each
other exactly:

    D == 0      ->  D == 0            P3 -> P3
    D >= 10     ->  D <= -10          P4 -> P6
    0 < D < 10  ->  -10 < D < 0       P5 -> P7

So `compare_scores(A, B)` always returns the mirror of `compare_scores(B, A)`,
for every valid pair, with UNCHANGED as the fixed point. **The function is
exactly antisymmetric.**

That is the property the docstring is defending when it rejects the
`abs(after - before)` implementation. With `abs()`, the magnitude is banded and
the direction attached afterwards, and antisymmetry becomes a claim about two
steps agreeing rather than a consequence of one. The claim would be true of a
correct implementation and could not be read off its path conditions, because
the sign would not appear in them. Carrying the sign through makes the symmetry
structural: it *is* the substitution above.

### Finding 5 - the guard order is load-bearing here, where in US07 it was not

The five banding conditions are **nested, not disjoint**:

    D >= 10   implies   D > 0
    D <= -10  implies   D < 0

So b4's set is a subset of b5's, and b6's is a subset of the implicit else's.
The guards are disjoint only because of the order they are written in.
Consequences, each provable by the same substitution:

  * **swap b4 and b5 and MUCH_IMPROVED becomes unreachable** - every gain,
    large or small, would be taken by `D > 0` first;
  * **swap b6 and the else and MUCH_REGRESSED becomes unreachable**;
  * **move b3 below b4 and nothing changes**, because `D == 0` is disjoint
    from both `D >= 10` and `D <= -10`, though it must stay above b5 and the
    else or UNCHANGED is lost to one of them.

This is the direct opposite of US07's finding 1, where the three guards formed
a conjunction, conjunction is commutative, and reordering them was proved to
change the path taken but never the result. **The same analysis applied to the
same-looking chain of guards gives the opposite answer**, and the difference is
visible only in the path conditions: US07's atoms were independent string
properties, these are nested intervals on one variable.

Four of the five banding outcomes depend on the ordering. Nothing in the source
says so, and no test of a single band would fail if two were swapped - the
suite would fail, but on the band that had become unreachable, which is a
confusing place to start debugging. Recorded here as the reason the docstring's
remark that "the branches are written out rather than looked up in a table" is
a claim about reviewability rather than a preference.

### Finding 6 - branch coverage cannot distinguish the two ways to fail a validation

b1 is `before < 0 or before > 100`, and `or` short-circuits. There are two
condition-paths to P1:

    P1a   B < 0                     the second operand never evaluated
    P1b   B >= 0 and B > 100

A suite that reaches P1 only through 101 covers both branches of the decision
and never evaluates `B < 0` to true. `coverage` reports 100% either way,
because both forms execute the same line. This is the first function in the
project where **line coverage, branch coverage and condition coverage are three
different numbers**, and the first where the distinction is worth paying for:
the two operands enforce different ends of the scale, and a transposition
defect - `before > 0 or before < 100`, which rejects nothing - would be caught
by condition coverage and missed by branch coverage of a suite that only ever
tested one end.

MC/DC would ask for three cases per decision rather than two, to show each
operand deciding the outcome alone. The four cases in
`branch_coverage/test_compare_scores.py` marked *condition coverage* are the
compromise: both operands of both validations exercised true, and both false
at their boundaries, which is condition coverage without the full MC/DC cost.

### Finding 7 - the integer domain is load-bearing and nowhere enforced

`b5` is `difference > 0` where `difference >= 1` would be equivalent - over the
integers. Over the reals they differ, and nothing in this function requires its
arguments to be integers. The range validation accepts any comparable numeric:

    compare_scores(0, 0.5)    D = 0.5    not == 0, not >= 10, > 0  -> IMPROVED
    compare_scores(0, 9.5)    D = 9.5                              -> IMPROVED
    compare_scores(0.5, 0.5)  D = 0.0                              -> UNCHANGED

So a half-point gain is IMPROVED, and the gap between the IMPROVED and
MUCH_IMPROVED bands - which over the integers is closed, 9 then 10 - is open
over the reals and holds infinitely many values that the band names still
describe correctly.

**Unreachable in the tool as it stands**, because `score_from_issues` returns
an integer by construction and is the only producer of these scores. Recorded
because it is a contract this function relies on and does not state: the
docstring says the bands are "1 to 9 points" and "10 or more", which is true
only of integer inputs, and the function would need a type check or a reworded
contract if scores ever became fractional.
"""

import pytest

from core.history import (
    IMPROVED,
    LARGE_CHANGE,
    MUCH_IMPROVED,
    MUCH_REGRESSED,
    REGRESSED,
    UNCHANGED,
    compare_scores,
)


def test_p1_before_out_of_range():
    # P1: the witness is doubly invalid, pinning the validation order
    with pytest.raises(ValueError) as caught:
        compare_scores(-1, 200)
    assert "before" in str(caught.value)
    assert "after" not in str(caught.value)


def test_p2_after_out_of_range():
    with pytest.raises(ValueError) as caught:
        compare_scores(50, 101)
    assert "after" in str(caught.value)


def test_p3_unchanged():
    assert compare_scores(72, 72) == UNCHANGED


def test_p4_much_improved():
    assert compare_scores(72, 85) == MUCH_IMPROVED


def test_p5_improved():
    assert compare_scores(72, 78) == IMPROVED


def test_p6_much_regressed():
    assert compare_scores(72, 60) == MUCH_REGRESSED


def test_p7_regressed():
    assert compare_scores(72, 66) == REGRESSED


def test_finding_1_the_seven_path_conditions_partition_the_domain():
    # Every valid pair satisfies exactly one, and no pair satisfies none.
    # 10,201 pairs, five outcomes, no exceptions and no gaps.
    expected = {MUCH_REGRESSED, REGRESSED, UNCHANGED, IMPROVED, MUCH_IMPROVED}
    seen = set()
    for before in range(0, 101):
        for after in range(0, 101):
            seen.add(compare_scores(before, after))
    assert seen == expected


def test_finding_2_the_band_sizes_over_the_whole_domain():
    # The counts derived in the write-up, recomputed. If a band boundary ever
    # moves, this is the test that says by how much.
    counts = {}
    for before in range(0, 101):
        for after in range(0, 101):
            band = compare_scores(before, after)
            counts[band] = counts.get(band, 0) + 1
    assert counts[MUCH_IMPROVED] == 4186
    assert counts[IMPROVED] == 864
    assert counts[UNCHANGED] == 101
    assert counts[REGRESSED] == 864
    assert counts[MUCH_REGRESSED] == 4186
    assert sum(counts.values()) == 101 * 101


def test_finding_2_one_critical_issue_is_always_a_large_change():
    # A CRITICAL issue costs 15 points in core.scoring, which exceeds
    # LARGE_CHANGE. So the appearance or repair of a single critical finding
    # can never be reported as a small change.
    assert LARGE_CHANGE < 15
    for before in range(15, 101):
        assert compare_scores(before, before - 15) == MUCH_REGRESSED
    for before in range(0, 86):
        assert compare_scores(before, before + 15) == MUCH_IMPROVED


def test_finding_3_unchanged_is_a_diagonal_not_a_point():
    # One value of D, 101 solutions in the inputs.
    for score in range(0, 101):
        assert compare_scores(score, score) == UNCHANGED


def test_finding_4_the_function_is_exactly_antisymmetric():
    mirror = {
        MUCH_IMPROVED: MUCH_REGRESSED,
        IMPROVED: REGRESSED,
        UNCHANGED: UNCHANGED,
        REGRESSED: IMPROVED,
        MUCH_REGRESSED: MUCH_IMPROVED,
    }
    for before in range(0, 101, 7):
        for after in range(0, 101, 5):
            forward = compare_scores(before, after)
            backward = compare_scores(after, before)
            assert backward == mirror[forward]


def test_finding_5_the_nesting_that_makes_the_order_load_bearing():
    # Every input that b4 takes would also satisfy b5's condition, so b4
    # exists only because it is written first. Both boundaries, both ways.
    assert compare_scores(50, 60) == MUCH_IMPROVED   # D = 10, also D > 0
    assert compare_scores(50, 59) == IMPROVED        # D = 9
    assert compare_scores(50, 40) == MUCH_REGRESSED  # D = -10, also D < 0
    assert compare_scores(50, 41) == REGRESSED       # D = -9
    # the largest and smallest differences the domain allows, both "much"
    assert compare_scores(0, 100) == MUCH_IMPROVED
    assert compare_scores(100, 0) == MUCH_REGRESSED


def test_finding_6_both_condition_paths_to_each_validation_leaf():
    # P1a and P1b, then P2a and P2b. Branch coverage needs one of each pair.
    for bad_before in (-1, -100, 101, 200):
        with pytest.raises(ValueError) as caught:
            compare_scores(bad_before, 50)
        assert "before" in str(caught.value)
    for bad_after in (-1, -100, 101, 200):
        with pytest.raises(ValueError) as caught:
            compare_scores(50, bad_after)
        assert "after" in str(caught.value)


def test_finding_6_the_valid_boundaries_are_not_rejected():
    # Both operands of both validations false at their extremes. A
    # transposition defect in either guard would reject one of these.
    assert compare_scores(0, 0) == UNCHANGED
    assert compare_scores(100, 100) == UNCHANGED
    assert compare_scores(0, 1) == IMPROVED
    assert compare_scores(100, 99) == REGRESSED


def test_finding_7_the_integer_domain_is_assumed_and_not_checked():
    # Unreachable through score_from_issues, which returns an integer. The
    # function accepts these and bands them by the same path conditions, so
    # the gap between IMPROVED and MUCH_IMPROVED is open rather than closed.
    assert compare_scores(0, 0.5) == IMPROVED
    assert compare_scores(0, 9.5) == IMPROVED
    assert compare_scores(0, 10.0) == MUCH_IMPROVED
    assert compare_scores(0.5, 0.5) == UNCHANGED
    assert compare_scores(0.5, 0.0) == REGRESSED
