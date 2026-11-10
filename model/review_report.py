"""The complete result of reviewing one source file."""


class ReviewReport:
    """Plain data holder for one file's review."""

    def __init__(self, file_name, code_lines, comment_lines, blank_lines,
                 records, issues, score, grade, timestamp="",
                 comment_band="OK", longest_line_grade="OK"):
        self.file_name = file_name
        self.code_lines = code_lines
        self.comment_lines = comment_lines
        self.blank_lines = blank_lines
        self.records = records      # list of FunctionRecord
        self.issues = issues        # list of Issue
        self.score = score          # 0-100
        self.grade = grade          # A to F
        self.timestamp = timestamp  # set by review_file; "" until then
        self.comment_band = comment_band              # ABSENT / LOW / OK / RICH
        self.longest_line_grade = longest_line_grade  # OK / LONG / VERY_LONG / EXTREME
