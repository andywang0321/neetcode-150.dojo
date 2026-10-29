# Development history

This curriculum is a port of a larger NeetCode 150 implementation that lived beside the
old engine. The rebuild moved the subject-specific code here and left the engine to
orchestrate.

## The port

The old curriculum had 18 patterns and 157 items: the 150 ladder rungs plus seven curated
items. Five are retired duplicates kept addressable for history, so the roadmap serves 152.
It had 127 measured items and 30 executable ones, with four files per item: statement,
workspace stub, visible check and a private assessment module.

The port kept the content and re-packaged it against the new contracts:

| old | new |
|---|---|
| `items/<item>.md` | `content/<item>/statement.md` |
| `items/<item>.py` | `content/<item>/workspace/solution.py` |
| `checks/<item>.py` | `content/<item>/workspace/check.py` |
| `assessment/<item>.py` | `src/neetcode_dojo/assessment/<item>.py` |
| old engine `judge/`, `measure/`, `proc.py`, `static.py` | `src/neetcode_dojo/` |
| old `curriculum.toml` | regenerated manifest: topics, items, evaluators, capabilities, A2A review |
| old prompts and hint ladder | `prompts/` and `policies/hints.toml` |
| old reviewer rubric | `reviewer/` A2A agent |

The old assessment modules imported the old engine's registry; the port removed that
coupling. The new modules register against `neetcode_dojo.registry` and the MCP server is
the only entrypoint.

## Parity

The representative parity check covered 15 items and every evaluator shape: strict
equality, sorted, mutating, approximate, class/ops and predicate checkers.

- **Cases:** 15/15 items produced identical case lists at the sampled sizes and seeds.
- **Verdicts:** 30/30 statuses matched on the ten items the old judge could decide.
- **Predicate path:** 15/15 predicate cases passed the ported checkers. The old judge
  deliberately had no checker map, so those cases errored there; the new server fixed it.
- **Intentional differences:** the predicate path, plus three restored helper functions
  the old port had dropped.

The full table is in the repository history; this document keeps the result, not the
spreadsheet.

## After the port

- **P6** moved the engine and reviewer onto one provider, one `DOJO_API_KEY` and one
  `settings.toml`; the reviewer reads the same config read-only.
- **P7** let dojo start the reviewer from the manifest, moved the statement into
  `solution.py`, hid the visible check, rendered reviews as Markdown and compacted
  progress.
- **P8** added the two complexity reflection questions; their answers become reviewer
  claims.
- **P9** added post-solve discussion, polish mode, saved conversation and snapshots, and
  numbered `history`/`show`.
- The cutover replaced the old engine and old curriculum; the old repositories are
  archived locally and are not dependencies.

## Current shape

- 18 topics, 157 items, 152 active; 6 evaluator tools, 4 attached to items.
- 127 measured-complexity items; 30 executable; 5 retired duplicates.
- 375 tests: 224 evaluator/content and 151 reviewer. The 15 optional old-engine parity
  tests skip without the archived engine; the rest pass. Ruff and ty are clean.
- The engine is at [github.com/andywang0321/dojo](https://github.com/andywang0321/dojo).

For the engine's side of the story, see its
[development history](https://github.com/andywang0321/dojo/blob/main/docs/development-history.md).
