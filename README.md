# neetcode-150.dojo

**The NeetCode 150 as a rigorous, evidence-graded practice curriculum for
[dojo](https://github.com/andywang0321/dojo).**

18 patterns. 157 problems. 152 active. Every submission is assessed, scheduled with FSRS,
reviewed by an A2A agent, and followed by a conversation about the code you actually wrote.

> **Private.** The statements are LeetCode's, reproduced from a community mirror, and the
> assessment tree contains the answers in machine form. `license = "private"` means this
> repository must never be published. See [Privacy](#privacy) below.

## Mission

Make interview preparation deliberate practice: short, repeated, evidence-graded work on
the patterns that matter, with honest feedback on correctness and complexity.

## Vision

A reference curriculum for what a dojo subject can be — local-first, rigorously assessed,
and honest about the boundary between helping a learner and solving the problem for them.

## Why this curriculum

- **The full ladder, in dependency order.** 18 patterns from arrays and hashing through
  graphs, dynamic programming, intervals and bit manipulation. Prerequisites define the
  roadmap; retired duplicates stay addressable for history.
- **The visible check is not the grade.** Each item has a small visible `check.py` for the
  examples. Private cases and, where useful, an independent oracle decide correctness.
- **Complexity is measured.** 127 items have a paired profiler that compares growth with a
  reference, so a plausible-sounding Big-O claim can be checked against evidence.
- **The reviewer is a real agent.** The post-solve reviewer runs over A2A, sees only the
  statement, submitted files, evidence, grade and claims, and never changes the grade.
- **The tutor will not solve it.** The in-solve tutor sees your current code, gives one
  hint at a time, and every answer is leak-audited. The teacher is a separate boundary for
  learning the underlying pattern.
- **Everything is saved.** Attempts, evidence, claims, reviews, discussion and solution
  snapshots are available through `dojo history` and `dojo show`.

## Quick start

You need a working dojo installation and access to this private repository. The engine's
[install guide](https://github.com/andywang0321/dojo/blob/main/docs/install.md) covers
the global `dojo` command, the first-run setup and the one `DOJO_API_KEY`.

```bash
# 1. install dojo (once)
git clone https://github.com/andywang0321/dojo.git
cd dojo
uv tool install .
dojo --version

# 2. clone and enroll this curriculum
git clone git@github.com:andywang0321/neetcode-150.dojo.git
cd neetcode-150.dojo
dojo enroll .

# 3. start practising
dojo curricula
dojo progress
dojo
```

dojo starts the evaluator server and the A2A reviewer from the manifest. You do not run a
second server. The first session is a solve; after `submit`, the reviewer discussion opens.

## A session

```text
dojo> open             # edit solution.py
dojo> check            # visible check only
dojo> submit           # time/space questions, evidence, grade, review
dojo> why does the set make membership O(1)?
... reviewer answer ...
dojo> polish           # revise and submit again
dojo> done
```

`dojo progress` shows the pattern tree; `dojo history` lists numbered attempts and
`dojo show 1` shows the newest one with its solution, evidence, review and conversation.

## Documentation

| guide | contents |
|---|---|
| [Getting started](docs/getting-started.md) | install, enroll, first session, reviewer troubleshooting |
| [How it works](docs/how-it-works.md) | evaluators, evidence, hints, review, privacy |
| [Contributing](docs/contributing.md) | development setup, tests and content changes |
| [Manual testing](docs/manual-testing.md) | end-to-end maintainer checklist |
| [Development history](docs/development-history.md) | the port, parity and current shape |
| [docs/](docs/) | all of the above |

Engine documentation: [github.com/andywang0321/dojo](https://github.com/andywang0321/dojo#documentation).
Curriculum authoring: [Build a curriculum](https://github.com/andywang0321/dojo/blob/main/docs/curriculum-authoring.md).

## What lives here

```text
curriculum.toml            18 topics, 157 items, 6 evaluators, 5 capabilities, A2A review
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

The engine lives separately; this repository owns the subject. The old curriculum and
engine are archived and are not dependencies.

## Development

```bash
uv sync
uv run pytest                 # 375 collected: 224 curriculum + 151 reviewer
uv run pytest tests
uv run pytest reviewer/tests
uv run ruff check .
uv run ruff format --check .
uv run ty check .
```

The suites are offline: no network, no API key, no bound port. The 15 optional parity
tests skip unless `OLD_ENGINE` points at the archived old engine. `ty` excludes only the
copied `content/` corpus and `src/neetcode_dojo/assessment/`; the evaluator core, server,
prompts, tests and reviewer are type-checked.

## Privacy

- **Never publish this repository.** The statements are LeetCode's and the assessment tree
  is the answers in machine form.
- Hidden cases, oracles, references and the reviewer rubric never reach a student, the
  in-solve tutor, the teacher or the leak auditor.
- The reviewer sees only the review view: statement, submitted files, evidence, grade and
  claims.
- The engine's MCP server does not receive `DOJO_API_KEY`; the reviewer reads the same
  settings file and key read-only.

No API key, database, attempt log, workbench file or `.env` belongs in this repository.
