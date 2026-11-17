"""Complexity metrics - member M2 (khm12, Kasam).

Every function here takes integers and returns an integer or a rating string.
The branching is written out explicitly rather than as table lookups: the module
is graded on cyclomatic complexity and on how clearly its symbolic execution
trees can be drawn, and explicit branches make both visible. Readability is
carried by the names, docstrings and per-branch comments instead.
"""


def decision_points(if_count, elif_count, for_count, while_count, except_count,
                    comprehension_count):
    """Total decision points in a function - US10.

    A decision point is anything that adds an outgoing edge to the control flow
    graph: each if, elif, for, while and except, plus each comprehension.
    Cyclomatic complexity is computed from this total.
    """
    counts = (("if_count", if_count), ("elif_count", elif_count),
              ("for_count", for_count), ("while_count", while_count),
              ("except_count", except_count),
              ("comprehension_count", comprehension_count))
    for name, value in counts:
        if value < 0:
            raise ValueError("%s must not be negative, got %r" % (name, value))
    return (if_count + elif_count + for_count + while_count + except_count
            + comprehension_count)


def cyclomatic_complexity(decision_point_count, bool_operators):
    """Cyclomatic complexity of a single-entry function - US11.

    McCabe's measure for a function with one entry and one exit is
    E - N + 2, which for structured code collapses to one more than the
    number of independent decisions. Each boolean operator inside a
    condition adds a decision of its own, because `if a and b` short
    circuits and so carries two outgoing edges rather than one.

    The constant 1 is not an adjustment: a function with no decisions
    still has exactly one path through it, so the lowest possible
    complexity is 1 and never 0.
    """
    if decision_point_count < 0:
        raise ValueError("decision_point_count must not be negative, got %r"
                         % (decision_point_count,))
    if bool_operators < 0:
        raise ValueError("bool_operators must not be negative, got %r"
                         % (bool_operators,))
    return decision_point_count + bool_operators + 1


def max_nesting_depth(depths):
    """Deepest nesting reached anywhere in a function - US12.

    Takes the per-line nesting depths produced by the scanner and returns the
    largest. An empty list is 0 rather than an error: a function with no lines
    is not nested, and the caller should not have to special-case it.

    Every element is validated before the scan begins, so a negative depth is
    rejected even when it is not the largest value in the list. Validating
    inside the scan would let a negative value pass unnoticed whenever a
    larger valid value had already been seen.
    """
    for depth in depths:
        if depth < 0:                      # a nesting depth is never negative
            raise ValueError("nesting depth must not be negative, got %r"
                             % (depth,))
    deepest = 0                            # the answer for an empty list
    for depth in depths:
        if depth > deepest:                # a new maximum
            deepest = depth
    return deepest
