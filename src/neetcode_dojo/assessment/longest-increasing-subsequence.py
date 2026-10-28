"""QUARANTINED assessment for `longest-increasing-subsequence` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("longest-increasing-subsequence")
def _longest_increasing_subsequence_oracle(nums: list[int]) -> int:
    # Brute force: the length of the longest strictly increasing subsequence
    # ENDING at each index, found by looking back at every earlier index. O(n^2),
    # obviously correct -- such a subsequence either starts at i or continues one
    # that ends at some j < i with nums[j] < nums[i] -- and a genuinely different
    # program from the reference: no tails array, no binary search, and no
    # assumption that anything is sorted. Total on the empty list (0), which the
    # statement's length >= 1 excludes.
    dp = [1] * len(nums)
    for i in range(len(nums)):
        for j in range(i):
            if nums[j] < nums[i] and dp[j] + 1 > dp[i]:
                dp[i] = dp[j] + 1
    return max(dp) if dp else 0


@cases("longest-increasing-subsequence")
def _longest_increasing_subsequence_case(n: int, rng: random.Random) -> tuple[list, int]:
    # Four shapes, all inside the statement's constraints (1 <= nums.length <= 2500,
    # -10^4 <= nums[i] <= 10^4): strictly increasing, strictly decreasing, all
    # equal (the statement's example 3), and a narrow-range draw where duplicates
    # are common -- duplicates are what make the word "strictly" load-bearing, and
    # a non-decreasing (>=) comparison passes the first two shapes but fails here.
    n = max(1, min(n, 12))
    mode = n % 4
    if mode == 0:
        values = sorted(rng.sample(range(-10_000, 10_001), n))
    elif mode == 1:
        values = sorted(rng.sample(range(-10_000, 10_001), n), reverse=True)
    elif mode == 2:
        values = [rng.randint(-10_000, 10_000)] * n
    else:
        values = [rng.randint(-5, 5) for _ in range(n)]
    return [values], _longest_increasing_subsequence_oracle(values)


@inputs("longest-increasing-subsequence")
def _longest_increasing_subsequence_profiler(n: int, rng: random.Random) -> list:
    # A strictly increasing ramp of `size` values, 1..size, clamped to the
    # statement's own length bound (2500, hence probe_max_n). Two properties make
    # the O(n^2) / O(n log n) difference visible rather than argued: the tails
    # array grows to its full length (the reference appends on every element, so
    # each of its n binary searches runs over the whole current array -- n log n
    # with nothing to short-circuit), and every earlier value is smaller than the
    # current one, so a quadratic student's inner loop cannot stop at the first
    # value it fails to beat: it walks the whole prefix at every index. The answer
    # is the whole array (size), so any correct solution returns the same digest.
    # A decreasing or random ramp would let an inner loop stop early at a large
    # element and would measure the shortcut instead of the algorithm.
    size = max(1, min(int(n), 2500))
    return [[index + 1 for index in range(size)]]


@reference("longest-increasing-subsequence")
def _longest_increasing_subsequence_reference(nums: list[int]) -> int:
    # The patience (tails) algorithm the statement's follow-up asks for: tails[k]
    # is the smallest value an increasing subsequence of length k + 1 can end
    # with, which is what keeps tails sorted, so each element costs one
    # bisect_left. Finding the position of the first tail >= value and overwriting
    # it (or appending when every tail is smaller) preserves that invariant; the
    # length of tails is the answer. O(n log n) time and O(n) space. `bisect` is
    # imported inside the function because the probe runs this source in its own
    # subprocess, where the registry's module-level imports are not in scope. Total
    # on the empty list (0), matching the oracle.
    import bisect

    tails: list[int] = []
    for value in nums:
        position = bisect.bisect_left(tails, value)
        if position == len(tails):
            tails.append(value)
        else:
            tails[position] = value
    return len(tails)


@measure("longest-increasing-subsequence")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
