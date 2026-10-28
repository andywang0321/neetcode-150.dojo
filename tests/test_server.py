"""The MCP surface: exact tool names/schemas and structured `assessment.v1` results.

The server is exercised in-process through the SDK's own client, so the tests cover
the real tool registration and result conversion without a network or a subprocess —
except the last test, which starts the actual `python -m neetcode_dojo.server` stdio
command the manifest will declare.
"""

from __future__ import annotations

import asyncio
import importlib
import os
import sys
from pathlib import Path
from typing import Any

from mcp import Client

from neetcode_dojo.evaluators import Evaluators
from neetcode_dojo.protocol import AssessmentResult
from neetcode_dojo.server import TOOL_NAMES, build_server
from tests.support import request_for

# `mcp.client.stdio` binds `sys.stderr` as a default argument when it is imported.
# Bind it here, with the interpreter's real stderr installed, so pytest's capture
# cannot replace (and later close) the stream a spawned server inherits.
_SAVED_STDERR = sys.stderr
sys.stderr = sys.__stderr__ or sys.stderr
try:
    importlib.import_module("mcp.client.stdio")
finally:
    sys.stderr = _SAVED_STDERR


def _run(coroutine: Any) -> Any:
    return asyncio.run(coroutine)


def test_the_six_declared_tools_exist_with_a_request_and_an_output_schema(
    evaluators: Evaluators,
) -> None:
    server = build_server(evaluators)

    async def scenario() -> Any:
        async with Client(server) as client:
            return await client.list_tools()

    listing = _run(scenario())
    names = {tool.name for tool in listing.tools}
    assert names == set(TOOL_NAMES)
    for tool in listing.tools:
        assert tool.input_schema["type"] == "object"
        assert "request" in tool.input_schema["properties"]
        assert tool.output_schema is not None
        assert "outcome" in tool.output_schema["properties"]


def test_every_tool_returns_a_structured_assessment_result(
    evaluators: Evaluators,
) -> None:
    requests = {
        "assess.tests": request_for("valid_parentheses"),
        "assess.oracle": request_for("valid_parentheses"),
        "assess.complexity": request_for("min_stack"),
        "assess.style": request_for("valid_parentheses"),
        "variant": request_for("valid_parentheses"),
        "grade": request_for(
            "valid_parentheses",
            evidence=[{"evaluator": "tests", "outcome": "pass", "summary": "6/6"}],
        ),
    }

    async def scenario() -> dict[str, Any]:
        results: dict[str, Any] = {}
        async with Client(build_server(evaluators)) as client:
            for tool_name, request in requests.items():
                results[tool_name] = await client.call_tool(tool_name, {"request": request})
        return results

    results = _run(scenario())
    for tool_name, call in results.items():
        assert call.is_error is False, tool_name
        assert call.structured_content is not None, tool_name
        result = AssessmentResult.model_validate(call.structured_content)
        assert result.contract == "assessment.v1"
        assert result.summary


def test_an_invalid_request_is_an_error_result_not_a_crashed_server(
    evaluators: Evaluators,
) -> None:
    async def scenario() -> Any:
        async with Client(build_server(evaluators)) as client:
            return await client.call_tool("assess.tests", {"request": {"item": "x"}})

    call = _run(scenario())
    assert call.is_error is False
    result = AssessmentResult.model_validate(call.structured_content)
    assert result.outcome == "error"
    assert "invalid assessment request" in result.summary


def test_an_unknown_tool_is_refused_by_the_sdk(evaluators: Evaluators) -> None:
    async def scenario() -> Any:
        async with Client(build_server(evaluators)) as client:
            return await client.call_tool("assess.nope", {"request": {}})

    call = _run(scenario())
    assert call.is_error is True


def test_the_stdio_server_starts_and_lists_its_tools(tmp_path: Path) -> None:
    """The manifest runs `python -m neetcode_dojo.server` with the curriculum root as
    cwd. The server must start, handshake, and expose the declared tools there."""
    from mcp.client.stdio import StdioServerParameters

    home = tmp_path / "home"
    home.mkdir()
    environment = {
        "PATH": os.environ.get("PATH", ""),
        "HOME": str(home),
    }
    parameters = StdioServerParameters(
        command=sys.executable,
        args=["-m", "neetcode_dojo.server"],
        cwd=tmp_path,
        env=environment,
    )

    async def scenario() -> Any:
        async with Client(parameters, read_timeout_seconds=30.0) as client:
            listing = await client.list_tools()
            # The merged curriculum has a real assessment module for this item,
            # so the server must return a real result. A missing module is an
            # error *result* and is covered by the evaluator unit tests.
            call = await client.call_tool(
                "assess.tests", {"request": request_for("valid_parentheses")}
            )
            return listing, call

    listing, call = _run(scenario())
    assert {tool.name for tool in listing.tools} == set(TOOL_NAMES)
    result = AssessmentResult.model_validate(call.structured_content)
    assert result.outcome == "pass"
