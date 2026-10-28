"""QUARANTINED assessment for `merge-two-sorted-lists` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("merge-two-sorted-lists")
def _merge_two_sorted_lists_oracle(list1: list[int], list2: list[int]) -> list[int]:
    """Brute force: concatenate the two lists and sort. Merging two sorted lists
    produces their combined values in non-decreasing order, which is exactly what
    sorted() returns, so this is obviously correct and knows nothing about
    pointers. O((m + k) log(m + k)) - the honest differential against the
    reference's single merge pass. Total on two empty lists (example 2)."""
    return sorted([*list1, *list2])


@cases("merge-two-sorted-lists")
def _merge_two_sorted_lists_case(n: int, rng: random.Random) -> tuple[list, list[int]]:
    size = max(0, min(n, 12))  # the statement's total is at most 50 + 50 nodes
    first = rng.randint(0, size)  # either list may be empty - both may be (example 2)
    second = size - first
    # Values are inside the statement's [-100, 100]; duplicates are allowed (both
    # lists are only promised to be non-decreasing), and sorting each draw is what
    # makes that promise true.
    list1 = sorted(rng.randint(-100, 100) for _ in range(first))
    list2 = sorted(rng.randint(-100, 100) for _ in range(second))
    return [list1, list2], _merge_two_sorted_lists_oracle(list1, list2)


@inputs("merge-two-sorted-lists")
def _merge_two_sorted_lists_profiler(n: int, rng: random.Random) -> list:
    # A strictly increasing ramp of n values inside the statement's [-100, 100],
    # split alternately between the two lists. Both lists are non-decreasing and
    # (for n >= 2) non-empty, and they interleave perfectly: every step of the
    # merge is a comparison, no run can be copied wholesale, and neither side can
    # be handed back untouched - the early exits this input has to defeat.
    #
    # One value per node inside a 201-value range makes 201 this input's hard
    # ceiling; probe_max_n = 100 keeps the whole ladder inside the statement's 50
    # nodes per list (50 + 50 at the top) and far below the ceiling. The ladder's
    # smallest point is n = 1, where one side is necessarily empty - a legal input
    # (the statement allows a 0-node list), just not a demanding one.
    size = max(1, min(n, 201))
    values = [-100 + i for i in range(size)]
    return [values[0::2], values[1::2]]


@reference("merge-two-sorted-lists")
def _merge_two_sorted_lists_reference(list1: list[int], list2: list[int]) -> list[int]:
    # The intended single pass: one index per list, take the smaller head each
    # time (<= keeps the merge stable, which no case can observe - the merged
    # multiset is the same either way), then drain whichever list is left. O(n)
    # time over n = m + k nodes and O(1) extra space: `merged` is the only list it
    # allocates, so the tails are drained with appends rather than slices.
    merged: list[int] = []
    i = 0
    j = 0
    while i < len(list1) and j < len(list2):
        if list1[i] <= list2[j]:
            merged.append(list1[i])
            i += 1
        else:
            merged.append(list2[j])
            j += 1
    while i < len(list1):
        merged.append(list1[i])
        i += 1
    while j < len(list2):
        merged.append(list2[j])
        j += 1
    return merged


@measure("merge-two-sorted-lists")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
