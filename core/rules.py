"""Rule engine - member M3 (ssl21, Saaket).

One function per rule. Each takes the measurements the scanner and the
complexity module produced, compares them against a configured limit, and
returns either an Issue or None. A rule never prints, never reads a file and
never decides a severity for itself: the severity comes from
core.severity.classify_severity, so that every rule in the tool grades its
findings on the same scale.

Returning None for "nothing wrong" rather than an empty list keeps the caller
simple - the report builder can drop the Nones in one pass.
"""

from core.severity import classify_severity
from model.issue import Issue

#: rule codes, one per rule. The code identifies the rule, not the severity.
CODE_COMPLEXITY = "CC001"
CODE_NESTING = "NEST001"
CODE_PARAMS = "PAR001"


def rule_complexity(cc, limit, line):
    """Raise an issue when a function is too complex - US19.

    Returns None when the cyclomatic complexity is within the limit, and an
    Issue when it is over. The limit is inclusive: a function sitting exactly
    on the configured maximum is acceptable, so the comparison is `cc <= limit`
    and not `cc < limit`.

    The severity is delegated to classify_severity rather than banded here.
    That matters for more than tidiness: it is the reason a complexity of 11
    against a limit of 10 is reported as MINOR while 20 against the same limit
    is CRITICAL, without this function knowing anything about the bands. If the
    project ever changes how far past a limit counts as serious, this rule does
    not change at all.
    """
    if cc < 0:                             # complexity is a count of paths
        raise ValueError("cc must not be negative, got %r" % (cc,))
    if limit < 1:                          # the contract classify_severity sets
        raise ValueError("limit must be at least 1, got %r" % (limit,))
    if cc <= limit:                        # within budget: no finding
        return None
    severity = classify_severity(cc, limit)
    message = "cyclomatic complexity %d exceeds limit %d" % (cc, limit)
    return Issue(CODE_COMPLEXITY, severity, line, message)


def rule_nesting(depth, limit, line):
    """Raise an issue when a function is nested too deeply - US20.

    The same shape as rule_complexity: None when the measurement is within its
    limit, an Issue when it is over, and the severity delegated to
    classify_severity so that every rule in the tool grades on one scale. The
    limit is inclusive, so a function sitting exactly on the configured
    maximum is acceptable.

    The duplication with rule_complexity is deliberate. The two could be one
    parameterised function taking a code and a message template, but each rule
    is a separately graded user story owned by a different member, and a shared
    helper would put two sets of marks inside one function. The cost is a
    near-identical body; the benefit is that the two can be assessed apart.

    What the two rules must share is the banding, and they do - both call
    classify_severity rather than deciding for themselves. A test in
    khm12/test/blackbox/equivalence_partitioning/ asserts that the two produce
    identical severities for identical numbers while carrying different codes,
    which is what would fail if either one re-implemented the bands.
    """
    if depth < 0:                          # a nesting depth is never negative
        raise ValueError("depth must not be negative, got %r" % (depth,))
    if limit < 1:                          # the contract classify_severity sets
        raise ValueError("limit must be at least 1, got %r" % (limit,))
    if depth <= limit:                     # within budget: no finding
        return None
    severity = classify_severity(depth, limit)
    message = "nesting depth %d exceeds limit %d" % (depth, limit)
    return Issue(CODE_NESTING, severity, line, message)


def rule_params(param_count, limit, line):
    """Raise an issue when a signature takes too many parameters - US22.

    The third rule in this module, and the third built to the shape US19
    established: None when the measurement is within its limit, an Issue when
    it is over, and the severity delegated to classify_severity.

    By the third instance the shape is worth stating as a contract rather than
    a coincidence. Every rule_* function in this module:

      * validates its measurement and its limit, in that order;
      * treats the limit as inclusive, so sitting exactly on it is acceptable;
      * returns None rather than an INFO-severity issue when nothing is wrong;
      * carries its own code constant and its own message, and decides nothing
        about severity.

    Tests in all three members' black-box packages assert that the three rules
    produce identical severities for identical numbers while carrying different
    codes, which is what would fail if any of them re-implemented the bands.
    """
    if param_count < 0:                    # a parameter count is never negative
        raise ValueError("param_count must not be negative, got %r"
                         % (param_count,))
    if limit < 1:                          # the contract classify_severity sets
        raise ValueError("limit must be at least 1, got %r" % (limit,))
    if param_count <= limit:               # within budget: no finding
        return None
    severity = classify_severity(param_count, limit)
    message = "%d parameters exceeds limit %d" % (param_count, limit)
    return Issue(CODE_PARAMS, severity, line, message)
