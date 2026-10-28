"""The wire contracts the NeetCode reviewer speaks.

These are a local mirror of `dojo.protocol.contracts.ReviewRequest` and `ReviewResult`.
The agent must not depend on the engine package, so the JSON shape is the contract and
these models are its executable form on the agent's side of the wire.

Extra fields are rejected on purpose: the request can carry exactly the review view and
nothing else, so a private case, oracle, reference or assessment tree cannot be smuggled
into the reviewer's context by accident.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

type OutcomeName = Literal["pass", "fail", "partial", "error", "unresolved"]


class ContractModel(BaseModel):
    """A strict, immutable wire model."""

    model_config = ConfigDict(extra="forbid", frozen=True)


class SubmissionFile(ContractModel):
    """One submitted file, as the engine snapshotted the workspace."""

    path: str = Field(min_length=1)
    content: str


class ReviewEvidence(ContractModel):
    """One evaluator's report, with the assurance the curriculum declared for it."""

    evaluator: str = Field(min_length=1)
    assurance: str = Field(min_length=1)
    outcome: OutcomeName
    summary: str


class ReviewRequest(ContractModel):
    """The engine -> reviewer request: the review view and nothing hidden."""

    contract: Literal["review.v1"] = "review.v1"
    curriculum: str = Field(min_length=1)
    item: str = Field(min_length=1)
    statement: str
    files: tuple[SubmissionFile, ...]
    evidence: tuple[ReviewEvidence, ...]
    grade: int | None = Field(default=None, ge=1, le=4)
    claims: dict[str, str] = Field(default_factory=dict)


class ReviewResult(ContractModel):
    """The reviewer's advice. Advisory: it never changes a grade.

    `quality` is a float in 0..1, not the old object with a score and a rationale. The
    rationale belongs in `summary` and the findings; the engine stores only this shape.
    """

    summary: str
    strengths: tuple[str, ...] = ()
    improvements: tuple[str, ...] = ()
    next_steps: tuple[str, ...] = ()
    quality: float | None = Field(default=None, ge=0.0, le=1.0)
