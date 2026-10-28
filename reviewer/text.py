"""Small text helpers shared by the review fields."""

from collections.abc import Iterable


def dedupe(items: Iterable[str]) -> tuple[str, ...]:
    """Collapse whitespace, drop empties and case-insensitive duplicates."""
    seen: set[str] = set()
    kept: list[str] = []
    for item in items:
        text = " ".join(item.split()).strip()
        key = text.casefold()
        if not text or key in seen:
            continue
        seen.add(key)
        kept.append(text)
    return tuple(kept)


def lower(text: str, limit: int) -> str:
    """Lowercase the first letter, clipping at `limit` characters."""
    clipped = text if len(text) <= limit else f"{text[:limit].rstrip()}..."
    return clipped[:1].lower() + clipped[1:]
