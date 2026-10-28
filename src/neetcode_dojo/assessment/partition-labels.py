"""QUARANTINED assessment for `partition-labels` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("partition-labels")
def _partition_labels_oracle(s: str) -> list[int]:
    """Brute force, straight off the definition: a cut is *allowed* only when no
    letter occurs on both sides of it, and "as many parts as possible" is exactly
    taking every allowed cut. O(n^2) — each candidate cut rebuilds both sides as
    sets — and it builds the whole cut list before emitting a single size, so it
    never stops early.

    The empty string is excluded by 1 <= s.length; it returns [] there (there are
    no parts), which is also what the reference returns."""
    n = len(s)
    if n == 0:
        return []
    cuts: list[int] = []
    for i in range(n - 1):
        if not (set(s[: i + 1]) & set(s[i + 1 :])):
            cuts.append(i + 1)
    sizes: list[int] = []
    prev = 0
    for cut in cuts + [n]:
        sizes.append(cut - prev)
        prev = cut
    return sizes


@cases("partition-labels")
def _partition_labels_case(n: int, rng: random.Random) -> tuple[str, list[int]]:
    n = max(1, min(n, 12))  # the statement's own constraint: 1 <= s.length
    # A small alphabet, so repeats, re-entries and single-letter parts all show
    # up in a 12-character case; occasionally the whole alphabet, for the
    # many-distinct-letters shape.
    width = 26 if rng.random() < 0.25 else rng.randint(1, 4)
    alphabet = "abcdefghijklmnopqrstuvwxyz"[:width]
    s = "".join(rng.choice(alphabet) for _ in range(n))
    return [s], _partition_labels_oracle(s)


@inputs("partition-labels")
def _partition_labels_profiler(n: int, rng: random.Random) -> list:
    # The 26-letter cycle, truncated to n (probe_max_n = 500 keeps n inside the
    # statement's own length bound). Every letter is still ahead of the current
    # part's end, so the greedy's window stretches to the very end of the string
    # (n = 500 comes out as [495, 2, 1, 1, 1, 1]) and its merge loop visits all n
    # indices — nothing to early-exit on. A per-index forward scan for a letter's
    # last occurrence (the obvious quadratic student) walks to the far end of the
    # string from every index, Theta(n^2) at n = 500; the reference does its two
    # linear passes.
    # Values are lowercase English letters, inside the constraint.
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    n = max(1, int(n))
    return [(alphabet * (n // 26 + 1))[:n]]


@reference("partition-labels")
def _partition_labels_reference(s: str) -> list[int]:
    """Canonical greedy: one pass records each letter's last index, a second
    extends the current part's end to every last occurrence seen inside it and
    closes the part exactly when the scan reaches that end. The scan therefore
    visits every index and never stops before the string does; the table holds at
    most 26 entries, which is O(1) for the statement's fixed alphabet."""
    last: dict[str, int] = {}
    for i, ch in enumerate(s):
        last[ch] = i
    sizes: list[int] = []
    start = 0
    end = 0
    for i, ch in enumerate(s):
        if last[ch] > end:
            end = last[ch]
        if i == end:
            sizes.append(i - start + 1)
            start = i + 1
    return sizes


@measure("partition-labels")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
