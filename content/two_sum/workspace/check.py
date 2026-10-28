"""Visible checks for `two_sum` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'args': [[3, 4, 5, 6], 7], 'expected': [0, 1]},
    {'args': [[4, 5, 6], 10], 'expected': [0, 2]},
    {'args': [[5, 5], 10], 'expected': [0, 1]},
    {'args': [[1, 2, 5, 5], 10], 'expected': [2, 3]},
]


def check() -> None:
    from solution import twosum

    checked = 0
    for number, case in enumerate(CASES, 1):
        got = twosum(*case["args"])
        ok = got == case["expected"]
        assert ok, f"case {number}: got {got!r}, want {case['expected']!r}"
        checked += 1
    print(f"{checked} of {len(CASES)} visible checks passed")


if __name__ == "__main__":
    check()
