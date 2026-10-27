# Port plan — the old NeetCode 150 curriculum to the new contract

Status: phase 5 of the dojo rebuild. This document is the inventory and the mapping; no
content has been ported yet.

## 1. Source

`../dojo-curriculum-neetcode-150` (the old repository, private, no remote):

- 18 patterns / 157 items: the 150 ladder rungs plus 7 curated items.
- 127 `measured`, 30 `executable`.
- 4 files per item: `items/<item>.md`, `items/<item>.py`, `checks/<item>.py`,
  `assessment/<item>.py`.
- The assessment modules import `dojo.curriculum.registry` decorators and are loaded by
  the old engine. That import is the coupling this port removes.
- 120 items register `cases, inputs, measure, oracle, reference`; 7 add a `checker`; 25
  register `cases, oracle, reference`; 2 are `cases, checker`; the rest are small
  variations. Thirty items are `executable`, not `measured`.
- Comparison modes: `strict` 113, `mutates` 5, `sorted` 3, `none` 6.

## 2. What moves where

| old | new | notes |
|---|---|---|
| `items/<item>.md` | `content/<item>/statement.md` | title/difficulty move to the manifest; the prose stays |
| `items/<item>.py` | `content/<item>/workspace/solution.py` | plus a copy of the visible check |
| `checks/<item>.py` | `content/<item>/workspace/check.py` | the student's visible check |
| `assessment/<item>.py` | `neetcode_dojo/assessment/<item>.py` | private; registered in a local registry, no engine import |
| old engine `judge/` | `neetcode_dojo/judge/` | runner, comparators, verdicts; now curriculum-owned |
| old engine `measure/` | `neetcode_dojo/measure/` | paired profiler, growth verdict; now curriculum-owned |
| old engine `proc.py` | `neetcode_dojo/proc.py` | subprocess isolation for the student's code |
| old engine `static.py` / `complexity.py` | `neetcode_dojo/static.py` | linter and static analysis |
| `curriculum.toml` | regenerated `curriculum.toml` | topics/items/evaluators/capabilities |
| old tutor/reviewer prompts | `prompts/` | curriculum-owned persona and rubric |
| old hint ladder | `policies/hints.toml` | curriculum-owned tiers and allowed content |
| old workbench rendering | `content/<item>/workspace/` | shebang, examples block and IDE config if any |

The old content is copied, not rewritten. The port is a re-packaging: the statement is the
same statement, the oracle is the same oracle, the case generator is the same generator.

## 3. The MCP tool surface

One server, `neetcode_dojo.server`, stdio. Tools:

| tool | input | output |
|---|---|---|
| `assess.tests` | item, submission, claims | machine evidence, per-case detail |
| `assess.oracle` | item, submission | independent machine evidence |
| `assess.complexity` | item, submission | measured evidence, ratio trend or unresolved |
| `assess.style` | item, submission | machine evidence from the linter |
| `variant` | item, history | a task spec (re-solve or re-derived inputs) |
| `grade` | item, evidence, claims | grade 1–4 + rationale |

The evaluator ids and tool names are declared in `curriculum.toml` and mirrored in the
server. The loader validates that every declared tool exists at enrollment (phase 2).

The tool payloads use the versioned contracts in the dojo `spec/` directory. The server
validates inputs and returns the standard `AssessmentResult`; it never returns a raw
LeetCode verdict shape to dojo.

## 4. The A2A reviewer

One real A2A agent, `neetcode_dojo.reviewer`, with a `review` skill. It receives the
statement, the submission, the evidence, the claims and the grade. It may use its own
tools — the linter, the profiler, a rubric lookup — and produces a structured critique:

```json
{
  "summary": "...",
  "strengths": ["..."],
  "improvements": ["..."],
  "next_steps": ["..."],
  "quality": {"score": 0.0, "rationale": "..."}
}
```

The review is advisory. A gating judgment needs an independent audit pass; the reviewer
never becomes the correctness verdict.

## 5. The agent roster

| capability | implementation | why |
|---|---|---|
| assess | MCP tools | deterministic; must not be an LLM |
| variant | MCP tool | re-solve is the default; re-derive needs generation |
| grade | MCP tool | only this curriculum knows what "good" means |
| assist | declarative LLM (`prompts/tutor.md`) | low latency, dojo controls the context |
| instruct | declarative LLM (`prompts/teacher.md`) | no item statement, no assessment |
| audit | declarative LLM (`prompts/leak.md` + hint policy) | semantic leak guard on every hint |
| review | A2A (`neetcode_dojo.reviewer`) | multi-step, own tools/model, post-solve |
| discuss | A2A or declarative (phase 4) | post-solve follow-up; solutions allowed |

## 6. Parity strategy

- Port a representative 15 items covering every evaluator shape and comparison mode.
- For each, run the old engine's judge and the new server's `assess.tests` on the same
  submissions and require identical verdicts and per-case statuses.
- For measured items, compare the measurement plan and the reference output at each ladder
  size; the ratio verdict is statistical, so assert the class only on the same pinned
  series, never on wall-clock timing.
- Port the old evaluator tests into `tests/` and run them offline.
- Only then bulk-port the remaining items.

## 7. Risks and decisions

- **Predicate cases.** Ten items use a `predicate` decided by a checker registered in the
  assessment module. The old engine's checker registry left with the corpus or was never
  fixed; the new server owns the checker and can call it directly, which is the clean fix.
- **Sub-linear references.** A sub-linear reference cannot support a "better" claim; the
  old `measure/growth.py` already handles this. Port the rule, not a new one.
- **In-place items.** Five items grade on their effect (`mutates`). Keep the same
  post-call comparison; the submission's arguments are the thing that changed.
- **Copyright.** The statements are LeetCode's. The new repository stays private; do not
  publish, quote statements into issues, or add a remote without a licensing decision.
- **Old history.** The user has discarded the old attempts and cards. The new curriculum
  does not need to map old ids to history; item ids stay stable for future use.
- **Workbench.** The old engine's examples block and IDE config were valuable. Reproduce
  them in the workspace template; do not depend on dojo rendering them.
- **Dependencies.** The server's `pyproject.toml` pins its own runtime (the MCP SDK, the
  profiler's needs). dojo does not install curriculum dependencies; the curriculum's
  README documents the command.

## 8. Milestones

| step | deliverable |
|---|---|
| 5a | port judge/measure/static libraries + their tests |
| 5b | manifest generator + 15 representative items end-to-end |
| 5c | MCP server, tools, evaluator conformance |
| 5d | A2A reviewer + prompts + hint policy |
| 5e | bulk port of the remaining 142 items + parity report |
