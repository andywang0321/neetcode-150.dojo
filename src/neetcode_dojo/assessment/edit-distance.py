"""QUARANTINED assessment for `edit-distance` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("edit-distance")
def _edit_distance_oracle(word1: str, word2: str) -> int:
    # The statement's three operations, tried directly: walk both words from the
    # front and, whenever the heads differ, pay one operation and recurse on the
    # three pairs it can produce. A genuinely different program from the
    # reference's table -- top-down over suffixes, recursive, driven by the two
    # heads rather than by two nested loops that fill a table in order -- and the
    # memo changes only the cost: without it the recursion is 3^(m+n), the honest
    # brute force, which cannot finish even at the generator's own 12-character
    # ceiling. The memo is a plain table of solved suffix pairs (a dict keyed by
    # the pair is 1.9x slower here and buys nothing). Total on the empty string on
    # either side, which the statement's 0 <= length allows and the generator does
    # emit. The recursion is m + n deep, which is why the profiler input stops at
    # 400 + 400 characters (probe_max_n = 800).
    m, n = len(word1), len(word2)
    memo = [[-1] * (n + 1) for _ in range(m + 1)]

    def solve(i: int, j: int) -> int:
        if i == m:
            return n - j
        if j == n:
            return m - i
        cached = memo[i][j]
        if cached >= 0:
            return cached
        if word1[i] == word2[j]:
            best = solve(i + 1, j + 1)
        else:
            best = 1 + min(solve(i + 1, j), solve(i, j + 1), solve(i + 1, j + 1))
        memo[i][j] = best
        return best

    return solve(0, 0)


@cases("edit-distance")
def _edit_distance_case(n: int, rng: random.Random) -> tuple[list, int]:
    # The statement's own sizes (0 <= length <= 500) clamped to the 0..12 the
    # caller sends, in five shapes that between them cover what the two examples
    # cannot: both words empty (n = 0), exactly one word empty on either side
    # (the answer is the other word's whole length), the two words identical (0,
    # and the shape that punishes a solution which replaces everything), disjoint
    # alphabets (every cell takes the mismatch branch), and a two-letter draw
    # where the words share characters heavily. Expected values come from the
    # oracle in every case.
    n = max(0, min(n, 12))
    if n == 0:
        return ["", ""], _edit_distance_oracle("", "")
    mode = n % 4
    if mode == 1:
        other = "".join(rng.choice("abc") for _ in range(n))
        word1, word2 = (other, "") if rng.random() < 0.5 else ("", other)
    elif mode == 2:
        word1 = "".join(rng.choice("ab") for _ in range(n))
        word2 = word1
    elif mode == 3:
        word1 = "".join(rng.choice("abc") for _ in range(n))
        word2 = "".join(rng.choice("xyz") for _ in range(n))
    else:
        word1 = "".join(rng.choice("ab") for _ in range(n))
        word2 = "".join(rng.choice("ab") for _ in range(n))
    return [word1, word2], _edit_distance_oracle(word1, word2)


@inputs("edit-distance")
def _edit_distance_profiler(n: int, rng: random.Random) -> list:
    # Two words whose lengths sum to ~n, split evenly and clamped to the
    # statement's own 500 per word: at the top of the ladder that is 400 + 400,
    # the largest pair the oracle's m + n deep recursion still solves inside
    # Python's default limit -- which is what probe_max_n = 800 encodes (the same
    # reason the corpus's tree inputs are complete trees rather than spines: a
    # canonical recursive student solution must not meet the recursion limit
    # because of the profiler input).
    # The alphabets are DISJOINT, so every one of the m * n cells takes the
    # three-way min branch: no cell can match, no row or column is cheaper than
    # its neighbours, and the answer is max(m, n) -- nothing here is reachable by
    # short-circuiting a prefix, and the whole table's work happens on both
    # sides. Values are the statement's lowercase English letters.
    size = max(2, min(int(n), 800))
    half = size // 2
    return ["a" * half, "b" * (size - half)]


@reference("edit-distance")
def _edit_distance_reference(word1: str, word2: str) -> int:
    # The canonical edit-distance table, bottom-up: table[i][j] is the cost of
    # turning word1[:i] into word2[:j], so every cell is one character comparison
    # plus a min() over three cells that are already final. O(m * n) time and
    # O(m * n) space -- exactly the class the statement's complexity line
    # declares -- and total on the empty string on either side (column 0 is
    # 0..m, row 0 is 0..n), which the generator emits and the visible tests pin.
    m, n = len(word1), len(word2)
    table = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        table[i][0] = i
    for j in range(n + 1):
        table[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if word1[i - 1] == word2[j - 1]:
                table[i][j] = table[i - 1][j - 1]
            else:
                table[i][j] = 1 + min(
                    table[i - 1][j], table[i][j - 1], table[i - 1][j - 1]
                )
    return table[m][n]


@measure("edit-distance")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
