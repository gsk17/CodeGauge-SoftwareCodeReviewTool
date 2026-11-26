"""White-box tests for comment_ratio_percent - US04, Gunjan (gsk17).

Technique: symbolic execution.
Function under test: core.line_metrics.comment_ratio_percent(comment_lines,
code_lines).

After US01 (string properties) and US02 (a loop needing k=2 unrolling), this
is the first of Gunjan's functions whose path conditions are **linear
arithmetic over two integers**, so the constraints are solvable by hand with
no search and no bounding.

**Symbolic inputs.** Two symbolic integers, C for comment_lines and K for
code_lines, with the derived term `N = C + K`. The function branches three
times and the tree is a chain, so there are four leaves and four paths.

    Path  Path condition                 Witness      Returns
    P1    C < 0                          (-1, -1)     ValueError, comment_lines
    P2    C >= 0, K < 0                  (0, -1)      ValueError, code_lines
    P3    C >= 0, K >= 0, N == 0         (0, 0)       0
    P4    C >= 0, K >= 0, N > 0          (28, 142)    C * 100 // N

Four leaves, four paths, no infeasible combinations among them - the chain
shape means each path condition simply extends its predecessor's negation.

### Finding 1 - P3's path condition has exactly one solution

    C >= 0  and  K >= 0  and  C + K == 0

Two non-negative integers summing to zero are both zero. **The empty-file
branch is reachable by precisely one input out of an infinite domain**, and
every other leaf is reachable by infinitely many.

That is worth stating because it changes what a test of that branch means.
Black-box equivalence partitioning picks a representative from each partition
and accepts the risk that the representative is not typical of the rest. Here
there is no rest: the partition is a singleton, so the test is exhaustive over
it, and no boundary analysis around it is possible because it has no interior.

It also means the branch cannot be reached by accident in production. A caller
that mis-counts cannot stumble into it; only a genuinely empty file arrives
there.

### Finding 2 - `== 0` and `<= 0` are interchangeable at b3, but only because of b1 and b2

The guard is `if counted == 0`, which reads like a deliberately narrow test
where a defensive programmer would write `<= 0`. Symbolically the two are
equivalent, because the path condition reaching b3 already contains
`C >= 0 and K >= 0`, which implies `N >= 0`, which makes `N < 0`
unsatisfiable. The branch `N <= 0 and N != 0` is an **infeasible path**.

**The equivalence is inherited from the validations, not intrinsic.** Delete
b1 and the two forms diverge immediately:

    (5, -5)   N == 0   ->  `== 0` returns 0;  `<= 0` returns 0        agree
    (5, -10)  N == -5  ->  `== 0` divides: 500 // -5 == -100          disagree
                           `<= 0` returns 0

So `== 0` is safe in the presence of the validations and produces a negative
percentage without them, while `<= 0` is safe either way. The current code is
correct; it is correct *conditionally*, and the condition is three lines
above. Recorded because the two validations look like input hygiene and are in
fact load-bearing for the arithmetic below them.

### Finding 3 - 100 is returned if and only if K == 0

Solving the leaf expression rather than sampling it:

    C * 100 // N == 100
      <=>  C * 100 >= 100 * N                  (floor division)
      <=>  C * 100 >= 100 * (C + K)
      <=>  0 >= 100 * K
      <=>  K <= 0

Conjoined with P4's `K >= 0` this gives `K == 0`, and with `N > 0` it gives
`C >= 1`. So the path condition for a returned 100 is exactly
`C >= 1 and K == 0`: **a file of comments and nothing else.**

The docstring asserts this ("a file containing even one line of code can never
reach it"). The derivation is what makes it a guarantee rather than an
observation from the examples that happened to be tried, and it is the reason
a downstream rule may treat 100 as the distinguishable case "no code here"
rather than as "very well documented".

### Finding 4 - 0 is returned for a band of inputs that do contain comments

    C * 100 // N == 0
      <=>  C * 100 < N
      <=>  C * 100 < C + K
      <=>  99 * C < K

So 0 does not mean "no comments". It means "fewer than K/99 comments", and
that threshold grows with the file:

    K = 99    C = 1  ->  100 // 100 == 1     reported as 1
    K = 100   C = 1  ->  100 // 101 == 0     reported as 0
    K = 500   C = 5  ->  500 // 505 == 0     reported as 0

Under rounding to nearest, the second case would report 1. Flooring is the
deliberate choice - the docstring argues a reported figure must never
overstate what is present - and this is its cost, stated exactly: **a file of
101 code lines with five comments in it is reported identically to a file with
none.** A caller that treats 0 as "undocumented" is wrong for those inputs,
and a caller that treats 0 as "below one percent" is right for all of them.

### Finding 5 - the metric's resolution is the file size, so large files are insensitive to single comments

The set of C values that produce a given result r is an interval. From
`r <= C * 100 / N < r + 1`, its width is about `N / 100`. For a file of 170
counted lines that is 1.7, so one or two comment lines move the figure by one
point. For a file of 1000 counted lines it is 10:

    C = 10, K = 990   ->  1000 // 1000 == 1
    C = 11, K = 990   ->  1100 // 1001 == 1
    C = 19, K = 990   ->  1900 // 1009 == 1
    C = 20, K = 990   ->  2000 // 1010 == 1

Four added comments, no change; it takes ten. **In a file over 100 counted
lines, a single added comment cannot change the reported percentage**, so the
metric cannot show incremental improvement on exactly the files most likely to
need it. That is a property of expressing the measure as a whole-number
percentage rather than of this implementation, and it is why the issue list
rather than this number is what a reviewer should act on.

### Finding 6 - no path raises ZeroDivisionError, and that is provable

The only division is on P4, whose path condition contains `N > 0`. There is no
path on which the division is reached with `N == 0`, because b3 returns first,
and none on which it is reached with `N < 0`, because b1 and b2 raise first.
The function is **total**: every pair of integers satisfies exactly one of the
four path conditions, so the function always either returns or raises
deliberately, and never fails arithmetically.
"""

import pytest

from core.line_metrics import comment_ratio_percent


def test_p1_negative_comments():
    # P1: C < 0. The witness makes K invalid too, to show b1 is reached first.
    with pytest.raises(ValueError) as caught:
        comment_ratio_percent(-1, -1)
    assert "comment_lines" in str(caught.value)


def test_p2_negative_code():
    # P2: C >= 0, K < 0
    with pytest.raises(ValueError) as caught:
        comment_ratio_percent(0, -1)
    assert "code_lines" in str(caught.value)


def test_p3_the_only_solution_of_its_path_condition():
    # P3: C >= 0, K >= 0, C + K == 0. Finding 1 - this is the whole partition,
    # not a representative of it.
    assert comment_ratio_percent(0, 0) == 0


def test_p4_the_division_leaf():
    # P4: C >= 0, K >= 0, C + K > 0
    assert comment_ratio_percent(28, 142) == 16


def test_finding_2_the_validations_are_load_bearing_for_the_equality():
    # The inputs that would distinguish `== 0` from `<= 0` are precisely those
    # with a negative total, and every one of them is rejected before the
    # arithmetic is reached. Both are rejected here, naming different faults.
    with pytest.raises(ValueError) as caught:
        comment_ratio_percent(5, -5)
    assert "code_lines" in str(caught.value)
    with pytest.raises(ValueError) as caught:
        comment_ratio_percent(-5, 10)
    assert "comment_lines" in str(caught.value)


def test_finding_3_one_hundred_requires_no_code_at_all():
    # Solved: result == 100  <=>  K == 0 and C >= 1
    assert comment_ratio_percent(1, 0) == 100
    assert comment_ratio_percent(500, 0) == 100
    # and one code line is enough to make 100 unreachable, at any C
    assert comment_ratio_percent(99, 1) == 99
    assert comment_ratio_percent(999, 1) == 99
    assert comment_ratio_percent(100000, 1) == 99


def test_finding_4_zero_does_not_mean_undocumented():
    # Solved: result == 0  <=>  99 * C < K. Either side of that boundary:
    assert comment_ratio_percent(1, 99) == 1     # 99 * 1 < 99 is false
    assert comment_ratio_percent(1, 100) == 0    # 99 * 1 < 100 is true
    assert comment_ratio_percent(5, 500) == 0    # five comments, reported 0
    assert comment_ratio_percent(0, 500) == 0    # and none, reported the same


def test_finding_5_a_large_file_is_insensitive_to_one_comment():
    # Width of the result-1 interval is about N / 100, which is 10 here.
    assert comment_ratio_percent(10, 990) == 1
    assert comment_ratio_percent(11, 990) == 1
    assert comment_ratio_percent(19, 990) == 1
    # it takes ten added comments to move the figure, and even then the
    # denominator has moved with it
    assert comment_ratio_percent(20, 990) == 1
    assert comment_ratio_percent(30, 990) == 2


def test_finding_6_the_function_is_total():
    # One input from each of the four path conditions, confirming the four
    # cover the plane with no gap. Any pair of integers satisfies exactly one.
    with pytest.raises(ValueError):
        comment_ratio_percent(-1, 0)
    with pytest.raises(ValueError):
        comment_ratio_percent(0, -1)
    assert comment_ratio_percent(0, 0) == 0
    assert comment_ratio_percent(1, 1) == 50
