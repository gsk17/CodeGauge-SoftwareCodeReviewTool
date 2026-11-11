"""Quality scoring - member M4 (hcg22, Harshita).

A review starts from a perfect 100 and pays a penalty per issue found. The
weights are fixed project constants so that two reviews of the same file are
always comparable.
"""

from core.severity import CRITICAL, INFO, MAJOR, MINOR

#: penalty points per issue, by severity
CRITICAL_WEIGHT = 15
MAJOR_WEIGHT = 8
MINOR_WEIGHT = 3
INFO_WEIGHT = 1


def weighted_penalty(severity, critical_w, major_w, minor_w, info_w):
    """Penalty points for one issue of the given severity - US28.

    The weights are passed in rather than read from the module constants so
    that the scoring policy can be varied without changing this function.
    """
    weights = (("critical_w", critical_w), ("major_w", major_w),
               ("minor_w", minor_w), ("info_w", info_w))
    for name, weight in weights:
        if weight < 0:
            raise ValueError("%s must not be negative, got %r" % (name, weight))
    if severity == CRITICAL:
        return critical_w
    if severity == MAJOR:
        return major_w
    if severity == MINOR:
        return minor_w
    if severity == INFO:
        return info_w
    raise ValueError("unknown severity %r" % (severity,))
