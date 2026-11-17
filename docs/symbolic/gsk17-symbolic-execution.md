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
