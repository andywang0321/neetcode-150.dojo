"""Test fixture assessment: the ``sorted`` comparison mode."""

import random

from neetcode_dojo.registry import cases, measure, oracle, reference


def _groups(strs: list[str]) -> list[list[str]]:
    grouped: dict[str, list[str]] = {}
    for item in strs:
        grouped.setdefault("".join(sorted(item)), []).append(item)
    return [sorted(group) for _, group in sorted(grouped.items())]


@oracle("group_anagrams")
def _oracle(strs: list[str]) -> list[list[str]]:
    return _groups(strs)


@cases("group_anagrams")
def _cases(n: int, rng: random.Random) -> tuple[list, list, dict]:
    count = max(0, min(n, 12))
    strs = ["".join(rng.choice("ab") for _ in range(rng.randint(1, 4))) for _ in range(count)]
    return [strs], _groups(strs), {"compare": "sorted"}


@reference("group_anagrams")
def group_anagrams(strs: list[str]) -> list[list[str]]:
    return _groups(strs)


@measure("group_anagrams")
def _measure(ctx: dict) -> dict:
    return {"axis": "n", "sizes": [32], "baseline": "reference", "compare": "sorted"}
