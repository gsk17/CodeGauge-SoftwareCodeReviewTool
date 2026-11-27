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

    #: the subset of NAMES passed to core.severity.classify_severity as its
    #: `limit`. These carry a higher floor, because a limit of 1 makes every
    #: finding CRITICAL - see MIN_SEVERITY_LIMIT. `comment_ratio_min` is NOT
    #: one of them: it is a minimum percentage compared directly, never banded,
    #: so a project asking for at least 1% comments is making a sensible
    #: request and must not be refused.
    SEVERITY_LIMITS = (
        "complexity_limit",
        "nesting_limit",
        "line_length_limit",
        "param_limit",
        "function_loc_limit",
        "duplicate_limit",
    )

    #: the floor for a name in SEVERITY_LIMITS, agreed at the Sprint 1
    #: retrospective on 24 November 2026.
    MIN_SEVERITY_LIMIT = 2

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
        """Return True only for a known threshold name and a usable value.

        A threshold of zero or less would make every rule fire on every
        function, so it is rejected rather than clamped.

        **A severity limit of 1 is also rejected**, which is the fix agreed at
        the Sprint 1 retrospective on 24 November 2026. At a limit of 1 the
        MINOR and MAJOR bands in `core.severity` are both empty by
        construction - MINOR is `limit // 2` values wide, and integer halving
        truncates 1 to nothing - so every finding in the report comes back
        CRITICAL and the severity scale conveys nothing. Nothing is lost by
        forbidding a configuration no user wants.

        **A severity limit of 2 is deliberately still permitted**, although the
        MAJOR band is empty there too. The symbolic analysis of `rule_params`
        in US22 showed that 3, not 2, is the smallest limit at which all three
        reachable bands are non-empty; the stand-up on 27 November decided
        against raising the floor again. A limit of 2 is a legitimate setting -
        a project insisting on at most two levels of nesting is strict rather
        than mistaken - and refusing it to keep a band non-empty would trade a
        real capability for a cosmetic one.
        `core.severity.reachable_severities` reports the limitation instead.

        **The floor applies only to SEVERITY_LIMITS.** `comment_ratio_min` is a
        minimum percentage compared directly rather than banded, so it keeps the
        floor of 1 and a project may ask for as little as 1% comments. Applying
        one floor to every name would have refused that for no reason, and the
        distinction is the reason this fix is seven lines rather than one
        character.
        """
        if name not in Thresholds.NAMES:
            return False
        if not isinstance(value, int) or isinstance(value, bool):
            return False
        if value < 1:                       # no threshold is ever usable at 0
            return False
        if name in Thresholds.SEVERITY_LIMITS:
            if value < Thresholds.MIN_SEVERITY_LIMIT:
                return False                # 1 makes every finding CRITICAL
        return True
