"""White-box tests for comment_ratio_percent - US04, Gunjan (gsk17).

Technique: concolic (dynamic symbolic) execution.
Function under test: core.line_metrics.comment_ratio_percent(comment_lines,
code_lines).

Seeded with `(28, 142)` - the comment and code counts the scanner produced for
`core/scanner.py` itself at the Sprint 1 close, so the first concrete run is a
real measurement rather than a contrived one.

Writing C for comment_lines, K for code_lines and N for their sum:

    It.  Input      Path  Collected PC              Negated       Next
    1    (28, 142)  P4    C>=0, K>=0, N>0           N>0           (0, 0)
    2    (0, 0)     P3    C>=0, K>=0, N==0          K>=0          (0, -1)
    3    (0, -1)    P2    C>=0, K<0                 C>=0          (-1, -1)
    4    (-1, -1)   P1    C<0                       none          -

Four iterations, four paths, **100% path coverage with no backtracking.** Like
US07 the tree is a chain rather than a bush, so negating the most recently
evaluated branch always lands on a fresh leaf and the stack is never unwound.
Unlike US07, each constraint here is linear arithmetic, so each step is a
solve rather than a construction.

### The step that had no choice

Iteration 1 negates `N > 0` and hands the solver:

    C >= 0  and  K >= 0  and  C + K == 0

This system has **exactly one model**, `(0, 0)`. Every other step in every
concolic walk in this project chose a witness from an infinite solution set,
and the choice was defensible rather than forced - US12's walk needed two
manual shrink steps precisely because the solver's first model was a large
ugly number. Here there is nothing to choose and nothing to shrink.

That is the clearest illustration in these write-ups of what the solver
actually does. It is not generating an example; it is reporting a model of a
constraint system, and when the system pins the model there is no room for the
tool's taste to enter. The seed input is irrelevant to iteration 2's output: a
walk seeded with `(1, 0)` or `(9999, 1)` produces the same `(0, 0)`.

### The step where the solver could have gone wrong

Iteration 2 negates `K >= 0` while carrying `C >= 0` forward and **dropping**
`C + K == 0`, because that term belonged to the branch being negated's
sibling, not to the prefix. A solver that kept it would be handed

    C >= 0  and  K < 0  and  C + K == 0

which is satisfiable - `(1, -1)` models it - and would produce a test that
still reaches P2 and still passes. The walk would look identical and would be
built on a constraint the program never asserted.

The result is the same here only by luck of this function's shape. Recorded
because it is the commonest way a hand-run concolic walk goes quietly wrong:
the prefix is what the *path* asserted, not everything observed along the way.
The witness chosen below, `(0, -1)`, satisfies the correct prefix and not the
incorrect one, so the distinction is visible in the test data.

### What the walk does not reach

Path coverage is complete, and the walk still says nothing about the division
leaf beyond the single point `(28, 142)`. P4's path condition admits every
input with a positive total, and findings 3 to 5 of the symbolic analysis are
all *within* P4 - the solved boundaries where the returned number changes.
**Concolic testing explores paths, and the interesting behaviour of this
function is inside one path.**

That is the honest limit of the technique on arithmetic leaves, and it is why
the random-based black-box suite exists alongside it: the invariant tests in
`blackbox/random_testing/` sample P4 thousands of times, which is the coverage
the walk below structurally cannot provide. The three cases appended after the
walk are taken from the solved boundaries rather than from any negation.
"""

import pytest

from core.line_metrics import comment_ratio_percent


def test_iteration_1_the_seed_a_real_measurement():
    # Seed (28, 142): C >= 0, K >= 0, N > 0 -> P4, the division leaf.
    # 2800 // 170 == 16, the comment density of core/scanner.py.
    assert comment_ratio_percent(28, 142) == 16


def test_iteration_2_the_forced_model():
    # Negating N > 0 under C >= 0 and K >= 0 admits exactly one input.
    # No seed produces any other answer at this step.
    assert comment_ratio_percent(0, 0) == 0


def test_iteration_3_the_prefix_must_drop_the_sibling_term():
    # Negating K >= 0 carries C >= 0 forward and drops N == 0. The witness
    # satisfies C >= 0 and K < 0 and NOT C + K == 0, so it distinguishes the
    # correct prefix from the plausible wrong one.
    with pytest.raises(ValueError) as caught:
        comment_ratio_percent(0, -1)
    assert "code_lines" in str(caught.value)


def test_iteration_3_the_wrong_prefix_would_also_have_passed():
    # (1, -1) models the incorrect prefix - C >= 0, K < 0, C + K == 0 - and
    # reaches the same leaf with the same message. A walk built on it would
    # look correct. Pinned so the two are known to be indistinguishable by
    # outcome and distinguishable only by the constraint they were derived
    # from.
    with pytest.raises(ValueError) as caught:
        comment_ratio_percent(1, -1)
    assert "code_lines" in str(caught.value)


def test_iteration_4_the_last_leaf():
    # Negating C >= 0. The remaining constraint is C < 0 alone, since K's
    # term belonged to the negated branch's prefix sibling and is discarded.
    with pytest.raises(ValueError) as caught:
        comment_ratio_percent(-1, -1)
    assert "comment_lines" in str(caught.value)


# ---------------------------------------------------------------------------
# Not produced by the walk. These are the boundaries solved in the symbolic
# analysis, all of which lie inside P4 and are therefore invisible to path
# exploration.
# ---------------------------------------------------------------------------


def test_outside_the_walk_the_boundary_at_which_zero_stops():
    # result == 0  <=>  99 * C < K
    assert comment_ratio_percent(1, 100) == 0
    assert comment_ratio_percent(1, 99) == 1


def test_outside_the_walk_the_boundary_at_which_one_hundred_becomes_reachable():
    # result == 100  <=>  K == 0
    assert comment_ratio_percent(50, 0) == 100
    assert comment_ratio_percent(50, 1) == 98


def test_outside_the_walk_the_floor_never_rounds_up():
    # Half a point either side of 50 on the same path as the seed.
    assert comment_ratio_percent(1, 2) == 33      # 33.33
    assert comment_ratio_percent(2, 3) == 40      # 40.00
    assert comment_ratio_percent(2, 1) == 66      # 66.67, not 67
