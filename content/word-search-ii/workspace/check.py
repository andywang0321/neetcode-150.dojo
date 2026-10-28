"""Visible checks for `word-search-ii` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'args': [[['o', 'a', 'a', 'n'], ['e', 't', 'a', 'e'], ['i', 'h', 'k', 'r'],
               ['i', 'f', 'l', 'v']],
              ['oath', 'pea', 'eat', 'rain']],
     'expected': ['eat', 'oath'],
     'compare': 'sorted'},
    {'args': [[['a', 'b'], ['c', 'd']], ['abcb']], 'expected': [], 'compare': 'sorted'},
    {'args': [[['a']], ['a', 'aa']], 'expected': ['a'], 'compare': 'sorted'},
    {'args': [[['a', 'a']], ['a', 'aa', 'aaa', 'b']],
     'expected': ['a', 'aa'],
     'compare': 'sorted'},
]


def check() -> None:
    import importlib.util
    from pathlib import Path

    _path = Path(__file__).with_name("solution.py")
    _spec = importlib.util.spec_from_file_location("artifact", _path)
    artifact = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(artifact)
    find_words = artifact.find_words

    checked = 0
    for number, case in enumerate(CASES, 1):
        got = find_words(*case["args"])
        if case.get("compare") == "sorted":
            ok = sorted(map(repr, got)) == sorted(map(repr, case["expected"]))
        else:
            ok = got == case["expected"]
        assert ok, f"case {number}: got {got!r}, want {case['expected']!r}"
        checked += 1
    print(f"{checked} of {len(CASES)} visible checks passed")


if __name__ == "__main__":
    check()
