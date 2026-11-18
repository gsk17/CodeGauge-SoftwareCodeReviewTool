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

---

## 2026-11-17 (Sprint 1, day 6)

**Gunjan**
- Yesterday: US02 `count_leading_spaces` implemented
- Today: US02 white-box, symbolic and concolic cases; pull request #42 reviewed
  by Kasam and merged. Reviewed and merged Harshita's US30 (#45)
- Hours on US02: 5.0 against a 6 hour budget
- Impediments: none

**Kasam**
- Yesterday: US12 `max_nesting_depth` implemented
- Today: US12 white-box, symbolic and concolic cases; pull request #43 reviewed
  by Saaket and merged. Reviewed and merged Gunjan's US02 (#42)
- Hours on US12: 6.0 against a 10 hour budget
- Impediments: none. US20 `rule_nesting` starts tomorrow and needs
  `core/rules.py`, which reached `main` with US19 this afternoon

**Saaket**
- Yesterday: US19 `rule_complexity` implemented, creating `core/rules.py`
- Today: US19 white-box, symbolic and concolic cases; pull request #44 reviewed
  by Harshita and merged. Reviewed and merged Kasam's US12 (#43).
  **All three Sprint 1 stories complete**
- Hours on US19: 4.5 against a 10 hour budget
- Impediments: none

**Harshita**
- Yesterday: US30 `grade_band` implemented
- Today: US30 white-box, symbolic and concolic cases; pull request #45 reviewed
  by Gunjan and merged. Reviewed and merged Saaket's US19 (#44)
- Hours on US30: 3.5 against a 6 hour budget
- Impediments: none

**Four stories merged, one per member, 16 points in a day.** Each member both
gave and received exactly one review, following the rotation in
`story-workflow.md`, so the peer-review evidence for the day is complete.

**Notes from today.**

`core/rules.py` is now on `main` with `rule_complexity` and the
`CODE_COMPLEXITY` constant. **Kasam is unblocked for US20**, which adds
`rule_nesting` and a `CODE_NESTING` constant to the same module tomorrow. This
is the second time a story has been sequenced behind another member's merge
rather than blocked by it - US28 waited on US26 the same way last Wednesday -
and in both cases the dependency was identified at planning and ordered around,
not discovered during the work.

**Two symbolic analyses found something the black-box tests could not.**

US19 is the first analysis in the project whose tree crosses a call boundary.
Inlining `classify_severity` showed that its INFO branch is guarded by
`cc <= limit`, which `rule_complexity` has already consumed by returning None -
so the conjunction is unsatisfiable and **this rule can never emit an INFO
issue**. Composed with the US26 finding that a limit of 1 collapses MINOR and
MAJOR, it follows that **at a limit of 1 the rule emits only CRITICAL**. The
number of severities the tool can report therefore depends on how it is
configured. Neither function shows this alone; it took the composed tree.

US12 is the first looping function analysed, so the tree is infinite and the
unrolling had to be bounded at k = 2. The analysis found that three path
conditions have a *unique* solution rather than an interval: `deepest` starts at
0 and validation forces depths non-negative, so the false branch of the scan
comparison on the first iteration requires exactly 0. The random-based test
samples depths in 0..20 and would reach that branch roughly once in twenty-one
lists, by chance.

Both findings go in the sprint review. They are the clearest evidence so far
that the white-box work is doing something the black-box work does not.

**Two honest limitations recorded rather than smoothed over.** The concolic walk
for US12 reaches 9 of its 10 bounded paths and the walk for US02 reaches 6 of
11, because loop length is not a branch condition and the solver cannot change
it. Both write-ups say so and point at the symbolic analysis that covers the
rest. A coverage table claiming 100% in both cases would have been easy to write
and worth less.

**Measurement.** Nine stories closed, 49.0 hours against an 84 hour budget, CPI
**1.71**. With nine data points the pattern is no longer ambiguous: fitting the
group means gives `hours = 3.0 + 0.5 x points`, so roughly **three hours of
every story is fixed process cost** - branch, five test packages, write-up, pull
request, review - and only about half an hour per point is the function itself.
That is why four of the five 5-point stories cost exactly 6.0 hours despite
being different functions in different modules written by three different
people. Recorded in `time-log.md` for the Sprint 1 review, where the rate
decision is due.

**Sprint status at end of day 6:** **9 of 12 stories done, 42 of 56 points.**
14 remaining against an ideal of 22.4 - **8.4 points ahead of the line**, the
largest lead of the sprint and a full recovery from the 13 November gap.

Remaining: US07 (Gunjan, 3), US20 (Kasam, 3), US29 (Harshita, 8). Saaket has
finished Sprint 1 two days early and will review the other three rather than
take new work, since pulling a Sprint 2 story forward would distort the velocity
figure the next sprint is planned from.

---

## 2026-11-18 (Sprint 1, day 7)

**Gunjan**
- Yesterday: US02 merged by pull request #42
- Today: US07 `is_function_header` — failing tests written in both black-box
  packages and observed failing, `4e1c706`
- Impediments: `.git/config.lock` could not be renamed when `git push -u` tried
  to record the upstream branch. The push itself reached GitHub; only the local
  tracking entry failed. Resolved by deleting the stale lock and setting the
  upstream separately. **`push -u` is now split into `git push` followed by
  `git branch --set-upstream-to` for everyone**, which closes the window where
  another process can hold `.git/config` open

**Kasam**
- Yesterday: US12 merged by pull request #43
- Today: US20 `rule_nesting` — failing tests written in both black-box packages
  and observed failing, `2ec1772`
- Impediments: none. The branch was cut from `main`, which already carried
  `core/rules.py` from Saaket's US19 merge yesterday, so the dependency
  identified at planning never became a block

**Harshita**
- Yesterday: US30 merged by pull request #45
- Today: US29 `score_from_issues` — failing tests written in both black-box
  packages and observed failing, `8c4bc45`
- Impediments: none

**Saaket**
- Yesterday: US19 merged; all three Sprint 1 stories complete
- Today: no story work — Sprint 1 allocation finished. Wrote the README's
  **Known limitations** section, twelve entries, six of them derived from the
  symbolic execution analyses rather than observed. Then corrected one of his
  own entries and recorded a defect found while checking it
- Impediments: none

### A defect found by analysis, not by testing

Checking a claim in the limitations section against `model/thresholds.py` turned
up the following chain:

1. The symbolic execution of `classify_severity` (US26) showed that a limit of 1
   makes the MINOR and MAJOR bands unsatisfiable — `actual <= 1 + floor(1/2)` is
   consumed by INFO, and `actual > 1 and actual < 2` has no integer solution.
2. The inter-procedural analysis of `rule_complexity` (US19) showed that no rule
   can emit INFO, because `actual > limit and actual <= limit` is
   unsatisfiable.
3. Composing them: **at a limit of 1 every finding any rule raises is
   CRITICAL.** Three of the four severity bands are unreachable.
4. `Thresholds.validate` rejects 0 and below, and **permits 1**.

So a user can set, from the menu, precisely the configuration at which the
severity scale collapses, and nothing warns them.

**Every test in the project passes and coverage is 100%.** No black-box test
would find this — each function is correct in isolation. It took reasoning about
path conditions across two members' modules to reach a line of validation code
in a third file that nobody owns.

The validator has **not** been changed. `model/thresholds.py` is shared
scaffolding rather than a graded story, it has its own tests, and the fix is a
one-character change whose justification is three pages of path conditions.
Changing it quietly would discard the only part of it worth anything. It goes to
the Sprint 1 review on Sunday as a finding with a decision attached — tighten
the validator to 2, or warn at 1 and allow it — and the decision will be
recorded in the retrospective either way.

This is the clearest answer the project has so far to "what did the measurement
tell us", and it should lead the sprint review.

### A correction to yesterday's own work

The first version of limitation 2 said `tab_width` was "configurable, defaulting
to 4". Neither half was true: `tab_width` is a required parameter of
`count_leading_spaces`, `Thresholds` does not carry it, and no default exists
anywhere in the source. The entry advised users to set it to 8, which they
cannot do.

Corrected the same day, in `e082e3b`'s successor. Recorded here rather than
silently amended, because the README is the document the markers read first and
a wrong claim in it is worse than a missing one. Adding `tab_width` to
`Thresholds` is now a Sprint 3 candidate.

### Notes from today

**US29 has the only genuinely subtle specification in Sprint 1.** The score is
capped at 40 when three or more critical issues are present, and floored at 0.
The two interact, and the order matters: with ten critical issues the raw score
is `100 - 150 = -50`. A cap written as an assignment — "if critical >= 3 then
score = 40" — returns 40, so ten critical issues would score *better* than five.
The cap has to be a minimum against the running score, applied before the floor.
`(3,0,0,0) == 40` and `(10,0,0,0) == 0` are the only pair of cases that
distinguishes the two readings, and both are in the partition tests Harshita
committed today.

**US20 is deliberately almost identical to US19**, and the last partition test
turns that into evidence: it asserts the two rules produce identical severities
for identical numbers while carrying different codes. That is the test that
fails if either story re-implements the bands instead of delegating to
`classify_severity`. It imports `rule_complexity`, which is Saaket's function —
as a consumer, not a change, and agreed at this stand-up so that ownership is
not in doubt.

**Sprint status at end of day 7:** 9 of 12 stories done, 42 of 56 points.
14 remaining against an ideal of 16.8 — **2.8 points ahead of the line**. The
three stories in progress are worth exactly the 14 that remain, and all three
merge on Friday.

Saaket has finished his Sprint 1 allocation and is not taking a Sprint 2 story
forward: velocity is the figure Sprint 2 gets planned from, and borrowing
against it now would make that forecast worse rather than better. He reviews the
three remaining pull requests on Friday instead, and drafts the sprint review
and retrospective before Sunday.
