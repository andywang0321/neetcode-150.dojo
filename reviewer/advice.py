"""The deterministic NeetCode review.

This is the default review body and the port of the old reviewer rubric. Each old rubric
dimension becomes a grounded observation: the evidence for correctness, the pattern
family and static facts for approach/style/edge cases, and the claims for complexity
reasoning. It invents nothing: it cites submitted files, evaluator summaries, the
recorded grade and the student's own claims. The review is advisory; the grade is read
but never recomputed.
"""

from reviewer.analysis import Analysis
from reviewer.contracts import ReviewEvidence, ReviewRequest, ReviewResult
from reviewer.findings import (
    claim,
    complexity_evidence,
)
from reviewer.findings import (
    improvements as build_improvements,
)
from reviewer.patterns import Pattern, aligned_strength
from reviewer.text import dedupe, lower

_GRADE_LABELS = {1: "fail", 2: "partial", 3: "pass", 4: "distinction"}
_BASE_QUALITY = {1: 0.20, 2: 0.45, 3: 0.65, 4: 0.80}
_MAX_STRENGTHS = 5
_MAX_STEPS = 4
_MAX_SUMMARY_SENTENCE = 180
_FOCUS = {
    "syntax": "making the submitted file parse",
    "range_len": "the indexed `range(len(...))` loop",
    "print": "the leftover debug output",
    "mutable_default": "the shared mutable default",
    "bare_except": "the bare `except`",
    "broad_except": "the broad exception handler",
    "none_comparison": "the `== None` comparison",
    "global": "the global state",
    "eval": "the use of `eval`/`exec`",
    "long_function": "the overlong function",
    "deep_nesting": "the deeply nested control flow",
    "naming": "the non-snake_case name",
}


def deterministic_review(
    request: ReviewRequest, analysis: Analysis, pattern: Pattern
) -> ReviewResult:
    """Compute the advisory result from the request and the submitted files only."""
    passed = tuple(item for item in request.evidence if item.outcome == "pass")
    not_passed = tuple(item for item in request.evidence if item.outcome != "pass")
    improvements = build_improvements(request, analysis, pattern, not_passed)
    return ReviewResult(
        summary=_summary(request, analysis, pattern, passed, not_passed, improvements),
        strengths=_strengths(request, analysis, pattern, passed),
        improvements=improvements,
        next_steps=_next_steps(request, analysis, pattern, not_passed),
        quality=_quality(request, analysis, pattern, passed),
    )


def _summary(
    request: ReviewRequest,
    analysis: Analysis,
    pattern: Pattern,
    passed: tuple[ReviewEvidence, ...],
    not_passed: tuple[ReviewEvidence, ...],
    improvements: tuple[str, ...],
) -> str:
    grade = (
        "ungraded"
        if request.grade is None
        else f"grade {request.grade} ({_GRADE_LABELS[request.grade]})"
    )
    total = len(request.evidence)
    evidence = (
        f"{len(passed)} of {total} evaluator reports passed"
        if total
        else "no evaluator evidence was recorded"
    )
    opening = f"Review of {request.item} in {request.curriculum}: {grade}; {evidence}."
    if analysis.syntax_errors:
        return (
            f"{opening} The submitted Python does not parse, so the review is "
            "limited to that error."
        )
    if not analysis.files:
        approach = "No submitted Python file was available to analyse."
    else:
        aligned = aligned_strength(analysis.constructs, pattern)
        approach = (
            f"The code reads as {pattern.name} and {lower(aligned[1], _MAX_SUMMARY_SENTENCE)}"
            if aligned is not None
            else f"The code reads as {pattern.name}."
        )
    opportunity = _opportunity(request, analysis, pattern, not_passed, improvements)
    return f"{opening} {approach} {opportunity}"


def _opportunity(
    request: ReviewRequest,
    analysis: Analysis,
    pattern: Pattern,
    not_passed: tuple[ReviewEvidence, ...],
    improvements: tuple[str, ...],
) -> str:
    if not_passed:
        first = not_passed[0]
        detail = f": {first.summary}" if first.summary else ""
        return f"The main opportunity is the {first.evaluator} result{detail}."
    if analysis.issues:
        issue = analysis.issues[0]
        focus = _FOCUS.get(issue.code, "the first static finding")
        return f"The main opportunity is {focus}."
    if improvements:
        return f"The main opportunity: {lower(improvements[0], _MAX_SUMMARY_SENTENCE)}"
    if request.grade is not None and request.grade >= 3:
        return (
            f"No blocking issue is visible; keep the {pattern.name.lower()} reasoning "
            "and the edge cases."
        )
    return "No blocking issue is visible; re-read the statement's constraints before resubmitting."


def _strengths(
    request: ReviewRequest,
    analysis: Analysis,
    pattern: Pattern,
    passed: tuple[ReviewEvidence, ...],
) -> tuple[str, ...]:
    strengths = [_evidence_strength(item) for item in passed]
    aligned = aligned_strength(analysis.constructs, pattern)
    if aligned is not None:
        strengths.append(aligned[1])
    if analysis.guards and analysis.files:
        strengths.append("Includes an explicit guard for empty or short input.")
    if analysis.functions and analysis.type_hints >= 0.5:
        strengths.append("Annotates the function signatures, which makes the contract explicit.")
    if _is_tidy(analysis):
        strengths.append(
            "Keeps functions short and nesting shallow, which makes the trace easy to follow."
        )
    return dedupe(strengths)[:_MAX_STRENGTHS]


def _next_steps(
    request: ReviewRequest,
    analysis: Analysis,
    pattern: Pattern,
    not_passed: tuple[ReviewEvidence, ...],
) -> tuple[str, ...]:
    steps: list[str] = []
    if analysis.syntax_errors:
        steps.append(
            "Fix the syntax error first; the evaluator cannot judge a file that does not parse."
        )
    steps.extend(f"Fix the {item.evaluator} finding and resubmit." for item in not_passed)
    if pattern.edge_cases:
        cases = " and ".join(pattern.edge_cases[:2])
        steps.append(f"Test the usual failure points for {pattern.name}: {cases}.")
    missing = [kind for kind in ("time", "space") if claim(request, kind) is None]
    if missing:
        steps.append(
            f"State the {' and '.join(missing)} complexity and the reason for it; an "
            "unstated claim cannot be checked."
        )
    elif complexity_evidence(request.evidence) is None:
        steps.append(
            "Run the complexity evaluator to check the stated bound against a measured trend."
        )
    if not request.evidence:
        steps.insert(
            0, "Run the item's evaluators before resubmitting; there is nothing to review yet."
        )
    elif request.grade is not None and request.grade >= 3:
        steps.append("Move on to the next item; the recorded grade stands.")
    else:
        steps.append("Resubmit after the fixes; the recorded grade stands.")
    return dedupe(steps)[:_MAX_STEPS]


def _quality(
    request: ReviewRequest,
    analysis: Analysis,
    pattern: Pattern,
    passed: tuple[ReviewEvidence, ...],
) -> float | None:
    if request.grade is None:
        return None
    score = _BASE_QUALITY[request.grade]
    if request.evidence and len(passed) == len(request.evidence):
        score += 0.05
    if aligned_strength(analysis.constructs, pattern) is not None:
        score += 0.04
    if analysis.guards:
        score += 0.03
    if analysis.type_hints >= 0.5:
        score += 0.02
    high = sum(1 for issue in analysis.issues if issue.severity == "high")
    medium = sum(1 for issue in analysis.issues if issue.severity == "medium")
    score -= min(high, 3) * 0.04
    score -= min(medium, 3) * 0.02
    return round(min(1.0, max(0.0, score)), 2)


def _evidence_strength(evidence: ReviewEvidence) -> str:
    detail = f": {evidence.summary}" if evidence.summary else ""
    return f"{evidence.evaluator} passed with {evidence.assurance} assurance{detail}"


def _is_tidy(analysis: Analysis) -> bool:
    functions = analysis.functions
    return bool(functions) and all(
        function.length <= 20 and function.max_nesting <= 2 for function in functions
    )
