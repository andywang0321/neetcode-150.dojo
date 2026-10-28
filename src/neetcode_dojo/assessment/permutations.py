"""QUARANTINED assessment for `permutations` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, oracle, reference


@oracle("permutations")
def _permutations_oracle(nums: list[int]) -> list[list[int]]:
    # Brute force by construction: start from the arrangement of the first value
    # and insert each next value into every position of every arrangement built so
    # far. Correct by induction — an arrangement's position for the last value is
    # unique, so each of the n! arrangements is reached exactly once, and nothing
    # else can be: the values are distinct, which the statement guarantees and the
    # generator upholds (a repeated value would make several insertion paths
    # produce the same list and the answer would stop being a set). The final sort
    # is the canonical (ascending-lexicographic) form of that set answer, which is
    # also the order the statement's own examples print.
    out: list[list[int]] = [[]]
    for value in nums:
        grown: list[list[int]] = []
        for arr in out:
            for i in range(len(arr) + 1):
                grown.append(arr[:i] + [value] + arr[i:])
        out = grown
    return sorted(out)


@cases("permutations")
def _permutations_case(n: int, rng: random.Random) -> tuple[list, list, dict]:
    # The statement's constraints, upheld exactly: 1 <= nums.length <= 6,
    # -10 <= nums[i] <= 10, and "All the integers of nums are unique" — n distinct
    # values from the statement's own range. Distinctness is what keeps the answer
    # a *set*: with a repeated value, [2, 2] would be one arrangement reachable
    # through two different index choices, and a correct solution that returned
    # the other copy would be false-failed. The statement's own cap of 6 is also
    # what keeps the answer real but small: 720 permutations at the top.
    n = max(1, min(n, 6))
    nums = rng.sample(range(-10, 11), n)
    if rng.random() < 0.5:
        nums.sort()  # the statement's examples are ascending; an unordered input is legal too
    return [nums], _permutations_oracle(nums), {"compare": "sorted"}


@reference("permutations")
def _permutations_reference(nums: list[int]) -> list[list[int]]:
    """Canonical backtracking: walk the values in sorted order, marking each one
    used and unmarking it on the way back out, so every arrangement is built
    exactly once and the result comes out ascending-lexicographic — the canonical
    form of a set answer (and the order the statement's examples print).

    O(n * n!) time: n! leaves, each copied out in O(n). O(n) auxiliary space: the
    path, the used flags and the recursion depth — the returned list of
    permutations is not counted."""
    values = sorted(nums)
    n = len(values)
    used = [False] * n
    path: list[int] = []
    out: list[list[int]] = []

    def _permutations_walk() -> None:
        if len(path) == n:
            out.append(list(path))
            return
        for i in range(n):
            if used[i]:
                continue
            used[i] = True
            path.append(values[i])
            _permutations_walk()
            path.pop()
            used[i] = False

    _permutations_walk()
    return out
