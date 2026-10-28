# Representative parity report — P5-B

Status: content parity complete; the new-server half is pending P5-A/P5-D.

This report covers the 15 representative items from `docs/port-plan.md` §§6–7:
every evaluator shape and comparison mode in the 157-item corpus. It was produced
on branch `p5/content` before the P5-A evaluator core landed, so the **new** side is:

- the ported assessment modules in `src/neetcode_dojo/assessment/` (only the registry
  import changed), loaded through the old registry in a disposable copy;
- the ported predicate checker invoked directly, which the old judge cannot do;
- not yet the P5-A `neetcode_dojo.judge`/MCP `assess.tests` server. P5-D completes
  that half once both branches are on main.

## Method

- Old module: `dojo-curriculum-neetcode-150/assessment/<item>.py` (read-only).
- New module: `src/neetcode_dojo/assessment/<item>.py`, with `from dojo.curriculum.registry`
  rewritten back to the old import only inside a temporary directory for this run.
- Cases: the old assessment harness generated at `n = 2, 5, 12` with seeds
  `parity-2`, `parity-5`, `parity-12`; the two case lists were compared as JSON.
- Verdicts: `dojo.judge.run_cases` (old engine) on the same cases for three
  submissions per item: a correct reference implementation, a wrong-but-runnable
  implementation, and one that raises. Statuses are old-engine statuses.
- Predicate checker: for the five predicate items, the new module's `@checker`
  was called with the correct submission and each predicate case, outside the old
  judge. The old judge's checker map is empty by design, so it reports a case error
  for every predicate; the new server owns the checker and decides it.

## Items and results

| item | shape | old/new cases | identical | correct | wrong | raises | checker |
|---|---|---|---|---|---|---|---|
| `two_sum` | strict equality; measured; reference; function | 3/3 | yes | correct (3/3) | wrong_answer (0/3) | error (0/3) | — |
| `contains_duplicate` | strict equality; measured; reference; bool | 3/3 | yes | correct (3/3) | wrong_answer (0/3) | error (0/3) | — |
| `valid_anagram` | strict equality; measured; reference | 3/3 | yes | correct (3/3) | wrong_answer (0/3) | error (0/3) | — |
| `min_stack` | class/ops; executable; oracle only | 3/3 | yes | correct (3/3) | wrong_answer (1/3) | error (0/3) | — |
| `lru-cache` | class/ops; executable; oracle+reference | 3/3 | yes | correct (3/3) | wrong_answer (0/3) | error (0/3) | — |
| `encode_and_decode_strings` | predicate checker; no oracle; executable | 3/3 | yes | error (0/3) | error (0/3) | error (0/3) | 3/3 |
| `generate_sample_to_target_sum` | predicate checker; no oracle; executable; no external id | 3/3 | yes | error (0/3) | error (0/3) | error (0/3) | 3/3 |
| `k-closest-points-to-origin` | predicate checker; measured; comparison none | 3/3 | yes | error (0/3) | error (0/3) | error (0/3) | 3/3 |
| `n-queens` | sorted comparison; executable | 3/3 | yes | correct (3/3) | wrong_answer (0/3) | error (0/3) | — |
| `merge-intervals` | sorted comparison; measured | 3/3 | yes | correct (3/3) | wrong_answer (0/3) | error (0/3) | — |
| `rotate-image` | mutates comparison; measured | 3/3 | yes | correct (3/3) | wrong_answer (0/3) | error (0/3) | — |
| `set-matrix-zeroes` | mutates comparison; measured | 3/3 | yes | correct (3/3) | wrong_answer (1/3) | error (0/3) | — |
| `correlation` | approx:0.0001; measured; no external id | 3/3 | yes | correct (3/3) | wrong_answer (0/3) | error (0/3) | — |
| `copy-list-with-random-pointer` | predicate checker; measured; hyphenated id | 3/3 | yes | error (0/3) | error (0/3) | error (0/3) | 3/3 |
| `serialize-and-deserialize-binary-tree` | predicate checker; executable; restored helper | 3/3 | yes | error (0/3) | error (0/3) | error (0/3) | 3/3 |

## Result

- **Case parity: 15/15 items.** The ported generator produces identical case
  lists (args, expected values and comparison tags) to the old generator at all three
  sampled sizes.
- **Verdict parity: 30/30 statuses on the ten items the old judge can decide.**
  Every correct submission is `correct`, every wrong submission is `wrong_answer`
  (two mutating/ops items correctly fail only some cases, but the report status is
  wrong_answer), and every raising submission is `error`.
- **Predicate path: 15/15 predicate cases pass the ported checker** across
  `encode_and_decode_strings`, `generate_sample_to_target_sum`,
  `k-closest-points-to-origin`, `copy-list-with-random-pointer` and
  `serialize-and-deserialize-binary-tree`. The old judge reports `error` for these
  cases because its `CHECKERS` map is intentionally empty; that is the known old
  limitation the new server fixes, not a regression.
- **Intentional differences from the old engine:** only the predicate cases above,
  plus the restored helpers listed below. Every non-predicate comparison mode
  (`strict`, `sorted`, `mutates`, `approx`, class `ops`) behaves identically.

## Port bugs fixed in the assessment tree

The old port dropped three helper functions that its own checkers call. They were
copied from the read-only old registry at commit `393783a` and kept local to the
assessment modules:

- `course-schedule-ii`: `_course_schedule_ii_schedulable` (empty-answer branch).
- `longest-palindromic-substring`: `_longest_palindromic_substring_max_len`.
- `serialize-and-deserialize-binary-tree`: `_serialize_and_deserialize_binary_tree_same`,
  `_size` and `_other` (round-trip checker).

## Not covered here

- The P5-A `assess.tests` MCP tool, `assess.oracle`, `assess.complexity` and
  `assess.style`; their conformance and timing belong to P5-A/P5-D.
- The A2A reviewer (P5-C).
- Measurement runs: the parity above compares the measurement *plan* input data and
  references indirectly (cases and references), not wall-clock growth classes. The
  plan must be run on the same pinned series in P5-D, never on a live clock.

