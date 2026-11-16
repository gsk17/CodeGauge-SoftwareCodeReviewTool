"""Plot a sprint burndown chart from docs/measurement/burndown-data.csv.

The CSV is written by scripts/daily_scrum.sh at each stand-up, so the chart is a
record of what actually happened rather than a line drawn at the end of the
sprint.

    python docs/measurement/scripts/burndown.py 1

Always prints an ASCII chart, which is enough for the terminal and for the
video. Also writes a PNG for the report if matplotlib happens to be installed -
matplotlib is not a project dependency, and nothing under core/, cli/ or model/
may import it.
"""

import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
MEASUREMENT = os.path.dirname(HERE)
DATA = os.path.join(MEASUREMENT, "burndown-data.csv")

# Committed points per sprint, from the sprint backlogs.
COMMITTED = {"1": 56, "2": 63, "3": 77}
WORKING_DAYS = 10


def read_sprint(sprint):
    """Return the (date, remaining) rows for one sprint, in date order."""
    if not os.path.isfile(DATA):
        return []
    rows = []
    with open(DATA, newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["sprint"] == sprint:
                rows.append((row["date"], int(row["remaining_points"])))
    rows.sort()
    return rows


def ideal_line(committed):
    """The ideal remaining on each of the working days, including day 0."""
    step = committed / float(WORKING_DAYS)
    return [committed - day * step for day in range(WORKING_DAYS + 1)]


def ascii_chart(sprint, rows, committed):
    """Render the burndown as an ASCII chart, ideal against actual."""
    height = 16
    ideal = ideal_line(committed)
    lines = []
    lines.append("Sprint %s burndown - %d points committed, %d days reported"
                 % (sprint, committed, len(rows)))
    lines.append("")

    for level in range(height, -1, -1):
        value = committed * level / float(height)
        row = "%4d |" % round(value)
        for day in range(WORKING_DAYS + 1):
            cell = " "
            if abs(ideal[day] - value) <= committed / (2.0 * height):
                cell = "."                      # the ideal line
            if day < len(rows):
                actual = rows[day][1]
                if abs(actual - value) <= committed / (2.0 * height):
                    cell = "#"                  # the actual line wins the cell
            row = row + " " + cell
        lines.append(row)

    lines.append("     +" + "--" * (WORKING_DAYS + 1))
    lines.append("      " + "".join(" %d" % (day % 10) for day in range(WORKING_DAYS + 1)))
    lines.append("      working day of the sprint")
    lines.append("")
    lines.append("      . ideal     # actual")
    return "\n".join(lines)


def write_png(sprint, rows, committed):
    """Write a PNG of the same chart if matplotlib is available."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return None

    ideal = ideal_line(committed)
    days = list(range(len(ideal)))
    plt.figure(figsize=(8, 5))
    plt.plot(days, ideal, linestyle="--", marker="", label="Ideal")
    if rows:
        plt.plot(list(range(len(rows))), [remaining for _, remaining in rows],
                 marker="o", label="Actual")
    plt.title("Sprint %s burndown" % sprint)
    plt.xlabel("Working day of the sprint")
    plt.ylabel("Story points remaining")
    plt.xticks(days)
    plt.ylim(0, committed + 2)
    plt.grid(True, alpha=0.3)
    plt.legend()
    path = os.path.join(MEASUREMENT, "burndown-sprint%s.png" % sprint)
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    return path


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in COMMITTED:
        print("Usage: python docs/measurement/scripts/burndown.py <1|2|3>")
        return 1

    sprint = sys.argv[1]
    committed = COMMITTED[sprint]
    rows = read_sprint(sprint)

    if not rows:
        print("No burndown data for sprint %s yet." % sprint)
        print("Record it at each stand-up with:")
        print("  bash scripts/daily_scrum.sh --sprint %s --member <name> "
              "--remaining <points>" % sprint)
        return 0

    print(ascii_chart(sprint, rows, committed))
    print()
    print("| Day | Date | Ideal remaining | Actual remaining | Variance |")
    print("|---|---|---|---|---|")
    ideal = ideal_line(committed)
    for day, (when, remaining) in enumerate(rows):
        expected = ideal[day] if day < len(ideal) else 0.0
        print("| %d | %s | %.1f | %d | %+.1f |"
              % (day, when, expected, remaining, remaining - expected))

    png = write_png(sprint, rows, committed)
    if png:
        print()
        print("Wrote %s" % os.path.relpath(png, os.path.dirname(MEASUREMENT)))
    else:
        print()
        print("matplotlib is not installed, so no PNG was written. The ASCII chart and")
        print("the table above are enough for the video; for the report either install")
        print("matplotlib (python -m pip install --user matplotlib) or paste the table")
        print("into a spreadsheet and insert a line chart.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
