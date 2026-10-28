"""Visible checks for `powx-n` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'args': [2.0, 10], 'expected': 1024.0, 'compare': 'approx:1e-5'},
    {'args': [2.1, 3], 'expected': 9.261000000000001, 'compare': 'approx:1e-5'},
    {'args': [2.0, -2], 'expected': 0.25, 'compare': 'approx:1e-5'},
    {'args': [2.5, 0], 'expected': 1.0, 'compare': 'approx:1e-5'},
    {'args': [-2.0, 3], 'expected': -8.0, 'compare': 'approx:1e-5'},
]


def check() -> None:
    import importlib.util
    from pathlib import Path

    _path = Path(__file__).with_name("solution.py")
    _spec = importlib.util.spec_from_file_location("artifact", _path)
    artifact = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(artifact)
    my_pow = artifact.my_pow

    checked = 0
    for number, case in enumerate(CASES, 1):
        got = my_pow(*case["args"])
        if case.get("compare", "").startswith("approx"):
            ok = abs(got - case["expected"]) <= 1e-5
        else:
            ok = got == case["expected"]
        assert ok, f"case {number}: got {got!r}, want {case['expected']!r}"
        checked += 1
    print(f"{checked} of {len(CASES)} visible checks passed")


if __name__ == "__main__":
    check()
