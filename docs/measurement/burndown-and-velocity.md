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
| 3 | Thu 12 Nov | 39.2 | 38 | — | US11 started; random-based black-box tests added to the four closed stories |
| 4 | Fri 13 Nov | 33.6 | 38 | — | no work on any story; US11's implementation and the planned starts for US02, US12 and US30 all slipped |
| — | Sun 15 Nov | — | 30 | US11 | unplanned weekend session to recover Friday; US11 merged, and US02, US12, US19 and US30 all started. Not a planned working day, so no ideal figure |
| 5 | Mon 16 Nov | 28.0 | 30 | — | US02, US12, US19 and US30 all implemented; none merged yet, so the 0/100 rule earns them nothing |
| 6 | Tue 17 Nov | 22.4 | 14 | US02 US12 US19 US30 | four stories merged, one per member; 16 points in a day |
| 7 | Wed 18 Nov | 16.8 | 14 | — | US07, US20 and US29 all started; the last three Sprint 1 stories, worth exactly the 14 that remain |
| 8 | Thu 19 Nov | 11.2 | 14 | — | US07, US20 and US29 all implemented; none merged, so the 0/100 rule earns them nothing |
| 9 | Fri 20 Nov | 5.6 | **0** | US07 US20 US29 | all three merged; **sprint complete, 56 of 56 points**, one working day ahead of the burn line |
| 10 | Sun 22 Nov | 0.0 | _ | _ | sprint review and retrospective |

## 3. Sprint 2 — 23 November to 6 December 2026, 63 points

Ideal burn 6.3 points per day.

| Day | Date | Ideal remaining | Actual remaining | Closed that day | Note |
|---|---|---|---|---|---|
| 0 | Mon 23 Nov | 63.0 | 63 | — | sprint planning |
| 1 | Tue 24 Nov | 56.7 | _ | _ | |
| 2 | Wed 25 Nov | 50.4 | _ | _ | |
| 3 | Thu 26 Nov | 44.1 | _ | _ | |
| 4 | Fri 27 Nov | 37.8 | _ | _ | |
| 5 | Mon 30 Nov | 31.5 | _ | _ | |
| 6 | Tue 1 Dec | 25.2 | _ | _ | |
| 7 | Wed 2 Dec | 18.9 | _ | _ | |
| 8 | Thu 3 Dec | 12.6 | _ | _ | |
| 9 | Fri 4 Dec | 6.3 | _ | _ | |
| 10 | Sun 6 Dec | 0.0 | _ | _ | sprint review and retrospective |

## 4. Sprint 3 — 7 to 20 December 2026, 77 points

Ideal burn 7.7 points per day.

| Day | Date | Ideal remaining | Actual remaining | Closed that day | Note |
|---|---|---|---|---|---|
| 0 | Mon 7 Dec | 77.0 | 77 | — | sprint planning |
| 1 | Tue 8 Dec | 69.3 | _ | _ | |
| 2 | Wed 9 Dec | 61.6 | _ | _ | |
| 3 | Thu 10 Dec | 53.9 | _ | _ | |
| 4 | Fri 11 Dec | 46.2 | _ | _ | |
| 5 | Mon 14 Dec | 38.5 | _ | _ | |
| 6 | Tue 15 Dec | 30.8 | _ | _ | |
| 7 | Wed 16 Dec | 23.1 | _ | _ | |
| 8 | Thu 17 Dec | 15.4 | _ | _ | |
| 9 | Fri 18 Dec | 7.7 | _ | _ | |
| 10 | Sun 20 Dec | 0.0 | _ | _ | sprint review and retrospective |

## 5. Velocity

Velocity is points **closed** per sprint — the measure used to forecast the next sprint's
capacity. The 0/100 rule applies: a story carried over earns its points in the sprint it
closes in, not the one it started in.

| Sprint | Committed | Completed | Carried over | Velocity |
|---|---|---|---|---|
| 1 | 56 | **56** | **0** | **56** |
| 2 | 63 | _ | _ | _ |
| 3 | 65 | _ | _ | _ |
| **Average** | **65** | **_** | | **_** |

**Per-member completion**, which is the figure the individual marks depend on — every member
must finish all nine of their stories:

| Member | Sprint 1 | Sprint 2 | Sprint 3 | Total (target 48) |
|---|---|---|---|---|
| Gunjan (M1, scanner) | **9/9** | /11 | /26 | 9/46 |
| Kasam (M2, complexity) | **13/13** | /18 | /24 | 13/55 |
| Saaket (M3, rules) | **18/18** | /13 | /16 | 18/47 |
| Harshita (M4, scoring) | **16/16** | /21 | /11 | 16/48 |

## 6. Plotting the charts for the report and the video

The numbers above are the evidence; the chart is the presentation. Either is acceptable to
produce it:

- **PyCharm / Python**: a short `matplotlib` script reading these tables. Note that
  `matplotlib` must not be imported by any file in `core/`, `cli/` or `model/` — the runtime
  is standard library only. Keep any plotting script in `docs/measurement/scripts/`.
- **Spreadsheet**: paste the Day / Ideal / Actual columns into Excel or Google Sheets and
  insert a line chart. Export as PNG into `docs/measurement/` and reference it from the
  report.

### Where the charts live

| Path | What it is |
|---|---|
| `burndown-sprint<N>.png` | **the current chart** - overwritten each time the script runs, and the one the README links to, so the README never needs editing |
| `charts/burndown-sprint<N>-<YYYY-MM-DD>.png` | **dated snapshots**, one per stand-up |

Keeping the dated copies matters for the same reason the daily commits do: a
single chart file shows only the finished sprint, and a sprint that was recorded
daily looks identical to one drawn at the end. The snapshots are the proof that
the line was plotted as the sprint ran. Copy the current chart into `charts/`
after each regeneration:

```bash
python docs/measurement/scripts/burndown.py 1
cp docs/measurement/burndown-sprint1.png docs/measurement/charts/burndown-sprint1-$(date +%F).png
```

Plot the ideal line and the actual line on the same axes, with days on x and remaining
points on y, and keep one chart per sprint as the rubric asks for "Burndown Chart for every
sprint".
