"""Severity classification - member M3 (ssl21, Saaket).

A severity is how far a measurement has gone past its limit, expressed in four
bands. Every rule in core.rules routes through classify_severity, so the whole
tool grades its findings on one consistent scale.
"""

CRITICAL = "CRITICAL"
MAJOR = "MAJOR"
MINOR = "MINOR"
INFO = "INFO"

#: worst first - the order combine_severities reduces along
RANK_ORDER = (CRITICAL, MAJOR, MINOR, INFO)


def classify_severity(actual, limit):
    """Band a measurement against its limit - US26.

    Within the limit is INFO, up to half again over is MINOR, below twice the
    limit is MAJOR, and at or beyond twice the limit is CRITICAL.
    """
    if actual < 0:
        raise ValueError("actual must not be negative, got %r" % (actual,))
    if limit < 1:
        raise ValueError("limit must be at least 1, got %r" % (limit,))
    if actual <= limit:
        return INFO                   # not over the limit at all
    if actual <= limit + limit // 2:
        return MINOR
    if actual < 2 * limit:
        return MAJOR
    return CRITICAL                   # twice the limit or worse
