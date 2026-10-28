"""QUARANTINED assessment for `valid-parenthesis-string` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


def _valid_parenthesis_string_balanced(pairs: int, rng: random.Random) -> str:
    """A random correctly matched bracket string with `pairs` pairs."""
    if pairs == 0:
        return ""
    left = rng.randint(0, pairs - 1)
    return (
        "("
        + _valid_parenthesis_string_balanced(left, rng)
        + ")"
        + _valid_parenthesis_string_balanced(pairs - 1 - left, rng)
    )


def _valid_parenthesis_string_valid(size: int, rng: random.Random) -> str:
    """A valid string of exactly `size` characters.

    A real bracket string is built first, then some of its brackets are rewritten
    to '*' - so those stars MUST read as that bracket - and the remaining length is
    filled with '*' that read as the empty string. Nothing here can produce an
    invalid string: every '*' has the reading of the bracket it replaced, or reads
    as empty."""
    chars = [
        "*" if char == "(" and rng.random() < 0.35
        else "*" if char == ")" and rng.random() < 0.35
        else char
        for char in _valid_parenthesis_string_balanced(size // 2, rng)
    ]
    while len(chars) < size:
        chars.insert(rng.randint(0, len(chars)), "*")
    return "".join(chars)


def _valid_parenthesis_string_pad(shape: str, size: int, rng: random.Random) -> str:
    """Grow `shape` to `size` characters with stars, inserted at random positions.

    Inserting a star that can read as the empty string cannot make a VALID string
    invalid: the original reading is still available (and every reading of the
    padded string restricts to a reading of the original). It can however rescue an
    INVALID string - the inserted star brings two new readings with it - which is
    why the invalid templates below are emitted unpadded."""
    chars = list(shape)
    while len(chars) < size:
        chars.insert(rng.randint(0, len(chars)), "*")
    return "".join(chars)


@oracle("valid-parenthesis-string")
def _valid_parenthesis_string_oracle(s: str) -> bool:
    """Brute force over the readings, memoized on (position, open count).

    The definition is itself a search: each '*' may be '(', ')' or the empty
    string, and the string is valid exactly when some choice of readings is a
    correctly matched bracket string, i.e. when the running number of unmatched
    '(' never goes negative and is zero at the end. This walks the string trying
    all three readings at every star; the only thing it prunes is a prefix that has
    already closed more brackets than it opened, which no later reading can repair.
    `failed` remembers the (position, open) states already proven dead, which is
    what turns 3^(number of stars) into O(n^2) states. Total on the empty string
    (which the statement's length bound excludes)."""
    failed: set[tuple[int, int]] = set()

    def read(index: int, opens: int) -> bool:
        if opens < 0:
            return False
        if index == len(s):
            return opens == 0
        if (index, opens) in failed:
            return False
        char = s[index]
        if char == "(":
            options = (opens + 1,)
        elif char == ")":
            options = (opens - 1,)
        else:  # '*': read it as '(', as ')' or as the empty string
            options = (opens + 1, opens, opens - 1)
        for nxt in options:
            if read(index + 1, nxt):
                return True
        failed.add((index, opens))
        return False

    return read(0, 0)


@cases("valid-parenthesis-string")
def _valid_parenthesis_string_case(n: int, rng: random.Random) -> tuple[list, bool]:
    size = max(1, min(n, 12))  # statement: 1 <= s.length <= 100
    roll = rng.random()
    # The star-critical shapes: cases where a 'count the stars and compare'
    # answer and the two-counter range disagree. In "(*))" the star must be a '('
    # to close the pair, in "((*)" it must be a ')', in "(*)" and "*" it must be
    # the empty string, and "**(" is false however the stars read - the three
    # readings the low/high range keeps apart. The self-check proves those roles by
    # enumerating every reading of every star, outside the fragment.
    opens_shape = [
        "*",          # true  - the star reads as empty
        "(*",         # true  - the star reads as ')'
        "*)",         # true  - the star reads as '('
        "**",         # true
        "(*)",        # true  - empty
        "(*))",       # true  - '(' (statement example 3)
        "((*)",       # true  - ')'
        "((**",       # true  - two stars as ')'
        "(**)",       # true
        "*()",        # true  - empty
        "(()*",       # true
    ]
    closed_shapes = [
        "*(",         # false - nothing after the '(' can close it
        "**(",        # false
        "*))",        # false - two stars cannot close three brackets
        "*)(",        # false
        "(((*",       # false - one star cannot close three opens
        "(((((****",  # false - four stars cannot close five opens
    ]
    if roll < 0.2:
        # A valid shape, padded to length with extra stars: the padding is where
        # the third role (a star reading as the empty string) comes from, and it
        # cannot change the verdict - the shape's own reading survives.
        shape = rng.choice([candidate for candidate in opens_shape if len(candidate) <= size])
        s = _valid_parenthesis_string_pad(shape, size, rng)
    elif roll < 0.35:
        # A false shape, emitted at its own length: padding it with stars would add
        # readings and could rescue it ("**))" is true while "*))" is false), and
        # this case is here to be false.
        usable = [candidate for candidate in closed_shapes if len(candidate) <= size]
        if usable:
            s = rng.choice(usable)
        else:  # size == 1: no star-critical false shape fits, so take a valid one
            s = rng.choice([candidate for candidate in opens_shape if len(candidate) <= size])
    elif roll < 0.7:
        # Valid by construction: a bracket string with some brackets rewritten to
        # '*' (that star must read as the bracket it replaced) and the rest filled
        # with '*' reading as empty. Exercises all three readings at once.
        s = _valid_parenthesis_string_valid(size, rng)
    elif roll < 0.85:
        # One character of a valid string changed: usually invalid, and the change
        # is usually adjacent to a star, which is where a range bug shows up.
        chars = list(_valid_parenthesis_string_valid(size, rng))
        index = rng.randrange(len(chars))
        chars[index] = rng.choice([c for c in "()*" if c != chars[index]])
        s = "".join(chars)
    else:
        # An unstructured draw.
        s = "".join(rng.choice("()*") for _ in range(size))
    return [s], _valid_parenthesis_string_oracle(s)


@inputs("valid-parenthesis-string")
def _valid_parenthesis_string_profiler(n: int, rng: random.Random) -> list:
    # A valid string of length size: half '(' and half '*' that close them. Nothing
    # can early-exit - the answer is true, no prefix pushes the minimum open count
    # below zero, and every character moves both counters, which is the whole cost
    # of the intended pass (a stack solution pays size pushes and pops on it).
    #
    # probe_max_n = 100 is a fidelity cap, not a preference: the statement bounds
    # s at 100 characters, so the default ladder's 6400 would measure inputs the
    # problem never promises (the merge-two-sorted-lists precedent). The cost is
    # resolution - over a 1..100 ladder an O(n) solution can realistically only
    # come back "agrees with the reference" or "unresolved", and unresolved is the
    # honest reading rather than a curation bug. What it still buys is the digest
    # check at 100 characters, ten times any generated case.
    size = max(1, min(n, 100))
    opens = size // 2
    return ["(" * opens + "*" * (size - opens)]


@reference("valid-parenthesis-string")
def _valid_parenthesis_string_reference(s: str) -> bool:
    """The intended one pass, two counters.

    `low` is the fewest '(' that can still be open if every '*' seen so far is read
    as ')' (never below zero: a star that closed a bracket could have been read as
    empty instead), and `high` is the most that can be open if every star is read
    as '('. The readings of a prefix leave it at every open count in [low, high]
    and at no other, so a prefix whose `high` is negative is a ')' that no reading
    can match, and the string is valid exactly when the whole string can end with
    nothing open - which the clamped `low` reports. O(n) time, O(1) space."""
    low = 0
    high = 0
    for char in s:
        if char == "(":
            low += 1
            high += 1
        elif char == ")":
            low -= 1
            high -= 1
        else:  # '*': ')' lowers the floor, '(' raises the ceiling
            low -= 1
            high += 1
        if high < 0:
            return False
        if low < 0:
            low = 0
    return low == 0


@measure("valid-parenthesis-string")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
