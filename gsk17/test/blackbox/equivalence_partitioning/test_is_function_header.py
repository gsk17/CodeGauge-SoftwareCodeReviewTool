"""Black-box tests for is_function_header - US07, Gunjan (gsk17).

Technique: equivalence partitioning with boundary value analysis.
Function under test: core.scanner.is_function_header(line).

A line is a function header only when its stripped form starts with `def ` or
`async def ` **and** contains an opening parenthesis. Both conditions matter,
and the partitions are chosen so that each one fails on its own somewhere:

    Headers
    H1  plain def, with parentheses          "def f(x):"
    H2  async def, with parentheses          "async def f(x):"
    H3  indented def                         "    def f(x):"

    Not headers - and why each one fails
    N1  commented out                        "# def f():"      leading hash
    N2  identifier beginning "def"           "default = 1"     no space after def
    N3  def with no parentheses              "def f:"          no "("
    N4  async with no def                    "async f():"      no "def "
    N5  ordinary code                        "x = 1"           neither
    N6  the empty or blank line              "", "   "         nothing at all

N2 is the partition this function exists to get right. `default`, `defer` and
`define` all begin with the three characters `def`, and a naive `startswith`
check misreads every one of them. The space is what separates a keyword from a
prefix.

**Known limitation, documented rather than tested as correct:** the scan is
line-based and does not track string literals, so a `def ` inside a triple-quoted
block or a string is misread as a header. That is recorded in the README; the
test below pins the current behaviour so a future change to it is deliberate
rather than accidental.
"""

from core.scanner import is_function_header


# --- H1, H2, H3: the three header forms ----------------------------------------

def test_h1_a_plain_def_is_a_header():
    assert is_function_header("def withdraw(self, amount):") is True


def test_h1_a_def_with_no_parameters_is_still_a_header():
    # boundary: the shortest possible header - "def", space, name, "()"
    assert is_function_header("def f():") is True


def test_h2_an_async_def_is_a_header():
    assert is_function_header("async def fetch(url):") is True


def test_h3_an_indented_def_is_a_header():
    # indentation is stripped before the test, so a method is a header
    assert is_function_header("    def fetch(self):") is True


def test_h3_an_indented_async_def_is_a_header():
    assert is_function_header("        async def fetch(url):") is True


# --- N1: commented out ---------------------------------------------------------

def test_n1_a_commented_def_is_not_a_header():
    assert is_function_header("# def commented_out():") is False


def test_n1_an_indented_commented_def_is_not_a_header():
    assert is_function_header("    # def commented_out():") is False


# --- N2: an identifier that merely begins with the letters def -----------------

def test_n2_default_is_not_a_header():
    # the partition this function exists for: "def" is a prefix of "default",
    # and only the space distinguishes the keyword from the identifier
    assert is_function_header("default = 1") is False


def test_n2_other_identifiers_beginning_with_def_are_not_headers():
    for line in ("defer(x)", "define(a, b)", "defaults = {}", "definition()"):
        assert is_function_header(line) is False, line


# --- N3: no parentheses --------------------------------------------------------

def test_n3_a_def_without_parentheses_is_not_a_header():
    assert is_function_header("def no_parens:") is False


def test_n3_an_async_def_without_parentheses_is_not_a_header():
    assert is_function_header("async def no_parens:") is False


# --- N4: async without def -----------------------------------------------------

def test_n4_async_alone_is_not_a_header():
    assert is_function_header("async f():") is False


def test_n4_async_with_something_else_is_not_a_header():
    assert is_function_header("async with session.get(url):") is False


# --- N5, N6: ordinary and empty lines ------------------------------------------

def test_n5_ordinary_code_is_not_a_header():
    for line in ("x = 1", "return f(x)", "if ready():", "class Account:"):
        assert is_function_header(line) is False, line


def test_n6_the_empty_line_is_not_a_header():
    # boundary: the shortest possible input
    assert is_function_header("") is False


def test_n6_a_whitespace_only_line_is_not_a_header():
    assert is_function_header("    ") is False


# --- the documented limitation, pinned rather than claimed correct -------------

def test_a_def_inside_a_string_is_misread():
    """Line-based scanning does not track string literals.

    This asserts the *current* behaviour, not the desired one. It is here so
    that a future change to string handling is a deliberate decision with a
    failing test attached, rather than a silent change nobody noticed. The
    limitation is recorded in the README.
    """
    assert is_function_header('    """def f(x): example in a docstring"""') is False
    assert is_function_header('def f(x): example') is True
