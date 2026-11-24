# Meeting Notes

Minutes of the Scrum events that produce a decision: sprint planning, sprint
reviews and sprint retrospectives. The fifteen-minute daily stand-ups are
recorded separately in [daily-scrum-log.md](daily-scrum-log.md).

Each entry records **what was discussed, what was decided, and who owns it** —
not a transcript. A decision with no owner and no check date is not a decision,
so every outcome below carries both.

---

## Sprint 2 planning — Monday 23 November 2026

**Present:** Gunjan, Kasam, Saaket, Harshita
**Chaired by:** Gunjan
**Duration:** ~30 minutes
**Output:** Sprint 2 backlog confirmed unchanged

### 1. Confirm the backlog

[sprint-2-backlog.md](sprint-2-backlog.md) was drafted at Sprint 0 and committed
on 11 November in `32ff60c`. The session read it through rather than re-planned
it: **63 story points across 12 stories, three per member.**

| Member | Stories | Points |
|---|---|---|
| Gunjan | US03, US04, US08 | 11 |
| Kasam | US13, US14, US17 | 18 |
| Saaket | US21, US22, US23 | 13 |
| Harshita | US31, US33, US34 | 21 |

Agreed unchanged.

### 2. The sprint goal

> The rule set is complete and a review can be written to and read back from the
> history file.

Two new modules appear this sprint — `core/line_metrics.py` (Gunjan, from US04)
and `core/history.py` (Harshita, from US31). Both are created by the first story
that needs them, in that story's implementation commit, the same way Saaket
created `core/rules.py` with US19.

### 3. Dependencies identified

**US34 `parse_record_line` reads back what US33 `serialise_report` writes.** US33
is scheduled first. Both are Harshita's, so the ordering is hers to hold rather
than a cross-member sequencing problem.

No other cross-member dependency this sprint. Sprint 1 had three — US28 on
US26, US11 inside Kasam's module, US20 on US19 — and all three were sequenced
rather than blocked. Sprint 2 is easier in that respect because the rule engine
and the scoring module already exist.

### 4. The load is uneven, and is being left uneven

**Harshita carries 21 points; Gunjan carries 11.** That is the widest per-member
gap in the project.

Discussed and deliberately not changed. The stories sit inside each member's
vertical slice, and moving one crosses a boundary that the individual testing
and research marks depend on. Raising it here makes it a recorded decision
rather than an oversight, and it is flagged again in the 24 November stand-up so
that it is watched during the sprint.

### 5. Outcome

Backlog agreed with no edits. **Nothing was committed**, because confirming an
existing document produces no change to it.

> **Observation taken forward.** A meeting that changes nothing leaves no trace
> in the repository. From Sprint 3 planning onward the team commits a short
> confirmation note at planning even when the backlog is agreed unchanged, so
> that the session is evidenced rather than asserted. CMMI Project Planning
> expects the plan to be reviewed and agreed; a review with no artifact is hard
> to demonstrate.

---

## Sprint 1 review — Tuesday 24 November 2026

**Present:** Gunjan, Kasam, Saaket, Harshita
**Duration:** ~45 minutes
**Full record:** [sprint-1-review.md](sprint-1-review.md)

> Planned for Sunday 22 November and held on the Tuesday. The sprint itself
> finished on schedule — all 56 points merged on Friday 20 November — but the
> review and retrospective slipped over the weekend. Recorded rather than
> back-dated; the commit history shows the gap plainly.

### 1. The increment, demonstrated

Each member ran their own test packages in front of the team rather than
describing them:

```bash
python -m pytest gsk17/test -v        # and khm12, ssl21, hcg22
python -m coverage run -m pytest && python -m coverage report -m
```

**492 tests passing. 100% statement coverage of all five `core` modules.**
Twelve stories, twelve branches on the remote, none deleted, every one merged by
a reviewed pull request with a merge commit rather than a squash.

### 2. Was the sprint goal met?

> A file can be scanned into per-function records, its complexity measured, the
> first rules raised against it and a score produced — the thin end-to-end
> thread through every member's slice.

**Met in part, and the gap was discussed at length.**

Every *function* in the thread exists and is tested, one per layer: scan,
measure, rule, score. What does not exist is anything that **joins** them.
`scan_file` (US09) is a Sprint 3 story and there is no CLI until Sprint 3, so a
file cannot yet be passed in at one end and a grade read off the other.

That was the plan rather than a shortfall — US09 was placed in Sprint 3 at
Sprint 0 because it consumes every other scanner function. But the goal as
written says *"a file can be scanned"*, which overstates what a sprint of single
functions can deliver.

**Raised at this review:** Sprint 2's goal has the same defect. *"A review can be
written to and read back from the history file"* implies an end-to-end path that
will not exist at the end of Sprint 2 either, because nothing assembles a
`ReviewReport` until Sprint 3. **Sprint goals from Sprint 3 onward are to be
phrased in terms of functions delivered, not end-to-end behaviour.**

### 3. Measurement

| Measure | Value |
|---|---|
| Committed / completed points | 56 / **56** |
| Velocity | **56** |
| Carried over | **0** |
| PV / EV / AC | 112 h / 112 h / **66.0 h** |
| CV / SV | **+46.0 h** / **0.0 h** |
| **CPI / SPI** | **1.70** / **1.00** |
| EAC / TCPI | 231 h / 0.859 |

**The pair of indices was the main discussion.** SPI of exactly 1.00 with a CPI
of 1.70 has one reading: the schedule was met, so capacity was not the
constraint, and the hours came in 40% under, so **the rate was wrong**. It is
not evidence that the team is fast.

An SPI of exactly 1.00 was also noted as something not to over-read. It is 1.00
because every committed story closed, not because work tracked the plan day by
day — the burndown was 4.4 points behind on 13 November and 8.4 ahead on the
17th, and an index measured at a sprint boundary cannot see either.

### 4. Defect raised

**`Thresholds.validate` permits a limit of 1**, which is the configuration at
which three of the four severity bands become unreachable.

The chain, all derived rather than observed:

1. Symbolic execution of `classify_severity` (US26): at a limit of 1, MINOR
   requires `actual <= 1` which INFO has taken, and MAJOR requires
   `actual > 1 and actual < 2` which has no integer solution. **Both
   unsatisfiable.**
2. Inter-procedural analysis of `rule_complexity` (US19): every rule returns
   `None` when the measurement is within its limit, which is exactly the INFO
   condition. **No rule can emit INFO.**
3. Composed: **at a limit of 1 every finding is CRITICAL.**
4. `Thresholds.validate` rejects 0 and below. It permits 1.

**Every test passes. Coverage of `core/` is 100%.** No black-box test would find
this — each function is correct in isolation. It took reasoning about path
conditions across two members' modules to reach a line of validation code in a
third file that no story owns.

Decision deferred to the retrospective; recorded there as 5.2.

### 5. An observation the numbers nearly hide

`model/thresholds.py` line 43 is the **only** statement in `core/` or `model/`
with no test exercising it — and it sits inside `Thresholds.validate`, the
function carrying the defect above.

Untested code and a latent defect in the same three lines is the correlation
quality assurance exists to predict. Noted deliberately rather than left for a
reader to find the 99% sitting beside the 100%.

### 6. Closed out

- `v0.1.0` tagged on `722c822`, the sprint close commit
- Board screenshot taken with all twelve stories in Done
- The four planning-poker corrections applied first — **US14 → 5, US15 → 8,
  US24 → 5, US31 → 8** — so the board, the product backlog and
  `planning-poker.md` agree

---

## Sprint 1 retrospective — Tuesday 24 November 2026

**Present:** Gunjan, Kasam, Saaket, Harshita
**Duration:** ~45 minutes
**Full record:** [sprint-1-retrospective.md](sprint-1-retrospective.md)

### 1. What went well

- **Dependencies were sequenced, not hit.** Three stories needed another
  member's merge first. All three were identified at planning and ordered
  around; none became a block.
- **Per-function ownership worked.** `core/complexity.py` is Kasam's module and
  holds Saaket's `cyclomatic_complexity`; `core/rules.py` is Saaket's and holds
  Kasam's `rule_nesting`. Agreed at stand-up before the work in both cases.
- **The review rotation held for every story.** Every member both gave and
  received exactly one review.
- **The lost day was recorded rather than hidden**, with the recovery decision
  written next to it.

### 2. What did not go well

- **A full working day lost to rework from a vague Definition of Done.** The DoD
  said "black-box test cases" without naming both required strategies, and four
  stories merged on 11 November with only equivalence partitioning. Caught the
  next day; fixing it consumed that day and earned zero story points. **The most
  expensive process defect of the sprint, and the cause was a document not
  specific enough to be checkable.**
- **Friday 13 November: no work on any branch.** Recovery cost an unplanned
  Sunday session.
- **Three of four members had no repository access on day 1.** Avoidable; the
  invites should have gone out at Sprint 0 planning.
- **Identity drift on commits, four times.** `git config user.email` persists
  between checkouts.
- **Two commits landed on `main` that belonged on a branch**, because a
  `git checkout` failed while the commands chained after it ran anyway. Both
  recovered locally before any push.

### 3. What the measurement told us

**The 2 h/point rate is wrong by roughly 70% — and the reason is not what we
first thought.**

After five stories the data looked like fixed overhead per story. After twelve,
the fit changed materially on the strength of one additional 8-point story,
which is itself worth recording: a two-parameter fit to eleven points is not a
finding to rely on.

**The real driver is how much of the design was already settled:**

| Story | Points | Hours | h/point | Why |
|---|---|---|---|---|
| US20 `rule_nesting` | 3 | **2.5** | 0.83 | near-copy of US19 |
| US19 `rule_complexity` | 5 | 4.5 | 0.90 | `classify_severity` did the banding |
| US02 `count_leading_spaces` | 3 | **5.0** | 1.67 | first loop; needed bounded unrolling |
| US29 `score_from_issues` | 8 | **9.5** | 1.19 | nothing preceded it |

**US20 cost a third of what US02 cost, for the same three points.** Not because
the function was simpler, but because US19 had already settled the rule shape,
the delegation, the code constant and the message format.

**This is what planning poker converged on.** Round 1 spread 280 points with only
US01 unanimous; round 2 brought it to 196. All four of the largest disagreements
resolved on the same question: *how much can this story reuse?* The hours say
that question was right, and that **the point values still do not capture its
answer**, because points were agreed per story while reuse depends on what has
merged before it.

### 4. The three decisions

#### 4.1 Hold the EVM baseline at 392 hours

| | Re-baseline to ~1.2 h/point | **Hold** |
|---|---|---|
| BAC | 235 h | **392 h** |
| CPI | ~1.03 | **1.70** |
| Cross-sprint comparability | lost | **kept** |
| Documents to edit | 4 files, ~60 figures | **none** |
| Forecast | 228 h | **EAC 231 h** |

Three reasons, recorded because the decision can look like inaction:

1. A baseline is **frozen by definition**. Re-cut it and Sprint 1 is measured
   against one baseline and Sprint 2 against another, so the variance between
   sprints — the thing being measured — stops meaning anything.
2. **`EAC = BAC / CPI` already applies the correction**, giving 231 hours with
   nothing edited. That is what the forecast formula is for.
3. **A CPI of 1.70 with an explanation is worth more than 1.03 with none.** A
   baseline quietly adjusted until the index reads 1.00 is the absence of a
   decision.

**Adopted for forward planning only: 1.2 h/point**, between the observed 1.18
and the independent forward estimate's 1.24.

#### 4.2 Tighten `Thresholds.validate` to reject limits below 2

**Owner: Saaket. During Sprint 2, after US22 merges.**

Considered and rejected: permit 1 and warn. **There is no CLI yet to warn in** —
the menu is a Sprint 3 story — so "warn" means say nothing until December.
Nothing is lost by forbidding a configuration that produces a tool reporting
everything as critical and nothing as minor.

`tests/test_model.py` gains a case asserting 1 is now rejected, which also
closes the one uncovered line noted at the review. **The reasoning goes in the
commit message, not only the diff**: the change is one character and its
justification is three pages of path conditions.

It is a defect fix, not a user story. **Its points do not count toward
velocity.**

#### 4.3 Capacity — nothing moved, a measurable trigger set

The project needs about **231 hours against 192 assumed available**, and Sprint 3
as committed needs **11.4 hours per person per week** in the fortnight ending 20
December, against the 8.3 Sprint 1 actually took.

> **At the Sprint 2 review on 6 December**, compare Sprint 2's actual hours
> against **80** (68 points at 1.2 h/point).
>
> - **At or under 80**, with all 63 points delivered: Sprint 3 stands, and the
>   8 h/person/week assumption in `cocomo.md` is revised upward to match
>   observed reality.
> - **Over 80, or points carried over**: the COULD-priority stories come out of
>   Sprint 3 into the hardening week of 21–27 December, which holds no story
>   commitments.

Rejected, with reasons:

- **Rebalancing Sprints 2 and 3** flattens the profile but leaves 231 against
  192 unchanged, and would re-cut the PV milestones minutes after deciding to
  hold the baseline.
- **Cutting scope now** acts on an untested assumption. The 192-hour figure was
  written in `cocomo.md` to explain why COCOMO over-estimates, not measured.
  Sprint 1 ran at 8.3; whether 10 is sustainable is exactly what Sprint 2
  answers.

**Risk accepted and recorded:** the decision point is 6 December, leaving two
weeks. That is enough to move COULD stories out of Sprint 3, not enough to
restructure it.

### 5. The one action for Sprint 2

| Action | Owner | Check |
|---|---|---|
| At planning, name for each story the **merged function it most resembles**, and let that inform the estimate | **Gunjan** | At the Sprint 2 retrospective, compare the h/point spread *within* each point value against Sprint 1's, where the three-point stories ranged 2.5 to 5.0 hours — a factor of two |

Two other candidates were considered and dropped: sending collaborator invites
before day 1, and making every DoD line checkable by a command. Both are worth
doing and **both are already done**. Neither changes how the team works from
here. The estimation action is the only candidate responding to a measured
finding rather than an operational slip, and the only one checkable with a
number.

**Applied immediately** at the 24 November stand-up rather than held for the next
planning session, so that December's comparison is against a prediction rather
than a memory.

### 6. Previous sprint's action

None. Sprint 0 produced the design, backlog and estimates but held no
retrospective, so there is nothing to check back against. **This is the first
retrospective and section 5's action is the first to be carried forward.**

### 7. Definition of Done — was it met?

**No. Four stories did not meet it, and it was caught and fixed inside the
sprint.**

US01, US10, US26 and US28 merged on 11 November with only
equivalence-partitioning black-box tests. The brief requires two strategies; the
DoD at the time said only "black-box test cases".

**The Definition of Done was wrong, not ignored.** Every member satisfied it as
written. It was amended in `cdfc8e7` on 12 November to name both
`equivalence_partitioning` and `random_testing` explicitly, and the four stories
were brought up to it the same day. All eight stories merged afterwards carry
both packages.

The lesson is section 5's: **a DoD line naming a path is checkable; one naming a
concept is not.**
