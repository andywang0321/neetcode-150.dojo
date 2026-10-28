"""QUARANTINED assessment for `interleaving-string` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


def _interleaving_string_merge(s1: str, s2: str, rng: random.Random) -> str:
    """A real interleaving of s1 and s2, built one character at a time.

    A coin decides which string supplies the next character whenever both can,
    which is what produces the ambiguous positions the DP exists for: a
    two-letter alphabet makes "both next characters match s3" common, and a
    two-pointer greedy has to guess there.
    """
    i = j = 0
    out: list[str] = []
    while i < len(s1) or j < len(s2):
        if i < len(s1) and j < len(s2) and rng.random() < 0.5:
            out.append(s1[i])
            i += 1
        elif i < len(s1) and j == len(s2):
            out.append(s1[i])
            i += 1
        else:
            out.append(s2[j])
            j += 1
    return "".join(out)


@oracle("interleaving-string")
def _interleaving_string_oracle(s1: str, s2: str, s3: str) -> bool:
    """Brute force by the definition: can s3 be consumed from s1 and s2 in order?

    reachable(i, j) asks whether s3[:i + j] is an interleaving of s1[:i] and
    s2[:j], and the answer is yes when the next character of s3 can be taken from
    s1's next character (and the rest works out) or from s2's. That is the
    definition read as a search, with no table and no cleverness. It is memoized
    on (i, j), and the reason is a live-session hazard rather than tidiness:
    flow._oracle_confirms runs the oracle IN PROCESS, at whatever size a
    student's output was disputed at -- up to the profiler's top rung, where the
    unmemoized walk branches twice per character and would hang the session
    instead of confirming anything (the house-robber fragment documents the same
    reasoning for its own tree). Memoizing turns the C(m + n, m) tree into m * n
    states; the differential against the reference stays real, because this is a
    dict explored top-down by recursion while the reference overwrites a single
    row of flags in place bottom-up -- including the step the reference can get
    wrong, where a cell that has stopped being reachable must be written back to
    False. Total on every input: empty strings, a length that does not add up, a
    character that appears in neither string.
    """
    if len(s1) + len(s2) != len(s3):
        return False
    memo: dict[tuple[int, int], bool] = {}

    def walk(i: int, j: int) -> bool:
        if i == len(s1) and j == len(s2):
            return True
        seen = memo.get((i, j))
        if seen is not None:
            return seen
        k = i + j
        found = False
        if i < len(s1) and s1[i] == s3[k]:
            found = walk(i + 1, j)
        if not found and j < len(s2) and s2[j] == s3[k]:
            found = walk(i, j + 1)
        memo[(i, j)] = found
        return found

    return walk(0, 0)


@cases("interleaving-string")
def _interleaving_string_case(n: int, rng: random.Random) -> tuple[list, bool]:
    # The caller sends 0..12 and the statement's floor is 0 for ALL THREE
    # lengths, so 0 is a legal case and it is the statement's own example 3
    # (three empty strings, true). |s3| = |s1| + |s2| is kept at every size --
    # an interleaving has the combined length, so a triple that does not add up
    # could only ever be false. Four shapes, and two of them are false by
    # construction rather than by luck:
    #   * a real merge (true by construction, and the largest single share);
    #   * an exchange near-miss: both strings start with 'a' and end with 'b',
    #     so every interleaving of them starts with 'a' and ends with 'b' --
    #     exchanging the merge's first and last characters keeps the length and
    #     the multiset and makes the string start with a letter neither string
    #     starts with, i.e. false;
    #   * one character replaced by 'z', a letter neither string contains, so
    #     the multiset no longer matches (false);
    #   * an unstructured draw over the same alphabet, where the oracle decides.
    # The empty-string shape is not a special branch: first is drawn from
    # 0..length, so a zero-length s1 or s2 occurs on its own, and the "one of
    # them is empty" corner is additionally forced a sixth of the time.
    total = max(0, min(n, 12))
    length = total // 2
    if length == 0:
        return ["", "", ""], True
    if rng.random() < 0.15:
        first = 0 if rng.random() < 0.5 else length
    elif length > 1:
        first = rng.randint(1, length - 1)
    else:
        first = length
    second = length - first
    alphabet = "ab"
    s1 = "".join(rng.choice(alphabet) for _ in range(first))
    s2 = "".join(rng.choice(alphabet) for _ in range(second))
    s3 = _interleaving_string_merge(s1, s2, rng)
    roll = rng.random()
    if roll < 0.4:
        pass  # a real merge: true by construction
    elif roll < 0.7 and first >= 2 and second >= 2:
        s1 = "a" + "".join(rng.choice(alphabet) for _ in range(first - 2)) + "b"
        s2 = "a" + "".join(rng.choice(alphabet) for _ in range(second - 2)) + "b"
        merged = _interleaving_string_merge(s1, s2, rng)
        s3 = merged[-1] + merged[1:-1] + merged[0]
    elif roll < 0.85 and s3:
        position = rng.randrange(len(s3))
        s3 = s3[:position] + "z" + s3[position + 1:]
    else:
        s3 = "".join(rng.choice(alphabet) for _ in range(length))
    return [s1, s2, s3], _interleaving_string_oracle(s1, s2, s3)


@inputs("interleaving-string")
def _interleaving_string_profiler(n: int, rng: random.Random) -> list:
    # A FALSE case, by construction, and it is the point rather than an accident.
    #
    # The family: s1 = s2 = "ab" repeated (with a trailing 'b' when the half
    # length is odd), and s3 = a real merge of them with its LAST TWO characters
    # transposed. Both strings end with 'b', so every interleaving of them ends
    # with 'b' -- the last character of an interleaving is the last character of
    # whichever string supplied it -- while this s3 ends with 'a'. False at every
    # rung, with the lengths still adding up exactly (|s1| + |s2| = |s3|), and
    # the top rung is exactly the statement's corners: 100 + 100 = 200
    # characters (probe_max_n = 400 is the TOTAL |s1| + |s2| + |s3|, the largest
    # input the bounds permit: |s1|, |s2| <= 100 forces |s3| <= 200).
    #
    # WHY FALSE AND NOT TRUE. A memoized depth-first student on a TRUE case
    # stops at the first path it finds: measured on the obvious true candidate
    # ("ab" * 50 against itself, s3 = "ab" * 100) it visits 250 of the 10,201
    # states -- an early exit, which is what a profiler input must not allow. On
    # this near-miss it cannot: measured visits are 3/4, 12/16, 37/49, 130/169,
    # 507/676, 1973/2601 and 7,698/10,201 states at the ladder's rungs, a steady
    # ~76% of the grid, because the defect is in the LAST character and every
    # prefix of s3 is consistent with a real merge. The reference's reachability
    # DP scans all m * n cells on any input, so both sides do Theta(m * n) work
    # with nothing to skip and no value that could let either stop.
    #
    # WHY THE LAST TWO CHARACTERS AND NOT A SHORTER DEFECT. A substitution (a 'z'
    # the strings do not contain) is false too, and it is what the generator uses
    # at small sizes, but at scale it is detected by a character-presence check
    # in O(n) -- a student's early exit, measuring as sublinear. The transposed
    # tail is the mildest defect that is still false: same length, same multiset,
    # and no prefix of s3 is inconsistent, so nothing local can answer it.
    #
    # MEASURED COST. The DP's work is Theta(|s1| * |s2|); at the top rung that is
    # 100 x 100 = 10^4 cells. The rolling reference takes 2.45 ms untraced and
    # 2.11 ms with tracemalloc active (peak 936 B), a full-table student 1.94 ms
    # and 2.26 ms (peak 83,888 B): one row against the whole table is a ~90x
    # space difference that itself grows with the ladder (O(k) against O(k^2)),
    # and the time is Theta(m * n) on both sides. Small absolute numbers are the
    # honest reading here -- the statement's own caps are what they are -- so the
    # digest and the space axis carry most of what this input can say.
    #
    # ACCEPTED WEAKNESSES. The digest is the single value False at every rung: a
    # stub returning a constant False would agree at scale (small-size
    # correctness is the judge's job). And a two-pointer greedy answers False
    # here too -- correctly, since a greedy that consumes both strings would have
    # PROVED s3 an interleaving -- so a greedy measures as far faster than the
    # reference; the probe reports that as a direction, which is what the
    # measurement actually saw.
    half = max(1, min(n // 4, 100))
    piece = "ab" * (half // 2) + ("b" if half % 2 else "")
    return [piece, piece, "ab" * (half - 1) + "ba"]


@reference("interleaving-string")
def _interleaving_string_reference(s1: str, s2: str, s3: str) -> bool:
    """The reachability DP in its 1-D form over s2: one row of flags, O(n) space.

    reachable[j] is "s3[:i + j] can be split into s1[:i] and s2[:j]" for the row
    i being built, so the cell is reachable when the character s3 offers is s1's
    next one and the cell above was reachable, or when it is s2's next one and
    the cell to the left (already updated in this row) was. The final else is not
    decoration: every cell of every row must be written, or a cell that stopped
    being reachable would keep the previous row's True. O(m * n) time and O(n)
    space -- the form the statement's own follow-up asks for, "only O(s2.length)
    additional memory space". A length that does not add up is false before any
    work; a length mismatch is a legal input under the statement's constraint
    block even though the generator never emits one.
    """
    if len(s1) + len(s2) != len(s3):
        return False
    cells = len(s2)
    reachable = [False] * (cells + 1)
    reachable[0] = True
    for i in range(len(s1) + 1):
        for j in range(cells + 1):
            if i == 0 and j == 0:
                continue
            k = i + j - 1
            if i > 0 and s1[i - 1] == s3[k] and reachable[j]:
                reachable[j] = True
            elif j > 0 and s2[j - 1] == s3[k] and reachable[j - 1]:
                reachable[j] = True
            else:
                reachable[j] = False
    return reachable[cells]


@measure("interleaving-string")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
