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

> **Status:** the Actual column is filled in only for stories that have closed. Rows for
> work not yet started are deliberately blank — an hours figure against an unstarted story
> would be a guess, and CPI computed from guesses is not a measurement.

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
| US02 | Gunjan | `count_leading_spaces` | 3 | 6 |  |  |
| US07 | Gunjan | `is_function_header` | 3 | 6 |  |  |
| US10 ✅ | Kasam | `decision_points` | 5 | 10 | **6.0** | branch initially cut from the US01 branch rather than main; resolved by merging US01 first |
| US12 | Kasam | `max_nesting_depth` | 5 | 10 |  |  |
| US20 | Kasam | `rule_nesting` | 3 | 6 |  |  |
| US11 | Saaket | `cyclomatic_complexity` | 8 | 16 |  |  |
| US19 | Saaket | `rule_complexity` | 5 | 10 |  |  |
| US26 ✅ | Saaket | `classify_severity` | 5 | 10 | **6.0** | dependency root - every rule story calls it, so taken first |
| US28 ✅ | Harshita | `weighted_penalty` | 5 | 10 | **6.0** | implementation waited on US26 merging for the severity constants |
| US29 | Harshita | `score_from_issues` | 8 | 16 |  |  |
| US30 | Harshita | `grade_band` | 3 | 6 |  |  |
| | | **Closed so far** | **18** | **36** | **23.0** | 4 of 12 stories. CPI 36 / 23.0 = **1.57** |
| | | **Sprint committed** | **56** | **112** | | |

### Sprint 2 — 63 points, 126 hours budgeted

| ID | Owner | Function | Points | Budget (h) | **Actual (h)** | Notes |
|---|---|---|---|---|---|---|
| US03 | Gunjan | `depth_from_indent` | 3 | 6 |  |  |
| US04 | Gunjan | `comment_ratio_percent` | 3 | 6 |  |  |
| US08 | Gunjan | `count_parameters` | 5 | 10 |  |  |
| US13 | Kasam | `nesting_penalty` | 5 | 10 |  |  |
| US14 | Kasam | `parameter_count_rating` | 5 | 10 |  |  |
| US17 | Kasam | `duplicate_block_score` | 8 | 16 |  |  |
| US21 | Saaket | `rule_length` | 5 | 10 |  |  |
| US22 | Saaket | `rule_params` | 3 | 6 |  |  |
| US23 | Saaket | `rule_comment_ratio` | 5 | 10 |  |  |
| US31 | Harshita | `compare_scores` | 8 | 16 |  |  |
| US33 | Harshita | `serialise_report` | 5 | 10 |  |  |
| US34 | Harshita | `parse_record_line` | 8 | 16 |  |  |
| | | **Sprint committed** | **63** | **126** | | not started |

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
| Closed | 18 | 36 | 23.0 | **1.57** |
| Remaining | 178 | 356 | — | — |
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

## Outstanding

The four stories closed on 11 November are recorded above: **23.0 hours against a 36 hour
budget**, giving a Sprint-1-to-date CPI of **1.57**.

That is the first real signal the measurement has produced, and it says the **2 h/point
rate set at planning is too generous** — by roughly 60%. Three of the four came in at 6
hours whether they were worth 3 points or 5, which suggests the fixed overhead per story
— branch, tests, symbolic write-up, pull request, review — matters more at this size than
the story's own complexity does.

Decide at the Sprint 1 review whether to recalibrate. Lowering the rate to 1.25 h/point
would take BAC from 392 to 245 hours and bring CPI close to 1.0. Record the decision
either way in `sprint-1-retrospective.md`: a rate left wrong once it is known to be wrong
is worse than one that was never checked.

Every remaining story is logged at the point of work, not reconstructed afterwards.
