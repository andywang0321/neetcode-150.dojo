# Port plan — the old NeetCode 150 curriculum to the new contract

Status: **phase 5 complete; P6 setup and reviewer config landed.** P5-A (evaluator core),
P5-B (content and manifest), P5-C (reviewer) and P5-D (integration and runbook) have
landed. P6-A/B unified the engine on one provider, one `DOJO_API_KEY` and one
`settings.toml`; P6-C moved the reviewer onto that same config and key; P6-D refreshed the
documentation. This document is the inventory and the mapping;
[`parity-report.md`](parity-report.md) is the parity record and
[`runbook.md`](runbook.md) is the manual end-to-end test guide.

## 1. Source

`../dojo-curriculum-neetcode-150` (the old repository, private, no remote):

- 18 patterns / 157 items: the 150 ladder rungs plus 7 curated items. Five are retired
  duplicates kept addressable, so the roadmap serves 152.
- 127 `measured`, 30 `executable`. 155 carry a LeetCode number; the two curated items
  `generate_sample_to_target_sum` and `correlation` do not.
- 4 files per item: `items/<item>.md`, `items/<item>.py`, `checks/<item>.py`,
  `assessment/<item>.py`.
- The assessment modules imported `dojo.curriculum.registry` decorators and were loaded
  by the old engine. That import is the coupling this port removed: the new modules import
  `neetcode_dojo.registry` only.
- Comparison modes in the old corpus: `strict` 113, `mutates` 5, `sorted` 3, `none` 6;
  five items decide their predicate cases through a registered checker.

## 2. What moved where

| old | new | notes |
|---|---|---|
| `items/<item>.md` | `content/<item>/statement.md` | title/difficulty moved to the manifest; the prose stays |
| `items/<item>.py` | `content/<item>/workspace/solution.py` | stub plus a copy of the visible check; the examples block is preserved |
| `checks/<item>.py` | `content/<item>/workspace/check.py` | the student's visible check, never the verdict |
| `assessment/<item>.py` | `src/neetcode_dojo/assessment/<item>.py` | private; registered in the curriculum-local registry, no engine import |
| old engine `judge/` | `src/neetcode_dojo/judge/` | runner, comparators, verdicts; now curriculum-owned |
| old engine `measure/` | `src/neetcode_dojo/measure/` | paired profiler, growth verdict; now curriculum-owned |
| old engine `proc.py` | `src/neetcode_dojo/proc.py` | subprocess isolation for the student's code |
| old engine `static.py` / `complexity.py` | `src/neetcode_dojo/static.py`, `complexity.py` | linter and static analysis |
| old `curriculum.toml` | regenerated `curriculum.toml` | 18 topics, 157 items, 6 evaluators, capabilities, A2A review |
| old tutor/reviewer prompts | `prompts/tutor.md`, `teacher.md`, `leak.md` | curriculum-owned persona and leak policy |
| old reviewer rubric | `reviewer/prompt.py` + `reviewer/advice.py` | the P5-C A2A agent owns the rubric |
| old hint ladder | `policies/hints.toml` | curriculum-owned tiers and allowed content |
| old workbench rendering | `content/<item>/workspace/` | shebang, examples block and visible check |

The old content is copied, not rewritten. The port is a re-packaging: the statement is the
same statement, the oracle is the same oracle, the case generator is the same generator.

## 3. The MCP tool surface

One server, `src/neetcode_dojo/server.py`, stdio. It is what `[server]` in the manifest
runs: `uv run --project . python -m neetcode_dojo.server`.

| tool | input | output |
|---|---|---|
| `assess.tests` | item, submission, claims | machine evidence, per-case detail |
| `assess.oracle` | item, submission | independent machine evidence |
| `assess.complexity` | item, submission | measured evidence, ratio trend or unresolved |
| `assess.style` | item, submission | advisory radon/ruff findings |
| `variant` | item, history | a task spec (re-solve or re-derived inputs) |
| `grade` | item, evidence, claims | grade 1-4 + rationale |

The evaluator ids and tool names are declared in `curriculum.toml` and mirrored in the
server. The engine loader validates that every declared tool exists at enrollment and
probes the real server for the tool list.

Every tool returns the versioned `assessment.v1` `AssessmentResult`; it never returns a
raw LeetCode verdict shape. The manifest owns the assurance (a tool cannot upgrade its
own evidence): `tests`/`oracle` are `machine`, `complexity` is `measured`, `style` and
`grade` are `judged`, `variant` is `self`.

## 4. The A2A reviewer

One real A2A agent in `reviewer/`, built on `a2a-sdk[fastapi]`, with one `review` skill.
It serves the card at `http://127.0.0.1:8766/.well-known/agent-card.json` and JSON-RPC at
`http://127.0.0.1:8766/`. The manifest's `command` lets dojo start it on demand; the user
does not run a separate reviewer terminal in normal use. For debugging,
`uv run python -m reviewer.server` from the repository root still works; stop it with
Ctrl-C.

It receives the `review.v1` review view — statement, submitted files, evaluator evidence,
grade and claims — and returns `ReviewResult`:

```json
{
  "summary": "...",
  "strengths": ["..."],
  "improvements": ["..."],
  "next_steps": ["..."],
  "quality": 0.76
}
```

The review is advisory. It never becomes the correctness verdict; the engine stores it in
`reviews` and records `provider = "a2a"` provenance in `ai_calls`, leaving the grade, card
and evidence untouched. A stopped or malformed agent prints `review unavailable` and the
attempt survives. The agent never sees the assessment tree, hidden cases, references or
history.

The reviewer has no configuration or key of its own. It reads the engine's one
`$DOJO_CONFIG_DIR/settings.toml` (or the engine's XDG default
`~/.config/dojo/settings.toml`) and the one `DOJO_API_KEY`. `[llm].provider`/`model`/
`base_url` select the model path, and `[curricula."neetcode-150".reviewer].model`
optionally overrides the model for the reviewer alone. `DOJO_REVIEWER_*`, `OPENAI_*` and
the provider-specific key variables are gone; they are not fallbacks. With no key, no
settings file or `provider = "mock"`, the deterministic rubric is the review and no model
call is made.

## 5. The agent roster

| capability | implementation | why |
|---|---|---|
| assess | MCP tools | deterministic; must not be an LLM |
| variant | MCP tool | re-solve is the default; re-derive needs generation |
| grade | MCP tool | only this curriculum knows what "good" means |
| assist | declarative LLM (`prompts/tutor.md`) | low latency, dojo controls the context |
| instruct | declarative LLM (`prompts/teacher.md`) | no item statement, no assessment |
| audit | declarative LLM (`prompts/leak.md` + hint policy) | semantic leak guard on every hint |
| review | A2A (`reviewer/`) | multi-step, own tools/model, post-solve |

`variant` and `grade` are declared but deliberately off every item's `evaluators`; the
engine's default policy grades, and the curriculum's own `grade` tool is available to a
later integration. `discuss` is not implemented in phase 5.

## 6. Parity strategy

- Port a representative 15 items covering every evaluator shape and comparison mode.
- For each, run the old engine's judge and the new server's `assess.tests` on the same
  submissions and require identical verdicts and per-case statuses.
- For measured items, compare the measurement plan and the reference output at each ladder
  size; the ratio verdict is statistical, so assert the class only on the same pinned
  series, never on wall-clock timing.
- Port the old evaluator tests into `tests/` and run them offline.
- Only then bulk-port the remaining items.

## 7. Parity and integration results

The representative parity report ([`parity-report.md`](parity-report.md)) records:

- **Case parity: 15/15** — the ported generators produce identical case lists (args,
  expected values and comparison tags) at `n = 2, 5, 12`.
- **Verdict parity: 30/30** statuses on the ten items the old judge can decide.
- **Predicate path: 15/15** predicate cases through the ported checker, which the old
  judge cannot decide because its `CHECKERS` map is empty.

P5-D completed the new-server half and the engine integration (2026-10-27):

- The engine enrolled the curriculum from the worktree, probing the real MCP server
  (all six tools) and the real P5-C A2A card/skill; the catalog persisted 18 topics and
  157 items (152 active, 5 retired).
- `contains_duplicate` ran end to end (tests, oracle, measured complexity, advisory style)
  with `check`, `submit`, grade 3, an FSRS card and an A2A review stored with
  `reviews.agent = reviewer/review` and `ai_calls.provider = a2a`.
- `encode_and_decode_strings` exercised the predicate checker end to end (26/26 private
  cases), and `valid_palindrome` exercised a measured item whose complexity evidence was
  `partial` (advisory for the default grade).
- The tutor/teacher/hint flow ran on `provider = "mock"`. Under the P6 setup gate a live
  provider without a key stops before a session instead of degrading mid-session, and
  `mock` needs no key; a blocking leak-auditor verdict withheld the answer and kept the
  hint level.
- The failure paths held: reviewer down at enrollment failed cleanly and enrolled nothing;
  reviewer stopped after enrollment left the attempt, grade and card intact and printed
  `review unavailable`; `unenroll` kept history.
- The full 157-item catalog is available to the engine (all statements/workspaces
  resolved); a full 157 submission run was not repeated because the item corpus and
  assessment registration are covered by the offline suite and the enrollment loader.

P6-D refreshed the setup, credentials, reviewer and test documentation (2026-10-28):

- The engine's first-run wizard writes one `settings.toml` (provider, optional base URL,
  the provider's default model, editor) and exports the one `DOJO_API_KEY` in the shell rc
  in a marked, backed-up block. A key-only step handles an existing config without a key;
  `--no-setup`, `DOJO_NO_SETUP` and non-TTY runs fail actionably; `--help`/`--version`
  never run setup.
- The reviewer reads the same `settings.toml` and `DOJO_API_KEY`;
  `[curricula."neetcode-150".reviewer].model` is its only override. No
  `DOJO_REVIEWER_*`/`OPENAI_*` or provider-specific key variable remains.
- Checks: curriculum 375 (224 + 151), engine 588, reference agent 17; `ruff check`,
  `ruff format --check` and `ty check` clean (the engine's only formatting complaint is
  the pre-existing `docs/phase-2.md` Markdown block).
- The runbook covers the first-run/key-only/mock flows, the one settings file, the
  reviewer's deterministic and model modes, the practice/A2A session, the failure paths,
  the full-corpus counts (157 corpus, 152 active, 5 retired), data/privacy and cleanup.

## 8. Risks and decisions

- **Predicate cases.** Five items use a `predicate` decided by a checker registered in the
  assessment module. The old engine's checker registry left with the corpus; the new
  server owns the checker and calls it directly, which is the clean fix.
- **Sub-linear references.** A sub-linear reference cannot support a "better" claim; the
  old `measure/growth.py` already handles this. The rule was ported, not invented.
- **In-place items.** Five items grade on their effect (`mutates`). The same post-call
  comparison is kept; the submission's arguments are the thing that changed.
- **Advisory evidence.** `style` is `judged` and `complexity` is `measured`, but neither is
  a required correctness verdict. The engine's default grade policy reads the required
  `tests` evaluator; a partial complexity reading is surfaced in evidence and the review
  without silently changing the grade. The curriculum's `grade` tool is the stricter
  path, declared off items for now.
- **Copyright.** The statements are LeetCode's. The repository stays private; do not
  publish, quote statements into issues, or add a remote without a licensing decision.
- **Old history.** The user has discarded the old attempts and cards. The new curriculum
  does not map old ids to history; item ids stay stable for future use.
- **Workbench.** The old engine's examples block is reproduced in the workspace template;
  dojo does not render it.
- **Dependencies.** The curriculum pins its own runtime (`a2a-sdk`, `mcp`, `pydantic`,
  `radon`, `uvicorn`); dojo does not install curriculum dependencies. The README and
  runbook document `uv sync`.
- **One config and one key.** The engine and the reviewer share one `settings.toml` and one
  `DOJO_API_KEY`. There is no username, no per-provider key and no reviewer key. The setup
  wizard exports the key in the shell rc; it stays out of the settings file, the database,
  the review view and the MCP child environment. `DOJO_EDITOR` overrides
  `[editor].command`; `$EDITOR`/`$VISUAL` are not read.
- **Reviewer lifecycle.** The reviewer must be started by the user before enrollment and
  kept up for reviews. It reads the same config/key as the engine, so both processes must
  be pointed at the same `settings.toml`; dojo fails closed at enrollment and degrades
  gracefully at submit.

## 9. Milestones

| step | deliverable | status |
|---|---|---|
| 5a | port judge/measure/static libraries + their tests | done |
| 5b | manifest + 157 content items + parity report | done |
| 5c | MCP server, tools, evaluator conformance | done (with 5a) |
| 5d | A2A reviewer + prompts + hint policy | done |
| 5e | integration: enrollment, representative items, runbook | done |

The P6-A/B setup, P6-C reviewer config and P6-D documentation packages are complete. The
phase-6 cutover (backup, rename, force-push, fresh database) is separate and destructive;
the P6-D runbook is its gate.
