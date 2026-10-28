"""Visible checks for `two_sum_2` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'args': [[1, 2, 3, 4], 3], 'expected': [1, 2]},
    {'args': [[2, 7, 11, 15], 9], 'expected': [1, 2]},
    {'args': [[2, 3, 4], 6], 'expected': [1, 3]},
]


def check() -> None:
    from solution import two_sum_2

    checked = 0
    for number, case in enumerate(CASES, 1):
        got = two_sum_2(*case["args"])
        ok = got == case["expected"]
        assert ok, f"case {number}: got {got!r}, want {case['expected']!r}"
        checked += 1
    print(f"{checked} of {len(CASES)} visible checks passed")


if __name__ == "__main__":
    check()
