"""``variant``: a re-solve task spec (default) or fresh small inputs."""

from __future__ import annotations

from typing import Any

from neetcode_dojo.protocol import AssessmentResult, VariantRequest
from neetcode_dojo.results import error_result, pass_result
from neetcode_dojo.toolkit import ToolContext, module_or_error


def variant(context: ToolContext, request: VariantRequest) -> AssessmentResult:
    """Return a task spec for a re-solve, or re-derived inputs with no answers."""
    mode = request.mode or "re-solve"
    spec: dict[str, Any] = {
        "kind": mode,
        "item": request.item,
        "history_entries": len(request.history),
        "reason": (
            "re-solve the same item; the statement and workspace are unchanged"
            if mode == "re-solve"
            else "re-derive fresh small inputs for the same item"
        ),
    }
    details: dict[str, Any] = {"item": request.item, "variant": spec}
    if mode == "re-solve":
        return pass_result(f"re-solve variant for {request.item!r}", details=details)

    module, failure = module_or_error(context.store, request.item)
    if failure is not None:
        return failure
    assert module is not None
    generated = context.store.cases(
        request.item,
        [
            {"n": 2 + index, "seed": f"{request.item}-variant-{index}"}
            for index in range(context.config.variant_inputs)
        ],
        timeout=context.config.assessment_timeout,
    )
    if not generated or not isinstance(generated.value, list):
        reason = generated.error or "the generator failed"
        return error_result(
            f"cannot re-derive inputs for {request.item!r}: {reason}",
            details={"item": request.item},
        )
    inputs: list[dict[str, Any]] = []
    for case in generated.value:
        if not isinstance(case, dict) or "ops" in case:
            continue
        # Args only: the expected answer is the thing a variant must never carry.
        inputs.append({"args": case.get("args") or []})
        if len(inputs) >= context.config.variant_inputs:
            break
    if not inputs:
        return error_result(
            f"the case generator for {request.item!r} produced no re-derivable inputs",
            details={"item": request.item},
        )
    details["inputs"] = inputs
    return pass_result(f"{len(inputs)} re-derived input(s) for {request.item!r}", details=details)
