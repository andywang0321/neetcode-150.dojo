"""``grade``: the curriculum's evidence policy as an assessment.v1 tool."""

from __future__ import annotations

from typing import Any

from neetcode_dojo import grading
from neetcode_dojo.protocol import AssessmentResult, GradeRequest
from neetcode_dojo.results import assessment_result, unresolved_result
from neetcode_dojo.toolkit import ToolContext


def grade(_context: ToolContext, request: GradeRequest) -> AssessmentResult:
    """Turn supplied evidence and claims into a grade 1-4 with a rationale."""
    decision = grading.decide(request.evidence, request.claims)
    details: dict[str, Any] = {
        "item": request.item,
        "grade": decision.grade,
        "rationale": decision.rationale,
        "notes": decision.notes,
        "claim_checks": decision.claim_checks,
        "evidence": [row.model_dump(mode="json") for row in request.evidence],
    }
    if decision.grade is None:
        return unresolved_result(f"not gradable: {decision.rationale}", details=details)
    return assessment_result(
        decision.outcome,
        f"grade {decision.grade}: {decision.rationale}",
        score=decision.grade / 4,
        details=details,
    )
