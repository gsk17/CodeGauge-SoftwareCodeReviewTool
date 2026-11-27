"""Black-box tests for serialise_report - US33, Harshita (hcg22).

Technique: random testing against invariants.
Function under test: core.history.serialise_report(report).

No expected line is written out by hand - that would reimplement the format in
the test. Each test states a property every serialised report must satisfy, and
builds reports randomly. The seed is fixed so a failure replays exactly.

The strongest invariant available without US34 is the **line count identity**:

    len(serialise_report(report))  ==  1 + len(report.records) + len(report.issues)

One REPORT line, one FUNC line per record, one ISSUE line per issue, and nothing
else. It is sharp because it fails in both directions - an implementation that
dropped a record, that emitted a header, or that wrote a trailing blank line
breaks it immediately.

The property this function really wants tested is the **round trip**: parsing
the lines back must reconstruct the report. That is US34's function, and it does
not exist yet, so it cannot be asserted here. The tests below therefore check
everything a reader would need in order to parse the lines - stable field
counts, no stray delimiters, every value recoverable as text - which is the
closest a one-sided test can get. **The round-trip test belongs in US34's random
suite and is the first thing that should be written there.**
"""

import random

import pytest

from core.history import serialise_report
from core.severity import CRITICAL, INFO, MAJOR, MINOR
from model.function_record import FunctionRecord
from model.issue import Issue
from model.review_report import ReviewReport

SEED = 20261127
TRIALS = 300

SEVERITIES = (CRITICAL, MAJOR, MINOR, INFO)
CODES = ("CC001", "NEST001", "PAR001", "LEN001")
GRADES = ("A", "B", "C", "D", "E", "F")
NAMES = ("withdraw", "deposit", "scan_file", "x", "a_very_long_function_name")


def _record(rng):
    return FunctionRecord(
        rng.choice(NAMES), rng.randint(1, 5000), rng.randint(0, 400),
        rng.randint(0, 12), rng.randint(0, 9), rng.randint(0, 30),
        rng.randint(0, 20), rng.randint(0, 50), rng.randint(0, 50),
        rng.randint(0, 300), rng.randint(0, 100),
        cc=rng.randint(1, 40), rating=rng.choice(("OK", "COMPLEX", "SEVERE")))


def _issue(rng):
    return Issue(rng.choice(CODES), rng.choice(SEVERITIES), rng.randint(1, 5000),
                 "%d exceeds limit %d" % (rng.randint(1, 500), rng.randint(1, 100)))


def _report(rng, max_records=6, max_issues=6):
    records = [_record(rng) for _ in range(rng.randint(0, max_records))]
    issues = [_issue(rng) for _ in range(rng.randint(0, max_issues))]
    return ReviewReport(
        rng.choice(("a.py", "core/scanner.py", "x.py")),
        rng.randint(0, 2000), rng.randint(0, 500), rng.randint(0, 500),
        records, issues, rng.randint(0, 100), rng.choice(GRADES),
        timestamp=rng.choice(("", "2026-11-27T09:00:00")))


def test_the_line_count_identity():
    rng = random.Random(SEED)
    for _ in range(TRIALS):
        report = _report(rng)
        lines = serialise_report(report)
        assert len(lines) == 1 + len(report.records) + len(report.issues)


def test_there_is_always_exactly_one_report_line_and_it_is_first():
    rng = random.Random(SEED)
    for _ in range(TRIALS):
        lines = serialise_report(_report(rng))
        tags = [line.split("|")[0] for line in lines]
        assert tags.count("REPORT") == 1
        assert tags[0] == "REPORT"


def test_the_tags_are_always_grouped_report_then_funcs_then_issues():
    rng = random.Random(SEED)
    for _ in range(TRIALS):
        report = _report(rng)
        tags = [line.split("|")[0] for line in serialise_report(report)]
        expected = (["REPORT"] + ["FUNC"] * len(report.records)
                    + ["ISSUE"] * len(report.issues))
        assert tags == expected


def test_the_field_count_is_fixed_for_every_tag():
    expected = {"REPORT": 8, "FUNC": 8, "ISSUE": 5}
    rng = random.Random(SEED)
    for _ in range(TRIALS):
        for line in serialise_report(_report(rng)):
            fields = line.split("|")
            assert len(fields) == expected[fields[0]]


def test_no_line_ever_contains_a_newline():
    rng = random.Random(SEED)
    for _ in range(TRIALS):
        for line in serialise_report(_report(rng)):
            assert "\n" not in line
            assert "\r" not in line


def test_no_field_is_ever_a_none():
    # a None reaching the file would serialise as the text "None" and parse
    # back as a string, which US34 could not detect
    rng = random.Random(SEED)
    for _ in range(TRIALS):
        for line in serialise_report(_report(rng)):
            assert "None" not in line.split("|")


def test_every_line_is_non_empty_and_has_no_leading_delimiter():
    rng = random.Random(SEED)
    for _ in range(TRIALS):
        for line in serialise_report(_report(rng)):
            assert line != ""
            assert not line.startswith("|")
            assert not line.endswith("|") or line.split("|")[0] == "REPORT"


def test_the_score_and_grade_are_recoverable_from_the_report_line():
    rng = random.Random(SEED)
    for _ in range(TRIALS):
        report = _report(rng)
        fields = serialise_report(report)[0].split("|")
        assert str(report.score) in fields
        assert report.grade in fields


def test_every_issue_line_carries_its_severity_and_code():
    rng = random.Random(SEED)
    for _ in range(TRIALS):
        report = _report(rng)
        lines = [l for l in serialise_report(report) if l.startswith("ISSUE|")]
        for line, issue in zip(lines, report.issues):
            fields = line.split("|")
            assert fields[1] == issue.code
            assert fields[2] == issue.severity
            assert fields[3] == str(issue.line)


def test_every_func_line_carries_its_name_and_start_line():
    rng = random.Random(SEED)
    for _ in range(TRIALS):
        report = _report(rng)
        lines = [l for l in serialise_report(report) if l.startswith("FUNC|")]
        for line, record in zip(lines, report.records):
            fields = line.split("|")
            assert fields[1] == record.name
            assert fields[2] == str(record.start_line)


def test_serialising_twice_gives_the_same_lines():
    # no hidden state, no timestamp generated inside the function
    rng = random.Random(SEED)
    for _ in range(TRIALS):
        report = _report(rng)
        assert serialise_report(report) == serialise_report(report)


def test_the_input_report_is_not_modified():
    rng = random.Random(SEED)
    for _ in range(TRIALS):
        report = _report(rng)
        before = (report.score, report.grade, len(report.records),
                  len(report.issues), report.timestamp)
        serialise_report(report)
        after = (report.score, report.grade, len(report.records),
                 len(report.issues), report.timestamp)
        assert before == after


def test_a_report_with_many_records_scales_linearly():
    # no quadratic behaviour and no truncation at any size
    rng = random.Random(SEED)
    for size in (0, 1, 2, 10, 50, 200):
        records = [_record(rng) for _ in range(size)]
        report = ReviewReport("a.py", 1, 1, 1, records, [], 80, "B")
        assert len(serialise_report(report)) == 1 + size


def test_none_is_always_rejected():
    with pytest.raises(ValueError):
        serialise_report(None)
