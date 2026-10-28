"""QUARANTINED assessment for `median-of-two-sorted-arrays` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("median-of-two-sorted-arrays")
def _median_of_two_sorted_arrays_oracle(nums1: list[int], nums2: list[int]) -> float | None:
    """Brute force: merge both arrays (sorted() is the merge), take the middle —
    the mean of the two middle elements when the total is even. Written to be
    total on two empty arrays, though the statement requires m + n >= 1."""
    merged = sorted(nums1 + nums2)
    size = len(merged)
    if size == 0:
        return None
    mid = size // 2
    if size % 2:
        return float(merged[mid])
    return (merged[mid - 1] + merged[mid]) / 2


@cases("median-of-two-sorted-arrays")
def _median_of_two_sorted_arrays_case(
    n: int, rng: random.Random
) -> tuple[list, float, dict]:
    size = max(1, min(n, 12))  # the statement's own bound: 1 <= m + n
    m = rng.randint(0, size)  # either side may be empty (0 <= m, 0 <= n)
    k = size - m
    # Values are inside [-10^6, 10^6]; duplicates are allowed by the statement
    # (only "sorted" is promised), and the median of a multiset is unique anyway.
    nums1 = sorted(rng.randint(-1_000_000, 1_000_000) for _ in range(m))
    nums2 = sorted(rng.randint(-1_000_000, 1_000_000) for _ in range(k))
    expected = _median_of_two_sorted_arrays_oracle(nums1, nums2)
    return [nums1, nums2], expected, {"compare": "approx:1e-5"}


@inputs("median-of-two-sorted-arrays")
def _median_of_two_sorted_arrays_profiler(n: int, rng: random.Random) -> list:
    # An even total split evenly and interleaved: both halves are non-empty,
    # strictly increasing, and neither dominates, so the partition search does
    # its full log(min(m, n)).
    #
    # The merged middle pair is (v, v + 1) by construction, so the median is a
    # half-integer: every correct solution returns exactly the same float, which
    # is what lets the probe's exact digest comparison accept a correct answer
    # instead of blaming it for an int/float spelling (an odd total would let a
    # solution legally return the int middle element and disagree with this
    # reference's float on the digest alone).
    total = max(2, n - (n % 2))
    merged = [-1_000_000 + i for i in range(total)]  # distinct, ascending, in range
    return [merged[0::2], merged[1::2]]


@reference("median-of-two-sorted-arrays")
def _median_of_two_sorted_arrays_reference(nums1: list[int], nums2: list[int]) -> float | None:
    """Canonical O(log min(m, n)): binary search how many elements of the smaller
    array sit left of the split, so that everything on the left is <= everything
    on the right; the median then reads off the four boundary values."""
    a, b = (nums1, nums2) if len(nums1) <= len(nums2) else (nums2, nums1)
    m, n = len(a), len(b)
    if m + n == 0:
        return None
    half = (m + n + 1) // 2  # the left side holds this many elements
    lo, hi = 0, m
    while lo <= hi:
        i = (lo + hi) // 2  # elements of a on the left
        j = half - i  # elements of b on the left
        left_a = a[i - 1] if i > 0 else float("-inf")
        right_a = a[i] if i < m else float("inf")
        left_b = b[j - 1] if j > 0 else float("-inf")
        right_b = b[j] if j < n else float("inf")
        if left_a > right_b:
            hi = i - 1
        elif left_b > right_a:
            lo = i + 1
        else:
            if (m + n) % 2:
                return float(max(left_a, left_b))
            return (max(left_a, left_b) + min(right_a, right_b)) / 2
    raise ValueError("median of two sorted arrays: inputs are not sorted")


@measure("median-of-two-sorted-arrays")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
