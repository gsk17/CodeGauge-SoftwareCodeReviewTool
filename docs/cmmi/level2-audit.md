# CMMI Level 2 (Managed) Documentation Audit

Project: CodeGauge - CO7095 project #17, Software Code Review Tool
Audit owner: `<member>` — complete the Evidence column as the project runs, not at the end.

CMMI Level 2 means the process is **managed**: work is planned, performed, measured and
controlled at the project level, and the practices are institutionalised rather than
heroic. The six process areas taught in the module are audited below. For each, the specific
practice is stated, what the team did, and the artifact that proves it.

**An unevidenced claim scores nothing.** Every row needs a commit SHA, an issue number, a
file path or a screenshot path. Where a row is not yet true, leave it blank rather than
claiming it — a partially complete audit with real evidence reads better than a complete one
with assertions.

---

## 1. REQM — Requirements Management

*Purpose: manage the requirements of the project's products and identify inconsistencies
between those requirements and the project's plans and work products.*

| Practice | What we did | Evidence |
|---|---|---|
| SP 1.1 Understand requirements | The assignment brief was read in full and decomposed into 36 fixed-size user stories, each naming a function, a module and an acceptance condition | `scripts/stories.tsv`; `docs/design/plans/2026-11-04-code-review-tool.md` §User story backlog |
| SP 1.2 Obtain commitment to requirements | Each story has a named assignee who accepted it at sprint planning and estimated it themselves in planning poker | GitHub issues US01–US36, assignee field; `docs/measurement/planning-poker.md` |
| SP 1.3 Manage requirements changes | Design decisions that changed a requirement are recorded as numbered rulings with their rationale and cost, rather than changed silently | project ledger, rulings 1–6; `docs/design/specs/2026-11-04-code-review-tool-design.md` §9 |
| SP 1.4 Maintain bidirectional traceability | Every story traces forward brief → story → function → test package → symbolic write-up, and backward from any function to the story that required it | `scripts/stories.tsv` (function and module columns); report §Software planning & design story table |
| SP 1.5 Ensure alignment between work and requirements | Each pull request is reviewed against its issue's definition of done before merge | PR review history on each `feature/*` branch |

**Known inconsistency identified and managed (evidence of the practice working):** the brief
names test packages after `your_student_user_id` with the example `jw333`, while the team
initially supplied 9-digit student numbers. A directory named `259059915` cannot be a Python
package, so the requirement was traced back, the inconsistency raised, and the layout fixed
to use university usernames. Recorded as ruling 4.

## 2. PP — Project Planning

*Purpose: establish and maintain plans that define project activities.*

| Practice | What we did | Evidence |
|---|---|---|
| SP 1.1 Estimate the scope | 36 user stories, 186 story points, decomposed from the brief | `docs/measurement/planning-poker.md` |
| SP 1.2 Establish estimates of work product and task attributes | LOC measured per module; story points per story | `docs/measurement/cocomo.md` §1 |
| SP 1.3 Define project lifecycle phases | Three 2-week sprints plus a setup phase and a hardening/reporting phase | `docs/design/plans/2026-11-04-code-review-tool.md` §Sprint calendar |
| SP 1.4 Estimate effort and cost | COCOMO I Basic and Intermediate and COCOMO II, with cost drivers and scale factors individually justified | `docs/measurement/cocomo.md` |
| SP 2.1 Establish the budget and schedule | PERT network with three-point estimates, forward and backward pass, slack and critical path; EVM baseline of 372 person-hours | `docs/measurement/pert.md`, `docs/measurement/evm.md` |
| SP 2.2 Identify project risks | Schedule risk quantified: the critical path needs 46 days against ~41 available, ~7% confidence, with three mitigations drawn from the slack table | `docs/measurement/pert.md` §6 |
| SP 2.3 Plan data management | Review history in a serialised text file; `reviews.dat` git-ignored as runtime data | `.gitignore`; `core/storage.py` |
| SP 2.4 Plan the project's resources | Four members, one vertical slice each, equal within 5 points (46/50/45/45) | `docs/measurement/planning-poker.md` §Balance check |
| SP 2.5 Plan needed knowledge and skills | Research component on symbolic execution and concolic testing scheduled as its own activity (J) with a worked example written up for the team to follow | `docs/symbolic/WORKED-EXAMPLE.md`; PERT activity J |
| SP 2.7 Establish the project plan | One implementation plan covering all 16 tasks, reviewed by the team before execution | `docs/design/plans/2026-11-04-code-review-tool.md` |
| SP 3.3 Obtain plan commitment | All four members reviewed and accepted the plan and their own slice before Sprint 1 | `<meeting note / sign-off, add here>` |

## 3. PMC — Project Monitoring and Control

*Purpose: provide understanding of project progress so corrective action can be taken when
performance deviates significantly from plan.*

| Practice | What we did | Evidence |
|---|---|---|
| SP 1.1 Monitor project planning parameters | Burndown updated daily; velocity per sprint; EVM row per sprint | `docs/measurement/burndown-and-velocity.md`, `docs/measurement/evm.md` |
| SP 1.2 Monitor commitments | Issue assignees and per-member point totals tracked against the 48-point target | `docs/measurement/burndown-and-velocity.md` §5 per-member table |
| SP 1.3 Monitor project risks | The schedule risk from PP SP 2.2 re-checked at each sprint review against actual velocity | sprint review notes |
| SP 1.6 Conduct progress reviews | Daily stand-up note on the active issue; sprint review at each sprint end | GitHub issue comments; board screenshots `docs/measurement/board-sprint<N>.png` |
| SP 1.7 Conduct milestone reviews | Sprint review and retrospective at the end of each of the three sprints | retrospective notes per sprint |
| SP 2.1 Analyse issues | CPI and SPI computed per sprint; a CPI below 1 with SPI near 1 diagnosed as underestimation rather than slow work | `docs/measurement/evm.md` §4 |
| SP 2.2 Take corrective action | `<record each one: what deviated, what was changed, when>` | |
| SP 2.3 Manage corrective action | `<record the outcome of each corrective action>` | |

## 4. CM — Configuration Management

*Purpose: establish and maintain the integrity of work products using configuration
identification, control, status accounting and audits.*

| Practice | What we did | Evidence |
|---|---|---|
| SP 1.1 Identify configuration items | CIs: the source modules under `core/`, `cli/`, `model/`; the test packages; the sample files; the measurement and CMMI documents; the plan and spec; `pytest.ini` and `.coveragerc`. Runtime data (`reviews.dat`) and build artifacts (`__pycache__`, `.coverage`) are explicitly **not** CIs | `.gitignore`; §CI register below |
| SP 1.2 Establish a configuration management system | Git with GitHub as the controlled repository; `main` holds only reviewed merges | repository history |
| SP 1.3 Create or release baselines | One semantic version tag per sprint: `v0.1.0` at Sprint 1 review, `v0.2.0` at Sprint 2, `v0.3.0` at Sprint 3, `v1.0.0` at submission | `git tag` output |
| SP 2.1 Track change requests | One GitHub issue per unit of change; no code enters `main` without an issue | GitHub issues US01–US36 |
| SP 2.2 Control configuration items | One branch per user story, `feature/<username>-us<NN>-<slug>`; merges only by pull request after review by another member; branches retained after merge as development evidence | branch list; PR history |
| SP 3.1 Establish configuration management records | Commit messages carry the story ID (`feat(US19): ...`); merge commits name the task | `git log --oneline` |
| SP 3.2 Perform configuration audits | At each sprint review: every closed issue has a branch, a PR, a review and a merge; the suite is green; coverage is at or above target | sprint review notes; coverage reports `docs/measurement/coverage-sprint<N>.md` |

### Configuration item register

| CI | Type | Owner | Baseline |
|---|---|---|---|
| `core/scanner.py`, `core/line_metrics.py` | source | M1 | v0.3.0 |
| `core/complexity.py` | source | M2 | v0.1.0 |
| `core/rules.py`, `core/severity.py` | source | M3 | v0.3.0 |
| `core/scoring.py`, `core/history.py`, `core/storage.py` | source | M4 | v0.3.0 |
| `cli/menu.py`, `cli/formatter.py`, `main.py` | source | group | v0.3.0 |
| `model/*.py` | source | group | v0.1.0 |
| `<username>/test/**` | test | each member | v0.3.0 |
| `samples/*.py` | test data | group | v0.3.0 |
| `docs/measurement/**`, `docs/cmmi/**`, `docs/symbolic/**` | document | group | v1.0.0 |
| `pytest.ini`, `.coveragerc`, `.gitignore` | configuration | group | v0.1.0 |

### Branching and merging strategy

```
main ──────●───────●───────●───────●──────────▶   only reviewed merges, tagged per sprint
            \     /         \     /
             ●───●           ●───●                 feature/<username>-us<NN>-<slug>
             one branch per user story, never deleted
```

Semantic versioning: `MAJOR.MINOR.PATCH` — MINOR for each sprint's delivered functionality,
PATCH for a defect fix within a sprint, MAJOR at submission.

## 5. MA — Measurement and Analysis

*Purpose: develop and sustain a measurement capability used to support management
information needs.*

| Practice | What we did | Evidence |
|---|---|---|
| SP 1.1 Establish measurement objectives | Four objectives: is the work balanced across members; are we on schedule; are we on budget; is the product adequately tested | this section |
| SP 1.2 Specify measures | Story points per member; velocity; burndown remaining; PV/EV/AC with CPI and SPI; statement coverage percentage; test pass rate; cyclomatic complexity per function | `docs/measurement/*` |
| SP 1.3 Specify data collection and storage procedures | Points from the GitHub issue point field; hours from issue comments; coverage from `coverage report -m`; complexity from the tool's own analysis of its own source | `docs/lab-setup-guide.md` §9 |
| SP 1.4 Specify analysis procedures | PERT formulas, COCOMO formulas and EVM formulas all stated next to their results, with one worked example each | `docs/measurement/pert.md` §3, `cocomo.md` §2–4, `evm.md` §4 |
| SP 2.1 Obtain measurement data | 97 test cases, 98% statement coverage, 100% pass rate at the Sprint 3 baseline | `coverage report -m` output |
| SP 2.2 Analyse measurement data | Coverage gaps identified line by line and either covered or recorded as infeasible with proof | `docs/symbolic/WORKED-EXAMPLE.md` §2.2 (the proven-infeasible branch) |
| SP 2.3 Store data and results | All measurement artifacts committed to the repository and versioned with the code | `docs/measurement/` |
| SP 2.4 Communicate results | Reported at each sprint review and in the report's measurement sections | sprint review notes |

**The tool measures itself.** Running the review tool over its own `core/` modules is a
measurement of the product by the product, and the figures are reported in the report's
implementation section.

## 6. PPQA — Process and Product Quality Assurance

*Purpose: provide staff and management with objective insight into processes and associated
work products.*

| Practice | What we did | Evidence |
|---|---|---|
| SP 1.1 Objectively evaluate processes | Sprint-end audit against the CM checklist: branch, PR, review, merge, green suite, coverage at target | sprint review notes |
| SP 1.2 Objectively evaluate work products | Every merge reviewed by a member who did not write the code; the whole branch independently reviewed before submission | PR review history; final review record |
| SP 2.1 Communicate and resolve noncompliance issues | Review findings recorded, graded and either fixed with a test that failed first, or recorded as an accepted deviation with the reason | PR review threads; project ledger |
| SP 2.2 Establish records | Test-first discipline: every function has tests that were observed failing before the implementation existed; deviations from that discipline recorded explicitly | project ledger; `git log` ordering of test and implementation commits |

**Noncompliance recorded against ourselves (evidence of the practice working):** the CLI and
formatter tests (Task 9) were written *after* their implementation rather than before,
because the pipeline had to be run against the sample files to discover their real output
before the assertions could be written. This departs from the team's test-first rule. It was
recorded in the ledger at the time rather than concealed, the one behavioural defect it
could have hidden (an empty file scoring 85 instead of 100) was found and fixed, and the
case was flagged to the independent reviewer. Recording a deviation is the practice; hiding
it would be the failure.

## 7. SAM — Supplier Agreement Management

**Not applicable.** The project acquires no products or services from suppliers. All code is
written by the four team members using the Python standard library and the module's taught
tools; `pytest` and `coverage` are development tools rather than supplied components, and
there is no runtime dependency on any third-party package. Recording a process area as not
applicable, with the reason, is itself a Level 2 practice — the alternative, inventing
supplier evidence, would be worse than omitting it.

---

## Audit summary

| Process area | Practices evidenced | Status |
|---|---|---|
| REQM | 5 / 5 | `<complete / in progress>` |
| PP | 11 / 11 | `<complete / in progress>` |
| PMC | 7 / 9 | corrective-action rows to be completed as they occur |
| CM | 7 / 7 | `<complete / in progress>` |
| MA | 8 / 8 | `<complete / in progress>` |
| PPQA | 4 / 4 | `<complete / in progress>` |
| SAM | n/a | not applicable, reason recorded |
