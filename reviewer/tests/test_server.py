"""The real Starlette app over an in-process ASGI transport and the official client.

Every request stays inside the process: `httpx.ASGITransport` calls the app directly, so
the suite needs no port and no network. The model is either absent (deterministic) or a
recording double.
"""

import asyncio

import httpx
from a2a.client import A2ACardResolver, Client, ClientConfig, create_client
from a2a.helpers import get_message_text, new_text_message
from a2a.types import Role, SendMessageRequest, StreamResponse
from google.protobuf import json_format
from starlette.applications import Starlette

from reviewer import server
from reviewer.app import build_app
from reviewer.card import CARD_URL, SKILL_ID
from reviewer.contracts import ReviewResult
from reviewer.review import review
from reviewer.tests.support import make_request

BASE_URL = "http://127.0.0.1:8766"


class StaticModel:
    """A model double for the app-level wiring test."""

    def review(self, system: str, user: str) -> ReviewResult:
        return ReviewResult(summary="Model says hi")


def _http_client(app: Starlette | None = None) -> httpx.AsyncClient:
    return httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app or build_app()),
        base_url=BASE_URL,
    )


async def _send(client: Client, payload: str) -> list[StreamResponse]:
    """Send one review.v1 user message and collect the client's stream responses."""
    request = SendMessageRequest(message=new_text_message(payload, role=Role.ROLE_USER))
    return [chunk async for chunk in client.send_message(request)]


def test_card_is_served_at_the_well_known_path() -> None:
    async def scenario() -> httpx.Response:
        async with _http_client() as http:
            return await http.get("/.well-known/agent-card.json")

    response = asyncio.run(scenario())
    assert response.status_code == 200

    card = response.json()
    assert card["name"] == "NeetCode 150 reviewer"
    assert card["version"] == "0.1.0"
    assert card["defaultInputModes"] == ["application/json"]
    assert card["defaultOutputModes"] == ["application/json"]
    assert card["capabilities"]["streaming"] is False

    interface = card["supportedInterfaces"][0]
    assert interface["protocolBinding"] == "JSONRPC"
    assert interface["protocolVersion"] == "1.0"
    assert interface["url"] == CARD_URL

    assert [skill["id"] for skill in card["skills"]] == [SKILL_ID]
    skill = card["skills"][0]
    assert skill["tags"] == ["review", "neetcode", "algorithms"]
    assert skill["inputModes"] == ["application/json"]
    assert skill["outputModes"] == ["application/json"]


def test_jsonrpc_route_accepts_a_send_message() -> None:
    async def scenario() -> httpx.Response:
        async with _http_client() as http:
            request = SendMessageRequest(
                message=new_text_message(make_request().model_dump_json(), role=Role.ROLE_USER)
            )
            return await http.post(
                "/",
                headers={"A2A-Version": "1.0"},
                json={
                    "jsonrpc": "2.0",
                    "id": "route-test",
                    "method": "SendMessage",
                    "params": json_format.MessageToDict(request),
                },
            )

    response = asyncio.run(scenario())
    assert response.status_code == 200

    body = response.json()
    assert body["jsonrpc"] == "2.0"
    assert body["id"] == "route-test"
    message = body["result"]["message"]
    assert message["role"] == "ROLE_AGENT"
    result = ReviewResult.model_validate_json(message["parts"][0]["text"])
    assert result == review(make_request())


def test_official_client_discovers_the_skill_and_returns_a_review() -> None:
    async def scenario() -> tuple[set[str], list[StreamResponse]]:
        async with _http_client() as http:
            card = await A2ACardResolver(http, CARD_URL).get_agent_card()
            client = await create_client(card, ClientConfig(streaming=False, httpx_client=http))
            try:
                chunks = await _send(client, make_request().model_dump_json())
            finally:
                await client.close()
        return {skill.id for skill in card.skills}, chunks

    skills, chunks = asyncio.run(scenario())
    assert SKILL_ID in skills
    assert len(chunks) == 1

    chunk = chunks[0]
    assert chunk.HasField("message")
    assert not chunk.HasField("task")
    assert chunk.message.role == Role.ROLE_AGENT
    result = ReviewResult.model_validate_json(get_message_text(chunk.message))
    assert result == review(make_request())


def test_malformed_request_returns_an_unavailable_text_over_the_route() -> None:
    async def scenario() -> str:
        async with _http_client() as http:
            card = await A2ACardResolver(http, CARD_URL).get_agent_card()
            client = await create_client(card, ClientConfig(streaming=False, httpx_client=http))
            try:
                chunks = await _send(client, "not a review request")
            finally:
                await client.close()
        return get_message_text(chunks[0].message)

    text = asyncio.run(scenario())

    assert text.startswith("review unavailable: invalid review.v1 request:")


def test_a_configured_model_is_wired_through_the_app() -> None:
    async def scenario() -> str:
        async with _http_client(build_app(model=StaticModel())) as http:
            card = await A2ACardResolver(http, CARD_URL).get_agent_card()
            client = await create_client(card, ClientConfig(streaming=False, httpx_client=http))
            try:
                chunks = await _send(client, make_request().model_dump_json())
            finally:
                await client.close()
        return get_message_text(chunks[0].message)

    result = ReviewResult.model_validate_json(asyncio.run(scenario()))

    assert result.summary == "Model says hi"


def test_server_serves_the_card_at_the_documented_port() -> None:
    assert server.HOST == "127.0.0.1"
    assert server.PORT == 8766
    assert f"http://{server.HOST}:{server.PORT}/" == CARD_URL
