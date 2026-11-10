"""Concolic testing for classify_line - US01, Gunjan (gsk17).

Technique: concolic (dynamic symbolic) execution. Starting from one arbitrary
seed, each iteration runs the function concretely, collects the path condition
it took, negates the last unexplored branch, and solves for the next input.
The three tests below are those three iterations, in order; together they drive
every path in the function from a single seed.

Full derivation: docs/symbolic/gsk17-symbolic-execution.md, section 5.
"""

from core.scanner import classify_line


def test_iteration_1_seed():
    # seed: "x = 1" (arbitrary)
    # path taken: P3, collected PC: T != empty and T[0] != '#'
    # negate T[0] != '#'  ->  next input must satisfy T[0] = '#'
    assert classify_line("x = 1") == "code"


def test_iteration_2_negate_the_hash_clause():
    # solved from iteration 1: shortest string with T[0] = '#'
    # path taken: P2, collected PC: T != empty and T[0] = '#'
    # frontier at b2 is now empty, so backtrack to b1 and negate T != empty
    assert classify_line("#x") == "comment"


def test_iteration_3_negate_the_non_empty_clause():
    # solved from iteration 2: shortest string with T = empty
    # path taken: P1. No unexplored branches remain - the function has no
    # loops, so the execution tree is finite and the frontier is exhausted.
    assert classify_line("") == "blank"
