"""The evaluator facade: validate a request, run one tool, never raise.

The judgement lives in the pure modules (``judge.compare``, ``measure.growth``,
``grading``, ``complexity``); the tool bodies live in ``neetcode_dojo/tools/``; this
module is the small surface the MCP server and the tests hold. Every method takes
the raw ``request`` mapping, validates it against the versioned contract, and turns
any failure — including its own — into ``assessment.v1`` error evidence.
"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from neetcode_dojo.assessment_loader import AssessmentStore
from neetcode_dojo.protocol import (
    AssessmentRequest,
    AssessmentResult,
    GradeRequest,
    VariantRequest,
)
from neetcode_dojo.toolkit import (
    EvaluatorConfig,
    ProbeRunner,
    ToolContext,
    default_run_probe,
    guard,
    validate_request,
)
from neetcode_dojo.tools import assess as assess_tools
from neetcode_dojo.tools import complexity as complexity_tool
from neetcode_dojo.tools import grade as grade_tool
from neetcode_dojo.tools import style as style_tool
from neetcode_dojo.tools import variant as variant_tool

__all__ = ["EvaluatorConfig", "Evaluators", "ProbeRunner"]


class Evaluators:
    """One curriculum's evaluator tools over one assessment store."""

    def __init__(
        self,
        root: Path | str,
        store: AssessmentStore,
        *,
        config: EvaluatorConfig | None = None,
        probe_runner: ProbeRunner | None = None,
    ) -> None:
        self.context = ToolContext(
            root=Path(root).expanduser().resolve(),
            store=store,
            config=config or EvaluatorConfig(),
            probe_runner=probe_runner or default_run_probe,
        )

    @property
    def root(self) -> Path:
        return self.context.root

    @property
    def store(self) -> AssessmentStore:
        return self.context.store

    @property
    def config(self) -> EvaluatorConfig:
        return self.context.config

    @property
    def probe_runner(self) -> ProbeRunner:
        return self.context.probe_runner

    @classmethod
    def from_defaults(
        cls,
        *,
        root: Path | str | None = None,
        assessments: Path | str | None = None,
        config: EvaluatorConfig | None = None,
        probe_runner: ProbeRunner | None = None,
    ) -> Evaluators:
        """The server's production wiring: curriculum root from the cwd, assessments
        from this package's private tree."""
        chosen_root = Path(root) if root is not None else Path.cwd()
        store = (
            AssessmentStore(assessments)
            if assessments is not None
            else AssessmentStore.from_package()
        )
        return cls(chosen_root, store, config=config, probe_runner=probe_runner)

    # ------------------------------------------------------------- assess.tests

    def assess_tests(self, raw: Mapping[str, Any]) -> AssessmentResult:
        """Judge the submission against the item's generated private cases."""
        request, failure = validate_request(AssessmentRequest, raw)
        if failure is not None:
            return failure
        assert request is not None
        return guard(lambda: assess_tools.tests(self.context, request))

    # ------------------------------------------------------------ assess.oracle

    def assess_oracle(self, raw: Mapping[str, Any]) -> AssessmentResult:
        """Cross-check the submission against the item's brute-force oracle."""
        request, failure = validate_request(AssessmentRequest, raw)
        if failure is not None:
            return failure
        assert request is not None
        return guard(lambda: assess_tools.oracle(self.context, request))

    # -------------------------------------------------------- assess.complexity

    def assess_complexity(self, raw: Mapping[str, Any]) -> AssessmentResult:
        """Measure growth against the item's reference over its ladder."""
        request, failure = validate_request(AssessmentRequest, raw)
        if failure is not None:
            return failure
        assert request is not None
        return guard(lambda: complexity_tool.complexity(self.context, request))

    # ------------------------------------------------------------- assess.style

    def assess_style(self, raw: Mapping[str, Any]) -> AssessmentResult:
        """Return advisory static-analysis evidence."""
        request, failure = validate_request(AssessmentRequest, raw)
        if failure is not None:
            return failure
        assert request is not None
        return guard(lambda: style_tool.style(self.context, request))

    # ----------------------------------------------------------------- variant

    def variant(self, raw: Mapping[str, Any]) -> AssessmentResult:
        """Return a re-solve spec (default) or fresh re-derived inputs."""
        request, failure = validate_request(VariantRequest, raw)
        if failure is not None:
            return failure
        assert request is not None
        return guard(lambda: variant_tool.variant(self.context, request))

    # ------------------------------------------------------------------- grade

    def grade(self, raw: Mapping[str, Any]) -> AssessmentResult:
        """Grade supplied evidence and claims 1-4 with a rationale."""
        request, failure = validate_request(GradeRequest, raw)
        if failure is not None:
            return failure
        assert request is not None
        return guard(lambda: grade_tool.grade(self.context, request))
