"""Shared machinery for the evaluator tools: context, validation, error mapping.

The tools themselves live in ``neetcode_dojo/tools/``; this module holds what they
all need and nothing that decides an item. It is the imperative shell's common
edge: a typed request is validated here, a bounded child's report is shaped here,
and an unexpected failure becomes ``error`` evidence here.
"""

from __future__ import annotations

import random
from collections.abc import Callable, Mapping, Sequence
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Protocol

from pydantic import BaseModel, ValidationError

from neetcode_dojo.assessment_loader import (
    DEFAULT_RUN_TIMEOUT,
    AssessmentStore,
    ModuleReport,
)
from neetcode_dojo.judge.runner import Checker, JudgeReport, run_cases_in
from neetcode_dojo.measure import growth
from neetcode_dojo.measure.probe import Probe, Target
from neetcode_dojo.measure.probe import run_probe as default_run_probe
from neetcode_dojo.protocol import AssessmentRequest, AssessmentResult
from neetcode_dojo.results import (
    error_result,
    fail_result,
    partial_result,
    pass_result,
)
from neetcode_dojo.submission import (
    EntryPoint,
    SubmissionError,
    materialized,
    resolve_entry,
)

#: How many private cases the tests/oracle tools generate. Each case is one
#: deterministic `(n, seed)` request; the generator itself decides the shape.
DEFAULT_CASE_COUNT = 26

#: Case sizes cycle through the old engine's 0..12 window.
CASE_SIZE_WINDOW = 13


class ProbeRunner(Protocol):
    """The measurement seam: the real paired profiler, or a synthetic one in tests."""

    def __call__(
        self,
        student: Target,
        generator: Callable[[int, random.Random], list[Any]],
        reference: Target | None = None,
        *,
        sizes: list[int],
        repeats: int,
        timeout: float,
        compare: str,
    ) -> Probe: ...


@dataclass(frozen=True, slots=True)
class EvaluatorConfig:
    """Timeouts and sizes a server process uses. Tests shrink these."""

    case_count: int = DEFAULT_CASE_COUNT
    judge_timeout: float = 10.0
    assessment_timeout: float = DEFAULT_RUN_TIMEOUT
    probe_repeats: int = 3
    probe_timeout: float = 20.0
    style_timeout: float = 60.0
    variant_inputs: int = 3


@dataclass(frozen=True, slots=True)
class ToolContext:
    """Everything a tool needs, injected once by the server or a test."""

    root: Path
    store: AssessmentStore
    config: EvaluatorConfig
    probe_runner: ProbeRunner = default_run_probe


def validate_request[Model: BaseModel](
    model: type[Model], raw: Mapping[str, Any]
) -> tuple[Model | None, AssessmentResult | None]:
    """Parse one tool request, returning error evidence instead of raising."""
    if not isinstance(raw, Mapping):
        return None, error_result("invalid assessment request: expected an object under `request`")
    try:
        return model.model_validate(dict(raw)), None
    except ValidationError as exc:
        problems = [
            {
                "loc": list(error.get("loc", ())),
                "msg": error.get("msg", "invalid value"),
                "type": error.get("type", "value_error"),
            }
            for error in exc.errors(include_url=False)
        ]
        return None, error_result(
            "invalid assessment request: " + _describe(problems),
            details={"error": problems},
        )


def _describe(problems: Sequence[Mapping[str, Any]]) -> str:
    parts = []
    for problem in problems[:3]:
        location = ".".join(str(part) for part in problem.get("loc", ())) or "request"
        parts.append(f"{location}: {problem.get('msg')}")
    if len(problems) > 3:
        parts.append(f"and {len(problems) - 3} more")
    return "; ".join(parts)


def guard(operation: Callable[[], AssessmentResult]) -> AssessmentResult:
    """Run a tool body; any failure becomes error evidence, never a crash."""
    try:
        return operation()
    except SubmissionError as exc:
        return error_result(f"invalid submission: {exc}", details={"error": str(exc)})
    except Exception as exc:  # a tool failure is evidence, not a crash
        return error_result(
            f"the evaluator failed: {type(exc).__name__}: {exc}",
            details={"error": f"{type(exc).__name__}: {exc}"},
        )


def module_or_error(
    store: AssessmentStore, item: str
) -> tuple[ModuleReport | None, AssessmentResult | None]:
    report = store.report(item)
    if report is None:
        return None, error_result(
            f"unknown item {item!r}: no private assessment module ({item}.py) exists "
            "under the assessment tree",
            details={"item": item, "kind": "assessment-module"},
        )
    if report.error:
        return None, error_result(
            f"the assessment module for {item!r} does not load: {report.error}",
            details={"item": item, "error": report.error},
        )
    return report, None


def entry_or_error(
    context: ToolContext, request: AssessmentRequest
) -> tuple[EntryPoint | None, AssessmentResult | None]:
    entry = resolve_entry(request.files, root=context.root, item=request.item)
    if entry is None:
        return None, error_result(
            f"cannot resolve the entry point for {request.item!r}: add "
            f"content/{request.item}/workspace/solution.py (the first top-level "
            "def/class names the entry point), or make solution.py define it",
            details={"item": request.item, "kind": "entry-point"},
        )
    return entry, None


def generated_cases(
    store: AssessmentStore,
    item: str,
    module: ModuleReport,
    config: EvaluatorConfig,
) -> tuple[list[dict[str, Any]] | None, AssessmentResult | None]:
    """Generate the item's private cases, deterministically, in a bounded child."""
    if not module.has("cases", item):
        return None, error_result(
            f"the assessment module for {item!r} registers no @cases generator",
            details={"item": item, "registrations": module.registrations},
        )
    generated = store.cases(
        item,
        case_requests(item, config.case_count),
        timeout=config.assessment_timeout,
    )
    if not generated:
        return None, error_result(
            f"the private case generator for {item!r} failed: {generated.error}",
            details={"item": item, "error": generated.error},
        )
    if not isinstance(generated.value, list) or not generated.value:
        return None, error_result(
            f"the private case generator for {item!r} produced no cases",
            details={"item": item},
        )
    cases: list[dict[str, Any]] = []
    for index, case in enumerate(generated.value):
        if not isinstance(case, dict) or ("args" not in case and "ops" not in case):
            return None, error_result(
                f"the private case generator for {item!r} produced a malformed case",
                details={"item": item, "case": case},
            )
        cases.append({**case, "label": f"generated {index + 1}"})
    return cases, None


def checker_for(context: ToolContext, item: str, entry: EntryPoint, root: Path) -> Checker:
    """A judge checker that runs the item's predicate in the assessment child."""

    def check(name: str, got: Any, args: Any) -> bool:
        return context.store.check_predicate(
            item,
            name,
            got,
            args,
            code_file=entry.code_file,
            cwd=root,
            timeout=context.config.assessment_timeout,
        )

    return check


def judge_in_submission(
    context: ToolContext,
    request: AssessmentRequest,
    entry: EntryPoint,
    cases: Sequence[Mapping[str, Any]],
) -> JudgeReport:
    """Materialize the snapshot and run the bounded judge against it."""
    with materialized(request.files) as root:
        return run_cases_in(
            root,
            entry.code_file,
            entry.function,
            cases,
            timeout=context.config.judge_timeout,
            checker=checker_for(context, request.item, entry, root),
        )


def judge_result(
    config: EvaluatorConfig,
    item: str,
    cases: Sequence[Mapping[str, Any]],
    report: JudgeReport,
    *,
    source: str,
) -> AssessmentResult:
    """Map a judge report onto the assessment.v1 outcome vocabulary."""
    details = case_details(item, cases, report, source=source)
    passed, total = report.passed, report.total
    if report.status == "correct":
        return _pass(passed, total, details)
    if report.status == "timed_out":
        return _timeout(config, details)
    if report.status == "error":
        first = next((result.error for result in report.results if result.error), None)
        return _error(passed, total, first, details)
    if 0 < passed < total:
        return _partial(passed, total, details)
    return _fail(total, details)


def case_details(
    item: str,
    cases: Sequence[Mapping[str, Any]],
    report: JudgeReport,
    *,
    source: str,
) -> dict[str, Any]:
    aligned = len(report.results) == len(cases)
    rendered: list[dict[str, Any]] = []
    for index, result in enumerate(report.results):
        entry: dict[str, Any] = {
            "label": result.label,
            "ok": result.passed,
            "expected": result.expected,
            "got": result.got,
            "error": result.error,
            "elapsed_ms": round(result.elapsed_ms, 3),
        }
        if aligned:
            case = cases[index]
            if "args" in case:
                entry["args"] = case["args"]
            if "ops" in case:
                entry["ops"] = case["ops"]
        if result.printed:
            entry["printed"] = result.printed[:2000]
        rendered.append(entry)
    return {
        "item": item,
        "source": source,
        "status": report.status,
        "passed": report.passed,
        "total": report.total,
        "cases": rendered,
    }


def case_requests(item: str, count: int) -> list[dict[str, Any]]:
    """Deterministic case requests: same item, same cases, every submission."""
    return [
        {"n": index % CASE_SIZE_WINDOW, "seed": f"{item}-{index}"} for index in range(max(1, count))
    ]


def plan_sizes(plan: Mapping[str, Any]) -> list[int] | None:
    from neetcode_dojo.measure.probe import ladder

    raw = plan.get("sizes")
    if raw is None:
        return ladder()
    if not isinstance(raw, list) or not raw:
        return None
    sizes: list[int] = []
    for value in raw:
        if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
            return None
        sizes.append(value)
    return sizes


def declared_class(plan: Mapping[str, Any], axis: str) -> str | None:
    for key in (f"declared_{axis}", f"expected_{axis}"):
        value = plan.get(key)
        if isinstance(value, str) and value:
            return value
    return None


def verdict_details(verdict: growth.Verdict) -> dict[str, Any]:
    return {
        **asdict(verdict),
        "label": verdict.label,
        "trend_label": verdict.trend_label,
        "resolved": verdict.resolved,
    }


def _pass(passed: int, total: int, details: dict[str, Any]) -> AssessmentResult:
    return pass_result(f"{passed}/{total} private cases passed", score=1.0, details=details)


def _timeout(config: EvaluatorConfig, details: dict[str, Any]) -> AssessmentResult:
    return error_result(
        f"the private cases timed out after {config.judge_timeout:g}s",
        details=details,
    )


def _error(passed: int, total: int, first: str | None, details: dict[str, Any]) -> AssessmentResult:
    return error_result(
        f"{passed}/{total} private cases passed; a case raised: {(first or 'unknown error')[:240]}",
        details=details,
    )


def _partial(passed: int, total: int, details: dict[str, Any]) -> AssessmentResult:
    return partial_result(
        f"{passed}/{total} private cases passed",
        score=passed / total if total else None,
        details=details,
    )


def _fail(total: int, details: dict[str, Any]) -> AssessmentResult:
    return fail_result(f"0/{total} private cases passed", score=0.0, details=details)
