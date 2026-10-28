"""Detect the NeetCode family from the item slug, statement or code shape."""

from collections.abc import Iterable

from reviewer.families import GENERAL, GENERAL_PATTERN, PATTERNS, Pattern

__all__ = ["GENERAL", "Pattern", "aligned_strength", "detect_pattern"]


def detect_pattern(item: str, statement: str, constructs: frozenset[str]) -> Pattern:
    """Name the item's NeetCode family from its slug, then its statement, then the code."""
    item_key = item.lower().replace("_", "-")
    best = _longest_match(
        item_key, ((marker, pattern) for pattern in PATTERNS for marker in pattern.markers)
    )
    if best is not None:
        return best
    best = _longest_match(
        statement.lower(),
        ((keyword, pattern) for pattern in PATTERNS for keyword in pattern.keywords),
    )
    if best is not None:
        return best
    return _pattern_from_constructs(constructs)


def aligned_strength(constructs: frozenset[str], pattern: Pattern) -> tuple[str, str] | None:
    """Return the first expected construct the code actually shows, with its strength."""
    for construct, message in pattern.strengths:
        if construct in constructs:
            return construct, message
    return None


def _longest_match(haystack: str, candidates: Iterable[tuple[str, Pattern]]) -> Pattern | None:
    """Prefer the most specific marker: `coin-change-ii` beats `coin-change`."""
    best: Pattern | None = None
    best_length = 0
    for text, pattern in candidates:
        if text in haystack and len(text) > best_length:
            best = pattern
            best_length = len(text)
    return best


def _pattern_from_constructs(constructs: frozenset[str]) -> Pattern:
    if "heap" in constructs:
        return _named("Heap / Priority Queue")
    if "dp_table" in constructs:
        return _named("2-D Dynamic Programming")
    if "memo" in constructs or "dp_array" in constructs:
        return _named("1-D Dynamic Programming")
    if "visited" in constructs or "deque" in constructs:
        return _named("Graphs")
    if "bisect" in constructs or "binary_search_loop" in constructs:
        return _named("Binary Search")
    if "two_pointer" in constructs:
        return _named("Two Pointers")
    if "hash_map" in constructs or "set" in constructs:
        return _named("Arrays & Hashing")
    if "bit_ops" in constructs:
        return _named("Bit Manipulation")
    return GENERAL_PATTERN


def _named(name: str) -> Pattern:
    for pattern in PATTERNS:
        if pattern.name == name:
            return pattern
    return GENERAL_PATTERN
