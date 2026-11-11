# Sprint 2 Review

**Date:** `<the last day of the sprint>`
**Attending:** Gunjan, Kasam, Saaket, Harshita

The sprint review inspects the **increment**: what was actually built, demonstrated
against the Definition of Done. It is not a status meeting - a story is either
demonstrated working or it is not Done.

## 1. Sprint goal

> `<paste the goal from sprint-2-backlog.md>`

Met in full / met in part / not met: `<which, and why>`

## 2. Increment demonstrated

Run the tests and the tool in front of the team. For each story, state the function
and show its tests passing.

| ID | Owner | Done? | Demonstrated | Notes |
|---|---|---|---|---|
| | | | | |

## 3. Stories not Done

| ID | Owner | Points | What is missing | Carried to |
|---|---|---|---|---|
| | | | | |

Points for a carried story are earned in the sprint it closes in, not this one.

## 4. Measurement

| Measure | Value | How it was obtained |
|---|---|---|
| Committed points | | sprint-2-backlog.md |
| Completed points (velocity) | | closed issues |
| Carried over | | |
| Tests passing | | `python -m pytest -v` |
| Statement coverage | | `python -m coverage report -m` |
| PV / EV / AC | | docs/measurement/evm.md |
| CPI / SPI | | docs/measurement/evm.md |

Burndown for the sprint: `python docs/measurement/scripts/burndown.py 2`

## 5. Increment tagged

```bash
git tag -a v0.2.0 -m "Sprint 2 increment"
git push origin v0.2.0
```

## 6. Board screenshot

Saved to `docs/measurement/board-sprint2.png`, showing the stories in this sprint,
their owners, and their start and end dates.
