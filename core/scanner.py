"""Line-based source scanning - member M1 (gsk17, Gunjan).

The Python ast module is deliberately not used: it is not taught in CO7095.
Scanning is line-based, which keeps every downstream function working on
integers rather than text.
"""


def classify_line(line):
    """Classify one source line as blank, comment or code - US01.

    Whitespace only is blank, a leading hash is a comment, and anything else
    is code. A hash later in the line is a trailing comment on a line that
    still does work, so that line counts as code.
    """
    stripped = line.strip()
    if stripped == "":
        return "blank"
    if stripped.startswith("#"):
        return "comment"
    return "code"


def count_leading_spaces(line, tab_width):
    """Width of a line's indentation, in columns - US02.

    Walks the line from the left and stops at the first character that is
    neither a space nor a tab. A space is one column; a tab is tab_width
    columns, because indentation is measured in the columns a reader sees
    rather than in characters.

    Only leading whitespace counts. Trailing whitespace is not indentation,
    and whitespace after the first real character is not either.
    """
    if tab_width < 1:                      # a tab cannot be narrower than one column
        raise ValueError("tab_width must be at least 1, got %r" % (tab_width,))
    width = 0
    for character in line:
        if character == " ":               # one column
            width = width + 1
        elif character == "	":            # as many columns as the tab stop
            width = width + tab_width
        else:                              # first non-whitespace: indentation ends
            break
    return width
