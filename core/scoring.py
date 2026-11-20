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


#: three or more critical issues hold the score down to this value
CRITICAL_CAP_COUNT = 3
CAPPED_SCORE = 40

#: the score a file with no findings earns, and the lowest possible score
PERFECT_SCORE = 100
WORST_SCORE = 0


def score_from_issues(critical, major, minor, info):
    """Quality score out of 100 from the issue counts - US29.

    A review starts at 100 and pays a weighted penalty per issue. Two rules
    then adjust the result, and the order in which they apply is the part of
    this function that actually needs care.

    **The cap is a maximum, not an assignment.** Three or more critical issues
    hold the score down to 40 - but a file with ten critical issues must not
    score the same as one with three, and must certainly not score better than
    one with five. So the cap is applied as "lower the score to 40 if it is
    above 40", never as "set the score to 40":

        (3, 0, 0, 0)   raw 55   -> capped to 40
        (4, 0, 0, 0)   raw 40   -> already at the cap, unchanged
        (5, 0, 0, 0)   raw 25   -> below the cap, left alone
        (10, 0, 0, 0)  raw -50  -> below the cap, then floored to 0

    Written as an assignment, the last of those would return 40, and ten
    critical issues would score better than five. The pair (3,0,0,0) -> 40 and
    (10,0,0,0) -> 0 is the only pair of inputs that distinguishes the two
    readings, and both are in the black-box tests.

    **The floor applies last**, after the cap, for the same reason: the cap can
    only lower a score, so a score already below zero must still be raised to
    zero afterwards.

    The weights are the module constants rather than parameters, because two
    reviews of the same file have to be comparable. weighted_penalty (US28)
    takes them as arguments for the cases where a caller wants to vary the
    policy; this function is the fixed project scoring.
    """
    counts = (("critical", critical), ("major", major),
              ("minor", minor), ("info", info))
    for name, value in counts:
        if value < 0:
            raise ValueError("%s must not be negative, got %r" % (name, value))

    penalty = (CRITICAL_WEIGHT * critical + MAJOR_WEIGHT * major
               + MINOR_WEIGHT * minor + INFO_WEIGHT * info)
    score = PERFECT_SCORE - penalty

    if critical >= CRITICAL_CAP_COUNT:     # the cap applies at all
        if score > CAPPED_SCORE:           # and only ever lowers the score
            score = CAPPED_SCORE

    if score < WORST_SCORE:                # the floor, applied after the cap
        score = WORST_SCORE
    return score
