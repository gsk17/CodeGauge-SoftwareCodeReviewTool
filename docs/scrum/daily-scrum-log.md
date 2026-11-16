# Daily Scrum Log

One entry per member per working day, written at the fifteen-minute stand-up and
committed the same day. Sprint 1 runs 9–22 November 2026.

---

## 2026-11-10 (Sprint 1, day 1)

**Gunjan**
- Yesterday: sprint planning; repository created, project board set up with the Sprint,
  Story Points, Start date and End date fields; 12 Sprint 1 issues created
- Today: US01 `classify_line` — failing tests written and observed failing, then the
  implementation
- Impediments: none

**Kasam, Saaket, Harshita**
- Not available today
- Impediments: awaiting repository collaborator access

---

## 2026-11-11 (Sprint 1, day 2)

**Gunjan**
- Yesterday: US01 implementation complete
- Today: US01 white-box, symbolic and concolic cases; reviewed and merged Kasam's US10;
  US01 merged by Kasam
- Impediments: none

**Kasam**
- Yesterday: repository access received, clone set up
- Today: US10 `decision_points` — three commits complete, merged by Saaket. Removed two
  write-ups committed in error that belonged to Saaket and Harshita
- Impediments: branch was cut from the US01 branch rather than `main`, so the pull request
  initially carried US01's commits. Resolved by merging US01 first

**Saaket**
- Yesterday: repository access received
- Today: US26 `classify_severity` — three commits complete, merged by Harshita. Reviewed
  and merged Kasam's US10
- Impediments: none

**Harshita**
- Yesterday: repository access received
- Today: US28 `weighted_penalty` — three commits complete, merged by Gunjan. Reviewed and
  merged Saaket's US26
- Impediments: US28 imports the severity constants from US26, so the implementation
  commit had to wait for Saaket's merge. Sequenced rather than blocked

**Sprint status at end of day 2:** 4 of 12 stories done, 18 of 56 points.
38 remaining against an ideal of 44.8 — ahead of the line.

---

## 2026-11-12 (Sprint 1, day 3)

**Saaket**
- Yesterday: US26 `classify_severity` complete and merged; reviewed and merged Kasam's US10
- Today: US11 `cyclomatic_complexity` — failing tests written and observed failing, then
  the implementation. This is the first story to carry both black-box packages
- Impediments: none. US11 edits `core/complexity.py`, which is Kasam's module, so the two
  of us agreed the boundary before starting - ownership is per function, not per file

**Gunjan**
- Yesterday: US01 merged; pushed the Sprint 0 planning artifacts and the poker evidence
- Today: adopted the round 2 poker values across every document — 196 points, sprint
  totals 56/63/77, EVM baseline 392 person-hours. Added the random-based black-box tests
  the brief requires and that the first four stories had shipped without
- Impediments: the Definition of Done said only "black-box test cases" and did not name
  both required strategies, which is how the omission reached four merged stories. Both
  it and the story workflow now name the two packages explicitly

**Kasam**
- Yesterday: US10 merged
- Today: no story work; US12 starts tomorrow
- Impediments: none

**Harshita**
- Yesterday: US28 merged; reviewed and merged Saaket's US26
- Today: no story work; US30 starts tomorrow
- Impediments: none

**Sprint status at end of day 3:** 4 of 12 stories done, 18 of 56 points. 38 remaining
against an ideal of 39.2 — level with the line. US11 is in progress and due 17 Nov.

---

## 2026-11-13 (Sprint 1, day 4)

**No stand-up held and no story work on any branch.**

US11's implementation commit, which was due this day, did not happen, and the
planned starts for US02 (Gunjan), US12 (Kasam) and US30 (Harshita) did not
happen either. The last commit on any branch remains `2bd851c`, US11's failing
tests, dated 12 November.

**Sprint status at end of day 4:** 4 of 12 stories done, 18 of 56 points.
38 remaining against an ideal of 33.6 — **4.4 points behind the line**, the
first time this sprint the actual has been worse than ideal.

*This entry was written on 15 November, not on the day. It is recorded rather
than back-dated because the commit history shows the gap plainly and a
stand-up minute claiming otherwise would contradict it. The corrective action
is in the 15 November entry below: the day was recovered by working the
Sunday rather than by moving a story into Sprint 2.*

---

## 2026-11-15 (Sprint 1, unplanned Sunday session)

**Saaket**
- Since Thursday: US11 failing tests committed and observed failing; nothing on
  Friday
- Today: US11 `cyclomatic_complexity` — implementation commit, then the
  white-box, symbolic and concolic cases. Pull request #41 reviewed by
  Harshita and merged to `main` with a merge commit, two days ahead of the
  17 November date on the board. Then started US19 `rule_complexity`:
  failing tests written in both black-box packages and observed failing on
  `ModuleNotFoundError: No module named 'core.rules'`
- Impediments: none. The function lives in `core/complexity.py`, Kasam's module,
  under the per-function ownership agreed on 12 November

**Gunjan**
- Today: recorded the 13 November gap in the burndown and in this log; re-cut
  the remaining Sprint 1 work. Started US02 `count_leading_spaces`: failing
  tests written in both black-box packages and observed failing
- Impediments: none

**Kasam**
- Since Thursday: US10 merged on Wednesday; no work Friday
- Today: started US12 `max_nesting_depth`: failing tests written in both
  black-box packages and observed failing
- Impediments: none

**Harshita**
- Since Thursday: US28 merged on Wednesday; no work Friday
- Today: reviewed and merged Saaket's US11 pull request #41. Started US30
  `grade_band`: failing tests written in both black-box packages and
  observed failing
- Impediments: none

**Why a weekend session.** Friday's loss put the sprint behind the ideal line
for the first time. Two options were considered: move one story to Sprint 2, or
recover the day. Sprint 2 is already 63 points against Sprint 1's 56, and
Sprint 3 is 77, so pushing work downstream makes the heaviest sprints heavier.
Recovering the day was chosen instead, and US11 — whose implementation was
already specified and whose tests were already written — was the cheapest story
to finish on a Sunday.

**The re-cut plan.** Rather than wait for Monday, all four members took their
next story today and committed its failing tests, which is the cheapest step in
the ten-step workflow and the one that unblocks Monday entirely. That pulls the
whole week forward by a day and gives the sprint two days of slack at the end
instead of none.

| Day | Gunjan | Kasam | Saaket | Harshita |
|---|---|---|---|---|
| **Sun 15** | **US02 c1** | **US12 c1** | **US11 c2+c3 → merged** · **US19 c1** | **US30 c1** |
| Mon 16 | US02 c2 | US12 c2 | US19 c2 | US30 c2 |
| Tue 17 | US02 c3 → merge | US12 c3 → merge | US19 c3 → merge | US30 c3 → merge |
| Wed 18 | US07 c1 | US20 c1 | — three stories done | US29 c1 |
| Thu 19 | US07 c2 | US20 c2 | — | US29 c2 |
| Fri 20 | US07 c3 → merge | US20 c3 → merge | — | US29 c3 → merge |
| Sat 21 | slack | slack | slack | slack |
| Sun 22 | sprint review and retrospective | | | |

By the end of Tuesday 17 that is **42 of 56 points** closed, leaving US07 (3),
US20 (3) and US29 (8) for the back half of the week — 14 points across three
days, against three members. Saaket finishes his three Sprint 1 stories on
Tuesday because US11 absorbed his Sunday, so he carries no Wednesday start.

**`core/rules.py` does not exist yet**, which is why US19 commit 1 fails on
`ModuleNotFoundError` rather than `ImportError`. US19 (Saaket) and US20 (Kasam)
both need the module. Agreed today: **Saaket creates it** with `rule_complexity`
in his US19 implementation commit, and Kasam adds `rule_nesting` to it on
Wednesday, after US19 has merged. Sequenced rather than blocked, the same way
US28 waited on US26 last Wednesday.

**Sprint status at end of 15 November:** 5 of 12 stories **done**, 26 of 56
points, 30 remaining. Four more stories are **in progress** with their failing
tests committed, worth a further 16 points; under the 0/100 rule they earn
nothing until they merge, so the burndown still reads 30.

Friday's 4.4-point deficit is cleared and the sprint is ahead of the line again.

---

## 2026-11-16 (Sprint 1, day 5)

**Gunjan**
- Yesterday: recorded the 13 November gap; US02 failing tests committed and
  observed failing
- Today: US02 `count_leading_spaces` implemented, `86e9034`. Tests went from
  `ImportError` to green
- Impediments: none

**Kasam**
- Yesterday: US12 failing tests committed and observed failing
- Today: US12 `max_nesting_depth` implemented, `582b03b`
- Impediments: none

**Saaket**
- Yesterday: US11 merged by pull request #41; US19 failing tests committed and
  observed failing on `ModuleNotFoundError`
- Today: US19 `rule_complexity` implemented, `33ebcc0`, which **creates
  `core/rules.py`** — the module Kasam needs on Wednesday for US20
- Impediments: none

**Harshita**
- Yesterday: reviewed and merged US11; US30 failing tests committed and observed
  failing
- Today: US30 `grade_band` implemented, `a95d826`
- Impediments: none

**Notes from today.**

`core/rules.py` now exists with `rule_complexity` and the `CODE_COMPLEXITY`
constant. Kasam adds `rule_nesting` and a `CODE_NESTING` constant to the same
module on Wednesday, once US19 has merged — the sequencing agreed yesterday, and
the same pattern as US28 waiting on US26 last Wednesday.

`rule_complexity` delegates its severity to `classify_severity` rather than
banding the value itself. That is why 11 against a limit of 10 reports MINOR
while 20 against the same limit reports CRITICAL, without the rule knowing
anything about the bands. It is the clearest dependency between two members'
modules in the project so far, and both the US19 symbolic write-up and the
sprint review should say so.

Four implementations landed on four different files, so the four branches did
not collide. That was deliberate when the sprint was planned, and it is the
reason four people could work the same day without blocking each other.

**Verification run on all four branches together:** 206 tests pass, and
statement coverage of `core/` is 100% across all five modules.

**Sprint status at end of day 5:** 5 of 12 stories done, 26 of 56 points, 30
remaining against an ideal of 28.0 — 2 points behind, and all four stories in
progress merge tomorrow. Under the 0/100 rule none of their 16 points count
until then.
