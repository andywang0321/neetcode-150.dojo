"""The P5-B migration seam: copy an old assessment module, change only the import.

The old modules import ``dojo.curriculum.registry``. This test copies real modules
out of the read-only old curriculum, rewrites that one import to
``neetcode_dojo.registry``, and runs them through the new tools. It skips when the
old curriculum checkout is not present; it never imports the old engine or edits the
old tree.
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from neetcode_dojo.assessment_loader import AssessmentStore, check_imports
from neetcode_dojo.evaluators import EvaluatorConfig, Evaluators
from neetcode_dojo.protocol import AssessmentRequest, SubmissionFile

OLD_IMPORT = "from dojo.curriculum.registry import"


def _old_curriculum() -> Path | None:
    candidates: list[Path] = []
    configured = os.environ.get("DOJO_OLD_CURRICULUM")
    if configured:
        candidates.append(Path(configured).expanduser())
    for parent in Path(__file__).resolve().parents:
        candidates.append(parent / "dojo-curriculum-neetcode-150")
    for candidate in candidates:
        if (candidate / "assessment" / "two_sum.py").is_file():
            return candidate.resolve()
    return None


OLD_CURRICULUM = _old_curriculum()

pytestmark = pytest.mark.skipif(
    OLD_CURRICULUM is None,
    reason="the read-only old curriculum checkout is not available",
)

TWO_SUM = (
    "def twosum(nums, target):\n"
    "    seen = {}\n"
    "    for index, value in enumerate(nums):\n"
    "        if target - value in seen:\n"
    "            return [seen[target - value], index]\n"
    "        seen[value] = index\n"
    "    return []\n"
)

ENCODE_DECODE = (
    "def encode(strs):\n"
    "    return ''.join(f'{len(s)}:{s}' for s in strs)\n"
    "\n\n"
    "def decode(s):\n"
    "    out = []\n"
    "    i = 0\n"
    "    while i < len(s):\n"
    "        j = s.index(':', i)\n"
    "        n = int(s[i:j])\n"
    "        out.append(s[j + 1:j + 1 + n])\n"
    "        i = j + 1 + n\n"
    "    return out\n"
)


def _port(tmp_path: Path, *items: str) -> tuple[Path, Path]:
    """A tiny curriculum holding copies of the named old items."""
    assert OLD_CURRICULUM is not None
    assessments = tmp_path / "assessments"
    assessments.mkdir()
    for item in items:
        source = (OLD_CURRICULUM / "assessment" / f"{item}.py").read_text(encoding="utf-8")
        assert OLD_IMPORT in source
        ported = source.replace(OLD_IMPORT, "from neetcode_dojo.registry import")
        assert check_imports(ported, dependencies=("random",)) == []
        (assessments / f"{item}.py").write_text(ported, encoding="utf-8")
        workspace = tmp_path / "content" / item / "workspace"
        workspace.mkdir(parents=True)
        (workspace / "solution.py").write_text(
            (OLD_CURRICULUM / "items" / f"{item}.py").read_text(encoding="utf-8"),
            encoding="utf-8",
        )
    return tmp_path, assessments


def _request(item: str, source: str) -> AssessmentRequest:
    return AssessmentRequest(
        curriculum="neetcode-150",
        item=item,
        files=(SubmissionFile(path="solution.py", content=source),),
    )


def test_an_old_oracle_and_case_generator_port_with_only_the_import_changed(
    tmp_path: Path,
) -> None:
    root, assessments = _port(tmp_path, "two_sum")
    tool = Evaluators(
        root,
        AssessmentStore(assessments),
        config=EvaluatorConfig(case_count=4),
    )
    tests = tool.assess_tests(_request("two_sum", TWO_SUM).model_dump())
    assert tests.outcome == "pass", tests.details
    oracle = tool.assess_oracle(_request("two_sum", TWO_SUM).model_dump())
    assert oracle.outcome == "pass", oracle.details
    assert oracle.details["oracle_disagreements"] == []


def test_an_old_predicate_item_ports_and_its_checker_decides(tmp_path: Path) -> None:
    root, assessments = _port(tmp_path, "encode_and_decode_strings")
    tool = Evaluators(
        root,
        AssessmentStore(assessments),
        config=EvaluatorConfig(case_count=4),
    )
    result = tool.assess_tests(_request("encode_and_decode_strings", ENCODE_DECODE).model_dump())
    assert result.outcome == "pass", result.details
