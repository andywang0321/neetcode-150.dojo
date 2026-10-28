"""QUARANTINED assessment for `encode_and_decode_strings` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, checker


@cases("encode_and_decode_strings")
def _encode_decode_case(n: int, rng: random.Random) -> tuple[list, bool, dict]:
    n = max(0, min(n, 12))
    strs = [
        "".join(rng.choice("ab:, !?") for _ in range(rng.randint(0, 6)))
        for _ in range(rng.randint(0, n))
    ]
    return [strs], True, {"predicate": "encode_decode_roundtrip"}


@checker("encode_decode_roundtrip")
def _encode_decode_roundtrip(module, got, args) -> bool:
    """decode(encode(strs)) == strs — the contract for encode_and_decode_strings."""
    return module.decode(got) == args[0]
