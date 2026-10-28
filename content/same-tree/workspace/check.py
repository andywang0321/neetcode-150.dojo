"""Visible checks for `same-tree` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'args': [[1, [2, None, None], [3, None, None]], [1, [2, None, None], [3, None, None]]],
     'expected': True},
    {'args': [[1, [2, None, None], None], [1, None, [2, None, None]]], 'expected': False},
    {'args': [[1, [2, None, None], [1, None, None]], [1, [1, None, None], [2, None, None]]],
     'expected': False},
    {'args': [None, None], 'expected': True},
]


def check() -> None:
    import importlib.util
    from pathlib import Path

    _path = Path(__file__).with_name("solution.py")
    _spec = importlib.util.spec_from_file_location("artifact", _path)
    artifact = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(artifact)
    is_same_tree = artifact.is_same_tree

    checked = 0
    for number, case in enumerate(CASES, 1):
        got = is_same_tree(*case["args"])
        ok = got == case["expected"]
        assert ok, f"case {number}: got {got!r}, want {case['expected']!r}"
        checked += 1
    print(f"{checked} of {len(CASES)} visible checks passed")


if __name__ == "__main__":
    check()
