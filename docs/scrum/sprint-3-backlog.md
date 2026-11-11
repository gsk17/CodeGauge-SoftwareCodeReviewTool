# Sprint 3 Backlog

**Sprint:** Mon 7 Dec 2026 to Sun 20 Dec 2026 (2 weeks, 10 working days)
**Committed:** 77 story points across 12 stories

## Sprint goal

Every remaining metric, band and history feature is in place, the command line brings them together, and the increment is the deliverable product.

## Sprint backlog

| ID | Owner | Story | Points | Function | Status | Start | End |
|---|---|---|---|---|---|---|---|
| US06 | Gunjan | As a reviewer I want each line's length graded against a limit so that over-long lines can be reported by seriousness | 5 | `line_length_grade` | To do | 07 Dec | 08 Dec |
| US09 | Gunjan | As a reviewer I want a source file reduced to a record per function so that every later stage works on numbers instead of text | 8 | `scan_file` | To do | 09 Dec | 11 Dec |
| US36 | Gunjan | As a reviewer I want reviews appended to a file and read back so that my review history survives restarting the tool | 13 | `save_review and load_history` | To do | 14 Dec | 18 Dec |
| US15 | Kasam | As a reviewer I want a function's length rated so that over-long functions can be described in words | 8 | `function_length_rating` | To do | 07 Dec | 08 Dec |
| US16 | Kasam | As a reviewer I want a maintainability index per function so that complexity and documentation are weighed together | 8 | `maintainability_index` | To do | 09 Dec | 14 Dec |
| US18 | Kasam | As a reviewer I want complexity, nesting and parameters combined into one rating so that the report has a single per-function verdict | 8 | `complexity_rating` | To do | 15 Dec | 18 Dec |
| US24 | Saaket | As a reviewer I want over-long lines reported so that I know which lines to wrap | 5 | `rule_line_length` | To do | 09 Dec | 10 Dec |
| US25 | Saaket | As a reviewer I want duplicated blocks reported so that I know which code to factor out | 8 | `rule_duplication` | To do | 11 Dec | 18 Dec |
| US27 | Saaket | As a reviewer I want a list of severities reduced to the worst one so that a function can be summarised by its most serious finding | 3 | `combine_severities` | To do | 07 Dec | 08 Dec |
| US05 | Harshita | As a reviewer I want comment density banded so that the report can describe it in words | 3 | `comment_ratio_band` | To do | 07 Dec | 09 Dec |
| US32 | Harshita | As a reviewer I want the trend across my review history described so that I can see the direction of travel | 3 | `trend_direction` | To do | 17 Dec | 18 Dec |
| US35 | Harshita | As a reviewer I want the minimum, maximum and mean of my scores so that I can summarise a file's history | 5 | `history_statistics` | To do | 10 Dec | 16 Dec |

## Capacity per member

| Member | Stories | Points |
|---|---|---|
| Gunjan | 3 | 26 |
| Kasam | 3 | 24 |
| Saaket | 3 | 16 |
| Harshita | 3 | 11 |
| **Total** | **12** | **77** |

Ideal burn: 7.7 points per working day over 10 days.

## Events

| Event | When | Output |
|---|---|---|
| Sprint planning | Mon 7 Dec 2026 | this sprint backlog, agreed points |
| Daily scrum | each working day, 15 minutes | entry in `daily-scrum-log.md` |
| Sprint review | Sun 20 Dec 2026 | increment demonstrated, `sprint-3-review.md` |
| Sprint retrospective | Sun 20 Dec 2026 | `sprint-3-retrospective.md` |

## Increment

Tagged `v0.3.0` at the sprint review, per the configuration management
strategy in `docs/cmmi/level2-audit.md`.
