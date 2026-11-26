"""White-box tests for parameter_count_rating - US14, Kasam (khm12).

Technique: branch coverage.
Function under test: core.complexity.parameter_count_rating(param_count,
limit).

Four decisions, each returning or raising immediately when true:

    b1  param_count < 0             -> ValueError
    b2  limit < 1                   -> ValueError
    b3  param_count <= limit        -> RATING_OK
    b4  param_count <= 2 * limit    -> RATING_MANY
    (implicit else)                 -> RATING_EXCESSIVE

Five leaves, so five tests give full branch coverage:

    test                        b1     b2     b3     b4
    negative_count              TRUE   -      -      -
    limit_below_one             FALSE  TRUE   -      -
    within_the_limit            FALSE  FALSE  TRUE   -
    over_but_not_by_much        FALSE  FALSE  FALSE  TRUE
    beyond_twice_the_limit      FALSE  FALSE  FALSE  FALSE

A dash means the decision is not reached on that path.

**All five leaves are reachable at every valid limit, including limit 1.** That
is not true of the severity bands in `core.severity`, where a limit of 1
empties two of the four bands - a defect this module does not share, because
the MANY band here holds exactly `limit` values and so is never empty. The
proof is in `symbolic_execution/test_parameter_count_rating.py` finding 1, and
the tests below exercise the five leaves twice, once at a realistic limit of 4
and once at the minimum limit of 1, to pin it.

**b4 is only ever evaluated with `param_count > limit`.** The combination
`param_count <= limit and param_count > 2 * limit` is unsatisfiable for every
`limit >= 1`, so the tree has no sixth leaf and none is missing from the table.
"""

import pytest

from core.complexity import (
    RATING_EXCESSIVE,
    RATING_MANY,
    RATING_OK,
    parameter_count_rating,
)


def test_b1_true_negative_parameter_count():
    # b1 TRUE - returns before b2, so the equally invalid limit is never
    # looked at and never named in the message
    with pytest.raises(ValueError) as caught:
        parameter_count_rating(-1, 0)
    assert "param_count" in str(caught.value)


def test_b2_true_limit_below_one():
    # b1 FALSE, b2 TRUE. A limit of 0 would rate every signature, including
    # one taking no parameters at all, as over its budget.
    with pytest.raises(ValueError) as caught:
        parameter_count_rating(3, 0)
    assert "limit" in str(caught.value)


def test_b3_true_within_the_limit():
    # b1 FALSE, b2 FALSE, b3 TRUE
    assert parameter_count_rating(3, 4) == RATING_OK


def test_b4_true_over_but_not_by_much():
    # b1 FALSE, b2 FALSE, b3 FALSE, b4 TRUE
    assert parameter_count_rating(6, 4) == RATING_MANY


def test_all_decisions_false_beyond_twice_the_limit():
    # every decision FALSE - the implicit else, the only leaf with no return
    # of its own in the source
    assert parameter_count_rating(9, 4) == RATING_EXCESSIVE


def test_b3_is_inclusive_and_b4_is_inclusive():
    # The two boundaries of the MANY band, at a limit of 4: OK runs 0-4,
    # MANY runs 5-8, EXCESSIVE begins at 9. Both comparisons are <=, so the
    # limit itself and twice the limit are each in the kinder band.
    assert parameter_count_rating(4, 4) == RATING_OK
    assert parameter_count_rating(5, 4) == RATING_MANY
    assert parameter_count_rating(8, 4) == RATING_MANY
    assert parameter_count_rating(9, 4) == RATING_EXCESSIVE


def test_all_three_ratings_are_reachable_at_the_minimum_limit():
    # limit 1: OK is {0, 1}, MANY is {2}, EXCESSIVE is {3, ...}. Every leaf
    # still reachable, which is the property core.severity lacks.
    assert parameter_count_rating(0, 1) == RATING_OK
    assert parameter_count_rating(1, 1) == RATING_OK
    assert parameter_count_rating(2, 1) == RATING_MANY
    assert parameter_count_rating(3, 1) == RATING_EXCESSIVE


def test_zero_parameters_is_ok_not_a_special_case():
    # There is no guard for an empty signature. b3 handles it, because 0 is
    # <= every valid limit. A derived property rather than a deliberate one,
    # pinned so a refactor does not add a redundant check.
    assert parameter_count_rating(0, 1) == RATING_OK
    assert parameter_count_rating(0, 99) == RATING_OK
