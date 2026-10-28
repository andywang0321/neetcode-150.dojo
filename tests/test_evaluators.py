"""The six evaluator tools over fixture assessment/content trees, offline."""

from __future__ import annotations

import math
from pathlib import Path

import pytest

from neetcode_dojo.evaluators import Evaluators
from tests.support import ASSESSMENTS, CORRECT, make_evaluators, request_for, synthetic_probe

# --------------------------------------------------------------- assess.tests


def test_tests_pass_a_correct_submission(evaluators: Evaluators) -> None:
    result = evaluators.assess_tests(request_for("valid_parentheses"))
    assert result.outcome == "pass"
    assert result.score == 1.0
    assert result.details["passed"] == result.details["total"] == 6
    assert all(case["ok"] for case in result.details["cases"])


def test_tests_report_wrong_answers_with_per_case_detail(evaluators: Evaluators) -> None:
    result = evaluators.assess_tests(
        request_for("valid_parentheses", source="def is_valid(s):\n    return True\n")
    )
    assert result.outcome in ("fail", "partial")
    assert result.details["passed"] < result.details["total"]
    failures = [case for case in result.details["cases"] if not case["ok"]]
    assert failures
    assert failures[0]["expected"] is not None


def test_tests_turn_a_crash_into_error_evidence(evaluators: Evaluators) -> None:
    result = evaluators.assess_tests(
        request_for(
            "valid_parentheses",
            source="def is_valid(s):\n    raise RuntimeError('boom')\n",
        )
    )
    assert result.outcome == "error"
    assert any("RuntimeError" in (case["error"] or "") for case in result.details["cases"])


def test_tests_report_an_import_failure(evaluators: Evaluators) -> None:
    result = evaluators.assess_tests(
        request_for("valid_parentheses", source="this is not python\n")
    )
    assert result.outcome == "error"
    assert result.details["status"] == "error"


def test_tests_unknown_item_is_error_evidence(evaluators: Evaluators) -> None:
    result = evaluators.assess_tests(request_for("does-not-exist", files=()))
    assert result.outcome == "error"
    assert "unknown item" in result.summary


def test_tests_without_a_case_generator_is_an_error(evaluators: Evaluators) -> None:
    result = evaluators.assess_tests(request_for("no_cases"))
    assert result.outcome == "error"
    assert "@cases" in result.summary


def test_tests_sorted_mode_passes_any_group_order(evaluators: Evaluators) -> None:
    source = (
        "def group_anagrams(strs):\n"
        "    groups = {}\n"
        "    for word in reversed(strs):\n"
        "        groups.setdefault(''.join(sorted(word)), []).append(word)\n"
        "    return list(groups.values())\n"
    )
    result = evaluators.assess_tests(request_for("group_anagrams", source=source))
    assert result.outcome == "pass", result.details


def test_tests_mutates_mode_grades_the_effect(evaluators: Evaluators) -> None:
    good = evaluators.assess_tests(request_for("rotate-image"))
    assert good.outcome == "pass", good.details
    rebinding = "def rotate(matrix):\n    matrix = [list(row) for row in zip(*matrix[::-1])]\n"
    bad = evaluators.assess_tests(request_for("rotate-image", source=rebinding))
    assert bad.outcome in ("fail", "partial")
    assert bad.details["passed"] < bad.details["total"]


def test_tests_ops_mode_replays_a_class(evaluators: Evaluators) -> None:
    result = evaluators.assess_tests(request_for("min_stack"))
    assert result.outcome == "pass", result.details
    assert result.details["cases"][0]["ops"]


def test_tests_predicate_is_decided_by_the_module_checker(evaluators: Evaluators) -> None:
    result = evaluators.assess_tests(request_for("encode"))
    assert result.outcome == "pass", result.details
    broken = CORRECT["encode"].replace("return [] if not s else s.split('|')", "return []")
    bad = evaluators.assess_tests(request_for("encode", source=broken))
    assert bad.outcome in ("fail", "partial")


def test_tests_resolve_a_sibling_import(evaluators: Evaluators) -> None:
    from neetcode_dojo.protocol import SubmissionFile

    files = (
        SubmissionFile(path="helper.py", content=CORRECT["valid_parentheses"]),
        SubmissionFile(
            path="solution.py",
            content=(
                "from helper import is_valid as _impl\n\n\ndef is_valid(s):\n    return _impl(s)\n"
            ),
        ),
    )
    result = evaluators.assess_tests(request_for("valid_parentheses", files=files))
    assert result.outcome == "pass", result.details


def test_tests_refuse_a_path_that_escapes_the_workspace(evaluators: Evaluators) -> None:
    from neetcode_dojo.protocol import SubmissionFile

    files = (SubmissionFile(path="../evil.py", content="def is_valid(s):\n    return True\n"),)
    result = evaluators.assess_tests(request_for("valid_parentheses", files=files))
    assert result.outcome == "error"
    assert "invalid submission" in result.summary


def test_tests_invalid_request_is_error_evidence(evaluators: Evaluators) -> None:
    result = evaluators.assess_tests({"item": "valid_parentheses"})
    assert result.outcome == "error"
    assert "invalid assessment request" in result.summary


# -------------------------------------------------------------- assess.oracle


def test_oracle_passes_a_correct_submission(evaluators: Evaluators) -> None:
    result = evaluators.assess_oracle(request_for("valid_parentheses"))
    assert result.outcome == "pass", result.details
    assert result.details["source"] == "oracle"
    assert result.details["oracle_disagreements"] == []


def test_oracle_is_independent_of_the_generators_expected_answers(
    evaluators: Evaluators,
) -> None:
    result = evaluators.assess_oracle(request_for("oracle_drift"))
    assert result.outcome == "unresolved"
    assert result.details["oracle_disagreements"]


def test_oracle_without_an_oracle_is_unresolved(evaluators: Evaluators) -> None:
    result = evaluators.assess_oracle(request_for("encode"))
    assert result.outcome == "unresolved"
    assert "no oracle" in result.summary


def test_oracle_handles_the_ops_shape(evaluators: Evaluators) -> None:
    result = evaluators.assess_oracle(request_for("min_stack"))
    assert result.outcome == "pass", result.details


# ---------------------------------------------------------- assess.complexity


def test_complexity_without_a_plan_is_unresolved(evaluators: Evaluators) -> None:
    result = evaluators.assess_complexity(request_for("min_stack"))
    assert result.outcome == "unresolved"
    assert "no measurement plan" in result.summary


def test_complexity_passes_when_growth_matches_the_reference() -> None:
    tool = make_evaluators(probe_runner=synthetic_probe(lambda label, n: n))
    result = tool.assess_complexity(request_for("valid_parentheses"))
    assert result.outcome == "pass", result.details
    assert result.details["time"]["kind"] == "matches"
    assert result.details["time"]["student_class"] == "O(n)"


def test_complexity_fails_when_growth_is_one_class_worse() -> None:
    tool = make_evaluators(
        probe_runner=synthetic_probe(lambda label, n: n * math.log(n) if label == "yours" else n)
    )
    result = tool.assess_complexity(request_for("valid_parentheses"))
    assert result.outcome == "fail", result.details
    assert result.details["time"]["kind"] == "worse"
    assert result.details["time"]["student_class"] == "O(n log n)"
    assert result.details["time"]["steps"] == 1


def test_complexity_reports_a_scale_failure() -> None:
    def model(label: str, n: int) -> float:
        if n >= 128:
            raise ValueError("Not enough elements!")
        return 1.0

    tool = make_evaluators(probe_runner=synthetic_probe(model))
    result = tool.assess_complexity(request_for("valid_parentheses"))
    assert result.outcome == "fail"
    assert result.details["failed_at"] == 128
    assert "Not enough elements!" in result.summary


def test_complexity_without_a_reference_is_unresolved() -> None:
    tool = make_evaluators(probe_runner=synthetic_probe(lambda label, n: n))
    result = tool.assess_complexity(request_for("no_reference"))
    assert result.outcome == "unresolved"
    assert result.details["reference_used"] is False


def test_complexity_plan_sizes_are_used() -> None:
    seen: dict[str, object] = {}

    def runner(student, generator, reference=None, **kwargs):
        seen.update(kwargs)
        return synthetic_probe(lambda label, n: n)(student, generator, reference, **kwargs)

    tool = make_evaluators(probe_runner=runner)
    tool.assess_complexity(request_for("valid_parentheses"))
    assert seen["sizes"] == [64, 128, 256, 512]
    assert seen["compare"] == "strict"


# ------------------------------------------------------------- assess.style


def test_style_is_advisory_and_clean_code_has_no_flags(evaluators: Evaluators) -> None:
    result = evaluators.assess_style(request_for("valid_parentheses"))
    assert result.outcome == "pass"
    assert result.score is None
    assert result.details["flags"] == []
    assert result.details["files"][0]["path"] == "solution.py"


def test_style_reports_ruff_findings_as_flags(evaluators: Evaluators) -> None:
    result = evaluators.assess_style(
        request_for(
            "valid_parentheses", source="import sys\n\n\ndef is_valid(s):\n    return True\n"
        )
    )
    codes = {finding["code"] for finding in result.details["files"][0]["ruff"]}
    assert "F401" in codes
    assert result.details["flags"]


def test_style_ignores_the_visible_check(evaluators: Evaluators) -> None:
    from neetcode_dojo.protocol import SubmissionFile

    files = (SubmissionFile(path="check.py", content="import sys\n"),)
    result = evaluators.assess_style(request_for("valid_parentheses", files=files))
    assert result.outcome == "error"
    assert "no Python files" in result.summary


def test_style_with_no_python_files_is_error_evidence(evaluators: Evaluators) -> None:
    result = evaluators.assess_style(request_for("valid_parentheses", files=()))
    assert result.outcome == "error"


# ----------------------------------------------------------------- variant


def test_variant_defaults_to_a_re_solve(evaluators: Evaluators) -> None:
    result = evaluators.variant(request_for("valid_parentheses"))
    assert result.outcome == "pass"
    assert result.details["variant"]["kind"] == "re-solve"


def test_variant_can_re_derive_inputs_without_leaking_expected_answers(
    evaluators: Evaluators,
) -> None:
    result = evaluators.variant(
        request_for("valid_parentheses", mode="re-derive", history=[{"grade": 2}])
    )
    assert result.outcome == "pass"
    assert result.details["variant"]["kind"] == "re-derive"
    assert len(result.details["inputs"]) == 3
    assert all("expected" not in entry for entry in result.details["inputs"])


# ------------------------------------------------------------------- grade


def _evidence(outcome: str, *, evaluator: str = "tests", details: dict | None = None) -> dict:
    return {
        "evaluator": evaluator,
        "outcome": outcome,
        "summary": "evidence",
        "details": details or {},
    }


def test_grade_four_needs_corroborated_claims(evaluators: Evaluators) -> None:
    result = evaluators.grade(
        request_for(
            "valid_parentheses",
            claims={"time": "O(n)"},
            evidence=[
                _evidence("pass", evaluator="tests"),
                _evidence(
                    "pass",
                    evaluator="complexity",
                    details={"time": {"student_class": "O(n)"}, "space": {}},
                ),
            ],
        )
    )
    assert result.outcome == "pass"
    assert result.details["grade"] == 4
    assert result.score == 1.0


def test_grade_three_without_claims(evaluators: Evaluators) -> None:
    result = evaluators.grade(request_for("valid_parentheses", evidence=[_evidence("pass")]))
    assert result.details["grade"] == 3


def test_grade_two_for_partial_evidence(evaluators: Evaluators) -> None:
    result = evaluators.grade(request_for("valid_parentheses", evidence=[_evidence("partial")]))
    assert result.details["grade"] == 2
    assert result.outcome == "partial"


def test_grade_one_for_a_failure(evaluators: Evaluators) -> None:
    result = evaluators.grade(request_for("valid_parentheses", evidence=[_evidence("fail")]))
    assert result.details["grade"] == 1
    assert result.outcome == "fail"


def test_grade_is_unresolved_while_evidence_is_unresolved(evaluators: Evaluators) -> None:
    result = evaluators.grade(request_for("valid_parentheses", evidence=[_evidence("error")]))
    assert result.outcome == "unresolved"
    assert result.details["grade"] is None


def test_grade_without_evidence_is_unresolved(evaluators: Evaluators) -> None:
    result = evaluators.grade(request_for("valid_parentheses"))
    assert result.outcome == "unresolved"


def test_grade_rejects_malformed_evidence(evaluators: Evaluators) -> None:
    result = evaluators.grade(
        request_for("valid_parentheses", evidence=[{"evaluator": "tests", "outcome": "nope"}])
    )
    assert result.outcome == "error"
    assert "invalid assessment request" in result.summary


def test_style_flags_withhold_grade_four(evaluators: Evaluators) -> None:
    result = evaluators.grade(
        request_for(
            "valid_parentheses",
            claims={"time": "O(n)"},
            evidence=[
                _evidence("pass", evaluator="style", details={"flags": ["ruff F401"]}),
                _evidence(
                    "pass",
                    evaluator="complexity",
                    details={"time": {"student_class": "O(n)"}},
                ),
            ],
        )
    )
    assert result.details["grade"] == 3


# -------------------------------------------------------------- error paths


def test_tools_never_raise_for_bad_inputs(evaluators: Evaluators) -> None:
    for tool in (
        evaluators.assess_tests,
        evaluators.assess_oracle,
        evaluators.assess_complexity,
        evaluators.assess_style,
        evaluators.variant,
        evaluators.grade,
    ):
        result = tool({})
        assert result.outcome == "error"
        assert result.summary


def test_a_broken_assessment_module_is_error_evidence() -> None:
    from neetcode_dojo.assessment_loader import AssessmentStore

    tool = Evaluators(
        ASSESSMENTS.parent,
        AssessmentStore(ASSESSMENTS.parent / "bad_assessments"),
    )
    result = tool.assess_tests(request_for("boom", source="def f(x):\n    return x\n"))
    assert result.outcome == "error"
    assert "does not load" in result.summary


def test_missing_assessment_tree_is_error_evidence(tmp_path: Path) -> None:
    from neetcode_dojo.assessment_loader import AssessmentStore

    tool = Evaluators(tmp_path, AssessmentStore(tmp_path / "missing"))
    result = tool.assess_tests(request_for("valid_parentheses"))
    assert result.outcome == "error"
    assert "unknown item" in result.summary


@pytest.mark.parametrize("item", ["valid_parentheses", "group_anagrams"])
def test_results_are_json_serializable(evaluators: Evaluators, item: str) -> None:
    result = evaluators.assess_tests(request_for(item))
    payload = result.model_dump(mode="json")
    assert payload["contract"] == "assessment.v1"
    assert payload["outcome"] in ("pass", "fail", "partial", "error", "unresolved")


def test_grade_four_needs_every_complexity_claim_measured(evaluators: Evaluators) -> None:
    result = evaluators.grade(
        request_for(
            "valid_parentheses",
            claims={"time": "O(n)", "space": "O(1)"},
            evidence=[
                _evidence("pass", evaluator="tests"),
                _evidence(
                    "pass",
                    evaluator="complexity",
                    details={"time": {"student_class": "O(n)"}},
                ),
            ],
        )
    )
    assert result.details["grade"] == 3
    statuses = {check["axis"]: check["status"] for check in result.details["claim_checks"]}
    assert statuses == {"time": "agrees", "space": "unmeasured"}


def test_grade_three_when_a_claim_contradicts_the_measurement(
    evaluators: Evaluators,
) -> None:
    result = evaluators.grade(
        request_for(
            "valid_parentheses",
            claims={"time": "O(1)"},
            evidence=[
                _evidence("pass", evaluator="tests"),
                _evidence(
                    "pass",
                    evaluator="complexity",
                    details={"time": {"student_class": "O(n)"}},
                ),
            ],
        )
    )
    assert result.details["grade"] == 3
    assert "disagrees" in " ".join(result.details["notes"])


def test_grade_accepts_the_engine_evidence_fields(evaluators: Evaluators) -> None:
    """The engine's evidence rows carry assurance and score; they must not make a
    valid grade request fail validation."""
    result = evaluators.grade(
        request_for(
            "valid_parentheses",
            claims={"time": "O(n)"},
            evidence=[
                {
                    "evaluator": "complexity",
                    "assurance": "measured",
                    "outcome": "pass",
                    "score": 1.0,
                    "summary": "time O(n)",
                    "details": {"time": {"student_class": "O(n)"}},
                }
            ],
        )
    )
    assert result.details["grade"] == 4
