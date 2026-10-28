"""QUARANTINED assessment for `letter-combinations-of-a-phone-number` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, oracle, reference


@oracle("letter-combinations-of-a-phone-number")
def _letter_combinations_of_a_phone_number_oracle(digits: str) -> list[str]:
    # Brute force, and the Cartesian product written out: start from one empty
    # prefix and, for every digit in turn, append each letter that key carries.
    # No recursion and no pruning -- obviously correct -- and a different
    # mechanism from the reference's backtracking DFS. The two agree letter for
    # letter AND in order, because both walk the digits left to right and each
    # key's letters in keypad order, which is why the statement's own Example 1
    # output can be transcribed verbatim. Total for empty digits (the statement's
    # 1 <= digits.length excludes them) and for a digit outside 2-9, which
    # contributes no letters on either side -- see the notes.
    keypad = {
        "2": "abc", "3": "def", "4": "ghi", "5": "jkl",
        "6": "mno", "7": "pqrs", "8": "tuv", "9": "wxyz",
    }
    if not digits:
        return []
    out = [""]
    for digit in digits:
        out = [prefix + letter for prefix in out for letter in keypad.get(digit, "")]
    return out


@cases("letter-combinations-of-a-phone-number")
def _letter_combinations_of_a_phone_number_case(
    n: int, rng: random.Random
) -> tuple[list, list, dict]:
    # The statement's range, honoured exactly on both ends: 1 <= digits.length <= 4
    # and every digit in '2'..'9'. The caller sends 0..12, so the clamp has a real
    # floor AND a real ceiling here -- the generator cannot emit the empty string
    # the statement excludes, nor a 5-digit input it forbids, nor '0'/'1' which are
    # outside the stated range (a solution that expects them has no case to fail on
    # here, because the statement gives it none).
    length = max(1, min(n, 4))
    dial = "79" if n % 3 == 0 else "23456789"
    digits = "".join(rng.choice(dial) for _ in range(length))
    return (
        [digits],
        _letter_combinations_of_a_phone_number_oracle(digits),
        {"compare": "sorted"},  # the answer is a set of strings: only order is free
    )


@reference("letter-combinations-of-a-phone-number")
def _letter_combinations_of_a_phone_number_reference(digits: str) -> list[str]:
    """Canonical backtracking: one DFS that extends a prefix with every letter of
    the current key and emits the prefix when it is as long as the input. O(4^n * n)
    time and O(n) space, where n is the number of digits -- at most four letters per
    digit gives at most 4^n prefixes and each one costs n character appends to
    build, and the recursion is n deep (the returned list is not counted, as
    everywhere else in the corpus). The output order is the keypad order of each
    digit, so it matches the statement's Example 1 exactly; the case's own
    "compare": "sorted" tag is what makes any other order legal for a student."""
    keypad = {
        "2": "abc", "3": "def", "4": "ghi", "5": "jkl",
        "6": "mno", "7": "pqrs", "8": "tuv", "9": "wxyz",
    }
    if not digits:
        return []
    out: list[str] = []
    prefix: list[str] = []

    def _letter_combinations_of_a_phone_number_walk(i: int) -> None:
        if i == len(digits):
            out.append("".join(prefix))
            return
        for letter in keypad.get(digits[i], ""):
            prefix.append(letter)
            _letter_combinations_of_a_phone_number_walk(i + 1)
            prefix.pop()

    _letter_combinations_of_a_phone_number_walk(0)
    return out
