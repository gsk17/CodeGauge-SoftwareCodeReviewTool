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
