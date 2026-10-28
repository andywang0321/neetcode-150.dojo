"""``assess.tests`` and ``assess.oracle``: executable correctness evidence."""

from __future__ import annotations

from typing import Any

from neetcode_dojo.judge.compare import check_equal
from neetcode_dojo.protocol import AssessmentRequest, AssessmentResult
from neetcode_dojo.results import (
    assessment_result,
    error_result,
    unresolved_result,
)
from neetcode_dojo.toolkit import (
    ToolContext,
    entry_or_error,
    generated_cases,
    judge_in_submission,
    judge_result,
    module_or_error,
)


def tests(context: ToolContext, request: AssessmentRequest) -> AssessmentResult:
    """Judge the submission against the item's generated private cases."""
    module, failure = module_or_error(context.store, request.item)
    if failure is not None:
        return failure
    assert module is not None
    entry, failure = entry_or_error(context, request)
    if failure is not None:
        return failure
    assert entry is not None
    cases, failure = generated_cases(context.store, request.item, module, context.config)
    if failure is not None:
        return failure
    assert cases is not None
    report = judge_in_submission(context, request, entry, cases)
    return judge_result(context.config, request.item, cases, report, source="tests")


def oracle(context: ToolContext, request: AssessmentRequest) -> AssessmentResult:
    """Judge the submission against the item's brute-force oracle, independently of
    the generator's expected answers."""
    module, failure = module_or_error(context.store, request.item)
    if failure is not None:
        return failure
    assert module is not None
    if not module.has("oracle", request.item):
        return unresolved_result(
            f"no oracle is registered for {request.item!r}; the tests evaluator "
            "decides the private cases",
            details={"item": request.item, "kind": "oracle"},
        )
    entry, failure = entry_or_error(context, request)
    if failure is not None:
        return failure
    assert entry is not None
    cases, failure = generated_cases(context.store, request.item, module, context.config)
    if failure is not None:
        return failure
    assert cases is not None

    calls = _oracle_calls(cases)
    if not calls:
        return unresolved_result(
            f"every case for {request.item!r} is predicate-decided; the tests "
            "evaluator decides them",
            details={"item": request.item},
        )
    result = context.store.oracle_many(
        request.item, calls, timeout=context.config.assessment_timeout
    )
    if not result:
        return error_result(
            f"the oracle for {request.item!r} could not run: {result.error}",
            details={"item": request.item, "error": result.error},
        )
    values = result.value
    if not isinstance(values, list) or len(values) != len(calls):
        return error_result(
            f"the oracle for {request.item!r} returned an unexpected payload",
            details={"item": request.item},
        )

    effective, oracle_errors, disagreements = _oracle_verdicts(cases, values)
    if not effective:
        return error_result(
            f"the oracle for {request.item!r} produced no usable case result",
            details={"item": request.item, "oracle_errors": oracle_errors},
        )
    report = judge_in_submission(context, request, entry, effective)
    result = judge_result(context.config, request.item, effective, report, source="oracle")
    details = dict(result.details)
    details["oracle_errors"] = oracle_errors
    details["oracle_disagreements"] = disagreements
    if disagreements:
        return unresolved_result(
            f"the oracle and the private cases disagree on {len(disagreements)} "
            f"case(s) for {request.item!r}; the item is not decidable until that is "
            "fixed",
            details=details,
        )
    summary = result.summary
    if oracle_errors:
        summary = f"{summary}; the oracle could not run for {len(oracle_errors)} case(s)"
    return assessment_result(result.outcome, summary, score=result.score, details=details)


def _oracle_calls(cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """The oracle calls for the non-predicate cases, in case order."""
    calls: list[dict[str, Any]] = []
    for case in cases:
        if case.get("predicate"):
            continue
        calls.append(
            {"args": [], "ops": case["ops"]} if "ops" in case else {"args": case.get("args") or []}
        )
    return calls


def _oracle_verdicts(
    cases: list[dict[str, Any]],
    values: list[Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Rebuild the case list with oracle-derived expectations.

    Returns the effective cases (predicate cases untouched, failed oracle cases
    omitted), the per-case oracle errors, and the cases where the oracle disagrees
    with the generator's expected answer."""
    effective: list[dict[str, Any]] = []
    oracle_errors: list[dict[str, Any]] = []
    disagreements: list[dict[str, Any]] = []
    value_index = 0
    for case in cases:
        if case.get("predicate"):
            effective.append(case)
            continue
        value = values[value_index]
        value_index += 1
        if not isinstance(value, dict) or not value.get("ok"):
            oracle_errors.append(
                {
                    "label": case.get("label"),
                    "error": (value.get("error") if isinstance(value, dict) else None)
                    or "the oracle failed",
                }
            )
            continue
        expected = (
            value.get("mutated_args") if case.get("compare") == "mutates" else value.get("value")
        )
        effective.append({**case, "expected": expected})
        agreement_mode = (
            "strict" if case.get("compare") == "mutates" else str(case.get("compare", "strict"))
        )
        if "expected" in case and not check_equal(expected, case.get("expected"), agreement_mode):
            disagreements.append(
                {
                    "label": case.get("label"),
                    "case_expected": case.get("expected"),
                    "oracle_expected": expected,
                }
            )
    return effective, oracle_errors, disagreements
