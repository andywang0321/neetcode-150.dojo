"""Visible checks for `car_fleet` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'args': [10, [1, 4], [3, 2]], 'expected': 1},
    {'args': [10, [4, 1, 0, 7], [2, 2, 1, 1]], 'expected': 3},
    {'args': [12, [10, 8, 0, 5, 3], [2, 4, 1, 1, 3]], 'expected': 3},
]


def check() -> None:
    from solution import car_fleet

    checked = 0
    for number, case in enumerate(CASES, 1):
        got = car_fleet(*case["args"])
        ok = got == case["expected"]
        assert ok, f"case {number}: got {got!r}, want {case['expected']!r}"
        checked += 1
    print(f"{checked} of {len(CASES)} visible checks passed")


if __name__ == "__main__":
    check()
