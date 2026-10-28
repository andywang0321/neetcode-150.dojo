# AGENTS.md — neetcode-150.dojo

This repository is the private **NeetCode 150 dojo curriculum**. The engine lives in
`../rebuild`; the old curriculum (`../dojo-curriculum-neetcode-150`) and the old engine
(`../dojo`) are read-only reference material. Do not import the old engine, copy its
application code into dojo, or depend on its database/history.

Read `docs/port-plan.md` and the engine's `docs/phase-5.md` before starting work.

## 1. What lives here

The curriculum owns everything subject-specific:

- `curriculum.toml` — topics, items, evaluators, capabilities, aliases, display words;
- `content/<item>/` — statement, workspace template and visible `check.py`;
- `neetcode_dojo/` — the private evaluator package: the local registry, judge, measurement,
  static analysis, process isolation and the MCP server (`assessment.v1`);
- `neetcode_dojo/assessment/` — the private cases, oracles, references and measurement plans;
- `prompts/` and `policies/` — tutor, teacher, leak-auditor and reviewer prompts; the hint
  ladder and leak policy;
- `reviewer/` — the A2A post-solve reviewer agent;
- `tests/` — the evaluators' own offline tests.

dojo only orchestrates the tools and records evidence. The judge, measurement and
workbench code moves here, not into the engine.

## 2. Private by construction

- `license = "private"` means **never publish**. The statements are LeetCode's; the
  assessment tree is the answers in machine form.
- The assessment, private cases, oracles, references and reviewer rubric must never reach
  a student, the in-solve tutor, the teacher, or the leak auditor. The A2A reviewer gets
  the submitted files, evidence and grade only.
- No API keys, database, attempt log, workbench file or `.env` in this repository.

## 3. Toolchain

- Python 3.15 via `uv`; `uv sync` for dependencies, `uv run` for everything.
- `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .`,
  `uv run ty check .`.
- Export `UV_CACHE_DIR=/Users/andywang/Projects/dojo-workspace/.uv-cache` in the sandboxed
  workspace. Do not commit `.venv`, caches or generated files.
- The approved dependencies are the engine's phase-5 set: `pydantic`, `mcp`, `radon`,
  `a2a-sdk[fastapi]`, `uvicorn`; no new dependency without the orchestrator.

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

## 6. Phase 5 packages

| package | scope |
|---|---|
| P5-A evaluator core | local registry, judge, measurement, static analysis, process isolation, MCP server, tests |
| P5-B content + manifest | the 157 items, content/checks, assessment modules, manifest, prompts, hints, tests |
| P5-C reviewer | the NeetCode A2A reviewer agent, prompt/rubric, tests |
| P5-D integration | engine enrollment, representative/full items, run instructions, fixes |

## 7. Definition of done

- `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .` and
  `uv run ty check .` pass here.
- The engine can enroll, practise, submit and review a representative set, then the full
  corpus, without a network except the local reference/A2A agent.
- The run instructions are written for a human to test the rebuild end to end.
- No private assessment material leaked into a prompt or a student-visible path.
