# AGENTS.md — neetcode-150.dojo

This is the private **NeetCode 150** curriculum for the dojo engine. The engine lives in
the sibling repository `../dojo`; this repository owns the subject and must never be
published.

Read [`README.md`](README.md), [`docs/how-it-works.md`](docs/how-it-works.md) and
[`docs/contributing.md`](docs/contributing.md) before changing content. The engine's
[`docs/curriculum-reference.md`](../dojo/docs/curriculum-reference.md) is the normative
manifest and wire contract.

## What lives here

- `curriculum.toml` — 18 topics, 157 items (152 active), 6 evaluator tools, 5
  capabilities, aliases and display words.
- `content/<item>/` — statement, workspace template and visible `check.py`.
- `src/neetcode_dojo/` — the private evaluator package: registry, judge, measurement,
  process isolation, static analysis and the stdio MCP server (`assessment.v1`).
- `src/neetcode_dojo/assessment/` — private cases, oracles, references and measurement
  plans. Never student-visible.
- `prompts/` and `policies/` — tutor, teacher, leak, discussion and fallback reviewer
  prompts; the ordered hint ladder.
- `reviewer/` — the A2A reviewer (`review` skill, port 8766). It reads the engine's one
  settings file and `DOJO_API_KEY` read-only.
- `tests/` and `reviewer/tests/` — offline suites.
- `docs/` — getting started, how it works, contributing, manual testing and history.

## Privacy

- `license = "private"` means **never publish**. The statements are LeetCode's and the
  assessment tree is the answers in machine form.
- Private cases, oracles, references and the reviewer rubric must never reach a student,
  the in-solve tutor, the teacher or the leak auditor. The reviewer gets only the review
  view.
- No API key, database, attempt log, workbench file or `.env` in this repository.

## Toolchain

- Python 3.15 via `uv`; `uv sync`, `uv run`.
- `uv run pytest` runs both suites: 375 tests (224 curriculum + 151 reviewer). The 15
  optional old-engine parity tests skip unless `OLD_ENGINE` points at the archive.
- `uv run ruff check .`, `uv run ruff format --check .`, `uv run ty check .`.
- `ty` excludes only the copied `content/` corpus and `src/neetcode_dojo/assessment/`
  (verbatim private content); do not add blanket excludes.
- Export `UV_CACHE_DIR=/Users/andywang/Projects/dojo-workspace/.uv-cache` in this sandbox.
  Do not commit `.venv`, caches or generated files.
- Dependencies: `pydantic`, `mcp`, `radon`, `a2a-sdk[fastapi]`, `uvicorn`. Do not add one
  without the maintainer's agreement.

## Rules

- Keep the evaluator core pure where it judges or measures; keep subprocess, filesystem
  and server code at the edge.
- Every new evaluator tool or comparator gets a test that fails before the change.
- Keep the visible check and the hidden cases distinct. A check that mirrors the hidden
  assessment is a bug.
- The manifest is strict. Enroll with the real engine before claiming a content change
  works; enrollment verifies every MCP tool and every A2A card/skill.
- The reviewer is started by dojo from the manifest `command` in normal use. For debugging,
  `uv run python -m reviewer.server`; do not add a second server path to the docs.
- No network in tests; no bound port except the reviewer's local development server.

## Workflow

Work on a branch; keep `main` loadable. Run all checks before reporting. Use conventional
commits (`feat(content): ...`, `fix(reviewer): ...`, `docs: ...`). The maintainer reviews
and merges; do not push to `main` directly.

Before a release or an engine-boundary change, follow
[`docs/manual-testing.md`](docs/manual-testing.md).
