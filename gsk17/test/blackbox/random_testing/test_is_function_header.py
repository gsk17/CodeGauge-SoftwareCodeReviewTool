"""Black-box tests for is_function_header - US07, Gunjan (gsk17).

Technique: random testing against invariants.
Function under test: core.scanner.is_function_header(line).

No expected value is written by hand. Each test states a property that must
hold for every line in its class and samples the class randomly. The seed is
fixed so a failure replays exactly.

The generator below builds *syntactically plausible* function headers from
random names and parameter lists, rather than random character soup. Random
strings would almost never be headers, so every test would pass trivially; the
interesting inputs are the ones close to being headers.
"""

import random
import string

from core.scanner import is_function_header

SEED = 20261118
TRIALS = 200

NAME_START = string.ascii_letters + "_"
NAME_REST = string.ascii_letters + string.digits + "_"


def _random_name(rng):
    length = rng.randint(1, 12)
    return rng.choice(NAME_START) + "".join(
        rng.choice(NAME_REST) for _ in range(length - 1))


def _random_params(rng):
    count = rng.randint(0, 4)
    return ", ".join(_random_name(rng) for _ in range(count))


def _random_header(rng):
    """A syntactically plausible header, randomly indented and async or not."""
    indent = " " * rng.choice((0, 4, 8, 12))
    keyword = rng.choice(("def", "async def"))
    return "%s%s %s(%s):" % (indent, keyword, _random_name(rng), _random_params(rng))


def test_the_result_is_always_a_boolean():
    rng = random.Random(SEED)
    for _ in range(TRIALS):
        assert is_function_header(_random_header(rng)) in (True, False)


def test_every_well_formed_header_is_recognised():
    rng = random.Random(SEED + 1)
    for _ in range(TRIALS):
        line = _random_header(rng)
        assert is_function_header(line) is True, line


def test_indentation_never_changes_the_answer():
    # the line is stripped first, so a method and a top-level function are
    # indistinguishable to this check
    rng = random.Random(SEED + 2)
    for _ in range(TRIALS):
        body = _random_header(rng).strip()
        for indent in ("", " ", "    ", "\t", "        "):
            assert is_function_header(indent + body) is True


def test_trailing_whitespace_never_changes_the_answer():
    rng = random.Random(SEED + 3)
    for _ in range(TRIALS):
        line = _random_header(rng)
        assert is_function_header(line + "   ") is is_function_header(line)


def test_commenting_a_header_out_always_hides_it():
    # whatever the header, a leading hash must suppress it
    rng = random.Random(SEED + 4)
    for _ in range(TRIALS):
        line = _random_header(rng)
        assert is_function_header("# " + line.strip()) is False
        assert is_function_header("#" + line.strip()) is False


def test_removing_the_parenthesis_always_hides_it():
    # both conditions are required, so breaking either one must be enough
    rng = random.Random(SEED + 5)
    for _ in range(TRIALS):
        line = _random_header(rng).replace("(", "").replace(")", "")
        assert is_function_header(line) is False, line


def test_an_identifier_beginning_with_def_is_never_a_header():
    # "def" as a prefix rather than a keyword - the case a naive startswith
    # check gets wrong. Built by appending random name characters directly to
    # "def" with no space.
    rng = random.Random(SEED + 6)
    for _ in range(TRIALS):
        suffix = "".join(rng.choice(NAME_REST) for _ in range(rng.randint(1, 8)))
        for line in ("def%s = 1" % suffix,
                     "def%s(x)" % suffix,
                     "    def%s = call(y)" % suffix):
            assert is_function_header(line) is False, line


def test_an_assignment_is_never_a_header():
    rng = random.Random(SEED + 7)
    for _ in range(TRIALS):
        line = "%s = %s(%s)" % (_random_name(rng), _random_name(rng),
                                _random_params(rng))
        assert is_function_header(line) is False, line


def test_the_function_is_deterministic():
    rng = random.Random(SEED + 8)
    for _ in range(TRIALS):
        line = _random_header(rng)
        assert is_function_header(line) is is_function_header(line)
