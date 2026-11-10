# Worked Example — Symbolic Execution and Concolic Testing

This is the model to follow for all 36 functions. It works two functions end to end: one
with pure interval branching (`classify_severity`) and one where a later branch re-reads an
earlier variable (`score_from_issues`), which is where concolic testing earns its keep.

Each member repeats this shape for each of their nine functions in their own file,
`docs/symbolic/<username>-symbolic-execution.md`.

---

## Part 1 — `core.severity.classify_severity(actual, limit)`

```python
def classify_severity(actual, limit):
    if actual < 0:                          # b1
        raise ValueError(...)
    if limit < 1:                           # b2
        raise ValueError(...)
    if actual <= limit:                     # b3
        return INFO
    if actual <= limit + limit // 2:        # b4
        return MINOR
    if actual < 2 * limit:                  # b5
        return MAJOR
    return CRITICAL                         # b6 (implicit else)
```

### 1.1 Symbolic inputs

Let `A` and `L` be symbolic integers standing for `actual` and `limit`. The symbolic state
on entry is `{actual -> A, limit -> L}` with path condition `true`.

### 1.2 Symbolic execution tree

```
                         PC: true
                         [b1] A < 0 ?
                        /              \
                 true  /                \  false
                      /                  \
            P1: ValueError           PC: A >= 0
            PC: A < 0                [b2] L < 1 ?
                                    /            \
                             true  /              \ false
                                  /                \
                        P2: ValueError        PC: A >= 0 and L >= 1
                        PC: A >= 0            [b3] A <= L ?
                            and L < 1        /             \
                                      true  /               \ false
                                           /                 \
                                   P3: INFO            PC: ... and A > L
                                   PC: A >= 0           [b4] A <= L + L//2 ?
                                   and L >= 1          /              \
                                   and A <= L   true  /                \ false
                                                     /                  \
                                            P4: MINOR            PC: ... and A > L + L//2
                                            PC: A >= 0            [b5] A < 2L ?
                                            and L >= 1           /            \
                                            and A > L     true  /              \ false
                                            and A <= L+L//2    /                \
                                                        P5: MAJOR        P6: CRITICAL
                                                        PC: A >= 0       PC: A >= 0
                                                        and L >= 1       and L >= 1
                                                        and A > L+L//2   and A > L+L//2
                                                        and A < 2L       and A >= 2L
```

### 1.3 Path conditions and their solutions

Six paths, six leaves, no infeasible paths. Solving each conjunction by hand:

| Path | Path condition | Solved input | Returns |
|---|---|---|---|
| P1 | `A < 0` | `actual=-1, limit=10` | `ValueError` |
| P2 | `A >= 0 and L < 1` | `actual=5, limit=0` | `ValueError` |
| P3 | `A >= 0 and L >= 1 and A <= L` | `actual=10, limit=10` | `INFO` |
| P4 | `A >= 0 and L >= 1 and A > L and A <= L + floor(L/2)` | `actual=11, limit=10` | `MINOR` |
| P5 | `... and A > L + floor(L/2) and A < 2L` | `actual=16, limit=10` | `MAJOR` |
| P6 | `... and A > L + floor(L/2) and A >= 2L` | `actual=20, limit=10` | `CRITICAL` |

**How P5 was solved.** The conjunction is `A >= 0`, `L >= 1`, `A > L`, `A > L + floor(L/2)`,
`A < 2L`. Choosing `L = 10` gives `floor(L/2) = 5`, so the constraints on `A` collapse to
`A > 15` and `A < 20`, and `A > L = 10` is then implied. The feasible set is
`A in {16, 17, 18, 19}`; `A = 16` is taken as the boundary-adjacent witness. The interval is
non-empty for every `L >= 1` except `L = 1`, where `A > 1` and `A < 2` has no integer
solution — so **P5 is infeasible when `L = 1`**, which is why the witness fixes `L = 10`.
That observation is the kind of thing symbolic execution finds and testing by example does
not.

**A note on `L // 2`.** Integer division makes the constraint piecewise rather than strictly
linear: `floor(L/2) = k` means `L = 2k` or `L = 2k+1`. Each path condition involving `b4` is
therefore solved by first fixing the parity of `L`. With `L` fixed to a concrete even value
every remaining constraint is linear in `A`.

### 1.4 Concolic (dynamic symbolic) execution

Concolic execution runs the function on a concrete input while collecting the symbolic path
condition, then negates the last unexplored branch and solves for the next input. Starting
from the arbitrary seed `(actual=5, limit=10)`:

| It. | Concrete input | Path taken | Collected PC | Branch negated | Next input |
|---|---|---|---|---|---|
| 1 | `(5, 10)` | P3 → `INFO` | `A>=0 and L>=1 and A<=L` | `A <= L` → `A > L` | `(11, 10)` |
| 2 | `(11, 10)` | P4 → `MINOR` | `... and A>L and A<=L+L//2` | `A <= L+L//2` → `A > L+L//2` | `(16, 10)` |
| 3 | `(16, 10)` | P5 → `MAJOR` | `... and A>L+L//2 and A<2L` | `A < 2L` → `A >= 2L` | `(20, 10)` |
| 4 | `(20, 10)` | P6 → `CRITICAL` | `... and A>=2L` | backtrack to `b2`: `L >= 1` → `L < 1` | `(5, 0)` |
| 5 | `(5, 0)` | P2 → `ValueError` | `A>=0 and L<1` | backtrack to `b1`: `A >= 0` → `A < 0` | `(-1, 10)` |
| 6 | `(-1, 10)` | P1 → `ValueError` | `A < 0` | none left | — |

Six iterations, six paths, **100% path coverage**. The frontier is explored depth-first and
terminates because the function has no loops, so its execution tree is finite.

### 1.5 Resulting test cases

The six solved inputs become the six test cases in
`<username>/test/whitebox/<WB_SYM>/test_classify_severity.py` and
`<username>/test/whitebox/<WB_CONCOLIC>/test_classify_severity.py`, each commented with the
path condition it discharges:

```python
def test_p5_major_path():
    # PC: A >= 0 and L >= 1 and A > L and A > L + L//2 and A < 2L
    # witness: actual = 16, limit = 10  (feasible interval A in 16..19)
    assert classify_severity(16, 10) == "MAJOR"
```

---

## Part 2 — `core.scoring.score_from_issues(critical, major, minor, info)`

The interesting case: the `critical` input is read twice, once in the all-zero guard and
again in the cap, so two leaves share a variable and the tree is not a simple interval split.

```python
def score_from_issues(critical, major, minor, info):
    for name, count in (...):           # b1 x4: any count < 0
        if count < 0:
            raise ValueError(...)
    if critical == 0 and major == 0 and minor == 0 and info == 0:   # b2
        return 100
    penalty = 15*critical + 8*major + 3*minor + 1*info
    score = 100 - penalty
    if score < 0:                        # b3
        score = 0
    if critical >= 3 and score > 40:     # b4
        return 40
    return score
```

### 2.1 Symbolic inputs and tree

Let `C, M, N, I` be symbolic non-negative integers. Write `S = 100 - (15C + 8M + 3N + I)`.

```
    PC: true
    [b1] C < 0 or M < 0 or N < 0 or I < 0 ?
      true -> P1: ValueError      PC: C < 0  (or M < 0, or N < 0, or I < 0 - four sub-paths)
      false
        [b2] C = 0 and M = 0 and N = 0 and I = 0 ?
          true -> P2: 100         PC: C=0 and M=0 and N=0 and I=0
          false
            [b3] S < 0 ?
              true  -> score := 0
                 [b4] C >= 3 and 0 > 40 ?  -> always false
                      P3: 0                PC: ... and S < 0
              false -> score := S
                 [b4] C >= 3 and S > 40 ?
                      true  -> P4: 40      PC: ... and S >= 0 and C >= 3 and S > 40
                      false -> P5: S       PC: ... and S >= 0 and (C < 3 or S <= 40)
```

### 2.2 Path conditions, solutions and one infeasible path

| Path | Path condition | Solved input | Returns |
|---|---|---|---|
| P1a–d | one of `C<0`, `M<0`, `N<0`, `I<0` | `(-1,0,0,0)` etc. | `ValueError` |
| P2 | `C=0 and M=0 and N=0 and I=0` | `(0,0,0,0)` | `100` |
| P3 | `not all zero and S < 0` | `(10,0,0,0)`: `S = 100-150 = -50` | `0` |
| P4 | `S >= 0 and C >= 3 and S > 40` | `(3,0,0,0)`: `S = 55 > 40` | `40` |
| P5 | `S >= 0 and (C < 3 or S <= 40)` | `(1,2,3,5)`: `S = 55`, `C = 1 < 3` | `55` |

**The infeasible path.** Inside the `S < 0` branch, `score` has already been set to 0, so the
guard `score > 40` in `b4` is `0 > 40`, which is unsatisfiable: the path
`S < 0 and C >= 3 and score > 40` **cannot be taken by any input**. Symbolic execution proves
that, and it is why P3 returns 0 regardless of `C`. A coverage tool will report `b4` as
partially covered there and no test can fix it — the correct response is to record the
infeasibility, not to chase the branch.

**A boundary worth noting.** `C = 3, M = 0, N = 0, I = 0` gives `S = 55`, and the cap returns
40 — the cap *lowers* a score that the penalty arithmetic alone would have passed. `C = 4`
gives `S = 40`, so `S > 40` is false and P5 returns 40 by arithmetic rather than by the cap.
Two different paths produce the same output 40, which is exactly the case that a black-box
test on the output alone cannot distinguish and a white-box path test can.

### 2.3 Concolic execution

| It. | Concrete input | Path | Collected PC | Branch negated | Next input |
|---|---|---|---|---|---|
| 1 | `(0,0,0,0)` | P2 → 100 | `C=0 and M=0 and N=0 and I=0` | all-zero guard → not all zero | `(1,0,0,0)` |
| 2 | `(1,0,0,0)` | P5 → 85 | `not all zero and S>=0 and C<3` | `S >= 0` → `S < 0` | `(10,0,0,0)` |
| 3 | `(10,0,0,0)` | P3 → 0 | `not all zero and S<0` | `C < 3` → `C >= 3` with `S >= 0` | `(3,0,0,0)` |
| 4 | `(3,0,0,0)` | P4 → 40 | `S>=0 and C>=3 and S>40` | `C >= 0` → `C < 0` | `(-1,0,0,0)` |
| 5 | `(-1,0,0,0)` | P1a → ValueError | `C < 0` | `M >= 0` → `M < 0` | `(0,-1,0,0)` |
| 6–8 | `(0,-1,0,0)`, `(0,0,-1,0)`, `(0,0,0,-1)` | P1b–d | one negative each | none left | — |

Eight iterations reach every feasible leaf. The one unreachable branch combination found in
2.2 is recorded as infeasible rather than counted as a coverage gap.

---

## What each member's file must contain, per function

1. The function source with each branch labelled `b1`, `b2`, …
2. The symbolic inputs and the initial symbolic state.
3. The drawn symbolic execution tree, every branch shown.
4. A table of every leaf: path condition as a conjunction, a solved concrete witness, the
   return value.
5. The working for at least one non-obvious solution, as in 1.3 above.
6. Any **infeasible** path, with the proof that it cannot be taken.
7. The concolic table: seed, path, collected condition, branch negated, next input, until
   the frontier is empty.
8. The resulting test cases, each commented with the path condition it discharges, committed
   under `<username>/test/whitebox/<WB_SYM>/` and `<WB_CONCOLIC>/`.
9. Paths found versus paths tested, and the coverage figure from
   `coverage run -m pytest <username>/test/whitebox`.

Write it yourself for your own nine functions: this section of the report is marked
individually.
