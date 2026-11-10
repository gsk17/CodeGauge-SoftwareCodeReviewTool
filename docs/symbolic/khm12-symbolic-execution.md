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

## US11 — `cyclomatic_complexity(decision_point_count, bool_operators)`

*To be completed when the story is implemented.*
