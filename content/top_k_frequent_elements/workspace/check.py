"""Visible checks for `top_k_frequent_elements` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'args': [[1, 2, 2, 3, 3, 3], 2], 'expected': [3, 2], 'compare': 'sorted'},
    {'args': [[7, 7], 1], 'expected': [7], 'compare': 'sorted'},
    {'args': [[8], 1], 'expected': [8], 'compare': 'sorted'},
    {'args': [[1, 1, 1, 2, 2, 3], 2], 'expected': [1, 2], 'compare': 'sorted'},
]


def check() -> None:
    from solution import top_k_freq

    checked = 0
    for number, case in enumerate(CASES, 1):
        got = top_k_freq(*case["args"])
        if case.get("compare") == "sorted":
            ok = sorted(map(repr, got)) == sorted(map(repr, case["expected"]))
        else:
            ok = got == case["expected"]
        assert ok, f"case {number}: got {got!r}, want {case['expected']!r}"
        checked += 1
    print(f"{checked} of {len(CASES)} visible checks passed")


if __name__ == "__main__":
    check()
