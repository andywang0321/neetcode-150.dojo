"""Visible checks for `serialize-and-deserialize-binary-tree` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'args': [[1, [2, None, None], [3, [4, None, None], [5, None, None]]]],
     'expected': [1, [2, None, None], [3, [4, None, None], [5, None, None]]],
     'predicate': 'tree_codec_roundtrip'},
    {'args': [None], 'expected': None, 'predicate': 'tree_codec_roundtrip'},
    {'args': [[-1000, None, None]],
     'expected': [-1000, None, None],
     'predicate': 'tree_codec_roundtrip'},
    {'args': [[7, [7, None, None], None]],
     'expected': [7, [7, None, None], None],
     'predicate': 'tree_codec_roundtrip'},
]


def check() -> None:
    import importlib.util
    from pathlib import Path

    _path = Path(__file__).with_name("solution.py")
    _spec = importlib.util.spec_from_file_location("artifact", _path)
    artifact = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(artifact)
    serialize = artifact.serialize

    checked = 0
    for number, case in enumerate(CASES, 1):
        if "predicate" in case:
            # This one is decided by a dojo checker, not by equality:
            # `dojo check` runs it, and it is not reproduced here.
            continue
        got = serialize(*case["args"])
        ok = got == case["expected"]
        assert ok, f"case {number}: got {got!r}, want {case['expected']!r}"
        checked += 1
    print(f"{checked} of {len(CASES)} visible checks passed")


if __name__ == "__main__":
    check()
