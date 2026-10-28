"""Prompts and the hint ladder: the curriculum-owned agent policy.

The engine owns the context builder; this repository owns the system prompt and the
ladder. These tests pin the parts a merge must not lose: the ladder is ordered and
non-empty, the tutor is told the appended level is authoritative, the teacher is told it
never sees the item, and the auditor is told to return strict JSON and not to look at
evidence or a reference.
"""

from __future__ import annotations

import importlib
import re
import sys
import tomllib

import pytest

from conftest import ROOT, engine_root

LEVELS = (
    "articulate the blockage",
    "conceptual nudge",
    "topic recognition",
    "data structure / invariant",
    "edge cases",
    "skeleton (no code)",
)


def _text(name: str) -> str:
    return (ROOT / "prompts" / name).read_text(encoding="utf-8")


def test_the_engine_accepts_the_hint_policy() -> None:
    """The TOML is not just shaped right; the engine's parser accepts it."""
    root = engine_root()
    if root is None:
        pytest.skip("no dojo engine checkout found; set DOJO_ENGINE")
    source = str(root / "src")
    if source not in sys.path:
        sys.path.insert(0, source)
    try:
        hints = importlib.import_module("dojo.domain.hints")
    except ImportError as exc:
        pytest.skip(f"the dojo engine is not importable: {exc}")
    policy = hints.parse_policy(
        tomllib.loads((ROOT / "policies/hints.toml").read_text(encoding="utf-8"))
    )
    assert len(policy.levels) == len(LEVELS)
    assert tuple(level.name for level in policy.levels) == LEVELS
    assert "stuck" in policy.reset_markers


def test_the_hint_ladder_is_ordered_and_explicit() -> None:
    policy = tomllib.loads((ROOT / "policies/hints.toml").read_text(encoding="utf-8"))
    assert set(policy) == {"level", "reset_markers"}
    levels = policy["level"]
    assert tuple(level["name"] for level in levels) == LEVELS
    for index, level in enumerate(levels):
        assert set(level) == {"name", "may"}
        assert level["name"].strip()
        assert level["may"].strip()
        assert (
            "do not write code" in level["may"].lower()
            or "never write code" in level["may"].lower()
        )
        if index:
            assert len(level["may"]) >= len(levels[index - 1]["may"]) // 2
    assert policy["reset_markers"]
    assert all(marker.strip() for marker in policy["reset_markers"])
    assert "stuck" in policy["reset_markers"]


def test_the_tutor_obeys_the_appended_level() -> None:
    prompt = _text("tutor.md")
    assert "appended" in prompt.lower()
    assert "hint level" in prompt.lower()
    assert "never write" in prompt.lower()
    assert "complete solution" in prompt.lower()
    assert "hidden tests" in prompt.lower()
    assert "reference solution" in prompt.lower()
    assert "assessment" not in prompt.lower()


def test_the_teacher_never_gets_the_item() -> None:
    prompt = re.sub(r"\s+", " ", _text("teacher.md").lower())
    assert "never see" in prompt
    assert "item statement" in prompt
    assert "no item id" in prompt
    assert "no evidence" in prompt
    assert "do not ask" in prompt.lower()
    # The teacher may not be handed the exercise, so it must not be told to solve one.
    assert "solve a particular exercise" in prompt.lower()


def test_the_leak_auditor_is_strict_json_and_blind_to_evidence() -> None:
    prompt = _text("leak.md")
    assert "strict json only" in prompt.lower()
    assert "no markdown fences" in prompt.lower()
    for key in ('"verdict"', '"reason"', '"revised"'):
        assert key in prompt
    assert "allow" in prompt and "revise" in prompt and "block" in prompt
    assert "evidence" in prompt.lower()
    assert "reference solution" in prompt.lower()
    assert "```" not in prompt  # strict JSON, not a fenced example


def test_the_manifest_wires_the_prompts_and_the_ladder(manifest: dict) -> None:
    capabilities = manifest["capabilities"]
    assert capabilities["assist"]["prompt"] == "prompts/tutor.md"
    assert capabilities["assist"]["hint_policy"] == "policies/hints.toml"
    assert capabilities["instruct"]["prompt"] == "prompts/teacher.md"
    assert capabilities["audit"]["prompt"] == "prompts/leak.md"
    for capability in ("assist", "instruct", "audit"):
        assert (ROOT / capabilities[capability]["prompt"]).is_file()
    reviewer_prompt = ROOT / "prompts/reviewer.md"
    if reviewer_prompt.exists():
        assert reviewer_prompt.read_text(encoding="utf-8").strip()
