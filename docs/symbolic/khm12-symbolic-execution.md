# Symbolic Execution and Concolic Testing — khm12 (Kasam)

Member M2, complexity metrics. One section per function, US10 to US18.
Method follows [WORKED-EXAMPLE.md](WORKED-EXAMPLE.md).

---

## US10 — `core.complexity.decision_points(...)`

### 1. The function, with branches labelled

```python
def decision_points(if_count, elif_count, for_count, while_count,
                    except_count, comprehension_count):
    counts = (...)                      # six (name, value) pairs
    for name, value in counts:          # loop, bounded at 6
        if value < 0:                   # b1, evaluated once per iteration
            raise ValueError(...)
    return if_count + elif_count + for_count + while_count \
         + except_count + comprehension_count
```

### 2. Symbolic inputs

Let `I, E, F, W, X, C` be symbolic integers for the six counts, in the order the guard
loop visits them. The loop is bounded at six iterations, so the execution tree is finite
and of depth six — no unrolling limit is needed.

### 3. Symbolic execution tree

```
                     PC: true
                     [b1 @ 1] I < 0 ?
                    /                \
              true /                  \ false
                  /                    \
          P1: ValueError          [b1 @ 2] E < 0 ?
          PC: I < 0              /                \
                           true /                  \ false
                               /                    \
                       P2: ValueError         [b1 @ 3] F < 0 ?
                       PC: I>=0 and E<0      /               \
                                       ... and so on through W, X, C ...
                                                             \
                                                       P0: return I+E+F+W+X+C
                                                       PC: I>=0 and E>=0 and
                                                           F>=0 and W>=0 and
                                                           X>=0 and C>=0
```

Seven leaves: six error paths, one for each position at which the **first** negative value
appears, plus the success path where none is negative.

### 4. Path conditions and solved witnesses

| Path | Path condition | Witness | Result |
|---|---|---|---|
| P1 | `I < 0` | `(-1, 0, 0, 0, 0, 0)` | `ValueError` |
| P2 | `I >= 0 and E < 0` | `(0, -1, 0, 0, 0, 0)` | `ValueError` |
| P3 | `I, E >= 0 and F < 0` | `(0, 0, -5, 0, 0, 0)` | `ValueError` |
| P4 | `I, E, F >= 0 and W < 0` | `(0, 0, 0, -1, 0, 0)` | `ValueError` |
| P5 | `I, E, F, W >= 0 and X < 0` | `(1, 1, 1, 1, -1, 0)` | `ValueError` |
| P6 | `I, E, F, W, X >= 0 and C < 0` | `(1, 1, 1, 1, 1, -1)` | `ValueError` |
| P0 | all six `>= 0` | `(3, 2, 1, 1, 1, 2)` | `10` |

**Working for P6.** The conjunction is `I>=0, E>=0, F>=0, W>=0, X>=0, C<0`. Every
constraint is independent, so the solution is immediate: set the first five to any
non-negative value and `C` to any negative one. `(1,1,1,1,1,-1)` is taken rather than
`(0,0,0,0,0,-1)` because the non-zero values prove the loop genuinely passed over five
valid entries rather than short-circuiting.

**Working for P0.** The return value is the symbolic expression `I+E+F+W+X+C` under a
conjunction of six independent lower bounds, so every assignment of non-negative integers
is a witness. `(3,2,1,1,1,2)` is chosen so the six addends are distinguishable — had the
implementation dropped or doubled a term, a witness of all ones would still produce a
plausible total and hide it.

**No infeasible paths.** Each guard constrains a different symbol, so no conjunction
contradicts itself.

### 5. Concolic execution

Seeded with `(1, 1, 1, 1, 1, 1)`:

| It. | Concrete input | Path | Collected PC | Branch negated | Next input |
|---|---|---|---|---|---|
| 1 | `(1,1,1,1,1,1)` | P0 → 6 | all six `>= 0` | `C >= 0` → `C < 0` | `(1,1,1,1,1,-1)` |
| 2 | `(1,1,1,1,1,-1)` | P6 | `… X>=0 and C<0` | `X >= 0` → `X < 0` | `(1,1,1,1,-1,0)` |
| 3 | `(1,1,1,1,-1,0)` | P5 | `… W>=0 and X<0` | `W >= 0` → `W < 0` | `(1,1,1,-1,0,0)` |
| 4 | `(1,1,1,-1,0,0)` | P4 | | `F >= 0` → `F < 0` | `(1,1,-1,0,0,0)` |
| 5 | `(1,1,-1,0,0,0)` | P3 | | `E >= 0` → `E < 0` | `(1,-1,0,0,0,0)` |
| 6 | `(1,-1,0,0,0,0)` | P2 | | `I >= 0` → `I < 0` | `(-1,0,0,0,0,0)` |
| 7 | `(-1,0,0,0,0,0)` | P1 | `I < 0` | none left | — |

Seven iterations, seven paths, **100% path coverage**. The frontier empties because the
loop is bounded.

### 6. Resulting test cases

`khm12/test/whitebox/symbolic_execution/test_decision_points.py` and
`.../concolic_testing/test_decision_points.py`, each commented with the path condition it
discharges.

### 7. Coverage

| Measure | Value |
|---|---|
| Paths in the tree | 7 |
| Paths tested | 7 (5 directly, 2 more by the concolic sequence) |
| Infeasible paths | 0 |
| Statement coverage of `decision_points` | 100% |

---

## US12 — `core.complexity.max_nesting_depth(depths)`

> **US11 `cyclomatic_complexity` is not in this document.** It was reassigned to
> Saaket (M3) in the Sprint 1 point rebalance — the US20 ↔ US11 swap recorded in
> the README — so its analysis is in
> [ssl21-symbolic-execution.md](ssl21-symbolic-execution.md). Ownership on this
> project is per function, not per module, and `core/complexity.py` therefore
> holds one function analysed by another member.

This is the **first looping function** analysed in the project, which changes
the method. Every earlier analysis produced a finite, complete tree; this one
cannot, and section 2a explains what is done instead.

### 1. The function, with branches labelled

```python
def max_nesting_depth(depths):
    for depth in depths:              # L1  the validation loop
        if depth < 0:                 # b1
            raise ValueError(...)
    deepest = 0
    for depth in depths:              # L2  the scan loop
        if depth > deepest:           # b2
            deepest = depth
    return deepest
```

Four decisions, not two: a loop header is itself a two-outcome decision —
entered, or exhausted — so L1 and L2 fork the tree as much as b1 and b2 do.

### 2. Symbolic inputs

`D0`, `D1`, … symbolic integers, one per list element, plus the list length `n`.

### 2a. The tree is infinite, so the unrolling is bounded

The input is a list of unknown length, so the loops can be entered any number
of times and the tree has no finite depth. There is no complete path set to
enumerate.

The standard treatment is **bounded unrolling**: analyse small concrete lengths
exhaustively, then argue the general case by induction over the pattern the
bounded cases establish. The bound here is **k = 2** — lengths 0, 1 and 2 —
chosen because k = 2 is the smallest bound at which every combination of b1 and
b2 appears, and no larger bound introduces a new decision. Length 3 only adds
another instance of b2 compared against a larger `deepest`.

**Why the bound is sound.** Both loops iterate the input with no early exit, and
the only state carried between iterations is `deepest`, updated by a monotone
operation — it never decreases. So the behaviour at length *n* is the behaviour
at length 2 with one more comparison, and nothing in the longer case can
invalidate a conclusion drawn from the shorter. The inductive step is asserted
in the test file rather than left as prose.

### 3. Symbolic execution tree, bounded at k = 2

```
                          case split on n
            ┌───────────────────┼───────────────────┐
          n = 0               n = 1               n = 2
            │                   │                   │
      L1 exhausted        [b1] D0 < 0 ?        [b1] D0 < 0 ?
      L2 exhausted        /          \          /          \
            │       true /            \ false  true         \ false
        P1: 0           /              \        │            \
                 P2: ValueError   PC: D0>=0   P5: ValueError  [b1] D1 < 0 ?
                                 [b2] D0>0 ?                  /          \
                                 /        \             true /            \ false
                           true /          \ false          /              \
                               /            \        P6: ValueError   PC: both >= 0
                         P3: D0          P4: 0                        [b2] D0 > 0 ?
                                      (D0 forced                      /          \
                                       to 0)                   true  /            \ false
                                                                     │             │
                                                          [b2] D1 > D0 ?   [b2] D1 > 0 ?
                                                           /        \       /        \
                                                     P7: D1    P8: D0  P9: D1   P10: 0
```

Ten paths at k = 2.

### 4. Path conditions and solved witnesses

| Path | n | Path condition | Witness | Returns |
|---|---|---|---|---|
| P1 | 0 | *(none)* | `[]` | `0` |
| P2 | 1 | `D0 < 0` | `[-1]` | `ValueError` |
| P3 | 1 | `D0 >= 0 and D0 > 0` | `[7]` | `D0` = 7 |
| P4 | 1 | `D0 >= 0 and D0 <= 0` | `[0]` | `0` |
| P5 | 2 | `D0 < 0` | `[-1, 3]` | `ValueError` |
| P6 | 2 | `D0 >= 0 and D1 < 0` | `[3, -1]` | `ValueError` |
| P7 | 2 | both `>= 0`, `D0 > 0`, `D1 > D0` | `[2, 5]` | `D1` = 5 |
| P8 | 2 | both `>= 0`, `D0 > 0`, `D1 <= D0` | `[5, 2]` | `D0` = 5 |
| P9 | 2 | both `>= 0`, `D0 <= 0`, `D1 > 0` | `[0, 4]` | `D1` = 4 |
| P10 | 2 | both `>= 0`, `D0 <= 0`, `D1 <= 0` | `[0, 0]` | `0` |

**Working for P8.** The conjunction is `D0 >= 0`, `D1 >= 0`, `D0 > 0`,
`D1 <= D0`. Fixing `D0 = 5` leaves `D1 in {0, …, 5}`; `D1 = 2` is taken. The
returned symbolic value is `D0`, not a constant — the witness demonstrates
which variable the function returns, which a single-value assertion would not.

**P5 and P6 are distinct for a structural reason.** P5 rejects on the first
element, so `D1` is never examined. P6 rejects on the second, which is only
reachable because validation is a **complete pass** over the list before the
scan begins. Fusing the two loops would still give the same answers here, since
the scan has no early exit, but the separation is what makes "a negative
anywhere is rejected, even when it is not the maximum" true by construction
rather than by argument.

### 4a. Finding — two path conditions have a unique solution

`deepest` is initialised to `0`, and validation has already established
`D0 >= 0`. So the FALSE branch of b2 on the **first** iteration requires:

```
D0 >= 0   and   D0 <= 0        forces D0 = 0 exactly
```

Unlike every other path condition in this function, P4 has a **single
solution** rather than an interval. The same collapse applies to `D1` in P9 and
to both variables in P10.

So the false branch of the scan comparison is, on the first iteration,
reachable by exactly one input value. A test suite that only sampled positive
depths would never execute it: the random-based black-box test generates depths
in 0..20 and would hit a leading zero only by chance, roughly one list in
twenty-one.

That is the one thing this analysis found that the black-box tests would not
have, and it is why `[0]`, `[0, 0]` and `[0, 4]` appear as explicit cases in the
white-box files.

**No infeasible paths.** Every path condition above has at least one solution,
and the witness column names it. Three of the ten have exactly one.

### 5. Concolic execution

Seeded with `[3, 1]` — two elements, descending, both valid:

| It. | Input | Path | Collected PC | Branch negated | Next input |
|---|---|---|---|---|---|
| 1 | `[3, 1]` | P8 → 3 | `D0>=0, D1>=0, D0>0, D1<=D0` | `D1<=D0` → `D1>D0` | `[3, 5]` |
| 2 | `[3, 5]` | P7 → 5 | `… D1 > D0` | `D0>0` → `D0<=0` | `[0, 5]` |
| 3 | `[0, 5]` | P9 → 5 | `… D0<=0, D1>0` | `D1>0` → `D1<=0` | `[0, 0]` |
| 4 | `[0, 0]` | P10 → 0 | `… D1<=0` | backtrack to validation: `D1>=0` → `D1<0` | `[0, -1]` |
| 5 | `[0, -1]` | P6 | `D0>=0, D1<0` | backtrack: `D0>=0` → `D0<0` | `[-1, -1]` |
| 6 | `[-1, -1]` | P5 | `D0 < 0` | nothing left at n = 2; **shrink** | `[0]` |
| 7 | `[0]` | P4 → 0 | `D0>=0, D0<=0` | `D0<=0` → `D0>0` | `[7]` |
| 8 | `[7]` | P3 → 7 | `D0>=0, D0>0` | nothing left; **shrink** | `[]` |
| 9 | `[]` | P1 → 0 | *(none)* | none left | — |

Nine iterations, **nine of the ten bounded paths**.

**The one path the walk does not reach is P2**, a single negative element.
Iteration 7 arrives at length 1 carrying `D0 >= 0` already on the path, and
nothing in the remaining walk negates it at that length. It is covered
explicitly at the end of the concolic test file rather than quietly added to
the walk — reporting partial coverage honestly is more useful than claiming 100%
and padding the table.

**The length is not a symbolic variable.** Concolic execution can only negate
*branch conditions*, and the number of loop iterations is not one — it is a
property of the concrete input. So the walk cannot solve its way from n = 2 to
n = 1: the shrink steps at iterations 6 and 8 are decisions made by the test
designer, not by the solver.

That is the honest limitation of the technique on looping code, and it is worth
stating plainly. Concolic execution explores the paths *within* a given
unrolling exhaustively and cheaply — no reasoning about symbolic lists is needed
once the length is fixed — but moving between unrollings is manual. The bounded
symbolic analysis in section 3 is what covers the choice of *n*; the walk covers
everything else. The two techniques are complementary here in a way they were
not for any loop-free function in this project.

### 6. Resulting test cases

| File | Contents |
|---|---|
| `khm12/test/whitebox/branch_coverage/test_max_nesting_depth.py` | eight outcomes: both loop headers, b1 both ways, b2 both ways including the first-iteration special case |
| `khm12/test/whitebox/symbolic_execution/test_max_nesting_depth.py` | one test per bounded path, plus the inductive step beyond k = 2 |
| `khm12/test/whitebox/concolic_testing/test_max_nesting_depth.py` | the nine iterations, plus P2 covered separately and labelled as such |

### 7. Coverage

| Measure | Value |
|---|---|
| Unrolling bound | k = 2 |
| Paths in the bounded tree | 10 |
| Paths tested | 10 |
| Paths reached by the concolic walk | 9 of 10 |
| Path conditions with a unique solution | 3 — P4, P9, P10 |
| Infeasible paths | 0 |
| Statement coverage of `max_nesting_depth` | 100% |
