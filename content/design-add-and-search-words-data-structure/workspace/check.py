"""Visible checks for `design-add-and-search-words-data-structure` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'ops': [['addWord', 'bad'], ['addWord', 'dad'], ['addWord', 'mad'], ['search', 'pad'],
             ['search', 'bad'], ['search', '.ad'], ['search', 'b..']],
     'expected': [None, None, None, False, True, True, True]},
    {'ops': [['search', '.'], ['addWord', 'a'], ['search', '.'], ['search', 'a'],
             ['search', 'b'], ['search', 'aa']],
     'expected': [False, None, True, True, False, False]},
    {'ops': [['addWord', 'ba'], ['search', 'ba.'], ['search', '.a'], ['search', 'b.'],
             ['search', '..'], ['search', 'bad']],
     'expected': [None, False, True, True, True, False]},
    {'ops': [['addWord', 'bad'], ['search', 'ba'], ['search', '.ad'], ['search', 'b.d'],
             ['search', 'b..'], ['search', 'bad.']],
     'expected': [None, False, True, True, True, False]},
]


def check() -> None:
    import importlib.util
    from pathlib import Path

    _path = Path(__file__).with_name("solution.py")
    _spec = importlib.util.spec_from_file_location("artifact", _path)
    artifact = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(artifact)
    WordDictionary = artifact.WordDictionary

    for number, case in enumerate(CASES, 1):
        obj = WordDictionary(*case.get("ctor_args", []))
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
