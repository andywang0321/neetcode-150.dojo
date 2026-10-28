"""Visible checks for `invert-binary-tree` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'args': [[4, [2, [1, None, None], [3, None, None]],
               [7, [6, None, None], [9, None, None]]]],
     'expected': [4, [7, [9, None, None], [6, None, None]],
                  [2, [3, None, None], [1, None, None]]]},
    {'args': [[2, [1, None, None], [3, None, None]]],
     'expected': [2, [3, None, None], [1, None, None]]},
    {'args': [None], 'expected': None},
]


def check() -> None:
    import importlib.util
    from pathlib import Path

    _path = Path(__file__).with_name("solution.py")
    _spec = importlib.util.spec_from_file_location("artifact", _path)
    artifact = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(artifact)
    invert_tree = artifact.invert_tree

    checked = 0
    for number, case in enumerate(CASES, 1):
        got = invert_tree(*case["args"])
        ok = got == case["expected"]
        assert ok, f"case {number}: got {got!r}, want {case['expected']!r}"
        checked += 1
    print(f"{checked} of {len(CASES)} visible checks passed")


if __name__ == "__main__":
    check()
