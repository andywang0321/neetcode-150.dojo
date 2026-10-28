"""The deterministic review and the optional model merge."""

import pytest

from reviewer.contracts import ReviewResult, SubmissionFile
from reviewer.review import ReviewUnavailable, review
from reviewer.tests.support import (
    BINARY_SOLUTION,
    HASH_SOLUTION,
    MESSY_SOLUTION,
    evidence,
    make_request,
)


class RecordingModel:
    """A model double: records the prompt and returns or raises on demand."""

    def __init__(
        self,
        result: ReviewResult | None = None,
        error: Exception | None = None,
    ) -> None:
        self.result = result or ReviewResult(
            summary="Model summary",
            strengths=("Model strength",),
            improvements=("Model improvement",),
            next_steps=("Model step",),
            quality=0.99,
        )
        self.error = error
        self.calls: list[tuple[str, str]] = []

    def review(self, system: str, user: str) -> ReviewResult:
        self.calls.append((system, user))
        if self.error is not None:
            raise self.error
        return self.result


def test_valid_request_returns_a_valid_review_result() -> None:
    result = review(make_request())

    assert isinstance(result, ReviewResult)
    assert "two-sum" in result.summary
    assert "grade 3 (pass)" in result.summary
    assert "1 of 1 evaluator reports passed" in result.summary
    assert result.strengths
    assert result.next_steps
    assert result.quality is not None
    assert 0.0 <= result.quality <= 1.0


def test_failed_evidence_becomes_an_improvement_and_a_next_step() -> None:
    request = make_request(
        grade=2,
        evidence_items=[evidence(outcome="partial", summary="3/5 cases passed")],
    )

    result = review(request)

    assert "grade 2 (partial)" in result.summary
    assert "0 of 1 evaluator reports passed" in result.summary
    assert any("tests reported partial" in item and "3/5" in item for item in result.improvements)
    assert any("Fix the tests finding" in step for step in result.next_steps)


def test_ungraded_review_has_no_quality() -> None:
    result = review(make_request(grade=None))

    assert "ungraded" in result.summary
    assert result.quality is None


def test_no_evidence_is_reported_honestly() -> None:
    result = review(make_request(evidence_items=[]))

    assert "no evaluator evidence was recorded" in result.summary
    assert any("No evaluator evidence was recorded" in item for item in result.improvements)
    assert any("Run the item's evaluators" in step for step in result.next_steps)


def test_no_submitted_code_is_reported_honestly() -> None:
    result = review(make_request(files=()))

    assert "No submitted Python file was available" in result.summary
    assert any("No submitted Python file was available" in item for item in result.improvements)
    assert result.quality is not None


def test_the_visible_harness_is_not_mistaken_for_a_solution() -> None:
    result = review(
        make_request(files=(SubmissionFile(path="check.py", content="raise SystemExit\n"),))
    )

    assert "No submitted Python file was available" in result.summary
    assert not any("check.py" in item for item in result.improvements)


def test_syntax_error_still_returns_a_review() -> None:
    request = make_request(files=(SubmissionFile(path="solution.py", content="def broken(:\n"),))

    result = review(request)

    assert "does not parse" in result.summary
    assert any("solution.py" in item and "syntax error" in item for item in result.improvements)
    assert result.quality is not None


def test_clean_code_scores_higher_than_messy_code() -> None:
    clean = review(make_request(files=(SubmissionFile(path="solution.py", content=HASH_SOLUTION),)))
    messy = review(
        make_request(files=(SubmissionFile(path="solution.py", content=MESSY_SOLUTION),))
    )

    assert clean.quality is not None
    assert messy.quality is not None
    assert clean.quality > messy.quality
    assert any("dict or Counter" in item for item in clean.strengths)
    assert any("nested iteration" in item for item in messy.improvements)
    assert any("print" in item for item in messy.improvements)


def test_pattern_family_shapes_the_strength_and_next_steps() -> None:
    request = make_request(
        item="binary-search",
        statement="Given a sorted array, return the index of target.",
        files=(SubmissionFile(path="solution.py", content=BINARY_SOLUTION),),
        claims={"time": "O(log n)", "space": "O(1)"},
    )

    result = review(request)

    assert "Binary Search" in result.summary
    assert any("halves it each step" in item for item in result.strengths)
    assert any("empty array" in step for step in result.next_steps)


def test_claim_mismatch_is_flagged() -> None:
    result = review(
        make_request(
            files=(SubmissionFile(path="solution.py", content=MESSY_SOLUTION),),
            claims={"time": "O(n)"},
        )
    )

    assert any("nested iteration" in item and "O(n)" in item for item in result.improvements)


def test_complexity_evidence_disagreement_is_flagged() -> None:
    result = review(
        make_request(
            evidence_items=[
                evidence(evaluator="complexity", outcome="fail", summary="measured O(n^2)")
            ],
            claims={"time": "O(n)"},
        )
    )

    assert any("not corroborated" in item and "complexity" in item for item in result.improvements)


def test_missing_complexity_claims_become_next_steps() -> None:
    both = review(make_request(claims={}))
    space_only = review(make_request(claims={"time": "O(n)"}))

    assert any("time and space complexity" in step for step in both.next_steps)
    assert any("space complexity" in step for step in space_only.next_steps)


def test_review_is_advisory_and_never_touches_the_grade() -> None:
    request = make_request(grade=2)
    before = request.model_dump()

    result = review(request)
    payload = result.model_dump()

    assert set(payload) == {"summary", "strengths", "improvements", "next_steps", "quality"}
    assert "grade" not in payload
    assert request.model_dump() == before
    assert request.grade == 2


def test_review_is_deterministic() -> None:
    request = make_request(grade=2, evidence_items=[evidence(outcome="partial")])

    assert review(request) == review(request)


@pytest.mark.parametrize("grade", [1, 2, 3, 4])
def test_quality_is_in_range_for_every_grade(grade: int) -> None:
    result = review(make_request(grade=grade))

    assert result.quality is not None
    assert 0.0 <= result.quality <= 1.0


def test_model_prose_is_merged_with_grounded_findings() -> None:
    model = RecordingModel()

    result = review(make_request(), model)

    assert result.summary == "Model summary"
    assert "Model strength" in result.strengths
    assert any("tests passed with machine assurance" in item for item in result.strengths)
    assert "Model improvement" in result.improvements
    assert result.quality == review(make_request()).quality
    assert len(model.calls) == 1
    system, user = model.calls[0]
    assert "advisory" in system
    assert "two-sum" in user
    assert "solution.py" in user


def test_model_quality_is_ignored_and_the_rubric_wins() -> None:
    model = RecordingModel(
        result=ReviewResult(summary="Model summary", quality=0.99),
    )

    result = review(make_request(), model)

    assert result.quality != 0.99
    assert result.quality == review(make_request()).quality


def test_model_prompt_contains_no_hidden_material() -> None:
    model = RecordingModel()

    review(make_request(), model)

    system, user = model.calls[0]
    assert "ASSESSMENT-SECRET" not in system + user
    assert "assessment" not in user.lower()
    assert "oracle" not in user.lower()
    assert "private" not in user.lower()


def test_model_failure_is_unavailable_not_a_crash() -> None:
    model = RecordingModel(error=RuntimeError("connection reset"))

    with pytest.raises(ReviewUnavailable, match="model reviewer failed"):
        review(make_request(), model)


def test_no_model_means_the_deterministic_review() -> None:
    assert review(make_request(), None) == review(make_request())
