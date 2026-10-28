"""Visible checks for `daily_temperatures` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'args': [[30, 38, 30, 36, 35, 40, 28]], 'expected': [1, 4, 1, 2, 1, 0, 0]},
    {'args': [[22, 21, 20]], 'expected': [0, 0, 0]},
    {'args': [[40, 30, 20, 35]], 'expected': [0, 2, 1, 0]},
]


def check() -> None:
    from solution import daily_temperatures

    checked = 0
    for number, case in enumerate(CASES, 1):
        got = daily_temperatures(*case["args"])
        ok = got == case["expected"]
        assert ok, f"case {number}: got {got!r}, want {case['expected']!r}"
        checked += 1
    print(f"{checked} of {len(CASES)} visible checks passed")


if __name__ == "__main__":
    check()
