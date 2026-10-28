"""The agent card is the enrollment contract."""

from reviewer import server
from reviewer.card import CARD_URL, SKILL_ID, VERSION, build_agent_card


def test_card_has_one_jsonrpc_interface_at_the_manifest_url() -> None:
    card = build_agent_card()

    assert card.name == "NeetCode 150 reviewer"
    assert card.version == VERSION == "0.1.0"
    assert card.default_input_modes == ["application/json"]
    assert card.default_output_modes == ["application/json"]
    assert card.capabilities.streaming is False
    assert len(card.supported_interfaces) == 1

    interface = card.supported_interfaces[0]
    assert interface.protocol_binding == "JSONRPC"
    assert interface.protocol_version == "1.0"
    assert interface.url == "http://127.0.0.1:8766/"


def test_card_has_exactly_one_review_skill() -> None:
    card = build_agent_card()

    assert [skill.id for skill in card.skills] == [SKILL_ID] == ["review"]
    skill = card.skills[0]
    assert skill.tags == ["review", "neetcode", "algorithms"]
    assert skill.input_modes == ["application/json"]
    assert skill.output_modes == ["application/json"]
    assert "advisory" in card.description
    assert "ReviewResult" in skill.description


def test_server_serves_the_card_at_the_manifest_url() -> None:
    assert server.HOST == "127.0.0.1"
    assert server.PORT == 8766
    assert f"http://{server.HOST}:{server.PORT}/" == CARD_URL
