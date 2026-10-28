"""Shared paths, submissions and request builders for the evaluator-core tests.

Everything here is offline and deterministic: fixture assessment modules register
through the curriculum-local registry, fixture content supplies workspace templates,
and no test reads the old engine or the real home directory.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from neetcode_dojo.assessment_loader import AssessmentStore
from neetcode_dojo.evaluators import EvaluatorConfig, Evaluators
from neetcode_dojo.measure.probe import Probe, Run, ScalePoint
from neetcode_dojo.protocol import SubmissionFile

FIXTURES = Path(__file__).resolve().parent / "fixtures"
ASSESSMENTS = FIXTURES / "assessments"
BAD_ASSESSMENTS = FIXTURES / "bad_assessments"
CONTENT = FIXTURES / "content"

CORRECT: dict[str, str] = {
    "valid_parentheses": (
        "def is_valid(s: str) -> bool:\n"
        "    pairs = {')': '(', ']': '[', '}': '{'}\n"
        "    stack = []\n"
        "    for char in s:\n"
        "        if char in '([{':\n"
        "            stack.append(char)\n"
        "        elif not stack or stack.pop() != pairs[char]:\n"
        "            return False\n"
        "    return not stack\n"
    ),
    "group_anagrams": (
        "def group_anagrams(strs: list[str]) -> list[list[str]]:\n"
        "    groups = {}\n"
        "    for word in strs:\n"
        "        groups.setdefault(''.join(sorted(word)), []).append(word)\n"
        "    return [sorted(group) for _, group in sorted(groups.items())]\n"
    ),
    "rotate-image": (
        "def rotate(matrix: list[list[int]]) -> None:\n"
        "    matrix[:] = [list(row) for row in zip(*matrix[::-1])]\n"
    ),
    "min_stack": (
        "class MinStack:\n"
        "    def __init__(self) -> None:\n"
        "        self.stack = []\n"
        "        self.mins = []\n"
        "\n"
        "    def push(self, val: int) -> None:\n"
        "        self.stack.append(val)\n"
        "        self.mins.append(val if not self.mins else min(val, self.mins[-1]))\n"
        "\n"
        "    def pop(self) -> None:\n"
        "        self.stack.pop()\n"
        "        self.mins.pop()\n"
        "\n"
        "    def top(self) -> int:\n"
        "        return self.stack[-1]\n"
        "\n"
        "    def getMin(self) -> int:\n"
        "        return self.mins[-1]\n"
    ),
    "encode": (
        "def encode(strs: list[str]) -> str:\n"
        "    return '' if not strs else '|'.join(strs)\n"
        "\n"
        "\n"
        "def decode(s: str) -> list[str]:\n"
        "    return [] if not s else s.split('|')\n"
    ),
    "oracle_drift": "def add_one(value: int) -> int:\n    return value + 1\n",
    "no_cases": "def add_one(value: int) -> int:\n    return value + 1\n",
}

WRONG: dict[str, str] = {
    "valid_parentheses": "def is_valid(s: str) -> bool:\n    return True\n",
    "group_anagrams": (
        "def group_anagrams(strs: list[str]) -> list[list[str]]:\n    return [strs]\n"
    ),
    "rotate-image": (
        "def rotate(matrix: list[list[int]]) -> None:\n"
        "    matrix = [list(row) for row in zip(*matrix[::-1])]\n"
    ),
    "min_stack": "class MinStack:\n    def push(self, val: int) -> None:\n        pass\n",
    "encode": (
        "def encode(strs: list[str]) -> str:\n    return '|'.join(strs)\n"
        "\n\n"
        "def decode(s: str) -> list[str]:\n    return s.split('|')\n"
    ),
}


def make_evaluators(
    *,
    assessments: Path = ASSESSMENTS,
    root: Path = FIXTURES,
    config: EvaluatorConfig | None = None,
    probe_runner: Any = None,
) -> Evaluators:
    """An evaluator set over the fixture trees, with a small deterministic config."""
    return Evaluators(
        root,
        AssessmentStore(assessments),
        config=config or EvaluatorConfig(case_count=6),
        probe_runner=probe_runner,
    )


def files_for(item: str, source: str | None = None) -> tuple[SubmissionFile, ...]:
    content = source if source is not None else CORRECT[item]
    return (SubmissionFile(path="solution.py", content=content),)


def request_for(
    item: str,
    *,
    source: str | None = None,
    files: Sequence[SubmissionFile] | None = None,
    claims: Mapping[str, str] | None = None,
    **extra: Any,
) -> dict[str, Any]:
    """A standard assessment.v1 request, with optional tool-specific extensions."""
    chosen = list(files) if files is not None else list(files_for(item, source))
    payload: dict[str, Any] = {
        "contract": "assessment.v1",
        "curriculum": "neetcode-150",
        "item": item,
        "files": [file.model_dump() for file in chosen],
        "claims": dict(claims or {}),
    }
    payload.update(extra)
    return payload


def synthetic_probe(cost_model: Any) -> Any:
    """A probe runner that replaces wall-clock measurement with a cost model.

    ``cost_model(label, n)`` returns milliseconds, or raises to model a failure.
    Peaks and digests are constant, so only the ratio series decided by the model
    reaches the growth verdict. This is how a complexity *class* can be asserted
    without testing the machine's load.
    """

    def runner(
        student: Any,
        generator: Any,
        reference: Any = None,
        *,
        sizes: list[int],
        repeats: int,
        timeout: float,
        compare: str,
    ) -> Probe:
        points: list[ScalePoint] = []
        for n in sizes:
            try:
                student_run = Run(
                    ms=float(cost_model("yours", n)), peak=8, digest="same", preview="ok"
                )
            except Exception as exc:
                student_run = Run(error=f"{type(exc).__name__}: {exc}")
            reference_run: Run | None = None
            if reference is not None:
                try:
                    reference_run = Run(
                        ms=float(cost_model("reference", n)),
                        peak=8,
                        digest="same",
                        preview="ok",
                    )
                except Exception as exc:
                    reference_run = Run(error=f"{type(exc).__name__}: {exc}")
            points.append(ScalePoint(n=n, student=student_run, reference=reference_run))
            if not student_run.ok:
                break
            if reference_run is not None and not reference_run.ok:
                break
        return Probe(points=points, has_reference=reference is not None)

    return runner


CORRECT["no_reference"] = "def size(values: list) -> int:\n    return len(values)\n"
