"""The optional model client is configured by the one dojo settings file and key."""

import json
from collections.abc import Mapping
from pathlib import Path

import pytest

import reviewer.model as model_module
from reviewer.config import ConfigError
from reviewer.model import (
    ANTHROPIC_VERSION,
    DEFAULT_TIMEOUT_SECONDS,
    AnthropicReviewer,
    ModelConfigError,
    ModelSettings,
    ModelUnavailable,
    OpenAICompatibleReviewer,
    model_from_environment,
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


def _write_settings(tmp_path: Path, source: str) -> Path:
    path = tmp_path / "settings.toml"
    path.write_text(source, encoding="utf-8")
    return path


def _env(tmp_path: Path, *, key: str = "dojo-key") -> dict[str, str]:
    return {"DOJO_API_KEY": key, "DOJO_CONFIG_DIR": str(tmp_path)}


def _settings(**overrides: object) -> ModelSettings:
    values: dict[str, object] = {
        "provider": "openai",
        "base_url": "http://model.local/v1",
        "model": "test-model",
        "api_key": "secret",
        "timeout_seconds": 5.0,
    }
    values.update(overrides)
    return ModelSettings(
        provider=str(values["provider"]),
        base_url=str(values["base_url"]),
        model=str(values["model"]),
        api_key=str(values["api_key"]),
        timeout_seconds=float(values["timeout_seconds"]),
    )


def _envelope(content: str) -> str:
    return json.dumps({"choices": [{"message": {"content": content}}]})


def _anthropic_envelope(content: str) -> str:
    return json.dumps({"content": [{"type": "text", "text": content}]})


def _review_json(**overrides: object) -> str:
    values: dict[str, object] = {
        "summary": "Model summary",
        "strengths": ["Uses a hash map well."],
        "improvements": ["Add an empty-input guard."],
        "next_steps": ["Try duplicate values."],
    }
    values.update(overrides)
    return json.dumps(values)


def test_no_key_means_deterministic_mode(tmp_path: Path) -> None:
    _write_settings(
        tmp_path,
        '[llm]\nprovider = "openai"\nmodel = "config-model"\n',
    )

    assert model_from_environment({}) is None
    assert model_from_environment({"DOJO_CONFIG_DIR": str(tmp_path)}) is None


def test_config_dir_settings_select_the_provider_model_and_base_url(tmp_path: Path) -> None:
    _write_settings(
        tmp_path,
        """
[llm]
provider = "openai"
model = "config-model"
base_url = "http://localhost:8000/v1/"
""",
    )

    model = model_from_environment(_env(tmp_path))

    assert isinstance(model, OpenAICompatibleReviewer)
    assert model.settings == ModelSettings(
        provider="openai",
        base_url="http://localhost:8000/v1",
        model="config-model",
        api_key="dojo-key",
        timeout_seconds=DEFAULT_TIMEOUT_SECONDS,
    )


@pytest.mark.parametrize(
    ("provider", "base_url", "default_model"),
    [
        ("deepseek", "https://api.deepseek.com", "deepseek-chat"),
        ("openai", "https://api.openai.com/v1", "gpt-4.1-mini"),
        ("anthropic", "https://api.anthropic.com", "claude-sonnet-4-5"),
    ],
)
def test_provider_defaults_its_host_model_and_wire(
    tmp_path: Path, provider: str, base_url: str, default_model: str
) -> None:
    _write_settings(tmp_path, f'[llm]\nprovider = "{provider}"\n')

    model = model_from_environment(_env(tmp_path))

    assert model is not None
    assert model.settings.provider == provider
    assert model.settings.base_url == base_url
    assert model.settings.model == default_model
    expected = AnthropicReviewer if provider == "anthropic" else OpenAICompatibleReviewer
    assert isinstance(model, expected)


def test_curriculum_reviewer_model_overrides_the_llm_model(tmp_path: Path) -> None:
    _write_settings(
        tmp_path,
        """
[llm]
provider = "openai"
model = "base-model"

[curricula.neetcode-150.reviewer]
model = "review-model"
""",
    )

    model = model_from_environment(_env(tmp_path))

    assert model is not None
    assert model.settings.model == "review-model"


def test_a_missing_config_is_deterministic(tmp_path: Path) -> None:
    assert model_from_environment(_env(tmp_path)) is None


def test_an_empty_settings_file_uses_the_engine_defaults(tmp_path: Path) -> None:
    _write_settings(tmp_path, "")

    model = model_from_environment(_env(tmp_path))

    assert model is not None
    assert model.settings.provider == "deepseek"
    assert model.settings.model == "deepseek-chat"


def test_a_mock_provider_is_deterministic(tmp_path: Path) -> None:
    _write_settings(tmp_path, '[llm]\nprovider = "mock"\nmodel = "mock"\n')

    assert model_from_environment(_env(tmp_path)) is None


def test_old_reviewer_and_provider_key_variables_are_ignored(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _write_settings(
        tmp_path,
        '[llm]\nprovider = "openai"\nmodel = "config-model"\n',
    )
    monkeypatch.delenv("DOJO_API_KEY", raising=False)
    monkeypatch.setenv("DOJO_CONFIG_DIR", str(tmp_path))
    for name in (
        "DOJO_REVIEWER_API_KEY",
        "OPENAI_API_KEY",
        "DEEPSEEK_API_KEY",
        "ANTHROPIC_API_KEY",
    ):
        monkeypatch.setenv(name, "not-a-dojo-key")
    monkeypatch.setenv("OPENAI_BASE_URL", "http://old-openai.local/v1")

    assert model_from_environment() is None


def test_dojo_api_key_and_settings_win_over_the_old_variables(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _write_settings(
        tmp_path,
        """
[llm]
provider = "openai"
model = "config-model"
base_url = "http://config.local/v1"
""",
    )
    monkeypatch.setenv("DOJO_API_KEY", "dojo-key")
    monkeypatch.setenv("DOJO_CONFIG_DIR", str(tmp_path))
    monkeypatch.setenv("DOJO_REVIEWER_API_KEY", "old-reviewer-key")
    monkeypatch.setenv("OPENAI_API_KEY", "old-openai-key")
    monkeypatch.setenv("OPENAI_BASE_URL", "http://old-openai.local/v1")
    monkeypatch.setenv("DOJO_REVIEWER_BASE_URL", "http://old.local/v1")
    monkeypatch.setenv("DOJO_REVIEWER_MODEL", "old-model")
    monkeypatch.setenv("DOJO_REVIEWER_TIMEOUT_SECONDS", "1")

    model = model_from_environment()

    assert model is not None
    assert model.settings.api_key == "dojo-key"
    assert model.settings.base_url == "http://config.local/v1"
    assert model.settings.model == "config-model"
    assert model.settings.timeout_seconds == DEFAULT_TIMEOUT_SECONDS


def test_malformed_settings_is_a_config_error(tmp_path: Path) -> None:
    _write_settings(tmp_path, "[llm\n")

    with pytest.raises(ConfigError, match="invalid TOML"):
        model_from_environment(_env(tmp_path))


def test_unknown_provider_is_a_config_error(tmp_path: Path) -> None:
    _write_settings(tmp_path, '[llm]\nprovider = "unknown"\nmodel = "config-model"\n')

    with pytest.raises(ModelConfigError, match="unknown"):
        model_from_environment(_env(tmp_path))


def test_the_configured_model_path_is_exercised_with_a_mock_transport(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _write_settings(
        tmp_path,
        '[llm]\nprovider = "openai"\nmodel = "config-model"\nbase_url = "http://model.local/v1"\n',
    )
    transport = RecordingTransport(_envelope(_review_json()))
    monkeypatch.setattr(model_module, "_urllib_transport", transport)

    model = model_from_environment(_env(tmp_path))
    assert model is not None
    result = model.review("system rubric", "user context")

    assert result.summary == "Model summary"
    assert len(transport.calls) == 1
    assert transport.calls[0][0] == "http://model.local/v1/chat/completions"


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


def test_review_posts_one_anthropic_messages_request() -> None:
    transport = RecordingTransport(_anthropic_envelope(_review_json()))
    settings = _settings(provider="anthropic", base_url="https://api.anthropic.com")
    reviewer = AnthropicReviewer(settings, transport)

    result = reviewer.review("system rubric", "user context")

    assert result.summary == "Model summary"
    assert result.quality is None

    assert len(transport.calls) == 1
    url, headers, body, timeout = transport.calls[0]
    assert url == "https://api.anthropic.com/v1/messages"
    assert headers["x-api-key"] == "secret"
    assert headers["anthropic-version"] == ANTHROPIC_VERSION
    assert timeout == 5.0
    payload = json.loads(body)
    assert payload["model"] == "test-model"
    assert payload["system"] == "system rubric"
    assert payload["temperature"] == 0
    assert payload["max_tokens"] == 4096
    assert payload["messages"] == [{"role": "user", "content": "user context"}]


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


def test_anthropic_response_without_text_is_model_unavailable() -> None:
    reviewer = AnthropicReviewer(
        _settings(provider="anthropic"),
        RecordingTransport('{"content": [{"type": "tool_use", "input": {}}]}'),
    )

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
