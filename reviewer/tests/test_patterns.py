"""The reviewer knows the eighteen NeetCode families and degrades to general advice."""

import pytest

from reviewer.patterns import GENERAL, Pattern, detect_pattern


@pytest.mark.parametrize(
    ("item", "expected"),
    [
        ("two-sum", "Arrays & Hashing"),
        ("two-sum-ii-input-array-is-sorted", "Two Pointers"),
        ("3sum", "Two Pointers"),
        ("longest-substring-without-repeating-characters", "Sliding Window"),
        ("best-time-to-buy-and-sell-stock-with-cooldown", "2-D Dynamic Programming"),
        ("valid-parentheses", "Stack"),
        ("binary-search", "Binary Search"),
        ("reverse-linked-list", "Linked List"),
        ("merge-k-sorted-lists", "Linked List"),
        ("invert-binary-tree", "Trees"),
        ("implement-trie-prefix-tree", "Tries"),
        ("word-search-ii", "Tries"),
        ("kth-largest-element-in-an-array", "Heap / Priority Queue"),
        ("subsets", "Backtracking"),
        ("number-of-islands", "Graphs"),
        ("network-delay-time", "Advanced Graphs"),
        ("climbing-stairs", "1-D Dynamic Programming"),
        ("coin-change", "1-D Dynamic Programming"),
        ("coin-change-ii", "2-D Dynamic Programming"),
        ("regular-expression-matching", "2-D Dynamic Programming"),
        ("jump-game", "Greedy"),
        ("merge-intervals", "Intervals"),
        ("rotate-image", "Math & Geometry"),
        ("single-number", "Bit Manipulation"),
    ],
)
def test_item_slugs_select_the_family(item: str, expected: str) -> None:
    pattern = detect_pattern(item, "Solve the item.", frozenset())

    assert pattern.name == expected


def test_statement_keywords_are_a_fallback_when_the_slug_is_unknown() -> None:
    pattern = detect_pattern("mystery", "Use a sliding window over the string.", frozenset())

    assert pattern.name == "Sliding Window"


@pytest.mark.parametrize(
    ("constructs", "expected"),
    [
        ({"heap"}, "Heap / Priority Queue"),
        ({"memo"}, "1-D Dynamic Programming"),
        ({"dp_table"}, "2-D Dynamic Programming"),
        ({"visited"}, "Graphs"),
        ({"bisect"}, "Binary Search"),
        ({"two_pointer"}, "Two Pointers"),
        ({"hash_map"}, "Arrays & Hashing"),
        ({"set"}, "Arrays & Hashing"),
        ({"bit_ops"}, "Bit Manipulation"),
    ],
)
def test_constructs_are_the_last_resort(constructs: set[str], expected: str) -> None:
    pattern = detect_pattern("mystery", "Implement the function.", frozenset(constructs))

    assert pattern.name == expected


def test_unknown_item_with_no_signal_is_general() -> None:
    pattern = detect_pattern("mystery", "Implement the function.", frozenset())

    assert pattern.name == GENERAL
    assert pattern.expected_time == "varies"
    assert pattern.edge_cases


def test_families_carry_grounded_expectations() -> None:
    arrays = detect_pattern("two-sum", "Find two numbers.", frozenset())
    binary = detect_pattern("binary-search", "Find the target.", frozenset())

    assert arrays.expected_time == "O(n)"
    assert binary.expected_time == "O(log n)"
    assert any(construct == "hash_map" for construct, _ in arrays.strengths)
    assert isinstance(arrays, Pattern)
