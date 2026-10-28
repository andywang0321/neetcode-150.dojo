"""Build the ASGI application: the agent card plus the JSON-RPC route."""

from a2a.server.agent_execution import AgentExecutor
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes import create_agent_card_routes, create_jsonrpc_routes
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCard
from starlette.applications import Starlette

from reviewer.card import build_agent_card
from reviewer.executor import ReviewExecutor
from reviewer.model import ModelReviewer


def build_app(
    *,
    agent_card: AgentCard | None = None,
    executor: AgentExecutor | None = None,
    model: ModelReviewer | None = None,
) -> Starlette:
    """Build the app; the arguments exist so tests and the server can inject pieces.

    `model=None` means a fully deterministic review. The tests construct the app that
    way (or with a recording fake), so the suite never reads a key or opens a socket.
    The real entry point passes `model_from_environment()`.
    """
    card = agent_card or build_agent_card()
    handler = DefaultRequestHandler(
        agent_executor=executor or ReviewExecutor(model=model),
        task_store=InMemoryTaskStore(),
        agent_card=card,
    )
    routes = [
        *create_agent_card_routes(card),
        *create_jsonrpc_routes(handler, rpc_url="/"),
    ]
    return Starlette(routes=routes)
