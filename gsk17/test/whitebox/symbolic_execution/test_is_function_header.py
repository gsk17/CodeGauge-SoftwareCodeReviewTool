"""White-box tests for is_function_header - US07, Gunjan (gsk17).

Technique: symbolic execution.
Function under test: core.scanner.is_function_header(line).

Like US02 this function branches on string properties rather than on integers,
but unlike US02 it has **no loop**, so the tree is finite and complete and needs
no bounding. That makes it the cleanest demonstration in the project of
symbolic execution over a non-numeric domain.

**Symbolic input.** One symbolic string S, with `T = S.strip()`. The function
can observe only four properties of T, so those are the only atoms any path
condition can contain:

    h   T starts with "#"
    p   T contains "("
    d   T starts with "def "
    a   T starts with "async def "

Everything else about the string - its length, its remaining characters, the
contents of the parameter list - is invisible to the function and therefore
absent from every path condition. That reduction is what makes the analysis
finite over an infinite input domain.

    Path  Path condition                   Witness                        Returns
    P1    h                                "# def commented_out():"       False
    P2    not h, not p                     "def no_parens:"               False
    P3    not h, p, d                      "def withdraw(self, amount):"  True
    P4    not h, p, not d, a               "async def fetch(url):"        True
    P5    not h, p, not d, not a           "total = compute(x, y)"        False

Five leaves, five paths.

### Finding 1 - the result is a conjunction, so guard order cannot change it

Collecting the two True paths:

    result = not h and p and (d or a)

That is a conjunction of three independent conditions. Conjunction is
commutative, so **reordering b1 to b4 can change which path an input takes but
never what the function returns.** The three False leaves partition the
complement exactly, with no overlap and no gap:

    P1   h                        whatever else is true
    P2   not h, not p
    P5   not h, p, not d, not a

Every string satisfies exactly one of the five path conditions. The function is
total, and there is no input for which it fails to return.

This is worth proving rather than assuming because the guards *look* order-
sensitive: a reader may suspect that testing for `"#"` after the keyword would
change the answer for `"# def f():"`. It would change the path - P5 instead of
P1 - and not the result.

### Finding 2 - `startswith` is load-bearing and `in` would be wrong

`"async def "` **contains** `"def "`, but not at position 0. So:

    "async def fetch(url):"     startswith("def ") -> False,  "def " in T -> True

With `in` instead of `startswith`, b3 would capture every coroutine definition
and b4 would be dead code - harmless here, since both return True. But `in`
also accepts strings where `"def "` appears anywhere at all:

    "x = my def (y)"            startswith("def ") -> False,  "def " in T -> True

which is not a definition. So the two tests are not interchangeable, and the
difference is demonstrable rather than hypothetical. P4's existence as a
separate path from P3 is the structural evidence that `startswith` was used.

### Finding 3 - b3 and b4 are mutually exclusive, so the tree has five leaves and not six

No string starts with both `"def "` and `"async def "`. The combination
`d and a` is unsatisfiable, so the tree has no leaf for it. The missing sixth
leaf is an **infeasible path**, not an untested one.

### Finding 4 - the empty string needs no special case

`"(" not in ""` is true, so the empty string takes P2 and returns False. There
is no length check anywhere in the function, and none is needed. A derived
property: the guard that rejects `"def no_parens:"` also rejects `""`, for the
same reason.
"""

from core.scanner import is_function_header


# --- the five paths -----------------------------------------------------------

def test_p1_the_comment_guard():
    # PC: h. The witness carries a parenthesis and a keyword, so it would
    # satisfy P3 were b1 not evaluated first - which is what makes it a
    # witness for this path rather than for that one.
    assert is_function_header("# def commented_out():") is False


def test_p2_no_parameter_list():
    # PC: not h and not p
    assert is_function_header("def no_parens:") is False


def test_p3_a_plain_definition():
    # PC: not h and p and d
    assert is_function_header("def withdraw(self, amount):") is True


def test_p4_a_coroutine_definition():
    # PC: not h and p and not d and a
    assert is_function_header("async def fetch(url):") is True


def test_p5_neither_keyword():
    # PC: not h and p and not d and not a
    assert is_function_header("total = compute(x, y)") is False


# --- Finding 1: the result is order-independent --------------------------------

def test_finding_1_the_result_is_the_conjunction_not_h_and_p_and_d_or_a():
    """Checked by evaluating the derived expression independently and comparing
    it against the function across a set of strings chosen to make each atom
    true and false in every combination."""
    cases = (
        "def f(x):", "async def f(x):", "def f:", "async def f:",
        "# def f(x):", "# async def f(x):", "#def f(x):",
        "x = f(y)", "x = y", "", "   ", "default = 1", "defer(x)",
        "async f(x):", "async with f(x):", "define(a, b)",
        "    def f(x):", "\tasync def f(x):", "class A:", "return f(x)",
    )
    for line in cases:
        stripped = line.strip()
        h = stripped.startswith("#")
        p = "(" in stripped
        d = stripped.startswith("def ")
        a = stripped.startswith("async def ")
        expected = (not h) and p and (d or a)
        assert is_function_header(line) is expected, line


def test_finding_1_the_five_path_conditions_partition_every_input():
    """Each string satisfies exactly one path condition, so the function is
    total. Counted rather than argued."""
    cases = ("def f(x):", "async def f(x):", "def f:", "# def f(x):",
             "x = f(y)", "", "default = 1", "async f(x):")
    for line in cases:
        stripped = line.strip()
        h = stripped.startswith("#")
        p = "(" in stripped
        d = stripped.startswith("def ")
        a = stripped.startswith("async def ")
        satisfied = [
            h,                                        # P1
            (not h) and (not p),                      # P2
            (not h) and p and d,                      # P3
            (not h) and p and (not d) and a,          # P4
            (not h) and p and (not d) and (not a),    # P5
        ]
        assert satisfied.count(True) == 1, line


# --- Finding 2: startswith is not interchangeable with in ----------------------

def test_finding_2_a_string_where_startswith_and_in_disagree():
    """`"def "` appears inside the line but not at its start. `in` would call
    this a header; `startswith` correctly does not."""
    line = "x = my def (y)"
    assert "def " in line.strip()
    assert not line.strip().startswith("def ")
    assert is_function_header(line) is False


def test_finding_2_a_coroutine_contains_def_but_does_not_start_with_it():
    line = "async def fetch(url):"
    assert "def " in line
    assert not line.startswith("def ")
    # recognised by b4, not b3 - which is why P4 is a separate path
    assert is_function_header(line) is True


# --- Finding 3: the unsatisfiable combination ----------------------------------

def test_finding_3_no_string_starts_with_both_keywords():
    """`d and a` is unsatisfiable, so the tree has five leaves rather than six.
    Checked over the witnesses for the paths where either is true."""
    for line in ("def f(x):", "async def f(x):", "    def f(x):",
                 "async def async def f(x):"):
        stripped = line.strip()
        d = stripped.startswith("def ")
        a = stripped.startswith("async def ")
        assert not (d and a), line


# --- Finding 4: the empty string is handled by the parenthesis guard ----------

def test_finding_4_the_empty_string_takes_the_no_parenthesis_path():
    assert "(" not in ""
    assert is_function_header("") is False
    # and by the same guard, for the same reason
    assert is_function_header("def no_parens:") is False
