"""Black-box tests for count_leading_spaces - US02, Gunjan (gsk17).

Technique: random testing against invariants.
Function under test: core.scanner.count_leading_spaces(line, tab_width).

These tests assert no hand-written expected values. Each one states a property
that must hold for every input in the domain and then samples the domain
randomly. The seed is fixed so that any failure can be replayed exactly.
"""

import random
import string

import pytest

from core.scanner import count_leading_spaces

SEED = 20261115
TRIALS = 200

# deliberately excludes space and tab, so generated bodies never add indentation
BODY_CHARS = string.ascii_letters + string.digits + "=+-*/()_.,:"


def _random_body(rng):
    """A random non-whitespace-leading line body."""
    length = rng.randint(1, 20)
    return "".join(rng.choice(BODY_CHARS) for _ in range(length))


def test_the_result_is_never_negative():
    # an indentation width is a count, so it cannot be below zero
    rng = random.Random(SEED)
    for _ in range(TRIALS):
        line = " " * rng.randint(0, 10) + "\t" * rng.randint(0, 5) + _random_body(rng)
        assert count_leading_spaces(line, rng.randint(1, 8)) >= 0


def test_a_body_with_no_leading_whitespace_always_measures_zero():
    rng = random.Random(SEED + 1)
    for _ in range(TRIALS):
        assert count_leading_spaces(_random_body(rng), rng.randint(1, 8)) == 0


def test_adding_n_spaces_to_the_front_adds_exactly_n():
    # the function must be additive in leading spaces, whatever follows them
    rng = random.Random(SEED + 2)
    for _ in range(TRIALS):
        line = _random_body(rng)
        tab_width = rng.randint(1, 8)
        extra = rng.randint(0, 12)
        before = count_leading_spaces(line, tab_width)
        after = count_leading_spaces(" " * extra + line, tab_width)
        assert after == before + extra


def test_n_tabs_always_measure_n_times_tab_width():
    rng = random.Random(SEED + 3)
    for _ in range(TRIALS):
        tabs = rng.randint(0, 6)
        tab_width = rng.randint(1, 8)
        line = "\t" * tabs + _random_body(rng)
        assert count_leading_spaces(line, tab_width) == tabs * tab_width


def test_trailing_text_never_changes_the_measurement():
    # indentation depends on the prefix alone
    rng = random.Random(SEED + 4)
    for _ in range(TRIALS):
        prefix = " " * rng.randint(0, 8) + "\t" * rng.randint(0, 3)
        tab_width = rng.randint(1, 8)
        first = count_leading_spaces(prefix + _random_body(rng), tab_width)
        second = count_leading_spaces(prefix + _random_body(rng), tab_width)
        assert first == second


def test_an_invalid_tab_width_always_raises():
    rng = random.Random(SEED + 5)
    for _ in range(TRIALS):
        line = " " * rng.randint(0, 6) + _random_body(rng)
        with pytest.raises(ValueError):
            count_leading_spaces(line, rng.randint(-50, 0))
