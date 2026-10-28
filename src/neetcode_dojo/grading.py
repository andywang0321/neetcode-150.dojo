"""The curriculum's grade policy: evidence in, grade 1-4 and a rationale out.

Pure logic, no IO and no clock. The rules mirror the engine's default evidence
policy and add the one judgement only the curriculum can make:

- any ``error`` or ``unresolved`` evidence leaves the submission ungraded;
- any ``fail`` is grade 1, any ``partial`` is grade 2, all-pass is grade 3;
- **grade 4** is reserved for a clean, fully-passing submission whose claimed
  complexity is corroborated by measured evidence and whose style evidence has no
  advisory flags. Grade 4 is never inferred from passing cases alone: that would
  turn "my code works" into "my work is excellent".

The policy is deterministic: the same evidence and claims always produce the same
grade and the same rationale.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import Any

from neetcode_dojo import complexity
from neetcode_dojo.protocol import EvidenceRow, OutcomeName

#: Claims that can be corroborated mechanically. Other claim names are recorded but
#: cannot earn grade 4.
COMPLEXITY_CLAIMS = ("time", "space")

#: The claimed axes and the evidence details key that carries their measured class.
_MEASURED_KEYS = {"time": "time", "space": "space"}


@dataclass(frozen=True, slots=True)
class Decision:
    grade: int | None
    outcome: OutcomeName
    rationale: str
    notes: list[str] = field(default_factory=list)
    claim_checks: list[dict[str, Any]] = field(default_factory=list)


def decide(rows: Sequence[EvidenceRow], claims: Mapping[str, str]) -> Decision:
    """Grade a submission from its evidence rows and self-reported claims."""
    if not rows:
        return Decision(
            grade=None,
            outcome="unresolved",
            rationale="no evidence was supplied, so the submission is not gradable",
        )

    blocking = [row.evaluator for row in rows if row.outcome in ("error", "unresolved")]
    if blocking:
        names = ", ".join(sorted(set(blocking)))
        return Decision(
            grade=None,
            outcome="unresolved",
            rationale=(
                f"not gradable while evidence from {names} is unresolved: the "
                "curriculum does not grade around missing machine evidence"
            ),
        )

    if any(row.outcome == "fail" for row in rows):
        return Decision(
            grade=1,
            outcome="fail",
            rationale="at least one evaluator failed; the submission is graded 1",
        )
    if any(row.outcome == "partial" for row in rows):
        return Decision(
            grade=2,
            outcome="partial",
            rationale="the evaluators partially passed; the submission is graded 2",
        )

    notes: list[str] = []
    checks = _claim_checks(rows, claims)
    if not claims:
        notes.append("no claims were supplied, so grade 4 is not available")
        return _all_pass(notes, checks)
    if any(isinstance(row.details.get("flags"), list) and row.details["flags"] for row in rows):
        notes.append("style flags are advisory findings, so grade 4 is withheld")
        return _all_pass(notes, checks)
    if any(check["status"] == "disagrees" for check in checks):
        notes.append(
            "a claimed complexity disagrees with the measured class, so grade 4 is withheld"
        )
        return _all_pass(notes, checks)
    complexity_checks = [check for check in checks if check["axis"] in COMPLEXITY_CLAIMS]
    if complexity_checks and all(check["status"] == "agrees" for check in complexity_checks):
        return Decision(
            grade=4,
            outcome="pass",
            rationale=(
                "every evaluator passed and the claimed complexity is "
                "corroborated by measured evidence"
            ),
            notes=notes,
            claim_checks=checks,
        )
    notes.append(
        "the claims are not corroborated by measured evidence, so grade 4 is not available"
    )
    return _all_pass(notes, checks)


def _all_pass(notes: list[str], checks: list[dict[str, Any]]) -> Decision:
    return Decision(
        grade=3,
        outcome="pass",
        rationale="every evaluator passed; the submission is graded 3",
        notes=notes,
        claim_checks=checks,
    )


def _claim_checks(rows: Sequence[EvidenceRow], claims: Mapping[str, str]) -> list[dict[str, Any]]:
    """Compare each complexity claim with the measured class in the evidence.

    A claim with no measured counterpart is recorded as ``unmeasured`` — neither
    corroboration nor contradiction."""
    measured = _measured_classes(rows)
    checks: list[dict[str, Any]] = []
    for axis, claim in claims.items():
        if axis not in COMPLEXITY_CLAIMS:
            checks.append({"axis": axis, "claim": claim, "status": "not-a-complexity-claim"})
            continue
        measured_class = measured.get(axis)
        if measured_class is None:
            checks.append(
                {
                    "axis": axis,
                    "claim": claim,
                    "measured": None,
                    "status": "unmeasured",
                }
            )
            continue
        kind = complexity.compare(claim, measured_class)
        status = {
            complexity.AGREE: "agrees",
            complexity.DISAGREE: "disagrees",
        }.get(kind, "incomparable")
        checks.append(
            {
                "axis": axis,
                "claim": claim,
                "measured": measured_class,
                "status": status,
            }
        )
    return checks


def _measured_classes(rows: Sequence[EvidenceRow]) -> dict[str, str]:
    """The measured class per axis, from an assess.complexity-style details dict."""
    found: dict[str, str] = {}
    for row in rows:
        for axis, key in _MEASURED_KEYS.items():
            verdict = row.details.get(key)
            if not isinstance(verdict, dict):
                continue
            student_class = verdict.get("student_class")
            if isinstance(student_class, str) and student_class:
                found.setdefault(axis, student_class)
    return found
