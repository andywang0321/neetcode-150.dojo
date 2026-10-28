"""The A2A executor: one review.v1 message in, one ReviewResult message out.

The executor uses the message-only streaming pattern: it enqueues exactly one
`ROLE_AGENT` text message and no task events. A malformed request never raises; it
returns an explanatory text starting with `review unavailable:`, which the engine treats
as an unavailable review (and stores nothing). A model or tool failure falls back to the
deterministic review; only an unexpected reviewer bug reaches the outer handler.
"""

from a2a.helpers import new_text_message
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.types import Role
from pydantic import ValidationError

from reviewer.contracts import ReviewRequest
from reviewer.model import ModelReviewer
from reviewer.review import ReviewUnavailable, review


class ReviewExecutor(AgentExecutor):
    """Serve the one `review` skill over the message-only A2A pattern."""

    def __init__(self, model: ModelReviewer | None = None) -> None:
        self._model = model

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        try:
            text = _review_text(context.get_user_input(), self._model)
        except ReviewUnavailable as error:
            text = f"review unavailable: {error}"
        except Exception as error:  # a reviewer bug must not take the server down
            text = f"review unavailable: the reviewer failed: {_reason(error)}"
        await event_queue.enqueue_event(new_text_message(text, role=Role.ROLE_AGENT))

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        """One request/response leaves nothing to cancel."""


def _review_text(payload: str, model: ModelReviewer | None) -> str:
    if not payload.strip():
        return "review unavailable: the request is empty"
    try:
        request = ReviewRequest.model_validate_json(payload)
    except ValidationError as error:
        return _invalid_request_text(error)
    return review(request, model).model_dump_json()


def _invalid_request_text(error: ValidationError) -> str:
    problems = "; ".join(_problem(item["loc"], item["msg"]) for item in error.errors()[:3])
    return f"review unavailable: invalid review.v1 request: {problems}"


def _problem(loc: tuple[int | str, ...], message: str) -> str:
    location = ".".join(str(part) for part in loc)
    return f"{location}: {message}" if location else message


def _reason(error: Exception) -> str:
    return str(error) or type(error).__name__
