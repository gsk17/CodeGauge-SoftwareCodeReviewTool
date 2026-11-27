"""Black-box tests for serialise_report - US33, Harshita (hcg22).

Technique: equivalence partitioning with boundary value analysis.
Function under test: core.history.serialise_report(report).

Turns a `ReviewReport` into a list of text lines, so a review can be stored
without a database. The brief forbids one, and the project's runtime is standard
library only, so the history file is plain text and this function decides what
it looks like.

### The format

One line per thing, pipe-delimited, with a tag in the first field saying what
the line is:

    REPORT|<file_name>|<code>|<comment>|<blank>|<score>|<grade>|<timestamp>
    FUNC|<name>|<start_line>|<loc>|<param_count>|<max_depth>|<cc>|<rating>
    ISSUE|<code>|<severity>|<line>|<message>

The REPORT line comes first, then one FUNC line per record in order, then one
ISSUE line per issue in order. The function returns a list of strings with no
trailing newlines - writing the file is US36's job, not this one's.

**Why a tag rather than a fixed layout.** A reader has to know what a line is
before it can know how many fields to expect, and the alternative - a header
line declaring the counts - means a corrupted count makes the whole file
unreadable rather than one line. With tags, US34 `parse_record_line` can reject
a single bad line and keep the rest.

### Partitions

    R1  a report with no functions and no issues -> one REPORT line only
    R2  one function, no issues                  -> REPORT + 1 FUNC
    R3  no functions, one issue                  -> REPORT + 1 ISSUE
    R4  several of each                          -> REPORT + n FUNC + m ISSUE, in that order
    R5  a score of 0 and a grade of F            -> serialised as "0" and "F", not omitted
    R6  an empty timestamp                       -> an empty field, not a missing one
    R7  a message containing a pipe              -> **the format cannot represent it**
    R8  report is None                           -> ValueError

**R1 is the partition this story exists for.** A clean file with no functions in
it is a legitimate review, and it must serialise to something a reader can parse
back into an empty report rather than to an empty list. An empty list would be
indistinguishable from a failed write.

**R6 matters because the field is positional.** `ReviewReport.timestamp`
defaults to `""` until `review_file` sets it. An absent field would shift every
field after it; an empty field between two pipes preserves the position. The
timestamp is last precisely so that the damage is contained if this is ever got
wrong.

**R7 is a known limitation of the format and is pinned, not worked around.**
There is no escaping. A message containing `|` produces a line that US34 will
split into too many fields. Every message this project generates is built by
the `rule_*` functions from a measurement and a limit - `"80 lines exceeds limit
50"` - so no pipe can occur today, and the test below records that the safety
comes from the callers rather than from the format. The alternatives were
escaping, quoting, or choosing a delimiter that cannot appear; all three cost
more than the problem is worth while the only producers are four rules whose
messages are fully determined. **If a rule ever formats a message from a
function name, this breaks**, and that is the note for whoever writes US25.
"""

import pytest

from core.history import serialise_report
from model.function_record import FunctionRecord
from model.issue import Issue
from model.review_report import ReviewReport
from core.severity import CRITICAL, MAJOR


def _empty_report():
    return ReviewReport("empty.py", 0, 0, 0, [], [], 100, "A")


def _record(name="withdraw", start=12, loc=20, params=3, depth=2):
    return FunctionRecord(name, start, loc, params, depth, 4, 1, 2, 1, 70, 0,
                          cc=5, rating="OK")


def test_r1_a_report_with_nothing_in_it_is_one_line():
    lines = serialise_report(_empty_report())
    assert len(lines) == 1
    assert lines[0].startswith("REPORT|")


def test_r1_is_never_an_empty_list():
    # an empty list would be indistinguishable from a failed write
    assert serialise_report(_empty_report()) != []


def test_r2_one_function_no_issues():
    report = ReviewReport("a.py", 40, 8, 5, [_record()], [], 85, "B")
    lines = serialise_report(report)
    assert len(lines) == 2
    assert lines[0].startswith("REPORT|")
    assert lines[1].startswith("FUNC|")


def test_r3_no_functions_one_issue():
    issue = Issue("LEN001", MAJOR, 12, "80 lines exceeds limit 50")
    report = ReviewReport("a.py", 40, 8, 5, [], [issue], 72, "C")
    lines = serialise_report(report)
    assert len(lines) == 2
    assert lines[0].startswith("REPORT|")
    assert lines[1].startswith("ISSUE|")


def test_r4_several_of_each_in_order():
    records = [_record("alpha", 1), _record("beta", 30), _record("gamma", 60)]
    issues = [Issue("CC001", CRITICAL, 1, "cyclomatic complexity 20 exceeds limit 10"),
              Issue("NEST001", MAJOR, 30, "nesting depth 6 exceeds limit 3")]
    report = ReviewReport("big.py", 200, 30, 20, records, issues, 40, "E")
    lines = serialise_report(report)
    assert len(lines) == 6
    tags = [line.split("|")[0] for line in lines]
    assert tags == ["REPORT", "FUNC", "FUNC", "FUNC", "ISSUE", "ISSUE"]


def test_r4_the_record_order_is_preserved():
    records = [_record("alpha", 1), _record("beta", 30), _record("gamma", 60)]
    report = ReviewReport("big.py", 200, 30, 20, records, [], 40, "E")
    names = [line.split("|")[1] for line in serialise_report(report)[1:]]
    assert names == ["alpha", "beta", "gamma"]


def test_r5_a_zero_score_and_an_f_grade_are_written_not_omitted():
    report = ReviewReport("bad.py", 500, 0, 0, [], [], 0, "F")
    fields = serialise_report(report)[0].split("|")
    assert "0" in fields
    assert "F" in fields


def test_r6_an_empty_timestamp_keeps_its_field():
    # the field must be present and empty, or every later field shifts
    report = _empty_report()                 # timestamp defaults to ""
    fields = serialise_report(report)[0].split("|")
    assert len(fields) == 8
    assert fields[-1] == ""


def test_r6_a_set_timestamp_appears_in_the_same_position():
    report = ReviewReport("a.py", 1, 1, 1, [], [], 90, "A",
                          timestamp="2026-11-27T09:00:00")
    fields = serialise_report(report)[0].split("|")
    assert len(fields) == 8
    assert fields[-1] == "2026-11-27T09:00:00"


def test_r7_a_pipe_in_a_message_breaks_the_format():
    # A known limitation, recorded rather than worked around. There is no
    # escaping, so this line splits into six fields where ISSUE expects five.
    issue = Issue("CC001", MAJOR, 7, "complexity 12 | limit 10")
    report = ReviewReport("a.py", 1, 1, 1, [], [issue], 80, "B")
    line = serialise_report(report)[1]
    assert len(line.split("|")) == 6


def test_r7_no_message_this_project_generates_contains_a_pipe():
    # Where the safety actually comes from: the rule_* functions build every
    # message from a measurement and a limit, so a pipe cannot occur.
    from core.rules import rule_complexity, rule_nesting, rule_params
    for limit in range(1, 20):
        for measurement in (limit + 1, limit * 2, limit * 5):
            for rule in (rule_complexity, rule_nesting, rule_params):
                assert "|" not in rule(measurement, limit, 1).message


def test_r8_none_is_rejected():
    with pytest.raises(ValueError):
        serialise_report(None)


# --------------------------------------------------------------------------
# Format invariants.
# --------------------------------------------------------------------------


def test_every_line_is_a_string_with_no_newline():
    # writing the file belongs to US36; this function returns bare lines
    records = [_record(), _record("beta", 40)]
    issues = [Issue("CC001", MAJOR, 1, "cyclomatic complexity 12 exceeds limit 10")]
    report = ReviewReport("a.py", 40, 8, 5, records, issues, 70, "C")
    for line in serialise_report(report):
        assert isinstance(line, str)
        assert "\n" not in line
        assert "\r" not in line


def test_every_line_carries_a_known_tag():
    records = [_record()]
    issues = [Issue("CC001", MAJOR, 1, "cyclomatic complexity 12 exceeds limit 10")]
    report = ReviewReport("a.py", 40, 8, 5, records, issues, 70, "C")
    for line in serialise_report(report):
        assert line.split("|")[0] in ("REPORT", "FUNC", "ISSUE")


def test_the_field_count_is_fixed_per_tag():
    records = [_record()]
    issues = [Issue("CC001", MAJOR, 1, "cyclomatic complexity 12 exceeds limit 10")]
    report = ReviewReport("a.py", 40, 8, 5, records, issues, 70, "C")
    expected = {"REPORT": 8, "FUNC": 8, "ISSUE": 5}
    for line in serialise_report(report):
        fields = line.split("|")
        assert len(fields) == expected[fields[0]]


def test_the_report_line_is_always_first():
    records = [_record()]
    issues = [Issue("CC001", MAJOR, 1, "complexity 12 exceeds limit 10")]
    report = ReviewReport("a.py", 40, 8, 5, records, issues, 70, "C")
    assert serialise_report(report)[0].split("|")[0] == "REPORT"


def test_the_file_name_survives_a_path_and_an_extension():
    report = ReviewReport("src/core/scanner.py", 1, 1, 1, [], [], 90, "A")
    assert "src/core/scanner.py" in serialise_report(report)[0]
