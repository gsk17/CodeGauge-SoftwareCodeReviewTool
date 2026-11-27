"""Black-box tests for rule_length - US21, Saaket (ssl21).

Technique: equivalence partitioning with boundary value analysis.
Function under test: core.rules.rule_length(loc, limit, line).

The fourth rule in `core/rules.py`, and the fourth built to the shape US19
established: `None` when the measurement is within its limit, an `Issue` when it
is over, and the severity delegated to `classify_severity`.

    R1  well within the limit     (20, 50, 7)   -> None
    R2  exactly on the limit      (50, 50, 7)   -> None
    R3  one line over             (51, 50, 7)   -> Issue, MINOR
    R4  half again over           (75, 50, 7)   -> Issue, MINOR
    R5  approaching twice over    (90, 50, 7)   -> Issue, MAJOR
    R6  twice the limit or more   (100, 50, 7)  -> Issue, CRITICAL
    R7  an empty function         (0, 50, 7)    -> None
    R8  loc negative                            -> ValueError
    R9  limit below 1                           -> ValueError

**By the fourth instance the shape is a contract, not a coincidence**, and US22
wrote it into the module docstring. These tests check this rule against that
contract rather than re-deriving it: the partitions above are the same
partitions as US19's, US20's and US22's with the measurement renamed, and the
test at the end of this file asserts that all four rules produce identical
severities for identical numbers while carrying different codes. That is the
only test that would fail if one of the four re-implemented the bands.

**R7 is the partition worth arguing about.** A function with zero lines of code
is not over any limit, so this rule returns `None` - and a zero-line function
is a real defect, just not this rule's defect. Reporting it here would mean this
rule fired on both too much code and no code, which makes the finding's message
("function is 0 lines, exceeds limit 50") nonsense. US15
`function_length_rating` has a `SHORT` band for exactly this case. **The rule
reports one thing and the rating describes the spectrum**, and R7 is where that
division of labour becomes visible.

**R3 to R6 are severity partitions, not rule partitions.** All four take the
same path through `rule_length` and differ only inside `classify_severity`. They
are listed separately because a reader of the report cares which severity
appears, and grouped in the comments because a reader of this function should
know the rule does not decide it.

**No partition produces INFO.** Reaching `classify_severity` requires
`loc > limit`, and INFO requires `loc <= limit`, so the combination is
impossible. US22 proved this for the whole rule shape; the test at the bottom
confirms the fourth rule inherits it.
"""

import pytest

from core.rules import (
    CODE_COMPLEXITY,
    CODE_LENGTH,
    CODE_NESTING,
    CODE_PARAMS,
    rule_complexity,
    rule_length,
    rule_nesting,
    rule_params,
)
from core.severity import CRITICAL, INFO, MAJOR, MINOR


def test_r1_well_within_the_limit():
    assert rule_length(20, 50, 7) is None


def test_r2_exactly_on_the_limit_is_acceptable():
    # the limit is inclusive, as in every other rule and rating in the project
    assert rule_length(50, 50, 7) is None


def test_r3_one_line_over_raises_a_minor_issue():
    issue = rule_length(51, 50, 7)
    assert issue is not None
    assert issue.code == CODE_LENGTH
    assert issue.severity == MINOR
    assert issue.line == 7


def test_r4_half_again_over_is_still_minor():
    # MINOR runs to limit + limit // 2, which is 75 here
    assert rule_length(75, 50, 7).severity == MINOR


def test_r5_approaching_twice_over_is_major():
    assert rule_length(76, 50, 7).severity == MAJOR
    assert rule_length(90, 50, 7).severity == MAJOR
    assert rule_length(99, 50, 7).severity == MAJOR


def test_r6_twice_the_limit_or_more_is_critical():
    assert rule_length(100, 50, 7).severity == CRITICAL
    assert rule_length(400, 50, 7).severity == CRITICAL


def test_r7_an_empty_function_is_not_this_rules_problem():
    # 0 lines is not over any limit. A zero-line function is a defect, and
    # US15 function_length_rating is where it is reported.
    assert rule_length(0, 50, 7) is None


def test_r8_negative_loc_is_rejected():
    with pytest.raises(ValueError) as caught:
        rule_length(-1, 50, 7)
    assert "loc" in str(caught.value)


def test_r9_a_limit_below_one_is_rejected():
    with pytest.raises(ValueError) as caught:
        rule_length(60, 0, 7)
    assert "limit" in str(caught.value)


def test_the_message_names_both_numbers():
    # a reviewer reading the report should not have to look up the limit
    message = rule_length(80, 50, 7).message
    assert "80" in message
    assert "50" in message


def test_the_line_number_is_carried_through_untouched():
    # the rule trusts the scanner on line numbering and validates nothing
    assert rule_length(80, 50, 1).line == 1
    assert rule_length(80, 50, 2048).line == 2048


# --------------------------------------------------------------------------
# Boundary value analysis, at the default function_loc_limit of 50.
# --------------------------------------------------------------------------


def test_boundaries_around_the_limit():
    assert rule_length(49, 50, 7) is None
    assert rule_length(50, 50, 7) is None        # on it
    assert rule_length(51, 50, 7) is not None    # the first finding


def test_boundaries_between_minor_and_major():
    # MINOR ends at limit + limit // 2 = 75
    assert rule_length(75, 50, 7).severity == MINOR
    assert rule_length(76, 50, 7).severity == MAJOR


def test_boundaries_between_major_and_critical():
    # CRITICAL begins at 2 * limit = 100
    assert rule_length(99, 50, 7).severity == MAJOR
    assert rule_length(100, 50, 7).severity == CRITICAL


def test_the_boundary_of_the_limit_argument():
    assert rule_length(5, 1, 7) is not None       # limit 1 is valid
    with pytest.raises(ValueError):
        rule_length(5, 0, 7)


# --------------------------------------------------------------------------
# The rule shape, now in its fourth instance.
# --------------------------------------------------------------------------


def test_this_rule_can_never_emit_info():
    # Reaching classify_severity requires loc > limit; INFO requires
    # loc <= limit. Proved for the shape in US22's symbolic analysis.
    for loc in range(51, 300):
        assert rule_length(loc, 50, 7).severity != INFO


def test_all_four_rules_band_identically_and_carry_different_codes():
    # The only test that would fail if any one of the four re-implemented the
    # severity bands. Codes must differ; severities must not.
    for limit in range(1, 9):
        for measurement in range(limit + 1, limit * 3 + 4):
            length = rule_length(measurement, limit, 7)
            params = rule_params(measurement, limit, 7)
            nesting = rule_nesting(measurement, limit, 7)
            complexity = rule_complexity(measurement, limit, 7)
            assert (length.severity == params.severity
                    == nesting.severity == complexity.severity)
            assert len({length.code, params.code,
                        nesting.code, complexity.code}) == 4
            assert length.code == CODE_LENGTH
            assert params.code == CODE_PARAMS
            assert nesting.code == CODE_NESTING
            assert complexity.code == CODE_COMPLEXITY


def test_all_four_rules_agree_on_the_clean_case():
    for limit in range(1, 9):
        for measurement in range(0, limit + 1):
            assert rule_length(measurement, limit, 7) is None
            assert rule_params(measurement, limit, 7) is None
            assert rule_nesting(measurement, limit, 7) is None
            assert rule_complexity(measurement, limit, 7) is None
