"""Per-file line metrics - member M1 (gsk17, Gunjan).

Measurements taken over the counts the scanner produces, rather than over the
source text itself. `core/scanner.py` is the only module that reads characters;
everything here consumes the integers it hands back, which is what keeps these
functions analysable by hand.
"""


def comment_ratio_percent(comment_lines, code_lines):
    """Comment density as a whole-number percentage - US04.

    The denominator is comment lines plus code lines. Blank lines are counted
    as neither by `classify_line` and never reach this function, so a file
    padded with blank lines is not reported as badly documented.

    **An empty file returns 0, not an error.** A file with no comments and no
    code gives a denominator of zero, and the obvious implementation raises
    `ZeroDivisionError` - a crash rather than a measurement. Nothing is
    documented in an empty file, so 0 is the honest answer and the caller is
    not made to special-case it.

    **The result is floored, not rounded.** 28 comments in 170 lines is 16.47%,
    reported as 16. A reported percentage should never overstate the
    documentation actually present, so the fractional part is discarded. That
    also keeps 100 meaningful: a file containing even one line of code can
    never reach it, so 100 means "comments only" and nothing else.
    """
    if comment_lines < 0:
        raise ValueError("comment_lines must not be negative, got %r"
                         % (comment_lines,))
    if code_lines < 0:
        raise ValueError("code_lines must not be negative, got %r"
                         % (code_lines,))
    counted = comment_lines + code_lines
    if counted == 0:                       # an empty file documents nothing
        return 0
    return comment_lines * 100 // counted  # floored, never rounded up
