"""Visible checks for `k_smallest_elem_matrix` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'args': [4, [[1, 4, 7], [3, 5, 9], [6, 8, 11]]], 'expected': 5},
    {'args': [8, [[1, 4, 7], [3, 5, 9], [6, 8, 11]]], 'expected': 9},
    {'args': [1, [[1]]], 'expected': 1},
]


def check() -> None:
    from solution import k_smallest

    checked = 0
    for number, case in enumerate(CASES, 1):
        got = k_smallest(*case["args"])
        ok = got == case["expected"]
        assert ok, f"case {number}: got {got!r}, want {case['expected']!r}"
        checked += 1
    print(f"{checked} of {len(CASES)} visible checks passed")


if __name__ == "__main__":
    check()
