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
