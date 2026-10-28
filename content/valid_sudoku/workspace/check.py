"""Visible checks for `valid_sudoku` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'args': [[['1', '2', '.', '.', '3', '.', '.', '.', '.'],
               ['4', '.', '.', '5', '.', '.', '.', '.', '.'],
               ['.', '9', '8', '.', '.', '.', '.', '.', '3'],
               ['5', '.', '.', '.', '6', '.', '.', '.', '4'],
               ['.', '.', '.', '8', '.', '3', '.', '.', '5'],
               ['7', '.', '.', '.', '2', '.', '.', '.', '6'],
               ['.', '.', '.', '.', '.', '.', '2', '.', '.'],
               ['.', '.', '.', '4', '1', '9', '.', '.', '8'],
               ['.', '.', '.', '.', '8', '.', '.', '7', '9']]],
     'expected': True},
    {'args': [[['1', '2', '.', '.', '3', '.', '.', '.', '.'],
               ['4', '.', '.', '5', '.', '.', '.', '.', '.'],
               ['.', '9', '1', '.', '.', '.', '.', '.', '3'],
               ['5', '.', '.', '.', '6', '.', '.', '.', '4'],
               ['.', '.', '.', '8', '.', '3', '.', '.', '5'],
               ['7', '.', '.', '.', '2', '.', '.', '.', '6'],
               ['.', '.', '.', '.', '.', '.', '2', '.', '.'],
               ['.', '.', '.', '4', '1', '9', '.', '.', '8'],
               ['.', '.', '.', '.', '8', '.', '.', '7', '9']]],
     'expected': False},
]


def check() -> None:
    from solution import valid_sudoku

    checked = 0
    for number, case in enumerate(CASES, 1):
        got = valid_sudoku(*case["args"])
        ok = got == case["expected"]
        assert ok, f"case {number}: got {got!r}, want {case['expected']!r}"
        checked += 1
    print(f"{checked} of {len(CASES)} visible checks passed")


if __name__ == "__main__":
    check()
