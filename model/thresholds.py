"""The configurable limits a review is measured against.

Defaults are the values fixed in the implementation plan. The menu lets a user
change them at runtime, which is why validation lives here beside them.
"""


class Thresholds:
    """Review limits, with the project's default values."""

    #: the threshold names the menu is allowed to change
    NAMES = (
        "complexity_limit",
        "nesting_limit",
        "line_length_limit",
        "param_limit",
        "function_loc_limit",
        "comment_ratio_min",
        "duplicate_limit",
    )

    def __init__(self, complexity_limit=10, nesting_limit=3, line_length_limit=100,
                 param_limit=4, function_loc_limit=50, comment_ratio_min=10,
                 duplicate_limit=6):
        self.complexity_limit = complexity_limit
        self.nesting_limit = nesting_limit
        self.line_length_limit = line_length_limit
        self.param_limit = param_limit
        self.function_loc_limit = function_loc_limit
        self.comment_ratio_min = comment_ratio_min
        self.duplicate_limit = duplicate_limit

    @staticmethod
    def validate(name, value):
        """Return True only for a known threshold name and a value of at least 1.

        A threshold of zero or less would make every rule fire on every function,
        so it is rejected rather than clamped.
        """
        if name not in Thresholds.NAMES:
            return False
        if not isinstance(value, int) or isinstance(value, bool):
            return False
        if value < 1:
            return False
        return True
