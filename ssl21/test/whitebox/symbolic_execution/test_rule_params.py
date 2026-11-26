"""White-box tests for rule_params - US22, Saaket (ssl21).

Technique: symbolic execution, inter-procedurally by inlining.
Function under test: core.rules.rule_params(param_count, limit, line).

The third rule of the shape US19 established, and the first analysis in this
project to treat that shape as a **contract** rather than a coincidence. The
interesting results below are properties of the shape, so they hold for
`rule_complexity` and `rule_nesting` as well, and the third instance is what
makes them worth proving once instead of observing three times.

**Symbolic inputs.** Two symbolic integers, P for param_count and L for limit.
`line` is carried into the Issue untouched and is never branched on, so it does
not appear in any path condition and is not symbolic.

### The caller alone

    Path  Path condition             Witness   Returns
    C1    P < 0                      (-1, 0)   ValueError, param_count
    C2    P >= 0, L < 1              (3, 0)    ValueError, limit
    C3    P >= 0, L >= 1, P <= L     (3, 4)    None
    C4    P >= 0, L >= 1, P > L      (6, 4)    Issue(...)

Four leaves. C4 is not a leaf of the program, only of this function: it calls
`classify_severity(P, L)`, which branches four more times.

### Inlining the callee into C4

`classify_severity(actual, limit)` has five leaves of its own. Substituting
`actual = P`, `limit = L` and conjoining C4's path condition:

    Leaf  Callee condition           Conjoined with C4            Satisfiable?
    S1    P < 0                      P >= 0 and P < 0             NO
    S2    P >= 0, L < 1              L >= 1 and L < 1             NO
    S3    P <= L                     P > L and P <= L             NO
    S4    L < P <= L + L//2          -                            yes, MINOR
    S5    L + L//2 < P < 2L          -                            yes, MAJOR
    S6    P >= 2L                    -                            yes, CRITICAL

So the inlined tree has **seven syntactic leaves and six feasible paths**:

    Path  Full path condition                        Witness   Returns
    P1    P < 0                                      (-1, 0)   raises
    P2    P >= 0, L < 1                              (3, 0)    raises
    P3    P >= 0, L >= 1, P <= L                     (3, 4)    None
    P4    P > L, P <= L + L//2                       (5, 4)    MINOR
    P5    P > L + L//2, P < 2L                       (7, 4)    MAJOR
    P6    P >= 2L                                    (8, 4)    CRITICAL

### Finding 1 - the callee's own validation is dead at every rule call site

S1, S2 and S3 are unsatisfiable, so **three of the callee's five leaves cannot
be reached from any rule.** The caller's b1, b2 and b3 establish precisely what
the callee's first three decisions re-check.

That is not an argument for deleting them. `classify_severity` is a public
function of `core.severity` and is called directly by its own tests and
potentially by future code; its validation is dead *relative to this caller*,
not dead in the module. The useful conclusion is the opposite one: **the
duplicated checks are the reason the inter-procedural analysis is this simple.**
Because the callee re-asserts the caller's guarantees, the conjunction either
collapses to the caller's prefix or becomes unsatisfiable, and no new constraint
on P or L is introduced by the call at all.

With three rules in the module, that is **nine infeasible leaves project-wide**
that no test of any rule can reach. `coverage` nevertheless reports
`core/severity.py` at 100%, because US26's own tests reach those lines
directly. Coverage is a statement about lines executed by the suite, not about
behaviour reachable through a given path - and these nine are the clearest
example of the gap in this project.

### Finding 2 - no rule in this tool can emit INFO, and now it is a theorem

The inlined condition for INFO is S3 conjoined with C4:

    P > L  and  P <= L

Unsatisfiable, trivially and for every L. The same substitution works for
`rule_complexity` (CC for P) and `rule_nesting` (depth for P), because all
three guard with `measurement <= limit -> return None` before calling.
Therefore:

> **For every `rule_*` function in `core.rules`, the INFO severity is
> unreachable.** An Issue produced by this tool carries MINOR, MAJOR or
> CRITICAL, never INFO.

US19 observed it for one rule and US20 for a second. The third instance makes
it a property of the shape, and the shape is now documented in the
`rule_params` docstring as a contract that any future rule must also satisfy -
which means any future rule inherits this consequence too.

The cost is that a reader of `core/severity.py` alone would conclude four
severities can appear in a report. INFO is defined, exported, and listed in
`RANK_ORDER`, which `combine_severities` reduces along. It is reachable only by
calling `classify_severity` directly, which nothing in the production path
does. A reviewer looking for the INFO findings in a report will not find any,
and the absence is structural rather than a sign of clean code.

### Finding 3 - the severity bands collapse at small limits, and the agreed fix does not go far enough

Band membership, read off the inlined path conditions:

    MINOR       { L+1 .. L + L//2 }        L // 2 values
    MAJOR       { L + L//2 + 1 .. 2L-1 }   L - L//2 - 1 values
    CRITICAL    { 2L .. }                  unbounded

Evaluating for small L:

    L    MINOR        MAJOR        CRITICAL     reachable severities
    1    { }          { }          { 2, ... }   CRITICAL only
    2    { 3 }        { }          { 4, ... }   MINOR, CRITICAL
    3    { 4 }        { 5 }        { 6, ... }   all three
    4    { 5, 6 }     { 7 }        { 8, ... }   all three
    5    { 6, 7 }     { 8, 9 }     { 10, ... }  all three

**At a limit of 1 every finding in the report is CRITICAL. At a limit of 2,
MAJOR is unreachable.** Both are configurations `Thresholds.validate` presently
permits.

The Sprint 1 retrospective agreed to tighten `Thresholds.validate` to **reject
limits below 2**, with the fix owned by Saaket and scheduled for Friday 27
November. This analysis says that fix is one short: **the smallest limit at
which all three reachable severities are non-empty is 3**, not 2. A limit of 2
passes the agreed validation and still produces a report in which the MAJOR
band is empty by construction.

Raised for the Sprint 2 stand-up before the fix is written, because it changes
the constant and not the design. The counter-argument to be weighed there is
that a limit of 2 is a legitimate configuration for a nesting depth - a project
insisting on at most two levels of indentation is strict, not misconfigured -
and forbidding it to protect a band from being empty refuses a reasonable
setting to fix a reporting artefact. The alternative is to change the banding
arithmetic rather than the validation, which affects every rule and every
existing test. **The decision belongs to the team, not to this file**; what the
analysis contributes is that 2 and 3 are different answers and the difference
was not visible when the retrospective chose 2.

### Finding 4 - the three rules are provably interchangeable, so the cross-rule test is not redundant

After renaming the measurement variable, the path conditions of
`rule_complexity`, `rule_nesting` and `rule_params` are **identical**, and so
are the inlined severity conditions. The three functions differ only in:

  * the code constant carried into the Issue (`CC001`, `NEST001`, `PAR001`);
  * the wording of the message;
  * the variable name in the validation messages.

Nothing else. The duplication is deliberate - the `rule_nesting` docstring
explains that a shared helper would put two members' marks inside one function
- and the analysis shows exactly what the duplication risks: three independent
copies of a banding decision that must stay in agreement.

**A per-rule test cannot detect a divergence**, because each rule tested alone
is self-consistent whatever bands it uses. The only test that would fail is one
asserting the three produce *equal severities for equal numbers*, which is why
such a test exists in all three members' black-box packages and is reproduced
below over the whole small-limit range.

### Finding 5 - `line` is absent from every path condition, and that is the only reason the analysis is two-dimensional

The function takes three arguments and branches on two. `line` is copied into
the Issue and never compared, so it contributes no atom to any path condition
and the tree is the same for every value of it, including nonsensical ones.

That is worth stating because it is a deliberate design decision with a cost:
`rule_params(9, 4, -1)` returns an Issue reporting a finding at line -1. No
validation rejects it. The rule trusts its caller on line numbering, on the
ground that the scanner owns it and a rule that second-guessed it could reject
a valid report. The analysis confirms there is no path on which a bad line
number is caught, so if that trust is ever misplaced the error surfaces in the
formatter, not here.
"""

import pytest

from core.rules import (
    CODE_COMPLEXITY,
    CODE_NESTING,
    CODE_PARAMS,
    rule_complexity,
    rule_nesting,
    rule_params,
)
from core.severity import CRITICAL, INFO, MAJOR, MINOR, classify_severity


def test_p1_negative_parameter_count():
    # P1: P < 0, doubly invalid witness, pinning the validation order
    with pytest.raises(ValueError) as caught:
        rule_params(-1, 0, 12)
    assert "param_count" in str(caught.value)


def test_p2_limit_below_one():
    # P2: P >= 0, L < 1
    with pytest.raises(ValueError) as caught:
        rule_params(3, 0, 12)
    assert "limit" in str(caught.value)


def test_p3_within_the_limit():
    # P3: P >= 0, L >= 1, P <= L
    assert rule_params(3, 4, 12) is None


def test_p4_minor_the_first_inlined_leaf():
    # P4: P > L, P <= L + L//2 -> 4 < 5 <= 6
    assert rule_params(5, 4, 12).severity == MINOR


def test_p5_major_the_second_inlined_leaf():
    # P5: P > L + L//2, P < 2L -> 6 < 7 < 8. A one-value band at this limit.
    assert rule_params(7, 4, 12).severity == MAJOR


def test_p6_critical_the_third_inlined_leaf():
    # P6: P >= 2L
    assert rule_params(8, 4, 12).severity == CRITICAL


def test_finding_1_the_callees_validation_is_unreachable_from_here():
    # S1 and S2 are unsatisfiable under C4, so no input makes classify_severity
    # raise when it is called from rule_params. The rule raises first, and the
    # message names the rule's own parameter rather than the callee's.
    with pytest.raises(ValueError) as caught:
        rule_params(-5, 4, 1)
    assert "param_count" in str(caught.value)
    assert "actual" not in str(caught.value)
    # and the callee can still raise when called directly, which is why its
    # validation is dead relative to this caller and not dead in the module
    with pytest.raises(ValueError) as caught:
        classify_severity(-5, 4)
    assert "actual" in str(caught.value)


def test_finding_2_info_is_unreachable_through_this_rule():
    # The inlined condition for INFO is P > L and P <= L.
    for limit in range(1, 8):
        for count in range(limit + 1, limit * 4 + 6):
            assert rule_params(count, limit, 1).severity != INFO


def test_finding_2_info_is_unreachable_through_any_rule():
    # The same substitution for the other two rules of the shape.
    for limit in range(1, 8):
        for measurement in range(limit + 1, limit * 4 + 6):
            assert rule_complexity(measurement, limit, 1).severity != INFO
            assert rule_nesting(measurement, limit, 1).severity != INFO


def test_finding_2_info_is_reachable_only_by_calling_the_callee_directly():
    # It is not dead code in core.severity - just unreachable through a rule.
    assert classify_severity(3, 4) == INFO
    assert classify_severity(4, 4) == INFO


def test_finding_3_at_a_limit_of_one_every_finding_is_critical():
    for count in range(2, 30):
        assert rule_params(count, 1, 1).severity == CRITICAL


def test_finding_3_at_a_limit_of_two_major_is_unreachable():
    seen = set()
    for count in range(3, 60):
        seen.add(rule_params(count, 2, 1).severity)
    assert seen == {MINOR, CRITICAL}
    assert MAJOR not in seen


def test_finding_3_three_is_the_smallest_limit_with_all_three_bands():
    # The point the retrospective's choice of 2 misses.
    def bands(limit):
        return set(rule_params(c, limit, 1).severity
                   for c in range(limit + 1, limit * 4 + 6))

    assert bands(1) == {CRITICAL}
    assert bands(2) == {MINOR, CRITICAL}
    assert bands(3) == {MINOR, MAJOR, CRITICAL}
    assert bands(4) == {MINOR, MAJOR, CRITICAL}
    assert bands(5) == {MINOR, MAJOR, CRITICAL}


def test_finding_4_the_three_rules_band_identically():
    # The only test in the project that would fail if one rule re-implemented
    # the severity bands. Codes differ, severities must not.
    for limit in range(1, 9):
        for measurement in range(limit + 1, limit * 3 + 4):
            params = rule_params(measurement, limit, 1)
            complexity = rule_complexity(measurement, limit, 1)
            nesting = rule_nesting(measurement, limit, 1)
            assert params.severity == complexity.severity == nesting.severity
            assert params.code == CODE_PARAMS
            assert complexity.code == CODE_COMPLEXITY
            assert nesting.code == CODE_NESTING


def test_finding_4_the_three_rules_agree_on_the_clean_case_too():
    for limit in range(1, 9):
        for measurement in range(0, limit + 1):
            assert rule_params(measurement, limit, 1) is None
            assert rule_complexity(measurement, limit, 1) is None
            assert rule_nesting(measurement, limit, 1) is None


def test_finding_5_the_line_number_is_never_branched_on():
    # No path condition mentions it, so no value of it is rejected - including
    # values the scanner could never produce.
    assert rule_params(9, 4, 0).line == 0
    assert rule_params(9, 4, -1).line == -1
    assert rule_params(9, 4, 10 ** 9).line == 10 ** 9
    # and it does not affect the severity, the code or the message
    first = rule_params(9, 4, 1)
    second = rule_params(9, 4, 999)
    assert first.severity == second.severity
    assert first.code == second.code
    assert first.message == second.message
