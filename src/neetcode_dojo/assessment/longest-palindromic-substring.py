"""QUARANTINED assessment for `longest-palindromic-substring` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, checker, inputs, measure, oracle, reference


@oracle("longest-palindromic-substring")
def _longest_palindromic_substring_oracle(s: str) -> str:
    """Brute force by definition: a table over every substring, filled by
    increasing length, then the longest one -- leftmost on a tie, which is what
    the statement's own Example 1 prints ("bab", not "aba"). Total on the empty
    string, which the statement's 1 <= s.length excludes."""
    n = len(s)
    if n == 0:
        return ""
    pal = [[False] * n for _ in range(n)]
    for i in range(n):
        pal[i][i] = True
    best_i, best_len = 0, 1
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            if s[i] == s[j] and (length == 2 or pal[i + 1][j - 1]):
                pal[i][j] = True
                if length > best_len:
                    best_i, best_len = i, length
    return s[best_i : best_i + best_len]


@cases("longest-palindromic-substring")
def _longest_palindromic_substring_case(n: int, rng: random.Random) -> tuple[list, str, dict]:
    """Half the draws are strings with MORE THAN ONE maximal palindrome, because
    that is the whole reason this problem is graded by a predicate rather than by
    equality -- every case carries {"predicate": "longest_palindrome_valid"}."""
    n = max(1, min(n, 12))  # the statement's own floor: 1 <= s.length <= 1000
    alphabet = "abcdefghijklmnopqrstuvwxyz0123456789"  # digits and English letters
    roll = rng.random()
    if n >= 5 and roll < 0.30:
        # p q p r p with three distinct symbols: "pqp" and "prp" are both
        # maximal, and the length-5 string is not a palindrome (q != r).
        p, q, r = rng.sample(alphabet, 3)
        s = p + q + p + r + p
    elif n >= 4 and roll < 0.55:
        # an alternating pair: for even n every maximal palindrome is length n-1
        # and there are two of them ("aba"/"bab" at n = 4); for odd n >= 5 the
        # whole string IS a palindrome, so the longest one is unique there.
        a, b = rng.sample(alphabet, 2)
        s = ((a + b) * n)[:n]
    elif n >= 5 and roll < 0.70:
        # a palindrome of length n-1 with one character appended: the example-2
        # shape ("cbbd"), where the answer is a proper substring.
        half = (n - 1) // 2
        core = "".join(rng.choice(alphabet[:4]) for _ in range(half))
        core = core + (rng.choice(alphabet[:4]) if (n - 1) % 2 else "") + core[::-1]
        s = core + rng.choice(alphabet)
    else:
        # a random string over three symbols: ties happen by accident, which the
        # deterministic shapes above do not cover.
        s = "".join(rng.choice(alphabet[:3]) for _ in range(n))
    return [s], _longest_palindromic_substring_oracle(s), {"predicate": "longest_palindrome_valid"}


@inputs("longest-palindromic-substring")
def _longest_palindromic_substring_profiler(n: int, rng: random.Random) -> list:
    # One letter with a different letter at the end: every one of the 2n-1
    # centers expands to the boundary (~500k expansion steps at n = 1000,
    # measured), and the string is NOT itself a palindrome, so "is the whole
    # string a palindrome?" is not a free exit. A random string is unusable as a
    # probe input: over "ab" it averages ~4.8k expansion steps at n = 1600, i.e.
    # it would measure both implementations as flat.
    return ["a" * (n - 1) + "b" if n > 1 else "a"]


@reference("longest-palindromic-substring")
def _longest_palindromic_substring_reference(s: str) -> str:
    """Expand around every center -- the intended O(n^2) time / O(1) extra space
    (the returned substring is not counted, the merge-two-sorted-lists
    convention). Leftmost on a tie, like the oracle, though the verdict does not
    depend on that."""
    n = len(s)
    best_start, best_len = 0, 0
    for center in range(n):
        lo, hi = center, center
        while lo >= 0 and hi < n and s[lo] == s[hi]:
            lo -= 1
            hi += 1
        if hi - lo - 1 > best_len:
            best_start, best_len = lo + 1, hi - lo - 1
        lo, hi = center, center + 1
        while lo >= 0 and hi < n and s[lo] == s[hi]:
            lo -= 1
            hi += 1
        if hi - lo - 1 > best_len:
            best_start, best_len = lo + 1, hi - lo - 1
    return s[best_start : best_start + best_len]


@checker("longest_palindrome_valid")
def _longest_palindromic_substring_valid(module, got, args) -> bool:
    """The statement's contract as a property, because the longest palindromic
    substring is NOT unique. The statement says so itself -- Example 1 prints
    "bab" with the explanation "'aba' is also a valid answer" -- and the
    generator emits inputs with two or more maximal palindromes on purpose.

    So this computes only the MAXIMAL LENGTH, never the oracle's choice among the
    ties, and accepts any palindromic substring of s of that length: the
    k_closest_points / minimum_window_valid lesson, where a checker that
    reimplements the oracle's tie-break turns a correct answer into a failed
    case. It rejects a non-string, a string that is not a substring of s, a
    string that is not a palindrome, and any palindrome shorter than the maximum.
    """
    s = args[0]
    if not isinstance(got, str) or got != got[::-1] or got not in s:
        return False
    return len(got) == _longest_palindromic_substring_max_len(s)


def _longest_palindromic_substring_max_len(s: str) -> int:
    """The length of the longest palindromic substring of ``s`` -- the DP table
    again, but read as a length and with no choice among ties."""
    n = len(s)
    if n == 0:
        return 0
    pal = [[False] * n for _ in range(n)]
    best = 1
    for i in range(n):
        pal[i][i] = True
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            if s[i] == s[j] and (length == 2 or pal[i + 1][j - 1]):
                pal[i][j] = True
                best = length
    return best


@measure("longest-palindromic-substring")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    none."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'none'}
