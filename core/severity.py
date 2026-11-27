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


#: the smallest limit at which all three reachable severities are non-empty.
#: Below this, at least one band is empty by construction - see
#: reachable_severities and docs/symbolic/ssl21-symbolic-execution.md, US22.
MIN_SOUND_LIMIT = 3


def reachable_severities(limit):
    """Which severities a rule can actually emit at a given limit - US22 follow-up.

    Returned worst-first, in RANK_ORDER. INFO never appears: reaching
    classify_severity from a rule requires the measurement to be over the
    limit, and INFO requires it to be within, so no rule can emit it at any
    limit at all.

    **At small limits the bands collapse**, because MINOR is `limit // 2`
    values wide and integer halving truncates to nothing:

        limit 1   ->  (CRITICAL,)                      MINOR and MAJOR empty
        limit 2   ->  (CRITICAL, MINOR)                MAJOR empty
        limit 3   ->  (CRITICAL, MAJOR, MINOR)         all three
        limit 10  ->  (CRITICAL, MAJOR, MINOR)

    The Sprint 1 retrospective agreed to tighten `Thresholds.validate` to
    reject limits below 2, which removes the worst case. A limit of 2 still
    produces a report in which MAJOR cannot appear, and that configuration is
    deliberately still permitted: a project insisting on at most two levels of
    nesting is strict rather than misconfigured, and refusing it would trade a
    real capability for a cosmetic one. **This function exists so the
    limitation is reported rather than forbidden**, which was the decision
    taken at the stand-up on 27 November.

    The bands are not restated here. The answer is computed by asking
    classify_severity, over the range `limit + 1` to `2 * limit`, which is the
    smallest range guaranteed to touch every reachable band - so if the banding
    arithmetic ever changes, this function changes with it rather than
    silently disagreeing. That is the whole point: US22 found three independent
    copies of a banding decision is already one risk too many.
    """
    if limit < 1:                          # the contract classify_severity sets
        raise ValueError("limit must be at least 1, got %r" % (limit,))
    found = set()
    for actual in range(limit + 1, 2 * limit + 1):
        found.add(classify_severity(actual, limit))
    return tuple(band for band in RANK_ORDER if band in found)
