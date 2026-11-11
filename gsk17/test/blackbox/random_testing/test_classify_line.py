"""Random-based black-box tests for classify_line - US01, Gunjan (gsk17).

Technique: random testing. Inputs are generated at random rather than chosen, so
there is no hand-written expected value to compare against. The oracle is an
INVARIANT - a property that must hold for every input, however that input was
produced.

The seed is fixed so that any failure can be replayed exactly; random testing
that cannot be reproduced is of little use once it finds something.
"""

import random
import string

from core.scanner import classify_line

SEED = 20261111
RUNS = 500

VALID = ("blank", "comment", "code")
WHITESPACE = " \t\n\r\f\v"


def random_line(rng):
    """A random line drawn from the printable characters, sometimes empty."""
    length = rng.randint(0, 40)
    return "".join(rng.choice(string.printable) for _ in range(length))


def test_result_is_always_one_of_three_values():
    """Invariant: the function is total - every string maps to a known class."""
    rng = random.Random(SEED)
    for _ in range(RUNS):
        line = random_line(rng)
        assert classify_line(line) in VALID, repr(line)


def test_whitespace_only_input_is_always_blank():
    """Invariant: any string drawn only from whitespace classifies as blank."""
    rng = random.Random(SEED + 1)
    for _ in range(RUNS):
        line = "".join(rng.choice(WHITESPACE) for _ in range(rng.randint(0, 20)))
        assert classify_line(line) == "blank", repr(line)


def test_leading_hash_after_whitespace_is_always_comment():
    """Invariant: whitespace then a hash is a comment, whatever follows it."""
    rng = random.Random(SEED + 2)
    for _ in range(RUNS):
        pad = "".join(rng.choice(" \t") for _ in range(rng.randint(0, 8)))
        tail = "".join(rng.choice(string.printable) for _ in range(rng.randint(0, 20)))
        assert classify_line(pad + "#" + tail) == "comment"


def test_leading_whitespace_never_changes_the_classification():
    """Invariant: the function strips before testing, so indentation cannot
    change the answer. This is what makes an indented comment a comment."""
    rng = random.Random(SEED + 3)
    for _ in range(RUNS):
        line = random_line(rng)
        pad = "".join(rng.choice(" \t") for _ in range(rng.randint(1, 8)))
        assert classify_line(pad + line) == classify_line(line), repr(line)
