# How it works

This is a rigorous practice curriculum, not a problem list. Every item has a statement, a
workspace, a visible check and private evaluators. Every submission becomes evidence; the
review and discussion happen after the grade.

## The corpus

- **18 patterns**, in the NeetCode/NeetCode-150 order: arrays and hashing, two pointers,
  sliding window, stack, binary search, linked list, trees, tries, heap, backtracking,
  graphs, advanced graphs, 1-D DP, 2-D DP, greedy, intervals, math and geometry, bit
  manipulation.
- **157 items**: the 150 ladder problems plus 7 curated items. Five are retired duplicates
  kept addressable for history, so **152 are active**.
- **127 items** have a measured complexity evaluator. The rest have executable or
  judge-based evaluation.
- Items are private: the statements are LeetCode's, and the assessment tree contains the
  answers in machine form. See [Privacy and copyright](#privacy-and-copyright).

## Evidence

The manifest declares six evaluator tools. Four are attached to items:

| evaluator | assurance | role |
|---|---|---|
| `tests` | machine, required | private cases through the item's comparator; the correctness verdict |
| `oracle` | machine | an independent reference where the tests use an executable/ops shape |
| `complexity` | measured | a paired profiler compares growth against a reference; 127 items |
| `style` | judged | advisory radon/ruff findings; never the correctness verdict |

`variant` and `grade` are declared for future use but are deliberately not attached to
item evaluators. The default dojo grade policy turns the evidence into grades 1–4.

The evaluator server is a stdio MCP process (six tools via `assessment.v1`). It runs
the submitted code in a separate interpreter with a timeout, so a broken or hostile
solution cannot crash the server. A failing or unresolved submission is still recorded;
it does not create a card, so the item stays in the queue.

The manifest owns the assurance, not the tool result. A tool cannot upgrade its own
evidence. A review cannot change a grade, card or evidence row.

## The session

1. **Solve.** The statement is shown; `open` edits `solution.py`; `check` runs the visible
   check. Any free text is a tutor question. The tutor sees the statement, current files,
   visible check output and prior turns; it never sees evidence, hidden cases or a
   reference solution. Every answer goes through the leak auditor and the ordered hint
   ladder; a blocked answer is withheld.
2. **Submit.** dojo asks for time and space complexity with a justification. Those answers
   become the attempt's claims and go to the evaluators and reviewer. Then dojo snapshots
   the workspace, calls the evaluator tools, records evidence, applies the grade and
   updates the FSRS card.
3. **Review.** The A2A reviewer receives the review view (statement, submitted files,
   evidence, grade and claims) and returns a `ReviewResult`: summary, strengths,
   improvements, next steps and optional quality. It is advisory.
4. **Discuss.** The session stays open with the reviewer. Ask about the approach,
   evidence, complexity or trade-offs; `polish` returns to the editor, and a resubmit
   records another revision and returns to discussion. `done` ends.
5. **Review later.** `dojo progress` shows the roadmap; `dojo history` lists attempts;
   `dojo show <n>` prints the saved solution, evidence, claims, review, conversation and
   snapshot timeline.

The curriculum also supplies `learn` (the topic teacher, which never sees the item
statement or your files) and the discussion prompt. The engine owns the session, FSRS, the
database, the model gateway and the terminal.

## Why it is rigorous

- **Correctness is evidence, not a self-report.** Private cases and optional oracles
  decide the grade; the style evaluator is advisory.
- **Complexity is measured where possible.** The profiler compares growth with a reference,
  and the reviewer can flag a claim that is looser than the measurement.
- **The visible check is not the hidden check.** It covers the examples; the private
  evaluator adds cases the check deliberately does not cover.
- **The reviewer cannot rescue a wrong solution.** The grade is already stored before the
  review is requested; the review can explain, not change.
- **Hints are gated.** The tutor can only reveal the next level, and the leak auditor fails
  closed.

## Privacy and copyright

`license = "private"` means **never publish**. The statements are LeetCode's, reproduced
from a community mirror; the assessment tree is the answers in machine form. The private
cases, oracles, references and reviewer rubric must never reach a student, the in-solve
tutor, the teacher or the leak auditor.

The reviewer sees only the review view. It never sees hidden tests, a reference solution
or your history. The engine's model gateway never sends `DOJO_API_KEY` to the curriculum's
MCP server; the curriculum's reviewer reads the same settings file and key read-only.
