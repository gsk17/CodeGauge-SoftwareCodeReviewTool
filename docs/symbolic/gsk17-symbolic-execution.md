# Symbolic Execution and Concolic Testing — gsk17 (Gunjan)

Member M1, scanning and line metrics. One section per function, US01 to US09.

Method follows [WORKED-EXAMPLE.md](WORKED-EXAMPLE.md): label every branch, draw the
symbolic execution tree, express each leaf's path condition as a conjunction, solve it for
a concrete witness, then run concolic execution from an arbitrary seed and negate branches
until the frontier is empty.

---

## US01 — `core.scanner.classify_line(line)`

### 1. The function, with branches labelled

```python
def classify_line(line):
    stripped = line.strip()
    if stripped == "":              # b1
        return "blank"
    if stripped.startswith("#"):    # b2
        return "comment"
    return "code"                   # b3 (implicit else)
```

### 2. Symbolic input

Let `S` be a symbolic string standing for `line`. The symbolic state on entry is
`{line -> S}` with path condition `true`.

The function immediately derives `T = strip(S)`, the input with leading and trailing
whitespace removed. Every branch tests `T`, not `S`, so the path conditions are expressed
over `T` and each witness is then any `S` whose strip is that `T`.

**A note on the domain.** This is one of the few functions in the project whose input is a
string rather than an integer, so its path conditions are predicates over strings —
`T = ε`, `T[0] = '#'` — rather than the linear integer constraints seen elsewhere. That is
exactly why the architecture confines string handling to `scanner` and `formatter` and has
every later stage consume integers: integer path conditions are solvable mechanically,
string ones have to be reasoned about. The tree here stays small enough that the reasoning
is short.

### 3. Symbolic execution tree

```
                        PC: true
                        T = strip(S)
                        [b1] T = ε ?
                       /              \
                 true /                \ false
                     /                  \
             P1: "blank"            PC: T ≠ ε
             PC: T = ε              [b2] T[0] = '#' ?
                                   /              \
                             true /                \ false
                                 /                  \
                      P2: "comment"             P3: "code"
                      PC: T ≠ ε                 PC: T ≠ ε
                       and T[0] = '#'            and T[0] ≠ '#'
```

Three leaves, three paths, no infeasible path. The tree is a chain rather than a bush
because each branch returns immediately, so there is no path that passes through both `b1`
and `b2` as true.

### 4. Path conditions and solved witnesses

| Path | Path condition | Witness `S` | `T = strip(S)` | Returns |
|---|---|---|---|---|
| P1 | `strip(S) = ε` | `""` | `ε` | `blank` |
| P1' | `strip(S) = ε` | `"   \t "` | `ε` | `blank` |
| P2 | `strip(S) ≠ ε ∧ strip(S)[0] = '#'` | `"# a comment"` | `# a comment` | `comment` |
| P2' | same | `"    # indented"` | `# indented` | `comment` |
| P3 | `strip(S) ≠ ε ∧ strip(S)[0] ≠ '#'` | `"    return x"` | `return x` | `code` |
| P3' | same | `"x = 1  # trailing"` | `x = 1  # trailing` | `code` |

**Working for P1'.** The condition `strip(S) = ε` is satisfied by any `S` drawn entirely
from the whitespace set `{' ', '\t', '\n', '\r', '\f', '\v'}`, including the empty string.
Two witnesses are taken rather than one — `""` and `"   \t "` — because they exercise
different parts of `strip`: the first never enters its loop, the second strips a mixture of
space and tab. The specification treats them identically, and the test records that it does.

**Working for P3'.** `"x = 1  # trailing"` is the witness that distinguishes this function
from a naive one. A hash appears in the string, so an implementation testing
`'#' in stripped` rather than `stripped.startswith('#')` would wrongly take P2. The path
condition `strip(S)[0] ≠ '#'` is what forbids that, and this witness is the test that
catches it.

**Why P2' matters.** `strip` removes the leading whitespace *before* `b2` tests the first
character, so an indented comment satisfies `T[0] = '#'` even though `S[0]` is a space.
Had the implementation tested `line.startswith("#")` instead of `stripped.startswith("#")`,
this path would be unreachable and every indented comment would be misclassified as code.

### 5. Concolic execution

Concolic execution runs on a concrete input while collecting the symbolic path condition,
then negates the last unexplored branch and solves for the next input. Seeded with an
arbitrary `"x = 1"`:

| It. | Concrete input | Path taken | Collected PC | Branch negated | Next input |
|---|---|---|---|---|---|
| 1 | `"x = 1"` | P3 → `code` | `T ≠ ε ∧ T[0] ≠ '#'` | `T[0] ≠ '#'` → `T[0] = '#'` | `"#x"` |
| 2 | `"#x"` | P2 → `comment` | `T ≠ ε ∧ T[0] = '#'` | backtrack to b1: `T ≠ ε` → `T = ε` | `""` |
| 3 | `""` | P1 → `blank` | `T = ε` | none left | — |

Three iterations, three paths, **100% path coverage**. The frontier empties after the third
iteration because the function contains no loops, so its execution tree is finite and of
depth two.

Solving the negated conditions by hand:

- Iteration 1 → 2: need `T ≠ ε ∧ T[0] = '#'`. Any string whose first non-whitespace
  character is a hash satisfies it; `"#x"` is the shortest.
- Iteration 2 → 3: need `T = ε`, so the input must be whitespace only; `""` is the shortest.

### 6. Resulting test cases

The six witnesses in section 4 become the white-box test cases, each commented with the
path condition it discharges:

- `gsk17/test/whitebox/branch_coverage/test_classify_line.py` — one test per branch
  outcome, so that `b1` and `b2` are each taken and not taken
- `gsk17/test/whitebox/symbolic_execution/test_classify_line.py` — one test per solved
  path condition
- `gsk17/test/whitebox/concolic_testing/test_classify_line.py` — the three iterations in
  order, which together drive every path from a single arbitrary seed

### 7. Coverage

| Measure | Value |
|---|---|
| Paths in the tree | 3 |
| Paths tested | 3 |
| Infeasible paths | 0 |
| Branch outcomes (`b1` true/false, `b2` true/false) | 4 of 4 |
| Statement coverage of `classify_line` | 100% |

Command:

```bash
python -m coverage run -m pytest gsk17/test/whitebox
python -m coverage report -m
```

---

## US02 — `core.scanner.count_leading_spaces(line, tab_width)`

This is the awkward analysis in the project, and the reason is worth stating
before the tree: **this function's path conditions are not linear integer
constraints.**

Every other function analysed here takes integers and compares them with `<`,
`<=` and `==`, so each path condition is a conjunction of linear inequalities
that solves by inspection. This one branches on **character equality** —
`c == " "`, `c == "\t"` — over a symbolic string of unknown length. The
constraints are therefore over a *sequence* of symbolic characters, and the
returned value is a symbolic *expression* in `W = tab_width` rather than a
constant.

That is not a flaw in the design; it is the boundary of it. `core/scanner.py` is
the only module that reads text, and everything downstream consumes the integers
it produces — which is precisely why the rest of this project's symbolic
analyses are tractable by hand. **This module is where the text stops**, and the
cost of that decision is visible here and nowhere else.

### 1. The function, with branches labelled

```python
def count_leading_spaces(line, tab_width):
    if tab_width < 1:              # b1
        raise ValueError(...)
    width = 0
    for character in line:         # L   the character loop
        if character == " ":       # b2
            width = width + 1
        elif character == "\t":    # b3
            width = width + tab_width
        else:                      # b4  (implicit else)
            break
    return width
```

b2, b3 and b4 are an if/elif/else, so the three arms are mutually exclusive and
each iteration takes exactly one.

### 2. Symbolic inputs

`W` for `tab_width`, and `c0`, `c1`, `c2`, … for the characters of the line.

Each `ci` ranges over **three equivalence classes**, because the code can only
distinguish three: space, tab, and anything else. That reduction is what makes
the analysis possible at all — the character domain is otherwise unbounded, but
no path condition can refer to any property of a character beyond which of those
three classes it falls into.

### 2a. Bounded unrolling

As with US12 the loop makes the tree infinite, so the unrolling is bounded at
**k = 2** — lines of 0, 1 and 2 leading characters. k = 2 is sufficient because
it exhibits every pairing of the three arms, and a third character adds no new
decision.

### 3. Symbolic execution tree, bounded at k = 2

```
                  PC: true
                  [b1] W < 1 ?
                 /            \
           true /              \ false
               /                \
      P1: ValueError        PC: W >= 1
      PC: W < 1             [L] any characters ?
                           /                  \
                 exhausted/                    \ taken
                         /                      \
                   P2: 0                   which arm for c0 ?
                   (empty line)          /         |         \
                                   b2 " "      b3 "\t"      b4 other
                                       |           |            |
                                 width = 1   width = W      P3: 0
                                       |           |         (break)
                              [L] more chars ?   [L] more chars ?
                              /     |     \       /     |     \
                        exhausted  " "  "\t"  exhausted " "  "\t"
                        or other        |     or other       |
                            |          |         |           |
                      P4/P6: 1    P8: 2   P9: 1+W  P5/P7: W  P10: W+1
                                                             P11: 2W
```

Eleven paths at k = 2.

### 4. Path conditions and solved witnesses

| Path | Path condition | Witness | Returns |
|---|---|---|---|
| P1 | `W < 1` | `("  x", 0)` | `ValueError` |
| P2 | `W >= 1`, line empty | `("", 4)` | `0` |
| P3 | `W >= 1`, `c0` = other | `("x", 4)` | `0` |
| P4 | `W >= 1`, `c0 = " "`, line ends | `(" ", 4)` | `1` |
| P5 | `W >= 1`, `c0 = "\t"`, line ends | `("\t", 4)` | `W` |
| P6 | `W >= 1`, `c0 = " "`, `c1` = other | `(" x", 4)` | `1` |
| P7 | `W >= 1`, `c0 = "\t"`, `c1` = other | `("\tx", 4)` | `W` |
| P8 | `W >= 1`, `c0 = c1 = " "` | `("  ", 4)` | `2` |
| P9 | `W >= 1`, `c0 = " "`, `c1 = "\t"` | `(" \t", 4)` | `1 + W` |
| P10 | `W >= 1`, `c0 = "\t"`, `c1 = " "` | `("\t ", 4)` | `W + 1` |
| P11 | `W >= 1`, `c0 = c1 = "\t"` | `("\t\t", 4)` | `2W` |

**The general shape.** A prefix of *m* spaces and *n* tabs, terminated either by
a non-whitespace character or by the end of the line, returns **m + nW**. The
eleven bounded paths are the m + n ≤ 2 instances of that expression, and the
inductive step is asserted in the test file for m, n up to 4.

**Witnesses for P5, P9, P10 and P11 are asserted at two values of `W`.** Those
paths return expressions containing `W`, so a single assertion at `W = 4` cannot
distinguish `W` from the constant 4, nor `2W` from 8. The test file checks each
at two tab widths for that reason.

### 4a. Finding 1 — the two whitespace arms commute

P9 and P10 are **different paths with different path conditions**, but both
return `1 + W`. Accumulation is addition, which is commutative, so the *order*
of spaces and tabs within the prefix cannot affect the result — only the counts
can.

That is a property of the returned symbolic expression, not something a set of
examples could establish. It is also exactly what the random-based black-box
test asserts by sampling (`test_adding_n_spaces_to_the_front_adds_exactly_n`
and the mixed-prefix invariant): the two techniques reach the same conclusion
from opposite directions, one by derivation and one by experiment.

### 4b. Finding 2 — a code line always measures zero

P3 is the **only** path reachable when `c0` is neither space nor tab, and it
returns `0` before the accumulator is ever touched.

So `count_leading_spaces` and `classify_line` (US01, same module) agree **by
construction**: a line that `classify_line` reports as code starting in column
one always measures 0 indentation. Two functions are consistent because of their
path structure, not because anyone tested the combination — which is the kind of
claim worth having before the two are composed in `scan_file` (US09, Sprint 3).

### 4c. Finding 3 — the function is total in `tab_width` above 1

**No path condition mentions an upper bound on `W`.** The guard at b1 is the
only constraint on `W` in the entire tree, so there is no tab width, however
large, that reaches a different path or a different arm. The function is total
in its second argument for every `W >= 1`.

This matters for the threshold-editing menu planned in Sprint 3: no validation
beyond `W >= 1` is needed, and that is now a derived fact rather than an
assumption.

**No infeasible paths.** Every path condition above is satisfiable, and the
witness column names an input for each.

### 5. Concolic execution

Concolic execution fits this function **better** than pure symbolic execution
does, and for a specific reason: the concrete run fixes the characters, so each
iteration branches on a known value and the solver only has to pick the *next*
character rather than reason about a symbolic string. The awkward string
constraints described above mostly disappear.

Seeded with `("  \tx = 1", 4)` — two spaces, a tab, then code. A real line of
indented Python, chosen over a minimal input so that the first run exercises all
three arms:

| It. | Input | Path | Collected PC | Branch negated | Next input |
|---|---|---|---|---|---|
| 1 | `("  \tx = 1", 4)` | → 6 | `W>=1, c0=" ", c1=" ", c2="\t", c3=other` | `c0 == " "` → tab arm | `("\t \tx", 4)` |
| 2 | `("\t \tx", 4)` | → 9 | `W>=1, c0="\t", c1=" ", c2="\t", c3=other` | `c1 == " "` → else arm | `("\tx", 4)` |
| 3 | `("\tx", 4)` | P7 → 4 | `W>=1, c0="\t", c1=other` | `c0 == "\t"` → else arm | `("x", 4)` |
| 4 | `("x", 4)` | P3 → 0 | `W>=1, c0=other` | nothing left at this length; **shrink** | `("", 4)` |
| 5 | `("", 4)` | P2 → 0 | `W >= 1` | `W >= 1` → `W < 1` | `("", 0)` |
| 6 | `("", 0)` | P1 | `W < 1` | none left | — |

Six iterations. Each negates the **earliest** branch that still has an
unexplored arm, which is why the walk shortens the whitespace prefix as it goes
rather than lengthening it.

**A three-way branch needs two negations per position, not one.** `c == " "` and
`c == "\t"` are separate decisions in an if/elif, so negating the space arm
leaves *both* the tab arm and the else arm unexplored. Iterations 1 to 3 work
through them in order for `c0`, which is why the walk visits the same character
position three times before moving on. A two-valued branch would have needed one
negation per position; this one needs two, and the iteration count reflects it.

**Character equality is cheap to solve here.** Negating `c0 == " "` requires
only "some character that is not a space", and the solver has a three-class
alphabet to choose from. Each negation therefore has at most two candidate
answers, and the walk is finite per position even though the character domain is
not. That three-class reduction, introduced in section 2, is what makes the
whole technique applicable to a string-handling function.

**What the walk does not reach.** Paths P8 to P11 — every bounded path with
*exactly two* leading whitespace characters — are reached only by the seed, which
has three. The walk shortens the prefix monotonically and never extends it, so
once it drops below that length it cannot generate a two-whitespace line. Those
four paths are covered in `symbolic_execution/`, where the bound is chosen
deliberately rather than arrived at by negation. Reported here rather than
papered over, for the same reason as the missing P2 in the US12 walk: the walk's
reach is a fact about the technique, and concealing it would make the coverage
table a worse piece of evidence, not a better one.

### 6. Resulting test cases

| File | Contents |
|---|---|
| `gsk17/test/whitebox/branch_coverage/test_count_leading_spaces.py` | nine outcomes: the guard, both loop exits, all three arms, and the break stopping accumulation |
| `gsk17/test/whitebox/symbolic_execution/test_count_leading_spaces.py` | one test per bounded path, all three findings, and the m + nW generalisation |
| `gsk17/test/whitebox/concolic_testing/test_count_leading_spaces.py` | the six iterations, plus the single-character-change property of each negation |

### 7. Coverage

| Measure | Value |
|---|---|
| Unrolling bound | k = 2 |
| Paths in the bounded tree | 11 |
| Paths tested | 11 |
| Paths reached by the concolic walk | 6 of 11; P8–P11 covered symbolically |
| Infeasible paths | 0 |
| Branch outcomes | 7 of 7 |
| Statement coverage of `count_leading_spaces` | 100% |

---

## US07 — `core.scanner.is_function_header(line)`

Like US02 this function branches on string properties rather than on integers,
but unlike US02 it has **no loop** — so the tree is finite and complete, and no
bounding is needed. That makes it the cleanest demonstration in the project of
symbolic execution over a non-numeric domain.

### 1. The function, with branches labelled

```python
def is_function_header(line):
    stripped = line.strip()
    if stripped.startswith("#"):              # b1
        return False
    if "(" not in stripped:                   # b2
        return False
    if stripped.startswith("def "):           # b3
        return True
    if stripped.startswith("async def "):     # b4
        return True
    return False                              # b5 (implicit else)
```

### 2. Symbolic inputs

One symbolic string `S`, with `T = S.strip()`.

**The function can observe only four properties of `T`**, so those are the only
atoms any path condition can contain:

| Atom | Meaning |
|---|---|
| `h` | `T` starts with `"#"` |
| `p` | `T` contains `"("` |
| `d` | `T` starts with `"def "` |
| `a` | `T` starts with `"async def "` |

Everything else about the string — its length, its remaining characters, the
contents of the parameter list, whether it is valid Python at all — is invisible
to the function and therefore absent from every path condition.

**That reduction is what makes the analysis finite over an infinite input
domain.** The input space is all strings; the space the function can
*distinguish* is at most `2⁴ = 16` combinations of four booleans, of which
several are unsatisfiable. This is the same technique as the three-class
character reduction in US02, applied to a whole line rather than to one
character.

### 3. Symbolic execution tree

```
                      PC: true
                      [b1] h ?
                     /         \
               true /           \ false
                   /             \
            P1: False        PC: not h
            PC: h            [b2] not p ?
                            /            \
                      true /              \ false
                          /                \
                   P2: False          PC: not h and p
                   PC: not h, not p   [b3] d ?
                                     /        \
                               true /          \ false
                                   /            \
                            P3: True       [b4] a ?
                                           /       \
                                     true /         \ false
                                         /           \
                                  P4: True       P5: False
```

Five leaves, five paths.

### 4. Path conditions and solved witnesses

| Path | Path condition | Witness | Returns |
|---|---|---|---|
| P1 | `h` | `"# def commented_out():"` | `False` |
| P2 | `not h and not p` | `"def no_parens:"` | `False` |
| P3 | `not h and p and d` | `"def withdraw(self, amount):"` | `True` |
| P4 | `not h and p and not d and a` | `"async def fetch(url):"` | `True` |
| P5 | `not h and p and not d and not a` | `"total = compute(x, y)"` | `False` |

**The P1 witness deliberately carries a parenthesis and a keyword.** It would
satisfy P3 were b1 not evaluated first, which is what makes it a witness for
P1 rather than an arbitrary comment. A witness like `"# hello"` would satisfy
the path condition but demonstrate nothing about the ordering.

**The P2 witness is a definition.** `"def no_parens:"` has the keyword and
fails only on the parameter list, so it isolates b2 from b3.

### 4a. Finding 1 — the result is a conjunction, so guard order cannot change it

Collecting the two `True` paths:

```
result  =  not h  and  p  and  (d or a)
```

A conjunction of three independent conditions. Conjunction is commutative, so
**reordering b1 to b4 can change which path an input takes, but never what the
function returns.**

The three `False` leaves partition the complement exactly — no overlap, no gap:

| | Path condition |
|---|---|
| P1 | `h` |
| P2 | `not h and not p` |
| P5 | `not h and p and not d and not a` |

Every string satisfies **exactly one** of the five path conditions. The function
is total; there is no input for which it fails to return.

This is worth deriving rather than assuming, because the guards *look*
order-sensitive. A reader may suspect that testing for `"#"` after the keyword
tests would change the answer for `"# def f():"`. It would change the path — P5
instead of P1 — and not the result. The analysis settles that, and the
black-box tests could not.

### 4b. Finding 2 — `startswith` is load-bearing and `in` would be wrong

`"async def "` **contains** `"def "`, but not at position 0:

```
"async def fetch(url):"      startswith("def ") -> False      "def " in T -> True
```

With `in` instead of `startswith`, b3 would capture every coroutine definition
and b4 would become dead code. That much is harmless, since both return `True`.
But `in` also accepts strings where `"def "` appears anywhere at all:

```
"x = my def (y)"             startswith("def ") -> False      "def " in T -> True
```

which is not a definition and must return `False`. So the two tests are **not
interchangeable**, and the difference is demonstrable rather than hypothetical.

**P4 existing as a separate path from P3 is the structural evidence that
`startswith` was used.** Under `in`, P4 would be unreachable.

### 4c. Finding 3 — `d` and `a` are mutually exclusive, so the tree has five leaves and not six

No string starts with both `"def "` and `"async def "`. The combination
`d and a` is unsatisfiable, so the tree has no leaf for it.

The missing sixth leaf is an **infeasible path**, not an untested one, and it
follows from the atoms being logically linked: `a` implies `not d`. Section 5
shows that linkage has a consequence for the concolic walk.

### 4d. Finding 4 — the empty string needs no special case

`"(" not in ""` is true, so the empty string takes **P2** and returns `False`.

There is no length check anywhere in the function, and none is needed: the guard
that rejects `"def no_parens:"` also rejects `""`, for the same reason. A
derived property rather than a deliberate design decision, and worth recording
so that a later refactor does not add a redundant emptiness guard believing one
to be missing.

### 5. Concolic execution

Seeded with `"def withdraw(self, amount):"` — a real method header from the
design notes, chosen over a minimal input so the first run takes the path the
function exists to recognise.

| It. | Input | Path | Collected PC | Negated |
|---|---|---|---|---|
| 1 | `"def withdraw(self, amount):"` | P3 → True | `not h, p, d` | `d` |
| 2 | `"async def withdraw(self):"` | P4 → True | `not h, p, !d, a` | `a` |
| 3 | `"total = withdraw(self)"` | P5 → False | `not h, p, !d, !a` | `p` |
| 4 | `"total = withdraw"` | P2 → False | `not h, !p` | `h` |
| 5 | `"# total = withdraw"` | P1 → False | `h` | none left |

Five iterations, five paths, **100% path coverage** — and unusually, **with no
backtracking at all.**

That is a consequence of the tree being a **chain** rather than a bush: every
decision has exactly one child that continues, so negating the deepest branch
always lands on a fresh leaf and the stack never has to be unwound. Compare the
US29 walk, which backtracks four times, or US12's, which backtracks twice and
then needs two manual shrink steps because loop length is not a branch
condition.

### 5a. Solving a string constraint is a search, not arithmetic

This is the honest difficulty of the technique on string-handling code.

Negating `T.startswith("def ")` yields "some string not beginning with those
four characters, which still contains `(` and does not begin with `#`". That is
not an equation. There is no solver that returns *the* answer; there is a space
of answers, and something has to choose.

What makes it tractable is the reduction from section 2: the function observes
only four booleans, so the constraint is over four booleans rather than over
characters. Choosing a representative string for a given combination is then
mechanical.

**The strings in this walk were therefore constructed, not computed**, and each
is the minimal edit to its predecessor that flips the negated atom:

| Step | Edit | Effect |
|---|---|---|
| 1 → 2 | prefix `"async "` | `d` false, `a` true |
| 2 → 3 | replace the keyword | neither `d` nor `a` |
| 3 → 4 | drop the parentheses | `p` false |
| 4 → 5 | prefix `"# "` | `h` true |

### 5b. One step flips two atoms, and that is Finding 3 seen from the walk

Step 1 → 2 changes **two** atoms, not one. It cannot do otherwise: `a` implies
`not d`, so there is no input that flips `d` alone and still reaches P4.

That is section 4c's unsatisfiable combination observed dynamically, and it is a
real limit on what a negation step can promise. **A solver can be asked to flip
one branch condition, but where two conditions are logically linked, its answer
flips both.** Every other step in this walk flips exactly one atom, and the test
file asserts both halves of that — the exception at step 1 → 2 and the rule
everywhere else.

The practical consequence: a walk that assumed one-atom-per-step would conclude
that a path had been skipped. It had not. The path that appears to be missing
does not exist.

### 6. Resulting test cases

| File | Contents |
|---|---|
| `gsk17/test/whitebox/branch_coverage/test_is_function_header.py` | the five leaves, plus the empty line reaching b2 and the break on an indented comment |
| `gsk17/test/whitebox/symbolic_execution/test_is_function_header.py` | one test per path, all four findings, and the partition checked by counting satisfied conditions |
| `gsk17/test/whitebox/concolic_testing/test_is_function_header.py` | the five iterations, the atom-flip property, and the absence of backtracking |

Finding 1 is asserted by evaluating the derived expression
`(not h) and p and (d or a)` independently and comparing it against the function
across twenty strings chosen to make each atom true and false in combination —
a derivation checked against the code, rather than the code checked against
itself.

### 7. Coverage

| Measure | Value |
|---|---|
| Paths in the tree | 5 |
| Paths tested | 5 |
| Infeasible paths found | **1** — `d and a` unsatisfiable |
| Concolic backtracking steps required | **0** |
| Branch outcomes | 9 of 9 |
| Statement coverage of `is_function_header` | 100% |
