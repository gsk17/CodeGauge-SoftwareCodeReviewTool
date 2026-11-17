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


#: lowest score that still earns each grade, best first
GRADE_A_FLOOR = 85
GRADE_B_FLOOR = 70
GRADE_C_FLOOR = 60
GRADE_D_FLOOR = 50


def grade_band(score):
    """Letter grade for a review score - US30.

    Five bands over the closed interval 0 to 100. Each test is written as a
    floor rather than a range, and the branches are checked best grade first,
    so each one only has to rule out the grades above it. That is what keeps
    the function monotonic: a higher score can never fall through to a lower
    grade than a smaller one did.

    A score outside 0 to 100 is a defect in the caller, not a very bad or very
    good file, so it is rejected rather than clamped.
    """
    if score < 0:                          # below the domain
        raise ValueError("score must not be negative, got %r" % (score,))
    if score > 100:                        # above the domain
        raise ValueError("score must not exceed 100, got %r" % (score,))
    if score >= GRADE_A_FLOOR:
        return "A"
    if score >= GRADE_B_FLOOR:
        return "B"
    if score >= GRADE_C_FLOOR:
        return "C"
    if score >= GRADE_D_FLOOR:
        return "D"
    return "F"                             # implicit else: below every floor
