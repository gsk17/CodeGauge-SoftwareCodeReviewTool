# Sprint 1 Backlog

**Sprint:** Mon 9 Nov 2026 to Sun 22 Nov 2026 (2 weeks, 10 working days)
**Committed:** 56 story points across 12 stories

## Sprint goal

A file can be scanned into per-function records, its complexity measured, the first rules raised against it and a score produced - the thin end-to-end thread through every member's slice.

## Sprint backlog

| ID | Owner | Story | Points | Function | Status | Start | End |
|---|---|---|---|---|---|---|---|
| US01 | Gunjan | As a reviewer I want each source line classified as blank, comment or code so that the tool can count the three kinds separately | 3 | `classify_line` | To do | | |
| US02 | Gunjan | As a reviewer I want a line's indentation measured in spaces so that nesting depth can be derived from it | 3 | `count_leading_spaces` | To do | | |
| US07 | Gunjan | As a reviewer I want function definition lines recognised so that the tool knows where each function starts | 3 | `is_function_header` | To do | | |
| US10 | Kasam | As a reviewer I want the decision keywords in a function totalled so that cyclomatic complexity can be computed from them | 5 | `decision_points` | To do | | |
| US12 | Kasam | As a reviewer I want the deepest nesting level in a function found so that deeply nested code can be flagged | 5 | `max_nesting_depth` | To do | | |
| US20 | Kasam | As a reviewer I want functions nested too deeply reported so that I know which functions to flatten | 3 | `rule_nesting` | To do | | |
| US11 | Saaket | As a reviewer I want each function's cyclomatic complexity computed so that over-complex functions can be flagged | 8 | `cyclomatic_complexity` | To do | | |
| US19 | Saaket | As a reviewer I want functions over the complexity limit reported so that I know which functions to simplify | 5 | `rule_complexity` | To do | | |
| US26 | Saaket | As a reviewer I want a measurement banded against its limit so that every rule grades its findings on one consistent scale | 5 | `classify_severity` | To do | | |
| US28 | Harshita | As a reviewer I want each severity to carry a penalty weight so that serious findings cost more than trivial ones | 5 | `weighted_penalty` | To do | | |
| US29 | Harshita | As a reviewer I want a quality score from the issues found so that a file's state is a single number | 8 | `score_from_issues` | To do | | |
| US30 | Harshita | As a reviewer I want a letter grade from the score so that the result is readable at a glance | 3 | `grade_band` | To do | | |

## Capacity per member

| Member | Stories | Points |
|---|---|---|
| Gunjan | 3 | 9 |
| Kasam | 3 | 13 |
| Saaket | 3 | 18 |
| Harshita | 3 | 16 |
| **Total** | **12** | **56** |

Ideal burn: 5.6 points per working day over 10 days.

## Events

| Event | When | Output |
|---|---|---|
| Sprint planning | Mon 9 Nov 2026 | this sprint backlog, agreed points |
| Daily scrum | each working day, 15 minutes | entry in `daily-scrum-log.md` |
| Sprint review | Sun 22 Nov 2026 | increment demonstrated, `sprint-1-review.md` |
| Sprint retrospective | Sun 22 Nov 2026 | `sprint-1-retrospective.md` |

## Increment

Tagged `v0.1.0` at the sprint review, per the configuration management
strategy in `docs/cmmi/level2-audit.md`.
