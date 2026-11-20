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

### Sprint 1 — measured, 22 November 2026

| Sprint | PV (h) | EV (h) | AC (h) | CV | SV | CPI | SPI | EAC (h) | VAC (h) |
|---|---|---|---|---|---|---|---|---|---|
| **1** | **112** | **112** | **66.0** | **+46.0** | **0.0** | **1.70** | **1.00** | **231** | **+161** |
| 2 | 238 | _ | _ | _ | _ | _ | _ | _ | _ |
| 3 | 392 | _ | _ | _ | _ | _ | _ | _ | _ |

**The arithmetic, shown.** All twelve Sprint 1 stories closed, so EV is the full
planned value of the sprint.

```
PV    = 56 planned points x 2 h                      = 112 h
EV    = 56 completed points x 2 h                    = 112 h
AC    = sum of the Actual column in time-log.md      =  66.0 h

CV    = EV - AC   = 112 - 66.0                       = +46.0 h   (under budget)
SV    = EV - PV   = 112 - 112                        =   0.0 h   (exactly on schedule)
CPI   = EV / AC   = 112 / 66.0                       =  1.697 -> 1.70
SPI   = EV / PV   = 112 / 112                        =  1.00

EAC   = BAC / CPI = 392 / 1.697                      = 231.0 h
ETC   = EAC - AC  = 231.0 - 66.0                     = 165.0 h
VAC   = BAC - EAC = 392 - 231.0                      = +161.0 h  (expected underspend)
TCPI  = (BAC - EV) / (BAC - AC) = 280 / 326          =  0.859
```

In money, at the notional £15/hour: EV £1,680, AC £990, **CV +£690**, EAC
£3,465 against a BAC of £5,880.

### What the pair of indices says

**SPI exactly 1.00 with CPI 1.70** is the cleanest reading EVM can give. The
sprint delivered precisely what it committed, on the day it committed to, using
**40% fewer hours than budgeted**.

That combination has one interpretation and it is not "the team is fast": the
schedule was met, so capacity was not the constraint, and the hours came in far
under, so **the rate was wrong**. CPI above 1.5 means the estimate was far too
generous, which is what `time-log.md` says at length — the 2 h/point rate was
set from a single reference story before any story had been built.

An SPI of exactly 1.00 is also worth not over-reading. It is 1.00 because every
committed story closed, not because the work tracked the plan day by day. The
burndown was 4.4 points *behind* on 13 November and 8.4 points *ahead* on 17
November. SPI measured at a sprint boundary cannot see either.

**TCPI of 0.859** is the figure that makes the baseline problem concrete: to
spend exactly the remaining budget, the team would have to become **15% less
efficient** than it has been. A TCPI below 1 means the baseline has more room in
it than the work needs.

### The baseline is deliberately not re-cut

The 2 h/point rate is wrong by roughly 70%, and it is **not** being changed.

| | Re-baseline to ~1.2 h/point | Hold the baseline |
|---|---|---|
| BAC | 235 h | **392 h** |
| CPI | ~1.03 | **1.70** |
| Comparability across sprints | **lost** | kept |
| What the forecast says | 228 h | **EAC 231 h** |

Three reasons for holding it:

1. **A baseline is frozen by definition.** Re-cutting it mid-project means
   Sprint 1 is measured against one baseline and Sprint 2 against another, and
   the variance between sprints — the thing being measured — stops meaning
   anything. Section 3 of this document already states the baseline is not
   re-baselined; honouring that is the point of having written it.
2. **`EAC = BAC / CPI` already applies the correction.** It gives 231 hours
   without a single figure being edited. That is what the forecast formula is
   *for*: the baseline records what was planned, EAC records what it will
   actually cost, and the gap between them is the finding rather than an error
   to be tidied away.
3. **A CPI of 1.70 with an explanation is worth more than a CPI of 1.03 with
   none.** The marks here are for what the measurement told us and what we
   changed, and "we found the rate was 70% generous, held the baseline so the
   sprints stay comparable, and re-planned forward at 1.2" is a decision. A
   baseline quietly adjusted until the index reads 1.00 is the absence of one.

**The revised rate of 1.2 h/point is adopted for forward planning of Sprints 2
and 3 only.** It sits between the observed 1.18 (66.0 / 56) and the independent
forward estimate's 1.24.

### The underlying cause is reuse, not a flat rate

The retrospective sets this out in full; the figure that matters to EVM is that
**hours are not proportional to points**:

| Story | Points | Hours | h/point |
|---|---|---|---|
| US20 `rule_nesting` | 3 | **2.5** | 0.83 |
| US02 `count_leading_spaces` | 3 | **5.0** | 1.67 |
| US29 `score_from_issues` | 8 | 9.5 | 1.19 |
| US11 `cyclomatic_complexity` | 8 | 7.0 | 0.88 |

US20 cost **half** what US02 cost for the same three points, because US19 had
already settled the rule shape, the delegation to `classify_severity`, the code
constant and the message format. US29 was expensive because nothing preceded it.

So a single hours-per-point rate — any rate — will mis-estimate individual
stories even when it gets the sprint total close. For EVM at sprint granularity
that is acceptable, because the errors offset: four of the five 5-point stories
landed at exactly 6.0 hours. For estimating a *single* story it is not, and
Sprint 2 planning should name, for each story, the merged function it most
resembles.

### Capacity, which EVM does not measure and should

EVM compares cost against budget. It says nothing about whether the hours are
*available*. `cocomo.md` puts the team at **192 person-hours** across the
project — four members at roughly 8 hours each per week over six weeks.

| Sprint | Points | Hours implied at 1.18 | Available | h/person/week |
|---|---|---|---|---|
| 1 | 56 | **66.0 actual** | 64 | 8.3 |
| 2 | 63 | 74.3 | 64 | 9.3 |
| 3 | 77 | 90.9 | 64 | **11.4** |
| **Total** | **196** | **231** | **192** | |

**Sprint 1 landed on the 8-hour assumption almost exactly**, which validates the
rate. It also means the EAC of 231 hours — comfortably under a BAC of 392 — is
still **20% more than the team has**. A healthy CPI and a healthy VAC can
coexist with a schedule that cannot be staffed, and this is the case where they
do.

That is the limitation of EVM on this project stated plainly: it is measuring
against a budget nobody is constrained by, while the real constraint is
calendar time in the two weeks before Christmas. The decision belongs to the
Sprint 1 retrospective, which sets out three options.

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
