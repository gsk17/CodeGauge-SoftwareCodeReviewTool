"""White-box tests for compare_scores - US31, Harshita (hcg22).

Technique: concolic (dynamic symbolic) execution.
Function under test: core.history.compare_scores(before, after).

Seeded with `(72, 85)` - the quality score of `core/scanner.py` at the Sprint 1
close and its score after US07 merged, so the first run is a real comparison
between two real reviews.

Writing B for before, A for after and D for `A - B`:

    It.  Input       Path  Collected PC                  Negated     Next
    1    (72, 85)    P4    valid, D!=0, D>=10            D>=10       (72, 78)
    2    (72, 78)    P5    valid, D!=0, D<10, D>0        D>0         (72, 60)
    3    (72, 60)    P6    valid, D!=0, D<0, D<=-10      D<=-10      (72, 66)
    4    (72, 66)    P7    valid, D!=0, D<0, D>-10       D!=0        (72, 72)
    5    (72, 72)    P3    valid, D==0                   A valid     (72, 101)
    6    (72, 101)   P2    B valid, A invalid            B valid     (-1, 101)
    7    (-1, 101)   P1    B invalid                     none        -

Seven iterations, seven leaves, **100% path coverage**, with **three
backtracks** - at iterations 5, 6 and 7, each of which unwinds to a shallower
branch because the deeper ones are exhausted.

That is the most backtracking of any walk in this member's set: US28 and US30
are chains, US29 backtracks four times for ten leaves. The cause here is that
the four banding guards sit at the bottom of the tree and are consumed first,
after which every remaining leaf is above them.

### The derived variable, and the choice it hides

Every negation produced a constraint on **D**, and D is not an input. Each
witness had to be recovered by solving `A - B = d` for a target d, which has
infinitely many solutions, and the walk resolved that by **holding B fixed at
the seed's 72 and moving A**:

    d = 6    -> (72, 78)
    d = -12  -> (72, 60)
    d = -6   -> (72, 66)
    d = 0    -> (72, 72)

Holding A fixed and moving B would be equally valid - `(66, 85)` has d = 19 and
reaches P4 just as the seed does - and produces a different suite with the same
coverage. Fixing B was chosen because it reads as one baseline compared against
several later reviews, which is what the function is for.

**A constraint on a derived value under-determines the inputs**, and that is
where the walk's freedom lives in this function. Compare US04, where the
negation `C + K == 0` under two non-negativity constraints pinned the model
exactly and no choice was available.

### Finding - path coverage is complete and condition coverage is not, and the technique cannot close the gap

Iteration 5 negates `not (A < 0 or A > 100)`, handing the solver

    0 <= B <= 100  and  (A < 0 or A > 100)

which is a **disjunction**. A solver returns one model. It returned `A = 101`;
`A = -1` is an equally good model of the same constraint and reaches the same
leaf by the other operand. The walk has no reason to ask for the second,
because the bookkeeping that drives it is per *decision* - the decision has
now been seen both ways, so there is nothing left to negate.

The same happens at iteration 6 for B.

So this walk achieves **100% path coverage while leaving two of the four
validation operands never evaluated true**: `A < 0` and `B > 100` are not
exercised by any of the seven cases above. A transposition defect in either
guard - `before > 0 or before < 100`, which rejects nothing at all - would
survive a suite that was complete by the measure the walk optimises.

**Two walks can be equally complete and disagree about which operands they
covered.** A walk whose solver preferred the first disjunct would cover `A < 0`
and `B < 0` and miss the other two. The coverage figure is reproducible and
the condition coverage behind it is not, which makes the figure a poor summary
of what the walk achieved.

The four cases after the walk below close the gap. They are not derived from
any negation and could not be: they are a second input for a path already
covered, which is exactly what a path-driven technique will never ask for.

### What else the walk does not reach

The band boundaries. Iteration 1 went from D = 13 to D = 6 and never evaluated
D = 10 or D = 9, the pair that decides whether LARGE_CHANGE is inclusive. For
the same reason as in US14 and US22, those points lie *inside* paths the walk
has already visited, so no negation asks for them. They are appended too.
"""

import pytest

from core.history import (
    IMPROVED,
    MUCH_IMPROVED,
    MUCH_REGRESSED,
    REGRESSED,
    UNCHANGED,
    compare_scores,
)


def test_iteration_1_the_seed_two_real_reviews():
    # Seed (72, 85): core/scanner.py before and after US07 merged. D = 13.
    assert compare_scores(72, 85) == MUCH_IMPROVED


def test_iteration_2_negating_the_large_gain_test():
    # Negating D >= 10 under D != 0. The solver held B fixed and moved A.
    assert compare_scores(72, 78) == IMPROVED
    # moving B instead would have reached the same leaf
    assert compare_scores(79, 85) == IMPROVED


def test_iteration_3_negating_the_gain_test():
    # Negating D > 0 leaves D < 0, and b6 is then evaluated for the first
    # time in the walk.
    assert compare_scores(72, 60) == MUCH_REGRESSED


def test_iteration_4_negating_the_large_loss_test():
    # Negating D <= -10 with D < 0 carried forward.
    assert compare_scores(72, 66) == REGRESSED


def test_iteration_5_the_first_backtrack():
    # The four banding guards are exhausted, so the walk unwinds to b3.
    assert compare_scores(72, 72) == UNCHANGED


def test_iteration_6_the_second_backtrack_resolves_a_disjunction():
    # Negating the `after` validation gives a disjunction, and the solver
    # returned the second operand. The first is never asked for.
    with pytest.raises(ValueError) as caught:
        compare_scores(72, 101)
    assert "after" in str(caught.value)


def test_iteration_7_the_third_backtrack():
    # Negating the `before` validation. Again a disjunction, again one model.
    with pytest.raises(ValueError) as caught:
        compare_scores(-1, 101)
    assert "before" in str(caught.value)


# ---------------------------------------------------------------------------
# Not produced by the walk. The two operands the walk's solver did not choose,
# which no negation would ever request because the decision is already covered.
# ---------------------------------------------------------------------------


def test_outside_the_walk_the_operand_the_solver_skipped_for_after():
    with pytest.raises(ValueError) as caught:
        compare_scores(72, -1)
    assert "after" in str(caught.value)


def test_outside_the_walk_the_operand_the_solver_skipped_for_before():
    with pytest.raises(ValueError) as caught:
        compare_scores(101, 72)
    assert "before" in str(caught.value)


def test_outside_the_walk_both_guards_must_accept_the_extremes():
    # The cases a transposition defect in either guard would fail.
    assert compare_scores(0, 0) == UNCHANGED
    assert compare_scores(100, 100) == UNCHANGED
    assert compare_scores(0, 100) == MUCH_IMPROVED
    assert compare_scores(100, 0) == MUCH_REGRESSED


def test_outside_the_walk_the_large_change_boundary():
    # The walk stepped from D = 13 to D = 6 over both of these.
    assert compare_scores(50, 60) == MUCH_IMPROVED
    assert compare_scores(50, 59) == IMPROVED
    assert compare_scores(50, 40) == MUCH_REGRESSED
    assert compare_scores(50, 41) == REGRESSED
