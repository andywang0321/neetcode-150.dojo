# neetcode-150.dojo

The NeetCode 150 as a **dojo curriculum**: 18 patterns and 157 problems — the 150 ladder
rungs in roadmap order plus seven of dojo's own curated problems. Five of the 157 are
retired duplicates kept addressable for history, so the roadmap serves 152.

The repository follows dojo's curriculum convention: `<curriculum-id>.dojo`.

Phases P5-A (evaluator core), P5-B (content and manifest), P5-C (A2A reviewer) and P5-D
(engine integration) are complete. P6-A/B moved the engine to one provider, one
`DOJO_API_KEY` and one `settings.toml`; P6-C moved the reviewer onto that same config and
key; P6-D refreshed the documentation. The engine (phases 1-4) lives in `../rebuild`; the
old curriculum and engine (`../dojo-curriculum-neetcode-150`, `../dojo`) are read-only
reference material. See [`docs/port-plan.md`](docs/port-plan.md) for the inventory and
mapping and [`docs/runbook.md`](docs/runbook.md) for the manual end-to-end test guide.

> **Private, and that is also a copyright statement.** The statements are LeetCode's,
> reproduced from a community mirror. `license = "private"` means this repository is never
> published. The assessment tree is the answers in machine form; it is private too, and it
> must never reach a student, the in-solve tutor, the teacher or the leak auditor.

## What lives here

```
curriculum.toml                 # 18 topics, 157 items, 6 evaluators, 4 capabilities, A2A review
content/<item>/                 # statement + workspace template + visible check.py
src/neetcode_dojo/              # the private evaluator package
  server.py                     # stdio MCP server: tests, oracle, complexity, style, variant, grade
  judge/                        # case runner, comparators, verdicts
  measure/                      # paired profiler and growth verdict
  assessment/                   # per-item private cases, oracles, references, measurement plans
  tools/                        # the six MCP tools and their assessment.v1 contracts
reviewer/                       # the NeetCode A2A post-solve reviewer (review skill, port 8766)
prompts/                        # tutor, teacher and leak-auditor prompts
policies/hints.toml             # the ordered hint ladder
tests/                          # the evaluator core's and content's offline tests
reviewer/tests/                 # the reviewer's offline tests
docs/                           # port plan, parity report, manual runbook
```

The old engine's judge, measurement and workbench code moved **here**, not into dojo.
dojo orchestrates the MCP evaluator tools, records the evidence, schedules the cards and
sends the advisory review request over A2A.

## The engine and its contracts

The manifest targets dojo `>=0.1,<1` with `assessment.v1` and `review.v1`:

- `[server]` runs `uv run --project . python -m neetcode_dojo.server` over stdio with the
  curriculum root as its working directory. Enrollment verifies all six declared tools.
- Items reference four evaluators: `tests` (required), `oracle`, `complexity` (127
  measured items) and `style` (advisory, assurance `judged`). `variant` and `grade` are
  declared for the grader but deliberately not attached to item `evaluators`.
- `[capabilities.assist/instruct/audit]` are declarative LLM prompts; `[capabilities.review]`
  is `impl = "a2a"` pointing at `[agents.reviewer]`, `http://127.0.0.1:8766/`, skill
  `review` (the P6-C agent in `reviewer/`).

The reviewer sees exactly the review view — statement, submitted files, evidence, grade
and claims — never the assessment tree, hidden cases, references or history. The review
is advisory: it is stored with `provider = "a2a"` provenance and never changes the grade,
card or evidence.

## Set up, start the reviewer and enrol

The engine and the reviewer share **one provider**, **one `DOJO_API_KEY`** and **one
`settings.toml`**. The first `dojo` in a terminal runs the setup wizard (provider, optional
base URL, the provider's default model, editor, hidden key), validates the key, writes the
config atomically and exports `DOJO_API_KEY` in your shell rc in a marked block; the key
never enters the settings file. `DOJO_EDITOR` overrides `[editor].command` for one shell;
`$EDITOR` and `$VISUAL` are not read. `--no-setup`/`DOJO_NO_SETUP` skip the wizard, and a
non-TTY run fails with an actionable message instead of prompting. The wizard exits, so
close the terminal and open a new one.

```bash
export UV_CACHE_DIR=/Users/andywang/Projects/dojo-workspace/.uv-cache

# 1. first run: answer the wizard, then open a new terminal
cd /Users/andywang/Projects/dojo-workspace/rebuild
uv sync
uv run dojo

# 2. the reviewer is started by dojo from the manifest command; no separate terminal
cd /Users/andywang/Projects/dojo-workspace/neetcode-150.dojo
uv sync
# dojo probes the card, starts `reviewer.server` when needed and stops it on exit

# 3. the engine, against isolated test data and the same one config
cd /Users/andywang/Projects/dojo-workspace/rebuild
export DOJO_DATA_DIR="$HOME/dojo-p6d/data"
export DOJO_WORKBENCH_DIR="$HOME/dojo-p6d/workbench"
mkdir -p "$DOJO_DATA_DIR" "$DOJO_WORKBENCH_DIR"
uv run dojo enroll /Users/andywang/Projects/dojo-workspace/neetcode-150.dojo
uv run dojo
```

The reviewer is required at enrollment (the card and skill are probed) and is started
automatically. If its launch command fails, the attempt, grade and card are still recorded
and `review unavailable` is printed. With `provider = "mock"` (or a mock profile) `check` and
`submit` work offline and no key is needed; a live provider without `DOJO_API_KEY` stops
at the setup gate. The reviewer is deterministic without a key; with the one key and a
live config it writes the prose from the same review view, and
`[curricula."neetcode-150".reviewer].model` overrides `[llm].model` for it only.

The full manual test — prerequisites, the first-run and key-only setup, the one
`settings.toml`, the reviewer's two modes, a sample session, tutor/teacher/hint flow,
progress/history, failure paths, data locations, cleanup and privacy — is in
[`docs/runbook.md`](docs/runbook.md).

## Tests and checks

```bash
cd /Users/andywang/Projects/dojo-workspace/neetcode-150.dojo
export UV_CACHE_DIR=/Users/andywang/Projects/dojo-workspace/.uv-cache
uv sync
uv run pytest                 # both suites: 373 (223 curriculum + 150 reviewer)
uv run pytest tests           # the evaluator core and content suite: 223
uv run pytest reviewer/tests  # the reviewer suite: 150
uv run ruff check .
uv run ruff format --check .
uv run ty check .
```

The curriculum and reviewer suites are offline: no network, no API key and no bound port.
The engine's 579 tests and the reference A2A agent's 17 tests are run from `../rebuild`
(the engine's one A2A integration test binds loopback 8765). `ty` excludes only the
copied `content/` corpus and `src/neetcode_dojo/assessment/` (verbatim private content);
the evaluator core, server, prompts, tests and reviewer are all type-checked.

## Phase-5 and P6 result

- **Enrollment:** the engine installs the curriculum, probes the real MCP server (all six
  tools) and the P6-C A2A card/skill, and persists 18 topics / 157 items (152 active).
- **Setup and credentials:** the first-run wizard writes one `settings.toml` and exports
  the one `DOJO_API_KEY` in the shell rc (never the file); the reviewer reads the same
  config and key, deterministic without a key, with no `DOJO_REVIEWER_*`/`OPENAI_*` and an
  optional `[curricula."neetcode-150".reviewer].model` override.
- **Representative end-to-end:** `contains_duplicate` (tests + oracle + measured
  complexity + advisory style) and `encode_and_decode_strings` (predicate checker) pass
  through `check`, `submit`, grade 3, FSRS card and the A2A review, stored as
  `reviews.agent = reviewer/review` with `ai_calls.provider = a2a`.
- **Failure paths:** reviewer down at enrollment fails cleanly and enrols nothing;
  reviewer stopped after enrollment leaves the attempt/card intact and prints
  `review unavailable`; a live provider without a key stops at the setup gate and `mock`
  needs none; a blocked audit withholds the tutor answer.
- **Parity:** the P5-B representative parity report shows 15/15 identical case lists,
  30/30 identical judge statuses on the ten items the old judge can decide, and 15/15
  predicate cases through the ported checker. See
  [`docs/parity-report.md`](docs/parity-report.md).
- **Checks:** curriculum `pytest` 373 (223 + 150), `ruff check`, `ruff format --check` and
  `ty check` clean; engine 579 tests and the same checks clean (the only engine formatting
  complaint is a pre-existing Markdown code block in its read-only `docs/phase-2.md`).

Requires `uv >= 0.13` and Python 3.15. The phase-6 cutover is a separate, destructive
step; this documentation gate does not run it.
