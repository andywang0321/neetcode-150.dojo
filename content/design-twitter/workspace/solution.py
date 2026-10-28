class Twitter:
    def __init__(self):
        # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
        raise NotImplementedError

    def postTweet(self, userId: int, tweetId: int) -> None:
        # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
        raise NotImplementedError

    def getNewsFeed(self, userId: int) -> list[int]:
        # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
        raise NotImplementedError

    def follow(self, followerId: int, followeeId: int) -> None:
        # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
        raise NotImplementedError

    def unfollow(self, followerId: int, followeeId: int) -> None:
        # Solve it. Use `dojo check` / `dojo hint` from a second terminal.
        raise NotImplementedError


# --- dojo: visible examples (auto-generated — run this file, or press F5) ---
if __name__ == "__main__":
    _cases = [
        ([['postTweet', 1, 5], ['getNewsFeed', 1], ['follow', 1, 2], ['postTweet', 2, 6], ['getNewsFeed', 1], ['unfollow', 1, 2], ['getNewsFeed', 1]], [None, [5], None, None, [6, 5], None, [5]], []),
        ([['postTweet', 1, 5], ['postTweet', 1, 11], ['postTweet', 1, 3], ['postTweet', 1, 8], ['postTweet', 1, 12], ['postTweet', 1, 1], ['postTweet', 1, 9], ['postTweet', 1, 4], ['postTweet', 1, 7], ['postTweet', 1, 13], ['postTweet', 1, 2], ['postTweet', 1, 6], ['getNewsFeed', 1]], [None, None, None, None, None, None, None, None, None, None, None, None, [6, 2, 13, 7, 4, 9, 1, 12, 8, 3]], []),
        ([['getNewsFeed', 3], ['postTweet', 1, 10], ['postTweet', 2, 11], ['follow', 3, 1], ['follow', 3, 2], ['postTweet', 1, 12], ['getNewsFeed', 3], ['postTweet', 4, 13], ['unfollow', 3, 4], ['getNewsFeed', 3]], [[], None, None, None, None, None, [12, 11, 10], None, None, [12, 11, 10]], []),
    ]
    for _i, (_ops, _want, _ctor) in enumerate(_cases, 1):
        _obj = Twitter(*_ctor)
        _got = [getattr(_obj, _m)(*_a) for _m, *_a in _ops]
        _ok = _got == _want
        print(f"case {_i}: {'ok  ' if _ok else 'FAIL'} got={_got!r} want={_want!r}")
# --- end dojo ---
