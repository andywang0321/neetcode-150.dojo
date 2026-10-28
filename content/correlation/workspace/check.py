"""Visible checks for `correlation` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'args': [[1, 2, 3, 4, 5], [3, 2, 5, 9, 6]], 'expected': 0.7506, 'compare': 'approx:0.0001'},
    {'args': [[1, 2, 3], [1, 2, 3]], 'expected': 1.0, 'compare': 'approx:0.0001'},
    {'args': [[1, 2, 3], [3, 2, 1]], 'expected': -1.0, 'compare': 'approx:0.0001'},
]


def check() -> None:
    from solution import correlation

    checked = 0
    for number, case in enumerate(CASES, 1):
        got = correlation(*case["args"])
        if case.get("compare", "").startswith("approx"):
            ok = abs(got - case["expected"]) <= 0.0001
        else:
            ok = got == case["expected"]
        assert ok, f"case {number}: got {got!r}, want {case['expected']!r}"
        checked += 1
    print(f"{checked} of {len(CASES)} visible checks passed")


if __name__ == "__main__":
    check()
