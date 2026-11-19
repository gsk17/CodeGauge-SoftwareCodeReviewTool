# Sprint 1 Review

**Meeting date:** 22 November 2026
**Attending:** Gunjan, Kasam, Saaket, Harshita

> **Prepared on 19 November, before the meeting.** Sections 1 to 4 assemble the
> evidence so the meeting can inspect it rather than spend its time gathering
> it. Sections 5 to 7 are the meeting's own output and are completed on the day.
>
> **Three stories were still open when this was prepared** — US07, US20 and
> US29 — and are marked as such throughout. Their commit 2 (implementation)
> landed on 19 November; commit 3 and the merges are due on Friday 20 November.
> Nothing below records them as Done, and the figures that depend on them are
> given as *projected* with the arithmetic shown, to be replaced with actuals on
> the day.

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
| US07 | Gunjan | `is_function_header` | 3 | ⏳ | due 20 Nov | implementation in `bce23cd`; commit 3 outstanding |
| US10 | Kasam | `decision_points` | 5 | ✅ | 11 Nov | |
| US12 | Kasam | `max_nesting_depth` | 5 | ✅ | 17 Nov, #43 | first looping function analysed; three single-solution path conditions |
| US20 | Kasam | `rule_nesting` | 3 | ⏳ | due 20 Nov | implementation in `b6937a7`; commit 3 outstanding |
| US11 | Saaket | `cyclomatic_complexity` | 8 | ✅ | 15 Nov, #41 | finished in an unplanned Sunday session to recover the lost Friday |
| US19 | Saaket | `rule_complexity` | 5 | ✅ | 17 Nov, #44 | created `core/rules.py`; first inter-procedural analysis |
| US26 | Saaket | `classify_severity` | 5 | ✅ | 11 Nov | dependency root — every rule story calls it |
| US28 | Harshita | `weighted_penalty` | 5 | ✅ | 11 Nov | waited on US26 for the severity constants |
| US29 | Harshita | `score_from_issues` | 8 | ⏳ | due 20 Nov | implementation in `5b7022d`; commit 3 outstanding |
| US30 | Harshita | `grade_band` | 3 | ✅ | 17 Nov, #45 | |

**9 of 12 Done at preparation, 42 of 56 points.** Three in progress at commit 2
of 3, worth 14 points.

Every merged story went through a reviewed pull request, reviewed by a different
member on the rotation Gunjan → Kasam → Saaket → Harshita → Gunjan, and
**no branch has been deleted**.

## 3. Stories not Done

| ID | Owner | Points | What is missing | Carried to |
|---|---|---|---|---|
| US07 | Gunjan | 3 | commit 3 (white-box, symbolic, concolic) and the merge | — due 20 Nov, inside the sprint |
| US20 | Kasam | 3 | commit 3 and the merge | — due 20 Nov, inside the sprint |
| US29 | Harshita | 8 | commit 3 and the merge | — due 20 Nov, inside the sprint |

**None of these is expected to carry into Sprint 2.** All three have their
failing tests and implementation committed, and the remaining work is the same
shape as the nine already completed. If any does slip, its points are earned in
the sprint it closes in, not this one, and the velocity figure below has to be
reduced accordingly.

## 4. Measurement

| Measure | At preparation, 19 Nov | Projected at close, 22 Nov | How it was obtained |
|---|---|---|---|
| Committed points | 56 | 56 | `sprint-1-backlog.md` |
| Completed points (velocity) | 42 | **56** | closed issues |
| Carried over | 14 | 0 | |
| Stories Done | 9 of 12 | 12 of 12 | |
| Tests passing | 319 on `main` | 399+ | `python -m pytest -q` |
| Statement coverage of `core/` | 100% | 100% | `python -m coverage report -m` |
| PV | 112 h | 112 h | 56 points × 2 h |
| EV | 84 h | 112 h | points closed × 2 h |
| AC | 49.0 h | **66.0 h** | `time-log.md` |
| CPI = EV / AC | 1.71 | **1.70** | |
| SPI = EV / PV | 0.75 | **1.00** | |
| EAC = BAC / CPI | 229 h | **231 h** | 392 / 1.70 |

The 399-test figure counts the three open stories' black-box tests, which are on
their branches; it will rise again when their commit 3 adds the white-box
packages.

**The projected AC of 66.0 hours** is 49.0 actual plus 17.0 forecast for the
three open stories (US07 5.0, US20 2.5, US29 9.5). **Replace with actuals on the
day** — a projection in the AC column is not a measurement, and the CPI below
depends on it.

Burndown: `python docs/measurement/scripts/burndown.py 1`, with dated snapshots
in [../measurement/charts/](../measurement/charts/).

### What the numbers say

**SPI of 1.00 with a CPI of 1.70** is the clearest possible reading: the sprint
delivered exactly what it committed, on time, using 40% fewer hours than
budgeted. That is not fast work — it is an estimate that was too generous, and
the full analysis is in [../measurement/time-log.md](../measurement/time-log.md).

**Velocity of 56 is not a safe basis for Sprint 2.** Sprint 2 is already
committed at 63 points and Sprint 3 at 77. A velocity of 56 says 63 is a 13%
stretch and 77 a 38% one, and nothing in Sprint 1 demonstrates that capacity.
Discuss at the retrospective.

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

**Decision required at this meeting:** tighten `validate` to reject values below
2, or permit 1 and warn. Record it in the retrospective either way, with the
owner and the sprint.

## 6. Increment tagged

```bash
git tag -a v0.1.0 -m "Sprint 1 increment: 12 stories, 56 points, scan/measure/rule/score functions"
git push origin v0.1.0
```

Tag only once all three outstanding stories have merged. A tag on a tree with
open stories misrepresents the increment.

## 7. Board screenshot

Saved to `docs/measurement/board-sprint1.png`, showing the 12 Sprint 1 stories,
their owners, their story points and their start and end dates, with all 12 in
the Done column.

**Before taking it**, four story-point values still need correcting on the board
from the round 2 planning poker: **US14 → 5, US15 → 8, US24 → 5, US31 → 8**. The
screenshot is evidence, and evidence that contradicts
[../measurement/planning-poker.md](../measurement/planning-poker.md) is worse
than none.
