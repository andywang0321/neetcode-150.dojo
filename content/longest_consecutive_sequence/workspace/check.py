"""Visible checks for `longest_consecutive_sequence` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'args': [[2, 20, 4, 10, 3, 4, 5]], 'expected': 4},
    {'args': [[0, 3, 2, 5, 4, 6, 1, 1]], 'expected': 7},
    {'args': [[]], 'expected': 0},
    {'args': [[100, 4, 200, 1, 3, 2]], 'expected': 4},
]


def check() -> None:
    from solution import longest_seqlen

    checked = 0
    for number, case in enumerate(CASES, 1):
        got = longest_seqlen(*case["args"])
        ok = got == case["expected"]
        assert ok, f"case {number}: got {got!r}, want {case['expected']!r}"
        checked += 1
    print(f"{checked} of {len(CASES)} visible checks passed")


if __name__ == "__main__":
    check()
