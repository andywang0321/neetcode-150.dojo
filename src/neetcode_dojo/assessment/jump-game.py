"""QUARANTINED assessment for `jump-game` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("jump-game")
def _jump_game_oracle(nums: list[int]) -> bool:
    """Brute force: fill a reachability table by trying every jump length from
    every index that turned out to be reachable. No shortcut on success — the
    whole table is filled, so it cannot early-exit on the profiler input.

    Total on the empty list (excluded by the statement's length >= 1): there is
    no last index to reach, so the answer is False, and the reference agrees."""
    n = len(nums)
    if n == 0:
        return False
    reachable = [False] * n
    reachable[0] = True
    for i in range(n):
        if not reachable[i]:
            continue
        for j in range(i + 1, min(n, i + nums[i] + 1)):
            reachable[j] = True
    return reachable[-1]


@cases("jump-game")
def _jump_game_case(n: int, rng: random.Random) -> tuple[list, bool]:
    n = max(1, min(n, 12))  # the statement's own constraint: 1 <= nums.length
    nums = [rng.randint(0, 3) for _ in range(n)]
    if rng.random() < 0.4:
        # One long jump somewhere: values in 0..3 alone leave most short arrays
        # unsolvable, and both answers have to show up in the generated cases.
        nums[rng.randrange(n)] = rng.randint(0, n)
    return [nums], _jump_game_oracle(nums)


@inputs("jump-game")
def _jump_game_profiler(n: int, rng: random.Random) -> list:
    # All ones: the frontier advances by exactly one index per step, so
    # `reach >= n - 1` first holds at index n - 2 — the latest index it can hold
    # at, since a jump of 1 is the shortest that can finish the array — and the
    # pass has to visit every index to find that out. The reachability table has
    # nothing to early-exit on either: one jump length per index and no value big
    # enough to shortcut to the end. (A student that re-scans the array per index
    # is still quadratic here; a student that scans the *jump lengths* is not,
    # and cannot be — no solvable array both lags the frontier this way and has
    # sum(nums) = O(n^2).)
    return [[1] * max(1, n)]


@reference("jump-game")
def _jump_game_reference(nums: list[int]) -> bool:
    """Canonical greedy: one pass, carrying the farthest index reachable so far;
    an index beyond that frontier means the array cannot be finished, and if the
    pass survives every index then the last one was reachable.

    Deliberately written without the mid-loop `reach >= n - 1 -> True` shortcut,
    so the probe's baseline always reads the whole array (on the profiler input
    the shortcut would fire two indices early); the answer is the same either way.
    The empty list is excluded by the constraint, but the guard keeps the
    reference identical to the oracle on every input the gate could hand it."""
    if not nums:
        return False  # no last index to reach
    reach = 0
    for i, jump in enumerate(nums):
        if i > reach:
            return False  # unreachable, and so is everything past it
        reach = max(reach, i + jump)
    return reach >= len(nums) - 1


@measure("jump-game")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
