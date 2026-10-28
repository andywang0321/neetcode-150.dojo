"""Visible checks for `course-schedule-ii` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'args': [2, [[1, 0]]], 'expected': [0, 1], 'predicate': 'valid_topological_order'},
    {'args': [4, [[1, 0], [2, 0], [3, 1], [3, 2]]],
     'expected': [0, 2, 1, 3],
     'predicate': 'valid_topological_order'},
    {'args': [1, []], 'expected': [0], 'predicate': 'valid_topological_order'},
    {'args': [2, [[1, 0], [0, 1]]], 'expected': [], 'predicate': 'valid_topological_order'},
]


def check() -> None:
    import importlib.util
    from pathlib import Path

    _path = Path(__file__).with_name("solution.py")
    _spec = importlib.util.spec_from_file_location("artifact", _path)
    artifact = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(artifact)
    find_order = artifact.find_order

    checked = 0
    for number, case in enumerate(CASES, 1):
        if "predicate" in case:
            # This one is decided by a dojo checker, not by equality:
            # `dojo check` runs it, and it is not reproduced here.
            continue
        got = find_order(*case["args"])
        ok = got == case["expected"]
        assert ok, f"case {number}: got {got!r}, want {case['expected']!r}"
        checked += 1
    print(f"{checked} of {len(CASES)} visible checks passed")


if __name__ == "__main__":
    check()
