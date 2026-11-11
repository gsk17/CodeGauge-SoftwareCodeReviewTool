# Design: CO7095 Software Code Review Tool

**Date:** 2026-11-04
**Module:** CO7095 Software Measurement & Quality Assurance, 2026-27 SEM1
**Project topic:** #17, Software Code Review Tool (claimed; locked in)
**Team size:** 4 members
**Deadline:** 4 January 2027, 17:00 UK

---

## 1. Intent and the why

Build a backend Python application that reviews Python source files automatically and
reports their quality, and build it through a documented agile process, because the
assignment is graded on both the product and the process.

The tool is the vehicle; the marks are the goal. The rubric allocates:

| Category | Marks | Group / Individual |
|---|---|---|
| Sprint planning, CMMI, configuration management | 10 | Group (except story estimation + each member's CM) |
| Software development measurement (PERT, COCOMO, COCOMO II, EVM) | 20 | Group |
| Code snippet (readability, coverage of core functions, README, GitHub link) | 20 | Group for packaging; individual for code |
| Black-box and white-box testing and coverage | 20 | Individual |
| Research: symbolic execution and concolic testing | 20 | Individual |
| Video demonstration | 10 | Group |

**40 of the 100 marks depend on testing every function and performing symbolic and
concolic execution on every function.** That single fact drives the whole design below:
the code must be shaped so that its functions are easy to test exhaustively and easy to
analyse symbolically by hand.

---

## 2. Goals

1. A working, runnable command-line tool that analyses Python source files and produces a
   review report: metrics, issues with severities, and an overall quality score.
2. Code whose graded functions take **numeric inputs** and branch on them, so that:
   - cyclomatic complexity is genuinely high (good for the "sufficient complexity"
     requirement in the brief),
   - path conditions are linear integer constraints that can be drawn as a symbolic
     execution tree and solved by hand for the report,
   - black-box partitioning and white-box coverage are both straightforward.
3. At least 36 user stories (>= 9 per member), implemented across at least 3 sprints,
   with roughly equal total story points per member.
4. Every function covered by black-box tests, white-box tests and symbolic/concolic
   analysis, in packages named to the brief's convention.
5. Average test coverage >= 85%, and >= 85% of test cases passing.
6. The submitted zip opens in PyCharm on a Percy Gee lab machine with no errors, with a
   detailed README and a working public GitHub link.

## 3. Non-goals

- No GUI. A simple text menu is the entire frontend.
- No database. Persistence is a serialised text file.
- No automatic fixing or rewriting of the analysed code; the tool reports, it does not edit.
- No languages other than Python as analysis targets.
- No analysis of code by executing it; analysis is static only.
- No third-party libraries. Python standard library only.
- No `ast` module (see Approaches).

## 4. Anti-goals — things that would make this a failure even if it runs

- **Becoming a wrapper around pylint / flake8 / similar.** The brief forbids tools not
  introduced in the module, and a wrapper leaves almost no original code to test, which
  destroys the 40 testing/research marks.
- **Low-complexity code.** Functions with one or two branches make the white-box and
  symbolic-execution sections trivial and thin, and the brief explicitly asks for user
  stories whose functions have "multiple conditions and branches and having high
  cyclomatic complexity number".
- **Functions that take whole source strings as input.** Path conditions over arbitrary
  strings cannot be drawn as a clean symbolic execution tree. See the Approaches section.
- **Unequal workload.** Marks for testing, research and code are individual; a member with
  few or shallow functions loses their own marks.

## 5. Constraints

| Constraint | Source |
|---|---|
| Python only | Brief, "Programming Language" |
| PyCharm as the IDE; project must load on a lab machine | Brief + rubric |
| GitHub for project management (GitHub Project), commits, code review; Professor and all TAs added to the repo | Brief |
| At least 3 sprints, each 1-2 weeks | Brief + rubric |
| >= 9 user stories per member for a group of 4 | Brief |
| Every user story (issue) linked to a GitHub branch, branches not deleted after merge | Brief |
| Test packages named `<student_id>.test.blackbox.<technique>` and `<student_id>.test.whitebox.<technique>` | Brief, deliverable 5 |
| Symbolic test cases follow the same naming convention | Brief, deliverable 6 |
| Report <= 5000 words, fixed structure, academic integrity cover sheet signed by all four | Brief |
| Submission under 50MB, single submitter, Turnitin similarity < ~10% | Brief |
| Only techniques and tools taught in the module | Brief |

Taught material available to us (Lectures 1-5, confirmed from slides): CMMI maturity levels
and the six Level-2 process areas (REQM, PMC, PP, CM, MA, PPQA); agile principles; user
stories and MoSCoW; Scrum, planning poker with Fibonacci values 1/3/5/8/13/21 capped at
3 rounds, velocity, burndown charts; configuration management, configuration items,
semantic versioning, branching and merging; PERT with three-point estimates
`(O + 4M + P) / 6`, forward and backward pass, slack, critical path; COCOMO Basic
(organic / semi-detached / embedded), Intermediate with EAF, COCOMO II with effort
multipliers and scale factors PREC/FLEX/RESL/TEAM/PMAT; EVM with PV, AC, EV, CV, SV, CPI,
SPI, BAC, EAC; size and complexity metrics — LOC, Function Point Count (UFC x TCF), and
cyclomatic complexity `E - N + 2P` from a control flow graph.

Lectures 8-10 (black-box and white-box testing techniques) were not available when this
document was written. The specific technique names used in test package paths must be
confirmed against those lectures before Sprint 1 testing begins. This is flagged as an
open item, not a blocker — the architecture does not depend on it.

---

## 6. Approaches considered

### A. Shallow line scanner plus a numeric rule engine — **CHOSEN**

Parsing is deliberately crude and line-based. The scanner reads a `.py` file and reduces
each function it finds to a small record of **integers**: line count, parameter count,
maximum nesting depth, decision-point count, comment line count, blank line count, longest
line length, duplicated-block count. Everything downstream — the rules, the severity
classification, the scoring — is a function over those integers.

**Trade-offs.** Metrics are approximate rather than exact (a line-based scanner can be
fooled by multi-line expressions, strings containing `if`, and decorators). In exchange:
every graded function has numeric inputs, so symbolic execution trees are clean, path
conditions are linear integer constraints solvable by hand, black-box equivalence
partitioning is natural, and nothing outside taught material is used.

### B. Proper AST analyser using Python's `ast` module

Accurate metrics, real control flow graphs. Rejected because `ast` is not taught in the
module (the brief penalises tools and techniques not introduced in it), and because the
core functions would walk recursive tree objects — symbolic execution over recursive tree
traversal is very hard to present as a tree with hand-computed path conditions, and much
of the resulting code is untestable plumbing rather than branchy logic.

### C. Wrapper around an existing linter (pylint, flake8)

Rejected outright. Banned by the brief, and it leaves almost no original code to test,
forfeiting the marks that matter most.

**Decision: A.** Chosen by the team on 2026-11-04.

---

## 7. The design

### 7.1 Shape of the system

```
main.py                     entry point, launches the menu
cli/
  menu.py                   text menu loop, input handling
  formatter.py              turns a ReviewReport into printed text
core/
  scanner.py                file reading, function extraction (crude, line-based)
  metrics.py                numeric metric computation over FunctionRecord
  complexity.py             cyclomatic complexity, nesting depth, duplication
  rules.py                  rule functions: integers in, Issue out
  severity.py               severity classification and thresholds
  scoring.py                issue list -> score 0-100 -> grade band
  storage.py                save/load review history to a serialised text file
model/
  function_record.py        the integer record for one function
  issue.py                  code, severity, line number, message
  review_report.py          one file's complete review
samples/                    deliberately flawed .py files to analyse in the demo
reviews.dat                 serialised review history (text, created at runtime)
```

**Data flow:** `file -> scanner -> list[FunctionRecord] -> metrics/complexity -> enriched
records -> rules -> list[Issue] -> severity -> scoring -> ReviewReport -> formatter ->
screen, and storage -> reviews.dat.`

The crucial property: everything from `metrics` rightwards consumes integers. The string
handling is confined to `scanner` and `formatter`, which are thin.

### 7.2 What the user sees

```
$ python main.py

CO7095 CODE REVIEW TOOL
  1) Review a file
  2) View review history
  3) Compare two reviews
  4) Configure thresholds
  5) Quit
> 1
File path: samples/bank_account.py

=== REVIEW REPORT: bank_account.py ===
Lines: 142 code / 28 comment / 19 blank
Functions analysed: 7

  FUNCTION            CC    DEPTH   PARAMS   RATING
  withdraw()          11      5        4     HIGH
  deposit()            3      2        2     OK
  apply_interest()     8      3        3     MEDIUM

ISSUES (5)
  [CRITICAL] withdraw()  line 44  nesting depth 5 exceeds limit 3
  [MAJOR]    withdraw()  line 38  cyclomatic complexity 11 exceeds limit 10
  [MAJOR]    validate()  line 61  duplicated block of 9 lines
  [MINOR]    Account     line 12  missing docstring
  [MINOR]    -           line 88  line length 118 exceeds limit 100

QUALITY SCORE: 62/100  (grade C)
Review saved to reviews.dat
```

### 7.3 Work split across the four members

Each member owns a vertical slice containing branch-heavy numeric functions, so that each
has their own material for the individual testing and research marks.

| Member | Slice | Example branchy functions |
|---|---|---|
| M1 | Scanning, LOC family, configuration of thresholds | `classify_line`, `count_leading_spaces`, `depth_from_indent`, `comment_ratio_band`, `line_length_grade` |
| M2 | Complexity metrics | `cyclomatic_complexity`, `max_nesting_depth`, `parameter_count_rating`, `duplicate_block_score` |
| M3 | Rule engine and severity | `rule_complexity`, `rule_nesting`, `rule_length`, `rule_params`, `classify_severity`, `combine_severities` |
| M4 | Scoring, history, comparison, report assembly | `weighted_penalty`, `score_from_issues`, `grade_band`, `compare_reviews`, `trend_direction` |

**Known risk:** M1's slice is the most string-heavy, which is exactly what the chosen
approach tries to avoid. Mitigation: M1's string functions are kept thin and
single-purpose, and M1 additionally owns the numeric threshold-configuration and
line-metric banding functions, which are branchy and integer-valued. M1's symbolic
execution write-up should target those, not the raw line splitter.

### 7.4 Deliberate complexity

Rule and scoring functions are written with explicit multi-way branching rather than table
lookups or dictionary dispatch. This is a conscious choice against conventional "clean
code" compactness, because the rubric rewards high cyclomatic complexity, multiple
conditions, and rich symbolic execution trees. Readability is preserved through naming,
docstrings and comments, which is what the "self-explanatory, easy to read" criterion in
the code rubric actually measures.

### 7.5 Persistence

`reviews.dat` is a serialised text file holding the review history: one record per review
with timestamp, file name, metric summary, issue list and score. No database. The format
is a decision left to the builder (see Section 9).

---

## 8. Process plan

- **Sprints:** 3 sprints, 2 weeks each, inside the window from now to the 4 January
  deadline, leaving the final stretch for the report, video and packaging.
- **Backlog:** >= 36 user stories, >= 9 per member, balanced to roughly equal story points
  per member. Each sits in the GitHub Project with an assignee, start and end dates, and a
  linked branch that is never deleted after merge.
- **Estimation:** planning poker, Fibonacci 1/3/5/8/13/21, maximum 3 rounds per story, with
  screenshots or photos captured as evidence for the video and report.
- **Tracking:** velocity per sprint, burndown chart per sprint, EVM table (PV, AC, EV, CV,
  SV, CPI, SPI, BAC, EAC) maintained from the start rather than reconstructed at the end.
- **Measurement:** PERT network over development activities with three-point estimates and
  a marked critical path; COCOMO Basic and Intermediate and COCOMO II cost estimates over
  the final KLOC.
- **Configuration management:** semantic versioning, one branch per user story, small
  atomic commits, code review on merge, CMMI Level 2 process areas evidenced as we go.
- **CMMI Level 2 audit:** collect evidence continuously for REQM, PMC, PP, CM, MA and
  PPQA rather than writing it retrospectively.

---

## 9. Left to the builder

- Serialisation format for `reviews.dat` (JSON text, CSV, or a hand-rolled line format) —
  any is acceptable provided it is a plain serialised text file and no database is used.
- Exact default thresholds (complexity limit, nesting limit, line length, parameter count)
  and the penalty weights per severity; these should be configurable through menu item 4.
- The precise grade bands mapping score to letter.
- Scanner edge-case handling: decorators, nested functions, multi-line signatures,
  `if` inside string literals. Approximation is acceptable and should be documented as a
  known limitation in the report.
- Naming of the sample flawed files used for the demonstration.

## 10. Open items needing the team

1. **Student IDs for all four members** — required for the test package names
   `<student_id>.test.blackbox.<technique>`, which must be fixed before any test code is
   written.
2. **Lectures 8-10** — the exact taught black-box and white-box technique names, which
   become directory names in the test packages.
3. **GitHub repository** — created, public, with the Professor and all TAs added.
4. **Sprint start date** — anchors the sprint calendar, the burndown charts and the EVM
   baseline.
