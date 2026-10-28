"""QUARANTINED assessment for `palindromic-substrings` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("palindromic-substrings")
def _palindromic_substrings_oracle(s: str) -> int:
    """Brute force by definition: mark every substring that reads the same both
    ways, fill the table by increasing length, count the marks. Total on the
    empty string (0), which the statement's 1 <= s.length excludes."""
    n = len(s)
    if n == 0:
        return 0
    pal = [[False] * n for _ in range(n)]
    total = 0
    for i in range(n):
        pal[i][i] = True
        total += 1
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            if s[i] == s[j] and (length == 2 or pal[i + 1][j - 1]):
                pal[i][j] = True
                total += 1
    return total


@cases("palindromic-substrings")
def _palindromic_substrings_case(n: int, rng: random.Random) -> tuple[list, int]:
    n = max(1, min(n, 12))  # the statement's own floor: 1 <= s.length <= 1000
    roll = rng.random()
    if roll < 0.22:
        # one repeated letter: every one of the n(n+1)/2 substrings counts, which
        # is the density no other shape reaches
        s = rng.choice("abcdefghijklmnopqrstuvwxyz") * n
    elif roll < 0.45 and n >= 2:
        s = ("ab" * n)[:n]  # both centre parities, and overlapping repeats
    elif roll < 0.70 and n >= 3:
        # a palindrome of exactly n characters: the whole string is counted, and
        # so are all of its inner palindromes -- a shape no example reaches
        half = n // 2
        core = "".join(rng.choice("abc") for _ in range(half))
        s = core + (rng.choice("abc") if n % 2 else "") + core[::-1]
    else:
        # a three-letter alphabet: overlaps by accident, and single-character
        # palindromes dominate, which is the other end of the range
        s = "".join(rng.choice("abc") for _ in range(n))
    return [s], _palindromic_substrings_oracle(s)


@inputs("palindromic-substrings")
def _palindromic_substrings_profiler(n: int, rng: random.Random) -> list:
    # The same shape as LC 5's probe input, for the same reasons: one letter with
    # a different letter at the end maximises expansion work for both
    # implementations (the counting reference and the DP oracle both do their
    # full Theta(n^2)), every character is inside the alphabet, and there is no
    # "the whole string is a palindrome" exit.
    return ["a" * (n - 1) + "b" if n > 1 else "a"]


@reference("palindromic-substrings")
def _palindromic_substrings_reference(s: str) -> int:
    """Expand around every center and count each palindrome exactly once -- the
    intended O(n^2) time / O(1) extra space."""
    total = 0
    n = len(s)
    for center in range(n):
        lo, hi = center, center
        while lo >= 0 and hi < n and s[lo] == s[hi]:
            total += 1
            lo -= 1
            hi += 1
        lo, hi = center, center + 1
        while lo >= 0 and hi < n and s[lo] == s[hi]:
            total += 1
            lo -= 1
            hi += 1
    return total


@measure("palindromic-substrings")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
