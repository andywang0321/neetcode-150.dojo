"""Visible checks for `combination-sum-ii` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'args': [[10, 1, 2, 7, 6, 1, 5], 8],
     'expected': [[1, 1, 6], [1, 2, 5], [1, 7], [2, 6]],
     'compare': 'sorted'},
    {'args': [[2, 5, 2, 1, 2], 5], 'expected': [[1, 2, 2], [5]], 'compare': 'sorted'},
    {'args': [[3, 3], 4], 'expected': [], 'compare': 'sorted'},
]


def check() -> None:
    import importlib.util
    from pathlib import Path

    _path = Path(__file__).with_name("solution.py")
    _spec = importlib.util.spec_from_file_location("artifact", _path)
    artifact = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(artifact)
    combination_sum2 = artifact.combination_sum2

    checked = 0
    for number, case in enumerate(CASES, 1):
        got = combination_sum2(*case["args"])
        if case.get("compare") == "sorted":
            ok = sorted(map(repr, got)) == sorted(map(repr, case["expected"]))
        else:
            ok = got == case["expected"]
        assert ok, f"case {number}: got {got!r}, want {case['expected']!r}"
        checked += 1
    print(f"{checked} of {len(CASES)} visible checks passed")


if __name__ == "__main__":
    check()
