"""QUARANTINED assessment for `subsets-ii` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, oracle, reference


@oracle("subsets-ii")
def _subsets_ii_oracle(nums: list[int]) -> list[list[int]]:
    # Brute force over all 2^n index subsets, then de-duplicate by the *sorted*
    # value tuple. Both halves are deliberate. The index enumeration is the
    # obvious total one (it yields the empty subset without a special case), and
    # the sorted key is what the statement's "must not contain duplicate
    # subsets" means once nums repeats a value: in [1,2,2] the index sets {0,1}
    # and {0,2} both spell the subset [1,2]. Sorting the key also makes a
    # subset's form independent of the order its copies were visited in, so
    # [2,1] and [1,2] are one answer and not two. `sorted(...)` over the tuple
    # set is the canonical output order the visible tests show.
    subsets = set()
    for mask in range(1 << len(nums)):
        subsets.add(tuple(sorted(nums[i] for i in range(len(nums)) if mask >> i & 1)))
    return sorted(list(subset) for subset in subsets)


@cases("subsets-ii")
def _subsets_ii_case(n: int, rng: random.Random) -> tuple[list, list, dict]:
    # n is clamped to the statement's own 1 <= nums.length <= 10 (the caller
    # sends 0..12) and every value stays inside -10 <= nums[i] <= 10. Values come
    # from a 7-value pool, and when n >= 2 a second copy of nums[0] is injected
    # with probability 0.6: duplicates are the entire difference between this
    # problem and LC 78, so leaving them to chance would leave the
    # duplicate-skipping path untested at small n. Measured over 20k draws (this
    # fragment's self-check, seed 1234): 78.7% of cases carry a repeat -- 66% at
    # n=2, 86% at n=4, 100% at n>=7; n=1 cannot have one, since a single element
    # has nothing to repeat.
    n = max(1, min(n, 10))
    nums = [rng.randint(-3, 3) for _ in range(n)]
    if n >= 2 and rng.random() < 0.6:
        nums[rng.randrange(1, n)] = nums[0]
    return [nums], _subsets_ii_oracle(nums), {"compare": "sorted"}


@reference("subsets-ii")
def _subsets_ii_reference(nums: list[int]) -> list[list[int]]:
    """Canonical sort + backtracking: grow every subset once, and at the level of
    the search where an earlier copy of a repeated value already built that
    branch, skip it. Sorting puts equal values next to each other, so
    `i > start and ordered[i] == ordered[i - 1]` is exactly "this branch repeats
    the one the previous copy just built" -- the answer never needs a
    result-level de-duplication pass. Paths grow in non-decreasing order because
    the array is sorted, so every subset comes out in the ascending form the
    site's own expected output uses (Example 1 is
    [[], [1], [1,2], [1,2,2], [2], [2,2]]). Time O(n * 2^n) -- at most 2^n
    subsets, each copied once at a cost of up to n -- and space O(n) for the path
    plus the recursion."""
    ordered = sorted(nums)
    out: list[list[int]] = []
    path: list[int] = []

    def _subsets_ii_walk(start: int) -> None:
        out.append(list(path))
        for i in range(start, len(ordered)):
            if i > start and ordered[i] == ordered[i - 1]:
                continue  # the previous copy already explored this branch
            path.append(ordered[i])
            _subsets_ii_walk(i + 1)
            path.pop()

    _subsets_ii_walk(0)
    return out
