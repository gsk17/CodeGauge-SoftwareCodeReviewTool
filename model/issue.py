"""One rule violation found during a review."""


class Issue:
    """Plain data holder: a rule code, a severity, a line and a message."""

    def __init__(self, code, severity, line, message):
        self.code = code          # e.g. "CC001"
        self.severity = severity  # one of the constants in core.severity
        self.line = line          # 1-based line the issue is reported against
        self.message = message    # human-readable explanation
