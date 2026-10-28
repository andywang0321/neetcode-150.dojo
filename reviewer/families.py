"""The eighteen NeetCode 150 pattern families, as review data.

The reviewer names a family from the item slug or statement, then uses the family's
expected complexity, usual failure points and aligned constructs to ground its advice.
This module is data only; the detection logic lives in `reviewer.patterns`.
"""

from dataclasses import dataclass

GENERAL = "General algorithms"


@dataclass(frozen=True, slots=True)
class Pattern:
    """One NeetCode topic family and the advice tied to it."""

    name: str
    markers: tuple[str, ...]
    keywords: tuple[str, ...]
    expected_time: str
    expected_space: str
    edge_cases: tuple[str, ...]
    strengths: tuple[tuple[str, str], ...] = ()
    revisit: str | None = None
    revisit_if: tuple[str, ...] = ()


def _family(
    name: str,
    markers: str,
    keywords: str,
    expected_time: str,
    expected_space: str,
    edge_cases: str,
    strengths: tuple[tuple[str, str], ...] = (),
    revisit: str | None = None,
    revisit_if: str = "",
) -> Pattern:
    """Build one family from compact pipe/space-separated strings."""
    return Pattern(
        name=name,
        markers=tuple(markers.split()),
        keywords=tuple(keywords.split("|")),
        expected_time=expected_time,
        expected_space=expected_space,
        edge_cases=tuple(edge_cases.split("|")),
        strengths=strengths,
        revisit=revisit,
        revisit_if=tuple(revisit_if.split()),
    )


PATTERNS: tuple[Pattern, ...] = (
    _family(
        "Two Pointers",
        ("two-sum-ii 3sum container-with-most-water trapping-rain-water valid-palindrome"),
        "two pointer|two-pointer|move pointers",
        "O(n)",
        "O(1)",
        "two elements|duplicate values|an already sorted input",
        (
            ("two_pointer", "Moves two indices through the data instead of re-scanning it."),
            ("sort", "Sorts once so the two-pointer sweep is valid."),
        ),
        (
            "The code does not show a moving two-pointer loop; the usual linear solution "
            "avoids nested scans."
        ),
        "nested_loop",
    ),
    _family(
        "Sliding Window",
        (
            "best-time-to-buy-and-sell-stock longest-substring-without-repeating-characters "
            "longest-repeating-character-replacement permutation-in-string "
            "find-all-anagrams-in-a-string minimum-window-substring sliding-window-maximum"
        ),
        "sliding window|window",
        "O(n)",
        "O(k)",
        "an empty string or list|a window that never shrinks|all characters identical",
        (
            ("hash_map", "Tracks the window with a hash map, so each step is incremental."),
            ("set", "Tracks window membership without rescanning it."),
            ("deque", "Keeps a monotonic window state."),
        ),
        (
            "No incremental window state is visible; each step should add one element and "
            "remove at most one."
        ),
        "nested_loop",
    ),
    _family(
        "Stack",
        (
            "valid-parentheses min-stack evaluate-reverse-polish-notation daily-temperatures "
            "car-fleet largest-rectangle-in-histogram"
        ),
        "stack|parenthes",
        "O(n)",
        "O(n)",
        "an unmatched closing token|a single token|deeply nested input",
        (
            ("list_ops", "Uses append/pop operations, the shape of a stack."),
            ("deque", "Uses a deque for the stack operations."),
            ("hash_map", "Pairs opening and closing tokens with a lookup."),
        ),
        (
            "No explicit stack operation is visible; confirm the code keeps the pending "
            "items rather than re-scanning them."
        ),
    ),
    _family(
        "Binary Search",
        (
            "binary-search search-a-2d-matrix koko-eating-bananas "
            "find-minimum-in-rotated-sorted-array search-in-rotated-sorted-array "
            "median-of-two-sorted-arrays time-based-key-value-store"
        ),
        "binary search|logarithmic|sorted array",
        "O(log n)",
        "O(1)",
        "an empty array|a target outside the range|duplicate boundary values",
        (
            ("binary_search_loop", "Maintains a low/high interval and halves it each step."),
            ("bisect", "Uses the standard bisect helpers for the halving search."),
        ),
        (
            "No halving midpoint loop or bisect call is visible; the expected bound for "
            "this item is logarithmic."
        ),
    ),
    _family(
        "Linked List",
        (
            "reverse-linked-list merge-two-sorted-lists reorder-list "
            "remove-nth-node-from-end-of-list copy-list-with-random-pointer add-two-numbers "
            "linked-list-cycle find-the-duplicate-number lru-cache reverse-nodes-in-k-group "
            "merge-k-sorted-lists palindrome-linked-list"
        ),
        "linked list|listnode",
        "O(n)",
        "O(1)",
        "an empty list|a single node|two nodes",
        (
            ("two_pointer", "Uses two references to walk the list without extra storage."),
            ("recursion", "Uses recursion cleanly on the list structure."),
            ("hash_map", "Uses a hash map to track nodes."),
        ),
        (
            "Confirm the pointer updates handle the empty list, one node, and the tail node "
            "before returning."
        ),
    ),
    _family(
        "Trees",
        (
            "invert-binary-tree maximum-depth-of-binary-tree diameter-of-binary-tree "
            "balanced-binary-tree same-tree subtree-of-another-tree lowest-common-ancestor "
            "binary-tree-level-order-traversal binary-tree-right-side-view "
            "count-good-nodes-in-binary-tree validate-binary-search-tree "
            "kth-smallest-element-in-a-bst construct-binary-tree "
            "serialize-and-deserialize-binary-tree binary-tree-maximum-path-sum"
        ),
        "binary tree|tree node|treenode|bst",
        "O(n)",
        "O(h)",
        "an empty tree|a single node|a completely skewed tree",
        (
            ("recursion", "Recurses over the tree structure with a clear base case."),
            ("deque", "Uses a queue for level-order traversal."),
            ("hash_map", "Indexes nodes or values instead of searching repeatedly."),
        ),
        (
            "Check the null-node base case before the recursive calls, and confirm the "
            "traversal reaches every subtree."
        ),
    ),
    _family(
        "Tries",
        ("implement-trie design-add-and-search-words-data-structure word-search-ii"),
        "trie|prefix",
        "O(L) per operation",
        "O(total characters)",
        "an empty word|a prefix that is not a word|words that share long prefixes",
        (
            ("class", "Defines a node/prefix type rather than flat searches."),
            ("hash_map", "Stores children in a hash map, the usual trie node shape."),
        ),
        (
            "Confirm the terminal-word marker is separate from the prefix path, so a prefix "
            "is not reported as a word."
        ),
    ),
    _family(
        "Heap / Priority Queue",
        (
            "kth-largest-element-in-a-stream last-stone-weight k-closest-points-to-origin "
            "kth-largest-element-in-an-array task-scheduler design-twitter "
            "find-median-from-data-stream"
        ),
        "heap|priority queue|k largest|k smallest",
        "O(n log k)",
        "O(k)",
        "k = 1|k = n|duplicate priorities",
        (
            ("heap", "Uses a heap to keep the relevant candidates ordered."),
            ("sort", "Sorts when a full ordering is cheaper than maintaining a heap."),
        ),
        (
            "No heap operation is visible; the expected bound for this item usually comes "
            "from keeping only k elements ordered."
        ),
    ),
    _family(
        "Backtracking",
        (
            "subsets combination-sum permutations word-search palindrome-partitioning "
            "letter-combinations-of-a-phone-number n-queens generate-parentheses"
        ),
        "backtrack|all combinations|all permutations",
        "exponential",
        "O(n)",
        "empty candidates|duplicate candidates|a target of zero",
        (
            ("recursion", "Explores choices recursively with an undo step."),
            ("set", "Deduplicates choices or partial states."),
        ),
        (
            "Confirm every recursive branch undoes its choice before returning, and that "
            "duplicates are pruned deliberately."
        ),
    ),
    _family(
        "Graphs",
        (
            "number-of-islands max-area-of-island clone-graph pacific-atlantic-water-flow "
            "surrounded-regions rotting-oranges walls-and-gates course-schedule "
            "redundant-connection word-ladder "
            "number-of-connected-components-in-an-undirected-graph graph-valid-tree"
        ),
        "grid|graph|bfs|dfs",
        "O(V + E)",
        "O(V)",
        "an empty grid|disconnected components|a node with no edges",
        (
            ("visited", "Tracks visited nodes so each component is explored once."),
            ("deque", "Uses a queue for breadth-first traversal."),
            ("recursion", "Uses recursive depth-first traversal with a base case."),
        ),
        (
            "No BFS/DFS marker (visited set, queue, or recursion) is visible; confirm "
            "disconnected components are covered."
        ),
    ),
    _family(
        "Advanced Graphs",
        (
            "reconstruct-itinerary min-cost-to-connect-points network-delay-time "
            "swim-in-rising-water alien-dictionary cheapest-flights-within-k-stops"
        ),
        "dijkstra|minimum spanning|topological|bellman",
        "O(E log V)",
        "O(V)",
        "unreachable nodes|cycles|multiple edges between two nodes",
        (
            ("heap", "Uses a priority queue for the weighted traversal."),
            ("visited", "Tracks settled nodes."),
            ("sort", "Sorts edges for the selected algorithm."),
        ),
        (
            "Name the graph algorithm in the review and confirm its complexity: weighted "
            "shortest paths and spanning trees need more than a plain BFS."
        ),
    ),
    _family(
        "1-D Dynamic Programming",
        (
            "climbing-stairs min-cost-climbing-stairs house-robber longest-palindromic-substring "
            "palindromic-substrings decode-ways coin-change max-product-subarray word-break "
            "longest-increasing-subsequence partition-equal-subset-sum maximum-subarray"
        ),
        "dynamic programming|dp|subproblem",
        "O(n)",
        "O(n) or O(1)",
        "n = 1|zero-valued inputs|the final state rather than the whole table",
        (
            ("memo", "Caches subproblem results instead of recomputing them."),
            ("dp_array", "Builds a one-dimensional state table."),
        ),
        (
            "No DP state (memo, cache, or dp array) is visible; the expected approach "
            "stores subproblem results."
        ),
    ),
    _family(
        "2-D Dynamic Programming",
        (
            "unique-paths longest-common-subsequence best-time-to-buy-and-sell-stock-with-cooldown "
            "coin-change-ii target-sum interleaving-string longest-increasing-path-in-a-matrix "
            "distinct-subsequences edit-distance burst-balloons regular-expression-matching"
        ),
        "2d dp|two-dimensional|grid dp|edit distance",
        "O(m * n)",
        "O(m * n) or O(n)",
        "an empty row or column|a 1 x 1 grid|the base row and column",
        (
            ("dp_table", "Builds a two-dimensional state table."),
            ("memo", "Caches subproblems while recursing over two indices."),
        ),
        "Confirm the base row/column are initialised before the table is filled.",
    ),
    _family(
        "Greedy",
        (
            "jump-game jump-game-ii gas-station hand-of-straights "
            "merge-triplets-to-form-target-triplet partition-labels valid-parenthesis-string"
        ),
        "greedy|locally optimal",
        "O(n) or O(n log n)",
        "O(1)",
        "all-equal elements|a local choice that fails globally|the last index",
        (
            ("sort", "Sorts before applying the greedy choice."),
            ("hash_map", "Counts the resources the greedy step needs."),
        ),
        (
            "State the invariant that makes the local choice safe; otherwise a "
            "counterexample can defeat the strategy."
        ),
    ),
    _family(
        "Intervals",
        (
            "insert-interval merge-intervals non-overlapping-intervals meeting-rooms "
            "meeting-rooms-ii minimum-interval-to-include-each-query"
        ),
        "interval|overlap",
        "O(n log n)",
        "O(n)",
        "touching intervals|nested intervals|a single interval",
        (
            ("sort", "Sorts by an endpoint so overlaps are adjacent."),
            ("heap", "Tracks the active interval with a heap."),
        ),
        (
            "Check whether touching endpoints count as overlapping for this item, and sort "
            "by the field that makes the sweep valid."
        ),
    ),
    _family(
        "Math & Geometry",
        (
            "rotate-image spiral-matrix set-matrix-zeroes happy-number plus-one pow-x-n "
            "multiply-strings detect-squares"
        ),
        "matrix rotation|geometry|arithmetic",
        "varies",
        "O(1)",
        "zero|negative values|the bounds of the numeric type",
        (
            ("bit_ops", "Uses bit operations for the arithmetic transform."),
            ("comprehension", "Builds the transformed matrix directly."),
        ),
        (
            "Check the in-place index arithmetic on a non-square or 1 x 1 input before "
            "claiming the transform."
        ),
    ),
    _family(
        "Bit Manipulation",
        (
            "single-number number-of-1-bits counting-bits reverse-bits missing-number "
            "sum-of-two-integers reverse-integer"
        ),
        "bit|xor|binary representation",
        "O(1) or O(n)",
        "O(1)",
        "zero|negative numbers if the item allows them|every bit set",
        (("bit_ops", "Uses bit operations directly, which matches this pattern."),),
        (
            "Check the bit width and sign handling; Python integers do not overflow like "
            "fixed-width ones."
        ),
    ),
    _family(
        "Arrays & Hashing",
        (
            "contains-duplicate valid-anagram two-sum group-anagrams top-k-frequent-elements "
            "encode-and-decode-strings product-of-array-except-self valid-sudoku "
            "longest-consecutive-sequence"
        ),
        "hash map|frequency|anagram|duplicate",
        "O(n)",
        "O(n)",
        "empty input|duplicate values|negative numbers",
        (
            (
                "hash_map",
                ("Uses a dict or Counter for O(1) lookups, the hashing tool this pattern expects."),
            ),
            ("set", "Uses a set for O(1) membership, the hashing tool this pattern expects."),
            ("sort", "Sorts when the ordering is the cheaper invariant."),
        ),
        (
            "No hash map or set is visible while the code iterates more than once; this "
            "pattern usually trades space for O(1) lookups."
        ),
        "nested_loop",
    ),
)


GENERAL_PATTERN = _family(
    "General algorithms",
    "",
    "",
    "varies",
    "varies",
    "empty input|a single element|the maximum constraints",
    (("comprehension", "Uses a comprehension to express the transformation directly."),),
)
