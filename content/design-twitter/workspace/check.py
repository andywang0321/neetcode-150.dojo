"""Visible checks for `design-twitter` — the student runs these.

Shipped to the student and rendered into their workbench, so they check the
statement's promises and nothing more. The verdict that counts comes from the
oracle and its generated cases, which are quarantined in `assessment/`.
"""

CASES = [
    {'ops': [['postTweet', 1, 5], ['getNewsFeed', 1], ['follow', 1, 2], ['postTweet', 2, 6],
             ['getNewsFeed', 1], ['unfollow', 1, 2], ['getNewsFeed', 1]],
     'expected': [None, [5], None, None, [6, 5], None, [5]]},
    {'ops': [['postTweet', 1, 5], ['postTweet', 1, 11], ['postTweet', 1, 3],
             ['postTweet', 1, 8], ['postTweet', 1, 12], ['postTweet', 1, 1],
             ['postTweet', 1, 9], ['postTweet', 1, 4], ['postTweet', 1, 7],
             ['postTweet', 1, 13], ['postTweet', 1, 2], ['postTweet', 1, 6],
             ['getNewsFeed', 1]],
     'expected': [None, None, None, None, None, None, None, None, None, None, None, None,
                  [6, 2, 13, 7, 4, 9, 1, 12, 8, 3]]},
    {'ops': [['getNewsFeed', 3], ['postTweet', 1, 10], ['postTweet', 2, 11], ['follow', 3, 1],
             ['follow', 3, 2], ['postTweet', 1, 12], ['getNewsFeed', 3], ['postTweet', 4, 13],
             ['unfollow', 3, 4], ['getNewsFeed', 3]],
     'expected': [[], None, None, None, None, None, [12, 11, 10], None, None, [12, 11, 10]]},
]


def check() -> None:
    import importlib.util
    from pathlib import Path

    _path = Path(__file__).with_name("solution.py")
    _spec = importlib.util.spec_from_file_location("artifact", _path)
    artifact = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(artifact)
    Twitter = artifact.Twitter

    for number, case in enumerate(CASES, 1):
        obj = Twitter(*case.get("ctor_args", []))
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
