"""Test fixture assessment whose oracle disagrees with its case expected answers."""

import random

from neetcode_dojo.registry import cases, oracle


@oracle("oracle_drift")
def _oracle(value: int) -> int:
    return value + 1


@cases("oracle_drift")
def _cases(n: int, rng: random.Random) -> tuple[list, int]:
    value = rng.randint(0, max(1, n))
    return [value], value + 2  # deliberately wrong: the oracle says +1
