"""White-box tests for grade_band - US30, Harshita (hcg22).

Technique: symbolic execution.
Function under test: core.scoring.grade_band(score).

The input is one symbolic integer, S. Every decision compares S against a
constant, so each path condition is a conjunction of linear constraints on S
and solves by hand. The function has no loops, so the tree is finite: seven
leaves, seven paths.

    Path  Path condition                       Witness  Returns
    P1    S < 0                                -1       ValueError
    P2    S >= 0 and S > 100                   101      ValueError
    P3    0 <= S <= 100 and S >= 85            85       "A"
    P4    ... and S < 85 and S >= 70           70       "B"
    P5    ... and S < 70 and S >= 60           60       "C"
    P6    ... and S < 60 and S >= 50           50       "D"
    P7    ... and S < 50                       49       "F"

Each witness below is the smallest value satisfying its path condition, because
every condition is a half-open interval closed at its lower end. Solving for
the minimum therefore lands exactly on the threshold, which is where an
off-by-one would show.

**What the analysis proves.** Collect the seven path conditions and they
partition the closed interval 0..100 into five intervals with no gap and no
overlap:

    [85,100]  [70,84]  [60,69]  [50,59]  [0,49]

That is a proof rather than a sample. It establishes two properties no finite
set of example inputs could:

  * **totality** - every integer in 0..100 satisfies exactly one path
    condition, so the function always returns and never falls through;
  * **monotonicity** - the intervals are ordered, so a larger score can never
    reach a worse grade than a smaller one.

The random-based black-box tests assert monotonicity by sampling. This derives
it, and the two together are the reason the story needs both techniques.

**No infeasible paths.** Each path condition is a non-empty interval of
integers, and the witness column names a member of each.
"""

import pytest

from core.scoring import grade_band


def test_p1_the_negative_guard():
    # PC: S < 0. Solved at the largest such integer, which is the boundary.
    with pytest.raises(ValueError):
        grade_band(-1)


def test_p2_the_upper_guard():
    # PC: S >= 0 and S > 100. Smallest solution: S = 101.
    with pytest.raises(ValueError):
        grade_band(101)


def test_p3_returns_a():
    # PC: 0 <= S <= 100 and S >= 85. Smallest solution: S = 85.
    assert grade_band(85) == "A"


def test_p4_returns_b():
    # PC: ... and S < 85 and S >= 70. Smallest solution: S = 70.
    assert grade_band(70) == "B"


def test_p5_returns_c():
    # PC: ... and S < 70 and S >= 60. Smallest solution: S = 60.
    assert grade_band(60) == "C"


def test_p6_returns_d():
    # PC: ... and S < 60 and S >= 50. Smallest solution: S = 50.
    assert grade_band(50) == "D"


def test_p7_returns_f():
    # PC: ... and S < 50. Largest solution: S = 49.
    assert grade_band(49) == "F"


def test_the_path_conditions_partition_the_whole_domain():
    """Totality, checked against the derivation rather than assumed.

    The seven path conditions were solved to five intervals covering 0..100
    with no gap and no overlap. If that derivation is right then every integer
    in the domain returns a grade, and each grade's own interval returns only
    that grade. Both halves are asserted here.
    """
    intervals = ((85, 100, "A"), (70, 84, "B"), (60, 69, "C"),
                 (50, 59, "D"), (0, 49, "F"))
    covered = 0
    for low, high, grade in intervals:
        for score in range(low, high + 1):
            assert grade_band(score) == grade
            covered = covered + 1
    # no gaps and no overlaps: the five intervals are exactly 101 integers
    assert covered == 101
