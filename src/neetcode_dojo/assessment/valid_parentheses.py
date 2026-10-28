"""QUARANTINED assessment for `valid_parentheses` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, inputs, measure, oracle, reference


@oracle("valid_parentheses")
def _valid_parentheses_oracle(s: str) -> bool:
    pairs = {")": "(", "]": "[", "}": "{"}
    stack: list[str] = []
    for ch in s:
        if ch in "([{":
            stack.append(ch)
        elif not stack or stack.pop() != pairs[ch]:
            return False
    return not stack


@cases("valid_parentheses")
def _valid_parentheses_case(n: int, rng: random.Random) -> tuple[list, bool]:
    """Random bracket strings of length n; half the time start from a valid
    string and mutate it, to guarantee coverage of near-valid inputs."""
    alphabet = "()[]{}"
    if n <= 0:
        return [""], _valid_parentheses_oracle("")
    if rng.random() < 0.5:
        # Build a valid string from k matched pairs, then mutate one char.
        k = max(1, n // 2)
        openers, closers = "([{", ")]}"
        parts = []
        for _ in range(k):
            i = rng.randrange(3)
            parts.append(openers[i] + closers[i])
        s = list("".join(parts))
        if rng.random() < 0.7 and s:
            pos = rng.randrange(len(s))
            s[pos] = rng.choice(alphabet)
        s = "".join(s[:n])
    else:
        s = "".join(rng.choice(alphabet) for _ in range(n))
    return [s], _valid_parentheses_oracle(s)


@inputs("valid_parentheses")
def _valid_parentheses_profiler(n: int, rng: random.Random) -> list:
    """n nested opens then n closes: valid, scans the whole string, stack
    grows to depth n. Guarantees the O(n) path, never an early exit."""
    return ["(" * n + ")" * n]


@reference("valid_parentheses")
def _valid_parentheses_reference(s: str) -> bool:
    pairs = {")": "(", "]": "[", "}": "{"}
    stack: list[str] = []
    for ch in s:
        if ch in "([{":
            stack.append(ch)
        elif not stack or stack.pop() != pairs[ch]:
            return False
    return not stack


@measure("valid_parentheses")
def _measure(ctx):
    """Transcribed from the pre-split probe policy: the ladder climbs to
    6,400, paired against the canonical reference, comparing outputs
    strict."""
    return {'axis': 'n', 'sizes': [100, 200, 400, 800, 1600, 3200, 6400], 'baseline': 'reference', 'compare': 'strict'}
