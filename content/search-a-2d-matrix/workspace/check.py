"""Visible checks for `search-a-2d-matrix` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'args': [[[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]], 3], 'expected': True},
    {'args': [[[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]], 13], 'expected': False},
    {'args': [[[1]], 1], 'expected': True},
    {'args': [[[1, 3]], 2], 'expected': False},
]


def check() -> None:
    import importlib.util
    from pathlib import Path

    _path = Path(__file__).with_name("solution.py")
    _spec = importlib.util.spec_from_file_location("artifact", _path)
    artifact = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(artifact)
    search_matrix = artifact.search_matrix

    checked = 0
    for number, case in enumerate(CASES, 1):
        got = search_matrix(*case["args"])
        ok = got == case["expected"]
        assert ok, f"case {number}: got {got!r}, want {case['expected']!r}"
        checked += 1
    print(f"{checked} of {len(CASES)} visible checks passed")


if __name__ == "__main__":
    check()
