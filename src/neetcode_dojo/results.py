"""Small constructors for `assessment.v1` results.

One place decides what an outcome means, so every tool reports the same shape and
none of them has to remember the contract's field names.
"""

from __future__ import annotations

from typing import Any

from neetcode_dojo.protocol import AssessmentResult, OutcomeName, jsonable


def assessment_result(
    outcome: OutcomeName,
    summary: str,
    *,
    score: float | None = None,
    details: dict[str, Any] | None = None,
) -> AssessmentResult:
    return AssessmentResult(
        outcome=outcome,
        score=score,
        summary=summary,
        details=jsonable(details or {}),
    )


def pass_result(
    summary: str,
    *,
    score: float | None = 1.0,
    details: dict[str, Any] | None = None,
) -> AssessmentResult:
    return assessment_result("pass", summary, score=score, details=details)


def fail_result(
    summary: str,
    *,
    score: float | None = 0.0,
    details: dict[str, Any] | None = None,
) -> AssessmentResult:
    return assessment_result("fail", summary, score=score, details=details)


def partial_result(
    summary: str,
    *,
    score: float | None = None,
    details: dict[str, Any] | None = None,
) -> AssessmentResult:
    return assessment_result("partial", summary, score=score, details=details)


def unresolved_result(
    summary: str,
    *,
    details: dict[str, Any] | None = None,
) -> AssessmentResult:
    return assessment_result("unresolved", summary, details=details)


def error_result(
    summary: str,
    *,
    details: dict[str, Any] | None = None,
) -> AssessmentResult:
    return assessment_result("error", summary, details=details)
