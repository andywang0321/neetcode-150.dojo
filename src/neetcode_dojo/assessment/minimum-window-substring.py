"""QUARANTINED assessment for `minimum-window-substring` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, checker, inputs, measure, oracle, reference


@oracle("minimum-window-substring")
def _minimum_window_substring_oracle(s: str, t: str) -> str:
    """Brute force: for each start, extend until the window covers t; the first
    covering window is the shortest one starting at that index."""
    from collections import Counter

    need = Counter(t)
    if not need:
        return ""  # an empty t is covered by the empty window
    best = ""
    for i in range(len(s)):
        have: Counter = Counter()
        for j in range(i, len(s)):
            have[s[j]] += 1
            if all(have[c] >= need[c] for c in need):
                if not best or j - i + 1 < len(best):
                    best = s[i : j + 1]
                break
    return best


@cases("minimum-window-substring")
def _minimum_window_substring_case(n: int, rng: random.Random) -> tuple[list, str, dict]:
    n = max(1, min(n, 12))  # the statement's own constraint: 1 <= m, n <= 10^5
    letters = "abAB"  # English letters; a tiny alphabet so windows collide
    s = "".join(rng.choice(letters) for _ in range(n))
    if rng.random() < 0.5:
        # A substring of s, so a window exists for sure -- and often more than
        # one of minimal length, which is what the predicate verdict is for.
        start = rng.randrange(n)
        t = s[start : start + rng.randint(1, n - start)]
    else:
        t = "".join(rng.choice(letters) for _ in range(rng.randint(1, n)))
    return [s, t], _minimum_window_substring_oracle(s, t), {"predicate": "minimum_window_valid"}


@inputs("minimum-window-substring")
def _minimum_window_substring_profiler(n: int, rng: random.Random) -> list:
    # The only 'b' in s sits on the very last character and t needs n//4 a's,
    # so the window closes exactly there and the shrink phase then walks back
    # over the whole 'a' run: both phases of the two-pointer traverse the
    # string, and t itself is Theta(n) so the n-term of the O(m + n) target is
    # exercised as well as the m-term (a constant-size t would measure only m).
    # The brute-force oracle never breaks early for the first ~3n/4 starts, and
    # no shorter window can cover t. A random string over a small alphabet
    # closes a window almost immediately and would measure the best case.
    size = max(8, n)
    quarter = size // 4
    return ["a" * (size - quarter - 2) + "b", "a" * quarter + "b"]


@reference("minimum-window-substring")
def _minimum_window_substring_reference(s: str, t: str) -> str:
    """Two pointers + a deficit counter over t -- the intended O(m + n)."""
    from collections import Counter

    if not t:
        return ""
    need = Counter(t)
    missing = len(t)  # characters still missing from the window, duplicates counted
    left = 0
    best_start, best_len = 0, len(s) + 1
    for right, ch in enumerate(s):
        if need[ch] > 0:
            missing -= 1
        need[ch] -= 1
        while missing == 0:
            if right - left + 1 < best_len:
                best_start, best_len = left, right - left + 1
            dropped = s[left]
            need[dropped] += 1
            if need[dropped] > 0:
                missing += 1
            left += 1
    return s[best_start : best_start + best_len] if best_len <= len(s) else ""


@checker("minimum_window_valid")
def _minimum_window_substring_valid(module, got, args) -> bool:
    """The contract as a property, because the minimal window is NOT unique.

    Over the statement's own constraints ("abba"/"ab") admits both "ab" and
    "ba" at the minimal length 2; the statement's uniqueness sentence is a
    promise about LeetCode's hidden testcases, not about this function. So the
    checker computes only the minimal *length* -- never the oracle's choice
    among the ties -- and then accepts any substring of s of that length that
    covers t. Equality judging here would false-fail a correct solution that
    picked the other minimal window (the k_closest_points trust bug)."""
    from collections import Counter

    s, t = args
    if not isinstance(got, str):
        return False
    need = Counter(t)
    if not need:
        return got == ""  # an empty t is covered by the empty window
    best = None
    for i in range(len(s)):
        have: Counter = Counter()
        for j in range(i, len(s)):
            have[s[j]] += 1
            if all(have[c] >= need[c] for c in need):
                if best is None or j - i + 1 < best:
                    best = j - i + 1
                break
    if best is None:
        return got == ""  # nothing in s covers t: "" is the only answer
    if len(got) != best:
        return False
    if any(got.count(c) < need[c] for c in need):
        return False
    return any(s[i : i + best] == got for i in range(len(s) - best + 1))


@measure("minimum-window-substring")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    none."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'none'}
