"""Visible checks for `evaluate_reverse_polish_notation` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'args': [['1', '2', '+', '3', '*', '4', '-']], 'expected': 5},
    {'args': [['2', '1', '+', '3', '*']], 'expected': 9},
    {'args': [['4', '13', '5', '/', '+']], 'expected': 6},
    {'args': [['10', '6', '9', '3', '+', '-11', '*', '/', '*', '17', '+', '5', '+']],
     'expected': 22},
    {'args': [['18']], 'expected': 18},
]


def check() -> None:
    from solution import eval_rpn

    checked = 0
    for number, case in enumerate(CASES, 1):
        got = eval_rpn(*case["args"])
        ok = got == case["expected"]
        assert ok, f"case {number}: got {got!r}, want {case['expected']!r}"
        checked += 1
    print(f"{checked} of {len(CASES)} visible checks passed")


if __name__ == "__main__":
    check()
