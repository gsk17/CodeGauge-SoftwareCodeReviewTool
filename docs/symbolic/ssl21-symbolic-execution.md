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

---

## US22 — `core.rules.rule_params(param_count, limit, line)`

The third rule of the shape US19 established, and the first analysis in this
project to treat that shape as a **contract** rather than a coincidence. The
findings below are properties of the shape, so they hold for `rule_complexity`
and `rule_nesting` too — and the third instance is what makes them worth
proving once instead of observing three times.

Analysed **inter-procedurally, by inlining** `classify_severity` into the
fourth leaf.

### 1. The functions, with branches labelled

```python
def rule_params(param_count, limit, line):
    if param_count < 0:                     # b1
        raise ValueError(...)
    if limit < 1:                           # b2
        raise ValueError(...)
    if param_count <= limit:                # b3
        return None
    severity = classify_severity(param_count, limit)
    return Issue(CODE_PARAMS, severity, line, message)     # b4 (implicit else)
```

```python
def classify_severity(actual, limit):
    if actual < 0:                          # s1
        raise ValueError(...)
    if limit < 1:                           # s2
        raise ValueError(...)
    if actual <= limit:                     # s3
        return INFO
    if actual <= limit + limit // 2:        # s4
        return MINOR
    if actual < 2 * limit:                  # s5
        return MAJOR
    return CRITICAL                         # s6 (implicit else)
```

### 2. Symbolic inputs

Two symbolic integers, `P` for `param_count` and `L` for `limit`. **`line` is
carried into the `Issue` untouched and is never branched on**, so it appears in
no path condition and is not symbolic — see finding 5.

### 3. The caller alone

| Path | Path condition | Witness | Returns |
|---|---|---|---|
| C1 | `P < 0` | `(-1, 0)` | ValueError, `param_count` |
| C2 | `P >= 0, L < 1` | `(3, 0)` | ValueError, `limit` |
| C3 | `P >= 0, L >= 1, P <= L` | `(3, 4)` | `None` |
| C4 | `P >= 0, L >= 1, P > L` | `(6, 4)` | `Issue(…)` |

C4 is a leaf of this function, not of the program.

### 4. Inlining the callee into C4

Substituting `actual = P`, `limit = L` and conjoining C4's path condition:

| Callee leaf | Condition | Conjoined with C4 | Satisfiable? |
|---|---|---|---|
| s1 | `P < 0` | `P >= 0 and P < 0` | **NO** |
| s2 | `L < 1` | `L >= 1 and L < 1` | **NO** |
| s3 | `P <= L` | `P > L and P <= L` | **NO** |
| s4 | `L < P <= L + L//2` | — | yes, MINOR |
| s5 | `L + L//2 < P < 2L` | — | yes, MAJOR |
| s6 | `P >= 2L` | — | yes, CRITICAL |

So the inlined tree has **seven syntactic leaves and six feasible paths**:

| Path | Full path condition | Witness | Returns |
|---|---|---|---|
| P1 | `P < 0` | `(-1, 0)` | raises |
| P2 | `P >= 0, L < 1` | `(3, 0)` | raises |
| P3 | `P >= 0, L >= 1, P <= L` | `(3, 4)` | `None` |
| P4 | `P > L, P <= L + L//2` | `(5, 4)` | MINOR |
| P5 | `P > L + L//2, P < 2L` | `(7, 4)` | MAJOR |
| P6 | `P >= 2L` | `(8, 4)` | CRITICAL |

### 5. Finding 1 — the callee's own validation is dead at every rule call site

Three of the callee's five leaves cannot be reached from any rule. The caller's
b1, b2 and b3 establish precisely what the callee's first three decisions
re-check.

That is **not** an argument for deleting them. `classify_severity` is a public
function, called directly by its own tests and potentially by future code; its
validation is dead *relative to this caller*, not dead in the module. The useful
conclusion is the opposite one: **the duplicated checks are the reason the
inter-procedural analysis is this simple.** Because the callee re-asserts the
caller's guarantees, the conjunction either collapses to the caller's prefix or
becomes unsatisfiable, and the call introduces no new constraint on `P` or `L`
at all.

With three rules in the module that is **nine infeasible leaves project-wide**
that no test of any rule can reach. `coverage` nevertheless reports
`core/severity.py` at 100%, because US26's own tests reach those lines directly.
Coverage is a statement about lines the suite executed, not about behaviour
reachable through a given path, and these nine are the clearest example of the
gap in this project.

### 6. Finding 2 — no rule in this tool can emit INFO, and now it is a theorem

The inlined condition for INFO is `P > L and P <= L`: unsatisfiable, trivially
and for every `L`. The same substitution works for `rule_complexity` and
`rule_nesting`, because all three guard with `measurement <= limit -> None`
before calling. Therefore:

> **For every `rule_*` function in `core.rules`, the INFO severity is
> unreachable.** An `Issue` produced by this tool carries MINOR, MAJOR or
> CRITICAL, never INFO.

US19 observed it for one rule and US20 for a second; the third instance makes it
a property of the shape, and the shape is now documented in the `rule_params`
docstring as a contract any future rule must satisfy — which means any future
rule inherits this consequence too.

The cost is that a reader of `core/severity.py` alone would conclude four
severities can appear in a report. INFO is defined, exported and listed in
`RANK_ORDER`, which `combine_severities` reduces along. It is reachable only by
calling `classify_severity` directly, which nothing in the production path does.
A reviewer looking for the INFO findings in a report will not find any, and the
absence is structural rather than a sign of clean code.

### 7. Finding 3 — the bands collapse at small limits, and the agreed fix does not go far enough

Band membership, read off the inlined path conditions:

| Band | Membership | Size |
|---|---|---|
| MINOR | `{ L+1 .. L + L//2 }` | `L // 2` |
| MAJOR | `{ L + L//2 + 1 .. 2L-1 }` | `L - L//2 - 1` |
| CRITICAL | `{ 2L .. }` | unbounded |

| `L` | MINOR | MAJOR | CRITICAL | Reachable severities |
|---|---|---|---|---|
| 1 | `{ }` | `{ }` | `{2, …}` | **CRITICAL only** |
| 2 | `{3}` | `{ }` | `{4, …}` | **MINOR, CRITICAL** |
| 3 | `{4}` | `{5}` | `{6, …}` | all three |
| 4 | `{5, 6}` | `{7}` | `{8, …}` | all three |
| 5 | `{6, 7}` | `{8, 9}` | `{10, …}` | all three |

**At a limit of 1 every finding in the report is CRITICAL. At a limit of 2,
MAJOR is unreachable.** Both are configurations `Thresholds.validate` presently
permits.

The Sprint 1 retrospective agreed to tighten `Thresholds.validate` to **reject
limits below 2**, owned by this member and scheduled for Friday 27 November.
This analysis says that fix is one short: **the smallest limit at which all
three reachable severities are non-empty is 3**, not 2. A limit of 2 passes the
agreed validation and still produces a report whose MAJOR band is empty by
construction.

Raised for the stand-up before the fix is written, because it changes the
constant and not the design. The counter-argument to weigh there is that a limit
of 2 is a legitimate setting for a nesting depth — a project insisting on at
most two levels of indentation is strict, not misconfigured — and forbidding it
to protect a band from being empty refuses a reasonable configuration to fix a
reporting artefact. The alternative is to change the banding arithmetic rather
than the validation, which affects every rule and every existing test. **The
decision belongs to the team**; what the analysis contributes is that 2 and 3
are different answers and the difference was not visible when the retrospective
chose 2.

### 8. Finding 4 — the three rules are provably interchangeable, so the cross-rule test is not redundant

After renaming the measurement variable, the path conditions of
`rule_complexity`, `rule_nesting` and `rule_params` are **identical**, and so
are the inlined severity conditions. The three differ only in the code constant
carried into the `Issue` (`CC001`, `NEST001`, `PAR001`), the wording of the
message, and the variable name in the validation messages. Nothing else.

The duplication is deliberate — a shared helper would put two members' marks
inside one function — and the analysis shows exactly what it risks: three
independent copies of a banding decision that must stay in agreement.

**A per-rule test cannot detect a divergence**, because each rule tested alone is
self-consistent whatever bands it uses. The only test that would fail is one
asserting the three produce equal severities for equal numbers, which is why
such a test exists in all three members' black-box packages and is reproduced
over the whole small-limit range in the white-box suite.

### 9. Finding 5 — `line` is absent from every path condition

The function takes three arguments and branches on two. `line` is copied into
the `Issue` and never compared, so the tree is the same for every value of it,
including nonsensical ones: `rule_params(9, 4, -1)` returns an `Issue` reporting
a finding at line −1, and no validation rejects it.

The rule trusts its caller on line numbering, on the ground that the scanner
owns it and a rule that second-guessed it could reject a valid report. The
analysis confirms there is **no path on which a bad line number is caught**, so
if that trust is ever misplaced the error surfaces in the formatter, not here.

### 10. Concolic walk

Seeded with `(7, 5, 12)` — seven parameters against the default limit of five,
taken from the worst signature in the Sprint 0 prototype before it was
discarded. The seed deliberately lands on an **inlined** leaf, so the walk
begins inside the callee and climbs outward.

| It. | Input | Path | Collected PC | Negated | Next |
|---|---|---|---|---|---|
| 1 | `(7, 5)` | MINOR | `P>=0, L>=1, P>L, P<=L+L//2` | callee s4 | `(8, 5)` |
| 2 | `(8, 5)` | MAJOR | `P>=0, L>=1, P>L, P<2L` | callee s5 | `(10, 5)` |
| 3 | `(10, 5)` | CRITICAL | `P>=0, L>=1, P>=2L` | caller b3 | `(3, 5)` |
| 4 | `(3, 5)` | None | `P>=0, L>=1, P<=L` | caller b2 | `(3, 0)` |
| 5 | `(3, 0)` | raises | `P>=0, L<1` | caller b1 | `(-1, 0)` |
| 6 | `(-1, 0)` | raises | `P<0` | — | — |

**Six iterations, six feasible paths, one backtrack** — at iteration 3, where
the two deepest branches belong to the callee and are exhausted, so the walk
unwinds to the caller's own b3.

**The walk crosses a call boundary without noticing, which is the point.**
Iterations 1 and 2 negate branches in `core/severity.py`; iterations 3 to 5
negate branches in `core/rules.py`. Nothing in the procedure distinguishes them,
because the path condition is a conjunction of atoms over `P` and `L` and which
file an atom came from is not recorded in it.

That is what makes inlining the right treatment rather than a convenient
simplification: `classify_severity(P, L)` passes the caller's symbols straight
through with no transformation, so the substitution is the identity. **A callee
that computed a new value from its arguments** — a hash, a lookup, anything
non-linear — **would break that**, and the walk would have to treat the call as
an opaque operation and stop exploring at it.

**Three negations the solver was never offered.** The walk reached six of the
seven syntactic leaves. The missing one is INFO, and no input was ever proposed
for it because `P > L and P <= L` is unsatisfiable. A real solver returns UNSAT,
the leaf is marked infeasible and the walk moves on. **A hand-run walk gets no
such signal**: an unsatisfiable negation and an exhausted frontier look the same
from the outside, which is how an infeasible path gets quietly recorded as "not
yet reached" and then as "uncovered". The same applies to the callee's two
validation leaves. Three leaves, three UNSAT results, and only the algebra
distinguishes them from a gap in the testing — which is the honest argument for
doing the symbolic work *alongside* the concolic walk rather than instead of it.

**What the walk cannot reach.** All six feasible paths, and only at `L = 5`.
Every finding about small limits — that MAJOR is empty at `L = 2`, that CRITICAL
is the only band at `L = 1`, that 3 and not 2 is the smallest safe limit — is
invisible, for the same reason as in US14. **So the walk cannot find the defect
the retrospective is about to half-fix.** It was found by solving the band
expressions.

### 11. Coverage

| Measure | Value |
|---|---|
| Leaves in the inlined tree | 7 |
| Feasible paths | 6 |
| Paths tested | 6 |
| Infeasible paths found | **3** — the callee's s1, s2 and s3 under C4 |
| Infeasible leaves across all three rules | **9** |
| Concolic backtracking steps required | **1** |
| Branch outcomes in `rule_params` | 6 of 6 |
| Statement coverage of `rule_params` | 100% |
| Severities a rule can emit | **3 of 4** — INFO proved unreachable |
| Defects raised | **1** — the agreed `validate` fix should reject limits below **3** |
