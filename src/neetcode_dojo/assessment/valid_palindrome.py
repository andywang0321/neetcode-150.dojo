"""QUARANTINED assessment for `valid_palindrome` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


def _normalize_palindrome(s: str) -> str:
    return "".join(c for c in s if c.isalnum()).lower()


@oracle("valid_palindrome")
def _is_palindrome_oracle(s: str) -> bool:
    t = _normalize_palindrome(s)
    return t == t[::-1]


@cases("valid_palindrome")
def _is_palindrome_case(n: int, rng: random.Random) -> tuple[list, bool]:
    n = max(0, min(n, 12))
    if rng.random() < 0.5:
        half = "".join(rng.choice("abcdefgh") for _ in range(n // 2))
        mid = rng.choice(["", "x", "!?"]) if n % 2 else ""
        s = half + mid + half[::-1]  # a palindrome (ignoring punctuation)
    else:
        s = "".join(rng.choice("abcdefgh !?,") for _ in range(n))
    return [s], _is_palindrome_oracle(s)


@inputs("valid_palindrome")
def _valid_palindrome_profiler(n: int, rng: random.Random) -> list:
    return ["a" * n]  # a true palindrome: no early mismatch to bail out on


@reference("valid_palindrome")
def is_palindrome(s: str) -> bool:
    i, j = 0, len(s) - 1
    while i < j:
        while i < j and not s[i].isalnum():
            i += 1
        while i < j and not s[j].isalnum():
            j -= 1
        if s[i].lower() != s[j].lower():
            return False
        i += 1
        j -= 1
    return True


@measure("valid_palindrome")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
