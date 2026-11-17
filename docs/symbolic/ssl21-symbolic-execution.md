# Symbolic Execution and Concolic Testing — ssl21 (Saaket)

Member M3, rule engine and severity. One section per function, US19 to US27.
Method follows [WORKED-EXAMPLE.md](WORKED-EXAMPLE.md), which uses this same function as
its illustration; the analysis below is the project record for US26.

---

## US26 — `core.severity.classify_severity(actual, limit)`

### 1. The function, with branches labelled

```python
def classify_severity(actual, limit):
    if actual < 0:                       # b1
        raise ValueError(...)
    if limit < 1:                        # b2
        raise ValueError(...)
    if actual <= limit:                  # b3
        return INFO
    if actual <= limit + limit // 2:     # b4
        return MINOR
    if actual < 2 * limit:               # b5
        return MAJOR
    return CRITICAL                      # b6 (implicit else)
```

### 2. Symbolic inputs

`A` and `L`, symbolic integers. Initial state `{actual -> A, limit -> L}`, path condition
`true`. Every branch compares linear expressions in `A` and `L`, so each path condition is
a conjunction of linear integer constraints and can be solved by hand.

### 3. Symbolic execution tree

```
                    PC: true
                    [b1] A < 0 ?
                   /            \
             true /              \ false
                 /                \
        P1: ValueError        PC: A >= 0
        PC: A < 0             [b2] L < 1 ?
                             /            \
                       true /              \ false
                           /                \
                  P2: ValueError      PC: A>=0 and L>=1
                  PC: A>=0 and L<1    [b3] A <= L ?
                                     /            \
                               true /              \ false
                                   /                \
                            P3: INFO          [b4] A <= L + L//2 ?
                            PC: A<=L         /                  \
                                       true /                    \ false
                                           /                      \
                                   P4: MINOR              [b5] A < 2L ?
                                                         /            \
                                                   true /              \ false
                                                       /                \
                                               P5: MAJOR           P6: CRITICAL
```

Six leaves, six paths.

### 4. Path conditions and solved witnesses

| Path | Path condition | Witness | Returns |
|---|---|---|---|
| P1 | `A < 0` | `(-1, 10)` | `ValueError` |
| P2 | `A >= 0 and L < 1` | `(5, 0)` | `ValueError` |
| P3 | `A >= 0 and L >= 1 and A <= L` | `(10, 10)` | `INFO` |
| P4 | `… and A > L and A <= L + floor(L/2)` | `(11, 10)` | `MINOR` |
| P5 | `… and A > L + floor(L/2) and A < 2L` | `(16, 10)` | `MAJOR` |
| P6 | `… and A > L + floor(L/2) and A >= 2L` | `(20, 10)` | `CRITICAL` |

**Working for P5.** The conjunction is `A >= 0`, `L >= 1`, `A > L`, `A > L + floor(L/2)`,
`A < 2L`. Fixing `L = 10` gives `floor(L/2) = 5`, so the constraints on `A` collapse to
`A > 15` and `A < 20`, and `A > L = 10` is then implied. The feasible set is
`A in {16, 17, 18, 19}`; `A = 16` is taken as the boundary-adjacent witness.

**An infeasible case, found by the analysis.** P5 is **not satisfiable for every `L`**.
With `L = 1` the constraints become `A > 1` and `A < 2`, which has no integer solution — so
at a limit of 1 the MAJOR band cannot be reached at all. The same collapse removes MINOR:
`A <= 1 + 0 = 1` is already consumed by P3. A user who sets a limit of 1 therefore sees
only INFO and CRITICAL.

This is a property of the integer banding rather than a defect, and it is recorded in the
README's known limitations. It is also the clearest demonstration in this project of
symbolic execution finding something that testing by example would not: no amount of
sampling at `L = 10` would have revealed it.

**On `L // 2`.** Integer division makes the `b4` constraint piecewise rather than strictly
linear: `floor(L/2) = k` means `L = 2k` or `L = 2k+1`. Each path condition involving `b4`
is therefore solved by first fixing the parity of `L`; with `L` fixed to a concrete even
value, every remaining constraint is linear in `A`.

### 5. Concolic execution

Seeded with `(5, 10)`:

| It. | Input | Path | Collected PC | Branch negated | Next input |
|---|---|---|---|---|---|
| 1 | `(5, 10)` | P3 → INFO | `A>=0, L>=1, A<=L` | `A <= L` → `A > L` | `(11, 10)` |
| 2 | `(11, 10)` | P4 → MINOR | `… A <= L+L//2` | → `A > L+L//2` | `(16, 10)` |
| 3 | `(16, 10)` | P5 → MAJOR | `… A < 2L` | → `A >= 2L` | `(20, 10)` |
| 4 | `(20, 10)` | P6 → CRITICAL | `… A >= 2L` | backtrack b2: `L >= 1` → `L < 1` | `(5, 0)` |
| 5 | `(5, 0)` | P2 | `A>=0, L<1` | backtrack b1: `A >= 0` → `A < 0` | `(-1, 10)` |
| 6 | `(-1, 10)` | P1 | `A < 0` | none left | — |

Six iterations, six paths, **100% path coverage**. The tree is finite because the function
contains no loops.

### 6. Resulting test cases

`ssl21/test/whitebox/symbolic_execution/test_classify_severity.py` and
`.../concolic_testing/test_classify_severity.py`.

### 7. Coverage

| Measure | Value |
|---|---|
| Paths in the tree | 6 |
| Paths tested | 6 |
| Infeasible path combinations found | 1 — P4 and P5 both unreachable when `L = 1` |
| Statement coverage of `classify_severity` | 100% |

---

## US11 — `core.complexity.cyclomatic_complexity(decision_point_count, bool_operators)`

### 1. The function, with branches labelled

```python
def cyclomatic_complexity(decision_point_count, bool_operators):
    if decision_point_count < 0:          # b1
        raise ValueError(...)
    if bool_operators < 0:                # b2
        raise ValueError(...)
    return decision_point_count + bool_operators + 1
```

### 2. Symbolic inputs

`D` and `B`, symbolic integers. The function has no loops and no nested
conditionals, so the tree is a chain of depth two with three leaves.

### 3. Symbolic execution tree

```
                PC: true
                [b1] D < 0 ?
               /                     true /              \ false
             /                    P1: ValueError        PC: D >= 0
    PC: D < 0             [b2] B < 0 ?
                         /                               true /              \ false
                       /                              P2: ValueError      P3: return D + B + 1
              PC: D>=0 and B<0    PC: D >= 0 and B >= 0
```

### 4. Path conditions and solved witnesses

| Path | Path condition | Witness | Result |
|---|---|---|---|
| P1 | `D < 0` | `(-1, 0)` | `ValueError` |
| P2 | `D >= 0 and B < 0` | `(5, -1)` | `ValueError` |
| P3 | `D >= 0 and B >= 0` | `(7, 3)` | `11` |
| P3' | same, both at the boundary | `(0, 0)` | `1` |

**Working for P2.** The conjunction is `D >= 0`, `B < 0`. The two constraints
are independent, so any non-negative `D` with any negative `B` satisfies it.
`D = 5` is chosen rather than `0` so that the witness also demonstrates the
first guard was evaluated and passed, rather than skipped.

**Working for P3'.** Both constraints are satisfied at their boundary, so the
returned symbolic expression `D + B + 1` evaluates to `0 + 0 + 1 = 1`. The
constant term is the whole point of the measure: a function with no decisions
still has exactly one path through it, so its complexity is 1 and never 0.
Symbolic execution makes that visible as an arithmetic fact about the returned
expression rather than as a remembered special case.

**No infeasible paths.** Each guard constrains a different symbol, so no
conjunction contradicts itself.

### 5. Concolic execution

Seeded with `(4, 2)`:

| It. | Input | Path | Collected PC | Branch negated | Next input |
|---|---|---|---|---|---|
| 1 | `(4, 2)` | P3 → 7 | `D >= 0 and B >= 0` | `B >= 0` → `B < 0` | `(4, -1)` |
| 2 | `(4, -1)` | P2 | `D >= 0 and B < 0` | backtrack to b1: `D >= 0` → `D < 0` | `(-1, 0)` |
| 3 | `(-1, 0)` | P1 | `D < 0` | none left | — |

Three iterations, three paths, **100% path coverage**.

### 6. Resulting test cases

`ssl21/test/whitebox/symbolic_execution/test_cyclomatic_complexity.py` and
`.../concolic_testing/test_cyclomatic_complexity.py`.

### 7. Coverage

| Measure | Value |
|---|---|
| Paths in the tree | 3 |
| Paths tested | 3 |
| Infeasible paths | 0 |
| Statement coverage of `cyclomatic_complexity` | 100% |

---

## US19 — `core.rules.rule_complexity(cc, limit, line)`

This is the first analysis in the project whose tree **crosses a call
boundary**, and the two findings below are only visible because of it. Neither
`rule_complexity` nor `classify_severity` shows them alone.

### 1. The function, with branches labelled

```python
def rule_complexity(cc, limit, line):
    if cc < 0:                           # b1
        raise ValueError(...)
    if limit < 1:                        # b2
        raise ValueError(...)
    if cc <= limit:                      # b3
        return None
    severity = classify_severity(cc, limit)   # inlined below
    return Issue(CODE_COMPLEXITY, severity, line, message)
```

With `classify_severity` (US26) inlined, the decisions reachable from here are:

```python
    if cc <= limit + limit // 2:         # b4  -> MINOR
    if cc < 2 * limit:                   # b5  -> MAJOR
    (implicit else)                      # b6  -> CRITICAL
```

The INFO branch of the callee, guarded by `actual <= limit`, is **not** listed
— see Finding 1.

### 2. Symbolic inputs

`C` (complexity), `L` (limit) and `N` (line), symbolic integers. `N` is carried
into the `Issue` untouched and appears in **no path condition**, so the tree
branches on `C` and `L` alone. That is itself worth recording: the line number
is data, not control, and no choice of `N` can change which path executes.

### 3. Symbolic execution tree

```
                PC: true
                [b1] C < 0 ?
               /            \
         true /              \ false
             /                \
    P1: ValueError        PC: C >= 0
                          [b2] L < 1 ?
                         /            \
                   true /              \ false
                       /                \
              P2: ValueError      PC: C>=0 and L>=1
                                  [b3] C <= L ?
                                 /            \
                           true /              \ false
                               /                \
                        P3: None          PC: ... and C > L
                        (no finding)      [b4] C <= L + L//2 ?
                                         /                  \
                                   true /                    \ false
                                       /                      \
                            P4: Issue MINOR          [b5] C < 2L ?
                                                     /            \
                                               true /              \ false
                                                   /                \
                                      P5: Issue MAJOR      P6: Issue CRITICAL
```

Six leaves, six paths.

### 4. Path conditions and solved witnesses

| Path | Path condition | Witness | Returns |
|---|---|---|---|
| P1 | `C < 0` | `(-1, 10)` | `ValueError` |
| P2 | `C >= 0 and L < 1` | `(5, 0)` | `ValueError` |
| P3 | `C >= 0 and L >= 1 and C <= L` | `(10, 10)` | `None` |
| P4 | `… and C > L and C <= L + floor(L/2)` | `(11, 10)` | `Issue`, MINOR |
| P5 | `… and C > L + floor(L/2) and C < 2L` | `(16, 10)` | `Issue`, MAJOR |
| P6 | `… and C > L + floor(L/2) and C >= 2L` | `(20, 10)` | `Issue`, CRITICAL |

**Working for P5.** The conjunction is `C >= 0`, `L >= 1`, `C > L`,
`C > L + floor(L/2)`, `C < 2L`. Fixing `L = 10` gives `floor(L/2) = 5`, so the
constraints on `C` collapse to `C > 15` and `C < 20`, and `C > L = 10` is then
implied. The feasible set is `C in {16, 17, 18, 19}`; `C = 16` is taken as the
boundary-adjacent witness.

**Working for P2.** `C = 5` is chosen rather than `0` so that the witness also
demonstrates b1 was evaluated and passed rather than skipped.

**On `floor(L/2)`.** Integer division makes b4 and b5 piecewise rather than
strictly linear: `floor(L/2) = k` means `L = 2k` or `L = 2k+1`. Each witness is
therefore solved by first fixing the parity of `L`; with `L` fixed to a
concrete even value, every remaining constraint is linear in `C`.

### 4a. Finding 1 — INFO is unreachable through this rule

`classify_severity` has four outcomes, but its INFO branch is guarded by
`C <= L`. Path P3 has already returned `None` under **exactly** that condition.
Reaching the callee at all requires `C > L`, so the conjunction needed for INFO
is:

```
C > L   and   C <= L          unsatisfiable
```

**`rule_complexity` can therefore never produce an INFO issue.** One quarter of
the severity scale is dead code as reached from this rule.

This is not a defect. It is the correct consequence of a rule that only speaks
when a limit is exceeded: "within the limit" is represented by returning `None`,
not by an issue of the lowest severity. But it is worth knowing for two
reasons. A report consumer that switches on all four bands has an arm this rule
can never trigger; and anyone extending the rule set should expect the same to
hold for every `rule_*` function built on the same shape, because the shape is
what causes it.

### 4b. Finding 2 — at a limit of 1, only CRITICAL survives

The US26 analysis above already showed that `L = 1` collapses two bands:
`C <= 1 + floor(1/2) = 1` is consumed by the INFO branch, and `C > 1 and C < 2`
has no integer solution, so MINOR and MAJOR are both unreachable. Compose that
with Finding 1 and **every issue this rule raises at a limit of 1 is
CRITICAL**, for every complexity above 1. Three of the four bands are gone.

Taken together, the number of severities this rule can emit **depends on the
configured limit**: three for `L >= 2`, one for `L = 1`. A user who sets a
complexity limit of 1 gets a tool that reports everything as critical and
nothing as minor — a configuration hazard rather than a bug, derived rather
than observed, and recorded in the README's known limitations.

This is the clearest demonstration in the project of symbolic execution finding
something testing by example would not. No amount of sampling at `L = 10` shows
it, and the two facts that combine to produce it live in different modules
owned by different members.

### 5. Concolic execution

Seeded with `(C, L) = (5, 10)` — a complexity comfortably inside the limit, so
the walk starts on the no-finding path and has to work outwards:

| It. | Input | Path | Collected PC | Branch negated | Next input |
|---|---|---|---|---|---|
| 1 | `(5, 10)` | P3 → `None` | `C>=0, L>=1, C<=L` | `C <= L` → `C > L` | `(11, 10)` |
| 2 | `(11, 10)` | P4 → MINOR | `… C <= L+L//2` | → `C > L+L//2` | `(16, 10)` |
| 3 | `(16, 10)` | P5 → MAJOR | `… C < 2L` | → `C >= 2L` | `(20, 10)` |
| 4 | `(20, 10)` | P6 → CRITICAL | `… C >= 2L` | backtrack b2: `L >= 1` → `L < 1` | `(20, 0)` |
| 5 | `(20, 0)` | P2 | `C>=0, L<1` | backtrack b1: `C >= 0` → `C < 0` | `(-1, 10)` |
| 6 | `(-1, 10)` | P1 | `C < 0` | none left | — |

Six iterations, six paths, **100% path coverage**. The tree is finite because
neither function contains a loop.

**Why the walk never produces an INFO issue.** Iteration 1 collects `C <= L`
and the solver negates it, so every subsequent input satisfies `C > L`. The
INFO branch requires `C <= L`, so the solver can never be *asked* for an input
reaching it — the constraint was negated away at the first step and nothing in
the walk restores it. Concolic execution therefore **demonstrates** the
unreachability that section 4a **proves**: the walk simply never goes there,
and the reason is visible in the collected condition rather than argued
separately.

### 6. Resulting test cases

| File | Contents |
|---|---|
| `ssl21/test/whitebox/branch_coverage/test_rule_complexity.py` | six branch outcomes, including the three in the inlined callee |
| `ssl21/test/whitebox/symbolic_execution/test_rule_complexity.py` | one test per path, plus both findings as domain sweeps |
| `ssl21/test/whitebox/concolic_testing/test_rule_complexity.py` | the six iterations in generated order |

Both findings are asserted over a wide domain rather than at a single example,
because both are universal claims: Finding 1 sweeps `L` in 1..39 against `C` in
0..119, and Finding 2 sweeps `C` in 2..59 at `L = 1`.

### 7. Coverage

| Measure | Value |
|---|---|
| Paths in the tree (inter-procedural) | 6 |
| Paths tested | 6 |
| Infeasible path combinations found | **2** — INFO unreachable; MINOR and MAJOR unreachable at `L = 1` |
| Branch outcomes | 6 reachable of 7 total; the 7th is proved unreachable |
| Statement coverage of `rule_complexity` | 100% |
