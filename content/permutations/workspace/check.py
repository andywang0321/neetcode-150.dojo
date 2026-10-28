"""Visible checks for `permutations` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'args': [[1, 2, 3]],
     'expected': [[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]],
     'compare': 'sorted'},
    {'args': [[0, 1]], 'expected': [[0, 1], [1, 0]], 'compare': 'sorted'},
    {'args': [[1]], 'expected': [[1]], 'compare': 'sorted'},
]


def check() -> None:
    from solution import permutations

    checked = 0
    for number, case in enumerate(CASES, 1):
        got = permutations(*case["args"])
        if case.get("compare") == "sorted":
            ok = sorted(map(repr, got)) == sorted(map(repr, case["expected"]))
        else:
            ok = got == case["expected"]
        assert ok, f"case {number}: got {got!r}, want {case['expected']!r}"
        checked += 1
    print(f"{checked} of {len(CASES)} visible checks passed")


if __name__ == "__main__":
    check()
