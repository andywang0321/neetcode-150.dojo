"""``assess.complexity``: the paired measurement over the item's ladder."""

from __future__ import annotations

import random
from typing import Any

from neetcode_dojo.measure import growth
from neetcode_dojo.measure.probe import Target
from neetcode_dojo.protocol import AssessmentRequest, AssessmentResult
from neetcode_dojo.results import (
    error_result,
    fail_result,
    partial_result,
    pass_result,
    unresolved_result,
)
from neetcode_dojo.submission import materialized
from neetcode_dojo.toolkit import (
    ToolContext,
    declared_class,
    entry_or_error,
    module_or_error,
    plan_sizes,
    verdict_details,
)


def complexity(context: ToolContext, request: AssessmentRequest) -> AssessmentResult:
    """Measure the submission against the item's reference over the ladder."""
    module, failure = module_or_error(context.store, request.item)
    if failure is not None:
        return failure
    assert module is not None
    plan = context.store.plan(request.item)
    if not plan or plan.get("axis") is None:
        return unresolved_result(
            f"this item declares no measurement plan (not measured): {request.item!r}",
            details={"item": request.item, "plan": plan},
        )
    sizes = plan_sizes(plan)
    if sizes is None:
        return error_result(
            f"the measurement plan for {request.item!r} has no usable sizes",
            details={"item": request.item, "plan": plan},
        )
    entry, failure = entry_or_error(context, request)
    if failure is not None:
        return failure
    assert entry is not None

    compare = str(plan.get("compare", "strict"))
    probe_compare = "strict" if compare == "none" else compare
    reference = (
        context.store.reference_target(request.item)
        if plan.get("baseline") == "reference"
        else None
    )
    inputs = context.store.inputs_many(
        request.item,
        [{"n": n, "seed": f"{request.item}-{n}"} for n in sizes],
        timeout=context.config.assessment_timeout,
    )
    if not inputs:
        return error_result(
            f"the measurement inputs for {request.item!r} could not be built: {inputs.error}",
            details={"item": request.item, "error": inputs.error},
        )
    built = inputs.value
    if not isinstance(built, list) or len(built) != len(sizes):
        return error_result(
            f"the measurement inputs for {request.item!r} returned an unexpected payload",
            details={"item": request.item},
        )
    by_size = dict(zip(sizes, built, strict=True))

    def generator(n: int, _rng: random.Random) -> list[Any]:
        args = by_size.get(n)
        if args is None:
            raise KeyError(f"no measurement input was built for n={n}")
        return args

    with materialized(request.files) as root:
        student = Target("yours", root / entry.code_file, entry.function)
        probe = context.probe_runner(
            student,
            generator,
            reference,
            sizes=sizes,
            repeats=context.config.probe_repeats,
            timeout=context.config.probe_timeout,
            compare=probe_compare,
        )

    declared_time = declared_class(plan, "time")
    declared_space = declared_class(plan, "space")
    failure_point = probe.first_failure()
    reference_failure = probe.reference_failure()
    mismatch = probe.first_mismatch() if compare != "none" else None
    time_verdict = growth.verdict(
        probe.time_ratios,
        declared_class=declared_time,
        has_reference=probe.has_reference,
        failure=failure_point.student.error if failure_point else None,
        failed_at=failure_point.n if failure_point else None,
    )
    space_verdict = growth.verdict(
        probe.space_ratios,
        declared_class=declared_space,
        has_reference=probe.has_reference,
    )
    details: dict[str, Any] = {
        "item": request.item,
        "plan": plan,
        "declared_time": declared_time,
        "declared_space": declared_space,
        "reference_used": probe.has_reference,
        "time": verdict_details(time_verdict),
        "space": verdict_details(space_verdict),
        "failure": failure_point.student.error if failure_point else None,
        "failed_at": failure_point.n if failure_point else None,
        "mismatch_at": mismatch.n if mismatch else None,
        "reference_failed_at": reference_failure.n if reference_failure else None,
        "reference_failure": (
            reference_failure.reference.error
            if reference_failure and reference_failure.reference
            else None
        ),
        "points": [
            {
                "n": point.n,
                "student_ms": point.student.ms,
                "reference_ms": point.reference.ms if point.reference else None,
                "ratio": point.time_ratio,
                "space_ratio": point.space_ratio,
                "error": point.student.error,
                "spread": round(point.spread, 4),
            }
            for point in probe.points
        ],
        "claim": request.claims.get("time"),
    }
    summary = f"time {time_verdict.label} ({time_verdict.trend_label}); space {space_verdict.label}"
    if failure_point is not None:
        return fail_result(
            f"the submission failed at n={failure_point.n}: {failure_point.student.error}",
            score=0.0,
            details=details,
        )
    if not probe.has_reference:
        return unresolved_result(
            "no reference solution was available to compare growth against",
            details=details,
        )
    if time_verdict.kind in (growth.MATCHES, growth.BETTER):
        if space_verdict.kind == growth.WORSE:
            return partial_result(
                f"{summary}; the space growth is worse than the reference",
                score=0.5,
                details=details,
            )
        return pass_result(summary, score=1.0, details=details)
    if time_verdict.kind == growth.WORSE:
        return fail_result(summary, score=0.0, details=details)
    return unresolved_result(f"{summary}; {time_verdict.note}", details=details)
