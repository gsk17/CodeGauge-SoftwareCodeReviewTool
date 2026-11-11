# Earned Value Management

Project: CodeGauge - CO7095 project #17, Software Code Review Tool

## 1. The value unit

Story points are the unit of work; **person-hours** are the unit of value, converted at the
team's agreed rate of **1 story point = 2 person-hours**. That rate was set at the Sprint 1
planning session from the planning-poker reference story (US01 `classify_line`, 3 points,
estimated at 6 person-hours including its tests).

A notional labour rate of £15/hour is also carried so that the figures can be read in
money, as the rubric asks for cost. It changes nothing in the ratios: CPI and SPI are
dimensionless.

| Quantity | Value |
|---|---|
| Total story points | 196 |
| Hours per story point | 2 |
| **Budget at Completion (BAC)** | **392 person-hours (£5,880)** |
| Sprint 1 planned points | 56 → 112 h |
| Sprint 2 planned points | 63 → 126 h |
| Sprint 3 planned points | 77 → 154 h |

## 2. The formulas

| Measure | Formula | Meaning |
|---|---|---|
| PV — Planned Value | planned points to date x 2 h | what we said we would have done by now |
| EV — Earned Value | completed points to date x 2 h | what we have actually finished, valued at plan |
| AC — Actual Cost | person-hours actually logged | what it actually took |
| CV — Cost Variance | `EV - AC` | negative means over budget |
| SV — Schedule Variance | `EV - PV` | negative means behind schedule |
| CPI — Cost Performance Index | `EV / AC` | below 1.0 means over budget |
| SPI — Schedule Performance Index | `EV / PV` | below 1.0 means behind schedule |
| EAC — Estimate at Completion | `BAC / CPI` | what the whole project will cost at this efficiency |
| ETC — Estimate to Complete | `EAC - AC` | what remains to be spent |
| VAC — Variance at Completion | `BAC - EAC` | expected overspend at the end |
| TCPI — To-Complete Performance Index | `(BAC - EV) / (BAC - AC)` | the efficiency needed from here to hit BAC |

## 3. Baseline — planned value curve

Cumulative PV at each sprint boundary. This is the S-curve the burndown and the EVM table
are measured against, baselined at Sprint 1 planning and **not** re-baselined afterwards.

| Date | Milestone | Points planned (cum.) | PV (h, cum.) | PV (£, cum.) |
|---|---|---|---|---|
| 8 Nov 2026 | Sprint 0 complete | 0 | 0 | 0 |
| 22 Nov 2026 | Sprint 1 complete | 56 | 112 | 1,680 |
| 6 Dec 2026 | Sprint 2 complete | 119 | 238 | 3,570 |
| 20 Dec 2026 | Sprint 3 complete | 196 | 392 | 5,880 |

## 4. Measurement table

**How to fill this in.** At each sprint review: count the points of the user stories whose
issues are *closed* (partially-done stories earn nothing — the 0/100 rule, which keeps the
measurement honest), multiply by 2 for EV, and total each member's logged hours for AC. Log
hours in the GitHub issue as a comment so the figure is evidenced rather than remembered.

| Sprint | PV (h) | EV (h) | AC (h) | CV | SV | CPI | SPI | EAC (h) | VAC (h) |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 112 | _ | _ | _ | _ | _ | _ | _ | _ |
| 2 | 238 | _ | _ | _ | _ | _ | _ | _ | _ |
| 3 | 392 | _ | _ | _ | _ | _ | _ | _ | _ |

### Worked example — the arithmetic to copy, with illustrative Sprint 1 figures

Suppose at the Sprint 1 review 58 of the 64 planned points are closed and the team has
logged 140 hours:

```
PV   = 64 x 2                    = 128 h
EV   = 58 x 2                    = 116 h
AC   =                             140 h
CV   = EV - AC = 116 - 140       = -24 h      (over budget by 24 h)
SV   = EV - PV = 116 - 128       = -12 h      (behind schedule by 12 h)
CPI  = EV / AC = 116 / 140       = 0.829      (getting 0.83 h of value per hour spent)
SPI  = EV / PV = 116 / 128       = 0.906      (running at 91% of planned pace)
EAC  = BAC / CPI = 384 / 0.829   = 463 h      (projected total at this efficiency)
ETC  = EAC - AC = 463 - 140      = 323 h
VAC  = BAC - EAC = 384 - 463     = -79 h      (projected 79 h overspend)
TCPI = (BAC - EV) / (BAC - AC)
     = (384 - 116) / (384 - 140) = 1.098      (must run 10% more efficiently from here)
```

**Reading it.** CPI 0.83 with SPI 0.91 is the signature of *underestimation*, not of poor
execution: the team is delivering nearly to pace but each point is costing 20% more than
the 2-hour rate assumed. The correct response is to recalibrate the hours-per-point rate
for Sprints 2 and 3 rather than to ask for more hours, and to note that TCPI of 1.10 is
achievable, whereas a TCPI above about 1.25 would mean the plan, not the effort, has to
change.

These figures are illustrative. Replace them with the real counts at each sprint review and
keep the arithmetic lines, because the rubric rewards the shown calculation as much as the
result.
