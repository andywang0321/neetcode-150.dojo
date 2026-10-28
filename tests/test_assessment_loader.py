"""The assessment quarantine: probe data, bounded runs, import refusal."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from neetcode_dojo.assessment_loader import (
    AssessmentStore,
    check_imports,
    probe_modules,
)
from tests.support import ASSESSMENTS, BAD_ASSESSMENTS

VALID = ASSESSMENTS / "valid_parentheses.py"
ROTATE = ASSESSMENTS / "rotate-image.py"
ENCODE = ASSESSMENTS / "encode.py"


def test_check_imports_allows_the_standard_library_and_the_local_registry() -> None:
    source = (
        "import random\n"
        "from collections.abc import Sequence\n"
        "from neetcode_dojo.registry import cases, oracle\n"
    )
    assert check_imports(source) == []


def test_check_imports_refuses_an_engine_or_network_import_by_line() -> None:
    problems = check_imports("import os\nimport requests\nfrom dojo.judge import run_cases\n")
    assert any("line 2" in problem and "requests" in problem for problem in problems)
    assert any("line 3" in problem and "dojo" in problem for problem in problems)


def test_check_imports_refuses_relative_imports_and_syntax_errors() -> None:
    assert any("relative imports" in problem for problem in check_imports("from . import helper\n"))
    assert any("does not parse" in problem for problem in check_imports("def broken(:\n"))


def test_probe_reports_registrations_functions_plans_and_samples() -> None:
    report = probe_modules([VALID])
    assert report.fatal is None
    module = report.report_for(VALID)
    assert module is not None
    assert module.error is None
    assert module.has("cases", "valid_parentheses")
    assert module.has("oracle", "valid_parentheses")
    assert module.function_name("reference", "valid_parentheses") == "_reference"
    plan = report.plan_for(VALID, "valid_parentheses")
    assert plan is not None and plan["sizes"] == [64, 128, 256, 512]
    sample = module.case_samples["valid_parentheses"]
    assert sample["decidable"] is True
    assert sample["error"] is None


def test_a_hyphenated_item_module_is_loaded_by_path() -> None:
    store = AssessmentStore(ASSESSMENTS)
    report = store.report("rotate-image")
    assert report is not None and report.error is None
    assert report.has("cases", "rotate-image")


def test_store_caches_a_module_report() -> None:
    store = AssessmentStore(ASSESSMENTS)
    first = store.report("valid_parentheses")
    second = store.report("valid_parentheses")
    assert first is second


def test_an_item_with_no_module_has_no_report() -> None:
    store = AssessmentStore(ASSESSMENTS)
    assert store.report("does-not-exist") is None
    assert store.report("../escape") is None
    assert store.module_for("../escape") is None


def test_a_module_that_raises_at_import_is_reported_not_raised() -> None:
    store = AssessmentStore(BAD_ASSESSMENTS)
    report = store.report("boom")
    assert report is not None
    assert report.error is not None
    assert "RuntimeError" in report.error
    assert "cannot load" in report.error


def test_case_generation_is_deterministic() -> None:
    store = AssessmentStore(ASSESSMENTS)
    requests = [{"n": 3, "seed": "fixed-1"}, {"n": 7, "seed": "fixed-2"}]
    first = store.cases("valid_parentheses", requests)
    second = store.cases("valid_parentheses", requests)
    assert first.ok and second.ok
    assert json.dumps(first.value) == json.dumps(second.value)


def test_inputs_and_oracle_run_in_a_child() -> None:
    store = AssessmentStore(ASSESSMENTS)
    args = store.inputs("valid_parentheses", 4, "seed")
    assert args.ok and args.value == ["((((" + "))))"]
    oracle = store.call("valid_parentheses", "oracle", ["()"])
    assert oracle.ok and oracle.value is True


def test_oracle_many_reports_a_failure_per_call() -> None:
    store = AssessmentStore(ASSESSMENTS)
    result = store.oracle_many(
        "oracle_drift",
        [{"args": [1]}, {"args": [1, 2]}],
    )
    assert result.ok
    assert result.value[0]["ok"] is True
    assert result.value[1]["ok"] is False
    assert "TypeError" in result.value[1]["error"]


def test_a_predicate_checker_runs_with_the_student_module(tmp_path: Path) -> None:
    (tmp_path / "solution.py").write_text(
        "def encode(strs):\n    return '|'.join(strs)\n\n\n"
        "def decode(s):\n    return s.split('|')\n"
    )
    store = AssessmentStore(ASSESSMENTS)
    args = [["a", "b"]]
    got = "a|b"
    assert store.check_predicate(
        "encode",
        "encode_roundtrip",
        got,
        args,
        code_file="solution.py",
        cwd=tmp_path,
    )
    assert not store.check_predicate(
        "encode",
        "encode_roundtrip",
        "a,b",
        args,
        code_file="solution.py",
        cwd=tmp_path,
    )


def test_a_missing_checker_is_a_run_error(tmp_path: Path) -> None:
    (tmp_path / "solution.py").write_text("def encode(strs):\n    return ''\n")
    store = AssessmentStore(ASSESSMENTS)
    with pytest.raises(RuntimeError, match="KeyError"):
        store.check_predicate(
            "encode", "not_a_checker", "", [[]], code_file="solution.py", cwd=tmp_path
        )


def test_the_package_store_points_at_its_private_tree() -> None:
    store = AssessmentStore.from_package()
    assert store.root is not None
    assert store.root.name == "assessment"
    assert store.root.parent.name == "neetcode_dojo"
