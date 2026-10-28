"""Visible checks for `generate_parentheses` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'args': [1], 'expected': ['()'], 'compare': 'sorted'},
    {'args': [2], 'expected': ['(())', '()()'], 'compare': 'sorted'},
    {'args': [3],
     'expected': ['((()))', '(()())', '(())()', '()(())', '()()()'],
     'compare': 'sorted'},
]


def check() -> None:
    from solution import generate_parentheses

    checked = 0
    for number, case in enumerate(CASES, 1):
        got = generate_parentheses(*case["args"])
        if case.get("compare") == "sorted":
            ok = sorted(map(repr, got)) == sorted(map(repr, case["expected"]))
        else:
            ok = got == case["expected"]
        assert ok, f"case {number}: got {got!r}, want {case['expected']!r}"
        checked += 1
    print(f"{checked} of {len(CASES)} visible checks passed")


if __name__ == "__main__":
    check()
