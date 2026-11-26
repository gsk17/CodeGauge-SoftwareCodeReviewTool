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

## US29 — `core.scoring.score_from_issues(critical, major, minor, info)`

### 1. The function, with branches labelled

```python
def score_from_issues(critical, major, minor, info):
    for name, value in counts:         # L   fixed four iterations
        if value < 0:                  # b1
            raise ValueError(...)
    penalty = 15*critical + 8*major + 3*minor + 1*info
    score = 100 - penalty
    if critical >= 3:                  # b2  the cap applies at all
        if score > 40:                 # b3  and only then lowers the score
            score = 40
    if score < 0:                      # b4  the floor
        score = 0
    return score
```

### 2. Symbolic inputs

`C`, `M`, `N`, `I`, symbolic integers. The validation loop runs a fixed four
times — the count comes from the signature, not from the data — so unlike US12
and US02 no bounding is required and the tree is complete.

Writing `P = 15C + 8M + 3N + I` for the penalty and `R = 100 - P` for the raw
score, every constraint is linear in the four variables.

### 3. Symbolic execution tree

```
        validation loop, four iterations
    C<0 ──true──> P1: ValueError
     │false
    M<0 ──true──> P2: ValueError
     │false
    N<0 ──true──> P3: ValueError
     │false
    I<0 ──true──> P4: ValueError
     │false
   R = 100 - P
    [b2] C >= 3 ?
    /            \
true/              \false
   /                \
[b3] R > 40 ?      [b4] R < 0 ?
 /        \          /       \
true     false   true       false
 │         │       │          │
score=40  [b4]   P8: 0     P9: R
 │       R < 0 ?
[b4]      /    \
R<40?  true   false
 │      │       │
 │    P6: 0   P7: R
P5: 40
```

Nine leaves, nine paths.

### 4. Path conditions and solved witnesses

| Path | Path condition | Witness | R | Returns |
|---|---|---|---|---|
| P1 | `C < 0` | `(-1,0,0,0)` | — | `ValueError` |
| P2 | `C >= 0, M < 0` | `(0,-1,0,0)` | — | `ValueError` |
| P3 | `C,M >= 0, N < 0` | `(0,0,-1,0)` | — | `ValueError` |
| P4 | `C,M,N >= 0, I < 0` | `(0,0,0,-1)` | — | `ValueError` |
| P5 | all `>= 0`, `C >= 3`, `R > 40` | `(3,0,0,0)` | 55 | `40` |
| P6 | all `>= 0`, `C >= 3`, `R <= 40`, `R < 0` | `(10,0,0,0)` | −50 | `0` |
| P7 | all `>= 0`, `C >= 3`, `0 <= R <= 40` | `(5,0,0,0)` | 25 | `R` |
| P8 | all `>= 0`, `C < 3`, `R < 0` | `(0,13,0,0)` | −4 | `0` |
| P9 | all `>= 0`, `C < 3`, `R >= 0` | `(0,0,1,0)` | 97 | `R` |

**P1 to P4 are distinct for a structural reason.** Validation is a complete
pass over all four counts before any arithmetic happens, so a negative value in
the fourth position is rejected only after the first three have passed. Fusing
validation into the penalty sum would collapse these four paths into one and
lose the guarantee that *every* count is checked.

**Working for P7.** The conjunction is all counts `>= 0`, `C >= 3`, `R <= 40`,
`R >= 0`. Fixing `M = N = I = 0` leaves `R = 100 - 15C`, so `R <= 40` requires
`C >= 4` and `R >= 0` requires `C <= 6`. The feasible set is `C in {4, 5, 6}`;
`C = 5` is taken, with `C = 4` used separately below because it sits exactly on
the P5/P7 boundary.

### 4a. Finding 1 — the floor is unreachable once the cap has fired

On P5 the score is **assigned** 40 before b4 is evaluated, and 40 is not below
zero. So the sub-path "cap fires, then floor fires" requires:

```
score = 40   and   score < 0        unsatisfiable
```

The tree therefore has nine leaves rather than ten, and the missing one is a
genuine infeasible path rather than an untested one. It is reported as such in
the coverage table.

### 4b. Finding 2 — the cap can only ever fire at exactly three critical issues

This is the result worth having, and it is not visible from reading the code.

P5 requires both `C >= 3` and `R > 40`. Substituting `R`:

```
100 - 15C - (8M + 3N + I) > 40
15C + (8M + 3N + I) < 60
```

With `C >= 3`:  `45 + (8M + 3N + I) < 60`,  so  `8M + 3N + I < 15`.
With `C >= 4`:  `60 + (8M + 3N + I) < 60`,  so  `8M + 3N + I < 0` — and all
three counts are non-negative on this path, so this is **unsatisfiable**.

**Therefore P5 requires `C == 3` exactly**, together with the other three
severities contributing fewer than 15 penalty points.

The cause is arithmetic rather than intentional. Four critical issues cost
`4 × 15 = 60`, which puts the raw score at exactly **40 — the cap value
itself**. Above three criticals, the weighted penalty has already done
everything the cap was designed to do.

**So the cap is very nearly vestigial.** It changes the answer only for a file
with exactly three critical issues and little else: `(3,0,0,0)` through
`(3,0,0,14)`, `(3,1,0,0)` through `(3,1,0,6)`, `(3,0,1,0)` through
`(3,0,4,2)`, and a handful of similar combinations. For every other input in
the domain, the weights and the floor alone produce the same number.

This is a finding about the **specification**, not the implementation. The
implementation satisfies the spec exactly; the spec contains a rule that fires
on one value of one argument. Whether that rule is worth having is a question
for the sprint review, and it is recorded in the README's known limitations.

It is also the second time symbolic execution has found that a project rule is
narrower than it looks — the first was the INFO band being unreachable through
any `rule_*` function. Both were invisible to the black-box tests, which assert
only that the cap holds the score at or below 40 when `critical >= 3`; that
assertion passes whether the cap is doing the work or the weights are.

### 5. Concolic execution

Seeded with `(0, 0, 0, 0)` — a clean file, the cheapest seed to justify and the
furthest from the interesting behaviour:

| It. | Input | Path | Collected PC | Branch negated | Next input |
|---|---|---|---|---|---|
| 1 | `(0,0,0,0)` | P9 → 100 | all `>= 0`, `C<3`, `R>=0` | `C < 3` → `C >= 3` | `(3,0,0,0)` |
| 2 | `(3,0,0,0)` | P5 → 40 | `… C>=3, R>40` | `R > 40` → `R <= 40` | `(4,0,0,0)` |
| 3 | `(4,0,0,0)` | P7 → 40 | `… R<=40, R>=0` | `R >= 0` → `R < 0` | `(10,0,0,0)` |
| 4 | `(10,0,0,0)` | P6 → 0 | `… R<0` | backtrack b2: `C>=3` → `C<3`, keeping `R<0` | `(0,13,0,0)` |
| 5 | `(0,13,0,0)` | P8 → 0 | `C<3, R<0` | backtrack to validation: `I>=0` → `I<0` | `(0,13,0,-1)` |
| 6 | `(0,13,0,-1)` | P4 | `… I<0` | `N >= 0` → `N < 0` | `(0,13,-1,0)` |
| 7 | `(0,13,-1,0)` | P3 | `… N<0` | `M >= 0` → `M < 0` | `(0,-1,0,0)` |
| 8 | `(0,-1,0,0)` | P2 | `C>=0, M<0` | `C >= 0` → `C < 0` | `(-1,0,0,0)` |
| 9 | `(-1,0,0,0)` | P1 | `C < 0` | none left | — |

Nine iterations, nine paths, **100% path coverage**.

**Iteration 2 is where the solver does something a person would not.** The
constraint is `C >= 3` conjoined with what has already been collected, and the
solver returns the smallest satisfying value, 3 — which Finding 2 shows is the
*only* value of `C` for which the cap can fire. The walk lands on the single
interesting input by solving for a boundary, without knowing anything about the
cap.

**Iteration 3 then negates `R > 40` and returns `(4,0,0,0)`**, which sits
exactly on the cap value. A person writing these cases by hand would very
likely pick `(5,0,0,0)` — comfortably below the cap — and so would never
distinguish `score > 40` from `score >= 40`. **This is the clearest case in the
project of concolic execution producing a better test than hand-selection
would have**, and it is worth stating plainly: the technique earned its place
here rather than merely reproducing what boundary value analysis already gave.

**Iteration 4 is the one the solver has to work at.** It must satisfy `C < 3`
while keeping `R < 0`, so the penalty has to come from somewhere other than
critical issues: with `C = 0` it needs `8M + 3N + I > 100`, and `M = 13` gives
104. A walk that only varied `C` could not reach P8 at all.

**The floor is never reached from the cap branch**, in any iteration. That
matches the infeasible path proved in section 4a — the walk demonstrates the
unreachability by never going there.

### 6. Resulting test cases

| File | Contents |
|---|---|
| `hcg22/test/whitebox/branch_coverage/test_score_from_issues.py` | eight branch outcomes, including b1 at each of the four argument positions |
| `hcg22/test/whitebox/symbolic_execution/test_score_from_issues.py` | one test per path, plus both findings as domain sweeps |
| `hcg22/test/whitebox/concolic_testing/test_score_from_issues.py` | the nine iterations in generated order |

Finding 2 is asserted by counting, over a bounded region of the input space,
every input where the capped and uncapped results differ, and then checking
that **all** of them have `critical == 3`.

### 7. Coverage

| Measure | Value |
|---|---|
| Paths in the tree | 9 |
| Paths tested | 9 |
| Infeasible paths found | **1** — the floor cannot fire after the cap |
| Narrowed specification found | **1** — the cap fires only at `critical == 3` |
| Branch outcomes | 8 of 8 reachable |
| Statement coverage of `score_from_issues` | 100% |

---

## US31 — `core.history.compare_scores(before, after)`

The first function in the project with a **compound decision**, so the first
where branch coverage, condition coverage and MC/DC are three different numbers
rather than three names for the same seven tests.

### 1. The function, with branches labelled

```python
def compare_scores(before, after):
    if before < 0 or before > 100:          # b1  (two conditions)
        raise ValueError(...)
    if after < 0 or after > 100:            # b2  (two conditions)
        raise ValueError(...)
    difference = after - before
    if difference == 0:                     # b3
        return UNCHANGED
    if difference >= LARGE_CHANGE:          # b4
        return MUCH_IMPROVED
    if difference > 0:                      # b5
        return IMPROVED
    if difference <= -LARGE_CHANGE:         # b6
        return MUCH_REGRESSED
    return REGRESSED                        # b7 (implicit else)
```

### 2. Symbolic inputs

Two symbolic integers, `B` for `before` and `A` for `after`, with the derived
term `D = A - B`. **Every decision after the two validations constrains `D`
alone**, which is why the seven path conditions reduce to intervals on a single
line.

### 3. The execution tree

| Path | Path condition | Witness | Returns |
|---|---|---|---|
| P1 | `B < 0 or B > 100` | `(-1, 200)` | ValueError, `before` |
| P2 | `0 <= B <= 100`, `A < 0 or A > 100` | `(50, 101)` | ValueError, `after` |
| P3 | valid, `D == 0` | `(72, 72)` | UNCHANGED |
| P4 | valid, `D >= 10` | `(72, 85)` | MUCH_IMPROVED |
| P5 | valid, `0 < D < 10` | `(72, 78)` | IMPROVED |
| P6 | valid, `D <= -10` | `(72, 60)` | MUCH_REGRESSED |
| P7 | valid, `-10 < D < 0` | `(72, 66)` | REGRESSED |

Seven leaves. P1 and P2 each cover **two condition-paths**, since `or`
short-circuits: the first operand true, or the first false and the second true.
Counting those separately gives nine paths — see finding 6.

### 4. Finding 1 — every path condition is satisfiable, which no other function in this member's set can say

Seven leaves, seven feasible paths, **no infeasible combinations at all.** That
is unusual here: US29's score cap produced a branch reachable at exactly one
issue count, US22's inlined severity call has three unsatisfiable leaves out of
seven, and US07's tree is missing a leaf because two string prefixes exclude
each other.

Full feasibility is a consequence of the bands being **nested and tested in
order**. Each guard's condition is weaker than the last, so each negation leaves
a non-empty remainder for the next. A version testing five disjoint conditions
independently would be no more correct and would admit unsatisfiable
combinations — which is to say the shape that makes finding 5 a hazard is the
same shape that makes this finding hold.

### 5. Finding 2 — the bands are wildly unequal, and "much" is the common case

The valid domain is `0 <= B, A <= 100`, so `D` ranges over `[-100, 100]` — 201
values:

| Band | `D` range | Values |
|---|---|---|
| MUCH_REGRESSED | `[-100, -10]` | 91 |
| REGRESSED | `[-9, -1]` | 9 |
| UNCHANGED | `0` | 1 |
| IMPROVED | `[1, 9]` | 9 |
| MUCH_IMPROVED | `[10, 100]` | 91 |

**182 of the 201 possible differences are "much" something.** Counting input
pairs sharpens it, since extreme differences need extreme scores. Over all
101 × 101 = 10,201 valid pairs:

| Band | Pairs | Share |
|---|---|---|
| MUCH_IMPROVED | 4,186 | 41.0% |
| IMPROVED | 864 | 8.5% |
| UNCHANGED | 101 | 1.0% |
| REGRESSED | 864 | 8.5% |
| MUCH_REGRESSED | 4,186 | 41.0% |

The five sum to 10,201, which is the check that the bands partition the domain
exactly. So **82% of all possible score pairs are classified as a large
change**, and the two bands named for the ordinary case cover 17% between them.

`LARGE_CHANGE` is 10 on a 0–100 scale, which sounds conservative and is not. On
the scale `score_from_issues` actually produces, a single CRITICAL issue costs
15 points — so **the appearance or repair of one critical finding is always
MUCH_IMPROVED or MUCH_REGRESSED.** The wording will overstate routine change in
almost every real report, and the threshold rather than the implementation is
what would have to move.

### 6. Finding 3 — UNCHANGED is one value of `D` and 101 inputs

P3's path condition is `D == 0` with the range checks, which in the original
inputs is the **diagonal** `B == A`, 0 through 100 — 101 solutions.

Worth separating from US04's finding 1, where the one-value path condition had
exactly one solution in the inputs too. Here the derived variable collapses and
the inputs do not, so the partition is a singleton in `D` and a 101-member set
in `(B, A)`. A test of this leaf is exhaustive over the derived space and a
sample of the input space — and only the second matters if the function is ever
changed to look at `B` or `A` directly rather than only at their difference.

### 7. Finding 4 — the antisymmetry is provable, not merely apparent

Substituting `D -> -D` maps the five banding conditions onto each other exactly:

```
D == 0       ->  D == 0            P3 -> P3
D >= 10      ->  D <= -10          P4 -> P6
0 < D < 10   ->  -10 < D < 0       P5 -> P7
```

So `compare_scores(A, B)` always returns the mirror of `compare_scores(B, A)`,
for every valid pair, with UNCHANGED as the fixed point. **The function is
exactly antisymmetric.**

That is the property the docstring is defending when it rejects the
`abs(after - before)` implementation. With `abs()`, the magnitude is banded and
the direction attached afterwards, and antisymmetry becomes a claim about two
steps agreeing rather than a consequence of one. The claim would be true of a
correct implementation and **could not be read off its path conditions**,
because the sign would not appear in them. Carrying the sign through makes the
symmetry structural: it *is* the substitution above.

### 8. Finding 5 — the guard order is load-bearing here, where in US07 it was not

The five banding conditions are **nested, not disjoint**:

```
D >= 10    implies   D > 0
D <= -10   implies   D < 0
```

b4's set is a subset of b5's, and b6's a subset of the implicit else's. The
guards are disjoint only because of the order they are written in.
Consequences, each provable by the same substitution:

* **swap b4 and b5 and MUCH_IMPROVED becomes unreachable** — every gain, large
  or small, would be taken by `D > 0` first;
* **swap b6 and b7 and MUCH_REGRESSED becomes unreachable**;
* **move b3 below b4 and nothing changes**, because `D == 0` is disjoint from
  both large bands — though it must stay above b5 and b7 or UNCHANGED is lost.

This is the direct opposite of US07's finding 1, where the guards formed a
conjunction, conjunction is commutative, and reordering was proved to change the
path taken but never the result. **The same analysis applied to the same-looking
chain of guards gives the opposite answer**, and the difference is visible only
in the path conditions: US07's atoms were independent string properties, these
are nested intervals on one variable.

Four of the five banding outcomes depend on the ordering. Nothing in the source
says so, and **no test of a single band would fail if two were swapped** — the
suite would fail, but on the band that had become unreachable, which is a
confusing place to begin debugging.

### 9. Finding 6 — branch coverage cannot distinguish the two ways to fail a validation

b1 is `before < 0 or before > 100`, and `or` short-circuits. There are two
condition-paths to P1:

| | Condition-path | Second operand |
|---|---|---|
| P1a | `B < 0` | never evaluated |
| P1b | `B >= 0 and B > 100` | evaluated |

A suite reaching P1 only through 101 covers both branches of the decision and
never evaluates `B < 0` to true. `coverage` reports 100% either way, because
both forms execute the same line.

| Criterion | What it demands of b1 | Tests |
|---|---|---|
| Branch coverage | the decision both ways | 2 |
| Condition coverage | each operand both ways | 2, if chosen well |
| MC/DC | each operand shown to decide alone | 3 |

**Branch coverage of this function is 7 tests; honest coverage is 11.** The
difference is entirely in the two validations and is invisible to the coverage
tool. It is worth paying for because the operands enforce different ends of the
scale: a transposition defect — `before > 0 or before < 100`, which rejects
nothing at all — would be caught by condition coverage and missed by branch
coverage of a suite that only ever tested one end.

### 10. Finding 7 — the integer domain is load-bearing and nowhere enforced

b5 is `difference > 0` where `difference >= 1` would be equivalent — over the
integers. Over the reals they differ, and nothing here requires integer
arguments; the range validation accepts any comparable numeric:

| Call | `D` | Returns |
|---|---|---|
| `compare_scores(0, 0.5)` | 0.5 | IMPROVED |
| `compare_scores(0, 9.5)` | 9.5 | IMPROVED |
| `compare_scores(0.5, 0.5)` | 0.0 | UNCHANGED |

So the gap between IMPROVED and MUCH_IMPROVED — closed over the integers, 9 then
10 — is **open over the reals** and holds infinitely many values the band names
still describe correctly.

**Unreachable in the tool as it stands**, because `score_from_issues` returns an
integer by construction and is the only producer of these scores. Recorded
because it is a contract this function relies on and does not state: the
docstring says "1 to 9 points" and "10 or more", which is true only of integer
inputs.

### 11. Concolic walk

Seeded with `(72, 85)` — the quality score of `core/scanner.py` at the Sprint 1
close and its score after US07 merged, so the first run is a real comparison
between two real reviews.

| It. | Input | Path | Collected PC | Negated | Next |
|---|---|---|---|---|---|
| 1 | `(72, 85)` | P4 | valid, `D!=0`, `D>=10` | `D>=10` | `(72, 78)` |
| 2 | `(72, 78)` | P5 | valid, `D!=0`, `D<10`, `D>0` | `D>0` | `(72, 60)` |
| 3 | `(72, 60)` | P6 | valid, `D!=0`, `D<0`, `D<=-10` | `D<=-10` | `(72, 66)` |
| 4 | `(72, 66)` | P7 | valid, `D!=0`, `D<0`, `D>-10` | `D!=0` | `(72, 72)` |
| 5 | `(72, 72)` | P3 | valid, `D==0` | `A` valid | `(72, 101)` |
| 6 | `(72, 101)` | P2 | `B` valid, `A` invalid | `B` valid | `(-1, 101)` |
| 7 | `(-1, 101)` | P1 | `B` invalid | — | — |

**Seven iterations, seven leaves, three backtracks** — at iterations 5, 6 and 7,
each unwinding to a shallower branch because the deeper ones are exhausted. The
most backtracking of any walk in this member's set, because the four banding
guards sit at the bottom of the tree and are consumed first, after which every
remaining leaf is above them.

**The derived variable hides a choice.** Every negation produced a constraint on
`D`, which is not an input. Each witness had to be recovered by solving
`A - B = d`, which has infinitely many solutions, and the walk resolved that by
**holding `B` fixed at the seed's 72 and moving `A`**. Holding `A` fixed and
moving `B` is equally valid — `(66, 85)` reaches P4 just as the seed does — and
yields a different suite with the same coverage. Fixing `B` reads as one
baseline compared against several later reviews, which is what the function is
for. Compare US04, where one negation pinned the model exactly and no choice was
available.

### 12. The headline finding — complete path coverage, incomplete condition coverage, and the technique cannot close the gap

Iteration 5 negates `not (A < 0 or A > 100)`, handing the solver

```
0 <= B <= 100  and  (A < 0 or A > 100)
```

which is a **disjunction**. A solver returns one model. It returned `A = 101`;
`A = -1` is an equally good model and reaches the same leaf by the other
operand. The walk has no reason to ask for the second, because the bookkeeping
driving it is per *decision* — the decision has now been seen both ways, so
there is nothing left to negate. The same happens at iteration 6 for `B`.

So this walk achieves **100% path coverage while leaving two of the four
validation operands never evaluated true**: `A < 0` and `B > 100` are not
exercised by any of the seven cases. The transposition defect of finding 6 would
survive a suite that was complete by the measure the walk optimises.

**Two walks can be equally complete and disagree about which operands they
covered.** A walk whose solver preferred the first disjunct would cover `A < 0`
and `B < 0` and miss the other two. The coverage figure is reproducible and the
condition coverage behind it is not, which makes the figure a poor summary of
what the walk achieved.

The four cases appended after the walk in
`hcg22/test/whitebox/concolic_testing/` close the gap. They are not derived from
any negation and could not be: they are a **second input for a path already
covered**, which is exactly what a path-driven technique will never ask for.

### 13. Coverage

| Measure | Value |
|---|---|
| Paths in the tree | 7 |
| Condition-paths in the tree | 9 |
| Paths tested | 7 |
| Condition-paths tested | 9 |
| Infeasible paths found | **0** — the only function in this member's set with none |
| Concolic backtracking steps required | **3** |
| Branch outcomes | 12 of 12 |
| Statement coverage of `compare_scores` | 100% |
| Branch coverage tests vs honest tests | **7 vs 11** |
| Condition-paths the concolic walk reached | **7 of 9** — the gap it cannot close |
