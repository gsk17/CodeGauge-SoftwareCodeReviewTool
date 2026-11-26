"""Review history and trends - member M4 (hcg22, Harshita).

Functions over a sequence of past review scores: comparing two, describing a
trend across several, and summarising a history. Everything here takes scores
rather than reports, so the module never touches a file - reading and writing
`reviews.dat` belongs to `core/storage.py`.
"""

#: the change between two reviews, worst to best
MUCH_REGRESSED = "MUCH_REGRESSED"
REGRESSED = "REGRESSED"
UNCHANGED = "UNCHANGED"
IMPROVED = "IMPROVED"
MUCH_IMPROVED = "MUCH_IMPROVED"

#: a change of this many points or more is a large one, in either direction
LARGE_CHANGE = 10


def compare_scores(before, after):
    """Classify the change between two review scores - US31.

    Five bands, symmetric about zero: no change, a small move of 1 to 9 points
    either way, and a large move of 10 or more either way.

    **The sign is carried, not discarded.** The obvious implementation takes
    `abs(after - before)`, bands the magnitude and then decides the direction
    afterwards - which works until the two steps disagree. Here the difference
    keeps its sign the whole way through and each band is tested against it
    directly, so a gain and a loss of the same size take different branches
    rather than the same branch with a label attached.

    The branches are written out rather than looked up in a table, so that the
    symmetry is visible as structure: the two gain tests mirror the two loss
    tests, and an error in one would not be hidden by the other.
    """
    if before < 0 or before > 100:
        raise ValueError("before must be between 0 and 100, got %r" % (before,))
    if after < 0 or after > 100:
        raise ValueError("after must be between 0 and 100, got %r" % (after,))

    difference = after - before            # positive is an improvement
    if difference == 0:
        return UNCHANGED
    if difference >= LARGE_CHANGE:         # a large gain
        return MUCH_IMPROVED
    if difference > 0:                     # a small gain, 1 to 9
        return IMPROVED
    if difference <= -LARGE_CHANGE:        # a large loss
        return MUCH_REGRESSED
    return REGRESSED                       # implicit else: a small loss, 1 to 9
