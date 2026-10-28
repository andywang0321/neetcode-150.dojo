"""Visible checks for `largest_rectangle_in_histogram` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'args': [[7, 1, 7, 2, 2, 4]], 'expected': 8},
    {'args': [[1, 3, 7]], 'expected': 7},
    {'args': [[2, 1, 5, 6, 2, 3]], 'expected': 10},
    {'args': [[2, 4]], 'expected': 4},
]


def check() -> None:
    from solution import largest_rectangle

    checked = 0
    for number, case in enumerate(CASES, 1):
        got = largest_rectangle(*case["args"])
        ok = got == case["expected"]
        assert ok, f"case {number}: got {got!r}, want {case['expected']!r}"
        checked += 1
    print(f"{checked} of {len(CASES)} visible checks passed")


if __name__ == "__main__":
    check()
