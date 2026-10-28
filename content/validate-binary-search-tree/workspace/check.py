"""Visible checks for `validate-binary-search-tree` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'args': [[2, [1, None, None], [3, None, None]]], 'expected': True},
    {'args': [[5, [1, None, None], [4, [3, None, None], [6, None, None]]]], 'expected': False},
    {'args': [[5, [4, None, None], [6, [3, None, None], [7, None, None]]]], 'expected': False},
]


def check() -> None:
    import importlib.util
    from pathlib import Path

    _path = Path(__file__).with_name("solution.py")
    _spec = importlib.util.spec_from_file_location("artifact", _path)
    artifact = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(artifact)
    is_valid_bst = artifact.is_valid_bst

    checked = 0
    for number, case in enumerate(CASES, 1):
        got = is_valid_bst(*case["args"])
        ok = got == case["expected"]
        assert ok, f"case {number}: got {got!r}, want {case['expected']!r}"
        checked += 1
    print(f"{checked} of {len(CASES)} visible checks passed")


if __name__ == "__main__":
    check()
