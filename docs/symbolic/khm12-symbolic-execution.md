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

---

## US20 — `core.rules.rule_nesting(depth, limit, line)`

> `rule_nesting` lives in `core/rules.py`, which Saaket created with US19.
> Ownership on this project is per function rather than per module, agreed at
> the 17 November stand-up before the work started, so this module holds two
> members' functions in the same way `core/complexity.py` holds Saaket's
> `cyclomatic_complexity`.

### 1. The function, with branches labelled

```python
def rule_nesting(depth, limit, line):
    if depth < 0:                        # b1
        raise ValueError(...)
    if limit < 1:                        # b2
        raise ValueError(...)
    if depth <= limit:                   # b3
        return None
    severity = classify_severity(depth, limit)   # inlined below
    return Issue(CODE_NESTING, severity, line, message)
```

With `classify_severity` (US26) inlined:

```python
    if depth <= limit + limit // 2:      # b4  -> MINOR
    if depth < 2 * limit:                # b5  -> MAJOR
    (implicit else)                      # b6  -> CRITICAL
```

### 2. Symbolic inputs

`D` (depth), `L` (limit) and `N` (line), symbolic integers. `N` is carried into
the `Issue` untouched and appears in **no path condition**, so no choice of line
number can change which path executes.

### 3. Symbolic execution tree

```
                PC: true
                [b1] D < 0 ?
               /            \
         true /              \ false
             /                \
    P1: ValueError        PC: D >= 0
                          [b2] L < 1 ?
                         /            \
                   true /              \ false
                       /                \
              P2: ValueError      PC: D>=0 and L>=1
                                  [b3] D <= L ?
                                 /            \
                           true /              \ false
                               /                \
                        P3: None          PC: ... and D > L
                        (no finding)      [b4] D <= L + L//2 ?
                                         /                  \
                                   true /                    \ false
                                       /                      \
                            P4: Issue MINOR          [b5] D < 2L ?
                                                     /            \
                                               true /              \ false
                                                   /                \
                                      P5: Issue MAJOR      P6: Issue CRITICAL
```

Six leaves, six paths.

### 4. Path conditions and solved witnesses

Witnesses use `L = 3`, the project default, rather than US19's `L = 10`.
Nesting limits are small in practice — a configured limit above about 6 would be
unusual — and the bands behave differently at small limits, as section 4c shows.

| Path | Path condition | Witness | Returns |
|---|---|---|---|
| P1 | `D < 0` | `(-1, 3)` | `ValueError` |
| P2 | `D >= 0 and L < 1` | `(5, 0)` | `ValueError` |
| P3 | `D >= 0 and L >= 1 and D <= L` | `(3, 3)` | `None` |
| P4 | `… and D > L and D <= L + floor(L/2)` | `(4, 3)` | `Issue`, MINOR |
| P5 | `… and D > L + floor(L/2) and D < 2L` | `(5, 3)` | `Issue`, MAJOR |
| P6 | `… and D > L + floor(L/2) and D >= 2L` | `(6, 3)` | `Issue`, CRITICAL |

**Working for P5.** With `L = 3`, `floor(L/2) = 1`, so the constraints on `D`
collapse to `D > 4` and `D < 6`. The feasible set is `{5}` — a single integer.
See section 4c.

**Working for P2.** `D = 5` rather than `0`, so that the witness also
demonstrates b1 was evaluated and passed rather than skipped.

### 4a. This tree is structurally identical to US19's

That is the point of the analysis rather than a shortcut in writing it. The two
rules were written separately, by different members, a day apart. Their trees
coming out the same shape below b3 is what demonstrates the shared contract was
actually honoured — had either re-implemented the banding instead of calling
`classify_severity`, the trees would diverge there.

The black-box tests assert the same thing from the outside: a test in
`khm12/test/blackbox/equivalence_partitioning/` checks that the two rules return
identical severities for identical `(actual, limit)` pairs while carrying
different codes. The symbolic analysis explains *why* that holds rather than
merely observing that it does.

### 4b. The two US19 findings are properties of the rule shape

Both findings from the US19 analysis reappear here unchanged, which establishes
that they belong to the **pattern** rather than to `rule_complexity`:

**Finding 1 — INFO is unreachable.** The INFO branch of `classify_severity`
requires `D <= L`, and P3 has already returned `None` under exactly that
condition. `D > L and D <= L` is unsatisfiable, so no issue this rule raises
can carry INFO.

**Finding 2 — at a limit of 1, only CRITICAL survives.** With `L = 1`: MINOR
requires `D <= 1 + floor(1/2) = 1`, which P3 consumes; MAJOR requires
`D > 1 and D < 2`, which has no integer solution.

Any future `rule_*` function built on this shape will have both properties
without anyone needing to re-derive them. That is a more useful result than
either individual finding.

### 4c. Finding 3 — the band collapse is worse at small limits, and nesting limits are small

New here, and specific to nesting rather than inherited from US19.

Counting the reachable severities at each realistic limit:

| `L` | MINOR band | MAJOR band | CRITICAL | Reachable bands |
|---|---|---|---|---|
| 1 | empty — `D <= 1` consumed by P3 | empty — `D > 1 and D < 2` | `D >= 2` | **1** |
| 2 | `{3}` | empty — `D > 3 and D < 4` | `D >= 4` | **2** |
| 3 | `{4}` | `{5}` | `D >= 6` | **3** |
| 4 | `{5, 6}` | `{7}` | `D >= 8` | 3 |
| 10 | `{11…15}` | `{16…19}` | `D >= 20` | 3 |

At `L = 2` the MAJOR band is **empty**: it requires `D > 2 + 1 = 3` and
`D < 4`, which has no integer solution. So the severity scale does not reach
its full three reachable bands until a limit of **3**.

**The project default for `nesting_limit` is exactly 3** — the smallest limit at
which this rule can express the whole range it is capable of.

That is luck rather than design. The default was chosen in the implementation
plan as a reasonable nesting depth for Python, not by analysing the bands. It is
recorded here because anyone adjusting it needs to know that **lowering it to 2
silently removes a severity band, and lowering it to 1 removes two** — and
because `Thresholds.validate` currently permits both.

Note also from the table that at `L = 3` the MINOR and MAJOR bands each hold a
**single integer**. At the project default, a nesting depth of 4 is the only
MINOR finding possible and 5 the only MAJOR one. Everything from 6 upwards is
CRITICAL. The scale is far coarser in practice than its four names suggest.

**No infeasible paths at `L >= 3`.** All six are satisfiable. At `L = 2` paths
P5 is infeasible, and at `L = 1` both P4 and P5 are — which is Finding 2 and
Finding 3 stated as a path property.

### 5. Concolic execution

Seeded with `(D, L) = (1, 3)` — a shallow function inside the default limit:

| It. | Input | Path | Collected PC | Branch negated | Next input |
|---|---|---|---|---|---|
| 1 | `(1, 3)` | P3 → `None` | `D>=0, L>=1, D<=L` | `D <= L` → `D > L` | `(4, 3)` |
| 2 | `(4, 3)` | P4 → MINOR | `… D <= L+L//2` | → `D > L+L//2` | `(5, 3)` |
| 3 | `(5, 3)` | P5 → MAJOR | `… D < 2L` | → `D >= 2L` | `(6, 3)` |
| 4 | `(6, 3)` | P6 → CRITICAL | `… D >= 2L` | backtrack b2: `L >= 1` → `L < 1` | `(6, 0)` |
| 5 | `(6, 0)` | P2 | `D>=0, L<1` | backtrack b1: `D >= 0` → `D < 0` | `(-1, 3)` |
| 6 | `(-1, 3)` | P1 | `D < 0` | none left | — |

Six iterations, six paths, **100% path coverage**.

**At this limit the walk does not sample the bands — it enumerates them.**
Iteration 1 negates `D <= 3` and the solver returns 4, which section 4c shows is
the *entire* MINOR band. Iteration 2 negates `D <= 4` and returns 5, the entire
MAJOR band. Every generated input is the tightest solution of its constraint,
and at `L = 3` the tightest solution is the only solution.

That is a property of small limits rather than of the technique, and it is why
this walk is worth running despite having the same tree as US19's. US19 seeds at
`L = 10`, where each band holds four or five values and the solver returns a
boundary *within* a band; here the boundary **is** the band. The two walks
exercise identical paths under opposite conditions, and between them they
demonstrate that the band widths are a function of the limit and not of the
code.

**Iteration 5 keeps `D = 6` rather than resetting it.** Backtracking to b2
negates only `L >= 1`; nothing requires `D` to change, so the solver leaves it
where it was. A solver that minimised every variable would have returned
`(0, 0)` and taken the same path — the choice is unconstrained, which is worth
noting because it means the walk is not unique.

### 6. Resulting test cases

| File | Contents |
|---|---|
| `khm12/test/whitebox/branch_coverage/test_rule_nesting.py` | six branch outcomes, including the three in the inlined callee |
| `khm12/test/whitebox/symbolic_execution/test_rule_nesting.py` | one test per path, all three findings, and the band count at each limit |
| `khm12/test/whitebox/concolic_testing/test_rule_nesting.py` | the six iterations, plus the proof that the bands were enumerated rather than sampled |

Finding 1 is additionally asserted **side by side with `rule_complexity`**,
sweeping both functions over the same domain and checking they agree on every
input. That is the test that would fail if the two rules ever diverged.

### 7. Coverage

| Measure | Value |
|---|---|
| Paths in the tree (inter-procedural) | 6 |
| Paths tested | 6 |
| Infeasible path combinations found | **3** — INFO unreachable at any limit; P5 infeasible at `L = 2`; P4 and P5 both infeasible at `L = 1` |
| Branch outcomes | 6 reachable of 7 total; the 7th is proved unreachable |
| Statement coverage of `rule_nesting` | 100% |

---

## US14 — `core.complexity.parameter_count_rating(param_count, limit)`

After US10 (a counting loop) and US12 (a loop needing k=2 unrolling), this is
this member's first **loop-free** function. The tree is finite and complete with
no bounding, so the analysis is exact rather than bounded.

### 1. The function, with branches labelled

```python
def parameter_count_rating(param_count, limit):
    if param_count < 0:                     # b1
        raise ValueError(...)
    if limit < 1:                           # b2
        raise ValueError(...)
    if param_count <= limit:                # b3
        return RATING_OK
    if param_count <= 2 * limit:            # b4
        return RATING_MANY
    return RATING_EXCESSIVE                 # b5 (implicit else)
```

### 2. Symbolic inputs

Two symbolic integers, `P` for `param_count` and `L` for `limit`.

### 3. The execution tree

| Path | Path condition | Witness | Returns |
|---|---|---|---|
| P1 | `P < 0` | `(-1, 0)` | ValueError, `param_count` |
| P2 | `P >= 0, L < 1` | `(3, 0)` | ValueError, `limit` |
| P3 | `P >= 0, L >= 1, P <= L` | `(3, 4)` | `OK` |
| P4 | `P >= 0, L >= 1, P > L, P <= 2L` | `(6, 4)` | `MANY` |
| P5 | `P >= 0, L >= 1, P > 2L` | `(9, 4)` | `EXCESSIVE` |

Five leaves, five paths. The sixth syntactic combination, `P <= L and P > 2L`,
is unsatisfiable for every `L >= 1` and is an **infeasible path** rather than an
untested one.

### 4. Finding 1 — no valid limit empties a band, which `core.severity` cannot say

Reading band sizes straight off the path conditions:

| Band | Membership | Size |
|---|---|---|
| OK | `{ 0 .. L }` | `L + 1` |
| MANY | `{ L+1 .. 2L }` | `L` |
| EXCESSIVE | `{ 2L+1 .. }` | unbounded |

`L >= 1` holds on every path that reaches a rating, so MANY always holds at
least one value and **all three ratings are reachable at every valid limit.** At
the minimum limit of 1: OK = {0, 1}, MANY = {2}, EXCESSIVE = {3, …}.

This is worth proving because the sibling function in the project does not have
the property. `classify_severity` bands with `limit + limit // 2` and
`2 * limit`:

| Band | Membership | Size | Empty when |
|---|---|---|---|
| MINOR | `{ L+1 .. L + L//2 }` | `L // 2` | `L = 1` |
| MAJOR | `{ L + L//2 + 1 .. 2L-1 }` | `L - L//2 - 1` | `L = 1, 2` |

A project configuring a limit of 1 therefore gets CRITICAL for every finding,
and one configuring 2 can never see MAJOR. **This function needs no such fix**,
and the difference is not a matter of care but of arithmetic: integer halving
collapses, doubling does not.

### 5. Finding 2 — the OK band is one wider than MANY, and both comparisons cause it

b3 and b4 are both inclusive, which puts `L` in OK and `2L` in MANY — an
asymmetry of exactly one value whose relative size falls away as the limit
rises:

| `L` | OK holds | MANY holds |
|---|---|---|
| 1 | 2 | 1 |
| 4 | 5 | 4 |
| 20 | 21 | 20 |

So "within the limit" is slightly more generous than "over by no more than the
limit", and at a small limit markedly so. Not a defect — inclusivity at b3 is
the documented contract — but the two bands are not the equal halves the phrase
"up to twice the limit" suggests.

### 6. Finding 3 — monotonicity in both arguments, provable from the path conditions

Each path condition is an interval in `P` and a half-plane in `L`, and the
intervals are ordered. Writing OK < MANY < EXCESSIVE:

* **for fixed `L`, the rating is non-decreasing in `P`** — adding a parameter
  can never improve a rating;
* **for fixed `P`, the rating is non-increasing in `L`** — raising the limit can
  never worsen a rating.

Neither is checked by any black-box test in isolation; both are properties of
the family of paths rather than of any one of them. The random-based suite
asserts the first as an invariant over sampled pairs, which is *evidence* for
it; this is a *proof* of it.

### 7. Finding 4 — almost every input is EXCESSIVE, so the rating cannot rank bad signatures

Two of the three bands are finite and the third is unbounded, so the rating maps
a finite set to OK and MANY and an infinite set to EXCESSIVE. At `L = 4`, nine
parameters, ninety and nine hundred are all EXCESSIVE.

The docstring states this is intended. The analysis makes the cost precise:
**the rating is not an ordering on over-limit signatures**, so a report cannot
use it to sort the worst offenders, and `max()` over a file's ratings tells a
reviewer only that at least one signature is beyond `2L`.

### 8. Finding 5 — at exactly twice the limit, this function says MANY and `classify_severity` says CRITICAL

A parameter count can be graded twice in this tool — by this function, and by
`core.rules.rule_params`, which routes through `classify_severity`. The two
band structures are not aligned, and the misalignment is provable at one point.
Substituting `P = 2L`, for any `L >= 1`:

```
parameter_count_rating(2L, L)
    2L <= L         false for L >= 1
    2L <= 2L        TRUE                 -> MANY, the kindest over-limit band

classify_severity(2L, L)
    2L <= L                 false
    2L <= L + L//2          false, since L + L//2 < 2L for all L >= 1
    2L < 2L                 false
                                         -> CRITICAL, the harshest band
```

So for **every** valid limit, the count `P = 2L` is simultaneously MANY and
CRITICAL. More broadly, the whole MANY band spans all three reachable
severities. At `L = 4`:

| `P` | Rating | Severity |
|---|---|---|
| 5, 6 | MANY | MINOR |
| 7 | MANY | MAJOR |
| 8 | MANY | **CRITICAL** |
| ≥ 9 | EXCESSIVE | CRITICAL |

**The rating is strictly coarser than the severity and disagrees with it about
where the serious boundary lies** — EXCESSIVE begins at `2L+1`, CRITICAL at
`2L`. Neither is wrong against its own documented contract; they are two
independent gradings of one measurement, and a report showing both would appear
to contradict itself for one parameter count in every configuration.

Raised for the Sprint 2 review. Either the rating is dropped from the report in
favour of the severity, or b4 becomes `param_count < 2 * limit` so the
boundaries coincide. The second is a one-character change and would shrink MANY
to `L - 1` values — **which would empty it at `L = 1` and recreate exactly the
defect finding 1 shows this function currently avoids.** The options are not
both free, and that is the substance of the finding.

### 9. Finding 6 — a doubly-invalid call reports only the first fault

b1 precedes b2, so `(-1, 0)` raises about `param_count` and never mentions that
the limit is also unusable. A caller correcting the reported fault and
re-running meets a second error rather than a result. Shared with every
validated function in the project; stated here because P1's witness is
deliberately doubly-invalid, so the test pins the order rather than accidentally
depending on it.

### 10. Concolic walk

Seeded with `(3, 4)` — the signature of `classify_line(line)` plus two, against
the project's default parameter limit of 4.

| It. | Input | Path | Collected PC | Negated | Next |
|---|---|---|---|---|---|
| 1 | `(3, 4)` | P3 | `P>=0, L>=1, P<=L` | `P<=L` | `(5, 4)` |
| 2 | `(5, 4)` | P4 | `P>=0, L>=1, P>L, P<=2L` | `P<=2L` | `(9, 4)` |
| 3 | `(9, 4)` | P5 | `P>=0, L>=1, P>L, P>2L` | `L>=1` | `(9, 0)` |
| 4 | `(9, 0)` | P2 | `P>=0, L<1` | `P>=0` | `(-1, 0)` |
| 5 | `(-1, 0)` | P1 | `P<0` | — | — |

**Five iterations, five paths, no backtracking** — a chain, as in US07 and US04.
The contrast is with the US12 walk, whose loop made the tree a bush and cost two
backtracks and two manual shrink steps.

**The solver had freedom at every step, and it was used differently each time.**
Unlike US04, where one negation admitted a unique model, every system here has
infinitely many solutions:

* **Iterations 1 and 2 held `L` fixed at 4 and moved `P`.** The negated atom
  mentions both variables, so `(3, 2)` would satisfy iteration 1's negation as
  readily as `(5, 4)`. Moving `P` was chosen because holding the configuration
  still and varying the measurement is what a reader comparing two adjacent
  tests expects, and it keeps the five witnesses on one line of the plane.
* **Iteration 3 could not hold `L` fixed**, since the negated atom is `L >= 1`
  itself. It moved `L` and then checked the carried terms were still
  satisfiable: `P > L` and `P > 2L` with `L = 0` reduce to `P > 0`, which
  `P = 9` meets, so the prefix survived unchanged.
* **Iteration 4 negated `P >= 0` and discarded everything about `L`**, since
  `L < 1` belonged to the negated branch's sibling. `(-1, 0)` keeps the previous
  `L` only as a convenience; `(-1, 7)` reaches the same leaf.

Recorded because "the solver returns a model" hides a real choice, and the
choice decides whether the resulting suite reads as a coherent sequence or as
five unrelated numbers. Both are 100% path coverage.

**What the walk cannot reach.** All five paths, and only at `L = 4`. Findings 1,
2 and 5 are all about how the bands change with `L`, and every one is invisible
here — finding 5 needs `P = 8`, and the walk went from 5 straight to 9. **A
different limit is a different band width, not a different path**, so no
negation ever demands a new value of `L` except iteration 3, which demands an
invalid one.

### 11. Coverage

| Measure | Value |
|---|---|
| Paths in the tree | 5 |
| Paths tested | 5 |
| Infeasible paths found | **1** — `P <= L and P > 2L` unsatisfiable for all `L >= 1` |
| Concolic backtracking steps required | **0** |
| Branch outcomes | 8 of 8 |
| Statement coverage of `parameter_count_rating` | 100% |
| Cross-module findings | **1** — `P = 2L` is MANY and CRITICAL at once, for every limit |
