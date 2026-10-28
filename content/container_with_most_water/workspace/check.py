"""Visible checks for `container_with_most_water` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'args': [[1, 7, 2, 5, 4, 7, 3, 6]], 'expected': 36},
    {'args': [[2, 2, 2]], 'expected': 4},
    {'args': [[1, 1]], 'expected': 1},
]


def check() -> None:
    from solution import max_area

    checked = 0
    for number, case in enumerate(CASES, 1):
        got = max_area(*case["args"])
        ok = got == case["expected"]
        assert ok, f"case {number}: got {got!r}, want {case['expected']!r}"
        checked += 1
    print(f"{checked} of {len(CASES)} visible checks passed")


if __name__ == "__main__":
    check()
