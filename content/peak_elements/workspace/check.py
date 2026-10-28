"""Visible checks for `peak_elements` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'args': [[3, 5, 2, 4, 1]], 'predicate': 'is_peak', 'expected': True},
    {'args': [[4, 3, 2, 1]], 'expected': 0},
    {'args': [[1, 2, 3, 4]], 'expected': 3},
    {'args': [[1]], 'expected': 0},
]


def check() -> None:
    from solution import find_a_peak

    checked = 0
    for number, case in enumerate(CASES, 1):
        if "predicate" in case:
            # This one is decided by a dojo checker, not by equality:
            # `dojo check` runs it, and it is not reproduced here.
            continue
        got = find_a_peak(*case["args"])
        ok = got == case["expected"]
        assert ok, f"case {number}: got {got!r}, want {case['expected']!r}"
        checked += 1
    print(f"{checked} of {len(CASES)} visible checks passed")


if __name__ == "__main__":
    check()
