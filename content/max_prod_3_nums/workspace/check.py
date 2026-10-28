"""Visible checks for `max_prod_3_nums` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'args': [[1, 3, 4, 5]], 'expected': 60},
    {'args': [[-2, -4, 5, 3]], 'expected': 40},
    {'args': [[-3, -2, -1]], 'expected': -6},
    {'args': [[0, 0, 0]], 'expected': 0},
]


def check() -> None:
    from solution import max_tri_prod

    checked = 0
    for number, case in enumerate(CASES, 1):
        got = max_tri_prod(*case["args"])
        ok = got == case["expected"]
        assert ok, f"case {number}: got {got!r}, want {case['expected']!r}"
        checked += 1
    print(f"{checked} of {len(CASES)} visible checks passed")


if __name__ == "__main__":
    check()
