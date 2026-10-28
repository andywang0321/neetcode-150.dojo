"""Visible checks for `surrounded-regions` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'args': [[['X', 'X', 'X', 'X'], ['X', 'O', 'O', 'X'], ['X', 'X', 'O', 'X'],
               ['X', 'O', 'X', 'X']]],
     'expected': [[['X', 'X', 'X', 'X'], ['X', 'X', 'X', 'X'], ['X', 'X', 'X', 'X'],
                   ['X', 'O', 'X', 'X']]],
     'compare': 'mutates'},
    {'args': [[['X']]], 'expected': [[['X']]], 'compare': 'mutates'},
    {'args': [[['O', 'O'], ['O', 'O']]],
     'expected': [[['O', 'O'], ['O', 'O']]],
     'compare': 'mutates'},
    {'args': [[['X', 'X', 'X'], ['X', 'O', 'X'], ['X', 'X', 'X']]],
     'expected': [[['X', 'X', 'X'], ['X', 'X', 'X'], ['X', 'X', 'X']]],
     'compare': 'mutates'},
]


def check() -> None:
    import importlib.util
    from pathlib import Path

    _path = Path(__file__).with_name("solution.py")
    _spec = importlib.util.spec_from_file_location("artifact", _path)
    artifact = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(artifact)
    solve = artifact.solve

    checked = 0
    for number, case in enumerate(CASES, 1):
        got = solve(*case["args"])
        compared = case["args"] if case.get("compare") == "mutates" else got
        ok = compared == case["expected"]
        assert ok, f"case {number}: got {compared!r}, want {case['expected']!r}"
        checked += 1
    print(f"{checked} of {len(CASES)} visible checks passed")


if __name__ == "__main__":
    check()
