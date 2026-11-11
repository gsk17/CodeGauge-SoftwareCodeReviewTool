"""Concolic testing for weighted_penalty - US28, Harshita (hcg22).

Technique: concolic (dynamic symbolic) execution. The severity parameter is a
string compared for equality, so each negation fixes S to the next literal in
the chain rather than solving an inequality - the string domain makes the
frontier an enumeration.

Full derivation: docs/symbolic/hcg22-symbolic-execution.md, section 5.
"""

import pytest

from core.scoring import weighted_penalty


def test_iteration_1_seed():
    # seed ("CRITICAL", 15, 8, 3, 1) - arbitrary. Path P5
    # negate S = "CRITICAL" -> next input needs a different severity
    assert weighted_penalty("CRITICAL", 15, 8, 3, 1) == 15


def test_iteration_2_negate_the_critical_comparison():
    # solved ("MAJOR", ...). Path P6
    assert weighted_penalty("MAJOR", 15, 8, 3, 1) == 8


def test_iteration_3_negate_the_major_comparison():
    # solved ("MINOR", ...). Path P7
    assert weighted_penalty("MINOR", 15, 8, 3, 1) == 3


def test_iteration_4_negate_the_minor_comparison():
    # solved ("INFO", ...). Path P8
    assert weighted_penalty("INFO", 15, 8, 3, 1) == 1


def test_iteration_5_negate_every_comparison():
    # solved ("WARNING", ...) - any string outside the four. Path P9
    # comparison frontier exhausted; backtrack into the guard loop
    with pytest.raises(ValueError):
        weighted_penalty("WARNING", 15, 8, 3, 1)


def test_iteration_6_negate_the_guard():
    # solved ("CRITICAL", -1, ...). Path P1. Frontier empty.
    with pytest.raises(ValueError):
        weighted_penalty("CRITICAL", -1, 8, 3, 1)
