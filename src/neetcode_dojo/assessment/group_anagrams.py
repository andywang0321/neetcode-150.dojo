"""QUARANTINED assessment for `group_anagrams` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("group_anagrams")
def _group_anagrams_oracle(strs: list[str]) -> list[list[str]]:
    groups: dict[str, list[str]] = {}
    for s in strs:
        groups.setdefault("".join(sorted(s)), []).append(s)
    return [sorted(group) for _, group in sorted(groups.items())]


@cases("group_anagrams")
def _group_anagrams_case(n: int, rng: random.Random) -> tuple[list, list, dict]:
    n = max(0, min(n, 12))
    strs = ["".join(rng.choice("ab") for _ in range(rng.randint(1, 4))) for _ in range(n)]
    return [strs], _group_anagrams_oracle(strs), {"compare": "sorted"}


@inputs("group_anagrams")
def _group_anagrams_profiler(n: int, rng: random.Random) -> list:
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    return [["".join(rng.choice(alphabet) for _ in range(8)) for _ in range(n)]]


@reference("group_anagrams")
def group_anagrams(strs: list[str]) -> list[list[str]]:
    groups: dict[tuple[int, ...], list[str]] = {}
    for s in strs:
        counts = [0] * 26
        for ch in s:
            counts[ord(ch) - 97] += 1
        key = tuple(counts)
        groups.setdefault(key, []).append(s)
    return [sorted(group) for _, group in sorted(groups.items())]


@measure("group_anagrams")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
