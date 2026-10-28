"""Visible checks for `valid_anagram` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'args': ['racecar', 'carrace'], 'expected': True},
    {'args': ['jar', 'jam'], 'expected': False},
    {'args': ['jarr', 'jar'], 'expected': False},
    {'args': ['anagram', 'nagaram'], 'expected': True},
]


def check() -> None:
    from solution import valid_anagram

    checked = 0
    for number, case in enumerate(CASES, 1):
        got = valid_anagram(*case["args"])
        ok = got == case["expected"]
        assert ok, f"case {number}: got {got!r}, want {case['expected']!r}"
        checked += 1
    print(f"{checked} of {len(CASES)} visible checks passed")


if __name__ == "__main__":
    check()
