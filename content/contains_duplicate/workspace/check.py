"""Visible checks for `contains_duplicate` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'args': [[1, 2, 3, 3]], 'expected': True},
    {'args': [[1, 2, 3, 4]], 'expected': False},
    {'args': [[]], 'expected': False},
    {'args': [[-1, 2, -1]], 'expected': True},
]


def check() -> None:
    from solution import contains_duplicate

    checked = 0
    for number, case in enumerate(CASES, 1):
        got = contains_duplicate(*case["args"])
        ok = got == case["expected"]
        assert ok, f"case {number}: got {got!r}, want {case['expected']!r}"
        checked += 1
    print(f"{checked} of {len(CASES)} visible checks passed")


if __name__ == "__main__":
    check()
