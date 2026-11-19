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


def is_function_header(line):
    """Is this line a function definition header? - US07.

    True only when the stripped line begins with `def ` or `async def ` and
    contains an opening parenthesis. Both conditions are needed, and each
    rejects a different kind of near-miss.

    The trailing space in `"def "` is the whole point of the first test.
    Without it, `default = 1`, `defer(x)` and `define(a, b)` all begin with the
    three characters `def` and would be read as function headers. The space is
    what separates a keyword from a prefix.

    The parenthesis test rejects `def no_parens:`, which is not valid Python
    but can appear mid-edit in a file being reviewed.

    The comment test comes first, so that a commented-out definition is
    rejected before either of the others is considered.

    Known limitation: the scan is line-based and does not track string state,
    so a line inside a triple-quoted block that happens to look like a
    definition is read as one. Documented in the README rather than worked
    around.
    """
    stripped = line.strip()
    if stripped.startswith("#"):           # a commented-out def is not a def
        return False
    if "(" not in stripped:                # a header always has a parameter list
        return False
    if stripped.startswith("def "):        # the space matters - see the docstring
        return True
    if stripped.startswith("async def "):  # a coroutine definition
        return True
    return False                           # implicit else: not a definition
