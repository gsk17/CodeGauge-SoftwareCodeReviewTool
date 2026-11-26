"""White-box tests for rule_params - US22, Saaket (ssl21).

Technique: concolic (dynamic symbolic) execution, across a call boundary.
Function under test: core.rules.rule_params(param_count, limit, line).

Seeded with `(7, 5, 12)` - seven parameters against the project's default
parameter limit of five, taken from the worst signature in the Sprint 0
prototype before it was discarded. The seed deliberately lands on an inlined
leaf rather than on a leaf of `rule_params` itself, so the walk begins inside
the callee and climbs outward.

Writing P for param_count and L for limit, and marking which function each
negated branch belongs to:

    It.  Input      Path  Collected PC                   Negated         Next
    1    (7, 5)     MINOR P>=0, L>=1, P>L, P<=L+L//2     callee b3       (8, 5)
    2    (8, 5)     MAJOR P>=0, L>=1, P>L, P<2L          callee b4       (10, 5)
    3    (10, 5)    CRIT  P>=0, L>=1, P>=2L              caller b3       (3, 5)
    4    (3, 5)     None  P>=0, L>=1, P<=L               caller b2       (3, 0)
    5    (3, 0)     raise P>=0, L<1                      caller b1       (-1, 0)
    6    (-1, 0)    raise P<0                            none            -

Six iterations, six paths, **100% coverage of the feasible paths** of the
inlined program. One backtrack, at iteration 3: the two deepest branches
belong to the callee and are exhausted after it, so the walk unwinds to the
caller's own b3 to continue.

### The walk crosses a call boundary without noticing, which is the point

Iterations 1 and 2 negate branches in `core/severity.py`. Iterations 3 to 5
negate branches in `core/rules.py`. **Nothing in the procedure distinguishes
them.** The path condition is a conjunction of atoms over P and L, and which
file an atom came from is not recorded in it, because every atom is expressed
in the caller's variables after substitution.

That is what makes inlining the right treatment here rather than a convenient
simplification: `classify_severity(P, L)` passes the caller's symbols straight
through with no transformation, so the substitution is the identity and the
callee's constraints are already in terms the solver can combine with the
caller's. A callee that computed a new value from its arguments - a hash, a
lookup, anything not linear - would break that, and the walk would have to
treat the call as an opaque operation and stop exploring at it.

### Three negations the solver was never offered

The inlined tree has seven syntactic leaves and the walk reached six. The
missing one is the callee's INFO leaf, and the walk never proposed an input
for it because the constraint

    P > L  and  P <= L

is unsatisfiable. A real solver returns UNSAT, the leaf is marked infeasible
and the walk moves on. **A hand-run walk gets no such signal**: an
unsatisfiable negation and an exhausted frontier look the same from the
outside, which is how an infeasible path gets quietly recorded as "not yet
reached" and then as "uncovered".

The same applies to the callee's two validation leaves, which the walk also
never offered. Three leaves, three UNSAT results, and only the symbolic
analysis distinguishes them from a gap in the testing. That is the honest
argument for doing the symbolic work alongside the concolic walk rather than
instead of it: the walk tells you which paths you reached, and only the
algebra tells you whether the rest exist.

### What the walk does not reach

All six feasible paths, and only at L = 5. Every finding in the symbolic
analysis about **small limits** - that MAJOR is empty at L = 2, that CRITICAL
is the only band at L = 1, that 3 and not 2 is the smallest safe limit - is
invisible here, for the same reason as in US14: a different limit is a
different band *width*, not a different path. No negation in the walk ever
demands a new L except iteration 5, which demands an invalid one.

So the walk cannot find the defect the retrospective is about to half-fix. It
was found by solving the band expressions, and the cases that pin it are
appended below rather than derived from any negation.
"""

import pytest

from core.rules import rule_params
from core.severity import CRITICAL, INFO, MAJOR, MINOR, classify_severity


def test_iteration_1_the_seed_lands_inside_the_callee():
    # Seed (7, 5, 12): P > L and P <= L + L//2, so 5 < 7 <= 7 - the top of
    # the MINOR band at this limit, reached through the caller's fourth leaf.
    issue = rule_params(7, 5, 12)
    assert issue.severity == MINOR
    assert "7 parameters exceeds limit 5" in issue.message


def test_iteration_2_negating_a_branch_in_the_other_module():
    # Negating the callee's MINOR test under the caller's prefix. MAJOR is
    # { 8, 9 } at this limit.
    assert rule_params(8, 5, 12).severity == MAJOR
    assert rule_params(9, 5, 12).severity == MAJOR


def test_iteration_3_negating_the_last_callee_branch():
    # Negating P < 2L leaves P >= 10, the unbounded band. The callee's
    # branches are now exhausted, so the walk must unwind to the caller.
    assert rule_params(10, 5, 12).severity == CRITICAL
    assert rule_params(500, 5, 12).severity == CRITICAL


def test_iteration_4_the_backtrack_into_the_caller():
    # Negating the caller's own b3. This is the first iteration whose witness
    # does not enter core.severity at all.
    assert rule_params(3, 5, 12) is None


def test_iteration_5_negating_the_limit_validation():
    # Negating L >= 1. The carried P <= L becomes P <= 0, which P = 3 does
    # not satisfy - so unlike the US14 walk, the prefix does NOT survive here
    # and the solver had to abandon it. Any P >= 0 reaches this leaf.
    with pytest.raises(ValueError) as caught:
        rule_params(3, 0, 12)
    assert "limit" in str(caught.value)
    with pytest.raises(ValueError):
        rule_params(0, 0, 12)


def test_iteration_6_the_last_leaf():
    with pytest.raises(ValueError) as caught:
        rule_params(-1, 0, 12)
    assert "param_count" in str(caught.value)


def test_the_unsatisfiable_negation_the_walk_never_proposed():
    # The callee's INFO leaf. No input reaches it through a rule, so there is
    # nothing to assert about rule_params here except the absence - and the
    # leaf itself is reachable, just not from here.
    for count in range(6, 60):
        assert rule_params(count, 5, 12).severity != INFO
    assert classify_severity(4, 5) == INFO


# ---------------------------------------------------------------------------
# Not produced by the walk. The small-limit collapse, which path exploration
# cannot find because a narrower band is not a new path.
# ---------------------------------------------------------------------------


def test_outside_the_walk_a_limit_of_one_gives_only_critical():
    assert rule_params(2, 1, 1).severity == CRITICAL
    assert rule_params(3, 1, 1).severity == CRITICAL
    assert rule_params(40, 1, 1).severity == CRITICAL


def test_outside_the_walk_a_limit_of_two_skips_major():
    # The configuration the agreed validation fix would still permit.
    assert rule_params(3, 2, 1).severity == MINOR
    assert rule_params(4, 2, 1).severity == CRITICAL
    for count in range(3, 40):
        assert rule_params(count, 2, 1).severity != MAJOR


def test_outside_the_walk_a_limit_of_three_is_the_first_sound_one():
    assert rule_params(4, 3, 1).severity == MINOR
    assert rule_params(5, 3, 1).severity == MAJOR
    assert rule_params(6, 3, 1).severity == CRITICAL
