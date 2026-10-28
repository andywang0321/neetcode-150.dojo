"""QUARANTINED assessment for `top_k_frequent_elements` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


def _unique_counts(n: int, rng: random.Random) -> list[int]:
    """Distinct positive counts summing to n — the top-k prompt promises
    'the answer is always unique', so generated frequencies must be unique
    (a frequency tie would make equality judging false-fail)."""
    counts: list[int] = []
    total = 0
    c = 1
    while total + c <= n:
        counts.append(c)
        total += c
        c += 1
    if total < n:
        remainder = n - total
        if remainder in counts:
            counts[-1] += remainder  # stays unique: > every existing count
        else:
            counts.append(remainder)
    rng.shuffle(counts)
    return counts


@oracle("top_k_frequent_elements")
def _top_k_freq_oracle(nums: list[int], k: int) -> list[int]:
    counts: dict[int, int] = {}
    for num in nums:
        counts[num] = counts.get(num, 0) + 1
    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return [value for value, _ in ranked[:k]]


@cases("top_k_frequent_elements")
def _top_k_freq_case(n: int, rng: random.Random) -> tuple[list, list, dict]:
    n = max(1, min(n, 12))
    counts = _unique_counts(n, rng)
    nums = []
    for i, count in enumerate(counts):
        nums.extend([i - 10] * count)
    rng.shuffle(nums)
    k = rng.randint(1, len(counts))
    return [nums, k], _top_k_freq_oracle(nums, k), {"compare": "sorted"}


@inputs("top_k_frequent_elements")
def _top_k_freq_profiler(n: int, rng: random.Random) -> list:
    values = list(range(n))
    rng.shuffle(values)
    return [values, max(1, n // 2)]


@reference("top_k_frequent_elements")
def _top_k_freq_reference(nums: list[int], k: int) -> list[int]:
    """Frequency buckets — the intended O(n).

    Mirrors the oracle's tie-break exactly (count descending, then value
    ascending): the gate compares the two under the judge's own equality, so a
    reference that broke ties differently would be — correctly — refused."""
    counts: dict[int, int] = {}
    for num in nums:
        counts[num] = counts.get(num, 0) + 1
    buckets: dict[int, list[int]] = {}
    for value, count in counts.items():
        buckets.setdefault(count, []).append(value)
    out: list[int] = []
    for count in sorted(buckets, reverse=True):
        for value in sorted(buckets[count]):
            out.append(value)
            if len(out) == k:
                return out
    return out


@measure("top_k_frequent_elements")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
