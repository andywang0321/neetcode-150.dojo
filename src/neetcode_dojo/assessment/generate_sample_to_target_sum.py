"""QUARANTINED assessment for `generate_sample_to_target_sum` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, checker


@cases("generate_sample_to_target_sum")
def _generate_sample_case(n: int, rng: random.Random) -> tuple[list, bool, dict]:
    n = max(1, min(n, 12))
    sigma = round(rng.uniform(1.0, 4.0), 1)  # >= 1: the even split is always feasible
    target = rng.randint(-20, 20)
    return [n, sigma, target], True, {"predicate": "sample_valid"}


@checker("sample_valid")
def _sample_valid(module, got, args) -> bool:
    """Exactly n integers, summing to target, standard deviation <= sigma."""
    n, sigma, target = args
    if not isinstance(got, list) or len(got) != n or any(not isinstance(x, int) for x in got):
        return False
    if sum(got) != target:
        return False
    mu = target / n
    variance = sum((x - mu) ** 2 for x in got) / n
    return variance**0.5 <= sigma + 1e-9
