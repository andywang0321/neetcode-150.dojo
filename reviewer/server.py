"""Run the NeetCode 150 reviewer.

    uv run python -m reviewer.server

It serves the agent card and the A2A JSON-RPC endpoint on 127.0.0.1:8766. The engine
discovers the card at `/.well-known/agent-card.json`; dojo never spawns the agent, so
keep this process running for enrollment and review. Stop it with Ctrl-C.
"""

import uvicorn

from reviewer.app import build_app
from reviewer.card import CARD_URL
from reviewer.model import model_from_env

HOST = "127.0.0.1"
PORT = 8766


def main() -> None:
    """Serve the app with uvicorn until interrupted."""
    model = model_from_env()
    mode = f"model {model.settings.model}" if model is not None else "deterministic, no model key"
    print(f"NeetCode 150 reviewer listening on {CARD_URL} ({mode})")
    uvicorn.run(build_app(model=model), host=HOST, port=PORT)


if __name__ == "__main__":
    main()
