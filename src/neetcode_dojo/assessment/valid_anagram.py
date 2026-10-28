"""QUARANTINED assessment for `valid_anagram` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("valid_anagram")
def _valid_anagram_oracle(s: str, t: str) -> bool:
    return sorted(s) == sorted(t)


@cases("valid_anagram")
def _valid_anagram_case(n: int, rng: random.Random) -> tuple[list, bool]:
    n = max(0, min(n, 12))
    s = "".join(rng.choice("abcdefgh") for _ in range(n))
    if rng.random() < 0.5:
        chars = list(s)
        rng.shuffle(chars)
        t = "".join(chars)
    else:
        t = "".join(rng.choice("abcdefgh") for _ in range(n))
    return [s, t], _valid_anagram_oracle(s, t)


@inputs("valid_anagram")
def _valid_anagram_profiler(n: int, rng: random.Random) -> list:
    s = ("abcdefgh" * (n // 8 + 1))[:n]
    chars = list(s)
    rng.shuffle(chars)
    return [s, "".join(chars)]


@reference("valid_anagram")
def valid_anagram(s: str, t: str) -> bool:
    if len(s) != len(t):
        return False
    counts = [0] * 26
    for ch in s:
        counts[ord(ch) - 97] += 1
    for ch in t:
        counts[ord(ch) - 97] -= 1
    return all(c == 0 for c in counts)


@measure("valid_anagram")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
