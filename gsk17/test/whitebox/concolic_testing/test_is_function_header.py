"""White-box tests for is_function_header - US07, Gunjan (gsk17).

Technique: concolic (dynamic symbolic) execution.
Function under test: core.scanner.is_function_header(line).

Seeded with `"def withdraw(self, amount):"` - a real method header from the
worked example in the design notes, chosen over a minimal input so the first
run takes the path the function exists to recognise.

Writing the four observable atoms as in the symbolic analysis - h for "starts
with #", p for "contains (", d for "starts with def ", a for "starts with
async def " - the walk is:

    It.  Input                            Path  Collected PC      Negated   Next
    1    "def withdraw(self, amount):"    P3    not h, p, d       d         (2)
    2    "async def withdraw(self):"      P4    not h, p, !d, a   a         (3)
    3    "total = withdraw(self)"         P5    not h, p, !d, !a  p         (4)
    4    "total = withdraw"               P2    not h, !p         h         (5)
    5    "# total = withdraw"             P1    h                 none      -

Five iterations, five paths, **100% path coverage** - and unusually, the walk
reaches every path with no backtracking at all. Each negation is of the
most recently evaluated branch, and each one leads straight to the next
unexplored leaf.

That is a consequence of the tree being a **chain** rather than a bush: every
decision has exactly one child that continues, so negating the deepest branch
always lands on a fresh leaf and the stack never has to be unwound. Compare the
US29 walk, which backtracks four times, or US12's, which backtracks twice and
then needs two manual shrink steps.

### Solving a string constraint is a search, not arithmetic

This is the honest difficulty of the technique on string-handling code, and it
is worth stating rather than glossing.

Negating `T.startswith("def ")` yields "some string not beginning with those
four characters, which still contains `(` and does not begin with `#`". That is
not an equation. There is no solver that returns *the* answer; there is a space
of answers, and something has to choose.

What makes it tractable here is the same reduction as in the symbolic analysis:
the function can observe only four properties of its input, so the constraint
is over four booleans rather than over characters. The space of distinct inputs
is at most 2^4 = 16 combinations, of which three are unsatisfiable
(`d and a`, and the two requiring `d or a` without `p`). Choosing a
representative string for a given combination of four booleans is mechanical.

**The strings in this walk were therefore constructed, not computed**, and each
one is the minimal edit to its predecessor that flips exactly the negated atom:

    1 -> 2    prefix "async " so d becomes false and a becomes true
    2 -> 3    replace the keyword so neither d nor a holds
    3 -> 4    drop the parentheses so p becomes false
    4 -> 5    prefix "# " so h becomes true

Each edit changes only the atom being negated and leaves the others alone -
**except the first**, which unavoidably changes two.

`a` implies `not d`: a string beginning `"async def "` cannot begin `"def "`.
The two atoms are logically linked, so negating `d` while landing on the `a`
branch flips both at once, and no input flips `d` alone and still reaches P4.
That is Finding 3 of the symbolic analysis - `d and a` unsatisfiable - seen from
the walk instead of from the tree, and it is a real limit on what a negation
step can promise: a solver can be asked to flip one branch condition, but if two
conditions are linked, its answer flips both.

Both properties are checked below.
"""

from core.scanner import is_function_header

#: the walk, as (iteration, line, expected)
WALK = (
    (1, "def withdraw(self, amount):", True),
    (2, "async def withdraw(self):", True),
    (3, "total = withdraw(self)", False),
    (4, "total = withdraw", False),
    (5, "# total = withdraw", False),
)


def _atoms(line):
    """The four properties the function can observe - nothing else is visible."""
    stripped = line.strip()
    return (stripped.startswith("#"),
            "(" in stripped,
            stripped.startswith("def "),
            stripped.startswith("async def "))


def test_iteration_1_the_seed():
    # seed: a plain method header. Path P3 - not h, p, d.
    assert is_function_header("def withdraw(self, amount):") is True


def test_iteration_2_negating_the_def_prefix():
    # PC: not h, p, and NOT d. Satisfied by prefixing "async ", which also
    # makes a true, so this lands on P4 rather than P5.
    assert is_function_header("async def withdraw(self):") is True


def test_iteration_3_negating_the_async_def_prefix():
    # PC: not h, p, not d, and NOT a. Neither keyword, so P5.
    assert is_function_header("total = withdraw(self)") is False


def test_iteration_4_negating_the_parenthesis():
    # PC: not h and NOT p. Dropping the parentheses returns before either
    # keyword test is reached.
    assert is_function_header("total = withdraw") is False


def test_iteration_5_negating_the_comment_guard():
    # PC: h. The last branch with an unexplored arm, and the walk terminates.
    assert is_function_header("# total = withdraw") is False


def test_the_walk_in_sequence():
    """All five iterations, replayed in generated order."""
    for iteration, line, expected in WALK:
        assert is_function_header(line) is expected, "iteration %d" % iteration


def test_each_step_flipped_only_the_atom_it_negated_except_where_two_are_linked():
    """Consecutive iterations differ in one atom - except step 1 to 2, which
    unavoidably flips two, and the reason is the finding.

    `a` (starts with "async def ") **implies** `not d` (starts with "def "):
    a string beginning "async def " cannot begin "def ". The two atoms are not
    independent, so negating `d` while landing on the `a` branch flips both at
    once. There is no input that flips `d` alone and still reaches P4.

    This is the same fact as Finding 3 in the symbolic analysis - `d and a` is
    unsatisfiable - seen from the walk rather than from the tree. It is also a
    limit on what the negation step can promise: a solver can be asked to flip
    one branch condition, but if two conditions are logically linked, the
    answer flips both.

    Every other step in the walk flips exactly one.
    """
    flips = []
    for first, second in zip(WALK, WALK[1:]):
        before = _atoms(first[1])
        after = _atoms(second[1])
        changed = [i for i, (b, a) in enumerate(zip(before, after)) if b != a]
        flips.append((first[0], second[0], changed))

    # step 1 -> 2 flips d (index 2) and a (index 3), together
    assert flips[0] == (1, 2, [2, 3])
    # every other step flips exactly one atom
    for _, _, changed in flips[1:]:
        assert len(changed) == 1

    # and the linkage that forces it: a implies not d, over every input in the walk
    for _, line, _ in WALK:
        _h, _p, d, a = _atoms(line)
        if a:
            assert not d


def test_the_walk_visited_all_five_distinct_atom_combinations():
    """Five iterations, five different observable states - so no path was
    visited twice and none was missed."""
    seen = set(_atoms(line) for _, line, _ in WALK)
    assert len(seen) == 5


def test_the_walk_needed_no_backtracking():
    """Each negation was of the deepest branch evaluated, which is only
    possible because the tree is a chain.

    Evidenced by the path depths being strictly decreasing: iteration 1 reaches
    depth 3, then 4, then 4, then 2, then 1 - each negation returns to a
    shallower or equal decision and immediately finds a new leaf, never
    re-exploring one already taken.
    """
    depths = []
    for _, line, _ in WALK:
        h, p, d, a = _atoms(line)
        if h:
            depths.append(1)              # P1, returned at b1
        elif not p:
            depths.append(2)              # P2, returned at b2
        elif d:
            depths.append(3)              # P3, returned at b3
        else:
            depths.append(4)              # P4 or P5, reached b4
    assert depths == [3, 4, 4, 2, 1]
