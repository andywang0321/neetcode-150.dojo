"""The OpenAI-compatible model client is optional, offline-testable and fail-closed."""

import json
from collections.abc import Mapping

import pytest

from reviewer.model import (
    DEFAULT_BASE_URL,
    DEFAULT_MODEL,
    DEFAULT_TIMEOUT_SECONDS,
    ModelSettings,
    ModelUnavailable,
    OpenAICompatibleReviewer,
    model_from_env,
    parse_review,
)


class RecordingTransport:
    """A fake POST: it records the request and returns a canned body."""

    def __init__(self, raw: str) -> None:
        self.raw = raw
        self.calls: list[tuple[str, Mapping[str, str], bytes, float]] = []

    def __call__(self, url: str, headers: Mapping[str, str], body: bytes, timeout: float) -> str:
        self.calls.append((url, headers, body, timeout))
        return self.raw


class FailingTransport:
    """A fake POST that fails before any response exists."""

    def __call__(self, url: str, headers: Mapping[str, str], body: bytes, timeout: float) -> str:
        raise RuntimeError("connection reset")


def _settings(**overrides: object) -> ModelSettings:
    values: dict[str, object] = {
        "base_url": "http://model.local/v1",
        "model": "test-model",
        "api_key": "secret",
        "timeout_seconds": 5.0,
    }
    values.update(overrides)
    return ModelSettings(
        base_url=str(values["base_url"]),
        model=str(values["model"]),
        api_key=str(values["api_key"]),
        timeout_seconds=float(values["timeout_seconds"]),
    )


def _envelope(content: str) -> str:
    return json.dumps({"choices": [{"message": {"content": content}}]})


def _review_json(**overrides: object) -> str:
    values: dict[str, object] = {
        "summary": "Model summary",
        "strengths": ["Uses a hash map well."],
        "improvements": ["Add an empty-input guard."],
        "next_steps": ["Try duplicate values."],
    }
    values.update(overrides)
    return json.dumps(values)


def test_no_key_means_deterministic_mode() -> None:
    assert ModelSettings.from_env({}) is None
    assert model_from_env({}) is None


def test_defaults_and_openai_fallbacks() -> None:
    settings = ModelSettings.from_env({"DOJO_REVIEWER_API_KEY": "key"})

    assert settings == ModelSettings(
        base_url=DEFAULT_BASE_URL,
        model=DEFAULT_MODEL,
        api_key="key",
        timeout_seconds=DEFAULT_TIMEOUT_SECONDS,
    )
    fallback = ModelSettings.from_env(
        {"OPENAI_API_KEY": "openai-key", "OPENAI_BASE_URL": "http://x/v1"}
    )
    assert fallback is not None
    assert fallback.api_key == "openai-key"
    assert fallback.base_url == "http://x/v1"


def test_reviewer_settings_can_be_overridden() -> None:
    settings = ModelSettings.from_env(
        {
            "DOJO_REVIEWER_API_KEY": "key",
            "DOJO_REVIEWER_BASE_URL": "http://localhost:8000/v1/",
            "DOJO_REVIEWER_MODEL": "local-model",
            "DOJO_REVIEWER_TIMEOUT_SECONDS": "12.5",
        }
    )

    assert settings is not None
    assert settings.base_url == "http://localhost:8000/v1"
    assert settings.model == "local-model"
    assert settings.timeout_seconds == 12.5


def test_invalid_timeout_falls_back_to_the_default() -> None:
    for value in ("", "soon", "-1", "0"):
        settings = ModelSettings.from_env(
            {"DOJO_REVIEWER_API_KEY": "key", "DOJO_REVIEWER_TIMEOUT_SECONDS": value}
        )
        assert settings is not None
        assert settings.timeout_seconds == DEFAULT_TIMEOUT_SECONDS


def test_model_from_env_builds_the_client_without_calling_it() -> None:
    reviewer = model_from_env({"DOJO_REVIEWER_API_KEY": "key"})

    assert isinstance(reviewer, OpenAICompatibleReviewer)
    assert reviewer.settings.api_key == "key"


def test_review_posts_one_openai_chat_completions_request() -> None:
    transport = RecordingTransport(_envelope(_review_json()))
    reviewer = OpenAICompatibleReviewer(_settings(), transport)

    result = reviewer.review("system rubric", "user context")

    assert result.summary == "Model summary"
    assert result.strengths == ("Uses a hash map well.",)
    assert result.quality is None

    assert len(transport.calls) == 1
    url, headers, body, timeout = transport.calls[0]
    assert url == "http://model.local/v1/chat/completions"
    assert headers["Authorization"] == "Bearer secret"
    assert headers["Content-Type"] == "application/json"
    assert timeout == 5.0
    payload = json.loads(body)
    assert payload["model"] == "test-model"
    assert payload["temperature"] == 0
    assert payload["messages"] == [
        {"role": "system", "content": "system rubric"},
        {"role": "user", "content": "user context"},
    ]


def test_transport_failure_is_model_unavailable() -> None:
    reviewer = OpenAICompatibleReviewer(_settings(), FailingTransport())

    with pytest.raises(ModelUnavailable, match="model endpoint failed"):
        reviewer.review("system", "user")


def test_non_json_endpoint_response_is_model_unavailable() -> None:
    reviewer = OpenAICompatibleReviewer(_settings(), RecordingTransport("not json"))

    with pytest.raises(ModelUnavailable, match="non-JSON"):
        reviewer.review("system", "user")


def test_response_without_choices_is_model_unavailable() -> None:
    reviewer = OpenAICompatibleReviewer(_settings(), RecordingTransport('{"choices": []}'))

    with pytest.raises(ModelUnavailable, match="no choices"):
        reviewer.review("system", "user")


def test_empty_model_message_is_model_unavailable() -> None:
    reviewer = OpenAICompatibleReviewer(_settings(), RecordingTransport(_envelope("  ")))

    with pytest.raises(ModelUnavailable, match="empty message"):
        reviewer.review("system", "user")


def test_parse_review_accepts_a_markdown_fence_and_ignores_extra_keys() -> None:
    fenced = f"```json\n{_review_json(grade=4, quality=0.99)}\n```"

    result = parse_review(fenced)

    assert result.summary == "Model summary"
    assert result.quality is None
    assert result.improvements == ("Add an empty-input guard.",)


def test_parse_review_accepts_a_bare_string_item() -> None:
    result = parse_review(_review_json(strengths="One strength."))

    assert result.strengths == ("One strength.",)


def test_parse_review_filters_empty_and_non_string_items() -> None:
    result = parse_review(_review_json(strengths=["good", "", 3, "  also good  "]))

    assert result.strengths == ("good", "also good")


def test_parse_review_caps_items_and_summary() -> None:
    result = parse_review(
        _review_json(summary="x" * 3000, strengths=[f"item {i}" for i in range(20)])
    )

    assert result.summary == "x" * 2000
    assert len(result.strengths) == 8


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        ("not json", "invalid JSON"),
        ("[]", "not an object"),
        ('{"strengths": []}', "no summary"),
        ('{"summary": "  "}', "no summary"),
    ],
)
def test_parse_review_rejects_unusable_output(payload: str, message: str) -> None:
    with pytest.raises(ModelUnavailable, match=message):
        parse_review(payload)
