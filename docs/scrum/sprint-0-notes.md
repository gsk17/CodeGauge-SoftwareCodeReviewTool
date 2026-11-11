# Sprint 0 — Design and Planning

**4 to 7 November 2026.** Before Sprint 1, which starts Monday 9 November.

Sprint 0 is not a development sprint. It produced no user-story functionality; it
produced the things Sprint 1 needs in order to start: the chosen project, the design,
the backlog, the estimates, the process agreements and the repository.

## What was produced

| Artifact | Where |
|---|---|
| Project topic chosen and confirmed (#17, Software Code Review Tool) | this file |
| Design document: goals, approaches considered and rejected, architecture | [../design/specs/2026-11-04-code-review-tool-design.md](../design/specs/2026-11-04-code-review-tool-design.md) |
| Implementation plan: 36 stories, signatures, fixed values, sprint calendar | [../design/plans/2026-11-04-code-review-tool.md](../design/plans/2026-11-04-code-review-tool.md) |
| Product backlog with MoSCoW priorities | [product-backlog.md](product-backlog.md) |
| Sprint backlogs for Sprints 1–3 | [sprint-1-backlog.md](sprint-1-backlog.md), [sprint-2-backlog.md](sprint-2-backlog.md), [sprint-3-backlog.md](sprint-3-backlog.md) |
| Definition of Done, agreed by all four | [definition-of-done.md](definition-of-done.md) |
| PERT network, critical path and schedule risk | [../measurement/pert.md](../measurement/pert.md) |
| COCOMO I and II estimates | [../measurement/cocomo.md](../measurement/cocomo.md) |
| EVM baseline, BAC 392 person-hours | [../measurement/evm.md](../measurement/evm.md) |
| Planning poker record sheet | [../measurement/planning-poker.md](../measurement/planning-poker.md) |
| CMMI Level 2 audit framework | [../cmmi/level2-audit.md](../cmmi/level2-audit.md) |
| Project skeleton, data model, test tooling | `main.py`, `model/`, `pytest.ini`, `.coveragerc` |

## The prototype spike, and why it exists

During Sprint 0 the team built a **throwaway prototype** of the whole tool to answer
three questions that the estimates depended on and that could not be answered on paper:

1. **Is the line-based design viable at all, without the `ast` module?** The spec rejects
   `ast` because the module does not teach it, and rejects wrapping a linter because the
   brief forbids it. That leaves line-based scanning, and the only honest way to find out
   whether it can measure real Python was to try it. It can, with documented
   approximations — and the prototype is what found them.
2. **How large is the work really?** COCOMO needs a size input. Guessing KLOC for an
   unfamiliar product is the largest single source of error in a cost estimate, so the
   prototype was measured instead of guessed, and its measurement is the basis of the
   estimate in `cocomo.md`.
3. **Will the functions be analysable by hand?** 40 of the 100 marks depend on testing
   every function and performing symbolic and concolic execution on every function. The
   prototype confirmed that keeping every post-scanner function integer-valued produces
   path conditions that are linear integer constraints, which is the design decision the
   whole architecture rests on.

**The prototype was thrown away.** It was a throwaway spike in the literal sense: built to
answer the three questions above, measured, and then discarded. Nothing from it is carried
into the deliverable. `main` carries only the Sprint 0 baseline, and the 36 user stories are
developed from the specification during Sprints 1–3, one branch and one pull request per
story, each with its own tests written first, its own technique packages and its own
symbolic analysis by the member who owns it.

What the spike left behind is written down rather than kept as code: the architecture
decision in the design specification, the size measurement the COCOMO estimate uses, and the
list of traps a line-based scanner falls into — multi-line function signatures, continuation
lines of wrapped expressions read as deep nesting, docstring prose counted as operators —
recorded in the implementation plan's Review Focus section.

Building a spike to retire technical risk before committing to estimates is ordinary
practice, and discarding it afterwards is what the word "throwaway" means.

## Risks identified at Sprint 0

| Risk | Assessment | Mitigation |
|---|---|---|
| The critical path needs 46 working days against roughly 41 available | ~7% confidence of finishing in the window ([pert.md](../measurement/pert.md) §6) | overlap the symbolic write-ups with the coverage work, which shortens the path to ~39.8 days; use F, G, K and L slack for blocked members |
| 40 marks are individual, so one member falling behind cannot be covered by the others | high impact | equal equal within 5 points (46/55/47/48); per-member completion tracked in the burndown file; Definition of Done names the individual artifacts per story |
| Technique directory names come from Lectures 8–10, not yet delivered | blocks the test package layout, not the code | `scripts/rename_test_packages.sh` parameterises them; confirm before Sprint 1 testing |
| University usernames needed for package names; student numbers cannot be Python packages | blocks the test packages entirely | collect in the first lab session; the script now rejects a digit-leading name outright |
| COCOMO over-estimates a project this small by roughly eightfold | affects the write-up, not the plan | discussed explicitly in `cocomo.md` §5 rather than presented as a prediction |

## Sprint 1 planning decisions

- **Sprint length:** 2 weeks, as the brief requires a minimum of 1–2 weeks.
- **Capacity:** 56 points, from 192 total across three sprints.
- **Sprint 1 goal:** a thin end-to-end thread through all four slices — a file can be
  scanned, measured, a rule raised against it and a score produced. Chosen over
  completing one member's slice first, so that integration risk surfaces in Sprint 1
  rather than Sprint 3.
- **Ordering constraint:** US10 (`decision_points`) before US09 (`scan_file`), because
  the scanner calls it rather than duplicating the summation. This is the `E → D`
  dependency on the PERT network.
- **Ceremonies:** planning on day 1, daily scrum each working day recorded through
  `scripts/daily_scrum.sh`, review and retrospective on the final day.
