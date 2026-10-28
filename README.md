# neetcode-150.dojo

The NeetCode 150 as a **dojo curriculum**: 18 patterns and 157 problems, the 150 ladder
rungs in roadmap order plus seven of dojo's own curated problems.

The repository follows dojo's curriculum convention: `<curriculum-id>.dojo`.

This repository is the **rebuild** of the old `dojo-curriculum-neetcode-150` against the
new dojo contract. It is a scaffold today; the content, the evaluators and the reviewer
agent land in phase 5 of the dojo rebuild. See [`docs/port-plan.md`](docs/port-plan.md).

> **Private, and that is also a copyright statement.** The statements are LeetCode's,
> reproduced from a community mirror. `license = "private"` means this repository is never
> published. The assessment tree is the answers in machine form; it is private too, and it
> must never reach a student or an in-solve agent.

## What this repository will contain

```
curriculum.toml            # topics, items, evaluators, capabilities, display words
content/<item>/            # statement + workspace template + visible check
neetcode_dojo/             # the MCP server and the evaluators (the answers)
  server.py                # MCP tool surface: tests, complexity, style, variant, grade
  judge/                   # case runner, comparators, verdicts
  measure/                 # paired profiler and growth verdict
  assessment/              # per-item cases, oracles, references, measurement plans
  reviewer/                # the A2A post-solve reviewer agent
prompts/                   # tutor, teacher, leak-auditor and reviewer prompts
policies/                  # hint ladder and leak policy
tests/                     # the evaluators' own offline tests
tools/                     # port and audit scripts (authoring, not dojo)
```

The old engine's judge, measurement and workbench code moves **here**, not into dojo.
dojo only orchestrates the tools and records the evidence.

## Phase 5 port

1. Port the judge, measurement and static-analysis libraries from the old engine into
   `neetcode_dojo/`, with their tests.
2. Generate the manifest from the old `curriculum.toml` and the old item corpus.
3. Port a representative 15 items across all evaluator shapes, prove them against the old
   engine, then port the remaining 142.
4. Expose the MCP tools and implement the A2A reviewer.
5. Add the hint ladder, prompts and grade policy.

The detailed inventory, mapping and risks are in [`docs/port-plan.md`](docs/port-plan.md).

## Development

```bash
uv sync
uv run pytest
uv run ruff check src tests
uv run ty check src tests
```

Requires `uv >= 0.13` and Python 3.15.
