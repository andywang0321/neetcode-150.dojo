"""The agent card the NeetCode reviewer publishes.

The card is the discovery contract: `dojo enroll` reads it at
`/.well-known/agent-card.json` and checks that the `review` skill exists before it sends
a `review.v1` request. The URL must match P5-B's manifest:

    [agents.reviewer]
    url = "http://127.0.0.1:8766/"
    skill = "review"
"""

from a2a.types import AgentCapabilities, AgentCard, AgentInterface, AgentSkill

CARD_URL = "http://127.0.0.1:8766/"
SKILL_ID = "review"
VERSION = "0.1.0"
_JSON = "application/json"


def build_agent_card() -> AgentCard:
    """Build the public card: one JSON-RPC 1.0 interface and one `review` skill."""
    return AgentCard(
        name="NeetCode 150 reviewer",
        description=(
            "The NeetCode 150 dojo post-solve reviewer. It reads a review.v1 request "
            "(statement, submitted files, evaluator evidence, grade and claims) and "
            "returns an advisory ReviewResult. It never changes the recorded grade."
        ),
        version=VERSION,
        supported_interfaces=[
            AgentInterface(
                protocol_binding="JSONRPC",
                protocol_version="1.0",
                url=CARD_URL,
            )
        ],
        default_input_modes=[_JSON],
        default_output_modes=[_JSON],
        capabilities=AgentCapabilities(streaming=False),
        skills=[
            AgentSkill(
                id=SKILL_ID,
                name="Review a NeetCode submission",
                description=(
                    "Critique a graded NeetCode 150 submission against the pattern family, "
                    "the submitted code, the evaluator evidence and the student's claims. "
                    "Returns ReviewResult JSON: summary, strengths, improvements, "
                    "next_steps and an advisory quality score."
                ),
                tags=["review", "neetcode", "algorithms"],
                input_modes=[_JSON],
                output_modes=[_JSON],
            )
        ],
    )
