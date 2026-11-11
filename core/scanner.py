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
