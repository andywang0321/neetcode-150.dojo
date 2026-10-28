"""``assess.style``: advisory radon complexity and ruff findings.

Never a verdict: its findings are flags for the reviewer and the learner. The tool
therefore returns ``pass`` with the findings in ``details``, whatever they are.
"""

from __future__ import annotations

from typing import Any

from neetcode_dojo import static
from neetcode_dojo.protocol import AssessmentRequest, AssessmentResult
from neetcode_dojo.results import error_result, pass_result
from neetcode_dojo.submission import analyze_files, materialized
from neetcode_dojo.toolkit import ToolContext


def style(context: ToolContext, request: AssessmentRequest) -> AssessmentResult:
    """Run advisory static analysis on the submitted Python files."""
    paths = analyze_files(request.files)
    if not paths:
        return error_result(
            f"the submission for {request.item!r} has no Python files to analyze",
            details={"item": request.item},
        )
    reports: list[dict[str, Any]] = []
    flags: list[str] = []
    with materialized(request.files) as root:
        for relative in paths:
            report = static.analyze(
                root / relative,
                ruff_timeout=context.config.style_timeout,
            )
            reports.append({"path": relative, **report.to_dict(), "flags": report.flags})
            flags.extend(f"{relative}: {flag}" for flag in report.flags)
    summary = "no advisory style flags" if not flags else f"{len(flags)} advisory style flag(s)"
    return pass_result(
        summary,
        score=None,
        details={"item": request.item, "files": reports, "flags": flags},
    )
