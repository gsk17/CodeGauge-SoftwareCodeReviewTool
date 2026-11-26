"""White-box tests for parameter_count_rating - US14, Kasam (khm12).

Technique: concolic (dynamic symbolic) execution.
Function under test: core.complexity.parameter_count_rating(param_count,
limit).

Seeded with `(3, 4)` - the signature of `classify_line(line)` plus two, against
the project's default parameter limit of 4, so the first run takes the path
almost every real signature in this codebase takes.

Writing P for param_count and L for limit:

    It.  Input    Path  Collected PC                      Negated   Next
    1    (3, 4)   P3    P>=0, L>=1, P<=L                  P<=L      (5, 4)
    2    (5, 4)   P4    P>=0, L>=1, P>L, P<=2L            P<=2L     (9, 4)
    3    (9, 4)   P5    P>=0, L>=1, P>L, P>2L             L>=1      (9, 0)
    4    (9, 0)   P2    P>=0, L<1                         P>=0      (-1, 0)
    5    (-1, 0)  P1    P<0                               none      -

Five iterations, five paths, **100% path coverage with no backtracking.** The
tree is a chain, as in US07 and US04, so negating the most recently evaluated
branch always lands on a fresh leaf. The contrast is with the US12 walk, whose
loop made the tree a bush and cost two backtracks and two manual shrink steps.

### The solver had freedom at every step, and it was used differently each time

Unlike US04 - where negating the total-is-zero branch admitted exactly one
model - every constraint system here has infinitely many solutions. What the
walk did with that freedom:

  * **Iterations 1 and 2 held L fixed at 4 and moved P.** The negated atom
    mentions both variables, so the solver could equally have moved L: from
    `(3, 4)`, negating `P <= L` is satisfied by `(3, 2)` as readily as by
    `(5, 4)`. Moving P was chosen because holding the configuration still and
    varying the measurement is what a reader comparing two adjacent tests
    expects, and because it keeps the five witnesses on one line of the plane.

  * **Iteration 3 could not hold L fixed**, because the negated atom is
    `L >= 1` itself. It had to move L and then check the carried terms were
    still satisfiable: `P > L` and `P > 2L` with `L = 0` reduce to `P > 0`,
    which `P = 9` meets. So the witness `(9, 0)` is the seed's P with an
    invalid limit, and the prefix survived unchanged.

  * **Iteration 4 negated `P >= 0` and discarded everything about L**, because
    `L < 1` belonged to the branch being negated's sibling and is not part of
    the prefix. `(-1, 0)` keeps the previous L only as a convenience; `(-1, 7)`
    reaches the same leaf.

Recorded because "the solver returns a model" hides a real choice, and the
choice determines whether the resulting test suite reads as a coherent
sequence or as five unrelated numbers. Both are 100% path coverage.

### What the walk does not reach

Path coverage is complete, and the walk visits only one point in each of the
three rating bands - all at a limit of 4. Findings 1, 2 and 5 of the symbolic
analysis are all about **how the bands change with L**, and every one of them
is invisible to this walk:

  * finding 1, that no limit empties a band, is a statement over all L;
  * finding 2, that OK is one value wider than MANY, needs both boundaries;
  * finding 5, that `P = 2L` is MANY and CRITICAL at once, needs the point the
    walk skipped - it went from P = 5 straight to P = 9 and never evaluated 8.

**The walk is driven by path novelty, and a different limit is not a different
path.** That is the structural limit of the technique here: the function's
behaviour is parameterised by L, and L appears in every path condition, so no
negation ever demands a new value of it. The cases appended after the walk come
from the solved boundaries instead, and the random-based black-box suite
samples the (P, L) plane for the monotonicity invariants.
"""

import pytest

from core.complexity import (
    RATING_EXCESSIVE,
    RATING_MANY,
    RATING_OK,
    parameter_count_rating,
)
from core.severity import CRITICAL, classify_severity


def test_iteration_1_the_seed_a_typical_signature():
    # Seed (3, 4): P >= 0, L >= 1, P <= L -> P3, OK.
    assert parameter_count_rating(3, 4) == RATING_OK


def test_iteration_2_negating_the_within_limit_test():
    # Negating P <= L under P >= 0 and L >= 1. The solver moved P rather than
    # L; (3, 2) models the same constraint and reaches the same leaf.
    assert parameter_count_rating(5, 4) == RATING_MANY
    assert parameter_count_rating(3, 2) == RATING_MANY


def test_iteration_3_negating_the_doubled_limit_test():
    # Negating P <= 2L with P > L carried forward. Satisfied by any P >= 2L+1.
    assert parameter_count_rating(9, 4) == RATING_EXCESSIVE


def test_iteration_4_negating_a_validation_while_the_prefix_survives():
    # Negating L >= 1 forces L = 0, and the carried P > L and P > 2L collapse
    # to P > 0, which the seed's P already satisfies. The prefix is preserved
    # rather than abandoned, which is why the witness keeps P = 9.
    with pytest.raises(ValueError) as caught:
        parameter_count_rating(9, 0)
    assert "limit" in str(caught.value)


def test_iteration_5_the_last_leaf_discards_the_prefix():
    # Negating P >= 0. Everything about L belonged to the sibling prefix and
    # is dropped, so the limit here is arbitrary - both witnesses are valid
    # models of the one remaining constraint, P < 0.
    with pytest.raises(ValueError) as caught:
        parameter_count_rating(-1, 0)
    assert "param_count" in str(caught.value)
    with pytest.raises(ValueError) as caught:
        parameter_count_rating(-1, 7)
    assert "param_count" in str(caught.value)


# ---------------------------------------------------------------------------
# Not produced by the walk. Each is a point the walk had no reason to visit,
# because varying the limit never opens a new path.
# ---------------------------------------------------------------------------


def test_outside_the_walk_the_boundary_the_walk_stepped_over():
    # The walk went from P = 5 to P = 9 and never evaluated the top of the
    # MANY band. This is the point finding 5 turns on.
    assert parameter_count_rating(8, 4) == RATING_MANY
    assert classify_severity(8, 4) == CRITICAL


def test_outside_the_walk_the_minimum_limit():
    # L = 1 is a different configuration, not a different path, so no
    # negation in the walk asks for it.
    assert parameter_count_rating(1, 1) == RATING_OK
    assert parameter_count_rating(2, 1) == RATING_MANY
    assert parameter_count_rating(3, 1) == RATING_EXCESSIVE


def test_outside_the_walk_an_unusually_generous_limit():
    # A project may configure a high limit. The bands scale with it, so the
    # seed's P = 3 is OK here and so is everything up to 20.
    assert parameter_count_rating(20, 20) == RATING_OK
    assert parameter_count_rating(21, 20) == RATING_MANY
    assert parameter_count_rating(40, 20) == RATING_MANY
    assert parameter_count_rating(41, 20) == RATING_EXCESSIVE
