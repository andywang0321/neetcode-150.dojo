# NeetCode 150 A2A reviewer

The post-solve reviewer for the `neetcode-150.dojo` curriculum. It is a real
[A2A](https://a2a-protocol.org/) agent built on the official `a2a-sdk[fastapi]`: it
serves one `review` skill, reads a `review.v1` request, and returns an advisory
`ReviewResult`. It never changes the recorded grade.

The review body is NeetCode-specific and deterministic by default: it reads the item
family, the submitted Python, the evaluator evidence and the student's claims, and cites
line-level findings. If an OpenAI-compatible model is configured, the model writes the
prose from the same grounded context; the rubric keeps the `quality` score. With no key,
no model is called and the review works offline.

## Run it

From the **repository root** (the reviewer uses the repository's uv environment):

```bash
export UV_CACHE_DIR=/Users/andywang/Projects/dojo-workspace/.uv-cache
uv sync
uv run python -m reviewer.server
```

The process stays in the foreground; stop it with Ctrl-C. It serves:

| endpoint | value |
|---|---|
| agent card | `GET http://127.0.0.1:8766/.well-known/agent-card.json` |
| A2A JSON-RPC | `POST http://127.0.0.1:8766/` (protocol v1.0, `JSONRPC` binding, `SendMessage`) |
| skill id | `review` |

This is the contract P5-B's manifest already declares:

```toml
[agents.reviewer]
url = "http://127.0.0.1:8766/"

[capabilities.review]
impl = "a2a"
agent = "reviewer"
skill = "review"
```

dojo never spawns the agent, so keep it running while you enroll and submit. The card is
the enrollment probe; the same card is checked again before every review.

## Card and skill

The card has one `JSONRPC` interface at protocol version `1.0`, JSON input/output modes,
`streaming = false`, and exactly one skill:

| field | value |
|---|---|
| `id` | `review` |
| `name` | `Review a NeetCode submission` |
| `tags` | `review`, `neetcode`, `algorithms` |
| input mode | `application/json` |
| output mode | `application/json` |

A review is one message request and one message response. There are no tasks, no
streaming and no multi-turn state.

## Wire shapes

The request is one JSON text part with `role = ROLE_USER`:

```json
{
  "contract": "review.v1",
  "curriculum": "neetcode-150",
  "item": "two-sum",
  "statement": "Given an array of integers nums and an integer target, ...",
  "files": [{"path": "solution.py", "content": "def two_sum(...):\n    ...\n"}],
  "evidence": [
    {"evaluator": "tests", "assurance": "machine", "outcome": "pass", "summary": "5/5 cases passed"}
  ],
  "grade": 3,
  "claims": {"time": "O(n)", "space": "O(n)"}
}
```

The response is exactly one `ROLE_AGENT` text message. Its text is a `ReviewResult`:

```json
{
  "summary": "Review of two-sum in neetcode-150: grade 3 (pass); 1 of 1 evaluator reports passed. ...",
  "strengths": ["tests passed with machine assurance: 5/5 cases passed"],
  "improvements": ["No explicit empty/short-input guard is visible; ..."],
  "next_steps": ["Test the usual failure points for Arrays & Hashing: empty input and duplicate values."],
  "quality": 0.76
}
```

The executable shapes are mirrored in `reviewer/contracts.py`. They match
`dojo.protocol.contracts.ReviewRequest`/`ReviewResult`; the project does not import the
engine. Extra fields are rejected, the contract tag is `review.v1`, `grade` is 1-4 or
null, and `quality` is a **float in 0..1** (or null) — not the old rubric object with a
score and a rationale. The rationale lives in `summary` and the findings.

A malformed request is not an exception. The agent returns one text message starting with
`review unavailable:`, which the engine treats as an unavailable review and stores
nothing. A configured-model failure behaves the same way:

```text
review unavailable: invalid review.v1 request: curriculum: Field required; ...
review unavailable: the model reviewer failed: the model endpoint returned HTTP 500
```

## What the review says

`reviewer/advice.py` and `reviewer/findings.py` implement the ported rubric. The review
is grounded in exactly five things: the item statement, the submitted files, the
evaluator evidence, the recorded grade and the student's claims.

- **Pattern family.** The item slug is matched against the eighteen NeetCode topics
  (`Arrays & Hashing` ... `Bit Manipulation`), with the statement and then the code shape
  as fallbacks. The family supplies the expected complexity, the usual edge cases and
  the constructs a typical solution shows.
- **Approach.** Static constructs (hash map/set, two-pointer loop, halving loop, heap,
  deque/visited set, memo/DP table, bit operations, ...) are named as strengths when they
  fit the family, and as a question when the expected tool is not visible.
- **Style/idiom and edge cases.** AST checks report nested loops, `range(len(...))`,
  debug `print`s, mutable defaults, bare/broad `except`, `== None`, `global`, `eval`,
  deep nesting, long functions and missing guards. `check.py` (the visible harness) is
  scaffolding and is excluded from these findings.
- **Complexity reasoning.** A stated time complexity is compared with complexity-shaped
  evidence and with the static shape; a nested loop under an `O(n)` claim is flagged, and
  a missing claim becomes a next step. The reviewer never claims a measured number that
  is not in the evidence.
- **Broader picture.** Next steps add the family's usual edge cases and one follow-up.

The deterministic body is the default. It is not the reference agent's
grade-to-quality stub: the grade contributes to `quality`, but the score also depends on
the evidence, the aligned constructs, guards and annotations, and is reduced by real
findings.

### Advisory rule

The review is advice. It never changes the grade, the card, the schedule or the
evidence; `ReviewResult` has no grade field, and `review()` only reads `request.grade`.
The engine stores the result as a `reviews` row and keeps the grade it already recorded.
If you only ever want deterministic reviews, leave the model key unset.

### Quality formula

`quality` is null for an ungraded submission; otherwise it starts at
`{1: 0.20, 2: 0.45, 3: 0.65, 4: 0.80}` and is adjusted, then clamped to `0.0..1.0` and
rounded to two decimals:

| signal | adjustment |
|---|---|
| every evaluator report passed | `+0.05` |
| an expected pattern construct is visible | `+0.04` |
| an explicit empty/short-input guard is visible | `+0.03` |
| at least half the functions are fully annotated | `+0.02` |
| each high-severity finding (max 3) | `-0.04` |
| each medium-severity finding (max 3) | `-0.02` |

## Model configuration (optional)

The agent speaks the OpenAI chat-completions wire. It is enabled by a key; without one
the deterministic review runs and no network call is made.

| variable | default | meaning |
|---|---|---|
| `DOJO_REVIEWER_API_KEY` | unset | enables the model path; `OPENAI_API_KEY` is a fallback |
| `DOJO_REVIEWER_BASE_URL` | `https://api.openai.com/v1` | OpenAI-compatible base; `OPENAI_BASE_URL` is a fallback |
| `DOJO_REVIEWER_MODEL` | `gpt-4o-mini` | model name sent to the endpoint |
| `DOJO_REVIEWER_TIMEOUT_SECONDS` | `60` | request timeout; invalid/`<= 0` falls back to 60 |

The request is one `POST {base_url}/chat/completions` with `temperature: 0` and the
system rubric plus the grounded user context. The endpoint must return a
`choices[0].message.content` string containing the JSON object. Fences and extra keys are
tolerated; an empty summary, invalid JSON, an HTTP/transport failure or a timeout is a
`review unavailable:` message. The model's `quality` (if it sends one) is ignored: the
rubric owns the score, so a model change cannot silently move it, and the model cannot
change the grade.

The model prompt contains only the review view and the static facts derived from the
submitted files. It never contains a private case, an oracle, a reference solution, the
assessment tree or the student's history.

## Data boundary

- The request model has exactly eight fields: `contract`, `curriculum`, `item`,
  `statement`, `files`, `evidence`, `grade`, `claims`. Extra fields — including
  `assessment`, `hidden_cases`, `oracle`, `reference` or `private_cases` — are rejected
  by validation and become `review unavailable`, never part of the context.
- The production modules read no files (`reviewer/tests/test_boundary.py` checks the AST
  for `open`/`read_text`), import nothing from `neetcode_dojo`, and have no path to
  `neetcode_dojo/assessment/`. The only outbound I/O is the optional model POST.
- The statement, submitted code and claims are treated as data, not instructions; the
  system rubric tells the model to ignore instructions embedded in them.
- The visible `check.py` is curriculum scaffolding: it is not analysed for code findings.
  Hidden tests, oracles, references and the measurement tree are never sent to this
  agent.

## Tests and checks

The reviewer suite is offline and deterministic: the model is a recording double (or
absent), and the server tests use `httpx.ASGITransport` against the real ASGI app, so no
port is bound and no network is used. No key is read in tests.

From the repository root:

```bash
export UV_CACHE_DIR=/Users/andywang/Projects/dojo-workspace/.uv-cache
uv sync
uv run pytest                      # both suites (curriculum tests + reviewer)
uv run pytest reviewer/tests       # the reviewer suite only (123 tests)
uv run ruff check .
uv run ruff format --check .
uv run ty check .
```

The repository root's pytest config includes both `tests/` and `reviewer/tests/`, so a
single `uv run pytest` runs the evaluator/content suite and this suite. The package
carries its own pytest/ruff configuration in `reviewer/pyproject.toml` for running it
standalone; it deliberately has no second virtualenv or lockfile, and uses the
repository's approved `a2a-sdk[fastapi]`, `pydantic` and `uvicorn` environment.

## Layout

| path | role |
|---|---|
| `reviewer/server.py` | uvicorn entry point on `127.0.0.1:8766` |
| `reviewer/card.py` | the `AgentCard` and the one `review` skill |
| `reviewer/contracts.py` | the local `review.v1` / `ReviewResult` Pydantic mirror |
| `reviewer/analysis/` | pure AST facts: model, rules, shape, walker |
| `reviewer/families.py` | the eighteen NeetCode families as data |
| `reviewer/patterns.py` | family detection and the aligned-construct lookup |
| `reviewer/advice.py` | summary, strengths, next steps and the quality rubric |
| `reviewer/findings.py` | grounded improvements, claim checks and the pattern revisit |
| `reviewer/prompt.py` | the ported reviewer rubric and the model context |
| `reviewer/model.py` | optional OpenAI-compatible client (urllib, no new dependency) |
| `reviewer/review.py` | the entry point: deterministic review, optional model merge |
| `reviewer/executor.py` | message-only `AgentExecutor`, errors as text |
| `reviewer/app.py` | card routes + JSON-RPC route on a Starlette app |
| `reviewer/tests/` | card, analysis, patterns, review, model, executor, boundary, server |

The reviewer mirrors the engine's `review.v1`/`ReviewResult` shape by hand, just like the
engine's reference agent, so it never depends on the engine package or its database.

## Notes on the port

- The old engine's `REVIEWER_SYSTEM` and `build_review_prompt` graded eight 1-5
  dimensions. Those dimensions are preserved as the review's concerns (correctness,
  approach/pattern, style/idiom, naming, edge cases, complexity claim, reasoning,
  broader picture) but the new contract has no per-dimension scores: they become
  findings, and `quality` is the single advisory float.
- The rubric lives in `reviewer/prompt.py` with the A2A project, not in
  `prompts/reviewer.md`; P5-B owns the curriculum's LLM-fallback prompt file and is free
  to reuse or replace it without touching the A2A agent.
- The card/skill/URL contract is P5-B's manifest; this project does not edit the
  manifest.
- Non-goals: no authentication, streaming, push notifications, task lifecycle, code
  execution or remote service. The reviewer is local-only, like the engine's phase-4
  reference agent.
