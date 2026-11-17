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
| US07 | Gunjan | `is_function_header` | 3 | 6 |  |  |
| US10 ✅ | Kasam | `decision_points` | 5 | 10 | **6.0** | branch initially cut from the US01 branch rather than main; resolved by merging US01 first |
| US12 ✅ | Kasam | `max_nesting_depth` | 5 | 10 | **6.0** | two sequential loops; the analysis found three single-solution path conditions |
| US20 | Kasam | `rule_nesting` | 3 | 6 |  |  |
| US11 ✅ | Saaket | `cyclomatic_complexity` | 8 | 16 | **7.0** | tests written 12 Nov, finished in an unplanned Sunday session on 15 Nov to recover the lost Friday |
| US19 ✅ | Saaket | `rule_complexity` | 5 | 10 | **4.5** | cheapest of the five-pointers; `classify_severity` did the banding, so the rule is nine lines |
| US26 ✅ | Saaket | `classify_severity` | 5 | 10 | **6.0** | dependency root - every rule story calls it, so taken first |
| US28 ✅ | Harshita | `weighted_penalty` | 5 | 10 | **6.0** | implementation waited on US26 merging for the severity constants |
| US29 | Harshita | `score_from_issues` | 8 | 16 |  |  |
| US30 ✅ | Harshita | `grade_band` | 3 | 6 | **3.5** | cheapest story so far; no dependencies and the bands were already agreed |
| | | **Closed so far** | **42** | **84** | **49.0** | 9 of 12 stories. CPI 84 / 49.0 = **1.71** |
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
| Closed | 42 | 84 | 49.0 | **1.71** |
| Remaining | 154 | 308 | — | — |
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

**Nine stories closed: 49.0 hours against an 84 hour budget, a CPI of 1.71.**

Nine data points is enough to stop calling this noise. The 2 h/point rate set at
planning is wrong by roughly 70%, and it has been wrong in the same direction
every single time.

| Story | Points | Budget (h) | Actual (h) | h/point |
|---|---|---|---|---|
| US30 | 3 | 6 | 3.5 | 1.17 |
| US01 | 3 | 6 | 5.0 | 1.67 |
| US02 | 3 | 6 | 5.0 | 1.67 |
| US19 | 5 | 10 | 4.5 | 0.90 |
| US10 | 5 | 10 | 6.0 | 1.20 |
| US12 | 5 | 10 | 6.0 | 1.20 |
| US26 | 5 | 10 | 6.0 | 1.20 |
| US28 | 5 | 10 | 6.0 | 1.20 |
| US11 | 8 | 16 | 7.0 | 0.88 |

### What the data actually says

Two things stand out, and the second is the useful one.

**Hours vary far less than points do.** The points range from 3 to 8, a factor
of 2.7. The hours range from 3.5 to 7.0, a factor of 2.0. A story worth nearly
three times as much does not take anywhere near three times as long.

**Four of the five 5-point stories cost exactly 6.0 hours.** US10, US12, US26
and US28 are different functions, written by three different people, in three
different modules — and they landed on the same figure. That is not people
rounding to a convenient number; it is the per-story process costing the same
every time regardless of what the function does.

### A better model than a flat rate

Fitting the group means to a straight line:

```
3-point stories   mean 4.5 h   (US30 3.5, US01 5.0, US02 5.0)
5-point stories   mean 5.7 h   (US19 4.5, four others at 6.0)
8-point story          7.0 h   (US11)

slope  b = (7.0 - 4.5) / (8 - 3) = 2.5 / 5 = 0.5 h per point
fixed  a = 4.5 - (3 x 0.5)      = 4.5 - 1.5 = 3.0 h per story

        hours  =  3.0  +  0.5 x points
```

Checked against the 5-point group: `3.0 + 0.5 x 5 = 5.5`, against an observed
mean of 5.7. Within 0.2 hours.

**So roughly three hours of every story is fixed cost and has nothing to do with
the function.** Branch, two black-box packages, three white-box packages, the
symbolic write-up, the pull request, the review — that is the same work whether
the function is four lines or twenty. Only about half an hour per story point is
the function itself.

That is why h/point *falls* as stories get bigger: a fixed cost divided by a
growing denominator. US11 is the clearest case — 8 points, the largest story
closed, and the lowest h/point of all nine at 0.88.

### What this means for the estimate

| Model | Arithmetic | Project total |
|---|---|---|
| Planning rate, 2.0 h/point | 196 x 2.0 | **392 h** |
| Observed flat rate | 49.0 / 42 = 1.17 h/point; 196 x 1.17 | **229 h** |
| Fixed + variable | 36 x 3.0 + 196 x 0.5 = 108 + 98 | **206 h** |
| Forward estimate in `time-full.md` | independent pass over all 36 stories | **243.5 h** |

Three independent routes land between 206 and 244 hours. The planning figure of
392 is not in that range and is not close to it.

### Decision for the Sprint 1 review

**Recalibrate to 1.2 h/point**, giving a BAC of **235 hours** and a CPI of
`84 / 49.0 / 1.667 = 1.03`.

The fixed-plus-variable model is the better description of reality and belongs
in the retrospective as the finding. It is *not* proposed as the planning rate,
for one reason: a flat rate per point is what the backlog, the sprint
commitments and the burndown are all built on, and changing to a two-parameter
model would mean re-deriving every planned figure in the project for an
improvement of about 25 hours on a 230-hour estimate. The flat rate of 1.2 sits
between the observed 1.17 and the forward estimate's 1.24, and is close enough
to both.

**Record the reasoning either way in `sprint-1-retrospective.md`.** A rate left
wrong once it is known to be wrong is worse than one that was never checked —
and the fixed-cost finding is worth more marks than the recalibration itself,
because it explains *why* the original estimate failed rather than just
correcting it.

### A caution about these figures

The nine hours figures above were collected from the team's own records rather
than timed with a stopwatch, and the first four were written down on 12
November, a day after those stories closed, rather than the same day. Actual
Cost in earned value management is always self-reported — every timesheet in
every project is — so this is the normal basis for the measure rather than a
weakness in it. But the figures are accurate to the half hour at best, and the
conclusions above are drawn at a scale where that does not matter: a 70% error
in the planning rate is not an artefact of rounding to 30 minutes.

Every remaining story is logged at the point of work, not reconstructed
afterwards.
