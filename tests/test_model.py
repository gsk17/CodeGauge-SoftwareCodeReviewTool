"""Black-box tests for the data model (plan Task 4).

Technique: specification-based - the values asserted here are the defaults and
field contracts fixed in the implementation plan, not implementation details.
Moved into <username>/test/blackbox/<technique>/ in plan Task 10.
"""

import pytest

from model.function_record import FunctionRecord
from model.issue import Issue
from model.review_report import ReviewReport
from model.thresholds import Thresholds


def test_thresholds_defaults():
    t = Thresholds()
    assert (t.complexity_limit, t.nesting_limit, t.line_length_limit) == (10, 3, 100)
    assert (t.param_limit, t.function_loc_limit) == (4, 50)
    assert (t.comment_ratio_min, t.duplicate_limit) == (10, 6)


def test_validate_rejects_zero_negative_and_unknown():
    assert Thresholds.validate("complexity_limit", 1) is True
    assert Thresholds.validate("complexity_limit", 0) is False
    assert Thresholds.validate("complexity_limit", -3) is False
    assert Thresholds.validate("not_a_threshold", 5) is False


def test_records_hold_their_fields():
    r = FunctionRecord("withdraw", 38, 24, 4, 5, 10, 1, 3, 2, 118, 0)
    assert (r.name, r.start_line, r.max_depth, r.longest_line) == ("withdraw", 38, 5, 118)


def test_record_enrichment_fields_default_then_set():
    # Ruling 2: cc and rating are filled in after the complexity stage.
    r = FunctionRecord("deposit", 10, 6, 2, 1, 0, 0, 1, 1, 42, 0)
    assert (r.cc, r.rating) == (0, "OK")
    r.cc, r.rating = 11, "HIGH"
    assert (r.cc, r.rating) == (11, "HIGH")


def test_issue_holds_its_fields():
    i = Issue("CC001", "MAJOR", 38, "cyclomatic complexity 16 exceeds limit 10")
    assert (i.code, i.severity, i.line) == ("CC001", "MAJOR", 38)
    assert i.message.endswith("limit 10")


def test_review_report_holds_its_fields_and_defaults_timestamp():
    # Ruling 3: timestamp is a trailing defaulted parameter.
    report = ReviewReport("bank_account.py", 142, 28, 19, [], [], 100, "A")
    assert (report.file_name, report.code_lines, report.score) == ("bank_account.py", 142, 100)
    assert report.timestamp == ""
    stamped = ReviewReport("a.py", 1, 1, 1, [], [], 90, "A", "2026-11-20T10:00")
    assert stamped.timestamp == "2026-11-20T10:00"
