"""Shared fixtures for the evaluator-core tests.

No network, no real home directory, and no import of the old engine: the old judge
is reached only through the parity test's subprocess driver.
"""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest

from neetcode_dojo.evaluators import Evaluators
from tests.support import make_evaluators

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
