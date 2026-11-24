# Sprint 1 Review

**Meeting date:** 24 November 2026 (planned for the 22nd; see the note below)
**Attending:** Gunjan, Kasam, Saaket, Harshita

> **Sections 1 to 4 were prepared on 19 November, before the meeting**, so that
> the meeting could inspect the evidence rather than spend its time gathering
> it. The three stories open at that point — US07, US20 and US29 — all merged on
> **Friday 20 November**, and the projected figures below have been replaced
> with actuals.
>
> **The meeting was held on 24 November, not the 22nd as planned.** The sprint
> itself finished on time; the review and retrospective slipped over the
> weekend. Recorded rather than back-dated.

The sprint review inspects the **increment**: what was actually built,
demonstrated against the Definition of Done. It is not a status meeting — a
story is either demonstrated working or it is not Done.

## 1. Sprint goal

> A file can be scanned into per-function records, its complexity measured, the
> first rules raised against it and a score produced — the thin end-to-end
> thread through every member's slice.

**Met in part, and the gap is worth stating precisely.** Every *function* in the
thread exists and is tested, one per layer:

| Layer | Function | Story | Member |
|---|---|---|---|
| scan | `classify_line`, `count_leading_spaces`, `is_function_header` | US01, US02, US07 | Gunjan |
| measure | `decision_points`, `cyclomatic_complexity`, `max_nesting_depth` | US10, US11, US12 | Kasam / Saaket |
| rule | `classify_severity`, `rule_complexity`, `rule_nesting` | US26, US19, US20 | Saaket / Kasam |
| score | `weighted_penalty`, `score_from_issues`, `grade_band` | US28, US29, US30 | Harshita |

What does **not** exist is anything that joins them. `scan_file` (US09) is a
Sprint 3 story, and there is no CLI until Sprint 3 either, so a file cannot yet
be passed in at one end and a grade read off the other. The thread is complete
as a set of parts, not as a path.

That was the plan rather than a shortfall — US09 was placed in Sprint 3
deliberately at Sprint 0, because it consumes every other scanner function — but
the goal as written says "a file can be scanned", which overstates what a sprint
of single functions can deliver. **The Sprint 2 goal should be phrased in terms
of functions delivered rather than end-to-end behaviour**, or it will overstate
again.

## 2. Increment demonstrated

Demonstrate by running each member's test packages in front of the team, not by
describing them:

```bash
python -m pytest gsk17/test -v      # and khm12, ssl21, hcg22
python -m coverage run -m pytest && python -m coverage report -m
```

| ID | Owner | Function | Pts | Done? | Merged | Notes |
|---|---|---|---|---|---|---|
| US01 | Gunjan | `classify_line` | 3 | ✅ | 11 Nov | reference story; set the three-commit pattern the other 35 follow |
| US02 | Gunjan | `count_leading_spaces` | 3 | ✅ | 17 Nov, #42 | first function with a loop, so first bounded-unrolling analysis |
| US07 | Gunjan | `is_function_header` | 3 | ✅ | 20 Nov, #46 | no loop, so the cleanest symbolic tree in the project |
| US10 | Kasam | `decision_points` | 5 | ✅ | 11 Nov | |
| US12 | Kasam | `max_nesting_depth` | 5 | ✅ | 17 Nov, #43 | first looping function analysed; three single-solution path conditions |
| US20 | Kasam | `rule_nesting` | 3 | ✅ | 20 Nov, #47 | the two US19 findings shown to be properties of the rule shape |
| US11 | Saaket | `cyclomatic_complexity` | 8 | ✅ | 15 Nov, #41 | finished in an unplanned Sunday session to recover the lost Friday |
| US19 | Saaket | `rule_complexity` | 5 | ✅ | 17 Nov, #44 | created `core/rules.py`; first inter-procedural analysis |
| US26 | Saaket | `classify_severity` | 5 | ✅ | 11 Nov | dependency root — every rule story calls it |
| US28 | Harshita | `weighted_penalty` | 5 | ✅ | 11 Nov | waited on US26 for the severity constants |
| US29 | Harshita | `score_from_issues` | 8 | ✅ | 20 Nov, #48 | the cap proved to fire only at exactly three critical issues |
| US30 | Harshita | `grade_band` | 3 | ✅ | 17 Nov, #45 | |

**12 of 12 Done. 56 of 56 points. Nothing carried over.**

Every merged story went through a reviewed pull request, reviewed by a different
member on the rotation Gunjan → Kasam → Saaket → Harshita → Gunjan, and
**no branch has been deleted**.

## 3. Stories not Done

**None.** All twelve committed stories merged within the sprint, the last three
on Friday 20 November. Carry-over is zero and the velocity figure below needs no
adjustment.

## 4. Measurement

| Measure | Value at close | How it was obtained |
|---|---|---|
| Committed points | 56 | `sprint-1-backlog.md` |
| **Completed points (velocity)** | **56** | closed issues |
| Carried over | 0 | |
| Stories Done | 12 of 12 | |
| Tests passing | **492** | `python -m pytest -q` |
| Statement coverage of `core/` | **100%** | `python -m coverage report -m` |
| Statement coverage overall | 99% | one line, `model/thresholds.py:43` |
| PV | 112 h | 56 points x 2 h |
| EV | 112 h | 56 points closed x 2 h |
| AC | **66.0 h** | `time-log.md` |
| CV = EV - AC | **+46.0 h** | under budget |
| SV = EV - PV | **0.0 h** | exactly on schedule |
| **CPI = EV / AC** | **1.70** | |
| **SPI = EV / PV** | **1.00** | |
| EAC = BAC / CPI | 231 h | 392 / 1.697 |
| TCPI | 0.859 | 280 / 326 |

The final three stories came in at US07 5.0 hours, US20 2.5 and US29 9.5 —
matching the forecast made on 19 November. **US20 at 2.5 hours is the cheapest
story of the sprint and US29 at 9.5 the most expensive**, and the reason is in
the retrospective: US19 had already settled the rule shape US20 reuses, while
nothing preceded US29.

Burndown: `python docs/measurement/scripts/burndown.py 1`, with dated snapshots
in [../measurement/charts/](../measurement/charts/).

### What the numbers say

**SPI of 1.00 with a CPI of 1.70** is the clearest possible reading: the sprint
delivered exactly what it committed, on time, using 40% fewer hours than
budgeted. That is not fast work — it is an estimate that was too generous, and
the full analysis is in [../measurement/time-log.md](../measurement/time-log.md).

**Velocity of 56 is not a safe basis for Sprint 2.** Sprint 2 is committed at 63
points and Sprint 3 at 77 — a 13% and a 38% stretch on demonstrated capacity.
The retrospective set a measurable trigger rather than moving stories now: at
the Sprint 2 review on 6 December, Sprint 2's actual hours are compared against
80, and the COULD stories come out of Sprint 3 if it is over.

**One member finished early.** Saaket completed his three Sprint 1 stories on 17
November, two days before the other three members, and took no further story —
deliberately, because velocity is the figure Sprint 2 is planned from and
borrowing against it would make that forecast worse. He reviewed pull requests
and wrote documentation instead. This is a consequence of allocating stories per
member rather than pulling from a shared backlog, which the project does because
the testing and research marks are individual.

## 5. Defect raised at this review

**`Thresholds.validate` permits a limit of 1**, which is the configuration at
which three of the four severity bands become unreachable.

The chain, all of it derived rather than observed:

1. Symbolic execution of `classify_severity` (US26): at a limit of 1, MINOR
   needs `actual <= 1 + floor(1/2) = 1` — already taken by INFO — and MAJOR
   needs `actual > 1 and actual < 2`, which has no integer solution. **Both
   bands are unsatisfiable.**
2. Inter-procedural analysis of `rule_complexity` (US19): every rule returns
   `None` when the measurement is within its limit, which is exactly the INFO
   condition, so `actual > limit and actual <= limit` is unsatisfiable. **No
   rule can emit INFO.**
3. Composed: **at a limit of 1, every finding any rule raises is CRITICAL.**
4. `Thresholds.validate` rejects 0 and below. It permits 1.

**Every test in the project passes and `core/` coverage is 100%.** No black-box
test would find this — each function is correct in isolation. It took reasoning
about path conditions across two modules to reach a line of validation code in a
third file that no story owns.

**Decision taken: tighten `validate` to reject values below 2. Owner Saaket,
Sprint 2.** There is no CLI yet to display a warning in, nothing is lost by
forbidding a configuration no user wants, and the reasoning goes in the commit
message rather than only in a one-character diff. Full rationale in
[sprint-1-retrospective.md](sprint-1-retrospective.md) section 5.2.

## 6. Increment tagged

```bash
git tag -a v0.1.0 -m "Sprint 1 increment: 12 stories, 56 points, scan/measure/rule/score functions"
git push origin v0.1.0
```

Tagged on 24 November, at the review, on commit `722c822` — the sprint close,
with all twelve stories merged and nothing outstanding.

## 7. Board screenshot

Saved to `docs/measurement/board-sprint1.png`, showing the 12 Sprint 1 stories,
their owners, their story points and their start and end dates, with all 12 in
the Done column.

The four story-point corrections from the round 2 planning poker — **US14 → 5,
US15 → 8, US24 → 5, US31 → 8** — were applied to the board before the screenshot
was taken, so the board, [product-backlog.md](product-backlog.md) and
[../measurement/planning-poker.md](../measurement/planning-poker.md) now agree.

## 8. One observation the numbers nearly hide

`model/thresholds.py` line 43 is the **only** statement in `core/` or `model/`
with no test exercising it — and it sits inside `Thresholds.validate`, the
function carrying the defect recorded in section 5.

Untested code and a latent defect in the same three lines is the correlation
quality assurance exists to predict, and it is worth stating rather than hoping
nobody reads the 99% next to the 100%. The Sprint 2 fix adds the missing test
along with the tightened guard.
