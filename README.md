# CodeGauge

A static code review tool for Python that measures complexity, flags quality issues and
scores source files.

CO7095 Software Measurement and Quality Assurance, 2026-27 Semester 1 — group assignment,
project **#17, Software Code Review Tool**.

> **This README grows with the project.** Each phase adds a section; the
> [update schedule](#readme-update-schedule) at the bottom says what to add when. Keep it
> current — it is the first thing the marker reads, and the brief requires a detailed
> README for the code marks.

---

## Status

| Phase | Dates | State |
|---|---|---|
| Sprint 0 — design and planning | 4–7 Nov 2026 | **complete** |
   Sprint 1 | 9–22 Nov 2026 | **in progress** |
| Sprint 2 | 23 Nov–6 Dec 2026 | not started |
| Sprint 3 | 7–20 Dec 2026 | not started |
| Hardening | 21–27 Dec 2026 | not started |
| Report, video, packaging | 28 Dec–3 Jan 2027 | not started |
| Submitted | 4 Jan 2027 | not started |

**User stories:** 0 of 36 done · 0 of 186 story points · Sprint 1 backlog: 12 stories, 56 points
**Tests:** 6 passing · **Coverage:** data model only

<!-- PHASE: update this table and these two lines at every sprint review. -->

## What it does

CodeGauge reviews Python source files without running them. It reduces each function to a
set of measurements — length, parameters, nesting depth, decision points, duplication —
then applies configurable quality rules, grades each finding by how far past its limit it
has gone, and reports a quality score out of 100 with a letter grade. Reviews are kept in a
history file so a file's quality can be tracked over time.

Backend only, by design: a text menu is the entire front end and the history lives in a
serialised text file. **No GUI, no database, no third-party runtime dependencies, and no
use of the `ast` module** — analysis is line-based, using only techniques taught in the
module.

## Team

| Member | Student number | Username | GitHub | Slice | Stories | Points |
|---|---|---|---|---|---|---|
| Gunjan | 259059915 | `gsk17` | `gsk17` | scanning and line metrics | US01–US04, US06–US09, US36 | 46 |
| Kasam | 259059933 | `khm12` | `kasam-leicester` | complexity metrics | US10, US12–US18, US20 | 50 |
| Saaket | 269046020 | `ssl21` | `saaket-ssl` | rule engine and severity | US11, US19, US21–US27 | 45 |
| Harshita | 269035432 | `hcg22` | `guduru0112` | scoring, history and persistence | US05, US28–US35 | 45 |

Each member owns a vertical slice, because the testing and research marks are assessed
individually. The story numbers are not contiguous: after planning poker the per-member
totals were 36/55/40/55, a 19-point spread, so two same-sprint swaps were made to bring
them within 5 of each other — US05 ↔ US36 and US20 ↔ US11. Ownership is therefore per
function, not per module.

**Repository:** https://github.com/gsk17/CodeGauge-SoftwareCodeReviewTool
**Collaborators:** `<add the Professor's and every TA's GitHub ID>`

<!-- PHASE 1: fill in usernames, GitHub handles, the repository URL and the collaborators. -->

## Requirements

- Python 3.9 or newer (developed on 3.11). Standard library only at runtime.
- PyCharm — the project is developed and marked in PyCharm.
- For the tests: `python -m pip install --user pytest coverage`

## Running it

```bash
python main.py
```

Right now this prints the banner only; the menu is wired in by the CLI story in Sprint 3.

## Running the tests

```bash
python -m pytest -v
python -m coverage run -m pytest && python -m coverage report -m
```

<!-- PHASE 1: add the per-technique commands once the test packages exist:
       python -m pytest <username>/test/blackbox/<technique> -v
     PHASE 5: add one line per member per technique, which the brief requires. -->

## Layout

```
main.py                 entry point
model/                  FunctionRecord, Issue, ReviewReport, Thresholds
cli/                    text menu and report formatter       (Sprint 3)
core/                   scanner, metrics, rules, scoring     (Sprints 1-3)
tests/                  shared tests for the data model
gsk17/test/             Gunjan - black-box and white-box test packages
khm12/test/             Kasam
ssl21/test/             Saaket
hcg22/test/             Harshita
docs/                   design, Scrum, measurement, CMMI, symbolic, report
```

<!-- PHASE: extend as modules land. The final version lists every module with its owner. -->

## Documentation

| Document | Contents |
|---|---|
| [docs/design/](docs/design/) | design specification: goals, approaches considered, architecture |
| [docs/scrum/](docs/scrum/) | product backlog, sprint backlogs, Definition of Done, sprint notes |
| [docs/measurement/](docs/measurement/) | PERT and critical path, COCOMO I and II, EVM, burndown, velocity, planning poker |
| [docs/cmmi/level2-audit.md](docs/cmmi/level2-audit.md) | CMMI Level 2 audit and configuration management |
| [docs/symbolic/](docs/symbolic/) | symbolic execution and concolic testing analyses |

## Process

Three two-week Scrum sprints, 9 November to 20 December 2026. Sprint 0 produced the design,
the backlog and the estimates — see [sprint-0-notes.md](docs/scrum/sprint-0-notes.md), which
also records the throwaway prototype that was built to size the work and then discarded,
and why.

One branch per user story, `feature/<username>-us<NN>-<slug>`, merged by reviewed pull
request and **never deleted** — the brief requires branches as development evidence.

---

## README update schedule

What to add, and when. Tick as you go.

- [ ] **Phase 1 (lab session)** — the four usernames and GitHub handles, the repository
      URL, the collaborators added, and the per-technique test commands now that the
      packages exist.
- [ ] **Each sprint review** — the status table, the story and point counts, the test
      count and the coverage figure.
- [ ] **Sprint 3** — the real menu options and the sample files, once the CLI story lands;
      replace the "prints the banner only" note.
- [ ] **Phase 4 (hardening)** — the final coverage figure, and a **Known limitations**
      section. The line-based design has real approximations: a `def` inside a string
      literal, comprehension counting, triple-quoted blocks read as documentation, tabs
      read as four spaces rather than eight, and the severity bands collapsing at a
      threshold of 1. Documenting them is a quality-assurance practice and reads far
      better than leaving them to be discovered.
- [ ] **Phase 5 (packaging)** — the full uncompress / PyCharm-import / run instructions for
      a Percy Gee lab machine, and one test command per member per technique. **The brief
      says a submission the graders cannot open and run, with a proper and comprehensive
      README, scores zero** — so this section is not optional.

