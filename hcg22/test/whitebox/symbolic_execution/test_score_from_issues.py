"""White-box tests for score_from_issues - US29, Harshita (hcg22).

Technique: symbolic execution.
Function under test: core.scoring.score_from_issues(critical, major, minor, info).

Symbolic inputs C, M, N, I. The validation loop runs a fixed four times, so it
needs no bounding - the number of iterations is a property of the signature, not
of the data. Every constraint is linear in the four variables.

Writing `P = 15C + 8M + 3N + I` for the penalty and `R = 100 - P` for the raw
score:

    Path  Path condition                                Witness        Returns
    P1    C < 0                                         (-1,0,0,0)     ValueError
    P2    C >= 0, M < 0                                 (0,-1,0,0)     ValueError
    P3    C,M >= 0, N < 0                               (0,0,-1,0)     ValueError
    P4    C,M,N >= 0, I < 0                             (0,0,0,-1)     ValueError
    P5    all >= 0, C >= 3, R > 40                      (3,0,0,0)      40
    P6    all >= 0, C >= 3, R <= 40, R < 0              (10,0,0,0)     0
    P7    all >= 0, C >= 3, R <= 40, R >= 0             (5,0,0,0)      R
    P8    all >= 0, C < 3, R < 0                        (0,13,0,0)     0
    P9    all >= 0, C < 3, R >= 0                       (0,0,1,0)      97

Nine paths.

**Finding 1 - the floor is unreachable after the cap fires.** On P5 the score
is assigned 40 before the floor is tested, and 40 is not below 0. So the
sub-path "cap fires, then floor fires" has no input at all. The tree has nine
leaves rather than ten, and the missing one is a genuine infeasible path:

    score = 40   and   score < 0        unsatisfiable

**Finding 2 - the cap can only ever fire at exactly three critical issues.**
This is the result worth having, and it is not obvious from reading the code.

P5 requires both `C >= 3` and `R > 40`. Substituting:

    R > 40
    100 - 15C - (8M + 3N + I) > 40
    15C + (8M + 3N + I) < 60

With `C >= 3` that gives `45 + (8M + 3N + I) < 60`, so `8M + 3N + I < 15`.
With `C >= 4` it gives `60 + (8M + 3N + I) < 60`, so `8M + 3N + I < 0` -
**unsatisfiable**, because all three counts are non-negative on this path.

Therefore **P5 requires `C == 3` exactly**, and additionally that the other
three severities contribute a penalty below 15.

The reason is arithmetic rather than intentional: four critical issues cost
`4 x 15 = 60`, which lands the raw score on exactly 40 - the cap value itself.
Above three criticals the weighted penalty has already done everything the cap
was meant to do.

**So the cap is very nearly vestigial.** It alters the result only for a file
with exactly three critical issues and fewer than 15 penalty points of other
findings: `(3,0,0,0)` through `(3,0,0,14)`, `(3,1,0,0)` through `(3,1,0,6)`, and
a handful of others. For every other input the floor and the weights alone give
the same answer.

That is a finding about the *specification*, not the implementation. The
implementation satisfies the spec exactly. Whether a rule that fires on one
value of C is worth having is a question for the Sprint 1 review, and it is
recorded in the README's known limitations.
"""

import pytest

from core.scoring import score_from_issues


def _raw(critical, major, minor, info):
    """The uncapped, unfloored score - the symbolic expression R, evaluated."""
    return 100 - (15 * critical + 8 * major + 3 * minor + info)


# --- P1 to P4: the four validation paths ---------------------------------------

def test_p1_critical_negative():
    # PC: C < 0. Rejected before M, N or I is examined.
    with pytest.raises(ValueError):
        score_from_issues(-1, 0, 0, 0)


def test_p2_major_negative():
    # PC: C >= 0 and M < 0. Reachable only because validation is a full pass.
    with pytest.raises(ValueError):
        score_from_issues(0, -1, 0, 0)


def test_p3_minor_negative():
    # PC: C, M >= 0 and N < 0
    with pytest.raises(ValueError):
        score_from_issues(0, 0, -1, 0)


def test_p4_info_negative():
    # PC: C, M, N >= 0 and I < 0 - the deepest validation path
    with pytest.raises(ValueError):
        score_from_issues(0, 0, 0, -1)


# --- P5: the cap fires ---------------------------------------------------------

def test_p5_the_cap_fires():
    # PC: all >= 0, C >= 3, R > 40. Witness (3,0,0,0): R = 55.
    assert _raw(3, 0, 0, 0) == 55
    assert score_from_issues(3, 0, 0, 0) == 40


# --- P6, P7: the cap applies but does not lower the score ----------------------

def test_p6_capped_then_floored():
    # PC: all >= 0, C >= 3, R <= 40, R < 0. Witness (10,0,0,0): R = -50.
    assert _raw(10, 0, 0, 0) == -50
    assert score_from_issues(10, 0, 0, 0) == 0


def test_p7_capped_but_already_below_the_cap():
    # PC: all >= 0, C >= 3, 0 <= R <= 40. Witness (5,0,0,0): R = 25.
    assert _raw(5, 0, 0, 0) == 25
    assert score_from_issues(5, 0, 0, 0) == 25


def test_p7_at_the_boundary_where_r_equals_the_cap():
    # The boundary between P5 and P7 is R = 40, and (4,0,0,0) sits exactly on
    # it: R = 40 is not *above* 40, so b3 is false and the cap does not fire.
    # The returned value is R, which happens to equal the cap.
    assert _raw(4, 0, 0, 0) == 40
    assert score_from_issues(4, 0, 0, 0) == 40


# --- P8, P9: the cap does not apply --------------------------------------------

def test_p8_floored_without_the_cap():
    # PC: all >= 0, C < 3, R < 0. Witness (0,13,0,0): R = -4.
    assert _raw(0, 13, 0, 0) == -4
    assert score_from_issues(0, 13, 0, 0) == 0


def test_p9_the_ordinary_path():
    # PC: all >= 0, C < 3, R >= 0. Witness (0,0,1,0): R = 97.
    assert score_from_issues(0, 0, 1, 0) == 97


def test_p9_at_the_floor_boundary():
    # R exactly 0 on the uncapped branch: 100 - (96 + 3 + 1) = 0
    assert _raw(0, 12, 1, 1) == 0
    assert score_from_issues(0, 12, 1, 1) == 0


# --- Finding 1: the floor cannot fire after the cap ----------------------------

def test_finding_1_the_cap_path_never_reaches_the_floor():
    """`score = 40 and score < 0` is unsatisfiable, so no input takes both.

    Checked by showing that every input on which the cap fires returns exactly
    40 - never 0. Swept over the whole region where P5 is satisfiable, which
    Finding 2 shows is C = 3 with the other penalties below 15.
    """
    capped = 0
    for major in range(0, 2):
        for minor in range(0, 5):
            for info in range(0, 15):
                if 8 * major + 3 * minor + info < 15:
                    assert score_from_issues(3, major, minor, info) == 40
                    capped = capped + 1
    assert capped > 0, "the sweep must actually reach the cap"


# --- Finding 2: the cap fires only at exactly three criticals ------------------

def test_finding_2_the_cap_never_fires_above_three_criticals():
    """`15C + rest < 60` with `C >= 4` needs `rest < 0`, which is impossible.

    So for four or more critical issues the raw score is already at or below
    the cap, and the cap changes nothing. Checked by confirming the result
    equals the raw score (or the floor) for every C from 4 upwards.
    """
    for critical in range(4, 20):
        for major in range(0, 4):
            raw = _raw(critical, major, 0, 0)
            expected = raw if raw > 0 else 0
            assert score_from_issues(critical, major, 0, 0) == expected


def test_finding_2_four_criticals_land_on_exactly_the_cap_value():
    """The arithmetic coincidence behind Finding 2: 4 x 15 = 60, and
    100 - 60 = 40, which is the cap value itself. That is why the cap has
    nothing left to do above three criticals."""
    assert 4 * 15 == 60
    assert _raw(4, 0, 0, 0) == 40


def test_finding_2_the_cap_changes_the_answer_for_a_narrow_set_of_inputs():
    """The cap alters the result only where C = 3 and the other penalties
    total below 15. Everywhere else the weights and the floor alone would give
    the same answer. Demonstrated by counting, over a bounded region, the
    inputs where capped and uncapped results differ."""
    differing = []
    for critical in range(0, 8):
        for major in range(0, 4):
            for minor in range(0, 6):
                for info in range(0, 6):
                    raw = _raw(critical, major, minor, info)
                    without_cap = raw if raw > 0 else 0
                    actual = score_from_issues(critical, major, minor, info)
                    if actual != without_cap:
                        differing.append((critical, major, minor, info))
    assert differing, "the cap must change something, or it is dead code"
    # every input where the cap matters has exactly three critical issues
    assert all(counts[0] == 3 for counts in differing)
