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

## US19 — `rule_complexity(cc, limit, line)`

*To be completed when the story is implemented.*
