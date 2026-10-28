"""QUARANTINED assessment for `regular-expression-matching` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("regular-expression-matching")
def _regular_expression_matching_oracle(s: str, p: str) -> bool:
    """The statement's two bullets, read straight into a recursion -- no table, no
    interval bookkeeping, no reference to any DP.

    covers(i, j) asks "can p[j:] match s[i:] exactly?", and the two bullets decide
    it: '.' matches any single character, and '*' means ZERO OR MORE OF THE
    PRECEDING ELEMENT -- so when the element after p[j] is a star, the pattern
    either drops the element and its star entirely (zero occurrences) or consumes
    one character that the element matches and asks the same question again with
    the element still in place (one more occurrence). Otherwise p[j] must match
    s[i] itself and both advance by one. The pattern running out with the string
    not yet consumed is a failure, which is the "covers the entire input string
    (not partial)" half of the statement.

    The memo is the one concession, and it is the same one climbing-stairs'
    oracle makes, for the same reason: flow._oracle_confirms runs the oracle IN
    PROCESS, with no timeout, at whatever size a student and the reference
    disagreed at, and the unmemoized recursion is exponential in the number of
    '*' groups -- at the top of this problem's ladder the unmemoized recursion
    already makes 260,337 calls and the count grows by roughly an order of
    magnitude every two star groups, which is a live session hanging instead of a
    finding. Memoizing does NOT weaken the
    differential against the reference: the two are different programs in every
    structural sense -- top-down with an explicit base case and a dictionary keyed
    by (i, j) versus bottom-up loops filling a rectangle, with the star-free and
    dot branches written separately rather than folded into one expression -- and
    the memo only refuses to re-ask a question it has already answered, so it
    cannot change what the recursion returns.

    Total on everything the generator can produce, the empty string included
    (covers(0, 0) with both empty is True: a pattern with no elements matches
    nothing but the empty string), and total on the shapes the statement's
    guarantee rules out -- a leading '*' never matches anything, because nothing
    precedes it to repeat, and the reference agrees there for the same reason.
    """
    memo: dict[tuple[int, int], bool] = {}

    def covers(i: int, j: int) -> bool:
        if j == len(p):
            return i == len(s)
        key = (i, j)
        if key in memo:
            return memo[key]
        first = i < len(s) and (p[j] == "." or p[j] == s[i])
        if j + 1 < len(p) and p[j + 1] == "*":
            answer = covers(i, j + 2) or (first and covers(i + 1, j))
        else:
            answer = first and covers(i + 1, j + 1)
        memo[key] = answer
        return answer

    return covers(0, 0)


@cases("regular-expression-matching")
def _regular_expression_matching_case(n: int, rng: random.Random) -> tuple[list, bool]:
    # Five shapes, one per 20% of the draws (rng.randrange(5) -- deliberately NOT
    # n % 5: the judge's own sweeps call the generator with n in (0, 3, 7, 12),
    # whose residues are 0, 3, 2, 2, so a residue-picked shape would leave two of
    # the five shapes never generated at all).
    #
    #   0. ".*" -- A STAR ON A DOT, 20%. Every group is a literal (sometimes empty)
    #      followed by ".*", so the pattern always contains a star whose preceding
    #      element is a dot, and a longer pattern contains several. This is the
    #      shape that separates "the star repeats the dot" from "the star repeats
    #      what comes after it", and the statement's example 3 lives here.
    #   1. several stars over literal letters, 20%. Two or three "x*" groups and a
    #      string drawn from those same letters, so groups whose letter never
    #      occurs are exercised through the zero-repetition branch. About a third of
    #      these append a letter no group can consume, which makes the answer False
    #      and pins that a star binds its own element rather than a neighbour.
    #   2. the empty string, 20%. s = "" against a pattern built only from "x*"
    #      groups: the zero half of "zero or more" is only observable when there is
    #      nothing left to match. Two thirds of these patterns can vanish entirely
    #      (True); the other third appends one element that cannot -- a literal or a
    #      lone '.', which still wants a character of its own -- so the shape has a
    #      False side as well. NOTE: s = "" is outside the statement's
    #      1 <= s.length line; it is emitted on purpose (the user's assignment asks
    #      for patterns that match empty strings, and the zero-occurrence reading of
    #      '*' is exactly what it pins), the oracle and the reference agree on it by
    #      construction, and a visible test puts the agreed value on record.
    #   3. near-misses, 20%, in three sub-variants, each False or True BY
    #      CONSTRUCTION rather than by luck:
    #        (a) 40% of the shape: a star-free pattern exactly as long as the core
    #            (some characters replaced by '.'), with one character too many
    #            appended to the string -- a '.' matches exactly one character, so
    #            the length mismatch alone settles it (False);
    #        (b) 35% of the shape: the star sits on the WRONG element --
    #            first + rest + "*" against first + first + rest, with rest a
    #            different letter from first, so the doubled first letter can never
    #            be consumed (False);
    #        (c) 25% of the shape: the mirror image, where the star rescues it --
    #            first + "*" + rest against first * k + rest with k drawn from 0..3,
    #            so a quarter of these (5% of all cases) are the zero-repetition
    #            case against a NON-empty string (p = "a*b" against s = "b") (True).
    #   4. no stars at all, 20% -- the control. Literals with some of them replaced
    #      by '.', and the string either the core the pattern was built from or an
    #      unrelated draw. With no star to hide behind, this is where "'.' matches
    #      exactly one character" and the exact-length requirement are pinned, and
    #      the second half of the branch supplies the shape's False answers.
    #
    # Every pattern is legal by construction -- the alphabet is only lowercase
    # letters, '.' and '*', and every '*' is emitted directly after the letter or
    # dot it repeats, which is the statement's own guarantee -- and every string is
    # at most 13 characters against the statement's 20, since size <= 12. Expected
    # always comes from the oracle, never from the reference.
    size = max(1, min(n, 12))
    shape = rng.randrange(5)
    if shape == 0:
        groups = rng.randint(1, max(1, size // 2))
        pattern = "".join(rng.choice(["", "a", "b", "c"]) + ".*" for _ in range(groups))
        text = "".join(rng.choice("abc") for _ in range(rng.randint(0, size)))
    elif shape == 1:
        letters = [rng.choice("ab") for _ in range(rng.randint(2, 3))]
        pattern = "".join(letter + "*" for letter in letters)
        text = "".join(rng.choice(letters) for _ in range(rng.randint(0, size)))
        if rng.random() < 0.35:
            text += "c"  # no group can consume this, so the whole match fails
    elif shape == 2:
        text = ""
        pattern = "".join(rng.choice("ab") + "*" for _ in range(rng.randint(1, 3)))
        if rng.random() < 0.34:
            pattern += rng.choice(["a", "b", "."])  # now it needs a character
    elif shape == 3:
        core = "".join(rng.choice("abc") for _ in range(rng.randint(1, max(1, size // 2))))
        roll = rng.random()
        first = rng.choice("abc")
        rest = rng.choice([letter for letter in "abc" if letter != first])
        if roll < 0.40:
            pattern = "".join(letter if rng.random() < 0.5 else "." for letter in core)
            text = core + rng.choice("abc")
        elif roll < 0.75:
            pattern = first + rest + "*"  # the star is on the following element
            text = first + first + rest
        else:
            pattern = first + "*" + rest
            text = first * rng.randint(0, 3) + rest
    else:
        length = rng.randint(1, max(1, min(size, 8)))
        if rng.random() < 0.5:
            core = "".join(rng.choice("ab") for _ in range(length))
            pattern = "".join(letter if rng.random() < 0.5 else "." for letter in core)
            text = core
        else:
            pattern = "".join(rng.choice("ab.") for _ in range(length))
            text = "".join(rng.choice("ab") for _ in range(rng.randint(1, 6)))
    return [text, pattern], _regular_expression_matching_oracle(text, pattern)


@inputs("regular-expression-matching")
def _regular_expression_matching_profiler(n: int, rng: random.Random) -> list:
    # s is a run of one letter; p is that letter's star group repeated, ending in a
    # LITERAL the string cannot supply. The requested size splits between the two
    # strings, so the top of the ladder (n = 40, which is probe_max_n) is 20
    # characters against a 19-character pattern -- the statement's cap on both --
    # and the rungs below 2 collapse onto the statement's one-character minima, so
    # no rung asks for a shape the statement excludes (the climbing-stairs floor
    # convention).
    #
    # The trailing 'b' is the whole design, and it is there because the obvious
    # alternative was MEASURED and rejected: with p = "a*" * 10 against the same
    # 20-character string the answer is True, and a memoized top-down matcher
    # reaches it through the zero-repetition chain in 30 of the table's 441 cells --
    # a general implementation measured as though constant. With the failing tail
    # the answer is False, so there is no witness to stop on and the matcher has to
    # exhaust every reachable state: 210 of the 420 cells at the top rung, measured
    # with an instrumented copy of the oracle. That is the Theta(m * n) the problem
    # is about, and it is what "nothing early-exits" means here:
    #   * the reference's bottom-up table computes all (m + 1) * (n + 1) cells
    #     unconditionally, whatever the strings are;
    #   * a top-down memoized matcher cannot skip either, because the failing tail
    #     forces every decomposition of the nine star groups to be tried;
    #   * a matcher that backtracks WITHOUT a memo does not get a shortcut either:
    #     the same input costs it 260,337 recursive calls (4 star groups: 335,
    #     6: 4,718, 8: 68,067 -- roughly an order of magnitude per two groups), so
    #     the ladder's ratios show the blow-up rather than a flat line;
    #   * and the answer being False rather than True also keeps the output
    #     comparison honest: an implementation that always answers True fails at
    #     every rung instead of passing the profiler input by accident.
    # The input ignores `rng` on purpose: flow._oracle_confirms regenerates the
    # profiler input for a disputed size with its own rng, so a random draw would
    # have the oracle confirm a different input than the one the student disagreed
    # on. The oracle itself stays cheap here (the same 210 states), which is what
    # keeps that in-process confirmation answerable.
    size = max(2, min(n, 40))  # 2 * the statement's 20-character cap, hence probe_max_n = 40
    length = max(1, size // 2)
    groups = max(1, min(9, (size - length - 1) // 2))
    return ["a" * length, "a*" * groups + "b"]


@reference("regular-expression-matching")
def _regular_expression_matching_reference(s: str, p: str) -> bool:
    """Canonical bottom-up table, O(m * n) time and O(m * n) space.

    table[i][j] is "can p[j:] match s[i:]?", filled from the bottom right, with
    table[m][n] the empty-against-empty base case. Reading the statement's bullets
    in that direction gives exactly three moves: a star after p[j] means either the
    element and its star vanish (table[i][j + 2]) or one character is consumed and
    the element is asked again with its star intact (first and table[i + 1][j]);
    otherwise p[j] must match s[i] itself ('.' matching anything) and both advance
    (first and table[i + 1][j + 1]). Every cell is computed unconditionally, which
    is what fixes the cost at Theta(m * n) rather than at the size of the search a
    smarter traversal would need.

    Total on every input, the empty string included: with p empty and s empty the
    base case answers True, and with p empty and s non-empty the base case answers
    False -- matching "covers the entire input string" rather than a prefix.
    """
    m, n = len(s), len(p)
    table = [[False] * (n + 1) for _ in range(m + 1)]
    table[m][n] = True
    for i in range(m, -1, -1):
        row = table[i]
        below = table[i + 1] if i < m else None
        for j in range(n - 1, -1, -1):
            first = i < m and (p[j] == "." or p[j] == s[i])
            if j + 1 < n and p[j + 1] == "*":
                row[j] = row[j + 2] or (first and below[j])
            else:
                row[j] = first and below[j + 1]
    return table[0][0]


@measure("regular-expression-matching")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
