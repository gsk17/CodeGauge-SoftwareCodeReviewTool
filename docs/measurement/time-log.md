# Time Log — Actual Cost for Earned Value Management

Earned Value needs three numbers. Two of them are already known; this file collects the
third.

| | What it is | Where it comes from |
|---|---|---|
| **PV** Planned Value | what we said we would finish by now | the sprint backlogs |
| **EV** Earned Value | what we actually finished, valued at plan | closed issues |
| **AC** Actual Cost | **hours actually spent** | **this file, and only this file** |

Without AC there is no CPI and no SPI, and those are two of the measures the brief lists
by name. Nothing else in the project can supply them.

> **Status:** the Actual column is filled in only for stories that have **closed**. Rows
> for work not yet closed are deliberately blank — under the 0/100 rule a part-finished
> story has earned nothing, so an hours figure against it would have no earned value to
> compare against, and CPI computed that way is not a measurement.

## How to record

**When you finish a story**, before you move the card to Done:

1. Comment on the GitHub issue: `Hours spent: 4.5`
2. Add the same number to the table below
3. Commit it with that day's daily scrum

Record **the hours you actually spent**, including the time that went nowhere — the branch
cut from the wrong base, the test that passed when it should have failed, the twenty
minutes working out why `pytest` could not see your package. That lost time is the most
useful data in the whole table, because it is what the retrospective is for.

Round to the nearest half hour. Do it the same day; a number remembered in December is a
guess, and a guess makes CPI and SPI meaningless.

## Budget

1 story point = **2 person-hours**, agreed at Sprint 1 planning from the reference story
(US01 `classify_line`, 3 points, estimated at 6 hours including its tests and write-up).

196 points × 2 = **392 person-hours**, the Budget at Completion.

## The log

### Sprint 1 — 56 points, 112 hours budgeted

| ID | Owner | Function | Points | Budget (h) | **Actual (h)** | Notes |
|---|---|---|---|---|---|---|
| US01 ✅ | Gunjan | `classify_line` | 3 | 6 | **5.0** | reference story; set the pattern the other 35 follow |
| US02 ✅ | Gunjan | `count_leading_spaces` | 3 | 6 | **5.0** | the first function with a loop, so the first bounded-unrolling write-up |
| US07 ✅ | Gunjan | `is_function_header` | 3 | 6 | **5.0** | string predicates, no loop — the cleanest symbolic tree in the project |
| US10 ✅ | Kasam | `decision_points` | 5 | 10 | **6.0** | branch initially cut from the US01 branch rather than main; resolved by merging US01 first |
| US12 ✅ | Kasam | `max_nesting_depth` | 5 | 10 | **6.0** | two sequential loops; the analysis found three single-solution path conditions |
| US20 ✅ | Kasam | `rule_nesting` | 3 | 6 | **2.5** | **cheapest story of the sprint** — US19 had already settled the rule shape |
| US11 ✅ | Saaket | `cyclomatic_complexity` | 8 | 16 | **7.0** | tests written 12 Nov, finished in an unplanned Sunday session on 15 Nov to recover the lost Friday |
| US19 ✅ | Saaket | `rule_complexity` | 5 | 10 | **4.5** | cheapest of the five-pointers; `classify_severity` did the banding, so the rule is nine lines |
| US26 ✅ | Saaket | `classify_severity` | 5 | 10 | **6.0** | dependency root - every rule story calls it, so taken first |
| US28 ✅ | Harshita | `weighted_penalty` | 5 | 10 | **6.0** | implementation waited on US26 merging for the severity constants |
| US29 ✅ | Harshita | `score_from_issues` | 8 | 16 | **9.5** | **most expensive** — the cap and floor interact and nothing preceded it |
| US30 ✅ | Harshita | `grade_band` | 3 | 6 | **3.5** | cheapest story so far; no dependencies and the bands were already agreed |
| | | **Sprint complete** | **56** | **112** | **66.0** | **12 of 12 stories.** CPI 112 / 66.0 = **1.70**, SPI 1.00 |
| | | **Sprint committed** | **56** | **112** | | |

### Sprint 2 — 63 points, 126 hours budgeted

| ID | Owner | Function | Points | Budget (h) | **Actual (h)** | Notes |
|---|---|---|---|---|---|---|
| US03 | Gunjan | `depth_from_indent` | 3 | 6 |  |  |
| US04 ✅ | Gunjan | `comment_ratio_percent` | 3 | 6 | **3.5** | new module `core/line_metrics.py`; closed 26 Nov |
| US08 | Gunjan | `count_parameters` | 5 | 10 |  |  |
| US13 | Kasam | `nesting_penalty` | 5 | 10 |  |  |
| US14 ✅ | Kasam | `parameter_count_rating` | 5 | 10 | **6.0** | the sixth five-pointer and the fifth to land on exactly 6.0; closed 26 Nov |
| US17 | Kasam | `duplicate_block_score` | 8 | 16 |  |  |
| US21 | Saaket | `rule_length` | 5 | 10 |  |  |
| US22 ✅ | Saaket | `rule_params` | 3 | 6 | **2.5** | equal to US20 — the two cheapest stories in the project are both rules of the same shape; closed 26 Nov |
| US23 | Saaket | `rule_comment_ratio` | 5 | 10 |  |  |
| US31 ✅ | Harshita | `compare_scores` | 8 | 16 | **9.5** | new module `core/history.py`; equal to US29, and the most expensive story of its sprint for the second sprint running; closed 26 Nov |
| US33 | Harshita | `serialise_report` | 5 | 10 |  |  |
| US34 | Harshita | `parse_record_line` | 8 | 16 |  |  |
| | | **Closed so far (4 of 12)** | **19** | **38** | **21.5** | CPI 38 / 21.5 = **1.77** |
| | | **Sprint committed** | **63** | **126** | | 8 stories open, 44 points |

### Sprint 3 — 77 points, 154 hours budgeted

| ID | Owner | Function | Points | Budget (h) | **Actual (h)** | Notes |
|---|---|---|---|---|---|---|
| US06 | Gunjan | `line_length_grade` | 5 | 10 |  |  |
| US09 | Gunjan | `scan_file` | 8 | 16 |  |  |
| US36 | Gunjan | `save_review and load_history` | 13 | 26 |  |  |
| US15 | Kasam | `function_length_rating` | 8 | 16 |  |  |
| US16 | Kasam | `maintainability_index` | 8 | 16 |  |  |
| US18 | Kasam | `complexity_rating` | 8 | 16 |  |  |
| US24 | Saaket | `rule_line_length` | 5 | 10 |  |  |
| US25 | Saaket | `rule_duplication` | 8 | 16 |  |  |
| US27 | Saaket | `combine_severities` | 3 | 6 |  |  |
| US05 | Harshita | `comment_ratio_band` | 3 | 6 |  |  |
| US32 | Harshita | `trend_direction` | 3 | 6 |  |  |
| US35 | Harshita | `history_statistics` | 5 | 10 |  |  |
| | | **Sprint committed** | **77** | **154** | | not started |

### Project to date

| | Points | Budget (h) | Actual (h) | CPI |
|---|---|---|---|---|
| Closed | 75 | 150 | 87.5 | **1.71** |
| Remaining | 121 | 242 | — | — |
| **Budget at Completion** | **196** | **392** | | |

## Rolling up to EVM

At each sprint review, from the figures above:

```
PV   = points planned this sprint x 2
EV   = points CLOSED this sprint x 2          (a part-finished story earns 0)
AC   = sum of the Actual column for closed stories

CV   = EV - AC          negative means over budget
SV   = EV - PV          negative means behind schedule
CPI  = EV / AC          below 1.0 means each hour bought less than planned
SPI  = EV / PV          below 1.0 means slower than planned
EAC  = BAC / CPI        what the whole project will cost at this rate
```

Put the result in [evm.md](evm.md), keeping the arithmetic lines visible — the rubric
rewards the shown calculation as much as the answer.

## Reading the result

| CPI | What it means | What to do |
|---|---|---|
| **0.7–0.9** | each story is costing more than the 2 h/point rate assumed | normal in sprint 1. Recalibrate the rate for the next sprint rather than demanding more hours |
| **0.9–1.1** | the estimate is holding | nothing |
| **1.1–1.4** | finishing faster than estimated | the rate may be padded, or sprint 1 was the easy stories |
| **above 1.5** | the estimate was far too generous | say so, and lower the rate |

| SPI | What it means |
|---|---|
| below 1.0 | behind the planned pace |
| around 1.0 | on pace |
| above 1.0 | ahead |

**The pairing is what matters, not either number alone:**

- **CPI low, SPI near 1** — you are delivering on time but each story costs more than
  budgeted. That is *under-estimation*, not slow work. The fix is a better rate, not more
  hours.
- **CPI near 1, SPI low** — the rate is right but less is getting done. Usually capacity:
  someone unavailable, or blocked waiting on another story.
- **Both low** — genuinely behind. Cut scope from the COULD stories, or rebalance.
- **Both high** — ahead and cheap. Pull Sprint 3 work forward; it is the heaviest sprint.

## Why imperfect numbers are the better outcome

A CPI of exactly 1.00 across three sprints would say nothing. The marks here are for
*"what the measurement told us and what we changed"*, and a project that never deviates
gives the retrospective nothing to discuss.

A CPI of 0.83 in Sprint 1, a recalibrated rate, and 0.97 in Sprint 2 is a far better story
than three perfect sprints — it shows the measurement was actually used to make a decision,
which is the entire point of tracking it.

So record what really happened. The analysis is where the marks are.

## Closed to date

**Sixteen stories closed: 87.5 hours against a 150 hour budget, a CPI of 1.71.**

Twelve from Sprint 1, four from Sprint 2.

| Story | Owner | Points | Budget (h) | Actual (h) | h/point |
|---|---|---|---|---|---|
| US20 | Kasam | 3 | 6 | 2.5 | 0.83 |
| US22 | Saaket | 3 | 6 | 2.5 | 0.83 |
| US04 | Gunjan | 3 | 6 | 3.5 | 1.17 |
| US30 | Harshita | 3 | 6 | 3.5 | 1.17 |
| US01 | Gunjan | 3 | 6 | 5.0 | 1.67 |
| US02 | Gunjan | 3 | 6 | 5.0 | 1.67 |
| US07 | Gunjan | 3 | 6 | 5.0 | 1.67 |
| US19 | Saaket | 5 | 10 | 4.5 | 0.90 |
| US10 | Kasam | 5 | 10 | 6.0 | 1.20 |
| US12 | Kasam | 5 | 10 | 6.0 | 1.20 |
| US14 | Kasam | 5 | 10 | 6.0 | 1.20 |
| US26 | Saaket | 5 | 10 | 6.0 | 1.20 |
| US28 | Harshita | 5 | 10 | 6.0 | 1.20 |
| US11 | Saaket | 8 | 16 | 7.0 | 0.88 |
| US29 | Harshita | 8 | 16 | 9.5 | 1.19 |
| US31 | Harshita | 8 | 16 | 9.5 | 1.19 |
| | | **75** | **150** | **87.5** | **1.17** |

### Per sprint

| | Points closed | Hours | h/point |
|---|---|---|---|
| Sprint 1, all 12 stories | 56 | 66.0 | 1.18 |
| Sprint 2, 4 of 12 stories | 19 | 21.5 | 1.13 |

The 2 h/point rate set at planning is wrong by roughly 70%, and it has been
wrong in the same direction every time. Four more stories have not moved the
overall figure: 87.5 / 75 is **1.17 h/point**, which is what nine stories said
and what twelve said. The rate agreed at the Sprint 1 retrospective for forward
planning was 1.2.

### The fixed-cost conclusion from the Sprint 1 review does not hold at sixteen stories

Recorded because it was written into the retrospective as a finding and the data
has since contradicted it. Refitting the group means as before:

```
3-point stories   mean 3.86 h   (7 stories: 2.5, 2.5, 3.5, 3.5, 5.0, 5.0, 5.0)
5-point stories   mean 5.75 h   (6 stories: 4.5, 6.0, 6.0, 6.0, 6.0, 6.0)
8-point stories   mean 8.67 h   (3 stories: 7.0, 9.5, 9.5)

        hours  =  0.97  +  0.96 x points
```

| Stories available | Fitted model | Fixed cost per story |
|---|---|---|
| 9 | `3.0 + 0.5 x points` | 3.0 h |
| 12 | `1.8 + 0.81 x points` | 1.8 h |
| 16 | `0.97 + 0.96 x points` | **0.97 h** |

The fixed component has fallen by a factor of three across three refits while the
variable component has risen toward the flat rate of 1.17. The Sprint 1 review
concluded that "roughly three hours of every story is fixed cost and has nothing
to do with the function"; **that was an artefact of nine data points.** Only one
eight-point story had closed, so the slope was estimated from a single
observation and came out too shallow. US29 and US31 at 9.5 hours each doubled
the eight-point sample and the slope nearly doubled with it.

The decision to keep a flat rate rather than adopt the two-parameter model was
therefore right, and for a stronger reason than the one given at the time: the
model was not stable enough to re-derive planned figures from.

### The Sprint 2 estimation action, checked against the four stories it covered

The action agreed at the Sprint 1 retrospective, owned by Gunjan: name for each
story the merged function it most resembles, and let that inform the estimate.
Applied at the day-1 stand-up on 24 November, before the work was done.

| Story | Compared to | Predicted | Actual | |
|---|---|---|---|---|
| US04 `comment_ratio_percent` | US02 `count_leading_spaces`, 5.0 h | cheaper than 5.0 | **3.5** | correct |
| US14 `parameter_count_rating` | US30 `grade_band`, 3.5 h | close to 3.5 | **6.0** | **wrong, +71%** |
| US22 `rule_params` | US20 `rule_nesting`, 2.5 h | at or below 2.5 | **2.5** | correct |
| US31 `compare_scores` | nothing merged; first to classify a change | high, like US29's 9.5 | **9.5** | correct |

Three of four. US14 was compared to `grade_band` because both are banding
functions with thresholds, which is a sound comparison of shape - but
`grade_band` is a three-point story and US14 a five-pointer, so the prediction
imported an hours figure from a story of a different size. US14 landed on 6.0,
which is what five of the six five-point stories in this project have cost.

**When the analogy and the point value disagreed, the point value won.**
`grade_band` at 1.17 h/point against US14's actual 1.20 would have been nearly
exact, so the analogy is useful expressed in h/point and misleading expressed in
hours. For the Sprint 2 retrospective to confirm.

### Within-size spread

The second half of the action was to check the hours-per-point spread within each
point value, where Sprint 1's three-point stories ranged 2.5 to 5.0 - a factor of
two for stories estimated identically.

| Point value | Sprint 1 range | Sprint 2 range so far |
|---|---|---|
| 3 | 2.5 - 5.0, factor **2.0** | 2.5 - 3.5, factor **1.4** |
| 5 | 4.5 - 6.0, factor 1.33 | 6.0, one story |
| 8 | 7.0 - 9.5, factor 1.36 | 9.5, one story |

Two stories is far too few to claim the narrowing as an effect. It is written
down now so that the comparison at the Sprint 2 retrospective is against a
recorded figure rather than a memory.

### A caution about these figures

The hours above were collected from the team's own records rather than timed with
a stopwatch, and the first four Sprint 1 figures were written down on 12
November, a day after those stories closed, rather than the same day. Actual Cost
in earned value management is always self-reported - every timesheet in every
project is - so this is the normal basis for the measure rather than a weakness
in it. But the figures are accurate to the half hour at best, and most of the
conclusions above are drawn at a scale where that does not matter: a 70% error in
the planning rate is not an artefact of rounding to 30 minutes.

**One is not**, and is flagged accordingly: the narrowing of the three-point
spread from a factor of 2.0 to 1.4 rests on two stories half an hour apart. It is
an observation to check, not a result.

Sprint 2's figures were logged at the point of work rather than reconstructed
afterwards, and every remaining story is logged the same way.
