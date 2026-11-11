"""White-box tests for classify_line - US01, Gunjan (gsk17).

Technique: branch coverage. classify_line has two decision points:

    b1  stripped == ""
    b2  stripped.startswith("#")

Branch coverage requires each to be taken and not taken, so four outcomes.
b1-true returns immediately, so b2 is only reachable when b1 is false; the
four outcomes are covered by the three tests below.
"""

from core.scanner import classify_line


def test_b1_true_returns_blank():
    # b1 TRUE  - stripped is empty, returns before b2 is reached
    assert classify_line("   \t ") == "blank"


def test_b1_false_b2_true_returns_comment():
    # b1 FALSE - stripped is not empty
    # b2 TRUE  - first character of the stripped line is a hash
    assert classify_line("    # indented comment") == "comment"


def test_b1_false_b2_false_returns_code():
    # b1 FALSE - stripped is not empty
    # b2 FALSE - first character is not a hash, even though the line holds one
    assert classify_line("x = 1  # trailing comment") == "code"
