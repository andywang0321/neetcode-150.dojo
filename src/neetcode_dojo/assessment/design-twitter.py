"""QUARANTINED assessment for `design-twitter` (transcribed from the pre-split registry).

Nothing here may reach a student or an AI agent that talks to one: these are the
answers in machine form. See `docs/curricula.md` §2.
"""

import random

from neetcode_dojo.registry import cases, oracle, reference


@oracle("design-twitter")
def _design_twitter_oracle(ops: list[list]) -> list:
    """Brute force, driven through the statement's own op list: keep one global
    log of (post order, author, tweetId) and answer every getNewsFeed by walking
    the log from the newest entry backwards, keeping the tweets whose author is
    the reader or someone they follow. No heaps, no per-user lists, no sorting by
    tweetId, and no dependence on dict or set iteration order — recency is post
    order and nothing else, which is exactly the contract the statement states.
    """
    log: list[tuple[int, int, int]] = []  # (post order, author, tweetId)
    following: dict[int, set[int]] = {}
    out: list = []
    for op in ops:
        method, *args = op
        if method == "postTweet":
            user, tweet = args
            log.append((len(log), user, tweet))
            out.append(None)
        elif method == "getNewsFeed":
            user = args[0]
            allowed = set(following.get(user, ())) | {user}
            feed: list[int] = []
            for _order, author, tweet in reversed(log):
                if author in allowed:
                    feed.append(tweet)
                    if len(feed) == 10:
                        break
            out.append(feed)
        elif method == "follow":
            follower, followee = args
            following.setdefault(follower, set()).add(followee)
            out.append(None)
        elif method == "unfollow":
            follower, followee = args
            following.setdefault(follower, set()).discard(followee)
            out.append(None)
        else:  # pragma: no cover - the generator only emits the four methods
            raise ValueError(f"unknown op {method}")
    return out


@cases("design-twitter")
def _design_twitter_case(n: int, rng: random.Random) -> tuple[list, list, dict]:
    # Deterministic by construction: every op comes from the seeded rng, the user
    # pool is a fixed list, the "already followed" pairs are read through
    # sorted(), and tweet ids are drawn without replacement from the statement's
    # own 0..10^4 range. The same (n, rng) always replays the same sequence, and
    # the harness builds a fresh Twitter for every case, so no state crosses
    # cases.
    steps = 3 * max(1, min(n, 12)) + 4
    users = [1, 2, 3]
    used_ids: set[int] = set()
    following: set[tuple[int, int]] = set()
    # A feed with nothing in it first: the statement documents no special case
    # for it, so [] is the answer, and every generated case pins it.
    ops: list[list] = [["getNewsFeed", rng.choice(users)]]
    for _ in range(steps):
        # Weighted towards posting and reading: with a small pool of three users
        # that is what pushes some feeds past 10 tweets, so the statement's cap
        # ("the 10 most recent tweet IDs") is exercised by generated cases too.
        method = rng.choice(
            ["postTweet"] * 4 + ["getNewsFeed"] * 3 + ["follow"] * 2 + ["unfollow"] * 2
        )
        if method == "postTweet":
            tweet = rng.randint(0, 10_000)
            while tweet in used_ids:  # "All the tweets have unique IDs."
                tweet = rng.randint(0, 10_000)
            used_ids.add(tweet)
            ops.append(["postTweet", rng.choice(users), tweet])
        elif method == "getNewsFeed":
            ops.append(["getNewsFeed", rng.choice(users)])
        elif method == "follow":
            follower = rng.choice(users)
            # "A user cannot follow himself" — never generated.
            followee = rng.choice([user for user in users if user != follower])
            following.add((follower, followee))
            ops.append(["follow", follower, followee])
        else:
            if following and rng.random() < 0.7:
                follower, followee = rng.choice(sorted(following))
                following.discard((follower, followee))
            else:  # unfollowing a user who was never followed is a legal no-op
                follower = rng.choice(users)
                followee = rng.choice([user for user in users if user != follower])
            ops.append(["unfollow", follower, followee])
    return [], _design_twitter_oracle(ops), {"ops": ops}


@reference("design-twitter")
def _design_twitter_reference(ops: list[list]) -> list:
    """Canonical Twitter, driven through the same op list the oracle takes. Each
    user keeps their tweets in post order as (sequence, tweetId), and
    getNewsFeed merges the newest tweet of the reader and of each followee
    through a max-heap, popping at most 10 and pushing that author's next-newest
    back: O(1) per post/follow/unfollow, O(f + 10 log f) per feed for f
    followees. Sequence numbers are unique, so the heap never falls back on a
    tuple tie-break and the feed order is decided by post order alone — never by
    tweetId, and never by set or dict iteration order (the followees are read
    through sorted()).
    """
    import heapq

    tweets: dict[int, list[tuple[int, int]]] = {}
    following: dict[int, set[int]] = {}
    sequence = 0
    out: list = []
    for op in ops:
        method, *args = op
        if method == "postTweet":
            user, tweet = args
            sequence += 1
            tweets.setdefault(user, []).append((sequence, tweet))
            out.append(None)
        elif method == "getNewsFeed":
            user = args[0]
            heap: list[tuple[int, int, int]] = []
            for author in [user] + sorted(following.get(user, ())):
                own = tweets.get(author)
                if own:
                    newest = len(own) - 1
                    heapq.heappush(heap, (-own[newest][0], author, newest))
            feed: list[int] = []
            while heap and len(feed) < 10:
                _neg, author, index = heapq.heappop(heap)
                own = tweets[author]
                feed.append(own[index][1])
                if index > 0:
                    heapq.heappush(heap, (-own[index - 1][0], author, index - 1))
            out.append(feed)
        elif method == "follow":
            follower, followee = args
            following.setdefault(follower, set()).add(followee)
            out.append(None)
        elif method == "unfollow":
            follower, followee = args
            following.setdefault(follower, set()).discard(followee)
            out.append(None)
        else:  # pragma: no cover - the generator only emits the four methods
            raise ValueError(f"unknown op {method}")
    return out
