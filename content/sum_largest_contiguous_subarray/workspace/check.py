"""Visible checks for `sum_largest_contiguous_subarray` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'args': [[-1, -3, 5, -4, 3, -6, 9, 2]], 'expected': 11},
    {'args': [[-1, -5, -3, -7]], 'expected': 0},
    {'args': [[-2, 1, -3, 4, -1, 2, 1, -5, 4]], 'expected': 6},
    {'args': [[5]], 'expected': 5},
]


def check() -> None:
    from solution import sum_largest_subarray

    checked = 0
    for number, case in enumerate(CASES, 1):
        got = sum_largest_subarray(*case["args"])
        ok = got == case["expected"]
        assert ok, f"case {number}: got {got!r}, want {case['expected']!r}"
        checked += 1
    print(f"{checked} of {len(CASES)} visible checks passed")


if __name__ == "__main__":
    check()
