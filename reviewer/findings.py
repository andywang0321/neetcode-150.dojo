"""Grounded improvements: evidence, code findings, claims and the pattern revisit.

Everything here is derived from the request and the static facts. It names a line or an
evaluator summary; it never invents a hidden case, a reference or a measurement.
"""

from reviewer.analysis import Analysis, Issue
from reviewer.contracts import OutcomeName, ReviewEvidence, ReviewRequest
from reviewer.patterns import Pattern, aligned_strength
from reviewer.text import dedupe

_OUTCOME_ADVICE: dict[OutcomeName, str] = {
    "fail": "Fix the failing behaviour and resubmit.",
    "partial": "Finish the partial cases and resubmit.",
    "error": "Rerun the evaluator; an errored result leaves the submission ungraded.",
    "unresolved": "Resolve the open check; it leaves the submission ungraded.",
}
_MAX_IMPROVEMENTS = 6


def improvements(
    request: ReviewRequest,
    analysis: Analysis,
    pattern: Pattern,
    not_passed: tuple[ReviewEvidence, ...],
) -> tuple[str, ...]:
    """Order improvements: evidence first, then claims, code, pattern and guards."""
    items: list[str] = []
    if not analysis.files:
        items.append(
            "No submitted Python file was available, so the review is limited to the "
            "evidence and claims."
        )
    items.extend(evidence_improvement(item) for item in not_passed)
    items.extend(claim_improvements(request, analysis, pattern))
    items.extend(f"{issue.path}:{issue.line}: {issue.message}" for issue in analysis.issues)
    revisit = pattern_revisit(analysis, pattern, request.grade)
    if revisit is not None:
        items.append(revisit)
    if analysis.functions and not analysis.guards and request.grade != 4:
        items.append(
            "No explicit empty/short-input guard is visible; add one or show why the "
            "constraints make it unnecessary."
        )
    if not request.evidence:
        items.append("No evaluator evidence was recorded, so correctness cannot be reviewed.")
    return dedupe(items)[:_MAX_IMPROVEMENTS]


def claim_improvements(
    request: ReviewRequest, analysis: Analysis, pattern: Pattern
) -> tuple[str, ...]:
    """Flag a claim that the evidence or the static shape contradicts."""
    claimed = claim(request, "time")
    if claimed is None:
        return ()
    evidence = complexity_evidence(request.evidence)
    if evidence is not None and evidence.outcome != "pass":
        return (
            f"The stated time complexity {claimed} is not corroborated by the "
            f"{evidence.evaluator} evidence: {evidence.summary}",
        )
    if (
        "nested_loop" in analysis.constructs
        and pattern.expected_time in {"O(n)", "O(log n)"}
        and claims_linear(claimed)
    ):
        issue = first_nested(analysis)
        where = f" at {issue.path}:{issue.line}" if issue is not None else ""
        return (
            f"The static shape shows nested iteration{where} while the claim is {claimed}; "
            "verify the bound or make the claim precise.",
        )
    return ()


def claim(request: ReviewRequest, kind: str) -> str | None:
    """Read a time/space claim under the usual key spellings."""
    aliases = {
        "time": {"time", "time_complexity", "complexity_time", "big_o_time"},
        "space": {"space", "space_complexity", "complexity_space", "big_o_space"},
    }[kind]
    for key, value in request.claims.items():
        normalized = key.strip().lower().replace(" ", "_").replace("-", "_")
        if normalized in aliases and value.strip():
            return value.strip()
    return None


def complexity_evidence(evidence: tuple[ReviewEvidence, ...]) -> ReviewEvidence | None:
    """The first evaluator that appears to measure complexity."""
    for item in evidence:
        name = item.evaluator.lower()
        if any(marker in name for marker in ("complex", "measure", "profile")):
            return item
    return None


def evidence_improvement(evidence: ReviewEvidence) -> str:
    detail = f": {evidence.summary}" if evidence.summary else ""
    advice = _OUTCOME_ADVICE[evidence.outcome]
    return f"{evidence.evaluator} reported {evidence.outcome}{detail}. {advice}"


def pattern_revisit(analysis: Analysis, pattern: Pattern, grade: int | None) -> str | None:
    """Ask the student to confirm the family's expected tool, when it is not visible."""
    if pattern.revisit is None or grade == 4 or not analysis.files:
        return None
    if aligned_strength(analysis.constructs, pattern) is not None:
        return None
    if pattern.revisit_if and not any(item in analysis.constructs for item in pattern.revisit_if):
        return None
    return pattern.revisit


def claims_linear(claim_text: str) -> bool:
    text = claim_text.lower().replace(" ", "")
    if any(marker in text for marker in ("^2", "**2", "n2", "n²", "mn", "n*m", "nlog")):
        return False
    return "o(n)" in text or "o(logn)" in text


def first_nested(analysis: Analysis) -> Issue | None:
    for issue in analysis.issues:
        if issue.code in {"nested_loop", "range_len"}:
            return issue
    return None
