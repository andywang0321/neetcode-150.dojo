"""QUARANTINED assessment for `palindrome-partitioning` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, oracle, reference


@oracle("palindrome-partitioning")
def _palindrome_partitioning_oracle(s: str) -> list[list[str]]:
    # Brute force over every set of cut positions: a string of length n has n - 1
    # gaps between its characters, so the 2^(n-1) masks enumerate every partition
    # of s exactly once -- a partition IS a choice of cuts -- and the masks whose
    # every piece reads the same both ways are kept. Nothing is de-duplicated and
    # nothing needs to be: different cut sets produce different piece lists
    # (pieces are non-empty, so the cuts are recoverable from the list), hence
    # the same partition can never appear twice. The empty string is the one case
    # the statement's 1 <= s.length excludes; it has exactly one partition, the
    # empty one, which is also what the reference returns.
    if not s:
        return [[]]
    n = len(s)
    out: list[list[str]] = []
    for mask in range(1 << (n - 1)):
        pieces: list[str] = []
        start = 0
        for i in range(n - 1):
            if mask >> i & 1:
                pieces.append(s[start : i + 1])
                start = i + 1
        pieces.append(s[start:])
        if all(piece == piece[::-1] for piece in pieces):
            out.append(pieces)
    return sorted(out)


@cases("palindrome-partitioning")
def _palindrome_partitioning_case(n: int, rng: random.Random) -> tuple[list, list, dict]:
    # n is clamped to the caller's ceiling (0..12); the statement allows up to
    # 16, so the ceiling only keeps a case cheap for the brute-force oracle
    # (2^(n-1) masks, and a run of one letter at n=12 already answers 2048
    # partitions). The alphabet is lowercase English letters as the statement
    # requires, drawn from "aab" 75% of the time and "abc" the rest: repeated
    # letters are what create palindromes longer than one character, so the
    # two-letter draw makes the answer branch, while the three-letter draw keeps
    # the collapsing cases where the only partition is every character alone
    # (measured by this fragment's self-check, seed 777 / 4000 draws: 20.0% of
    # cases, mean 42 partitions per case, largest 2048).
    n = max(1, min(n, 12))
    alphabet = "aab" if rng.random() < 0.75 else "abc"
    s = "".join(rng.choice(alphabet) for _ in range(n))
    return [s], _palindrome_partitioning_oracle(s), {"compare": "sorted"}


@reference("palindrome-partitioning")
def _palindrome_partitioning_reference(s: str) -> list[list[str]]:
    """Canonical backtracking: from the current cut position, try every prefix of
    the remaining string that is a palindrome and recurse past it. The cuts ARE
    the path, so every partition of s is exactly one root-to-leaf walk, and two
    different walks differ in at least one cut -- with non-empty pieces that
    means different piece lists -- so the answer cannot contain the same
    partition twice and no result-level de-duplication is needed. The palindrome
    test is the obvious slice flip rather than a memoized table: the intended
    complexity is the backtracking itself (time O(n * 2^n) -- at most 2^(n-1)
    partitions, each copied at a cost of up to n -- and space O(n) for the path
    plus the recursion), and a table would only hide that behind a fixed cost."""
    n = len(s)
    out: list[list[str]] = []
    path: list[str] = []

    def _palindrome_partitioning_walk(start: int) -> None:
        if start == n:
            out.append(list(path))
            return
        for end in range(start + 1, n + 1):
            piece = s[start:end]
            if piece == piece[::-1]:
                path.append(piece)
                _palindrome_partitioning_walk(end)
                path.pop()

    _palindrome_partitioning_walk(0)
    return out
