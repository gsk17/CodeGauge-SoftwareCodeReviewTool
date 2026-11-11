# PERT Analysis and Critical Path

Project: CodeGauge - CO7095 project #17, Software Code Review Tool
Computed with [scripts/pert.py](scripts/pert.py) — run `python docs/measurement/scripts/pert.py`
to reproduce every number below.

## 1. Method

Each activity carries a three-point estimate in **working days**: optimistic (O),
most likely (M) and pessimistic (P). The expected duration is the PERT weighted mean

```
TE = (O + 4M + P) / 6
```

and the uncertainty of each estimate is its variance

```
Var = ((P - O) / 6)^2
```

The forward pass computes the earliest start and finish of every activity
(`ES = max(EF of predecessors)`, `EF = ES + TE`). The backward pass computes the latest
start and finish (`LF = min(LS of successors)`, `LS = LF - TE`). Slack is `LS - ES`, and the
critical path is the chain of activities with zero slack — the activities where any delay
delays the whole project.

## 2. Activity list and dependencies

| Act | Activity | Depends on | Owner |
|---|---|---|---|
| A | Requirements and user story backlog | — | all four |
| B | Repository, PyCharm project, skeleton, tooling | A | all four |
| C | Data model | B | all four |
| E | M2 complexity metrics (`core/complexity.py`) | C | Kasam* |
| D | M1 scanner and line metrics (`core/scanner.py`, `core/line_metrics.py`) | C, E | Gunjan* |
| F | M3 rule engine and severity (`core/rules.py`, `core/severity.py`) | C | Saaket* |
| G | M4 scoring, history, persistence (`core/scoring.py`, `core/history.py`, `core/storage.py`) | C | Harshita* |
| H | CLI, formatter, samples (integration) | D, E, F, G | all four |
| I | Test packages and coverage gate | H | all four |
| J | Symbolic execution and concolic write-ups | I | all four |
| K | Measurement artifacts (PERT, COCOMO, EVM, burndown) | H | all four |
| L | CMMI Level 2 audit pack | B | all four |
| M | Report | J, K, L | all four |
| N | Video demonstration | M | all four |
| O | Packaging and lab verification | N | all four |

\* Primary owner. After planning poker the per-member point totals were 36/55/40/55, a
19-point spread against the brief's requirement that they be relatively equal, so two
same-sprint story swaps were made: US05 ↔ US36 and US20 ↔ US11. Ownership is therefore per
**function**, not per module — Saaket owns US11 inside `core/complexity.py`, and Gunjan
owns US36 inside `core/storage.py`. The work packages below are still the right unit for
scheduling, because the dependencies run between modules rather than between people.

**Why D depends on E.** The scanner counts the five decision keywords separately and calls
`core.complexity.decision_points(...)` to aggregate them, so M2's function must exist before
M1's `scan_file` can be finished. The alternative — duplicating the summation inside the
scanner — would have left US10 as dead code that still had to be tested and symbolically
analysed. The dependency is a deliberate design decision, recorded in the project ledger.

## 3. Computed network

| Act | O | M | P | TE | Var | ES | EF | LS | LF | Slack | Critical |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A | 2 | 3 | 5 | 3.17 | 0.25 | 0.00 | 3.17 | 0.00 | 3.17 | 0.00 | **yes** |
| B | 1 | 1 | 3 | 1.33 | 0.11 | 3.17 | 4.50 | 3.17 | 4.50 | 0.00 | **yes** |
| C | 1 | 2 | 3 | 2.00 | 0.11 | 4.50 | 6.50 | 4.50 | 6.50 | 0.00 | **yes** |
| E | 3 | 5 | 8 | 5.17 | 0.69 | 6.50 | 11.67 | 6.50 | 11.67 | 0.00 | **yes** |
| D | 4 | 6 | 10 | 6.33 | 1.00 | 11.67 | 18.00 | 11.67 | 18.00 | 0.00 | **yes** |
| F | 3 | 4 | 7 | 4.33 | 0.44 | 6.50 | 10.83 | 13.67 | 18.00 | 7.17 | no |
| G | 4 | 5 | 9 | 5.50 | 0.69 | 6.50 | 12.00 | 12.50 | 18.00 | 6.00 | no |
| H | 2 | 3 | 6 | 3.33 | 0.44 | 18.00 | 21.33 | 18.00 | 21.33 | 0.00 | **yes** |
| I | 4 | 6 | 11 | 6.50 | 1.36 | 21.33 | 27.83 | 21.33 | 27.83 | 0.00 | **yes** |
| J | 5 | 8 | 14 | 8.50 | 2.25 | 27.83 | 36.33 | 27.83 | 36.33 | 0.00 | **yes** |
| K | 2 | 4 | 7 | 4.17 | 0.69 | 21.33 | 25.50 | 32.17 | 36.33 | 10.83 | no |
| L | 2 | 3 | 5 | 3.17 | 0.25 | 4.50 | 7.67 | 33.17 | 36.33 | 28.67 | no |
| M | 3 | 5 | 9 | 5.33 | 1.00 | 36.33 | 41.67 | 36.33 | 41.67 | 0.00 | **yes** |
| N | 1 | 2 | 4 | 2.17 | 0.25 | 41.67 | 43.83 | 41.67 | 43.83 | 0.00 | **yes** |
| O | 1 | 2 | 4 | 2.17 | 0.25 | 43.83 | 46.00 | 43.83 | 46.00 | 0.00 | **yes** |

### Worked example of each calculation, for activity I

- `TE = (4 + 4 x 6 + 11) / 6 = 39 / 6 = 6.50` days
- `Var = ((11 - 4) / 6)^2 = (1.1667)^2 = 1.36`
- forward pass: I's only predecessor is H, whose `EF = 21.33`, so `ES = 21.33` and
  `EF = 21.33 + 6.50 = 27.83`
- backward pass: I's only successor is J, whose `LS = 27.83`, so `LF = 27.83` and
  `LS = 27.83 - 6.50 = 21.33`
- `Slack = LS - ES = 21.33 - 21.33 = 0`, so I is on the critical path

## 4. Network diagram

Activity-on-node. Critical path drawn with `===`, non-critical with `---`.

```
                                  +--- F (4.33, slack 7.17) ---+
                                  |                            |
                                  +--- G (5.50, slack 6.00) ---+
                                  |                            |
  A ==== B ==== C =================+==== E ==== D =============+==== H ====+
 3.17   1.33   2.00                      5.17   6.33                3.33   |
          |                                                                |
          +--- L (3.17, slack 28.67) ----------------------+               |
                                                           |               |
                                       +--- K (4.17, slack 10.83) ---+     |
                                       |                             |     |
                                       +=============================+=====+
                                                                     |
                                       I ==== J ==== M ==== N ==== O  |
                                      6.50   8.50   5.33   2.17  2.17 |
                                       +-----------------------------+
```

Read as: `A -> B -> C` is sequential setup; `E` must finish before `D`, while `F` and `G`
run in parallel with them; all four member slices converge on `H`; `I -> J -> M -> N -> O`
is the sequential tail; `K` and `L` hang off `H` and `B` respectively with large slack.

## 5. Results

- **Project duration: 46.00 working days.**
- **Critical path: A → B → C → E → D → H → I → J → M → N → O.**
- Critical path variance = 7.72, standard deviation = **2.78 days**.
- Sum of all activity durations = 63.17 days, so parallel work across the four members
  saves 17.17 days against doing everything serially.

### Probability of meeting the deadline

Assuming the critical path total is approximately normal with mean 46.00 and standard
deviation 2.78 days, the probability of finishing within *n* days is `P(Z <= (n - 46) / 2.78)`:

| Target | Z | Probability |
|---|---|---|
| 42 days | -1.44 | ~7% |
| 46 days | 0.00 | 50% |
| 50 days | +1.44 | ~93% |
| 52 days | +2.16 | ~98% |

## 6. Interpretation and the schedule risk this exposes

The calendar from 5 November 2026 to 3 January 2027 holds roughly **41 working days** once
weekends are excluded. The critical path needs 46, and the estimate has a standard
deviation of 2.78 days, so the plan as estimated has only about a 7% chance of finishing
inside the available window. This is a real finding, not a presentational one, and three
mitigations follow directly from the table:

1. **J (8.50 days) is the single largest activity on the critical path.** The symbolic and
   concolic write-ups do not need the *coverage gate* to be finished, only the functions
   they analyse. Starting J for each member's functions as soon as that member's slice
   merges — overlapping J with I — removes up to 6.5 days from the path.
2. **K and L have 10.83 and 28.67 days of slack.** Both are documentation activities, so
   they are the right work to give a member who is blocked, and neither should ever be the
   reason the project is late.
3. **F and G carry 7.17 and 6.00 days of slack** because the `E → D` chain is longer than
   either. Saaket and Harshita therefore have genuine spare capacity in Sprints 1 and 2,
   which is the capacity that funds mitigation 1.

Applying mitigation 1 alone shortens the critical path to about 39.8 days, which fits the
window with roughly 60% confidence. That is the schedule the team is working to.
