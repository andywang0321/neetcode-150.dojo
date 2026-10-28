"""The curriculum's stdio MCP server: six evaluator tools behind `assessment.v1`.

dojo starts this server from the manifest's ``[server]`` command and calls one tool
per evaluator. Every tool takes one argument, ``request``, validates it, and returns
an ``assessment.v1`` ``AssessmentResult`` — including for its own failures, which
become ``error`` evidence rather than a crashed server. The engine records the
evaluator's assurance from the manifest, so a tool cannot upgrade its own evidence.

Tool names (mirrored by the manifest's ``[[evaluator]].tool`` declarations):

- ``assess.tests``      — private generated cases, per-case detail
- ``assess.oracle``     — independent brute-force evidence
- ``assess.complexity`` — paired measurement, growth verdict
- ``assess.style``      — advisory radon/ruff findings
- ``variant``           — a re-solve or re-derived task spec
- ``grade``             — grade 1-4 + rationale over supplied evidence

Run it with ``python -m neetcode_dojo.server`` from the curriculum root (the
manifest's command does exactly that).
"""

from __future__ import annotations

from typing import Any

from mcp.server.mcpserver import MCPServer

from neetcode_dojo import __version__
from neetcode_dojo.evaluators import Evaluators
from neetcode_dojo.protocol import AssessmentResult

#: The tool surface the manifest mirrors. A test pins this tuple so a rename cannot
#: silently break enrollment.
TOOL_NAMES: tuple[str, ...] = (
    "assess.tests",
    "assess.oracle",
    "assess.complexity",
    "assess.style",
    "variant",
    "grade",
)

_TOOL_DESCRIPTIONS = {
    "assess.tests": (
        "Judge the submission against the item's private generated cases and return "
        "assessment.v1 evidence with per-case detail."
    ),
    "assess.oracle": (
        "Cross-check the submission against the item's brute-force oracle, "
        "independently of the generator's expected answers."
    ),
    "assess.complexity": (
        "Run the item's paired measurement ladder against its reference and return "
        "the growth verdict as measured evidence."
    ),
    "assess.style": (
        "Run advisory static analysis (radon complexity, ruff) on the submitted Python files."
    ),
    "variant": (
        "Return a task spec for a re-solve (default) or fresh re-derived inputs for the item."
    ),
    "grade": (
        "Grade evidence and claims 1-4 with a rationale, using the curriculum's evidence policy."
    ),
}


def build_server(evaluators: Evaluators | None = None) -> MCPServer:
    """Construct the MCP server around one set of evaluators.

    Tests inject evaluators over fixture assessment/content trees; production uses
    the package's own private assessment tree and the curriculum root as cwd."""
    active = evaluators if evaluators is not None else Evaluators.from_defaults()
    server: MCPServer = MCPServer(
        "neetcode-150",
        version=__version__,
        log_level="WARNING",
    )

    @server.tool(name="assess.tests", description=_TOOL_DESCRIPTIONS["assess.tests"])
    def assess_tests(request: dict[str, Any]) -> AssessmentResult:
        return active.assess_tests(request)

    @server.tool(name="assess.oracle", description=_TOOL_DESCRIPTIONS["assess.oracle"])
    def assess_oracle(request: dict[str, Any]) -> AssessmentResult:
        return active.assess_oracle(request)

    @server.tool(
        name="assess.complexity",
        description=_TOOL_DESCRIPTIONS["assess.complexity"],
    )
    def assess_complexity(request: dict[str, Any]) -> AssessmentResult:
        return active.assess_complexity(request)

    @server.tool(name="assess.style", description=_TOOL_DESCRIPTIONS["assess.style"])
    def assess_style(request: dict[str, Any]) -> AssessmentResult:
        return active.assess_style(request)

    @server.tool(name="variant", description=_TOOL_DESCRIPTIONS["variant"])
    def variant(request: dict[str, Any]) -> AssessmentResult:
        return active.variant(request)

    @server.tool(name="grade", description=_TOOL_DESCRIPTIONS["grade"])
    def grade(request: dict[str, Any]) -> AssessmentResult:
        return active.grade(request)

    return server


def main() -> None:
    """Start the stdio server. This is the manifest's `[server]` entry point."""
    build_server().run()


if __name__ == "__main__":
    main()
