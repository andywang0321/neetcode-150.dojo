"""QUARANTINED assessment for `permutation-in-string` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("permutation-in-string")
def _permutation_in_string_oracle(s1: str, s2: str) -> bool:
    target = sorted(s1)
    width = len(s1)
    for start in range(len(s2) - width + 1):
        if sorted(s2[start : start + width]) == target:
            return True
    return False


@cases("permutation-in-string")
def _permutation_in_string_case(n: int, rng: random.Random) -> tuple[list, bool]:
    size = max(1, min(n, 12))  # the statement's own constraint: both lengths >= 1
    a = rng.randint(1, size)
    b = rng.randint(1, size)  # drawn independently: s1 longer than s2 is a legal input
    s1 = "".join(rng.choice("ab") for _ in range(a))
    s2 = "".join(rng.choice("ab") for _ in range(b))
    return [s1, s2], _permutation_in_string_oracle(s1, s2)


@inputs("permutation-in-string")
def _permutation_in_string_profiler(n: int, rng: random.Random) -> list:
    # s1 is an "ab" cycle of about n/4 characters and s2 an "abc" cycle holding
    # the rest, so the total size is ~n. The window width grows with n, which is
    # what makes a per-window O(len(s1)) or O(len(s1) log len(s1)) solution
    # (Counter- or sorted-comparison per window) measure quadratic, while n2 - n1
    # is still about n/2 window positions for the reference. No window can match:
    # every stretch of >= 3 consecutive characters of the "abc" cycle contains a
    # "c", and s1 contains none — so the answer is False all the way and nothing
    # early-exits. Both strings are lowercase English letters.
    width = max(3, n // 4)
    rest = max(1, n - width)
    s1 = ("ab" * (width // 2 + 1))[:width]
    s2 = ("abc" * (rest // 3 + 1))[:rest]
    return [s1, s2]


@reference("permutation-in-string")
def _permutation_in_string_reference(s1: str, s2: str) -> bool:
    width = len(s1)
    if width > len(s2):
        return False
    need = [0] * 26
    for ch in s1:
        need[ord(ch) - 97] += 1
    window = [0] * 26
    for ch in s2[:width]:
        window[ord(ch) - 97] += 1
    if window == need:
        return True
    for i in range(width, len(s2)):
        window[ord(s2[i]) - 97] += 1
        window[ord(s2[i - width]) - 97] -= 1
        if window == need:
            return True
    return False


@measure("permutation-in-string")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
