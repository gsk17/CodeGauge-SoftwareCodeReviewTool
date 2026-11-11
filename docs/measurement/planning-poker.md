# Planning Poker Record

Project: CodeGauge — CO7095 project #17
Deck: Fibonacci **1, 3, 5, 8, 13, 21** · Platform: planningpoker.com
Participants: Gunjan (gsk17), Kasam (khm12), Saaket (ssl21), Harshita (hcg22) — all four present
Reference story: **US01 `classify_line` = 3 points**

All 36 product backlog stories were estimated over two rounds, with a structured
discussion between them. The round 2 values are the agreed estimates.

## Rules the team agreed

- Fibonacci deck, maximum 3 rounds per story.
- Everyone reveals simultaneously; nobody speaks a number first, so no anchoring.
- A spread of 5 points or more is discussed before re-voting, with the highest and the
  lowest estimator each explaining their reasoning.
- The points carried into the sprint backlogs are the team's **agreed** values, not the
  platform's computed score.
- A story estimated at 13 or above is a candidate for splitting.

## Evidence

| Artifact | Path |
|---|---|
| Round 1, 36 screenshots | `poker/Planning Poker/Round1/1..36.png` |
| Round 1, platform export | `poker/Planning Poker/Round1/planningpoker-export-score.csv` |
| Round 1, session PDF | `poker/Planning Poker/Round1/PlanningPoker.com - Round1.pdf` |
| Round 1, per-member votes and reasons | `poker/Planning Poker/Round1/Dissagreement_round1.txt` |
| Discussion outcomes | `poker/Planning Poker/Round1/Discussion_outcomes.txt` |
| Round 2, 36 screenshots | `poker/Planning Poker/Round2/1..36.png` |
| Round 2, platform export | `poker/Planning Poker/Round2/planningpoker-export-Round2.csv` |
| Round 2, session PDF | `poker/Planning Poker/Round2/PlanningPoker.com - Round2.pdf` |
| Story list used in the session | `poker-import.txt` |

## What the two rounds did

| | Total | Note |
|---|---|---|
| Round 1 | **280 points** | only US01, the reference story, was unanimous |
| Round 2 | **196 points** | 27 of the 36 stories moved after discussion |
| **Final agreed** | **196 points** | the round 2 values, carried into the sprint backlogs |

Round 1 produced wide spreads, which is what an honest first round looks like on an
unfamiliar problem. **Sixteen stories had a spread of 5 points or more**, and eight had a
spread of 8 or more: US09, US16, US17, US18, US25, US29, US34 and US36.

The aggregate fell 280 → 196, a reduction of 30%. The direction is not an
accident. Almost every first-round estimate was high because nobody had yet agreed how
much existing work each story could reuse, and the discussion was largely about reuse —
the outcomes below say so explicitly.

## The four largest disagreements, and how they resolved

| Story | Spread | The disagreement | Outcome |
|---|---|---|---|
| **US36** `save_review` / `load_history` | 8–21 | Harshita estimated 21 for persistence and error handling; Kasam estimated 8, expecting basic file operations to suffice | settled at **13** — still the largest story in the project and a candidate for splitting |
| **US16** `maintainability_index` | 5–13 | Gunjan and Saaket saw the formula and the combination of measurements as complex; Harshita expected the existing measurements to be reusable | **8** — agreed to use the existing complexity and documentation measurements rather than compute new ones |
| **US25** `rule_duplication` | 5–13 | Kasam expected substantial detection logic; Harshita expected the rule to reuse the existing duplication score | **8** — agreed to reuse the existing duplication measurement rather than build separate detection |
| **US29** `score_from_issues` | 5–13 | Kasam expected complexity in aggregating penalties and bounding the score; Harshita expected a straightforward calculation | **8** — agreed to reuse the severity weights and the existing issue data |

Two more were resolved the same way: **US04** `comment_ratio_percent` — agreed on a
straightforward percentage with defined zero-line handling — and **US12**
`max_nesting_depth`, agreed to reuse the existing function and indentation information.

Every one came down to the same question: how much can this story reuse? That is why the
totals fell so sharply between the rounds, and it is the single most useful thing the
session produced, because it settled the architecture question as well as the numbers.

## Full record

R1 votes are the four individual cards from round 1. R1 and R2 are the platform's computed
score for each round. **Final** is the team's agreed value, which is what the sprint
backlogs, the burndown and the EVM baseline all use.

| ID | Function | Owner | R1 votes G/K/S/H | R1 | R2 / Final |
|---|---|---|---|---|---|
| US01 | `classify_line` | Gunjan | 3/3/3/3 | 3 | **3** |
| US02 | `count_leading_spaces` | Gunjan | 2/3/5/3 | 5 | **3** |
| US03 | `depth_from_indent` | Gunjan | 3/5/3/2 | 5 | **3** |
| US04 | `comment_ratio_percent` | Gunjan | 5/3/5/2 | 5 | **3** |
| US05 | `comment_ratio_band` | Harshita | 2/3/5/3 | 5 | **3** |
| US06 | `line_length_grade` | Gunjan | 5/3/8/5 | 8 | **5** |
| US07 | `is_function_header` | Gunjan | 3/5/2/3 | 5 | **3** |
| US08 | `count_parameters` | Gunjan | 5/3/8/5 | 8 | **5** |
| US09 | `scan_file` | Gunjan | 8/5/13/8 | 13 | **8** |
| US10 | `decision_points` | Kasam | 3/5/5/3 | 5 | **5** |
| US11 | `cyclomatic_complexity` | Saaket | 8/5/8/5 | 8 | **8** |
| US12 | `max_nesting_depth` | Kasam | 5/8/5/3 | 8 | **5** |
| US13 | `nesting_penalty` | Kasam | 5/3/8/5 | 8 | **5** |
| US14 | `parameter_count_rating` | Kasam | 2/3/5/3 | 5 | **3** |
| US15 | `function_length_rating` | Kasam | 5/3/5/2 | 5 | **5** |
| US16 | `maintainability_index` | Kasam | 13/8/13/5 | 13 | **8** |
| US17 | `duplicate_block_score` | Kasam | 8/5/8/13 | 13 | **8** |
| US18 | `complexity_rating` | Kasam | 8/5/13/8 | 13 | **8** |
| US19 | `rule_complexity` | Saaket | 3/5/3/5 | 5 | **5** |
| US20 | `rule_nesting` | Kasam | 5/3/5/3 | 5 | **3** |
| US21 | `rule_length` | Saaket | 3/5/8/5 | 8 | **5** |
| US22 | `rule_params` | Saaket | 3/2/5/3 | 5 | **3** |
| US23 | `rule_comment_ratio` | Saaket | 5/3/5/8 | 8 | **5** |
| US24 | `rule_line_length` | Saaket | 2/3/5/3 | 5 | **3** |
| US25 | `rule_duplication` | Saaket | 8/13/8/5 | 13 | **8** |
| US26 | `classify_severity` | Saaket | 5/3/5/3 | 5 | **5** |
| US27 | `combine_severities` | Saaket | 3/5/2/3 | 5 | **3** |
| US28 | `weighted_penalty` | Harshita | 5/3/8/5 | 8 | **5** |
| US29 | `score_from_issues` | Harshita | 8/13/8/5 | 13 | **8** |
| US30 | `grade_band` | Harshita | 3/2/5/3 | 5 | **3** |
| US31 | `compare_scores` | Harshita | 5/8/5/3 | 8 | **5** |
| US32 | `trend_direction` | Harshita | 3/5/2/3 | 5 | **3** |
| US33 | `serialise_report` | Harshita | 5/8/5/8 | 8 | **5** |
| US34 | `parse_record_line` | Harshita | 8/5/13/8 | 13 | **8** |
| US35 | `history_statistics` | Harshita | 3/5/5/3 | 5 | **5** |
| US36 | `save_review and load_history` | Gunjan | 13/8/13/21 | 21 | **13** |

## Per-member workload

The agreed points produced an uneven split, so two same-sprint **swaps** were made to meet
the brief's requirement that per-member totals be relatively equal. Swapping rather than
moving preserved the rule that every member has at least three stories in every sprint — a
straight move would have left two members with only two stories in Sprint 3.

- US05 `comment_ratio_band` Gunjan ⇄ US36 `save_review` / `load_history` Harshita
- US20 `rule_nesting` Saaket ⇄ US11 `cyclomatic_complexity` Kasam

| Member | Before swaps | After swaps | Stories |
|---|---|---|---|
| Gunjan | **46** | 9 |
| Kasam | **50** | 9 |
| Saaket | **45** | 9 |
| Harshita | **45** | 9 |
| **Total** | **196** | **196** | **36** |

Spread fell from 18 points to 9. Ownership is therefore per **function**, not per module:
Saaket owns US11 inside `core/complexity.py`, and Gunjan owns US36 inside
`core/storage.py`.

## Sprint distribution

| Sprint | Stories | Points | Ideal burn |
|---|---|---|---|
| Sprint 1, 9–22 Nov 2026 | 12 | 56 | 5.6/day |
| Sprint 2, 23 Nov–6 Dec 2026 | 12 | 63 | 6.3/day |
| Sprint 3, 7–20 Dec 2026 | 12 | 77 | 7.7/day |

At 2 person-hours per point, the EVM Budget at Completion is **392 person-hours**.
