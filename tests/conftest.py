"""Shared fixtures: the evaluator-core doubles plus this curriculum's root/manifest.

No network, no real home directory, no old-engine import: the old judge is reached only
through the parity test's subprocess driver. The manifest is validated by the engine's own
loader when a checkout is available (`DOJO_ENGINE`, or the rebuild checkout beside this
workspace); the content/private-tree tests are this repository's own gates.
"""

from __future__ import annotations

import copy
import hashlib
import importlib
import importlib.util
import json
import os
import sys
import tomllib
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from neetcode_dojo.evaluators import Evaluators
from tests.support import make_evaluators

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

#: Registry decorators injected into a measured module's namespace by the probe
#: harness; the synthetic measurement must inject the same set.
_NOOP_DECORATORS = (
    "oracle",
    "judge_case",
    "profiler_input",
    "checker",
    "reference",
    "cases",
    "inputs",
    "measure",
    "rubric",
)


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


@pytest.fixture()
def evaluators() -> Evaluators:
    """The six tools over the fixture assessment and content trees."""
    return make_evaluators()


@pytest.fixture()
def synthetic_probe(
    monkeypatch: pytest.MonkeyPatch,
) -> Callable[[Callable[[str, int], float]], Any]:
    """Replace the probe's subprocess measurement with a deterministic cost model.

    Everything else stays real: pairing, medians, digests, failure propagation and
    the ratio series. A test may assert a complexity verdict only because the
    measurement is exact here — reading a class off wall-clock time tests the
    machine's load, not the code.
    """

    def install(model: Callable[[str, int], float]) -> Callable[[str, int], float]:
        from neetcode_dojo.measure.probe import Run

        def _identity_decorator(*args: Any, **kwargs: Any) -> Callable:
            def wrap(fn: Callable) -> Callable:
                return fn

            return wrap

        def fake_run_one(
            target: Any,
            args: list[Any],
            timeout: float = 20.0,
            compare: str = "strict",
            *,
            python: Any = None,
        ) -> Run:
            size = sum(len(value) if isinstance(value, (list, str)) else 1 for value in args)
            spec = importlib.util.spec_from_file_location(f"synth_{target.label}", target.path)
            if spec is None or spec.loader is None:
                return Run(error="cannot load the measured module")
            module = importlib.util.module_from_spec(spec)
            for name in _NOOP_DECORATORS:
                setattr(module, name, _identity_decorator)
            try:
                spec.loader.exec_module(module)
                got = getattr(module, target.function_name)(*copy.deepcopy(args))
            except BaseException as exc:  # mirrors the harness
                return Run(error=f"{type(exc).__name__}: {exc}")
            blob = json.dumps(got, sort_keys=True, default=str)
            return Run(
                ms=float(model(target.label, size)),
                peak=8 * size,
                digest=hashlib.sha256(blob.encode()).hexdigest(),
                preview=blob[:60],
            )

        monkeypatch.setattr("neetcode_dojo.measure.probe.run_one", fake_run_one)
        return model

    return install


@pytest.fixture()
def repo_root() -> Path:
    """The neetcode-150.dojo checkout this test suite lives in."""
    return Path(__file__).resolve().parents[1]
