# Contributing

This repository is the private NeetCode 150 curriculum. It has two test suites: the
evaluator/content suite in `tests/` and the reviewer suite in `reviewer/tests/`.

## Set up

```bash
git clone git@github.com:andywang0321/neetcode-150.dojo.git
cd neetcode-150.dojo
uv sync
uv run pytest
```

Python 3.15 and uv 0.13+ are required. The engine is a separate checkout; enroll this
curriculum to exercise the integration:

```bash
dojo enroll .
dojo curricula
```

## Checks

```bash
uv run pytest                 # 375 collected: 224 curriculum + 151 reviewer
uv run pytest tests           # evaluator core and content
uv run pytest reviewer/tests  # the reviewer
uv run ruff check .
uv run ruff format --check .
uv run ty check .
```

The suites are offline: no network, no API key and no bound port. The 15 optional
old-engine parity tests skip unless `OLD_ENGINE` points at the archived engine. `ty`
excludes only the copied `content/` corpus and `src/neetcode_dojo/assessment/` (verbatim
private content); the evaluator core, server, prompts, tests and reviewer are
type-checked.

For the engine side, run its checks from the engine checkout. The engine's [contributing
guide](https://github.com/andywang0321/dojo/blob/main/docs/contributing.md) is the source
of truth for engine changes.

## Layout

```text
curriculum.toml            18 topics, 157 items, 6 evaluators, capabilities, A2A review
content/<item>/            statement, workspace template, visible check.py
src/neetcode_dojo/         private evaluator package: judge, measure, server, tools
src/neetcode_dojo/assessment/  per-item private cases, oracles, references
reviewer/                  A2A reviewer (review skill, port 8766)
prompts/                   tutor, teacher, leak, discussion and fallback reviewer prompts
policies/hints.toml        ordered hint ladder
tests/                     evaluator core and content tests
reviewer/tests/            reviewer tests
docs/                      this guide, history and manual test checklist
```

## Changing content or evaluators

- Keep the privacy boundary: private cases, oracles, references and the reviewer rubric
  stay out of `content/`, prompts and student-visible files.
- The visible `check.py` covers examples only; the private evaluator adds cases. Do not
  make them the same set.
- The manifest is strict. Enroll against a real engine before claiming a content change
  works; enrollment verifies every MCP tool and every A2A card/skill.
- New evaluator tools and comparators need a test that fails before the change.
- Add or change a curriculum field only after checking the engine's
  [curriculum reference](https://github.com/andywang0321/dojo/blob/main/docs/curriculum-reference.md).

## The reviewer

The reviewer is a real A2A agent. Its card is served at
`http://127.0.0.1:8766/.well-known/agent-card.json`; the engine starts it from the
manifest command and stops it on exit. For debugging, `uv run python -m reviewer.server`.

It reads the engine's one `settings.toml` and `DOJO_API_KEY` read-only. It never writes the
settings file and never reads a provider-specific key. Without a key, a settings file or
with `provider = "mock"`, it serves the deterministic review.

## Branches and review

Work on a branch, keep `main` loadable, and report the checks you ran. Use conventional
commits (`feat(content): ...`, `fix(reviewer): ...`, `docs: ...`). The maintainer reviews
and merges; do not push to `main` directly.

## Manual test

Before a release or a change that touches the engine boundary, follow
[Manual testing](manual-testing.md). It covers enrollment, the full session, discussion,
polish, history/show, reviewer failure and cleanup.
