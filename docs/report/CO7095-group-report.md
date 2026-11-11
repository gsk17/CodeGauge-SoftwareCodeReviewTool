# CodeGauge — A Static Code Review Tool for Python

**CO7095 Software Measurement and Quality Assurance — Group Assignment Report**
**Project #17: Software Code Review Tool**
Module: CO7095, 2026-27 Semester 1
Submission: 4 January 2027

> **Structure warning.** The brief fixes this structure and says "you must adhere to the
> report structure". Do not add, rename or reorder the headings below. Main text must be
> **under 5,000 words** — the cover sheet, tables, figure captions, references and
> appendices are the places to put detail that would otherwise blow the count.
>
> Word budget that fits 5,000: Introduction 300 · Planning & design 1,100 · Implementation
> 700 · Testing & coverage 1,400 (of which the symbolic/concolic subsection 600) · CMMI 600 ·
> Conclusion 300 · Section B 600.

---

## Cover Sheet of Academic Integrity

Module Code: **CO7095**

Assignment: **Group Assignment — Project #17, Software Code Review Tool (CodeGauge)**

> I understand that this is a piece of coursework. I confirm that I handed in a signed
> Declaration of Academic Honesty Form (available at
> https://campus.cs.le.ac.uk/ForStudents/plagiarism/) and that I am fully aware of the
> statements contained therein. I understand if the submission will be checked by Turnitin
> Software. Any submission with similarity scores greater than approximately 20% may be
> further assessed individually and may be reported to Plagiarism Office. You should aim to
> keep the similarity score to less than 10%.

| | Member 1 | Member 2 | Member 3 | Member 4 |
|---|---|---|---|---|
| **Last, First Name** (CAPITALS) | | | | |
| **Student ID** | 259059915 | 259059933 | 269046020 | 269035432 |
| **Date** | | | | |
| **Signature** | | | | |

---

# Section A

## A.1 Introduction

*What the product is, what problem it addresses, and what this report covers. ~300 words.*

Suggested opening paragraph, to adapt rather than copy:

> CodeGauge is a backend static analysis tool that assesses the quality of Python source
> code. Rather than parsing source syntactically, it applies a deliberately line-based
> scanner that reduces each function to a record of integer measurements; every subsequent
> stage - metric computation, rule evaluation, severity classification and scoring - is a
> pure function over those integers. This design was chosen so that each graded function
> admits straightforward black-box partitioning and tractable symbolic execution, in which
> path conditions reduce to linear integer constraints solvable by hand. The tool reports
> size and complexity metrics, rule violations classified across four severity bands, and
> an aggregate quality score, persisting its review history to a serialised text file.

Open with the description below, then cover: project #17 chosen from the list; a backend
Python tool that statically reviews Python source files and reports size and complexity metrics, rule violations with
severities, and a quality score; text menu only, no GUI, no database, standard library only;
why static line-based analysis was chosen over the `ast` module (and that `ast` is not taught
in the module); and a one-paragraph map of the rest of the report.

## A.2 Software planning and design

*~1,100 words plus tables. The tables carry the detail; the prose carries the reasoning.*

### A.2.1 User stories, ownership and story points

Reproduce the 36-story table with, for every story: ID, story text, **owner**, story points,
sprint, and **the full path of the function(s) it produced** — the brief asks for the full
path explicitly. Source: `scripts/stories.tsv` and the backlog tables in the implementation
plan.

| ID | Story | Owner | Points | Sprint | Function path |
|---|---|---|---|---|---|
| US01 | … | Gunjan | 3 | 1 | `core/scanner.py :: classify_line` |
| … | | | | | |

State the per-member totals and that they are equal at equal within 5 points (46/50/45/45).

### A.2.2 Planning poker

How the session ran: Fibonacci deck, maximum three rounds, the reference story, what to do
on non-convergence. Include two or three photographs of real rounds and one story where the
cards diverged and why. Source: `docs/measurement/planning-poker.md`.

### A.2.3 Sprints, burndown and velocity

The three-sprint calendar; one burndown chart per sprint with the ideal and actual lines; the
velocity table; what the retrospectives changed. Source:
`docs/measurement/burndown-and-velocity.md`.

### A.2.4 PERT network and critical path

The activity list with dependencies, the three-point estimates, the network diagram, the
forward and backward pass, slack per activity, and the critical path. Include the worked
calculation for one activity and the probability analysis. **State and discuss the schedule
risk the analysis exposed** (46 days needed against ~41 available) and the three mitigations
— examiners reward an analysis that changed a decision. Source: `docs/measurement/pert.md`.

### A.2.5 Cost estimation: COCOMO I, COCOMO II and EVM

COCOMO I Basic with the mode justified, COCOMO I Intermediate with all 15 cost drivers rated
and the EAF shown, COCOMO II with the five scale factors and the effort multipliers, and the
EVM baseline with the per-sprint table. Include the critical discussion of why the models
over-estimate a 2.6 KLOC student project by roughly eight times and what the estimate is
still worth. Sources: `docs/measurement/cocomo.md`, `docs/measurement/evm.md`.

## A.3 Implementation

### A.3.1 Back-End

*~700 words.* The module structure and the data flow
`file → scanner → FunctionRecord → metrics/complexity → rules → severity → scoring →
ReviewReport → formatter / storage`. Explain the design decision at the centre of the
project: **everything after the scanner consumes integers**, which is what makes every
graded function partitionable for black-box testing and analysable by hand for symbolic
execution. Note the deliberate choice of explicit multi-way branching over dictionary
dispatch, and why (the rubric rewards complexity and rich execution trees; readability is
carried by naming, docstrings and per-branch comments instead).

Include the serialised text format for `reviews.dat`, the threshold configuration, and the
**documented limitations** of line-based scanning: a `def` inside a string literal,
multi-line signatures, a `)` inside a trailing comment, and approximate comprehension
counting. Stating known limitations is a quality-assurance practice, not a weakness.

Run the tool over its own `core/` modules and report the result — the product measuring
itself is worth a paragraph.

## A.4 Testing and Test Coverage Measurement

### A.4.1 Black-Box Testing

Which tool (`pytest`) and which taught techniques. For each technique: the package path, the
functions covered, the test cases, and expected versus actual results. State which test
cases belong to which functions — the brief requires this. Any failure needs an explanation;
aim for none.

### A.4.2 White-Box Testing

As above for the taught white-box techniques, with the coverage achieved per technique.

### A.4.3 Research Component: Symbolic Execution and Concolic Testing

*~600 words, the highest-value section at 20 marks and individually assessed.* Per member,
per function: the symbolic execution tree, the path conditions as conjunctions of linear
integer constraints, the solved concrete witness per path, the concolic iteration table, and
paths found versus paths tested. Each member writes their own. Put the full trees in an
appendix and keep the main text to the method plus two or three representative examples —
including, if you have one, an **infeasible path with the proof that it cannot be taken**,
which is the clearest evidence of understanding the technique. Sources:
`docs/symbolic/WORKED-EXAMPLE.md` and each member's own file.

### A.4.4 Test Coverage of the individual testing technique

The coverage table per member and per technique, the project average, and a line-by-line
account of anything uncovered — either now covered, or recorded as infeasible with the
reason.

## A.5 CMMI Level 2 Documentation Audit

*~600 words.* All six taught Level 2 process areas — REQM, PP, PMC, CM, MA, PPQA — each with
the practice, what the team did and the evidence, plus SAM recorded as not applicable with
the reason. Include the configuration item register and the branching strategy. Keep the two
"the practice working" examples: the requirement inconsistency that traceability caught, and
the test-first deviation the team recorded against itself. Source:
`docs/cmmi/level2-audit.md`.

## A.6 Conclusion

*~300 words.* What was delivered against what was planned; what the measurement actually
told the team as opposed to what it decorated; the two or three things that would be done
differently; and an honest statement of the product's limitations.

---

# Section B

## B.1 Introduction

*~100 words.* What Section B covers: how the team organised itself and how the work was
actually distributed.

## B.2 Team Structure

*~200 words.* Roles and the vertical-slice split — M1 scanning and line metrics, M2
complexity metrics, M3 rule engine and severity, M4 scoring, history and persistence — and
why vertical slices were chosen over horizontal layers: each member needed their own
branch-heavy numeric functions to own for the individually-marked testing and research
components. How Scrum ceremonies ran, how code review was allocated, and how decisions were
made and recorded.

## B.3 Team Contribution and Reflection

*~300 words, each member writes their own paragraph.* Per member: the stories owned, the
functions written, the test packages produced, the symbolic/concolic work done, reviews
performed for others, and an honest reflection — what was harder than estimated, what the
measurement revealed, what you would do differently. Include the per-member story point
totals and the velocity table as evidence of equal distribution.

---

# References

Use a consistent style throughout. Likely sources:

- Boehm, B. W. *Software Engineering Economics*. Prentice Hall, 1981. (COCOMO I)
- Boehm, B. W. et al. *Software Cost Estimation with COCOMO II*. Prentice Hall, 2000.
- CMMI Product Team. *CMMI for Development, Version 1.3*. Carnegie Mellon SEI, 2010.
- Pezzè, M. and Young, M. *Software Testing and Analysis: Process, Principles and
  Techniques*. Wiley, 2008.
- Walkinshaw, N. *Software Quality Assurance: Consistency in the Face of Complexity and
  Change*. Springer, 2017.
- King, J. C. "Symbolic execution and program testing". *Communications of the ACM*, 19(7),
  1976. (the original symbolic execution paper)
- Sen, K., Marinov, D. and Agha, G. "CUTE: a concolic unit testing engine for C". *ESEC/FSE*,
  2005. (the concolic testing paper)
- Module lecture slides, CO7095, University of Leicester, 2026-27.

---

# Appendices

- **Appendix A** — Full 36-story backlog with owners, points, sprints and function paths
- **Appendix B** — Complete symbolic execution trees and path condition tables, per member
- **Appendix C** — Full coverage report
- **Appendix D** — Burndown charts and the EVM table
- **Appendix E** — Planning poker round photographs
- **Appendix F** — GitHub Project board screenshots, per sprint
- **Appendix G** — README (how to uncompress, import into PyCharm, run the code and tests)

---

## Pre-submission checklist

- [ ] Main text under 5,000 words (check excluding cover sheet, tables, references, appendices)
- [ ] Structure matches the brief exactly — no added, renamed or reordered headings
- [ ] Cover sheet signed by all four members, with student IDs and dates
- [ ] Every story in the table names its owner **and the full function path**
- [ ] Every test case attributed to the function it tests
- [ ] Every failed test explained (ideally none)
- [ ] All six CMMI process areas evidenced, SAM recorded as not applicable
- [ ] Working public GitHub link included
- [ ] Every figure referenced from the main text
- [ ] Turnitin similarity under 10% (submit an early attempt to check)
- [ ] Exported to PDF
