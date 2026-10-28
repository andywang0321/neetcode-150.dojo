"""The `assessment.v1` wire contract, as the curriculum's server implements it.

The engine owns the normative models (``dojo/protocol/contracts.py``); this is the
curriculum's executable copy of the same shape, so the evaluator can validate a
request and build a result without importing the engine. The two extra request
shapes — ``variant`` and ``grade`` — extend the standard submission with the
history/evidence those tools need; the engine sends the standard fields, and the
extensions stay optional.
"""

from __future__ import annotations

import math
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

type OutcomeName = Literal["pass", "fail", "partial", "error", "unresolved"]


class ContractModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class SubmissionFile(ContractModel):
    path: str = Field(min_length=1)
    content: str


class AssessmentRequest(ContractModel):
    """One submission snapshot: what the engine sends for every assess tool."""

    contract: Literal["assessment.v1"] = "assessment.v1"
    curriculum: str = Field(min_length=1)
    item: str = Field(min_length=1)
    files: tuple[SubmissionFile, ...]
    claims: dict[str, str] = Field(default_factory=dict)


class EvidenceRow(ContractModel):
    """One evaluator's evidence, as the curriculum's `grade` tool sees it."""

    evaluator: str = Field(min_length=1)
    outcome: OutcomeName
    score: float | None = Field(default=None, ge=0.0, le=1.0)
    summary: str = ""
    details: dict[str, Any] = Field(default_factory=dict)
    assurance: str | None = None


class VariantRequest(AssessmentRequest):
    """A request for a re-solve or re-derived task. `history` is learner-side data."""

    history: tuple[Any, ...] = ()
    mode: Literal["re-solve", "re-derive"] | None = None


class GradeRequest(AssessmentRequest):
    """A request to grade existing evidence against the curriculum's policy."""

    evidence: tuple[EvidenceRow, ...] = ()


class AssessmentResult(ContractModel):
    contract: Literal["assessment.v1"] = "assessment.v1"
    outcome: OutcomeName
    score: float | None = Field(default=None, ge=0.0, le=1.0)
    summary: str
    details: dict[str, Any] = Field(default_factory=dict)


def jsonable(value: Any) -> Any:
    """Turn arbitrary evaluator output into JSON-safe data.

    Evidence crosses the MCP boundary, so a value the student's code returned that
    ``json.dumps`` cannot serialize must not crash the server: it becomes its repr.
    Non-finite floats become their string spelling, and sets are sorted so the same
    submission produces the same evidence twice."""
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else repr(value)
    if isinstance(value, dict):
        return {str(key): jsonable(item) for key, item in value.items()}
    if isinstance(value, (set, frozenset)):
        return sorted((jsonable(item) for item in value), key=repr)
    if isinstance(value, (list, tuple)):
        return [jsonable(item) for item in value]
    return repr(value)
