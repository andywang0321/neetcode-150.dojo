"""The review entry point: static facts -> deterministic advice -> optional model prose.

The deterministic review always runs first. With no model configured it is the answer.
With a model configured, the model writes the prose from the same grounded context and
the rubric keeps the `quality` score; if the model fails, `ReviewUnavailable` becomes a
single `review unavailable:` message in the executor, never a crash and never a partial
review.
"""

from reviewer.advice import deterministic_review
from reviewer.analysis import analyze
from reviewer.contracts import ReviewRequest, ReviewResult
from reviewer.model import ModelReviewer
from reviewer.patterns import detect_pattern
from reviewer.prompt import build_prompt

_MAX_MODEL_STRENGTHS = 5
_MAX_MODEL_IMPROVEMENTS = 6
_MAX_MODEL_STEPS = 4
_MAX_ITEM = 500


class ReviewUnavailable(Exception):
    """The reviewer could not produce a result; the engine stores no review."""


def review(request: ReviewRequest, model: ModelReviewer | None = None) -> ReviewResult:
    """Review one valid request. Raises `ReviewUnavailable` only on a model failure."""
    analysis = analyze(request.files)
    pattern = detect_pattern(request.item, request.statement, analysis.constructs)
    fallback = deterministic_review(request, analysis, pattern)
    if model is None:
        return fallback
    try:
        system, user = build_prompt(request, analysis, pattern)
        primary = model.review(system, user)
    except Exception as error:
        raise ReviewUnavailable(f"the model reviewer failed: {_reason(error)}") from error
    return _merge(primary, fallback)


def _merge(primary: ReviewResult, fallback: ReviewResult) -> ReviewResult:
    """Use the model prose but keep the grounded evidence findings and rubric score."""
    summary = primary.summary.strip() or fallback.summary
    return ReviewResult(
        summary=summary,
        strengths=_combine(primary.strengths, fallback.strengths, _MAX_MODEL_STRENGTHS),
        improvements=_combine(primary.improvements, fallback.improvements, _MAX_MODEL_IMPROVEMENTS),
        next_steps=_combine(primary.next_steps, fallback.next_steps, _MAX_MODEL_STEPS),
        quality=fallback.quality,
    )


def _combine(primary: tuple[str, ...], fallback: tuple[str, ...], limit: int) -> tuple[str, ...]:
    seen: set[str] = set()
    kept: list[str] = []
    for item in (*primary, *fallback):
        text = " ".join(item.split())[:_MAX_ITEM]
        key = text.casefold()
        if not text or key in seen:
            continue
        seen.add(key)
        kept.append(text)
        if len(kept) >= limit:
            break
    return tuple(kept)


def _reason(error: Exception) -> str:
    return str(error) or type(error).__name__
