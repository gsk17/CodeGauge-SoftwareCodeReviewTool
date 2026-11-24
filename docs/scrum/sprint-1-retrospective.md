# Sprint 1 Retrospective

**Meeting date:** 24 November 2026 (planned for the 22nd; see the note below)
**Attending:** Gunjan, Kasam, Saaket, Harshita

> **Sections 1 to 3 were prepared on 19 November, before the meeting**, so that
> the meeting could argue about what the records mean rather than about what
> happened. **Sections 4 to 6 were completed at the meeting itself.**
>
> **The meeting was held on 24 November, not on the 22nd as planned.** The
> sprint ended on schedule — all 56 points merged on Friday 20 November — but
> the review and retrospective slipped over the weekend and were held on the
> Tuesday. The cost is two days of Sprint 2 begun without the retrospective's
> action in place, and it is recorded here rather than back-dated because the
> commit history shows it plainly.

The retrospective inspects the **process**, not the product — how the team
worked, and what one change it will make next sprint. Keep it honest: a
retrospective that records nothing to improve is evidence of nothing.

## 1. What went well

- **Dependencies were sequenced rather than hit.** Three stories needed another
  member's merge first — US28 on US26 for the severity constants, US11 inside
  Kasam's `core/complexity.py`, US20 on US19 creating `core/rules.py`. All three
  were identified at planning and ordered around. None became a block, and the
  only time a branch went wrong was Kasam's US10, cut from the US01 branch
  instead of `main` on 11 November, which was resolved by merging US01 first.

- **Per-function ownership worked.** `core/complexity.py` is Kasam's module and
  holds Saaket's `cyclomatic_complexity`; `core/rules.py` is Saaket's and holds
  Kasam's `rule_nesting`. Agreed at stand-up before the work in both cases, and
  neither produced a conflict.

- **The review rotation held for every story.** Gunjan → Kasam → Saaket →
  Harshita → Gunjan, so each member both gave and received review. Four pull
  requests merged on 17 November, each by a different reviewer.

- **The white-box work found things the black-box work did not.** Three times,
  and they are listed in section 3 rather than here because they are findings,
  not process observations.

- **The gap was recorded rather than hidden.** Nobody worked on Friday 13
  November. It is in the burndown as a row, in the daily scrum log as an entry
  that says so on its face, and the recovery decision is written next to it.

## 2. What did not go well

- **A full working day was lost to rework caused by a vague Definition of Done.**
  The DoD said "black-box test cases" without naming both required strategies,
  and four stories merged on 11 November with only equivalence partitioning. The
  omission was caught on 12 November and cost that whole day to fix — four
  `random_testing` packages written retrospectively, earning zero story points.
  The DoD now names both strategies explicitly, in `cdfc8e7`.

  **This is the most expensive process defect of the sprint**, and the cause was
  a document that was not specific enough to be checkable.

- **Friday 13 November: no work on any branch.** Four people, nothing committed.
  It put the sprint behind the ideal line for the first time, at +4.4 points, and
  the recovery cost an unplanned Sunday session.

- **Three of four members had no repository access on day 1.** Collaborator
  invites had not been accepted, so 10 November produced one member's work
  instead of four. Avoidable: the invites should have gone out at Sprint 0
  planning on 9 November.

- **Identity drift on commits, four times.** `git config user.email` persists
  between checkouts, so several commits were initially authored by the wrong
  member and had to be corrected. The fix now in use is to set name and email
  explicitly at the top of every member's command block.

- **Two commits landed on `main` that belonged on a branch** — US11's commit 1
  and later its commit 2 — because a `git checkout` failed while the commands
  chained after it ran anyway. Both were recovered locally before any push.
  The habit now is to run `git checkout` on its own line and confirm with
  `git rev-parse --abbrev-ref HEAD` before committing.

- **A wrong claim reached the README.** The Known limitations section stated
  that `tab_width` was "configurable, defaulting to 4". It is neither — it is a
  required parameter of `count_leading_spaces`, and `Thresholds` does not carry
  it. Corrected the same day, and the correction is recorded in the scrum log
  rather than silently applied.

## 3. What we learned from the measurement

### 3.1 The hours-per-point rate is wrong by 70%, and the reason is not what we first thought

**CPI 1.70, SPI 1.00** (projected at close). Delivered exactly what was
committed, on time, in 40% fewer hours than budgeted. That is an estimate that
was too generous, not fast work.

The first reading, after five stories, was that the cost is mostly **fixed
overhead per story** — `hours = 3.0 + 0.5 × points` fitted the group means
closely. With all twelve stories the fit changes materially:

```
  3-point stories   mean 4.2 h   (5 stories: 5.0, 5.0, 5.0, 3.5, 2.5)
  5-point stories   mean 5.7 h   (5 stories: 6.0, 6.0, 6.0, 6.0, 4.5)
  8-point stories   mean 8.25 h  (2 stories: 7.0, 9.5)

  refitted:  hours = 1.8 + 0.81 x points
```

The fixed term halved and the slope rose by 60%, on the strength of one
additional 8-point story. **The model was less stable than it looked**, which is
itself worth recording: a two-parameter fit to eleven points, grouped three
ways, is not a finding to rely on.

### 3.2 The real driver is how much of the design was already settled

The spread *within* a single point value is wider than the spread between point
values, and it is explained by novelty rather than size:

| Story | Pts | Hours | h/point | Why |
|---|---|---|---|---|
| **US20** `rule_nesting` | 3 | **2.5** | 0.83 | near-copy of US19; the design was already decided |
| US19 `rule_complexity` | 5 | 4.5 | 0.90 | `classify_severity` did the banding; the rule is nine lines |
| US11 `cyclomatic_complexity` | 8 | 7.0 | 0.88 | largest story closed, lowest h/point |
| US01 `classify_line` | 3 | 5.0 | 1.67 | first story; established the whole pattern |
| US02 `count_leading_spaces` | 3 | 5.0 | 1.67 | first loop; needed bounded unrolling worked out |
| **US29** `score_from_issues` | 8 | **9.5** | 1.19 | cap and floor interact; the only subtle spec in the sprint |

US20 cost **a third** of what US02 cost, for the same three points. Not because
it was simpler as a function, but because US19 had already settled the rule
shape, the delegation to `classify_severity`, the code constant and the message
format. US29 was expensive for the opposite reason — nothing preceded it, and
the cap-before-floor ordering had to be reasoned out.

**This is what the planning poker converged on.** Round 1 spread 280 points
across the backlog with only US01 unanimous; round 2 brought it to 196. All four
of the largest disagreements — US36 at 8 vs 21, and US16, US25 and US29 all at 5
vs 13 — resolved on the same question: *how much can this story reuse?* The
actual hours say that question was the right one, and that **the point values
still do not fully capture its answer**, because points were agreed per story
while reuse depends on what has merged before it.

### 3.3 The burndown is a staircase, and daily variance means little at this size

Stories are worth 3, 5 or 8 points and the 0/100 rule pays nothing until merge,
so the actual line cannot track a 5.6-points-per-day ideal. It held flat for
three days and then fell 18 points in one afternoon (11 November) and 16 in
another (17 November).

Of seven days with a gap, **one was a real failure** — the lost Friday. Two were
structural: nothing can close on day 0 or day 1. One was the rework day. The
rest were the 0/100 rule timing. **The trend across the sprint is the only
reading worth taking**; the daily figure mostly measures whether a batch of pull
requests happened to land that afternoon.

### 3.4 Three estimation models disagree by a factor of four, and the EVM baseline is the outlier

| Model | Project total | Source |
|---|---|---|
| EVM baseline, 2 h/point | **392 h** | Sprint 1 planning, from one reference story |
| Observed flat rate, 1.18 h/point | 231 h | 66.0 / 56 across twelve stories |
| Refitted fixed + variable | 223 h | `36 × 1.8 + 196 × 0.81` |
| Independent forward estimate | 243.5 h | a pass over all 36 stories |
| COCOMO I Basic | 996 h | `docs/measurement/cocomo.md` |
| COCOMO II Early Design | 1598 h | `docs/measurement/cocomo.md` |

The three bottom-up routes agree within 10% of each other, at 223–244 hours. The
EVM baseline is 60% above all of them, and the two COCOMO figures are 4× and 7×
above. COCOMO is calibrated on industrial projects with requirements,
integration and deployment phases that this project does not have, so the
disagreement there is expected and is discussed in `cocomo.md`. **The 392 is the
figure that needs a decision.**

### 3.5 The remaining sprints need more hours than the team has

`cocomo.md` records the team's available capacity: **192 person-hours** across the
whole project window, from four members at roughly 8 hours each per week over six
weeks. That figure was written to explain why COCOMO over-estimates. Put next to
Sprint 1's actual hours it says something sharper.

At the observed **1.18 h/point**:

| Sprint | Points | Hours implied | Available at 8 h/person/week | Hours per person per week needed |
|---|---|---|---|---|
| 1 | 56 | **66.0 actual** | 64 | **8.3** |
| 2 | 63 | 74.3 | 64 | 9.3 |
| 3 | 77 | 90.9 | 64 | **11.4** |
| **Total** | **196** | **231** | **192** | |

**Sprint 1 landed exactly on the 8-hour assumption** — 66 hours against 64
available, which is as close to a validated planning figure as this project has
produced. That is the good news, and it means the 1.18 h/point rate can be
trusted for forecasting.

It also means **Sprint 3 requires 42% more hours per person per week than Sprint
1 actually took**, in the two weeks ending 20 December. The total overruns
available capacity by about 39 hours, or 20%.

This is the same concern as the velocity figure in the review, but stated in the
unit that matters. Velocity says Sprint 3 is a 38% stretch on points; this says
it is 11.4 hours per person per week in the week before Christmas. The second is
the one to plan against.

**The sprint totals were not set by capacity.** They came out of the planning
poker round 2 values falling where they fell once the per-member balance was
fixed — 56 / 63 / 77, rising 38% across the project. Nobody checked that against
hours available, because until Sprint 1 closed there was no rate to check it
with. There is now.

Three responses, for the meeting:

- **Move COULD-priority stories out of Sprint 3 into the hardening week**
  (21–27 December), which is currently reserved for polish and has no story
  commitments.
- **Rebalance Sprint 2 and Sprint 3** so the two carry similar loads — roughly
  70 points each rather than 63 and 77.
- **Accept the stretch and plan the hours explicitly**, which means agreeing now
  who is available over the Christmas week rather than discovering it on 15
  December.

Doing nothing is the fourth option and the worst one, because the figure is now
known.

### 3.6 Symbolic execution found one defect and two configuration hazards

None of these would have been found by testing. All tests pass; coverage is
100%.

1. **`rule_complexity` can never emit INFO** — `actual > limit and actual <= limit`
   is unsatisfiable. A quarter of the severity scale is unreachable through any
   rule.
2. **At a limit of 1, MINOR and MAJOR are unreachable** — integer collapse in
   the banding arithmetic.
3. Composing 1 and 2: **at a limit of 1, every finding is CRITICAL** — and
   **`Thresholds.validate` permits 1.** This is an open defect, not a documented
   design decision.

`max_nesting_depth` also has three path conditions with a *unique* solution
rather than an interval, reachable only at a depth of exactly 0 — which the
random tests, sampling 0..20, would hit roughly once in twenty-one lists.

## 4. Action for Sprint 2

One change, owned by a named member, checked at the next retrospective.

| Action | Owner | How we will know it worked |
|---|---|---|
| **At Sprint 2 planning, name for each story the merged function it most resembles, and let that inform the estimate.** Points are currently agreed per story in isolation; section 3.2 shows reuse is the dominant cost driver and that the point values do not capture it. | **Gunjan** (runs planning) | At the Sprint 2 retrospective, compare the hours-per-point *spread within each point value* against Sprint 1's. Sprint 1's three-point stories ranged 2.5 to 5.0 hours — a factor of two. If naming the precedent narrows that spread, the action worked. |

**Why this one and not the other two candidates.** Sending collaborator invites
before day 1, and making every Definition of Done line checkable by a command,
are both worth doing and both already done — the invites are no longer an issue
and the DoD was amended on 12 November. Neither is a change to how the team
works from here. The estimation action is the only candidate that responds to a
measured finding rather than to an operational slip, and it is the only one that
can be checked with a number at the next retrospective.

## 5. Decisions taken at this meeting

### 5.1 The EVM baseline — **held at 392 hours, not re-cut**

CPI is 1.70 and the 2 h/point rate is wrong by roughly 70%. The baseline is
**deliberately not changed.**

| | Re-baseline to ~1.2 h/point | **Hold the baseline** |
|---|---|---|
| BAC | 235 h | **392 h** |
| CPI | ~1.03 | **1.70** |
| Comparability across sprints | lost | **kept** |
| Documents to edit | 4 files, ~60 figures | **none** |
| What the forecast says | 228 h | **EAC 231 h** |

Three reasons, recorded because the decision looks like inaction and is not:

1. **A baseline is frozen by definition.** Re-cutting it mid-project means
   Sprint 1 is measured against one baseline and Sprint 2 against another, and
   the variance between sprints — the thing being measured — stops meaning
   anything. `evm.md` section 3 already states the baseline is not re-baselined.
2. **`EAC = BAC / CPI` already applies the correction**, giving 231 hours
   without a figure being edited. That is what the forecast formula is for.
3. **A CPI of 1.70 with an explanation is worth more than a CPI of 1.03 with
   none.** A baseline quietly adjusted until the index reads 1.00 is the absence
   of a decision rather than the presence of one.

**Adopted for forward planning only:** 1.2 hours per story point, for Sprints 2
and 3. It sits between the observed 1.18 and the independent forward estimate's
1.24. The underlying cause is reuse, per section 3.2, so the rate will still
mis-estimate individual stories even where it gets a sprint total close.

### 5.2 `Thresholds.validate` permits a limit of 1 — **tighten it**

**Decision: reject values below 2. Owner Saaket. Sprint 2.**

The analysis chain is in section 3.6 and in the sprint review: at a limit of 1,
MINOR and MAJOR are unsatisfiable, no rule can emit INFO, so every finding is
CRITICAL — and the validator permits exactly that value.

Why tighten rather than warn and allow:

- There is **no CLI yet** to display a warning in. The menu is a Sprint 3 story,
  so "permit and warn" means permit and say nothing until December.
- Nothing is lost. A limit of 1 produces a tool that reports everything as
  critical and nothing as minor. No user wants that configuration; it is
  reachable only by accident.
- It is a one-character change, and `tests/test_model.py` gains a case asserting
  1 is now rejected. **The reason goes in the commit message, not only in the
  diff** — the change is trivial and its justification is three pages of path
  conditions, and a future reader finding `if value < 2` with no explanation
  would reasonably assume it was arbitrary.

Sprint 2 rather than immediately, because `model/thresholds.py` belongs to no
user story and the change needs to be attributable. Saaket owns it because his
US19 and US26 analyses produced the finding.

**It does not become a user story.** It is a defect fix, logged here, and the
points are not counted toward velocity.

### 5.3 Capacity — **no stories moved; a trigger set instead**

Section 3.5 shows the project needs about **231 hours against 192 available**,
and that Sprint 3 as committed needs **11.4 hours per person per week** in the
fortnight ending 20 December, against the 8.3 Sprint 1 actually took.

Three options were considered: move COULD stories from Sprint 3 into the
hardening week, rebalance Sprint 2 and Sprint 3 to roughly 70 points each, or
accept the stretch and agree availability now.

**Decision: change nothing yet, and set a measurable trigger.**

> **At the Sprint 2 review on 6 December**, compare Sprint 2's actual hours
> against **80**, which is 68 points at the adopted 1.2 h/point rate.
>
> - **At or under 80 hours** with all 63 points delivered: the team is
>   sustaining roughly 10 hours per person per week, Sprint 3 stands as
>   committed, and the capacity figure of 8 h/person/week in `cocomo.md` is
>   revised upward to match observed reality.
> - **Over 80 hours, or points carried over**: move the COULD-priority stories
>   out of Sprint 3 into the hardening week (21–27 December), which currently
>   holds no story commitments.

Reasons for deferring rather than acting now:

- **Rebalancing does not reduce the total.** Moving points between Sprints 2 and
  3 flattens the profile but leaves 231 hours against 192. It would also re-cut
  the Sprint 2 and Sprint 3 PV milestones, days after deciding in 5.1 to hold
  the baseline.
- **The 192-hour figure is an assumption, not a measurement.** It comes from "8
  hours each per week" written in `cocomo.md` to explain why COCOMO
  over-estimates. Sprint 1 ran at 8.3. Whether the team can sustain 10 is
  unknown, and Sprint 2 is the experiment that answers it.
- **Cutting scope on an untested assumption is the expensive mistake.** Removing
  stories now and finding in December that capacity was there would have cost
  marks for no reason.

The risk accepted is that the decision point is 6 December, leaving two weeks to
act. That is enough to move COULD stories out of Sprint 3 but not enough to
restructure it, and that limit is recorded deliberately.

## 6. Previous sprint's action

| Action from Sprint 0 | Did it work? | Evidence |
|---|---|---|
| None was recorded | — | Sprint 0 produced the design, backlog and estimates; it held no retrospective, so there is nothing to check back against. **This is the first retrospective, and section 4's action is the first to be carried forward.** |

## 7. Definition of Done

Did every story merged this sprint actually meet it?

**No — four did not, and it was caught and fixed inside the sprint.** US01,
US10, US26 and US28 merged on 11 November with only equivalence-partitioning
black-box tests. The brief requires two black-box strategies, and the DoD at the
time said only "black-box test cases".

**The Definition of Done was wrong, not ignored.** Every member satisfied it as
written. It was amended in `cdfc8e7` on 12 November to name both
`equivalence_partitioning` and `random_testing` explicitly, and the four stories
were brought up to it the same day.

The eight stories merged after the amendment all carry both packages. The lesson
is in section 4: a DoD line naming a path is checkable, and one naming a concept
is not.
