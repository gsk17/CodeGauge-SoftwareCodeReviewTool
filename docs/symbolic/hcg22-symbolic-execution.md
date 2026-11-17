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

## US30 — `core.scoring.grade_band(score)`

### 1. The function, with branches labelled

```python
def grade_band(score):
    if score < 0:            # b1
        raise ValueError(...)
    if score > 100:          # b2
        raise ValueError(...)
    if score >= 85:          # b3
        return "A"
    if score >= 70:          # b4
        return "B"
    if score >= 60:          # b5
        return "C"
    if score >= 50:          # b6
        return "D"
    return "F"               # b7 (implicit else)
```

### 2. Symbolic inputs

One symbolic integer, `S`. Every decision compares `S` against a literal
constant, so each path condition is a conjunction of linear constraints in a
single variable and solves by inspection. There are no loops, so the tree is
finite and complete — no bounding is needed.

### 3. Symbolic execution tree

```
          PC: true
          [b1] S < 0 ?
         /               true /              \ false
       /                P1: ValueError      PC: S >= 0
PC: S < 0           [b2] S > 100 ?
                   /                           true /                \ false
                 /                          P2: ValueError         PC: 0 <= S <= 100
                               [b3] S >= 85 ?
                              /                                      true /                \ false
                            /                                        P3: "A"            [b4] S >= 70 ?
                                        /                                                true /                \ false
                                      /                                                  P4: "B"            [b5] S >= 60 ?
                                                  /                                                          true /                \ false
                                                /                                                            P5: "C"            [b6] S >= 50 ?
                                                            /                                                                  true /              \ false
                                                          /                                                                    P6: "D"            P7: "F"
```

Seven leaves, seven paths.

### 4. Path conditions and solved witnesses

| Path | Path condition | Witness | Returns |
|---|---|---|---|
| P1 | `S < 0` | `-1` | `ValueError` |
| P2 | `S >= 0 and S > 100` | `101` | `ValueError` |
| P3 | `0 <= S <= 100 and S >= 85` | `85` | `"A"` |
| P4 | `… and S < 85 and S >= 70` | `70` | `"B"` |
| P5 | `… and S < 70 and S >= 60` | `60` | `"C"` |
| P6 | `… and S < 60 and S >= 50` | `50` | `"D"` |
| P7 | `… and S < 50` | `49` | `"F"` |

**How the witnesses were chosen.** Each path condition for P3 to P7 is a
half-open interval closed at its lower end, so solving for the *minimum*
satisfying integer lands exactly on the threshold. That is deliberate: a
witness at the interior of a band, say 92 for `"A"`, discharges the path
condition but would survive an off-by-one in the comparison. A witness at 85
would not.

**Working for P5.** The conjunction is `S >= 0`, `S <= 100`, `S < 85`,
`S < 70`, `S >= 60`. The constraints `S >= 0` and `S < 85` are implied by the
others, so the feasible set reduces to `S in {60, …, 69}`. The minimum, 60, is
taken as the witness; 69 is used in the black-box tests as the matching upper
boundary.

### 4a. What the analysis proves

Collect the seven path conditions and they partition the closed interval 0..100
into five intervals with **no gap and no overlap**:

```
[85,100]   [70,84]   [60,69]   [50,59]   [0,49]
   A          B         C         D         F
```

That is a derivation, not a sample, and it establishes two properties that no
finite set of example inputs could:

- **Totality.** Every integer in 0..100 satisfies exactly one path condition, so
  the function always returns and never falls through. The implicit else at b7
  is reachable and is the only path with no explicit guard of its own.
- **Monotonicity.** The five intervals are ordered and contiguous, so a higher
  score can never reach a worse grade than a lower one. The random-based
  black-box test asserts this by sampling pairs; the path conditions *prove* it.

Monotonicity is the property most at risk in a banding function. An if-chain
with one threshold written the wrong way round — `score > 85` instead of
`score >= 85`, or the bands tested worst-first — passes most single-point tests
and still misbands a value. Deriving the intervals is what rules it out.

**No infeasible paths.** Each path condition is a non-empty interval of
integers, and the witness column names a member of each.

### 5. Concolic execution

Seeded with `S = 100`, the top of the domain:

| It. | Input | Path | Collected PC | Branch negated | Next input |
|---|---|---|---|---|---|
| 1 | `100` | P3 → `"A"` | `S>=0, S<=100, S>=85` | `S >= 85` → `S < 85` | `84` |
| 2 | `84` | P4 → `"B"` | `… S<85, S>=70` | `S >= 70` → `S < 70` | `69` |
| 3 | `69` | P5 → `"C"` | `… S<70, S>=60` | `S >= 60` → `S < 60` | `59` |
| 4 | `59` | P6 → `"D"` | `… S<60, S>=50` | `S >= 50` → `S < 50` | `49` |
| 5 | `49` | P7 → `"F"` | `… S<50` | backtrack b2: `S <= 100` → `S > 100` | `101` |
| 6 | `101` | P2 | `S>=0, S>100` | backtrack b1: `S >= 0` → `S < 0` | `-1` |
| 7 | `-1` | P1 | `S < 0` | none left | — |

Seven iterations, seven paths, **100% path coverage**.

**The solver always returns a threshold.** Negating `S >= 85` gives `S < 85`
conjoined with everything already collected, and the solver returns the largest
satisfying integer — 84. Every input after the seed is therefore a boundary
value, so concolic execution rediscovers *mechanically* the same values that
boundary value analysis picks by hand in
`hcg22/test/blackbox/equivalence_partitioning/`. Two independently derived test
sets agreeing on the same seven inputs is the most useful result here: it is
evidence that the black-box boundaries were chosen correctly, arrived at
without reference to them.

**Negation order is a property of the seed, not the function.** Because the
grade chain is ordered best-first and each negation pushes the score below the
previous threshold, the walk descends A, B, C, D, F and only then backtracks to
the two guards. A seed of `S = 0` would walk the same tree in the opposite
order and find the same seven paths.

### 6. Resulting test cases

| File | Contents |
|---|---|
| `hcg22/test/whitebox/branch_coverage/test_grade_band.py` | one test per leaf, with the outcome table |
| `hcg22/test/whitebox/symbolic_execution/test_grade_band.py` | one test per path condition, plus the partition proof |
| `hcg22/test/whitebox/concolic_testing/test_grade_band.py` | the seven iterations in generated order |

### 7. Coverage

| Measure | Value |
|---|---|
| Paths in the tree | 7 |
| Paths tested | 7 |
| Infeasible paths | 0 |
| Branch outcomes | 13 of 13 |
| Statement coverage of `grade_band` | 100% |

---

## US29 — `score_from_issues(critical, major, minor, info)`

*To be completed when the story is implemented.*
