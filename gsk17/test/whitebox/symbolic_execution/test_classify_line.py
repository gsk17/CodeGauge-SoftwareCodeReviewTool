"""Symbolic execution tests for classify_line - US01, Gunjan (gsk17).

Technique: symbolic execution. Each test discharges one leaf of the symbolic
execution tree in docs/symbolic/gsk17-symbolic-execution.md. S is the symbolic
input and T = strip(S); every path condition is written over T, because both
branches test the stripped line rather than the raw one.
"""

from core.scanner import classify_line


def test_path_p1_empty_after_strip():
    # PC: strip(S) = empty
    # witness: "" - strip never enters its loop
    assert classify_line("") == "blank"


def test_path_p1_whitespace_only_after_strip():
    # PC: strip(S) = empty
    # witness: "   \t " - a mixture of space and tab, all stripped away
    assert classify_line("   \t ") == "blank"


def test_path_p2_first_stripped_char_is_hash():
    # PC: strip(S) != empty  and  strip(S)[0] = '#'
    # witness: "# a comment"
    assert classify_line("# a comment") == "comment"


def test_path_p2_indented_comment():
    # PC: strip(S) != empty  and  strip(S)[0] = '#'
    # witness: "    # indented comment" - strip removes the indent BEFORE b2
    # tests the first character, so S[0] is a space while T[0] is a hash.
    assert classify_line("    # indented comment") == "comment"


def test_path_p3_first_stripped_char_is_not_hash():
    # PC: strip(S) != empty  and  strip(S)[0] != '#'
    # witness: "    return x"
    assert classify_line("    return x") == "code"


def test_path_p3_hash_present_but_not_first():
    # PC: strip(S) != empty  and  strip(S)[0] != '#'
    # witness: "x = 1  # trailing comment" - the line contains a hash, so an
    # implementation testing '#' in stripped would wrongly take P2. The path
    # condition forbids it; this witness is what catches that mistake.
    assert classify_line("x = 1  # trailing comment") == "code"
