"""White-box tests for is_function_header - US07, Gunjan (gsk17).

Technique: branch coverage.
Function under test: core.scanner.is_function_header(line).

Four decisions, each returning immediately when true:

    b1  stripped.startswith("#")            -> False
    b2  "(" not in stripped                 -> False
    b3  stripped.startswith("def ")         -> True
    b4  stripped.startswith("async def ")   -> True
    (implicit else)                         -> False

Five leaves, so five tests give full branch coverage:

    test                        b1     b2     b3     b4
    commented_out               TRUE   -      -      -
    no_parentheses              FALSE  TRUE   -      -
    plain_def                   FALSE  FALSE  TRUE   -
    async_def                   FALSE  FALSE  FALSE  TRUE
    neither_keyword             FALSE  FALSE  FALSE  FALSE

A dash means the decision is not reached on that path.

**b3 and b4 can never both be true.** A string cannot start with both `"def "`
and `"async def "`, so the tree has no leaf for that combination and none is
missing from the table. `"async def "` does *contain* `"def "`, but not at
position 0, which is why `startswith` and not `in` is the right test - see
`symbolic_execution/test_is_function_header.py`.

**There is no length or emptiness check.** The empty string is handled by b2,
because `"(" not in ""` is true. That is a derived property rather than a
deliberate special case, and the test below pins it so a future refactor does
not introduce a redundant guard.
"""

from core.scanner import is_function_header


def test_b1_true_a_commented_definition():
    # b1 TRUE - returns before b2 is evaluated, so the parenthesis is never
    # looked at even though this line has one
    assert is_function_header("# def commented_out():") is False


def test_b2_true_a_definition_without_parentheses():
    # b1 FALSE, b2 TRUE - the keyword is present but the parameter list is not
    assert is_function_header("def no_parens:") is False


def test_b3_true_a_plain_definition():
    # b1 FALSE, b2 FALSE, b3 TRUE
    assert is_function_header("def withdraw(self, amount):") is True


def test_b4_true_a_coroutine_definition():
    # b1 FALSE, b2 FALSE, b3 FALSE, b4 TRUE.
    # b3 is false because the line starts with "async", not "def".
    assert is_function_header("async def fetch(url):") is True


def test_all_decisions_false_ordinary_code():
    # every decision FALSE - the implicit else, the only leaf with no return
    # statement of its own in the source
    assert is_function_header("total = compute(x, y)") is False


def test_b2_true_on_the_empty_line():
    # b1 FALSE, b2 TRUE. No emptiness check exists; the parenthesis test
    # handles it, because "(" is not in the empty string.
    assert is_function_header("") is False


def test_b2_true_on_a_whitespace_only_line():
    # stripping leaves the empty string, so this takes the same path as above
    assert is_function_header("    ") is False


def test_b1_reached_after_stripping_not_before():
    # An indented comment must still take b1. If the comment test ran against
    # the raw line rather than the stripped one, this would fall through to
    # b2 and then b3, and the result would be unchanged - but the path taken
    # would differ, which is what branch coverage is measuring.
    assert is_function_header("    # def commented_out():") is False
    assert is_function_header("        async def fetch(url):") is True
