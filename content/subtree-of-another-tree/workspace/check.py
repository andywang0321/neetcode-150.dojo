"""Visible checks for `subtree-of-another-tree` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'args': [[3, [4, [1, None, None], [2, None, None]], [5, None, None]],
              [4, [1, None, None], [2, None, None]]],
     'expected': True},
    {'args': [[3, [4, [1, None, None], [2, [0, None, None], None]], [5, None, None]],
              [4, [1, None, None], [2, None, None]]],
     'expected': False},
    {'args': [[1, [2, None, None], None], [1, [2, None, None], None]], 'expected': True},
    {'args': [[1, None, None], [2, None, None]], 'expected': False},
]


def check() -> None:
    import importlib.util
    from pathlib import Path

    _path = Path(__file__).with_name("solution.py")
    _spec = importlib.util.spec_from_file_location("artifact", _path)
    artifact = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(artifact)
    is_subtree = artifact.is_subtree

    checked = 0
    for number, case in enumerate(CASES, 1):
        got = is_subtree(*case["args"])
        ok = got == case["expected"]
        assert ok, f"case {number}: got {got!r}, want {case['expected']!r}"
        checked += 1
    print(f"{checked} of {len(CASES)} visible checks passed")


if __name__ == "__main__":
    check()
