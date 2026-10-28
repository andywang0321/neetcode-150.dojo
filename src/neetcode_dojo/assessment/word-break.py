"""QUARANTINED assessment for `word-break` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("word-break")
def _word_break_oracle(s: str, word_dict: list[str]) -> bool:
    """Brute force: try every dictionary word at the current position and recurse
    -- the statement's definition, one word at a time. The memo only stops the
    same suffix from being explored twice; it cannot change the answer, and it is
    what keeps the oracle total on the profiler input (300 positions x ~300
    dictionary words).

    The empty string is answered False, honouring "one or more dictionary
    words". The constraints exclude it and the generator never emits it; the
    reference makes the same choice so the two agree."""
    words = set(word_dict)
    n = len(s)
    if n == 0:
        return False
    memo: dict[int, bool] = {}

    def can(i: int) -> bool:
        if i == n:
            return True
        if i in memo:
            return memo[i]
        memo[i] = any(can(i + len(w)) for w in words if s.startswith(w, i))
        return memo[i]

    return can(0)


@cases("word-break")
def _word_break_case(n: int, rng: random.Random) -> tuple[list, bool]:
    """The dictionary is built the only way the statement allows: distinct
    entries, lowercase letters, at most 20 characters, at least one of them (a
    duplicate is dropped rather than emitted -- "All the strings of wordDict are
    unique"). The first branch makes reuse of a word the visible structure of the
    case, and the second is the greedy trap, which is where this problem's most
    common wrong answer dies."""
    n = max(1, min(n, 12))  # the statement's own floors: 1 <= s.length, 1 <= wordDict.length
    roll = rng.random()
    if roll < 0.30:
        # TRUE by construction: cut a random string into pieces and put exactly
        # those pieces in the dictionary, so a segmentation exists (and the
        # statement's "may be reused multiple times" is exercised whenever two
        # cuts produce the same piece).
        s = "".join(rng.choice("ab") for _ in range(n))
        cuts = sorted(rng.sample(range(1, n), min(n - 1, rng.randint(0, 3))))
        pieces, prev = [], 0
        for cut in cuts + [n]:
            pieces.append(s[prev:cut])
            prev = cut
        word_dict = list(dict.fromkeys(pieces))
    elif roll < 0.55 and n >= 3:
        # A GREEDY TRAP: s = short + rest is segmentable as short | rest, but the
        # dictionary also holds a longer word that is a proper prefix of s and
        # leads nowhere -- the "cars" / ["car", "ca", "rs"] shape of the added
        # visible test 5. The answer is True by construction; a longest-match
        # greedy scan usually fails it.
        s = "".join(rng.choice("ab") for _ in range(n))
        cut = rng.randint(1, n - 2)
        short, rest = s[:cut], s[cut:]
        trap = s[: cut + rng.randint(1, len(rest) - 1)]
        word_dict = list(dict.fromkeys([short, rest, trap]))
    else:
        # a small dictionary over three letters against a random string: the
        # answer is whatever the dictionary happens to allow, and every letter of
        # s is covered by some word, so no character-set pre-check decides it
        word_dict = list(
            dict.fromkeys(
                "".join(rng.choice("abc") for _ in range(rng.randint(1, 4)))
                for _ in range(rng.randint(1, 4))
            )
        )
        s = "".join(rng.choice("abc") for _ in range(n))
    return [s, word_dict], _word_break_oracle(s, word_dict)


@inputs("word-break")
def _word_break_profiler(n: int, rng: random.Random) -> list:
    # s = "a"*(n-1) + "b" against a dictionary of ~n words: {"aa", "b"} plus
    # words over a disjoint alphabet, which therefore can never be substrings of
    # s (pure distractors, and they cost the reference's set lookup the same as
    # a real word).
    #
    # What it forces: the reference's split scan can only match through the
    # two-letter "aa" step, so for half the positions it walks all the way back
    # with no break (measured ~n^2 growth across the ladder). The dictionary is
    # ~n entries, so the word-per-position transcription pays its full
    # O(n * |wordDict|) too, and the two land within a factor of ~2.5 of each
    # other across the ladder rather than a whole class apart. "b" keeps every
    # character of s inside some dictionary word, so a "this character is in no
    # word" pre-check cannot decide it; and the answer is False for even n, so no
    # correct solver can stop as soon as it finds a segmentation.
    n = max(2, n)
    s = "a" * (n - 1) + "b"
    words = ["aa", "b"]
    while len(words) < min(1000, n):
        candidate = "".join(rng.choice("cdefgh") for _ in range(rng.randint(1, 10)))
        if candidate not in words:
            words.append(candidate)
    return [s, words]


@reference("word-break")
def _word_break_reference(s: str, word_dict: list[str]) -> bool:
    """The canonical bottom-up DP: dp[i] is True when s[:i] can be segmented.
    Each position looks back for the nearest split that lands on a dictionary
    word and stops there -- O(n^2) time and O(n) space, with a set so a lookup is
    O(1). Total on the empty string (False: "one or more dictionary words"),
    which the statement's 1 <= s.length excludes."""
    words = set(word_dict)
    n = len(s)
    if n == 0:
        return False
    dp = [False] * (n + 1)
    dp[0] = True
    for i in range(1, n + 1):
        for j in range(i - 1, -1, -1):
            if dp[j] and s[j:i] in words:
                dp[i] = True
                break
    return dp[n]


@measure("word-break")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
