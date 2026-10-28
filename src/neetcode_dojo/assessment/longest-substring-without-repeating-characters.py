"""QUARANTINED assessment for `longest-substring-without-repeating-characters` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("longest-substring-without-repeating-characters")
def _longest_substring_without_repeating_characters_oracle(s: str) -> int:
    best = 0
    for start in range(len(s)):
        seen: set[str] = set()
        for end in range(start, len(s)):
            if s[end] in seen:
                break
            seen.add(s[end])
            best = max(best, end - start + 1)
    return best


@cases("longest-substring-without-repeating-characters")
def _longest_substring_without_repeating_characters_case(n: int, rng: random.Random) -> tuple[list, int]:
    n = max(0, min(n, 12))  # the statement's own constraint is 0 <= s.length: n = 0 stays 0
    alphabet = "abcABC12 ."  # letters, digits, a symbol and a space — the statement's own set
    s = "".join(rng.choice(alphabet) for _ in range(n))
    return [s], _longest_substring_without_repeating_characters_oracle(s)


@inputs("longest-substring-without-repeating-characters")
def _longest_substring_without_repeating_characters_profiler(n: int, rng: random.Random) -> list:
    # A shuffled cycle through (almost) every character the statement allows.
    # Every window of at most len(chars) consecutive characters is repeat-free,
    # so the window grows to the alphabet's own size — the longest a repeat-free
    # substring can be under these constraints — instead of stopping early on a
    # repeat, and the cycle keeps the left pointer moving. Values stay inside
    # "English letters, digits, symbols and spaces".
    chars = list(
        "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        " .,;:!?+-*/=_()[]{}<>@#$%&|~^`"
    )
    rng.shuffle(chars)
    cycle = "".join(chars)
    return ["".join(cycle[i % len(cycle)] for i in range(n))]


@reference("longest-substring-without-repeating-characters")
def _longest_substring_without_repeating_characters_reference(s: str) -> int:
    last: dict[str, int] = {}
    left = 0
    best = 0
    for right, ch in enumerate(s):
        if ch in last and last[ch] >= left:
            left = last[ch] + 1
        last[ch] = right
        best = max(best, right - left + 1)
    return best


@measure("longest-substring-without-repeating-characters")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
