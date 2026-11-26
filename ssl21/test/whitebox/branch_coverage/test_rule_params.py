"""White-box tests for rule_params - US22, Saaket (ssl21).

Technique: branch coverage.
Function under test: core.rules.rule_params(param_count, limit, line).

The third rule built to the shape US19 established, and structurally identical
to `rule_complexity` and `rule_nesting` after renaming the measurement:

    b1  param_count < 0         -> ValueError
    b2  limit < 1               -> ValueError
    b3  param_count <= limit    -> None
    (implicit else)             -> Issue(CODE_PARAMS, classify_severity(...))

Four leaves in this function, so four tests give full branch coverage of it:

    test                        b1     b2     b3
    negative_count              TRUE   -      -
    limit_below_one             FALSE  TRUE   -
    within_the_limit            FALSE  FALSE  TRUE
    over_the_limit              FALSE  FALSE  FALSE

A dash means the decision is not reached on that path.

**Four leaves is not the whole story, and this is the point of the file.** The
fourth leaf calls `classify_severity`, which has four decisions of its own.
Branch coverage of `rule_params` in isolation is achieved by the four tests
above and tells a reader nothing about which severities a finding can carry.
Covering the *inlined* function needs the severity band tests further down,
and the symbolic analysis shows that three of the callee's five leaves are
unreachable from here however many tests are added.

Coverage measured per function is therefore an over-statement of what has been
checked. `coverage` reports `core/rules.py` at 100% after the four tests
above, because every line in the file has run; the severity bands a report can
actually display are decided in another file, by code those four tests execute
without exercising.
"""

import pytest

from core.rules import CODE_PARAMS, rule_params
from core.severity import CRITICAL, MAJOR, MINOR


def test_b1_true_negative_parameter_count():
    # b1 TRUE - returns before b2, so the equally invalid limit is never seen
    with pytest.raises(ValueError) as caught:
        rule_params(-1, 0, 12)
    assert "param_count" in str(caught.value)


def test_b2_true_limit_below_one():
    # b1 FALSE, b2 TRUE. The lower bound exists because classify_severity
    # requires limit >= 1; the rule enforces its callee's contract rather
    # than letting the error surface from inside it.
    with pytest.raises(ValueError) as caught:
        rule_params(3, 0, 12)
    assert "limit" in str(caught.value)


def test_b3_true_within_the_limit_returns_none():
    # b1 FALSE, b2 FALSE, b3 TRUE. None rather than an INFO-severity Issue,
    # so the report builder can drop the Nones in one pass.
    assert rule_params(3, 4, 12) is None


def test_all_decisions_false_an_issue_is_raised():
    # every decision FALSE - the implicit else, the only leaf that builds an
    # Issue and the only one that calls into core.severity
    issue = rule_params(6, 4, 12)
    assert issue is not None
    assert issue.code == CODE_PARAMS
    assert issue.line == 12
    assert "6 parameters exceeds limit 4" in issue.message


def test_b3_is_inclusive_so_sitting_on_the_limit_is_clean():
    # The boundary. Four parameters against a limit of four is acceptable;
    # five is not.
    assert rule_params(4, 4, 1) is None
    assert rule_params(5, 4, 1) is not None


def test_the_severity_bands_inside_the_fourth_leaf():
    # Not reachable by any additional branch of rule_params - these all take
    # the same path through it and differ only inside classify_severity.
    # At a limit of 4: MINOR is {5, 6}, MAJOR is {7}, CRITICAL is {8, ...}.
    assert rule_params(5, 4, 1).severity == MINOR
    assert rule_params(6, 4, 1).severity == MINOR
    assert rule_params(7, 4, 1).severity == MAJOR
    assert rule_params(8, 4, 1).severity == CRITICAL
    assert rule_params(99, 4, 1).severity == CRITICAL


def test_no_issue_this_rule_produces_can_carry_info():
    # INFO exists in core.severity and is in RANK_ORDER, and no rule can emit
    # it: reaching classify_severity requires param_count > limit, and INFO
    # requires param_count <= limit. See the symbolic analysis, finding 2.
    for count in range(5, 40):
        assert rule_params(count, 4, 1).severity in (MINOR, MAJOR, CRITICAL)


def test_the_line_number_is_carried_through_untouched():
    # The rule decides nothing about the line; it reports where the caller
    # said the signature was. No validation, deliberately - the scanner owns
    # line numbering and a rule that second-guessed it could reject a valid
    # report.
    assert rule_params(9, 4, 1).line == 1
    assert rule_params(9, 4, 4096).line == 4096
    assert rule_params(9, 4, 0).line == 0
