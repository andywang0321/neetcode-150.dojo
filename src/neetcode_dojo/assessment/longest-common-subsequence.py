"""QUARANTINED assessment for `longest-common-subsequence` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("longest-common-subsequence")
def _longest_common_subsequence_oracle(text1: str, text2: str) -> int:
    """The full (m + 1) x (n + 1) table, filled straight from the definition.

    dp[i][j] is the length of the longest common subsequence of text1[:i] and
    text2[:j]: when the two last characters agree, that character can end a
    common subsequence, so the answer is the diagonal plus one; otherwise the
    answer is the better of dropping one character from either string. That is
    the definition, read as a table, with every cell computed and nothing shared
    with the reference except the recurrence itself -- the reference keeps ONE
    row and has to carry the diagonal by hand, which is the step it can get
    wrong. Total on empty strings (0), which the statement's length >= 1
    excludes and the generator never emits.
    """
    rows, cols = len(text1), len(text2)
    table = [[0] * (cols + 1) for _ in range(rows + 1)]
    for i in range(1, rows + 1):
        row, above = table[i], table[i - 1]
        char = text1[i - 1]
        for j in range(1, cols + 1):
            if char == text2[j - 1]:
                row[j] = above[j - 1] + 1
            else:
                row[j] = above[j] if above[j] > row[j - 1] else row[j - 1]
    return table[rows][cols]


@cases("longest-common-subsequence")
def _longest_common_subsequence_case(n: int, rng: random.Random) -> tuple[list, int]:
    # The caller sends 0..12 and the statement's own bound is
    # 1 <= text1.length, text2.length <= 1000, so both floors are 1: a case with
    # an empty string is not an input this problem has. The five shapes are the
    # ones the recurrence treats differently -- text2 a subsequence of text1
    # (the answer is exactly len(text2), since a common subsequence can never be
    # longer than the shorter string), two identical strings, two disjoint
    # alphabets (the answer is 0, example 3's shape), a two-letter alphabet where
    # repeats make the max() branch decide almost every cell, and one repeated
    # letter, where the whole shorter string is a subsequence. expected always
    # comes from the oracle.
    size = max(1, min(n, 12))
    first = rng.randint(1, size)
    second = rng.randint(1, size)
    mode = n % 5
    if mode == 0:
        text1 = "".join(rng.choice("abc") for _ in range(first))
        text2 = "".join(char for char in text1 if rng.random() < 0.7)
        if not text2:
            text2 = text1[rng.randrange(len(text1))]
    elif mode == 1:
        text1 = "".join(rng.choice("abc") for _ in range(first))
        text2 = text1
    elif mode == 2:
        text1 = "".join(rng.choice("abcde") for _ in range(first))
        text2 = "".join(rng.choice("fghij") for _ in range(second))
    elif mode == 3:
        text1 = "".join(rng.choice("ab") for _ in range(first))
        text2 = "".join(rng.choice("ab") for _ in range(second))
    else:
        text1 = "a" * first
        text2 = "a" * second
    return [text1, text2], _longest_common_subsequence_oracle(text1, text2)


@inputs("longest-common-subsequence")
def _longest_common_subsequence_profiler(n: int, rng: random.Random) -> list:
    # The two strings split the size evenly -- equal lengths maximise m * n for a
    # fixed total, which is the work the reference pays -- and each is capped at
    # the statement's own 1000, so probe_max_n = 2000 puts the ladder's top rung
    # exactly on 1000 + 1000 characters: 31, 62, 125, 250, 500, 1000, 2000, i.e.
    # 15 to 1000 characters a side. text1 is "ab" repeated and text2 is "baa"
    # repeated, two periodic strings of coprime period. Three properties, all
    # measured at every rung of that ladder:
    # (1) The answer is a large fraction of the input. The LCS lengths are
    #     12, 25, 51, 104, 208, 416, 833 -- about 0.83 k -- so a solution that
    #     returns 0, or a constant, digs a hole it cannot climb out of at scale.
    # (2) The longest common SUBSTRING is 3 at every rung, constant. Subsequence
    #     versus substring is the mistake this problem is famous for, and a
    #     substring solution answers 3 where the truth is 833 at the top: the
    #     digest catches it at every measured size.
    # (3) The "sum of the per-letter minimum counts" heuristic answers exactly
    #     one more than the truth at every rung (13, 27, 52, 105, 209, 417, 834),
    #     so that shortcut is caught too. (The obvious alternative family,
    #     "ab" * k against "ba" * k, fails all of this: there the LCS, the
    #     longest common substring and the letter-count heuristic are all k - 1.)
    # There is also nothing to trim: text1 starts with 'a' and text2 with 'b', so
    # no common prefix or suffix exists for a preprocessing step to exploit.
    #
    # NEITHER SIDE CAN EARLY-EXIT. The table recurrence settles every one of the
    # m * n cells and has no branch that skips work, and the memoized top-down
    # form reaches every (i, j) state because it always branches on both "consume
    # from text1" and "consume from text2". The values are inside the statement's
    # own range (lowercase letters, lengths <= 1000), which is what keeps the
    # comparison honest: the answer is at most 1000, so no cell is a big integer
    # and the per-cell cost is the same at every rung.
    #
    # MEASURED COST AT THE TOP RUNG (1000 + 1000, 10^6 cells), so a reviewer can
    # see the cap is affordable rather than argued: the reference takes 167 ms
    # untraced and 3.1 s with tracemalloc active, a full-table student 177 ms and
    # 3.6 s, and their peakiest allocations are 31.3 KiB against 16.5 MiB -- all
    # of it far inside the probe's 20 s per-run bound, and the space difference
    # (one row versus the whole table) is one the ladder's growth can see.
    size = max(1, min(n // 2, 1000))
    text1 = ("ab" * ((size + 1) // 2))[:size]
    text2 = ("baa" * ((size + 2) // 3))[:size]
    return [text1, text2]


@reference("longest-common-subsequence")
def _longest_common_subsequence_reference(text1: str, text2: str) -> int:
    """The 1-D rolling form of the same recurrence: one row, O(min(m, n)) space.

    row[j] is dp[i][j] for the row being built. Two things have to be right for
    the in-place update to work, and both are why this is not the oracle: the
    value under row[j] before the write is still dp[i - 1][j] (the cell above),
    and the diagonal dp[i - 1][j - 1] is gone by then, so it is carried forward
    in `previous` one step at a time. The strings are swapped when text2 is the
    longer one, so the row is the shorter dimension -- O(m * n) time and
    O(min(m, n)) space, the class the statement's complexity line names, and the
    same code path the oracle's full table follows. Total on empty strings (0),
    matching the oracle.
    """
    if len(text2) > len(text1):
        text1, text2 = text2, text1
    cells = len(text2)
    row = [0] * (cells + 1)
    for i in range(1, len(text1) + 1):
        character = text1[i - 1]
        previous = 0  # dp[i - 1][j - 1] for the cell about to be visited
        for j in range(1, cells + 1):
            above = row[j]  # dp[i - 1][j], before this row overwrites it
            if character == text2[j - 1]:
                row[j] = previous + 1
            elif row[j - 1] > above:
                row[j] = row[j - 1]
            previous = above
    return row[cells]


@measure("longest-common-subsequence")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
