"""Run the NeetCode 150 reviewer.

    uv run python -m reviewer.server

It serves the agent card and the A2A JSON-RPC endpoint on 127.0.0.1:8766. The engine
discovers the card at `/.well-known/agent-card.json`; dojo never spawns the agent, so
keep this process running for enrollment and review. Stop it with Ctrl-C.

The optional model is resolved once at startup from the one dojo `settings.toml` and
`DOJO_API_KEY`. A missing key/config/model keeps the deterministic review; a malformed
settings file is reported and also leaves the reviewer deterministic.
"""

import uvicorn

from reviewer.app import build_app
from reviewer.card import CARD_URL
from reviewer.config import ConfigError
from reviewer.model import AnthropicReviewer, OpenAICompatibleReviewer, model_from_environment

HOST = "127.0.0.1"
PORT = 8766


def main() -> None:
    """Serve the app with uvicorn until interrupted."""
    model, mode = _startup_model()
    print(f"NeetCode 150 reviewer listening on {CARD_URL} ({mode})")
    uvicorn.run(build_app(model=model), host=HOST, port=PORT)


def _startup_model() -> tuple[OpenAICompatibleReviewer | AnthropicReviewer | None, str]:
    """Resolve the model and describe it; a broken config never stops the reviewer."""
    try:
        model = model_from_environment()
    except ConfigError as error:
        return None, f"deterministic, configuration error: {error}"
    if model is None:
        return None, "deterministic, no dojo model configured"
    settings = model.settings
    return model, f"model {settings.provider}/{settings.model}"


if __name__ == "__main__":
    main()
