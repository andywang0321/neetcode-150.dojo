"""Visible checks for `merge-intervals` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'args': [[[1, 3], [2, 6], [8, 10], [15, 18]]],
     'expected': [[1, 6], [8, 10], [15, 18]],
     'compare': 'sorted'},
    {'args': [[[1, 4], [4, 5]]], 'expected': [[1, 5]], 'compare': 'sorted'},
    {'args': [[[4, 7], [1, 4]]], 'expected': [[1, 7]], 'compare': 'sorted'},
    {'args': [[[5, 5]]], 'expected': [[5, 5]], 'compare': 'sorted'},
    {'args': [[[1, 2], [2, 2], [2, 5]]], 'expected': [[1, 5]], 'compare': 'sorted'},
]


def check() -> None:
    import importlib.util
    from pathlib import Path

    _path = Path(__file__).with_name("solution.py")
    _spec = importlib.util.spec_from_file_location("artifact", _path)
    artifact = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(artifact)
    merge = artifact.merge

    checked = 0
    for number, case in enumerate(CASES, 1):
        got = merge(*case["args"])
        if case.get("compare") == "sorted":
            ok = sorted(map(repr, got)) == sorted(map(repr, case["expected"]))
        else:
            ok = got == case["expected"]
        assert ok, f"case {number}: got {got!r}, want {case['expected']!r}"
        checked += 1
    print(f"{checked} of {len(CASES)} visible checks passed")


if __name__ == "__main__":
    check()
