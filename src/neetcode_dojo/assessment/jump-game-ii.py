"""QUARANTINED assessment for `jump-game-ii` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("jump-game-ii")
def _jump_game_ii_oracle(nums: list[int]) -> int:
    """Brute force: the minimum-jumps DP. best[i] is the fewest jumps that reach
    index i, relaxed over every jump length from every index — O(n^2), and it
    fills the whole table rather than returning at the first hit, so it cannot
    early-exit on the profiler input.

    A position no path reaches stays at n + 1 (no route needs more than n - 1
    jumps) and is reported as -1; the statement guarantees that never happens,
    and the generator's guarantee is checked against this answer."""
    n = len(nums)
    if n <= 1:
        return 0
    unreachable = n + 1
    best = [unreachable] * n
    best[0] = 0
    for i in range(n):
        if best[i] == unreachable:
            continue
        for j in range(i + 1, min(n, i + nums[i] + 1)):
            if best[i] + 1 < best[j]:
                best[j] = best[i] + 1
    return best[-1] if best[-1] != unreachable else -1


@cases("jump-game-ii")
def _jump_game_ii_case(n: int, rng: random.Random) -> tuple[list, int]:
    n = max(1, min(n, 12))  # the statement's own constraint: 1 <= nums.length
    # The statement guarantees nums[n - 1] is reachable, so the case is built to
    # be: a random walk lays a path down first and every index it lands on keeps
    # at least the step it needs. Extra reach anywhere else only helps.
    nums = [rng.randint(0, 3) for _ in range(n)]
    idx = 0
    while idx < n - 1:
        step = rng.randint(1, min(3, n - 1 - idx))
        nums[idx] = max(nums[idx], step)
        idx += step
    return [nums], _jump_game_ii_oracle(nums)


@inputs("jump-game-ii")
def _jump_game_ii_profiler(n: int, rng: random.Random) -> list:
    # All ones: a strictly increasing staircase of reach. The level boundary
    # advances by exactly one index per level, so the greedy pays a jump at every
    # index and first reaches index n - 1 only on its (n - 1)-th level — there is
    # no `farthest >= n - 1` shortcut to take and no level that swallows the rest
    # of the array. The DP oracle re-relaxes the whole table too, one jump length
    # per index, and the values respect the statement's 0 <= nums[i] <= 1000.
    return [[1] * max(1, n)]


@reference("jump-game-ii")
def _jump_game_ii_reference(nums: list[int]) -> int:
    """Canonical level-BFS greedy: one pass remembering where the current jump
    lands (cur_end) and the farthest index the whole level can reach (farthest);
    each time the scan reaches cur_end, one more jump has been spent.

    The reachability guard keeps the reference total and makes it agree with the
    oracle (which answers -1) on an array the statement's guarantee excludes; on
    graded and measured inputs it never fires."""
    jumps = 0
    cur_end = 0
    farthest = 0
    for i in range(len(nums) - 1):
        if i > farthest:
            return -1  # index i is unreachable: there is no route to the end
        farthest = max(farthest, i + nums[i])
        if i == cur_end:
            jumps += 1
            cur_end = farthest
    return jumps


@measure("jump-game-ii")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
