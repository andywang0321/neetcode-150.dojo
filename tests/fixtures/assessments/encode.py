"""Test fixture assessment: a predicate case decided by the module's checker."""

import random

from neetcode_dojo.registry import cases, checker


@cases("encode")
def _cases(n: int, rng: random.Random) -> tuple[list, bool, dict]:
    strs = [
        "".join(rng.choice("ab:, !?") for _ in range(rng.randint(0, 6)))
        for _ in range(rng.randint(0, max(0, min(n, 12))))
    ]
    return [strs], True, {"predicate": "encode_roundtrip"}


@checker("encode_roundtrip")
def _roundtrip(module, got, args) -> bool:
    return module.decode(got) == args[0]
