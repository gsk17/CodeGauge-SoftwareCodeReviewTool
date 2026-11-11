# Burndown Charts and Velocity

Project: CodeGauge - CO7095 project #17, Software Code Review Tool

Burndown must be recorded **daily, as the sprint runs**. A chart reconstructed at the end of
a sprint is visible in the commit history of this file, and the rubric asks for evidence.

**The data is recorded at the daily scrum, not here.** At each stand-up:

```bash
bash scripts/daily_scrum.sh --sprint 1 --member gunjan      --did "US01 failing tests written" --next "US01 implement"      --blocked none --remaining 61
```

That appends the three daily-scrum answers to `docs/scrum/daily-scrum-log.md` and the
remaining-points figure to `docs/measurement/burndown-data.csv`. Commit both the same day,
so the commit date matches the day being recorded. The script refuses a future date.

To draw the chart and fill the tables below:

```bash
python docs/measurement/scripts/burndown.py 1
```

It prints an ASCII chart and a Day/Date/Ideal/Actual/Variance table, and writes
`burndown-sprint<N>.png` if matplotlib is installed.

## 1. How the ideal line is computed

A sprint of P points over D working days burns `P / D` points per day. The ideal remaining
on day *n* is `P - n x (P / D)`. Sprint 1 is 56 points over 10 working days, so the ideal
burn is 5.6 points per day.

## 2. Sprint 1 — 9 to 22 November 2026, 56 points

| Day | Date | Ideal remaining | Actual remaining | Closed that day | Note |
|---|---|---|---|---|---|
| 0 | Mon 9 Nov | 56.0 | 56 | — | sprint planning |
| 1 | Tue 10 Nov | 50.4 | 56 | — | US01 started; three members awaiting repo access |
| 2 | Wed 11 Nov | 44.8 | 38 | US01 US10 US26 US28 | four stories merged, one per member |
| 3 | Thu 12 Nov | 39.2 | _ | _ | |
| 4 | Fri 13 Nov | 33.6 | _ | _ | |
| 5 | Mon 16 Nov | 28.0 | _ | _ | |
| 6 | Tue 17 Nov | 22.4 | _ | _ | |
| 7 | Wed 18 Nov | 16.8 | _ | _ | |
| 8 | Thu 19 Nov | 11.2 | _ | _ | |
| 9 | Fri 20 Nov | 5.6 | _ | _ | |
| 10 | Sun 22 Nov | 0.0 | _ | _ | sprint review and retrospective |

## 3. Sprint 2 — 23 November to 6 December 2026, 58 points

Ideal burn 5.8 points per day.

| Day | Date | Ideal remaining | Actual remaining | Closed that day | Note |
|---|---|---|---|---|---|
| 0 | Mon 23 Nov | 58.0 | 58 | — | sprint planning |
| 1 | Tue 24 Nov | 52.2 | _ | _ | |
| 2 | Wed 25 Nov | 46.4 | _ | _ | |
| 3 | Thu 26 Nov | 40.6 | _ | _ | |
| 4 | Fri 27 Nov | 34.8 | _ | _ | |
| 5 | Mon 30 Nov | 29.0 | _ | _ | |
| 6 | Tue 1 Dec | 23.2 | _ | _ | |
| 7 | Wed 2 Dec | 17.4 | _ | _ | |
| 8 | Thu 3 Dec | 11.6 | _ | _ | |
| 9 | Fri 4 Dec | 5.8 | _ | _ | |
| 10 | Sun 6 Dec | 0.0 | _ | _ | sprint review and retrospective |

## 4. Sprint 3 — 7 to 20 December 2026, 72 points

Ideal burn 7.2 points per day.

| Day | Date | Ideal remaining | Actual remaining | Closed that day | Note |
|---|---|---|---|---|---|
| 0 | Mon 7 Dec | 72.0 | 72 | — | sprint planning |
| 1 | Tue 8 Dec | 64.8 | _ | _ | |
| 2 | Wed 9 Dec | 57.6 | _ | _ | |
| 3 | Thu 10 Dec | 50.4 | _ | _ | |
| 4 | Fri 11 Dec | 43.2 | _ | _ | |
| 5 | Mon 14 Dec | 36.0 | _ | _ | |
| 6 | Tue 15 Dec | 28.8 | _ | _ | |
| 7 | Wed 16 Dec | 21.6 | _ | _ | |
| 8 | Thu 17 Dec | 14.4 | _ | _ | |
| 9 | Fri 18 Dec | 7.2 | _ | _ | |
| 10 | Sun 20 Dec | 0.0 | _ | _ | sprint review and retrospective |

## 5. Velocity

Velocity is points **closed** per sprint — the measure used to forecast the next sprint's
capacity. The 0/100 rule applies: a story carried over earns its points in the sprint it
closes in, not the one it started in.

| Sprint | Committed | Completed | Carried over | Velocity |
|---|---|---|---|---|
| 1 | 56 | _ | _ | _ |
| 2 | 58 | _ | _ | _ |
| 3 | 65 | _ | _ | _ |
| **Average** | **62** | **_** | | **_** |

**Per-member completion**, which is the figure the individual marks depend on — every member
must finish all nine of their stories:

| Member | Sprint 1 | Sprint 2 | Sprint 3 | Total (target 48) |
|---|---|---|---|---|
| Gunjan (M1, scanner) | 3/9 | /11 | /26 | 3/46 |
| Kasam (M2, complexity) | 5/13 | /16 | /21 | 5/50 |
| Saaket (M3, rules) | 5/18 | /13 | /14 | 5/45 |
| Harshita (M4, scoring) | 5/16 | /18 | /11 | 5/45 |

## 6. Plotting the charts for the report and the video

The numbers above are the evidence; the chart is the presentation. Either is acceptable to
produce it:

- **PyCharm / Python**: a short `matplotlib` script reading these tables. Note that
  `matplotlib` must not be imported by any file in `core/`, `cli/` or `model/` — the runtime
  is standard library only. Keep any plotting script in `docs/measurement/scripts/`.
- **Spreadsheet**: paste the Day / Ideal / Actual columns into Excel or Google Sheets and
  insert a line chart. Export as PNG into `docs/measurement/` and reference it from the
  report.

Plot the ideal line and the actual line on the same axes, with days on x and remaining
points on y, and keep one chart per sprint as the rubric asks for "Burndown Chart for every
sprint".
