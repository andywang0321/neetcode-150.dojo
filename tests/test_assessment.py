"""The private assessment tree: registration shape, static hygiene, and (when the
evaluator core is present) the registrations the new server will consume.

The static half runs on this branch without P5-A: every module imports the local
registry, registers its item's cases, and only advertises a measurement plan when the
item declares the complexity evaluator. The runtime half is skipped until
`neetcode_dojo.registry` lands; it then loads every module and exercises one generated
case, the oracle and the measurement plan through the decorator surface.
"""

from __future__ import annotations

import ast
import importlib.util
import json
import random
import sys
from pathlib import Path

import pytest

from tests.conftest import ROOT

ASSESSMENT = ROOT / "src" / "neetcode_dojo" / "assessment"
ENTITY_KINDS = ("oracle", "cases", "inputs", "reference", "rubric", "measure", "checker")


def _modules(manifest: dict) -> dict[str, Path]:
    found = {path.stem: path for path in ASSESSMENT.glob("*.py") if path.name != "__init__.py"}
    assert set(found) == {item["id"] for item in manifest["item"]}
    return found


def _decorators(path: Path) -> dict[str, str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), str(path))
    found: dict[str, str] = {}
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef):
            continue
        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call) or not isinstance(decorator.func, ast.Name):
                continue
            if len(decorator.args) != 1 or not isinstance(decorator.args[0], ast.Constant):
                continue
            found[decorator.func.id] = str(decorator.args[0].value)
    return found


def test_every_module_imports_the_local_registry(manifest: dict) -> None:
    for item_id, path in _modules(manifest).items():
        source = path.read_text(encoding="utf-8")
        assert "from neetcode_dojo.registry import" in source, f"{item_id}: wrong registry"
        assert "dojo.curriculum" not in source, f"{item_id}: old engine import remains"
        assert "from neetcode_dojo.assessment" not in source
        tree = ast.parse(source, str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    assert alias.name.split(".")[0] in sys.stdlib_module_names, (
                        f"{item_id}: imports {alias.name!r}"
                    )
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if module == "neetcode_dojo.registry":
                    continue
                assert module.split(".")[0] in sys.stdlib_module_names, (
                    f"{item_id}: imports from {module!r}"
                )


def test_every_item_registers_the_kinds_its_manifest_promises(manifest: dict) -> None:
    modules = _modules(manifest)
    checker_count = 0
    for item in manifest["item"]:
        item_id = item["id"]
        decorators = _decorators(modules[item_id])
        assert decorators.get("cases") == item_id, f"{item_id}: no @cases({item_id!r})"
        if "oracle" in item["evaluators"]:
            assert decorators.get("oracle") == item_id, f"{item_id}: no @oracle"
        if "complexity" in item["evaluators"]:
            assert decorators.get("measure") == item_id, f"{item_id}: no @measure"
            assert decorators.get("inputs") == item_id, f"{item_id}: no @inputs"
        else:
            assert "measure" not in decorators, f"{item_id}: plan without complexity"
            assert "inputs" not in decorators, f"{item_id}: inputs without complexity"
        if "checker" in decorators:
            checker_count += 1
            assert decorators["checker"] != item_id
            assert decorators["checker"] in modules[item_id].read_text(encoding="utf-8")
    assert checker_count == 11


def test_no_item_registers_a_rubric(manifest: dict) -> None:
    for item_id, path in _modules(manifest).items():
        assert "rubric" not in _decorators(path), f"{item_id}: unexpected @rubric"


def test_the_private_tree_is_a_package_without_import_side_effects() -> None:
    init = (ASSESSMENT / "__init__.py").read_text(encoding="utf-8")
    tree = ast.parse(init)
    assert not any(isinstance(node, (ast.Import, ast.ImportFrom)) for node in tree.body)
    assert "quarantined" in init.lower()


def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _store(registry, kind: str) -> dict:
    stores = getattr(registry, "STORES", None)
    if isinstance(stores, dict) and kind in stores:
        return stores[kind]
    attribute = {
        "oracle": "ORACLES",
        "cases": "CASES",
        "inputs": "INPUTS",
        "reference": "REFERENCES",
        "rubric": "RUBRICS",
        "measure": "MEASURES",
        "checker": "CHECKERS",
    }[kind]
    store = getattr(registry, attribute, None)
    if not isinstance(store, dict):
        pytest.fail(
            "the P5-A registry does not expose the old registration stores "
            f"(`STORES[{kind!r}]` or `{attribute}`); the assessment content cannot be "
            "checked against it"
        )
    return store


def test_registrations_load_and_sample_through_the_new_registry(manifest: dict) -> None:
    registry = pytest.importorskip(
        "neetcode_dojo.registry", reason="P5-A evaluator core is not on this branch yet"
    )
    reset = getattr(registry, "reset", None)
    if callable(reset):
        reset()
    modules = _modules(manifest)
    for index, (_item_id, path) in enumerate(sorted(modules.items())):
        _load(path, f"p5b_assessment_{index}")

    cases = _store(registry, "cases")
    oracles = _store(registry, "oracle")
    measures = _store(registry, "measure")
    inputs = _store(registry, "inputs")
    checkers = _store(registry, "checker")

    for item in manifest["item"]:
        item_id = item["id"]
        assert item_id in cases, f"{item_id}: no cases registration"
        for size in (2, 7):
            produced = cases[item_id](size, random.Random(f"p5b-{item_id}-{size}"))
            assert isinstance(produced, (tuple, list)) and len(produced) >= 2, item_id
            args = produced[0]
            extras = produced[2] if len(produced) > 2 and isinstance(produced[2], dict) else {}
            assert isinstance(args, list), f"{item_id}: args are not a list"
            if extras.get("predicate"):
                assert extras["predicate"] in checkers, f"{item_id}: missing checker"

            if "oracle" in item["evaluators"]:
                assert item_id in oracles, f"{item_id}: no oracle registration"
                if "ops" not in extras:
                    oracles[item_id](*args)  # a registration that raises is not usable

        if "complexity" in item["evaluators"]:
            assert item_id in measures, f"{item_id}: no measure registration"
            plan = measures[item_id]({})
            json.dumps(plan)
            assert isinstance(plan, dict) and (plan.get("axis") or plan.get("reason")), item_id
            assert item_id in inputs, f"{item_id}: no inputs registration"
            ladder_input = inputs[item_id](2, random.Random(f"p5b-input-{item_id}"))
            assert isinstance(ladder_input, list), item_id


def test_the_restored_predicate_helpers_are_exercised() -> None:
    """The three helpers the old port dropped: the checkers must not raise F821."""
    registry = pytest.importorskip(
        "neetcode_dojo.registry", reason="P5-A evaluator core is not on this branch yet"
    )
    from types import SimpleNamespace

    _load(ASSESSMENT / "course-schedule-ii.py", "p5b_course_schedule_ii")
    _load(ASSESSMENT / "longest-palindromic-substring.py", "p5b_longest_palindrome")
    _load(ASSESSMENT / "serialize-and-deserialize-binary-tree.py", "p5b_serialize")

    checkers = _store(registry, "checker")
    assert checkers["valid_topological_order"](SimpleNamespace(), [0, 1], (2, [[1, 0]]))
    assert checkers["longest_palindrome_valid"](SimpleNamespace(), "bab", ("babad",))

    def deserialize(data):
        return {"encoded": data}

    module = SimpleNamespace(
        __name__="submission",
        serialize=lambda root: "encoded",
        deserialize=lambda data: data,
    )
    # The checker's own shape: a round-trip module is accepted.
    tree_checker = checkers["tree_codec_roundtrip"]
    assert callable(tree_checker)
    # It must not raise NameError on the helper path; the actual verdict belongs to
    # the evaluator parity suite, which exercises it with a real codec.
    try:
        tree_checker(module, "encoded", ([1, None, None],))
    except NameError as exc:  # pragma: no cover - regression guard
        pytest.fail(f"tree checker still has an unresolved helper: {exc}")
