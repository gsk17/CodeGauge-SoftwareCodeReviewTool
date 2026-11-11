# Planning Poker Record

Project: CodeGauge - CO7095 project #17, Software Code Review Tool
Session date: `<fill in>` — Sprint 1 planning
Participants: Gunjan, Kasam, Saaket, Harshita (all four must be present)

## Rules the team agreed

- Deck: Fibonacci **1, 3, 5, 8, 13, 21**.
- Everyone reveals simultaneously; no anchoring by speaking first.
- Maximum **3 rounds** per story. If round 3 does not converge, the **highest** card stands
  and the reason for the spread is recorded in the Notes column — a persistent spread is
  information, usually that the story is under-specified.
- Reference story: **US01 `classify_line` = 3 points**. Every other estimate is relative to it.
- A story estimated at 13 or 21 is too big and is split before the sprint starts.

## Evidence required

Photograph or screenshot **each round** of each story — four cards visible — and save them as
`docs/measurement/poker/US<NN>-round<N>.jpg`. The rubric asks for story points
"estimated via Planning Poker **with evidence**"; the table below without the images is not
evidence.

## The estimates brought into the session

The "seed" column is the estimate from the implementation plan. It is a starting point for
discussion, **not** the agreed value — the whole point of the session is that the four
owners estimate their own work. Record what the team actually agrees in the "Agreed" column
even where it differs from the seed, then update the GitHub issue point field to match.

### Gunjan — M1, scanning and line metrics

| ID | Story | Seed | R1 cards (G/K/S/H) | R2 | R3 | Agreed | Notes |
|---|---|---|---|---|---|---|---|
| US01 | `classify_line` — blank, comment or code | 3 | / / / | | | | reference story |
| US02 | `count_leading_spaces` — indentation width | 3 | / / / | | | | |
| US07 | `is_function_header` — recognise a definition | 8 | / / / | | | | |
| US03 | `depth_from_indent` — indentation to depth | 5 | / / / | | | | |
| US08 | `count_parameters` — parameters in a signature | 8 | / / / | | | | |
| US04 | `comment_ratio_percent` — comment density | 3 | / / / | | | | |
| US05 | `comment_ratio_band` — band the density | 5 | / / / | | | | |
| US06 | `line_length_grade` — grade a line's length | 5 | / / / | | | | |
| US09 | `scan_file` — file to FunctionRecords | 8 | / / / | | | | depends on US10 |
| | **Total** | **48** | | | | | |

### Kasam — M2, complexity metrics

| ID | Story | Seed | R1 cards (G/K/S/H) | R2 | R3 | Agreed | Notes |
|---|---|---|---|---|---|---|---|
| US10 | `decision_points` — sum the keyword counts | 5 | / / / | | | | US09 depends on this |
| US11 | `cyclomatic_complexity` — E - N + 2P | 8 | / / / | | | | |
| US12 | `max_nesting_depth` — deepest level | 5 | / / / | | | | |
| US13 | `nesting_penalty` — penalty for excess nesting | 3 | / / / | | | | |
| US14 | `parameter_count_rating` — rate a count | 3 | / / / | | | | |
| US17 | `duplicate_block_score` — duplication percentage | 8 | / / / | | | | |
| US15 | `function_length_rating` — rate a length | 5 | / / / | | | | |
| US18 | `complexity_rating` — combined four-way rating | 8 | / / / | | | | |
| US16 | `maintainability_index` — 0-100 index | 3 | / / / | | | | |
| | **Total** | **48** | | | | | |

### Saaket — M3, rule engine and severity

| ID | Story | Seed | R1 cards (G/K/S/H) | R2 | R3 | Agreed | Notes |
|---|---|---|---|---|---|---|---|
| US26 | `classify_severity` — band against the limit | 8 | / / / | | | | every rule depends on this |
| US19 | `rule_complexity` | 5 | / / / | | | | |
| US20 | `rule_nesting` | 5 | / / / | | | | |
| US21 | `rule_length` | 5 | / / / | | | | |
| US22 | `rule_params` | 5 | / / / | | | | |
| US23 | `rule_comment_ratio` | 5 | / / / | | | | runs in the opposite direction |
| US24 | `rule_line_length` | 5 | / / / | | | | |
| US25 | `rule_duplication` | 5 | / / / | | | | |
| US27 | `combine_severities` — worst of a list | 5 | / / / | | | | |
| | **Total** | **48** | | | | | |

### Harshita — M4, scoring, history and persistence

| ID | Story | Seed | R1 cards (G/K/S/H) | R2 | R3 | Agreed | Notes |
|---|---|---|---|---|---|---|---|
| US28 | `weighted_penalty` — weight per severity | 3 | / / / | | | | |
| US29 | `score_from_issues` — 0-100 score | 8 | / / / | | | | the critical-issue cap |
| US30 | `grade_band` — letter grade | 3 | / / / | | | | |
| US33 | `serialise_report` — report to text lines | 5 | / / / | | | | |
| US34 | `parse_record_line` — parse a stored line | 8 | / / / | | | | corrupt-line handling |
| US31 | `compare_scores` — classify the change | 5 | / / / | | | | |
| US36 | `save_review` / `load_history` | 8 | / / / | | | | round-trip |
| US32 | `trend_direction` — trend across history | 5 | / / / | | | | |
| US35 | `history_statistics` — min, max, mean | 3 | / / / | | | | |
| | **Total** | **48** | | | | | |

## Balance check after the session

The brief requires the total story points per member to be **relatively equal**. Complete
this after the agreed column is filled:

| Member | Agreed total | Difference from mean |
|---|---|---|
| Gunjan | _ | _ |
| Kasam | _ | _ |
| Saaket | _ | _ |
| Harshita | _ | _ |
| **Mean** | **_** | |

If any member is more than 5 points from the mean, move a story between members and
re-estimate the moved story, then update this table and the GitHub issue assignments. Record
what moved and why — a deliberate, documented rebalance reads far better than four totals
that happen to be unequal.
