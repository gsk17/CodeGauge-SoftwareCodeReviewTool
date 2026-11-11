# Sprint 2 Backlog

**Sprint:** Mon 23 Nov 2026 to Sun 6 Dec 2026 (2 weeks, 10 working days)
**Committed:** 63 story points across 12 stories

## Sprint goal

The rule set is complete and a review can be written to and read back from the history file.

## Sprint backlog

| ID | Owner | Story | Points | Function | Status | Start | End |
|---|---|---|---|---|---|---|---|
| US03 | Gunjan | As a reviewer I want an indentation width converted to a nesting depth so that deeply nested code can be flagged | 3 | `depth_from_indent` | To do | 26 Nov | 30 Nov |
| US04 | Gunjan | As a reviewer I want comment density as a percentage so that poorly documented files can be flagged | 3 | `comment_ratio_percent` | To do | 23 Nov | 25 Nov |
| US08 | Gunjan | As a reviewer I want the parameters in a definition counted so that functions with too many parameters can be flagged | 5 | `count_parameters` | To do | 01 Dec | 04 Dec |
| US13 | Kasam | As a reviewer I want penalty points charged for excess nesting so that the score reflects how far past the limit the code is | 5 | `nesting_penalty` | To do | 25 Nov | 27 Nov |
| US14 | Kasam | As a reviewer I want a parameter count rated so that the report can describe it in words | 5 | `parameter_count_rating` | To do | 23 Nov | 24 Nov |
| US17 | Kasam | As a reviewer I want duplication expressed as a percentage so that copied code can be flagged | 8 | `duplicate_block_score` | To do | 30 Nov | 04 Dec |
| US21 | Saaket | As a reviewer I want over-long functions reported so that I know which functions to split | 5 | `rule_length` | To do | 25 Nov | 30 Nov |
| US22 | Saaket | As a reviewer I want functions with too many parameters reported so that I know which signatures to simplify | 3 | `rule_params` | To do | 23 Nov | 24 Nov |
| US23 | Saaket | As a reviewer I want insufficiently commented files reported so that I know which files need documenting | 5 | `rule_comment_ratio` | To do | 01 Dec | 04 Dec |
| US31 | Harshita | As a reviewer I want two reviews compared so that I can see whether a file improved or regressed | 8 | `compare_scores` | To do | 23 Nov | 25 Nov |
| US33 | Harshita | As a reviewer I want a report turned into text lines so that it can be stored without a database | 5 | `serialise_report` | To do | 26 Nov | 30 Nov |
| US34 | Harshita | As a reviewer I want stored lines parsed back and corrupt ones rejected so that one bad line does not destroy my history | 8 | `parse_record_line` | To do | 01 Dec | 04 Dec |

## Capacity per member

| Member | Stories | Points |
|---|---|---|
| Gunjan | 3 | 11 |
| Kasam | 3 | 18 |
| Saaket | 3 | 13 |
| Harshita | 3 | 21 |
| **Total** | **12** | **63** |

Ideal burn: 6.3 points per working day over 10 days.

## Events

| Event | When | Output |
|---|---|---|
| Sprint planning | Mon 23 Nov 2026 | this sprint backlog, agreed points |
| Daily scrum | each working day, 15 minutes | entry in `daily-scrum-log.md` |
| Sprint review | Sun 6 Dec 2026 | increment demonstrated, `sprint-2-review.md` |
| Sprint retrospective | Sun 6 Dec 2026 | `sprint-2-retrospective.md` |

## Increment

Tagged `v0.2.0` at the sprint review, per the configuration management
strategy in `docs/cmmi/level2-audit.md`.
