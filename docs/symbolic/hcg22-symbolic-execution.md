# Symbolic Execution and Concolic Testing — hcg22 (Harshita)

Member M4, scoring, history and persistence. One section per function, US28 to US36.
Method follows [WORKED-EXAMPLE.md](WORKED-EXAMPLE.md).

---

## US28 — `core.scoring.weighted_penalty(severity, ...)`

### 1. The function, with branches labelled

```python
def weighted_penalty(severity, critical_w, major_w, minor_w, info_w):
    weights = (...)                          # four (name, weight) pairs
    for name, weight in weights:             # loop, bounded at 4
        if weight < 0:                       # b1, once per iteration
            raise ValueError(...)
    if severity == CRITICAL:                 # b2
        return critical_w
    if severity == MAJOR:                    # b3
        return major_w
    if severity == MINOR:                    # b4
        return minor_w
    if severity == INFO:                     # b5
        return info_w
    raise ValueError(...)                    # b6 (implicit else)
```

### 2. Symbolic inputs

`S` is a symbolic string; `Wc, Wm, Wn, Wi` are symbolic integers. The function has a
**mixed domain**: the guard loop produces linear integer constraints, while the severity
comparisons produce string equalities. The two parts are independent — the guard runs to
completion before any comparison — so the tree is the guard chain followed by the
comparison chain.

### 3. Symbolic execution tree

```
    PC: true
    [b1 @ 1..4]  any of Wc, Wm, Wn, Wi < 0 ?
      |
      +-- P1  PC: Wc < 0                            -> ValueError
      +-- P2  PC: Wc>=0 and Wm<0                    -> ValueError
      +-- P3  PC: Wc,Wm>=0 and Wn<0                 -> ValueError
      +-- P4  PC: Wc,Wm,Wn>=0 and Wi<0              -> ValueError
      |
      +-- all four >= 0
            [b2] S = "CRITICAL" ?   true -> P5  return Wc
            [b3] S = "MAJOR"    ?   true -> P6  return Wm
            [b4] S = "MINOR"    ?   true -> P7  return Wn
            [b5] S = "INFO"     ?   true -> P8  return Wi
                                    else -> P9  ValueError
```

Nine leaves: four guard failures and five comparison outcomes.

### 4. Path conditions and solved witnesses

| Path | Path condition | Witness | Result |
|---|---|---|---|
| P1 | `Wc < 0` | `("CRITICAL", -1, 8, 3, 1)` | `ValueError` |
| P2 | `Wc >= 0 and Wm < 0` | `("MAJOR", 15, -1, 3, 1)` | `ValueError` |
| P3 | `Wc, Wm >= 0 and Wn < 0` | `("MINOR", 15, 8, -1, 1)` | `ValueError` |
| P4 | `Wc, Wm, Wn >= 0 and Wi < 0` | `("INFO", 15, 8, 3, -1)` | `ValueError` |
| P5 | all `>= 0` and `S = "CRITICAL"` | `("CRITICAL", 15, 8, 3, 1)` | `15` |
| P6 | all `>= 0`, `S != "CRITICAL"`, `S = "MAJOR"` | `("MAJOR", 15, 8, 3, 1)` | `8` |
| P7 | `… and S = "MINOR"` | `("MINOR", 15, 8, 3, 1)` | `3` |
| P8 | `… and S = "INFO"` | `("INFO", 15, 8, 3, 1)` | `1` |
| P9 | all `>= 0`, `S` matches none of the four | `("WARNING", 15, 8, 3, 1)` | `ValueError` |

**Working for P4.** The guard constraints are independent, so the witness sets the first
three weights to any non-negative value and `Wi` negative. Non-zero values are chosen for
the first three to prove the loop passed over them rather than exiting on the first entry
it checked.

**Working for P9.** The condition is a conjunction of four disequalities over a string:
`S != "CRITICAL" and S != "MAJOR" and S != "MINOR" and S != "INFO"`. Any string outside
that set satisfies it. `"WARNING"` is chosen as a plausible near-miss; `"critical"` is
also tested in the black-box package, because the comparison is case-sensitive and a
caller lower-casing a severity name would land silently on this error path rather than on
P5.

**A note on the domain.** Unlike the integer-valued functions elsewhere in the project,
the comparison chain tests string equality, so negating a branch fixes `S` to the next
literal rather than solving an inequality. The frontier is an enumeration of five cases
rather than a search over a range — which is why the concolic sequence below terminates in
exactly as many iterations as there are comparisons.

### 5. Concolic execution

Seeded with `("CRITICAL", 15, 8, 3, 1)`:

| It. | Input severity | Path | Branch negated | Next input |
|---|---|---|---|---|
| 1 | `"CRITICAL"` | P5 → 15 | `S = "CRITICAL"` | `"MAJOR"` |
| 2 | `"MAJOR"` | P6 → 8 | `S = "MAJOR"` | `"MINOR"` |
| 3 | `"MINOR"` | P7 → 3 | `S = "MINOR"` | `"INFO"` |
| 4 | `"INFO"` | P8 → 1 | `S = "INFO"` | `"WARNING"` |
| 5 | `"WARNING"` | P9 → ValueError | comparison frontier empty; backtrack into the guard | `Wc = -1` |
| 6 | `"CRITICAL", Wc = -1` | P1 → ValueError | continue backtracking through `Wm, Wn, Wi` | — |

Six iterations reach every comparison leaf and the first guard leaf; continuing the
backtrack through the remaining three guard positions reaches all nine paths.

### 6. Resulting test cases

`hcg22/test/whitebox/symbolic_execution/test_weighted_penalty.py` and
`.../concolic_testing/test_weighted_penalty.py`.

### 7. Coverage

| Measure | Value |
|---|---|
| Paths in the tree | 9 |
| Paths tested | 9 |
| Infeasible paths | 0 |
| Statement coverage of `weighted_penalty` | 100% |

---

## US29 — `score_from_issues(critical, major, minor, info)`

*To be completed when the story is implemented.*
