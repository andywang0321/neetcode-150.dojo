"""The optional model path, configured by the engine's one dojo settings file.

The reviewer is useful with no key at all: the deterministic rubric is the default body.
When `DOJO_API_KEY` is set and `$DOJO_CONFIG_DIR/settings.toml` names a provider and a
model, the server also asks that model for the prose, grounded in the same context. The
reviewer has no key, provider or model setting of its own: the one dojo key, `[llm]` and
the curriculum's reviewer override are the only sources. The model never sees hidden
material and its `quality` is ignored; the rubric owns the score. A transport failure
raises `ModelUnavailable`, which the executor turns into a `review unavailable:` text
instead of a crash. Tests inject a fake transport, so the suite is offline and key-free.
"""

import json
import os
import urllib.error
import urllib.request
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Protocol

from reviewer.config import DEFAULT_PROVIDER, ConfigError, DojoConfig, load_config
from reviewer.config import config_path as dojo_config_path
from reviewer.contracts import ReviewResult

DEFAULT_TIMEOUT_SECONDS = 60.0
MOCK_PROVIDER = "mock"
ANTHROPIC_VERSION = "2023-06-01"
_ANTHROPIC_MAX_TOKENS = 4096
_MAX_SUMMARY = 2_000
_MAX_ITEM = 500
_MAX_ITEMS = 8

type Wire = Literal["openai", "anthropic"]


class ModelUnavailable(Exception):
    """The configured model endpoint could not produce a usable review."""


class ModelConfigError(ConfigError):
    """The dojo settings name an LLM the reviewer cannot use."""


class ModelReviewer(Protocol):
    """The one model operation the reviewer needs."""

    def review(self, system: str, user: str) -> ReviewResult: ...


class JsonTransport(Protocol):
    """A POST that returns the response body as text; tests replace this."""

    def __call__(
        self, url: str, headers: Mapping[str, str], body: bytes, timeout: float
    ) -> str: ...


@dataclass(frozen=True, slots=True)
class Provider:
    """A dojo provider name, its wire shape, its default host and its default model."""

    name: str
    wire: Wire
    base_url: str
    default_model: str


PROVIDERS: Mapping[str, Provider] = {
    "deepseek": Provider(
        name="deepseek",
        wire="openai",
        base_url="https://api.deepseek.com",
        default_model="deepseek-chat",
    ),
    "openai": Provider(
        name="openai",
        wire="openai",
        base_url="https://api.openai.com/v1",
        default_model="gpt-4.1-mini",
    ),
    "anthropic": Provider(
        name="anthropic",
        wire="anthropic",
        base_url="https://api.anthropic.com",
        default_model="claude-sonnet-4-5",
    ),
}


@dataclass(frozen=True, slots=True)
class ModelSettings:
    """The provider configuration, resolved once at startup from the dojo settings."""

    provider: str
    base_url: str
    model: str
    api_key: str
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS

    def __post_init__(self) -> None:
        if self.provider not in PROVIDERS:
            known = ", ".join(sorted((*PROVIDERS, MOCK_PROVIDER)))
            raise ModelConfigError(f"unknown LLM provider {self.provider!r}; choose: {known}")

    @property
    def wire(self) -> Wire:
        """The wire protocol the provider speaks."""
        return PROVIDERS[self.provider].wire


class OpenAICompatibleReviewer:
    """Ask one chat-completions endpoint for a ReviewResult JSON."""

    def __init__(self, settings: ModelSettings, transport: JsonTransport | None = None) -> None:
        self._settings = settings
        self._transport = transport or _urllib_transport

    @property
    def settings(self) -> ModelSettings:
        """Expose the resolved settings for the README and the startup line."""
        return self._settings

    def review(self, system: str, user: str) -> ReviewResult:
        """Call the endpoint once and parse its JSON; failures are `ModelUnavailable`."""
        payload: dict[str, object] = {
            "model": self._settings.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0,
        }
        headers = {
            "Authorization": f"Bearer {self._settings.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        url = f"{self._settings.base_url}/chat/completions"
        raw = _post(self._transport, url, headers, payload, self._settings.timeout_seconds)
        return parse_review(_openai_content(raw))


class AnthropicReviewer:
    """Ask one Anthropic messages endpoint for a ReviewResult JSON."""

    def __init__(self, settings: ModelSettings, transport: JsonTransport | None = None) -> None:
        self._settings = settings
        self._transport = transport or _urllib_transport

    @property
    def settings(self) -> ModelSettings:
        """Expose the resolved settings for the README and the startup line."""
        return self._settings

    def review(self, system: str, user: str) -> ReviewResult:
        """Call the endpoint once and parse its JSON; failures are `ModelUnavailable`."""
        payload: dict[str, object] = {
            "model": self._settings.model,
            "system": system,
            "messages": [{"role": "user", "content": user}],
            "max_tokens": _ANTHROPIC_MAX_TOKENS,
            "temperature": 0,
        }
        headers = {
            "x-api-key": self._settings.api_key,
            "anthropic-version": ANTHROPIC_VERSION,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        url = f"{self._settings.base_url}/v1/messages"
        raw = _post(self._transport, url, headers, payload, self._settings.timeout_seconds)
        return parse_review(_anthropic_content(raw))


type ModelClient = OpenAICompatibleReviewer | AnthropicReviewer


def model_from_environment(
    env: Mapping[str, str] | None = None,
    *,
    config_file: Path | None = None,
) -> ModelClient | None:
    """Build the configured model reviewer, or `None` for deterministic-only mode.

    The only key source is `DOJO_API_KEY`. The only configuration source is the one dojo
    `settings.toml`; the provider's default model fills a missing `[llm].model`, exactly
    as it does in the engine. With no key, no file or `provider = "mock"`, no model is
    built and the deterministic review is the answer. Malformed TOML or an unknown
    provider is a `ConfigError` the entry point reports before serving.
    """
    values = os.environ if env is None else env
    api_key = values.get("DOJO_API_KEY", "").strip()
    if not api_key:
        return None
    config = load_config(config_file or dojo_config_path(values))
    if config is None:
        return None
    settings = _model_settings(config, api_key)
    if settings is None:
        return None
    if settings.wire == "anthropic":
        return AnthropicReviewer(settings)
    return OpenAICompatibleReviewer(settings)


def _model_settings(config: DojoConfig, api_key: str) -> ModelSettings | None:
    provider_name = (config.provider or "").strip().lower() or DEFAULT_PROVIDER
    if provider_name == MOCK_PROVIDER:
        return None
    provider = PROVIDERS.get(provider_name)
    if provider is None:
        known = ", ".join(sorted((*PROVIDERS, MOCK_PROVIDER)))
        raise ModelConfigError(f"unknown [llm].provider {provider_name!r}; choose one of: {known}")
    model = (
        (config.reviewer_model or "").strip()
        or (config.model or "").strip()
        or provider.default_model
    )
    base_url = (config.base_url or provider.base_url).strip().rstrip("/")
    if not base_url:
        raise ModelConfigError("[llm].base_url must be a non-empty string")
    return ModelSettings(
        provider=provider.name,
        base_url=base_url,
        model=model,
        api_key=api_key,
    )


def parse_review(text: str) -> ReviewResult:
    """Parse a model's ReviewResult JSON, tolerating a Markdown fence and extra keys."""
    data = _json_object(text)
    summary = _text(data.get("summary"), _MAX_SUMMARY)
    if not summary:
        raise ModelUnavailable("the model returned no summary")
    return ReviewResult(
        summary=summary,
        strengths=_items(data.get("strengths")),
        improvements=_items(data.get("improvements")),
        next_steps=_items(data.get("next_steps")),
        quality=None,
    )


def _post(
    transport: JsonTransport,
    url: str,
    headers: Mapping[str, str],
    payload: Mapping[str, object],
    timeout: float,
) -> str:
    try:
        return transport(url, headers, json.dumps(payload).encode(), timeout)
    except ModelUnavailable:
        raise
    except Exception as error:
        raise ModelUnavailable(f"the model endpoint failed: {_reason(error)}") from error


def _openai_content(raw: str) -> str:
    data = _response_object(raw)
    choices = data.get("choices")
    if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
        raise ModelUnavailable("the model endpoint returned no choices")
    message = choices[0].get("message")
    content = message.get("content") if isinstance(message, dict) else None
    if not isinstance(content, str) or not content.strip():
        raise ModelUnavailable("the model endpoint returned an empty message")
    return content


def _anthropic_content(raw: str) -> str:
    data = _response_object(raw)
    blocks = data.get("content")
    if not isinstance(blocks, list):
        raise ModelUnavailable("the model endpoint returned no content blocks")
    parts = (
        block.get("text")
        for block in blocks
        if isinstance(block, dict) and block.get("type") == "text"
    )
    text = "".join(part for part in parts if isinstance(part, str))
    if not text.strip():
        raise ModelUnavailable("the model endpoint returned an empty message")
    return text


def _response_object(raw: str) -> dict[str, object]:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as error:
        raise ModelUnavailable("the model endpoint returned non-JSON") from error
    if not isinstance(data, dict):
        raise ModelUnavailable("the model endpoint returned a non-object response")
    return data


def _json_object(text: str) -> dict[str, object]:
    stripped = _unfence(text.strip())
    try:
        data = json.loads(stripped)
    except json.JSONDecodeError as error:
        raise ModelUnavailable("the model returned invalid JSON") from error
    if not isinstance(data, dict):
        raise ModelUnavailable("the model returned JSON that is not an object")
    return data


def _unfence(text: str) -> str:
    if not text.startswith("```"):
        return text
    lines = text.splitlines()
    if lines and lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    return "\n".join(lines)


def _text(value: object, limit: int) -> str:
    if not isinstance(value, str):
        return ""
    return value.strip()[:limit]


def _items(value: object) -> tuple[str, ...]:
    if isinstance(value, str):
        value = [value]
    if not isinstance(value, list):
        return ()
    items = (_text(item, _MAX_ITEM) for item in value)
    return tuple(item for item in items if item)[:_MAX_ITEMS]


def _urllib_transport(url: str, headers: Mapping[str, str], body: bytes, timeout: float) -> str:
    request = urllib.request.Request(url, data=body, headers=dict(headers), method="POST")
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        raise ModelUnavailable(f"the model endpoint returned HTTP {error.code}") from error
    except urllib.error.URLError as error:
        raise ModelUnavailable(f"the model endpoint is unreachable: {error.reason}") from error
    except TimeoutError as error:
        raise ModelUnavailable("the model endpoint timed out") from error


def _reason(error: Exception) -> str:
    return str(error) or type(error).__name__
