"""Visible checks for `implement-trie-prefix-tree` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'ops': [['insert', 'apple'], ['search', 'apple'], ['search', 'app'], ['startsWith', 'app'],
             ['insert', 'app'], ['search', 'app']],
     'expected': [None, True, False, True, None, True]},
    {'ops': [['search', 'a'], ['startsWith', 'a'], ['insert', 'a'], ['search', 'a'],
             ['startsWith', 'ab'], ['search', 'ab']],
     'expected': [False, False, None, True, False, False]},
    {'ops': [['insert', 'app'], ['search', 'app'], ['insert', 'apple'], ['search', 'app'],
             ['search', 'apple'], ['search', 'appl'], ['startsWith', 'appl']],
     'expected': [None, True, None, True, True, False, True]},
]


def check() -> None:
    import importlib.util
    from pathlib import Path

    _path = Path(__file__).with_name("solution.py")
    _spec = importlib.util.spec_from_file_location("artifact", _path)
    artifact = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(artifact)
    Trie = artifact.Trie

    for number, case in enumerate(CASES, 1):
        obj = Trie(*case.get("ctor_args", []))
        got = []
        for op in case["ops"]:
            method, *args = op
            got.append(getattr(obj, method)(*args))
        assert got == case["expected"], (
            f"case {number}: got {got!r}, want {case['expected']!r}"
        )
    print(f"all {len(CASES)} visible checks passed")


if __name__ == "__main__":
    check()
