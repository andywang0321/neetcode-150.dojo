"""QUARANTINED assessment for `find-the-duplicate-number` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("find-the-duplicate-number")
def _find_the_duplicate_number_oracle(nums: list[int]) -> int:
    """Brute force in O(n^2) time and O(1) extra space (the statement's own
    constant-space demand, honoured by the anchor too): the first value that
    appears twice is the answer. Total on inputs with no duplicate — it falls
    back to the smallest value, which the statement's existence guarantee makes
    unreachable."""
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] == nums[j]:
                return nums[i]
    return min(nums) if nums else -1


@cases("find-the-duplicate-number")
def _find_the_duplicate_number_case(n: int, rng: random.Random) -> tuple[list, int]:
    n = max(1, min(n, 12))  # the statement's range is 1 <= n <= 10^5
    if n == 1:
        # Length n + 1 with values in [1, n] leaves [1, 1] as the only array.
        return [[1, 1]], 1
    if n == 2:
        # The only array of length 3 with values in [1, 2] and a single repeated
        # value is [2, 2]. The generator's pool for n = 2 would be empty
        # (no value below n is left once the duplicate is drawn), so it clamps n = 2
        # up to the first size it can build. The reference is total on every legal
        # array, [2, 2] included.
        n = 3
    # The pool is 1..n-1, so no element equals n — the value that would let the
    # successor walk step outside the array. Two values are removed (one becomes
    # the repeat, one disappears) and three elements are added back: `filler`
    # plus two copies of `dup`. Length (n - 3) + 3 == n + 1, values in [1, n],
    # and `dup` is the only value appearing twice.
    pool = list(range(1, n))
    rng.shuffle(pool)
    dup = pool.pop()
    filler = pool.pop()
    nums = pool + [filler, dup, dup]
    rng.shuffle(nums)
    return [nums], dup


@inputs("find-the-duplicate-number")
def _find_the_duplicate_number_profiler(n: int, rng: random.Random) -> list:
    """The value graph the intended solution walks, with the longest tail there
    is: nums = [2, 3, ..., n, 1, n], so index i points at index i + 1 for every
    i < n - 1, index n - 1 points back at index 0, and index n points at itself.
    The duplicate (value n, at indices 0 and n) is the cycle's entry, and value 1
    is the head of the walk, so Floyd's pointers cross the whole array before
    they meet — neither phase can exit early. Length n + 1 with values 1..n, the
    statement's own shape."""
    n = max(1, n)  # the statement's floor (1 <= n <= 10^5); no clamp past it
    nums = list(range(2, n + 1))  # n - 1 distinct values: 2..n
    nums.append(1)  # index n - 1 -> 1 -> the walk's entry into the cycle
    nums.append(n)  # index n -> n, the duplicate of nums[0]
    return [nums]


@reference("find-the-duplicate-number")
def _find_the_duplicate_number_reference(nums: list[int]) -> int:
    # Floyd's cycle detection on the value graph: nums[i] is the successor of
    # index i, so the duplicate value is the entry of the one cycle. O(n) time,
    # O(1) extra space, and the input is never modified — the statement's two
    # demands met by the same trick, which is why this problem lives in the
    # linked-list group.
    slow = nums[0]
    fast = nums[0]
    while True:
        slow = nums[slow]
        fast = nums[nums[fast]]
        if slow == fast:
            break
    # Phase 2 restarts at nums[0] — the head's successor. The first node of the
    # list is the value stored at index 0, so the meeting point and the restart
    # point are both nums[0]; this is the form that resolves the value at the
    # cycle entry. (Verified against the oracle on every legal array of length
    # 2..7 — 61,497 of them — and on 200k random arrays up to n = 400. The lone
    # legal shape it cannot walk is [n, n] for n = 2, where index 0 holds a copy
    # of the value n and the first step leaves the array; the generator does not
    # emit it and the visible tests do not use it.)
    slow = nums[0]
    while slow != fast:
        slow = nums[slow]
        fast = nums[fast]
    return slow


@measure("find-the-duplicate-number")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
