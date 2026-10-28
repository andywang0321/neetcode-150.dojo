# AGENTS.md — neetcode-150.dojo

This repository is the private **NeetCode 150 dojo curriculum**. The engine lives in
`../rebuild`; the old curriculum (`../dojo-curriculum-neetcode-150`) and the old engine
(`../dojo`) are read-only reference material. Do not import the old engine, copy its
application code into dojo, or depend on its database/history.

Read `docs/port-plan.md`, the engine's `docs/phase-5.md` and `docs/runbook.md` before
starting work.

## 1. What lives here

The curriculum owns everything subject-specific:

- `curriculum.toml` — 18 topics, 157 items, 6 evaluators, 4 capabilities, aliases and
  display words;
- `content/<item>/` — statement, workspace template and visible `check.py`;
- `src/neetcode_dojo/` — the private evaluator package: the local registry, judge,
  measurement, static analysis, process isolation and the MCP server (`assessment.v1`);
- `src/neetcode_dojo/assessment/` — the private cases, oracles, references and measurement
  plans;
- `prompts/` and `policies/` — tutor, teacher and leak-auditor prompts; the hint ladder;
- `reviewer/` — the P5-C/P6-C A2A post-solve reviewer agent (`review` skill, port 8766;
  it reads the engine's one settings file and `DOJO_API_KEY`);
- `tests/` and `reviewer/tests/` — the evaluators' and reviewer's offline tests;
- `docs/` — the port plan, the parity report and `docs/runbook.md`, the manual end-to-end
  test guide.

dojo only orchestrates the tools and records evidence. The judge, measurement and
workbench code lives here, not in the engine.

## 2. Private by construction

- `license = "private"` means **never publish**. The statements are LeetCode's; the
  assessment tree is the answers in machine form.
- The assessment, private cases, oracles, references and reviewer rubric must never reach
  a student, the in-solve tutor, the teacher, or the leak auditor. The A2A reviewer gets
  the submitted files, evidence and grade only.
- No API keys, database, attempt log, workbench file or `.env` in this repository.

## 3. Toolchain

- Python 3.15 via `uv`; `uv sync` for dependencies, `uv run` for everything.
- `uv run pytest` runs both suites (`tests/` and `reviewer/tests/`; 373 tests today:
  223 + 150). `uv run pytest tests` and `uv run pytest reviewer/tests` run one at a time.
- The engine and the reviewer share one provider, one `DOJO_API_KEY` and one
  `settings.toml` (`[llm]`, `[editor]`, `[curricula.<id>]`). The engine's first-run setup
  writes the config and exports the key in the shell rc; the key is never in the file.
  `DOJO_EDITOR` overrides `[editor].command` (do not read `$EDITOR`/`$VISUAL`). There is
  no reviewer key and no `DOJO_REVIEWER_*`/provider-specific key variable.
- `uv run ruff check .`, `uv run ruff format --check .`, `uv run ty check .`.
- `ty` is configured in `pyproject.toml` (`[tool.ty.src]`): it excludes only the copied
  `content/` corpus and `src/neetcode_dojo/assessment/`. The evaluator core, server,
  prompts, tests and reviewer stay type-checked; do not add blanket excludes.
- Export `UV_CACHE_DIR=/Users/andywang/Projects/dojo-workspace/.uv-cache` in the sandboxed
  workspace. Do not commit `.venv`, caches or generated files.
- The approved dependencies are the engine's phase-5 set: `pydantic`, `mcp`, `radon`,
  `a2a-sdk[fastapi]`, `uvicorn`; no new dependency without the orchestrator.
- The A2A reviewer is declared in `curriculum.toml` with a `command`; dojo probes the
  card, starts the command in the repository root when needed, and stops it on exit. Run
  `uv run python -m reviewer.server` directly only for debugging; the runbook covers the
  normal `dojo` flow.

## 4. Branch protocol

`main` is the integration branch. Never commit to it directly.

1. Work in your own git worktree of this repository, created by the orchestrator:
   `git worktree add -b p5/<name> ../worktrees/neetcode/<name> main`.
2. Stay in your worktree; do not switch branches, rebase, merge or push.
3. Commit with a conventional message; report the branch, summary, checks and deviations.
4. The orchestrator reviews and merges. Do not merge yourself.

Every branch must keep `main` loadable: no half-wired tools, no tests that pass only with
uncommitted files.

## 5. Code and content rules

- The functional core/imperative shell rule applies to the evaluator package: pure
  judgement/oracle logic separate from subprocess, filesystem and SQLite.
- Small files; typed; no magic state; no network in tests.
- The port copies the old content rather than rewriting it, and re-packages it against
  the new `assessment.v1` contract. The mapping is in `docs/port-plan.md`.
- Every new evaluator tool gets a test that fails before the change.
- The manifest is validated by the engine's loader; run the engine's `dojo enroll` against
  a built tree before claiming a content package works.

## 6. Phase 5 and P6 packages

All four phase-5 packages are on `main`. P6-A/B (one-provider setup), P6-C (the reviewer
reads the same config and key) and P6-D (this documentation refresh) are the current
phase; the phase-6 cutover is separate and destructive.

| package | scope |
|---|---|
| P5-A evaluator core | local registry, judge, measurement, static analysis, process isolation, MCP server, tests |
| P5-B content + manifest | the 157 items, content/checks, assessment modules, manifest, prompts, hints, tests |
| P5-C reviewer | the NeetCode A2A reviewer agent, prompt/rubric, tests |
| P5-D integration | engine enrollment, representative/full items, run instructions, fixes |
| P6-A/B setup | one provider, one `DOJO_API_KEY`, one settings file, first-run wizard |
| P6-C reviewer config | same settings/key; deterministic without a key |
| P6-D docs | runbook, README and port-plan refresh |

## 7. Definition of done

- `uv run pytest` (both suites), `uv run ruff check .`, `uv run ruff format --check .` and
  `uv run ty check .` pass here.
- The engine enrolls the curriculum (MCP tools and A2A card/skill probes), practises,
  submits and reviews the representative items, and lists the full corpus, without a
  network except the local A2A reviewer and the loopback MCP server.
- `docs/runbook.md` is a complete manual test guide a human can follow end to end.
- No private assessment material leaked into a prompt or a student-visible path.
