"""QUARANTINED assessment for `word-ladder` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


def _word_ladder_off_by_one(a: str, b: str) -> bool:
    """True when `a` and `b` are the same length and differ in exactly one
    position (the statement's "differs by a single letter")."""
    if len(a) != len(b):
        return False
    differences = 0
    for x, y in zip(a, b):
        if x != y:
            differences += 1
            if differences > 1:
                return False
    return differences == 1


def _word_ladder_random_words(
    rng: random.Random, alphabet: str, length: int, count: int
) -> list[str]:
    """`count` distinct random words of `length` lowercase letters drawn from
    `alphabet` (fewer only if the alphabet is too small to hold that many, which
    the generator's alphabets never are)."""
    words: list[str] = []
    seen: set[str] = set()
    for _ in range(200 * (count + 1)):
        if len(words) >= count:
            break
        word = "".join(rng.choice(alphabet) for _ in range(length))
        if word in seen:
            continue
        seen.add(word)
        words.append(word)
    return words


@oracle("word-ladder")
def _word_ladder_oracle(beginWord: str, endWord: str, wordList: list[str]) -> int:
    """Brute force: breadth-first search in which a word's neighbours are found by
    scanning the WHOLE list and measuring the Hamming distance -- the classic
    O(N^2 * L) solution, which uses nothing but the statement's definition of
    "differs by a single letter" and builds no graph.

    Total on everything the generator can produce. `beginWord == endWord` is
    excluded by the statement's constraint; the sequence would be [beginWord]
    itself, one word long, and both sides return 1 for it. An `endWord` that is
    not in the list, or one no chain reaches, gives 0, which is the statement's
    own answer for "no such sequence"."""
    if beginWord == endWord:
        return 1
    if endWord not in wordList:
        return 0
    seen = {beginWord}
    frontier = [beginWord]
    steps = 1
    while frontier:
        steps += 1
        next_frontier: list[str] = []
        for word in frontier:
            for candidate in wordList:
                if candidate in seen or not _word_ladder_off_by_one(word, candidate):
                    continue
                if candidate == endWord:
                    return steps
                seen.add(candidate)
                next_frontier.append(candidate)
        frontier = next_frontier
    return 0


@cases("word-ladder")
def _word_ladder_case(n: int, rng: random.Random) -> tuple[list, int]:
    """Both halves of the statement's answer set, built deliberately rather than
    hoped for. `n` is the word list's length here (the statement's own
    `1 <= wordList.length`, clamped to 12 so a case stays small); a case has 1..4
    letter words, which is inside the statement's `<= 10`.

    SOLVABLE (about half): beginWord -> endWord through one intermediate per
    changed position, so the list really does contain a chain of single-letter
    steps; the remaining slots are filled with random words, which may add
    shortcuts (the oracle measures the true shortest sequence, not the chain).

    UNSOLVABLE (the rest): every list word except endWord is spelled from the
    first half of the alphabet and endWord from the second half, so endWord
    differs from ALL of them in ALL `length` positions and is never one mutation
    away. endWord IS in the list, which is what makes it a real unsolvable case
    rather than one your solution can dismiss with "endWord is not in wordList"
    -- the statement's Example 2 is the dismissible kind, and this generator
    produces both."""
    n = max(1, min(n, 12))  # the statement's own range: 1 <= wordList.length
    length = rng.randint(1, 4)  # 1 <= word length <= 10
    left = "abcdefghijklm"
    right = "nopqrstuvwxyz"
    if length >= 2 and rng.random() < 0.5:
        beginWord = "".join(rng.choice(left) for _ in range(length))
        endWord = "".join(rng.choice(right) for _ in range(length))
        # endWord is seeded first so it survives the fill: the whole point of this
        # branch is a list that CONTAINS endWord and still cannot reach it.
        words = [endWord]
        for word in _word_ladder_random_words(rng, left, length, n):
            if len(words) >= n:
                break
            if word not in words and word != beginWord:
                words.append(word)
    else:
        pool = "abcdefgh"
        start = [rng.choice(pool) for _ in range(length)]
        end = list(start)
        # One intermediate per changed position, and never more intermediates than
        # the list can hold, so the chain that makes this case solvable fits inside
        # `words` with endWord still in it.
        positions = rng.sample(range(length), rng.randint(1, min(length, n)))
        for i in positions:
            end[i] = rng.choice([c for c in pool if c != start[i]])
        beginWord = "".join(start)
        endWord = "".join(end)
        chain: list[str] = []
        current = list(start)
        for i in positions:
            current[i] = end[i]
            chain.append("".join(current))  # the last one IS endWord
        words = list(dict.fromkeys(chain))
        for word in _word_ladder_random_words(rng, pool, length, n):
            if len(words) >= n:
                break
            if word not in words and word != beginWord:
                words.append(word)
    rng.shuffle(words)
    return [beginWord, endWord, words], _word_ladder_oracle(beginWord, endWord, words)


@inputs("word-ladder")
def _word_ladder_profiler(n: int, rng: random.Random) -> list:
    # Total size ~n characters: every word is the statement's maximum 10 letters,
    # so the list holds about n // 10 words (the statement allows 5000).
    #
    # The list is one long chain of single-letter mutations, and endWord is spelled
    # from a DISJOINT half of the alphabet, so it differs from every word of the
    # chain in all 10 positions and is unreachable from any of them. Three
    # properties follow, and all three are the point:
    #   * endWord IS in the list, so the "endWord not in wordList" shortcut cannot
    #     answer -- the search has to run.
    #   * beginWord is one mutation away from the chain's first word, so the whole
    #     chain is reachable and the BFS must exhaust it before it can answer 0:
    #     there is no early exit to take, on either side.
    #   * the chain is the deepest, widest thing the answer can hide behind, and a
    #     correct BFS walks all ~n/10 words while a pairwise-scan solution does
    #     its full O(N^2 * L) work.
    # Values stay inside the statement: lowercase, all words the same length
    # (10 <= 10), unique, beginWord != endWord, 1 <= wordList.length <= 5000.
    length = 10
    count = max(3, n // length)
    chain_letters = "abcde"
    end_letters = "vwxyz"
    current = [rng.choice(chain_letters) for _ in range(length)]
    chain = ["".join(current)]
    used = {chain[0]}
    attempts = 0
    while len(chain) < count - 1 and attempts < 50 * count:
        attempts += 1
        i = rng.randrange(length)
        letter = rng.choice([c for c in chain_letters if c != current[i]])
        candidate = "".join(current[:i]) + letter + "".join(current[i + 1 :])
        if candidate in used:
            continue
        used.add(candidate)
        chain.append(candidate)
        current[i] = letter
    begin = list(chain[0])
    i = rng.randrange(length)
    begin[i] = rng.choice([c for c in chain_letters if c != begin[i]])
    endWord = "".join(rng.choice(end_letters) for _ in range(length))
    return ["".join(begin), endWord, chain + [endWord]]


@reference("word-ladder")
def _word_ladder_reference(beginWord: str, endWord: str, wordList: list[str]) -> int:
    """Canonical wildcard-bucket BFS: every word is filed under its L one-letter
    wildcard patterns ("h*t"), so the neighbours of a word are found by looking up
    its own L patterns instead of by scanning the whole list. That is O(N * L^2)
    to build the buckets and O(N * L) for the search, against the pairwise scan's
    O(N^2 * L) -- the intended solution's complexity, with no graph materialized.

    The "endWord is not in wordList -> 0" check stays, because it is the
    statement's own answer and costs O(N) once; what the reference must not do is
    stop the search early on the profiler input, where endWord IS in the list, and
    it does not."""
    if beginWord == endWord:
        return 1
    words = set(wordList)
    if endWord not in words:
        return 0
    length = len(beginWord)
    buckets: dict[str, list[str]] = {}
    for word in words:
        for i in range(length):
            buckets.setdefault(word[:i] + "*" + word[i + 1 :], []).append(word)
    seen = {beginWord}
    frontier = [beginWord]
    steps = 1
    while frontier:
        steps += 1
        next_frontier: list[str] = []
        for word in frontier:
            for i in range(length):
                for candidate in buckets.get(word[:i] + "*" + word[i + 1 :], ()):
                    if candidate in seen:
                        continue
                    if candidate == endWord:
                        return steps
                    seen.add(candidate)
                    next_frontier.append(candidate)
        frontier = next_frontier
    return 0


@measure("word-ladder")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
