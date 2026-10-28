"""The optional OpenAI-compatible model path.

The reviewer is useful with no key at all: the deterministic rubric is the default body.
When `DOJO_REVIEWER_API_KEY` (or `OPENAI_API_KEY`) is set, the server also asks a model
for the prose, grounded in the same context. The model never sees hidden material and its
`quality` is ignored; the rubric owns the score. A transport failure raises
`ModelUnavailable`, which the executor turns into a `review unavailable:` text instead of
a crash. Tests inject a fake transport, so the suite is offline and key-free.
"""

import json
import os
import urllib.error
import urllib.request
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Protocol

from reviewer.contracts import ReviewResult

DEFAULT_BASE_URL = "https://api.openai.com/v1"
DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_TIMEOUT_SECONDS = 60.0
_MAX_SUMMARY = 2_000
_MAX_ITEM = 500
_MAX_ITEMS = 8


class ModelUnavailable(Exception):
    """The configured model endpoint could not produce a usable review."""


class ModelReviewer(Protocol):
    """The one model operation the reviewer needs."""

    def review(self, system: str, user: str) -> ReviewResult: ...


class JsonTransport(Protocol):
    """A POST that returns the response body as text; tests replace this."""

    def __call__(
        self, url: str, headers: Mapping[str, str], body: bytes, timeout: float
    ) -> str: ...


@dataclass(frozen=True, slots=True)
class ModelSettings:
    """The provider configuration, resolved once at startup."""

    base_url: str
    model: str
    api_key: str
    timeout_seconds: float

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> ModelSettings | None:
        """Read the provider/key settings; `None` means deterministic-only mode."""
        values = os.environ if env is None else env
        api_key = values.get("DOJO_REVIEWER_API_KEY") or values.get("OPENAI_API_KEY")
        if not api_key:
            return None
        base_url = (
            values.get("DOJO_REVIEWER_BASE_URL")
            or values.get("OPENAI_BASE_URL")
            or DEFAULT_BASE_URL
        ).rstrip("/")
        model = values.get("DOJO_REVIEWER_MODEL") or DEFAULT_MODEL
        return cls(
            base_url=base_url,
            model=model,
            api_key=api_key,
            timeout_seconds=_timeout(values.get("DOJO_REVIEWER_TIMEOUT_SECONDS")),
        )


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
        payload = {
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
        try:
            raw = self._transport(
                url, headers, json.dumps(payload).encode(), self._settings.timeout_seconds
            )
        except ModelUnavailable:
            raise
        except Exception as error:
            raise ModelUnavailable(f"the model endpoint failed: {_reason(error)}") from error
        return parse_review(_content(raw))


def model_from_env(env: Mapping[str, str] | None = None) -> OpenAICompatibleReviewer | None:
    """Build the configured model reviewer, or `None` for deterministic-only mode."""
    settings = ModelSettings.from_env(env)
    return None if settings is None else OpenAICompatibleReviewer(settings)


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


def _content(raw: str) -> str:
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as error:
        raise ModelUnavailable("the model endpoint returned non-JSON") from error
    if not isinstance(data, dict):
        raise ModelUnavailable("the model endpoint returned a non-object response")
    choices = data.get("choices")
    if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
        raise ModelUnavailable("the model endpoint returned no choices")
    message = choices[0].get("message")
    content = message.get("content") if isinstance(message, dict) else None
    if not isinstance(content, str) or not content.strip():
        raise ModelUnavailable("the model endpoint returned an empty message")
    return content


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


def _timeout(value: str | None) -> float:
    try:
        timeout = float(value) if value is not None else DEFAULT_TIMEOUT_SECONDS
    except ValueError:
        return DEFAULT_TIMEOUT_SECONDS
    return timeout if timeout > 0 else DEFAULT_TIMEOUT_SECONDS


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
