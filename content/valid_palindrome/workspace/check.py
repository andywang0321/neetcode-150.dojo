"""Visible checks for `valid_palindrome` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'args': ['Was it a car or a cat I saw?'], 'expected': True},
    {'args': ['tab a cat'], 'expected': False},
    {'args': ['A man, a plan, a canal: Panama'], 'expected': True},
    {'args': ['race a car'], 'expected': False},
    {'args': [' '], 'expected': True},
]


def check() -> None:
    from solution import is_palindrome

    checked = 0
    for number, case in enumerate(CASES, 1):
        got = is_palindrome(*case["args"])
        ok = got == case["expected"]
        assert ok, f"case {number}: got {got!r}, want {case['expected']!r}"
        checked += 1
    print(f"{checked} of {len(CASES)} visible checks passed")


if __name__ == "__main__":
    check()
