"""Visible checks for `trapping_rain_water` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'args': [[0, 2, 0, 3, 1, 0, 1, 3, 2, 1]], 'expected': 9},
    {'args': [[4, 2, 0, 3, 2, 5]], 'expected': 9},
    {'args': [[0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]], 'expected': 6},
]


def check() -> None:
    from solution import trap

    checked = 0
    for number, case in enumerate(CASES, 1):
        got = trap(*case["args"])
        ok = got == case["expected"]
        assert ok, f"case {number}: got {got!r}, want {case['expected']!r}"
        checked += 1
    print(f"{checked} of {len(CASES)} visible checks passed")


if __name__ == "__main__":
    check()
