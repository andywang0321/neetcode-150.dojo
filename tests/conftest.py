"""Shared fixtures: this curriculum's root, its manifest, and the new engine.

The manifest is validated by the engine's own loader when that checkout is available
(`DOJO_ENGINE`, or the `rebuild` checkout beside this workspace). The content and
private-tree tests do not need the engine: they are this repository's own gates.
"""

from __future__ import annotations

import importlib
import os
import sys
import tomllib
from collections.abc import Callable
from pathlib import Path

import pytest

#: The curriculum root: the directory holding `curriculum.toml`.
ROOT = Path(__file__).resolve().parents[1]

#: The read-only old curriculum and engine, used only by the parity report.
OLD_CURRICULUM = Path(
    os.environ.get(
        "OLD_CURRICULUM",
        "/Users/andywang/Projects/dojo-workspace/dojo-curriculum-neetcode-150",
    )
).expanduser()
OLD_ENGINE = Path(
    os.environ.get("OLD_ENGINE", "/Users/andywang/Projects/dojo-workspace/dojo")
).expanduser()


def _engine_candidates() -> list[Path]:
    candidates = []
    configured = os.environ.get("DOJO_ENGINE")
    if configured:
        candidates.append(Path(configured).expanduser())
    candidates.extend(
        (
            Path("/Users/andywang/Projects/dojo-workspace/rebuild"),
            ROOT.parent / "rebuild",
            ROOT.parents[1] / "rebuild",
            ROOT.parents[2] / "rebuild",
        )
    )
    return candidates


def engine_root() -> Path | None:
    """The new engine checkout whose `dojo` package can validate the manifest."""
    for candidate in _engine_candidates():
        if (candidate / "src" / "dojo" / "protocol" / "manifest.py").is_file():
            return candidate.resolve()
    return None


def old_engine_root() -> Path | None:
    """The read-only old engine, used only to prove parity of the copied corpus."""
    if (OLD_ENGINE / "src" / "dojo" / "judge" / "runner.py").is_file():
        return OLD_ENGINE.resolve()
    return None


def old_curriculum_root() -> Path | None:
    if (OLD_CURRICULUM / "curriculum.toml").is_file():
        return OLD_CURRICULUM.resolve()
    return None


@pytest.fixture(scope="session")
def manifest() -> dict:
    """The decoded manifest, used by the independent shape/content tests."""
    return tomllib.loads((ROOT / "curriculum.toml").read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def engine_loader() -> Callable[[Path], object]:
    """The new engine's `load_manifest`, or a skip when no engine checkout is present."""
    root = engine_root()
    if root is None:
        pytest.skip("no dojo engine checkout found; set DOJO_ENGINE to run the loader gate")
    source = str(root / "src")
    if source not in sys.path:
        sys.path.insert(0, source)
    try:
        module = importlib.import_module("dojo.protocol.manifest")
    except ImportError as exc:  # pragma: no cover - depends on the host checkout
        pytest.skip(f"the dojo engine is not importable: {exc}")
    return module.load_manifest
