"""The message-only A2A executor: errors are messages, never exceptions."""

import asyncio
import json

from a2a.helpers import get_message_text, new_text_message
from a2a.server.agent_execution import RequestContext
from a2a.server.context import ServerCallContext
from a2a.server.events import Event, EventQueue
from a2a.types import Message, Role, SendMessageRequest

from reviewer.contracts import ReviewResult
from reviewer.executor import ReviewExecutor
from reviewer.model import ModelReviewer
from reviewer.review import review
from reviewer.tests.support import make_request


class RecordingQueue(EventQueue):
    """A queue double that records what the executor enqueues."""

    def __init__(self) -> None:
        self.events: list[Event] = []

    async def enqueue_event(self, event: Event) -> None:
        self.events.append(event)


class StaticModel:
    """A model double returning a fixed result or raising a fixed error."""

    def __init__(self, result: ReviewResult | None = None, error: Exception | None = None) -> None:
        self.result = result or ReviewResult(summary="Model says hi")
        self.error = error

    def review(self, system: str, user: str) -> ReviewResult:
        if self.error is not None:
            raise self.error
        return self.result


def _execute(payload: str, model: ModelReviewer | None = None) -> list[Event]:
    message = new_text_message(payload, role=Role.ROLE_USER)
    context = RequestContext(
        call_context=ServerCallContext(),
        request=SendMessageRequest(message=message),
    )
    queue = RecordingQueue()
    executor = ReviewExecutor(model=model)
    asyncio.run(executor.execute(context, queue))
    return queue.events


def _only_agent_message(events: list[Event]) -> Message:
    assert len(events) == 1
    message = events[0]
    assert isinstance(message, Message)
    assert message.role == Role.ROLE_AGENT
    return message


def test_valid_request_enqueues_one_agent_review_message() -> None:
    events = _execute(make_request().model_dump_json())

    message = _only_agent_message(events)
    result = ReviewResult.model_validate_json(get_message_text(message))
    assert result == review(make_request())


def test_invalid_json_returns_an_error_text_instead_of_raising() -> None:
    message = _only_agent_message(_execute("{not json"))
    text = get_message_text(message)

    assert text.startswith("review unavailable: invalid review.v1 request:")
    assert "Invalid JSON" in text


def test_missing_required_fields_are_reported() -> None:
    message = _only_agent_message(_execute('{"contract": "review.v1"}'))
    text = get_message_text(message)

    assert text.startswith("review unavailable: invalid review.v1 request:")
    assert "curriculum" in text


def test_out_of_range_grade_is_reported() -> None:
    payload = json.loads(make_request().model_dump_json())
    payload["grade"] = 9

    message = _only_agent_message(_execute(json.dumps(payload)))
    text = get_message_text(message)

    assert text.startswith("review unavailable: invalid review.v1 request:")
    assert "grade" in text


def test_wrong_contract_is_reported() -> None:
    payload = json.loads(make_request().model_dump_json())
    payload["contract"] = "review.v0"

    message = _only_agent_message(_execute(json.dumps(payload)))
    text = get_message_text(message)

    assert text.startswith("review unavailable: invalid review.v1 request:")
    assert "contract" in text


def test_hidden_material_in_the_request_is_rejected() -> None:
    payload = json.loads(make_request().model_dump_json())
    payload["assessment"] = {"cases": ["hidden"]}

    message = _only_agent_message(_execute(json.dumps(payload)))
    text = get_message_text(message)

    assert text.startswith("review unavailable: invalid review.v1 request:")
    assert "assessment" in text


def test_empty_input_returns_an_error_text() -> None:
    message = _only_agent_message(_execute(""))

    assert get_message_text(message) == "review unavailable: the request is empty"


def test_a_configured_model_supplies_the_prose() -> None:
    message = _only_agent_message(_execute(make_request().model_dump_json(), StaticModel()))
    result = ReviewResult.model_validate_json(get_message_text(message))

    assert result.summary == "Model says hi"


def test_model_failure_returns_a_review_unavailable_text() -> None:
    model = StaticModel(error=RuntimeError("endpoint down"))

    message = _only_agent_message(_execute(make_request().model_dump_json(), model))
    text = get_message_text(message)

    assert text.startswith("review unavailable: the model reviewer failed:")
    assert "endpoint down" in text


def test_unexpected_reviewer_bug_returns_an_error_text(monkeypatch) -> None:
    import reviewer.executor as executor_module

    def boom(request: object, model: object) -> ReviewResult:
        raise RuntimeError("boom")

    monkeypatch.setattr(executor_module, "review", boom)

    message = _only_agent_message(_execute(make_request().model_dump_json()))
    text = get_message_text(message)

    assert text.startswith("review unavailable: the reviewer failed:")
    assert "boom" in text


def test_cancel_is_a_no_op() -> None:
    message = new_text_message("{}", role=Role.ROLE_USER)
    context = RequestContext(
        call_context=ServerCallContext(),
        request=SendMessageRequest(message=message),
    )
    queue = RecordingQueue()

    asyncio.run(ReviewExecutor().cancel(context, queue))

    assert queue.events == []
