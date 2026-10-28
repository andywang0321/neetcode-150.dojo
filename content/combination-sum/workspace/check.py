"""Visible checks for `combination-sum` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'args': [[2, 3, 6, 7], 7], 'expected': [[2, 2, 3], [7]], 'compare': 'sorted'},
    {'args': [[2, 3, 5], 8], 'expected': [[2, 2, 2, 2], [2, 3, 3], [3, 5]], 'compare': 'sorted'},
    {'args': [[2], 1], 'expected': [], 'compare': 'sorted'},
]


def check() -> None:
    import importlib.util
    from pathlib import Path

    _path = Path(__file__).with_name("solution.py")
    _spec = importlib.util.spec_from_file_location("artifact", _path)
    artifact = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(artifact)
    combination_sum = artifact.combination_sum

    checked = 0
    for number, case in enumerate(CASES, 1):
        got = combination_sum(*case["args"])
        if case.get("compare") == "sorted":
            ok = sorted(map(repr, got)) == sorted(map(repr, case["expected"]))
        else:
            ok = got == case["expected"]
        assert ok, f"case {number}: got {got!r}, want {case['expected']!r}"
        checked += 1
    print(f"{checked} of {len(CASES)} visible checks passed")


if __name__ == "__main__":
    check()
