"""Visible checks for `palindrome-partitioning` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'args': ['aab'], 'expected': [['a', 'a', 'b'], ['aa', 'b']], 'compare': 'sorted'},
    {'args': ['a'], 'expected': [['a']], 'compare': 'sorted'},
    {'args': ['aaa'],
     'expected': [['a', 'a', 'a'], ['a', 'aa'], ['aa', 'a'], ['aaa']],
     'compare': 'sorted'},
]


def check() -> None:
    import importlib.util
    from pathlib import Path

    _path = Path(__file__).with_name("solution.py")
    _spec = importlib.util.spec_from_file_location("artifact", _path)
    artifact = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(artifact)
    partition = artifact.partition

    checked = 0
    for number, case in enumerate(CASES, 1):
        got = partition(*case["args"])
        if case.get("compare") == "sorted":
            ok = sorted(map(repr, got)) == sorted(map(repr, case["expected"]))
        else:
            ok = got == case["expected"]
        assert ok, f"case {number}: got {got!r}, want {case['expected']!r}"
        checked += 1
    print(f"{checked} of {len(CASES)} visible checks passed")


if __name__ == "__main__":
    check()
