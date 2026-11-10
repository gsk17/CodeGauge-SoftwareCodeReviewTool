"""The integer record describing one function found in a source file.

Everything downstream of the scanner consumes these integers rather than source
text, which is what makes the graded functions straightforward to partition for
black-box testing and to analyse symbolically.
"""


class FunctionRecord:
    """Plain data holder for one function's measurements. No logic lives here."""

    def __init__(self, name, start_line, loc, param_count, max_depth,
                 decision_points, bool_operators, comment_lines, blank_lines,
                 longest_line, duplicate_lines, cc=0, rating="OK",
                 penalty=0, length_rating="OK", param_rating="OK",
                 duplication=0, maintainability=0, worst_severity="INFO"):
        self.name = name                        # function name as written
        self.start_line = start_line            # 1-based line of the def
        self.loc = loc                          # lines of code in the body
        self.param_count = param_count          # parameters, excluding self/cls
        self.max_depth = max_depth              # deepest nesting level
        self.decision_points = decision_points  # if/elif/for/while/except/comprehensions
        self.bool_operators = bool_operators    # occurrences of "and" / "or"
        self.comment_lines = comment_lines
        self.blank_lines = blank_lines
        self.longest_line = longest_line        # characters in the longest line
        self.duplicate_lines = duplicate_lines  # repeated code lines
        self.cc = cc                            # filled in by the complexity stage
        self.rating = rating                    # filled in by the complexity stage
        # The remaining fields are the derived metrics the review pipeline fills
        # in after the complexity stage; they are reported, not used as rules.
        self.penalty = penalty                  # nesting penalty points
        self.length_rating = length_rating      # SHORT / OK / LONG / VERY_LONG
        self.param_rating = param_rating        # OK / MANY / EXCESSIVE
        self.duplication = duplication          # duplicated lines, percent
        self.maintainability = maintainability  # 0-100 maintainability index
        self.worst_severity = worst_severity    # worst issue raised against it
