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

## US02 — `count_leading_spaces(line, tab_width)`

*To be completed when the story is implemented.*
