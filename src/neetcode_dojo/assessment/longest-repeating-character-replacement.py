"""QUARANTINED assessment for `longest-repeating-character-replacement` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("longest-repeating-character-replacement")
def _longest_repeating_character_replacement_oracle(s: str, k: int) -> int:
    best = 0
    for start in range(len(s)):
        counts: dict[str, int] = {}
        for end in range(start, len(s)):
            counts[s[end]] = counts.get(s[end], 0) + 1
            length = end - start + 1
            if length - max(counts.values()) > k:
                break
            best = max(best, length)
    return best


@cases("longest-repeating-character-replacement")
def _longest_repeating_character_replacement_case(n: int, rng: random.Random) -> tuple[list, int]:
    n = max(1, min(n, 12))  # the statement's own constraint: 1 <= s.length
    s = "".join(rng.choice("ABC") for _ in range(n))
    k = rng.randint(0, n)  # the statement's own constraint: 0 <= k <= s.length
    return [s, k], _longest_repeating_character_replacement_oracle(s, k)


@inputs("longest-repeating-character-replacement")
def _longest_repeating_character_replacement_profiler(n: int, rng: random.Random) -> list:
    # A strict A..Z cycle keeps every window's counts balanced, so the maximum
    # frequency of a window stays near len/26 and the window that satisfies
    # len - maxfreq <= k is about 1.04k long: with k = n // 2 the answer is
    # Theta(n), which is what makes a nested-loop solution measure quadratic
    # instead of looking linear. The window shrinks periodically (the whole
    # string is scanned, there is no early exit) and k sits strictly between the
    # two shortcut values — k > 0 (so the "k = 0, just find the longest run"
    # special case cannot trigger) and k < n - maxfreq_total (so "replace
    # everything, the answer is n" cannot either). Uppercase only, k <= n.
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    s = "".join(letters[i % len(letters)] for i in range(n))
    return [s, n // 2]


@reference("longest-repeating-character-replacement")
def _longest_repeating_character_replacement_reference(s: str, k: int) -> int:
    counts = [0] * 26
    left = 0
    best = 0
    for right, ch in enumerate(s):
        counts[ord(ch) - 65] += 1
        while (right - left + 1) - max(counts) > k:
            counts[ord(s[left]) - 65] -= 1
            left += 1
        best = max(best, right - left + 1)
    return best


@measure("longest-repeating-character-replacement")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
