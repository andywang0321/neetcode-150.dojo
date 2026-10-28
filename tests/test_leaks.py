"""The quarantine holds: no private assessment material in a prompt or student path.

This is a content-boundary test, not a runtime one. It compares the private tree with
everything a student or an in-solve agent can read: the statements, the workspace files,
the manifest and the system prompts. Exact long lines and 120-character statement chunks
are the practical tripwires: they catch a careless copy without flagging the coincidental
shared vocabulary that a statement, a starter signature and an oracle must have.
"""

from __future__ import annotations

import re
from pathlib import Path

from conftest import ROOT

PRIVATE = ROOT / "src" / "neetcode_dojo" / "assessment"
PROMPTS = tuple(sorted((ROOT / "prompts").glob("*.md")))
STUDENT = tuple(
    sorted(list((ROOT / "content").rglob("*.md")) + list((ROOT / "content").rglob("*.py")))
)
FORBIDDEN_IN_PUBLIC = (
    "neetcode_dojo.assessment",
    "@oracle(",
    "@cases(",
    "@reference(",
    "@measure(",
    "@checker(",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def test_the_private_tree_never_appears_in_a_student_path() -> None:
    for path in STUDENT:
        assert PRIVATE not in path.parents
        assert "assessment" not in path.parts
        text = _read(path)
        for marker in FORBIDDEN_IN_PUBLIC:
            assert marker not in text, f"{path.relative_to(ROOT)}: {marker}"


def test_the_prompts_never_reference_the_private_tree() -> None:
    assert PROMPTS
    for path in PROMPTS:
        text = _read(path)
        for marker in FORBIDDEN_IN_PUBLIC:
            assert marker not in text, f"{path.name}: {marker}"


def test_no_private_source_line_is_copied_into_a_prompt_or_workspace() -> None:
    public = _normalise("\n".join(_read(path) for path in (*PROMPTS, *STUDENT)))
    for module in PRIVATE.glob("*.py"):
        for line in _read(module).splitlines():
            stripped = line.strip()
            if len(stripped) < 80:
                continue
            assert stripped not in public, (
                f"{module.name}: a private source line appears in the public tree: "
                f"{stripped[:100]!r}"
            )


def test_no_statement_text_reaches_a_prompt() -> None:
    prompts = _normalise("\n".join(_read(path) for path in PROMPTS))
    for statement in sorted((ROOT / "content").glob("*/statement.md")):
        text = _normalise(_read(statement))
        for start in range(0, max(1, len(text) - 119), 60):
            chunk = text[start : start + 120]
            if len(chunk) < 120:
                break
            assert chunk not in prompts, (
                f"{statement.parent.name}: statement text appears in a prompt: {chunk[:80]!r}"
            )


def test_no_item_title_or_id_reaches_a_prompt(manifest: dict) -> None:
    prompts = _normalise("\n".join(_read(path) for path in PROMPTS))
    for item in manifest["item"]:
        title = item["title"]
        pattern = r"(?<![A-Za-z0-9])" + re.escape(title) + r"(?![A-Za-z0-9])"
        assert re.search(pattern, prompts, re.IGNORECASE) is None, (
            f"{item['id']}: the item title appears in a prompt"
        )
        pattern = r"(?<![A-Za-z0-9_-])" + re.escape(item["id"]) + r"(?![A-Za-z0-9_-])"
        assert re.search(pattern, prompts) is None, f"{item['id']}: the item id appears in a prompt"


def test_no_student_file_contains_a_reference_implementation(manifest: dict) -> None:
    for item in manifest["item"]:
        workspace = ROOT / item["workspace"]
        solution = _read(workspace / "solution.py")
        assert "raise NotImplementedError" in solution
        # The starter is a signature plus a stub. The old examples block is appended
        # below the sentinel, and its expected values are student-visible by design;
        # the starter half must not return an answer.
        starter = solution.split("# --- dojo: visible examples", 1)[0]
        assert "return " not in starter, f"{item['id']}: starter has a return statement"
        assert "# --- end dojo ---" in solution


def test_the_manifest_does_not_carry_old_content_paths(manifest: dict) -> None:
    for item in manifest["item"]:
        for key in ("statement", "workspace"):
            assert not item[key].startswith(("items/", "checks/", "assessment/"))
    assert not (ROOT / "items").exists()
    assert not (ROOT / "checks").exists()
    assert not (ROOT / "assessment").exists()
