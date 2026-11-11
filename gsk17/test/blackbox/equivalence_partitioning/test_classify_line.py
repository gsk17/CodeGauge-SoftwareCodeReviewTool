"""Black-box tests for classify_line - US01, Gunjan (gsk17).

Technique: equivalence partitioning. The specification names three classes of
line - blank, comment and code - so the input domain partitions into exactly
those three. One representative is taken from each, plus the two boundary
cases that distinguish the partitions: a whitespace-only line (blank, not
code) and a hash appearing mid-line (code with a trailing comment, not a
comment line).
"""

from core.scanner import classify_line


def test_blank_partition():
    assert classify_line("") == "blank"
    assert classify_line("   \t ") == "blank"


def test_comment_partition():
    assert classify_line("# a comment") == "comment"
    assert classify_line("    # indented comment") == "comment"


def test_code_partition():
    assert classify_line("    return x") == "code"
    assert classify_line("x = 1  # trailing comment") == "code"
