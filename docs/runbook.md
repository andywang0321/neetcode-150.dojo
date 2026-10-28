# NeetCode 150 dojo — phase-5 manual runbook

This is the human test guide for the rebuilt dojo engine (phases 1-4) and the
`neetcode-150.dojo` curriculum (phase 5, including the P5-C A2A reviewer). It walks
through installation, enrollment, a real practice session, tutor/teacher/hint behaviour,
progress and history, the A2A review, the failure paths and the test suites.

**Phase 6 is not in this runbook.** The cutover (backup, renaming the engine and
curriculum, force-pushing, starting the fresh database and discarding the old history) is
a separate, explicitly destructive step. Nothing here touches the old `dojo` engine or the
old `dojo-curriculum-neetcode-150` repository.

Every command is exact for this machine. The only variable you choose is `$P5D`, the
directory that holds the isolated test data; `$ENGINE` and `$CURRICULUM` are the two
checkouts from section 2.

## 1. What you are testing

| piece | location | what it is |
|---|---|---|
| engine | `/Users/andywang/Projects/dojo-workspace/rebuild` | dojo phases 1-4: CLI, session, SQLite, MCP client, A2A client |
| curriculum | `/Users/andywang/Projects/dojo-workspace/neetcode-150.dojo` | 18 topics, 157 items (152 active, 5 retired), 6 evaluators, prompts, hint ladder |
| MCP evaluator server | `$CURRICULUM/src/neetcode_dojo/server.py` | `assess.tests`, `assess.oracle`, `assess.complexity`, `assess.style`, `variant`, `grade` |
| reviewer | `$CURRICULUM/reviewer/` | the P5-C A2A agent, one `review` skill, port 8766 |
| reference A2A agent (optional) | `$ENGINE/curriculum-kit/a2a-reviewer` | the engine's phase-4 reference agent, port 8765 |

The curriculum is private: `license = "private"`, no remote, never publish. The
statements are LeetCode's and the assessment tree is the answers in machine form.

## 2. Prerequisites

- macOS on this machine.
- Python 3.15 through `uv` (the repository's `.python-version` pins 3.15; `uv` downloads
  it on first sync if needed).
- `uv >= 0.13`. Check:

```bash
uv --version
# uv 0.13.6 (Homebrew 2026-10-26 aarch64-apple-darwin)
```

- The two checkouts. During P5-D the curriculum is the branch worktree
  `/Users/andywang/Projects/dojo-workspace/worktrees/neetcode/integration`; after the
  merge it is `/Users/andywang/Projects/dojo-workspace/neetcode-150.dojo`. The commands
  below use `$CURRICULUM`, so set it to the checkout you are testing:

```bash
export ENGINE=/Users/andywang/Projects/dojo-workspace/rebuild
export CURRICULUM=/Users/andywang/Projects/dojo-workspace/neetcode-150.dojo
# P5-D branch testing only:
# export CURRICULUM=/Users/andywang/Projects/dojo-workspace/worktrees/neetcode/integration
export UV_CACHE_DIR=/Users/andywang/Projects/dojo-workspace/.uv-cache
```

- No network beyond loopback and no API key are required. The reviewer and the MCP
  server are local. The test suites use only loopback HTTP doubles and no real provider.
- Enough disk for `.venv`, the uv cache and the test data (well under 1 GB).

## 3. Sync the engine, the curriculum and the reviewer

The reviewer is part of the curriculum's uv environment; it has no second lockfile or
virtualenv.

```bash
cd "$ENGINE"
uv sync

cd "$CURRICULUM"
uv sync

# optional: the engine's phase-4 reference agent (its own project, 17 tests)
cd "$ENGINE/curriculum-kit/a2a-reviewer"
uv sync
```

Quick sanity checks:

```bash
cd "$ENGINE"
uv run dojo --version          # dojo 0.1.0

cd "$CURRICULUM"
uv run python -c "import neetcode_dojo, reviewer; print('imports ok')"
```

Why the curriculum's server works without dojo installing it: the manifest's
`[server].command` is `["uv", "run", "--project", ".", "python", "-m",
"neetcode_dojo.server"]`, and dojo runs it with the curriculum root as the working
directory. dojo inherits only `PATH`, `HOME`, `SHELL`, `TERM`, `USER`, `LOGNAME` and the
`UV_*` cache settings into that child; it never forwards a provider key.

## 4. An isolated test profile and settings

Use a throwaway directory so the test cannot touch your real dojo database or history:

```bash
export P5D="$HOME/dojo-p5d"
mkdir -p "$P5D/data" "$P5D/config" "$P5D/workbench"
export DOJO_DATA_DIR="$P5D/data"
export DOJO_CONFIG_DIR="$P5D/config"
export DOJO_WORKBENCH_DIR="$P5D/workbench"
```

The defaults, when these are unset, are:

| setting | default |
|---|---|
| database | `~/.local/share/dojo/dojo.db` (`$XDG_DATA_HOME/dojo/dojo.db`) |
| curricula | `~/.local/share/dojo/curricula/<id>` |
| workbench | `~/.local/share/dojo/workbench` |
| settings | `~/.config/dojo/settings.toml` (`$XDG_CONFIG_HOME/dojo/settings.toml`) |

Create `$P5D/config/settings.toml` with the offline provider and your editor. The mock
provider needs no key and makes the whole LLM path deterministic:

```bash
cat > "$P5D/config/settings.toml" <<'EOF'
# dojo settings. API keys stay in the environment, never in this file.
[editor]
command = "code --wait"          # or "vim", "nano", or your editor; omit to use $VISUAL/$EDITOR

[llm]
provider = "mock"
model = "mock"

[models]
tutor = "mock"
teacher = "mock"
reviewer = "mock"
auditor = "mock"

[study]
warmup_budget = 2
EOF
```

If you want a real provider instead, set `provider`/`model` and `base_url` in `[llm]`,
point `[models]` at real model names, and export the matching key (`DEEPSEEK_API_KEY`,
`OPENAI_API_KEY` or `ANTHROPIC_API_KEY`). The key never goes in the settings file.
Provider `mock` is the recommended first run. The optional reviewer model is configured
per process in section 5.

`dojo` opens the editor on the session workspace at the start of a session; `check` runs
in that workspace. If no editor is configured, `dojo` prints a warning and you can edit
`$DOJO_WORKBENCH_DIR/neetcode-150/<item>/<session>/solution.py` in a second terminal.

## 5. Start the NeetCode A2A reviewer

Terminal 1 (leave it running; stop with Ctrl-C):

```bash
cd "$CURRICULUM"
export UV_CACHE_DIR=/Users/andywang/Projects/dojo-workspace/.uv-cache
uv run python -m reviewer.server
```

Expected first line:

```text
NeetCode 150 reviewer listening on http://127.0.0.1:8766/ (deterministic, no model key)
```

The agent serves:

| endpoint | value |
|---|---|
| agent card | `GET http://127.0.0.1:8766/.well-known/agent-card.json` |
| A2A JSON-RPC | `POST http://127.0.0.1:8766/` (protocol v1.0, `JSONRPC` binding, `SendMessage`) |
| skill | `review` |

Verify the card and skill from another terminal:

```bash
curl -sS http://127.0.0.1:8766/.well-known/agent-card.json | python3 -m json.tool
# "name": "NeetCode 150 reviewer"
# "skills": [{"id": "review", ...}]
```

The reviewer is deterministic by default and needs no key. To let it write the review
prose with an OpenAI-compatible model, set `DOJO_REVIEWER_API_KEY` (or `OPENAI_API_KEY`),
optionally `DOJO_REVIEWER_BASE_URL` (default `https://api.openai.com/v1`) and
`DOJO_REVIEWER_MODEL` (default `gpt-4o-mini`), and restart it. The rubric still owns the
advisory `quality` score and the review never changes the grade. Leave the key unset for
the offline test.

This is the contract the manifest already declares:

```toml
[agents.reviewer]
url = "http://127.0.0.1:8766/"

[capabilities.review]
impl = "a2a"
agent = "reviewer"
skill = "review"
```

dojo never starts, stops or authenticates this process.

## 6. Enroll the curriculum

Terminal 2:

```bash
cd "$ENGINE"
export UV_CACHE_DIR=/Users/andywang/Projects/dojo-workspace/.uv-cache
export DOJO_DATA_DIR="$HOME/dojo-p5d/data"
export DOJO_CONFIG_DIR="$HOME/dojo-p5d/config"
export DOJO_WORKBENCH_DIR="$HOME/dojo-p5d/workbench"

uv run dojo enroll "$CURRICULUM"
```

Expected output:

```text
Enrolled NeetCode 150 (neetcode-150)
  version: 0.1.0
  items: 157
  path: /Users/andywang/Projects/dojo-workspace/neetcode-150.dojo   # or your $CURRICULUM
  active: yes
```

Enrollment does the two live probes:

1. starts the curriculum's stdio MCP server and verifies all six declared tools
   (`assess.tests`, `assess.oracle`, `assess.complexity`, `assess.style`, `variant`,
   `grade`);
2. fetches the reviewer card at `/.well-known/agent-card.json` and verifies the `review`
   skill.

It also statically validates all 157 item statements/workspaces and writes the catalog
(18 topics, 157 items; 5 retired items are addressable but not served). Check the catalog:

```bash
uv run dojo curricula
```

```text
Curricula
┏━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┓
┃ active ┃ id           ┃ title        ┃ version ┃ items ┃ path                ┃
┡━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━┩
│ *      │ neetcode-150 │ NeetCode 150 │ 0.1.0   │ 152   │ /Users/andywang/Pr… │
└────────┴──────────────┴──────────────┴─────────┴───────┴─────────────────────┘
```

`items: 152` is the active count; the corpus is 157 with 5 retired duplicates
(`array_intersection`, `peak_elements`, `mirror_image_binary_tree`,
`k_smallest_elem_matrix`, `max_prod_3_nums`). Re-enrolling the same local path is how you
refresh the catalog after a curriculum change (the installer reuses the symlink).

If the reviewer is down at this point, enrollment refuses and enrolls nothing:

```text
error: cannot verify A2A agent 'reviewer': cannot read the agent card at
http://127.0.0.1:8766/: Network communication error fetching agent card ...
not enrolled, the installed files are kept
```

## 7. A real practice session: contains_duplicate

`dojo` serves the first unlocked item, which is `contains_duplicate` in Arrays & Hashing.
It has all four item evaluators: `tests`, `oracle`, `complexity` (measured) and `style`
(advisory, assurance `judged`).

```bash
cd "$ENGINE"
export UV_CACHE_DIR=/Users/andywang/Projects/dojo-workspace/.uv-cache
export DOJO_DATA_DIR="$HOME/dojo-p5d/data"
export DOJO_CONFIG_DIR="$HOME/dojo-p5d/config"
export DOJO_WORKBENCH_DIR="$HOME/dojo-p5d/workbench"
uv run dojo
```

Expected start:

```text
NeetCode 150 · Contains Duplicate
workspace: /Users/you/dojo-p5d/workbench/neetcode-150/contains_duplicate/<session>

Given an integer array nums, return true if any value appears more than once ...
Commands:
  open       open the workspace in your editor
  check      run the item's check command
  submit     assess the workspace and end the session
  learn      learn the topic with the teacher, then `practice`
  quit       abandon the session; nothing is recorded
  statement  print the statement again
  help       this list
Any other text asks the tutor at your current hint level.
dojo>
```

Replace the stub in `solution.py` with a correct solution, save and close the editor. For
this runbook a set is enough:

```python
def contains_duplicate(nums: list[int]) -> bool:
    seen = set()
    for value in nums:
        if value in seen:
            return True
        seen.add(value)
    return False
```

At the `dojo>` prompt:

```text
dojo> check
check exited 0
4 of 4 visible checks passed
```

Before you submit, you can run section 8's mock tutor/`learn` flow in this same session
(it works on the current workspace and abandons the session at `practice`); otherwise
skip it and submit now. After a passing submit the card is scheduled in 2 days, so this
item is not served again until it is due.

```text
dojo> submit
```

Expected evidence and grade (timings and the last decimals vary):

```text
Evidence
┏━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ evaluator  ┃ assurance ┃ outcome ┃ summary                                   ┃
┡━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ tests      │ machine   │ pass    │ 26/26 private cases passed                │
│ oracle     │ machine   │ pass    │ 26/26 private cases passed                │
│ complexity │ measured  │ pass    │ time like the reference (1.17x); space    │
│            │           │         │ like the reference                        │
│ style      │ judged    │ pass    │ no advisory style flags                   │
└────────────┴───────────┴─────────┴───────────────────────────────────────────┘
Grade: 3 (pass)
Next review: <date> (in 2 days)
review · advisory, the grade stands
Summary: Review of contains_duplicate in neetcode-150: grade 3 (pass); 4 of 4 evaluator
reports passed. The code reads as Arrays & Hashing and uses a set for O(1) membership ...
Strengths: ...
Improvements: ...
Next steps: ...
Quality: 0.76/1
```

What to verify in the database (SQLite is fine; the engine uses one file):

```bash
python3 - "$DOJO_DATA_DIR/dojo.db" <<'PY'
import sqlite3, sys

db = sqlite3.connect(sys.argv[1])
db.row_factory = sqlite3.Row
for sql in (
    "select item_id, grade, outcome from attempts",
    "select evaluator_id, assurance, outcome from evidence order by evidence_id",
    "select item_id, reps, stability, difficulty from cards",
    "select agent from reviews",
    "select purpose, provider, model from ai_calls order by call_id",
):
    print(sql)
    for row in db.execute(sql):
        print(" ", dict(row))
PY
```

Expected:

- one `attempts` row, `contains_duplicate`, grade 3, outcome `pass`;
- four `evidence` rows: `tests`/`machine`/`pass`, `oracle`/`machine`/`pass`,
  `complexity`/`measured`/`pass`, `style`/`judged`/`pass`;
- one `cards` row, reps 1, next review in 2 days (FSRS);
- one `reviews` row with `agent = reviewer/review` (the P5-C agent), not `reviewer`;
- one `ai_calls` row with `purpose = reviewer`, `provider = a2a`,
  `model = reviewer/review` and a 64-character SHA-256; the tutor/auditor/teacher rows
  exist only if you asked the agents.

The A2A review is advisory. It has no grade field, `review()` only reads the grade, and
the engine saves it after the attempt/card/evidence are already committed. To prove that
from the database, note the `attempts.grade = 3` row and the review's `quality` value; the
review never rewrites either.

### Why grade 3 and not 4

The engine's default policy grades from the required evidence: `tests` is the only
required evaluator, so all-pass is grade 3. Grade 4 is a curriculum judgement (claims
corroborated by measured evidence) and the curriculum's `grade` tool is declared but
deliberately not attached to items in P5. `complexity` and `style` remain advisory
evidence; a partial measured reading shows up in the evidence and the review without
silently changing the grade.

## 8. Tutor, teacher, hints and `learn` / `practice`

Do this in a session **before** its submit (section 7), or in a fresh profile: after a
passing submit the item is scheduled and is not served again until it is due. The
transcript below is from the run before the submit. With the mock provider, inside the
same session, type a question:

```text
dojo> why does a set help here?
tutor · level 0 (articulate the blockage)
Mock tutor: try the simplest example first, then check what happens at the edges.
```

The answer was leak-audited and the hint level advanced from 0 to 1. The hint ladder is
`$CURRICULUM/policies/hints.toml`; the reset markers `stuck` and `no idea` move that
answer back to level 0. A withheld answer never advances the level.

Type `learn` to hand the topic to the teacher. The practice session is abandoned and the
teacher never sees the item statement:

```text
dojo> learn
learn · NeetCode 150 · Arrays & Hashing
0/152 exercises done. Recent grades, newest first: none yet.
learn> what is an invariant?
teacher · Arrays & Hashing
Mock teacher: state the invariant in one sentence, then test it on a small input.
learn> practice
Starting a fresh practice session.
```

`practice` starts a fresh session on the next unsolved item — on this first run that is
`contains_duplicate` again. The editor opens a new workspace with the starter stub; write
the solution again before `check`/`submit`. `done` or `quit` leaves the teacher loop. The
abandoned session keeps its hint level and is not an attempt.

With **no LLM key**, the agents report unavailable and practice continues. Use a separate
profile: repeat section 4 with `P5D="$HOME/dojo-p5d-nokey"`, set `[llm] provider =
"deepseek"`, `model = "deepseek-chat"`, leave `DEEPSEEK_API_KEY` (and the other provider
keys) unset, enroll, and start a session. The same commands from section 7 still work.

```text
dojo> why does a set help here?
tutor · withheld
The answer was not shown: the tutor is unavailable: DEEPSEEK_API_KEY is not set; export it
or set [llm] provider = 'mock' to run offline
The hint level is unchanged. Ask again, or type `help`.
dojo> learn
learn> what is an invariant?
teacher unavailable: the teacher is unavailable: DEEPSEEK_API_KEY is not set; ...
The learn loop continues; `practice`, `done` and `quit` still work.
learn> practice
dojo> check
dojo> submit
```

The submission still grades and cards; only the LLM agents are unavailable. The A2A
review still works if the reviewer is running.

### Blocked leak-auditor check (optional, loopback stub)

With the mock provider the auditor always returns `allow`, so a block is not visible. To
see the withhold path live, run a tiny OpenAI-compatible stub that answers tutor requests
with a leak and always blocks the audit. Terminal 3:

```bash
cat > /tmp/p5d-block-stub.py <<'PY'
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class Handler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        length = int(self.headers["Content-Length"])
        request = json.loads(self.rfile.read(length) or b"{}")
        if request.get("response_format", {}).get("type") == "json_object":
            content = '{"verdict": "block", "reason": "the answer gives away the solution"}'
        else:
            content = "Return len(nums) != len(set(nums)) -- that is the whole answer."
        payload = json.dumps({"choices": [{"message": {"content": content}}]}).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format: str, *args: object) -> None:
        pass


ThreadingHTTPServer(("127.0.0.1", 8799), Handler).serve_forever()
PY
python3 /tmp/p5d-block-stub.py
```

In a separate profile (rerun section 4 with `$P5D` plus `-block`), set:

```toml
[llm]
provider = "openai"
model = "p5d-stub"
base_url = "http://127.0.0.1:8799/v1"
```

and export `OPENAI_API_KEY=stub-key`. Enroll, start a session and ask a question:

```text
dojo> how do I solve this?
tutor · withheld
The answer was not shown: the answer gives away the solution
The hint level is unchanged. Ask again, or type `help`.
```

The student turn and the tutor/auditor provenance are recorded; no tutor turn is stored
and the level does not move. Stop the stub with Ctrl-C.

## 9. Progress, history, curricula, settings and unenroll

```bash
cd "$ENGINE"
# with the same DOJO_* exports as section 7
uv run dojo progress neetcode-150
```

The roadmap prints all 18 patterns and every item with its status (`done`, `next`, `open`,
`locked`, `retired`), plus the `neetcode-150: N/152 done` line. Retired items are shown
but not counted or served. This is the full-corpus smoke: the catalog has all 157 items
and all their statements/workspaces resolved.

```bash
uv run dojo history
```

```text
History
┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━┓
┃ date             ┃ curriculum   ┃ item                     ┃ grade ┃ outcome ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━┩
│ 2026-10-27 23:10 │ neetcode-150 │ Contains Duplicate       │ 3     │ pass    │
└──────────────────┴──────────────┴──────────────────────────┴───────┴─────────┘
```

```bash
uv run dojo settings
```

`settings` opens `$DOJO_CONFIG_DIR/settings.toml` in the configured editor. If you set
`[editor] command = "cat"` in a throwaway profile, it prints the file and the path
instead. The file never contains a key.

```bash
uv run dojo unenroll neetcode-150
```

```text
Unenrolled neetcode-150. Installed files and history are kept.
No active curriculum. Run `dojo enroll <path-or-url>` to add one.
```

`unenroll` pauses the enrollment; `dojo history` still shows the attempts and the
installed symlink stays. Re-enroll with the same command to resume.

## 10. The failure paths

Run these in order; each one is a boundary check.

### 10.1 Reviewer down at enrollment

Stop the reviewer (Ctrl-C) and enroll into a fresh profile:

```bash
export P5D="$HOME/dojo-p5d-down"
export DOJO_DATA_DIR="$P5D/data" DOJO_CONFIG_DIR="$P5D/config" DOJO_WORKBENCH_DIR="$P5D/workbench"
mkdir -p "$DOJO_DATA_DIR" "$DOJO_CONFIG_DIR" "$DOJO_WORKBENCH_DIR"
cp "$HOME/dojo-p5d/config/settings.toml" "$DOJO_CONFIG_DIR/settings.toml"
cd "$ENGINE"
uv run dojo enroll "$CURRICULUM"
```

Expected: exit code 1 and one clear error naming the card URL, ending
`not enrolled, the installed files are kept`. The installer leaves the
`$DOJO_DATA_DIR/curricula/neetcode-150` symlink, and the database has zero `curricula`
rows. Restart the reviewer for the next checks.

### 10.2 Reviewer stopped after enrollment

Enroll while it is up, then stop the reviewer and submit an item (for example the next
`dojo` session):

```text
dojo> submit
Grade: 3 (pass)
Next review: <date>
review unavailable: the review failed: Network communication error fetching agent card
from http://127.0.0.1:8766/.well-known/agent-card.json: All connection attempts failed
```

The attempt, grade, evidence and card are recorded; no `reviews` row and no `reviewer`
`ai_calls` row for that attempt are written. Restart the reviewer and submit another item
to see the review return.

### 10.3 No LLM key

Section 8. `check` and `submit` work; the tutor/teacher report unavailable; the A2A
review works if the reviewer is up. The practice loop never depends on a provider.

### 10.4 Blocked leak audit

Section 8's optional stub. The answer is withheld, the hint level is unchanged, and the
student turn/provenance are kept.

## 11. Test suites and static checks

From the curriculum checkout:

```bash
cd "$CURRICULUM"
export UV_CACHE_DIR=/Users/andywang/Projects/dojo-workspace/.uv-cache
uv sync
uv run pytest                 # 346: 223 curriculum + 123 reviewer
uv run pytest tests           # 223
uv run pytest reviewer/tests  # 123
uv run ruff check .
uv run ruff format --check .
uv run ty check .
```

`ty` excludes only `content/` and `src/neetcode_dojo/assessment/`; everything else is
checked.

From the engine checkout (read-only for P5-D):

```bash
cd "$ENGINE"
uv run pytest                 # 493
uv run ruff check .
uv run ty check .
uv run ruff format --check .  # see the known-issue note below
```

Known issue: the engine's `uv run ruff format --check .` reports one pre-existing
Markdown file, `docs/phase-2.md` (a Python code block in the read-only docs). It is not
caused by this curriculum and the engine is not edited here.

The optional reference agent:

```bash
cd "$ENGINE/curriculum-kit/a2a-reviewer"
uv run pytest                 # 17
```

The suites are offline: no network, no API key, no bound port. The reviewer tests use
`httpx.ASGITransport` against the real ASGI app; the evaluator tests use subprocesses and
fixture assessment trees.

## 12. Sampling the evaluator shapes

The end-to-end run covers `contains_duplicate` (tests + oracle + measured complexity +
advisory style) and the A2A review. Two more shapes are worth checking:

- **Predicate item** (`encode_and_decode_strings`): the private cases are decided by the
  registered `encode_decode_roundtrip` checker. The visible `check.py` intentionally
  skips predicate cases, so `check` prints `0 of 5 visible checks passed` and exits 0;
  that is the content's visible-check design, not a failure. The engine's `submit` runs
  the private checker and reports `26/26 private cases passed`.
- **Measured complexity**: `contains_duplicate`'s table above is the measured evidence;
  `valid_palindrome` is an example where the space growth is `partial` while the required
  tests pass (still grade 3, advisory evidence).

To exercise the predicate evaluator through the real MCP server without walking the
roadmap, run this from the engine checkout:

```bash
cd "$ENGINE"
uv run python - <<'PY'
import os
from pathlib import Path

from dojo.adapters.mcp import McpAssessor
from dojo.protocol.contracts import AssessmentRequest, SubmissionFile
from dojo.protocol.manifest import load_manifest

root = Path(os.environ["CURRICULUM"])
curriculum = load_manifest(root)
item = next(item for item in curriculum.items if item.id == "encode_and_decode_strings")
source = '''def encode(strs: list[str]) -> str:
    return "".join(f"{len(word)}:{word}" for word in strs)


def decode(s: str) -> list[str]:
    words = []
    index = 0
    while index < len(s):
        colon = s.index(":", index)
        length = int(s[index:colon])
        start = colon + 1
        words.append(s[start:start + length])
        index = start + length
    return words
'''
evaluators = tuple(e for e in curriculum.evaluators if e.id in item.evaluators)
request = AssessmentRequest(
    curriculum=curriculum.id,
    item=item.id,
    files=(SubmissionFile(path="solution.py", content=source),),
    claims={},
)
for evaluator, result in zip(
    evaluators, McpAssessor().assess(curriculum, request, evaluators), strict=True
):
    print(f"{evaluator.id}: {result.outcome} | {result.summary}")
PY
```

Expected:

```text
tests: pass | 26/26 private cases passed
style: pass | no advisory style flags
```

The same server answers the six tools; enrollment already listed all six.

## 13. Data locations, cleanup and privacy

The isolated profile is entirely under `$P5D`:

| path | contents |
|---|---|
| `$P5D/data/dojo.db` | SQLite: catalog, sessions, attempts, evidence, cards, reviews, AI provenance |
| `$P5D/data/curricula/neetcode-150` | symlink to `$CURRICULUM` (a local install) |
| `$P5D/workbench/neetcode-150/<item>/<session>/` | the student's workspace snapshots |
| `$P5D/config/settings.toml` | editor/provider/models; never a key |

Cleanup after testing:

```bash
# stop the reviewer (Ctrl-C in terminal 1) and any stub (section 8)
rm -rf "$HOME/dojo-p5d" "$HOME/dojo-p5d-down" "$HOME/dojo-p5d-nokey" "$HOME/dojo-p5d-block"
```

Do not commit a database, an attempt log, a workbench file, a `.env` or an API key. The
repository's `.gitignore` covers `.venv/`, caches and `.env`; do not add the test data
either.

Privacy and the data boundary:

- The statements are LeetCode's, reproduced from a community mirror. The repository is
  `license = "private"` and has no remote; **never publish it**, and do not quote
  statements into a public issue or chat.
- The assessment tree (`src/neetcode_dojo/assessment/`), private cases, oracles,
  references and the measurement plans never reach a student, the in-solve tutor, the
  teacher or the leak auditor.
- The reviewer receives exactly the review view: statement, submitted files, evidence,
  grade and claims. It never receives the assessment tree, hidden cases, references or
  history. The `review.v1` request rejects extra fields, and `reviewer/tests/test_boundary.py`
  checks the reviewer's production modules for file reads and imports into the private
  tree.
- The MCP server child inherits no provider key. In the offline setup above, no request
  leaves the machine; the only outbound requests are the configured LLM provider calls,
  including the reviewer's optional one, and only when you set a key.

## 14. What "good" looks like

- `uv sync` succeeds in the engine, the curriculum and the optional reference agent.
- The reviewer serves `NeetCode 150 reviewer` with the `review` skill on 8766.
- `dojo enroll` prints `Enrolled NeetCode 150 (neetcode-150)`, `items: 157`, `active: yes`.
- `dojo curricula` shows 152 active items; `dojo progress` lists 18 patterns and every
  item, with the 5 retired ones marked `retired`.
- `check` is 0 and `submit` reports `tests`/`oracle`/`complexity`/`style` with the
  manifest's assurance (`machine`, `machine`, `measured`, `judged`), grade 3 and a card.
- The review is advisory, comes from `reviewer/review`, and is stored with
  `provider = a2a`; the attempt/card are untouched.
- With the reviewer down after enrollment, submit still records grade/card/attempt and
  prints `review unavailable`.
- With no LLM key, the agents report unavailable and check/submit still work.
- The curriculum suite is 346 (223 + 123), `ruff` and `ty` are clean; the engine is 493
  and clean apart from the pre-existing `docs/phase-2.md` formatting note.
- No private material appears in any prompt, workspace, review request or committed file.

## 15. Phase 6

The cutover is separate: back up the old `dojo` and old curriculum, rename the rebuild,
force-push the new engine over the old `dojo`, rename the new curriculum repository, start
the fresh single-user database and discard the old history. Do not run it as part of this
runbook. The phase-5 result above is the gate for that decision.
