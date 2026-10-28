"""QUARANTINED assessment for `alien-dictionary` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, checker, inputs, measure, oracle, reference


@oracle("alien-dictionary")
def _alien_dictionary_oracle(words: list[str]) -> str:
    """The definition of the answer, with no heap and no indegree bookkeeping:
    keep taking the alphabetically smallest letter whose implied predecessors
    have all been placed.

    The constraints are exactly the statement's own. For each adjacent pair, the
    first position where the two words differ says "this letter comes before
    that one"; if one word is a prefix of the next the pair is CONSISTENT -- and
    a valid order really does make every adjacent pair sorted, so a list that is
    only locally consistent is sorted as a whole, which is why the definition is
    faithful to "taken from the dictionary, sorted lexicographically". The one
    thing no alphabet can explain is the FIRST word being the longer one, which
    makes the list invalid and the answer "". Validity, not speed, is this
    anchor's job: the selection is a linear scan, so the oracle is O(v^2 + v * e)
    with v <= 26, and if no letter is free while letters remain, the constraints
    contain a cycle -- the same "" an unrecoverable list gets. Total on [] and on
    [""] (the statement's 1 <= words.length and 1 <= words[i].length exclude
    both)."""
    letters = sorted({ch for word in words for ch in word})
    precedes: set[tuple[str, str]] = set()
    for first, second in zip(words, words[1:]):
        for a, b in zip(first, second):
            if a != b:
                precedes.add((a, b))
                break
        else:
            if len(first) > len(second):
                return ""
    placed: list[str] = []
    remaining = list(letters)
    while remaining:
        pick = None
        for ch in remaining:
            if all((before, ch) not in precedes for before in remaining):
                pick = ch
                break
        if pick is None:
            return ""  # every remaining letter waits on another: a cycle
        remaining.remove(pick)
        placed.append(pick)
    return "".join(placed)


@cases("alien-dictionary")
def _alien_dictionary_case(n: int, rng: random.Random) -> tuple[list, str, dict]:
    """Words of 1..3 lowercase letters over a 2..5 letter alphabet, in five
    shapes chosen by one roll so a 12-case batch reaches all of them:

      * an unrecoverable CYCLE (words like [a, b, a], which imply a < b and
        b < a) -- the statement's "If no valid order exists" path;
      * a longer word before its own PREFIX ([head + x, head]), the other
        unrecoverable shape, whose implied constraints are perfectly acyclic --
        so it is the case that separates "the graph has a cycle" from "the list
        is invalid";
      * a prefix pair the right way round ([head, head + x]): CONSISTENT, and
        the shorter word's letters are related to nothing, so several orders are
        valid;
      * a genuinely sorted dictionary under a randomly shuffled alien order,
        built by sorting with the order's own rank list (a prefix compares less
        than its extension, exactly as the statement's rule says);
      * a forced CHAIN (word i = order[i] + order[i + 1]), where every letter is
        pinned by a relation and exactly one order is valid.

    Word count is clamp(n, 1, 12) and every word is non-empty and lowercase, so
    the statement's own 1..100 bounds hold with room to spare. `expected` is the
    oracle's answer -- one valid order, never the only one -- and every case
    carries the predicate tag, so the judge grades what the statement grades.
    """
    size = max(1, min(n, 12))
    alphabet = "abcde"[: max(2, min(5, size + 1))]
    roll = rng.random()
    if roll < 0.20:
        a, b = rng.sample(alphabet, 2)
        words = [a, b, a]
    elif roll < 0.35:
        head = "".join(rng.choice(alphabet) for _ in range(rng.randint(1, 3)))
        words = [head + rng.choice(alphabet), head]
    elif roll < 0.50:
        head = "".join(rng.choice(alphabet) for _ in range(rng.randint(1, 3)))
        words = [head, head + rng.choice(alphabet)]
    elif roll < 0.75:
        order = list(alphabet)
        rng.shuffle(order)
        words = sorted(
            (
                "".join(
                    rng.choice(order[: rng.randint(2, len(order))])
                    for _ in range(rng.randint(1, 3))
                )
                for _ in range(size)
            ),
            key=lambda word: [order.index(ch) for ch in word],
        )
    else:
        order = list(alphabet)
        rng.shuffle(order)
        words = [order[i] + order[i + 1] for i in range(len(order) - 1)]
        if size > len(words):
            words = words + [words[-1]] * (size - len(words))
    return [words], _alien_dictionary_oracle(words), {"predicate": "valid_alien_order"}


@inputs("alien-dictionary")
def _alien_dictionary_profiler(n: int, rng: random.Random) -> list:
    """A dictionary whose every adjacent pair shares a long common prefix and
    differs in its LAST character, with a total of ~n characters.

    Each pair therefore forces both implementations to scan the pair's whole
    length before the relation appears -- there is no early exit to take -- and
    the letters b..z are chained b < c < ... < z, so the topological sort is
    real work over 25 letters even though the alphabet is fixed. Repeating the
    last word fills the rest of the budget: a pair of identical words is
    consistent, adds no edge and still costs a full scan, which is what keeps
    the reference's cost proportional to the character count the ladder scales
    (an implementation that compares every PAIR of words instead of every
    adjacent pair pays the square of it, and the ratio trend says so).
    word length is clamped to 1..100 and the word count to 1..100, so the input
    is inside the statement's own bounds at every rung -- 100 x 100 = 10,000
    characters, which is why the default 6400 ladder needs no probe_max_n. rng is
    unused: a paired measurement wants the same deterministic input at every
    rung."""
    total = max(2, n)
    length = max(1, min(100, total // 64))
    count = max(1, min(100, total // length))
    pad = "a" * (length - 1)
    letters = "bcdefghijklmnopqrstuvwxyz"
    words = [pad + letters[index] for index in range(min(len(letters), count))]
    while len(words) < count:
        words.append(words[-1])
    return [words]


@reference("alien-dictionary")
def _alien_dictionary_reference(words: list[str]) -> str:
    """Canonical Kahn's algorithm: O(n) time and O(1) space, where n is the total
    number of characters across all the words (the graph is over at most 26
    letters, so everything except the scan of the words is a constant).

    One pass builds the edge set from the adjacent pairs and the indegrees, then
    a queue seeded with the letters nothing precedes emits a topological order.
    Two details the statement insists on: an edge is only counted once even when
    several adjacent pairs imply it (a double count would leave a letter with a
    positive indegree forever and be misreported as a cycle), and if some letters
    are never emitted the constraints contain a cycle -- an unrecoverable list --
    which is the "" answer. The same "" comes back for a longer word placed
    before its own prefix, which no order can explain."""
    from collections import deque  # the probe runs this snippet alone

    letters = {ch for word in words for ch in word}
    followers: dict[str, set[str]] = {ch: set() for ch in letters}
    indegree: dict[str, int] = {ch: 0 for ch in letters}
    for first, second in zip(words, words[1:]):
        for a, b in zip(first, second):
            if a != b:
                if b not in followers[a]:
                    followers[a].add(b)
                    indegree[b] += 1
                break
        else:
            if len(first) > len(second):
                return ""
    queue = deque(sorted(ch for ch in letters if indegree[ch] == 0))
    order: list[str] = []
    while queue:
        ch = queue.popleft()
        order.append(ch)
        for follower in sorted(followers[ch]):
            indegree[follower] -= 1
            if indegree[follower] == 0:
                queue.append(follower)
    if len(order) != len(letters):
        return ""  # a cycle left some letters unemitted
    return "".join(order)


@checker("valid_alien_order")
def _valid_alien_order(module, got, args) -> bool:
    """The predicate this problem is graded by: ANY order the words allow.

    It reads the implied "a comes before b" relations off the adjacent pairs --
    the same rule the oracle reads, because that rule IS the problem -- and then
    judges the candidate against them, so it never reimplements the oracle's
    choice among the valid orders. A submission is accepted exactly when:

      * it is a string listing EVERY letter appearing in words, each exactly once
        (the statement says "any string of the unique letters in the alien
        language"; the language here is the letters the words actually use, which
        is why Example 2 answers "zx" and not the 26-letter alphabet) and every
        implied relation holds in it -- so a correct answer ordered differently
        from the oracle's passes, and a single reversed relation fails; or
      * it is "" and the list is genuinely unrecoverable, which happens two ways:
        a longer word placed before its own prefix (no order of letters can make
        that list sorted), or a cycle among the implied relations (no permutation
        satisfies them). The second is decided by peeling: remove the letters
        nothing unplaced precedes, repeat, and a letter left waiting on itself is
        a cycle. The peel only decides whether an order EXISTS -- it never picks
        one, so it is not the oracle's selection in disguise.

    Everything else fails, in both directions: "" for a list that does have a
    valid order, a correct-looking string that drops a letter, repeats one,
    invents one the words never use, or gets a single implied pair backwards, and
    any order at all for an unrecoverable list. `module` is deliberately unused
    (the answer is a value, not a codec), so the same checker works in the judge
    harness, in the reference gate (which hands it a namespace) and in the corpus
    tests."""
    words = args[0] if args else []
    if not isinstance(got, str):
        return False
    letters: set[str] = set()
    precedes: set[tuple[str, str]] = set()
    for word in words:
        letters.update(word)
    for first, second in zip(words, words[1:]):
        for a, b in zip(first, second):
            if a != b:
                precedes.add((a, b))
                break
        else:
            if len(first) > len(second):
                return got == ""  # a longer word before its own prefix
    if len(got) == len(letters) and set(got) == letters:
        position = {ch: index for index, ch in enumerate(got)}
        return all(position[a] < position[b] for a, b in precedes)
    if got != "":
        return False  # a string that is not the unique letters, once each
    pending = set(letters)
    while pending:
        free = {
            ch
            for ch in pending
            if not any((before, ch) in precedes for before in pending)
        }
        if not free:
            return True  # a cycle: no order exists, so "" is the answer
        pending -= free
    return False  # the peel emptied, so an order existed and "" is wrong


@measure("alien-dictionary")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    none."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'none'}
