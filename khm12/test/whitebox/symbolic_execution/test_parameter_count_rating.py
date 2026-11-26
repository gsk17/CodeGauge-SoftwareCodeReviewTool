"""White-box tests for parameter_count_rating - US14, Kasam (khm12).

Technique: symbolic execution.
Function under test: core.complexity.parameter_count_rating(param_count,
limit).

After US10 (a counting loop) and US12 (a loop needing k=2 unrolling), this is
Kasam's first **loop-free** function, so the tree is finite and complete with
no bounding and the analysis is exact rather than bounded.

**Symbolic inputs.** Two symbolic integers, P for param_count and L for limit.
The tree is a chain of four decisions, so five leaves and five paths:

    Path  Path condition                       Witness   Returns
    P1    P < 0                                (-1, 0)   ValueError, param_count
    P2    P >= 0, L < 1                        (3, 0)    ValueError, limit
    P3    P >= 0, L >= 1, P <= L               (3, 4)    OK
    P4    P >= 0, L >= 1, P > L, P <= 2L       (6, 4)    MANY
    P5    P >= 0, L >= 1, P > 2L               (9, 4)    EXCESSIVE

Five leaves, five paths. The sixth syntactic combination, `P <= L and P > 2L`,
is unsatisfiable for every `L >= 1` and so is an **infeasible path** rather
than an untested one.

### Finding 1 - no valid limit empties a band, which `core.severity` cannot say

Reading the band sizes straight off the path conditions:

    OK          { 0 .. L }          L + 1 values
    MANY        { L+1 .. 2L }       L values
    EXCESSIVE   { 2L+1 .. }         unbounded

`L >= 1` holds on every path that reaches a rating, so the MANY band always
holds at least one value and **all three ratings are reachable at every valid
limit.** At the minimum limit of 1, OK is {0, 1}, MANY is {2}, EXCESSIVE is
{3, ...}.

That is worth proving because the sibling function in this project does not
have the property. `core.severity.classify_severity` bands with
`limit + limit // 2` and `2 * limit`, giving

    MINOR       { L+1 .. L + L//2 }       L // 2 values       empty at L = 1
    MAJOR       { L + L//2 + 1 .. 2L-1 }  L - L//2 - 1 values empty at L = 1, 2

so a project configuring a limit of 1 gets CRITICAL for every finding, and one
configuring 2 can never see MAJOR. US26's analysis found that; `Thresholds`
still permits those limits, and the fix is scheduled for Sprint 2. **This
function needs no such fix**, and the difference is not a matter of care but of
arithmetic: integer halving collapses, doubling does not.

### Finding 2 - the OK band is one wider than MANY, and both comparisons cause it

`b3` and `b4` are both inclusive, which puts L in OK and 2L in MANY. The
result is an asymmetry of exactly one value, whose relative size falls away as
the limit rises:

    L = 1    OK holds 2, MANY holds 1      OK is twice as wide
    L = 4    OK holds 5, MANY holds 4
    L = 20   OK holds 21, MANY holds 20    the difference is noise

So "within the limit" is slightly more generous than "over by no more than the
limit", and at a small limit it is markedly so. Not a defect - inclusivity at
b3 is the documented contract, and the docstring states that a signature
sitting exactly on the limit is acceptable - but it means the two bands are not
the equal halves the phrase "up to twice the limit" suggests.

### Finding 3 - monotonicity in both arguments, provable from the path conditions

Each path condition is an interval in P and a half-plane in L, and the
intervals are ordered. Therefore, writing OK < MANY < EXCESSIVE:

  * **for fixed L, the rating is non-decreasing in P** - adding a parameter
    can never improve a rating;
  * **for fixed P, the rating is non-increasing in L** - raising the limit can
    never worsen a rating.

Both are what a reader expects, and neither is checked by any black-box test
in isolation; they are properties of the family of paths rather than of any
one of them. The random-based suite in
`blackbox/random_testing/test_parameter_count_rating.py` asserts the first as
an invariant over sampled pairs, which is evidence for it; this is a proof of
it.

### Finding 4 - almost every input is EXCESSIVE, so the rating cannot rank bad signatures

Two of the three bands are finite - `L + 1` and `L` values - and the third is
unbounded. Over the whole valid domain, **the rating maps a finite set to OK
and MANY and an infinite set to EXCESSIVE.** At a limit of 4:

    parameter_count_rating(9, 4)    EXCESSIVE
    parameter_count_rating(90, 4)   EXCESSIVE
    parameter_count_rating(900, 4)  EXCESSIVE

The docstring states this is intended, on the ground that once a signature is
excessive the exact count stops being useful. The analysis makes the cost
precise: **the rating is not an ordering on over-limit signatures**, so a
report cannot use it to sort the worst offenders, and `max()` over a file's
ratings tells a reviewer only that at least one signature is beyond 2L.

### Finding 5 - at exactly twice the limit, this function says MANY and `classify_severity` says CRITICAL

A parameter count can be graded twice in this tool - by this function, and by
`core.rules.rule_params`, which routes through `classify_severity`. The two
band structures are not aligned, and the misalignment is provable at one point.

Substituting `P = 2L` into both, for any `L >= 1`:

    parameter_count_rating(2L, L)
        2L <= L     false for L >= 1
        2L <= 2L    TRUE                -> MANY, the kindest over-limit band

    classify_severity(2L, L)
        2L <= L                 false
        2L <= L + L//2          false, since L + L//2 < 2L for all L >= 1
        2L < 2L                 false
                                        -> CRITICAL, the harshest band

So for every valid limit, the count `P = 2L` is simultaneously **MANY and
CRITICAL**. At the default parameter limit of 4 that is a signature of eight
parameters: "over, but not by much" and "twice the limit or worse" at the same
time.

More broadly, the whole MANY band spans all three reachable severities. At
L = 4:

    P = 5, 6    MANY + MINOR
    P = 7       MANY + MAJOR
    P = 8       MANY + CRITICAL
    P >= 9      EXCESSIVE + CRITICAL

**The rating is therefore strictly coarser than the severity and disagrees
with it about where the serious boundary lies** - EXCESSIVE begins at 2L+1,
CRITICAL at 2L. Neither is wrong against its own documented contract; they are
two independent gradings of one measurement, and a report that showed both
would appear to contradict itself for one parameter count in every
configuration.

Recorded as a design finding rather than a defect, and raised for the Sprint 2
review: either the rating is dropped from the report in favour of the severity,
or b4 becomes `param_count < 2 * limit` so the two boundaries coincide. The
second is a one-character change and would make EXCESSIVE and CRITICAL begin
together at 2L, at the cost of shrinking MANY to `L - 1` values - which would
empty it at L = 1 and recreate exactly the defect finding 1 shows this
function currently avoids. **The options are not both free, and that is the
substance of the finding.**

### Finding 6 - a doubly-invalid call reports only the first fault

b1 precedes b2, so `(-1, 0)` raises about `param_count` and never mentions that
the limit is also unusable. A caller correcting the reported fault and
re-running meets a second error rather than a result. Shared with every
validated function in the project; stated here because the witness for P1 above
is deliberately doubly-invalid, so the test pins the order rather than
accidentally depending on it.
"""

import pytest

from core.complexity import (
    RATING_EXCESSIVE,
    RATING_MANY,
    RATING_OK,
    parameter_count_rating,
)
from core.severity import CRITICAL, MAJOR, MINOR, classify_severity


def test_p1_negative_parameter_count():
    # P1: P < 0. The witness is doubly invalid, pinning the order - finding 6.
    with pytest.raises(ValueError) as caught:
        parameter_count_rating(-1, 0)
    assert "param_count" in str(caught.value)
    assert "limit" not in str(caught.value)


def test_p2_limit_below_one():
    # P2: P >= 0, L < 1
    with pytest.raises(ValueError) as caught:
        parameter_count_rating(3, 0)
    assert "limit" in str(caught.value)


def test_p3_within_the_limit():
    # P3: P >= 0, L >= 1, P <= L
    assert parameter_count_rating(3, 4) == RATING_OK


def test_p4_over_but_not_by_much():
    # P4: P >= 0, L >= 1, P > L, P <= 2L
    assert parameter_count_rating(6, 4) == RATING_MANY


def test_p5_beyond_twice_the_limit():
    # P5: P >= 0, L >= 1, P > 2L
    assert parameter_count_rating(9, 4) == RATING_EXCESSIVE


def test_finding_1_every_band_is_reachable_at_every_small_limit():
    # The MANY band holds exactly `limit` values and so is never empty.
    # L = 1: {0,1} {2} {3,...}
    assert parameter_count_rating(1, 1) == RATING_OK
    assert parameter_count_rating(2, 1) == RATING_MANY
    assert parameter_count_rating(3, 1) == RATING_EXCESSIVE
    # L = 2: {0,1,2} {3,4} {5,...}
    assert parameter_count_rating(2, 2) == RATING_OK
    assert parameter_count_rating(3, 2) == RATING_MANY
    assert parameter_count_rating(5, 2) == RATING_EXCESSIVE


def test_finding_1_the_severity_bands_do_collapse_at_the_same_limits():
    # The contrast that makes finding 1 worth stating. At L = 1 every
    # over-limit measurement is CRITICAL; at L = 2 MAJOR is unreachable.
    assert classify_severity(2, 1) == CRITICAL
    assert classify_severity(99, 1) == CRITICAL
    assert classify_severity(3, 2) == MINOR
    assert classify_severity(4, 2) == CRITICAL      # MAJOR is skipped entirely


def test_finding_2_the_ok_band_is_one_wider_than_many():
    # L = 1: OK holds two values, MANY holds one.
    assert parameter_count_rating(0, 1) == RATING_OK
    assert parameter_count_rating(1, 1) == RATING_OK
    assert parameter_count_rating(2, 1) == RATING_MANY
    # the boundaries at L = 4: L in OK, 2L in MANY
    assert parameter_count_rating(4, 4) == RATING_OK
    assert parameter_count_rating(8, 4) == RATING_MANY


def test_finding_3_monotone_non_decreasing_in_the_count():
    # Adding a parameter never improves the rating.
    order = {RATING_OK: 0, RATING_MANY: 1, RATING_EXCESSIVE: 2}
    previous = -1
    for count in range(0, 15):
        current = order[parameter_count_rating(count, 4)]
        assert current >= previous
        previous = current


def test_finding_3_monotone_non_increasing_in_the_limit():
    # Raising the limit never worsens the rating.
    order = {RATING_OK: 0, RATING_MANY: 1, RATING_EXCESSIVE: 2}
    previous = 99
    for limit in range(1, 15):
        current = order[parameter_count_rating(6, limit)]
        assert current <= previous
        previous = current


def test_finding_4_the_rating_cannot_rank_two_bad_signatures():
    # An infinite band. Nine parameters and nine hundred are indistinguishable.
    assert parameter_count_rating(9, 4) == RATING_EXCESSIVE
    assert parameter_count_rating(900, 4) == RATING_EXCESSIVE


def test_finding_5_twice_the_limit_is_many_and_critical_at_once():
    # Provable for every L >= 1; checked across the plausible range.
    for limit in range(1, 11):
        assert parameter_count_rating(2 * limit, limit) == RATING_MANY
        assert classify_severity(2 * limit, limit) == CRITICAL


def test_finding_5_the_many_band_spans_all_three_severities():
    # At L = 4 the single rating MANY covers MINOR, MAJOR and CRITICAL.
    assert parameter_count_rating(6, 4) == RATING_MANY
    assert classify_severity(6, 4) == MINOR
    assert parameter_count_rating(7, 4) == RATING_MANY
    assert classify_severity(7, 4) == MAJOR
    assert parameter_count_rating(8, 4) == RATING_MANY
    assert classify_severity(8, 4) == CRITICAL
