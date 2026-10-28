# NeetCode 150 dojo — phase-6 manual runbook

This is the human test guide for the rebuilt dojo engine (phases 1-4 plus the P6-A/B
one-provider setup) and the `neetcode-150.dojo` curriculum (phase 5 plus the P6-C A2A
reviewer). It walks through installation, the first-run setup wizard, the one settings
file, the reviewer, enrollment, a real practice session, tutor/teacher/hint behaviour,
progress and history, the failure paths, the test suites and the data/privacy boundary.

**The phase-6 cutover is not in this runbook.** The cutover (backup, renaming the engine
and curriculum, force-pushing, starting the fresh database and discarding the old history)
is a separate, explicitly destructive step. Nothing here touches the old `dojo` engine or
the old `dojo-curriculum-neetcode-150` repository.

Every command is exact for this machine. The only variable you choose is `$P6D`, the
directory that holds the isolated test data; `$ENGINE` and `$CURRICULUM` are the two
checkouts from section 2.

## 1. What you are testing

| piece | location | what it is |
|---|---|---|
| engine | `/Users/andywang/Projects/dojo-workspace/rebuild` | dojo phases 1-4 and P6-A/B: CLI, first-run setup, one model gateway, session, SQLite, MCP client, A2A client |
| curriculum | `/Users/andywang/Projects/dojo-workspace/neetcode-150.dojo` | 18 topics, 157 items (152 active, 5 retired), 6 evaluators, prompts, hint ladder |
| MCP evaluator server | `$CURRICULUM/src/neetcode_dojo/server.py` | `assess.tests`, `assess.oracle`, `assess.complexity`, `assess.style`, `variant`, `grade` |
| reviewer | `$CURRICULUM/reviewer/` | the P6-C A2A agent, one `review` skill, port 8766; it reads the engine's one settings file and key |
| reference A2A agent (optional) | `$ENGINE/curriculum-kit/a2a-reviewer` | the engine's phase-4 reference agent, port 8765 |

The engine and the reviewer share **one provider**, **one `DOJO_API_KEY`** and **one
`settings.toml`**. There is no username and no second key. The key lives in the
environment (the first-run wizard exports it in your shell rc); it never enters the
settings file, the database or this repository.

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

- The two checkouts. During P6-D the curriculum is the branch worktree
  `/Users/andywang/Projects/dojo-workspace/worktrees/neetcode/docs`; after the merge it
  is `/Users/andywang/Projects/dojo-workspace/neetcode-150.dojo`. The commands below use
  `$CURRICULUM`, so set it to the checkout you are testing:

```bash
export ENGINE=/Users/andywang/Projects/dojo-workspace/rebuild
export CURRICULUM=/Users/andywang/Projects/dojo-workspace/neetcode-150.dojo
# P6-D branch testing only:
# export CURRICULUM=/Users/andywang/Projects/dojo-workspace/worktrees/neetcode/docs
export UV_CACHE_DIR=/Users/andywang/Projects/dojo-workspace/.uv-cache
```

- Network: the reviewer and the MCP server are local (loopback only). A **live** provider
  (deepseek, openai or anthropic) additionally sends model calls to that provider; the
  first-run key validation is one such call. The `mock` provider needs no network and no
  key. The test suites are fully offline.
- Enough disk for `.venv`, the uv cache and the test data (well under 1 GB).

## 3. Sync the engine, the curriculum and the reference agent

The reviewer is part of the curriculum's uv environment; it has no second lockfile, key or
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
directory. The child environment is a small allowlist (`UV_CACHE_DIR`,
`UV_PYTHON_INSTALL_DIR`, `XDG_CACHE_HOME`, `UV_OFFLINE`); dojo never forwards
`DOJO_API_KEY` or any other secret to it.

## 4. First-run setup: one provider, one key, one settings file

On a machine without a config, the first `dojo` in a terminal runs a setup wizard **before
any command** and then exits, so the next command runs in a shell that has
`DOJO_API_KEY`. It asks only for what the one-config design needs:

1. the provider (`deepseek`, `openai`, `anthropic` or `mock`; default `deepseek`);
2. an optional base URL (for a local OpenAI-compatible server);
3. the provider's default model (accepted with Enter);
4. an optional editor command;
5. the hidden `DOJO_API_KEY` — validated with one tiny model request (not for `mock`).

It then writes `settings.toml` atomically, adds the key to your shell rc in a marked,
backed-up block, prints a summary and exits. Re-running only rewrites dojo's marked block,
so the rc edit is idempotent. There is no username prompt and no per-provider key.

### 4.1 The wizard

From the engine checkout, in a real terminal:

```bash
cd "$ENGINE"
export UV_CACHE_DIR=/Users/andywang/Projects/dojo-workspace/.uv-cache
uv run dojo
```

Expected transcript (the key is hidden; Enter accepts the bracketed default):

```text
Welcome to dojo. This sets up the model gateway and your editor.
Press Enter to accept the value in brackets.
Provider (deepseek/openai/anthropic/mock) [deepseek]:
Base URL (optional; Enter for the provider default):
Model [deepseek-chat]:
Editor command (optional, e.g. code --wait): code --wait
API key (DOJO_API_KEY):
Validating the key...

Setup complete.
  settings: /Users/andywang/.config/dojo/settings.toml
  editor:   code --wait
  provider: deepseek (model deepseek-chat)
  shell:    /Users/andywang/.zshrc (backup: /Users/andywang/.zshrc.dojo-backup)

setup complete; close this terminal and open a new one
```

What to notice:

- **Validation.** The wizard sends one 8-token request (`Reply with the single word ok.`)
  to the selected model with a 20-second timeout. A failure prints
  `Key validation failed: <error>` (the key is redacted) and asks
  `Try again with a different key? [n]:`. Answering `n` prints
  `Setup aborted; nothing was written.` and exits 1. An empty key re-prompts with
  `An API key is required for this provider.`
- **Atomic config.** The settings file is written through a temporary file and a rename;
  a failed write leaves the previous file and no partial config.
- **Shell rc.** For zsh the block is appended to `~/.zshrc`; bash uses `~/.bashrc` and
  fish uses `~/.config/fish/config.fish` (an unknown `$SHELL` defaults to zsh). The block
  is marked and the first edit backs the file up once:

  ```text
  # >>> dojo setup >>>
  export DOJO_API_KEY=...
  # <<< dojo setup <<<
  ```

  Fish uses `set -gx DOJO_API_KEY '...'`. A re-run replaces only the marked block; the
  backup is not overwritten.
- **It does not run your command.** The wizard exits after the summary. The command you
  typed (for example `dojo enroll ...`) does **not** continue.
- **Open a new terminal.** `DOJO_API_KEY` is exported by the rc, not by the current
  shell. Close this terminal, open a new one and check:

  ```bash
  test -n "$DOJO_API_KEY" && echo "DOJO_API_KEY is set"
  ```

### 4.2 The one `settings.toml`

The wizard writes `$DOJO_CONFIG_DIR/settings.toml`, or the engine's default
`$XDG_CONFIG_HOME/dojo/settings.toml` (`~/.config/dojo/settings.toml`). It never contains
a key. After first-run setup and an enrollment, the file looks like this (the reviewer
table is optional; section 4.3 adds it):

```toml
# dojo settings. API keys stay in the environment, never in this file.
# One provider for every curriculum: deepseek, openai, anthropic
# (key: export DOJO_API_KEY=...) or mock (offline, no key).

[editor]
command = "code --wait"

[llm]
provider = "deepseek"
model = "deepseek-chat"
# base_url = "http://localhost:8080/v1"   # optional; override for a local server

# Optional per-role model overrides; each falls back to [llm].model.
[models]

[study]
curriculum = "neetcode-150"
warmup_budget = 2

[curricula.neetcode-150]

[curricula.neetcode-150.reviewer]
model = "deepseek-reasoner"
```

The same table can be written with a quoted curriculum id; TOML treats the two forms
identically, and the reviewer reads either:

```toml
[curricula."neetcode-150".reviewer]
model = "deepseek-reasoner"
```

- `[llm].provider` is global: one choice serves the engine's tutor, teacher, auditor and
  fallback reviewer **and** the A2A reviewer. `[llm].model` defaults to the provider's
  default (`deepseek-chat`, `gpt-4.1-mini`, `claude-sonnet-4-5`, `mock`).
- `[editor].command` is the editor dojo launches. `DOJO_EDITOR` overrides it for one
  shell; `$EDITOR` and `$VISUAL` are deliberately not read.
- `[models]` holds optional per-role overrides (`tutor`, `teacher`, `auditor`, ...); each
  falls back to `[llm].model`.
- `[study].curriculum` is written by `enroll` and cleared by `unenroll`.
- `[curricula.<id>]` tables are preserved without interpretation. The reviewer reads
  `[curricula."neetcode-150".reviewer].model` as its optional model override and
  otherwise uses `[llm].model`. dojo itself keeps using `[llm].model` for its agents.

### 4.3 The reviewer override in the same file

The reviewer is not configured separately. Add the optional override to the one file,
for example by running `dojo settings` and editing it:

```toml
[curricula."neetcode-150".reviewer]
model = "deepseek-reasoner"   # optional; the engine keeps using [llm].model
```

It matters only when the reviewer runs in model mode (a live provider and
`DOJO_API_KEY`); with the mock provider or no key the reviewer is deterministic and this
table is ignored. Section 6.1/6.2 describes both cases.

### 4.4 The editor

`dojo` never opens the editor at startup: the statement is shown first. The `open`
command opens `solution.py` (the statement is prepended to it as a docstring, and the
visible `check.py` is hidden under `.dojo/`); `dojo settings` opens the settings file. The
command is `[editor].command` from the one settings file, or `DOJO_EDITOR` for one shell:

```bash
export DOJO_EDITOR="code --wait"     # overrides [editor].command in this shell
uv run dojo
```

`$EDITOR` and `$VISUAL` are **not** read. If no editor is configured or the command
cannot launch, dojo prints the reason, the workspace (or settings) path and:

```text
Set [editor].command in settings.toml, or export DOJO_EDITOR for one shell.
```

so you can edit the file from a second terminal.

### 4.5 The key-only run

If the settings file exists but the selected provider is live and `DOJO_API_KEY` is not in
this shell (for example a terminal opened before setup, or an rc that was not sourced),
the wizard asks for the key alone. It never re-asks the provider, base URL, model or
editor, and it does not rewrite the settings file:

```bash
# in a shell without the key; keep the normal DOJO_CONFIG_DIR
env -u DOJO_API_KEY uv run dojo
```

```text
The settings file exists, but its provider needs an API key.
API key (DOJO_API_KEY):
Validating the key...

Setup complete.
  settings: /Users/andywang/.config/dojo/settings.toml (unchanged)
  editor:   code --wait
  provider: deepseek (model deepseek-chat)
  shell:    /Users/andywang/.zshrc (backup: /Users/andywang/.zshrc.dojo-backup)

setup complete; close this terminal and open a new one
```

The settings file's bytes are unchanged; only the shell rc block is refreshed. `mock` and
an unknown provider never trigger this key step. The reviewer has no key step of its own:
without a key it is deterministic (section 6).

### 4.6 The offline (`mock`) setup

The mock provider needs no key, writes no rc block and makes the whole LLM path
deterministic. To see the full wizard without touching the real config or `~/.zshrc`, run
it in a contained `HOME`:

```bash
export P6D_WIZ="$HOME/dojo-p6d-wizard"
mkdir -p "$P6D_WIZ/home"
cd "$ENGINE"
HOME="$P6D_WIZ/home" \
DOJO_CONFIG_DIR="$P6D_WIZ/config" \
DOJO_DATA_DIR="$P6D_WIZ/data" \
DOJO_WORKBENCH_DIR="$P6D_WIZ/workbench" \
uv run dojo
```

```text
Welcome to dojo. This sets up the model gateway and your editor.
Press Enter to accept the value in brackets.
Provider (deepseek/openai/anthropic/mock) [deepseek]: mock
Base URL (optional; Enter for the provider default):
Model [mock]:
Editor command (optional, e.g. code --wait):

Setup complete.
  settings: /Users/andywang/dojo-p6d-wizard/config/settings.toml
  editor:   not set; export DOJO_EDITOR or run `dojo settings`
  provider: mock (model mock)
  shell:    unchanged (the mock provider needs no key)

setup complete; close this terminal and open a new one
```

No `DOJO_API_KEY` is requested and `$P6D_WIZ/home/.zshrc` is not created. The summary's
editor line shows the hint when no editor was given. The isolated walkthrough in section 5
uses this offline shape so every expected output below is reproducible without a network.

### 4.7 `--no-setup`, `DOJO_NO_SETUP`, non-TTY and `--help`

`--no-setup` (before or after a subcommand) and any non-empty `DOJO_NO_SETUP` value other
than `0`/`false`/`no`/`off` skip the wizard. With a complete config (and a key when the
provider is live) the command runs normally. They never invent a config or a key: when the
config or key is missing, the command stops with an actionable message and exit 1.

```bash
# no config: skip the wizard and fail
env -u DOJO_API_KEY DOJO_CONFIG_DIR="$P6D_WIZ/missing" \
  DOJO_DATA_DIR="$P6D_WIZ/data" uv run dojo --no-setup
```

```text
dojo setup is not complete: no settings file at /Users/andywang/dojo-p6d-wizard/missing/settings.toml.
Run `dojo` in an interactive terminal to finish setup.
```

```bash
# a live config without the key: non-TTY (or --no-setup) fails instead of prompting
mkdir -p "$P6D_WIZ/live"
cat > "$P6D_WIZ/live/settings.toml" <<'EOF'
[llm]
provider = "deepseek"
model = "deepseek-chat"
EOF
env -u DOJO_API_KEY DOJO_CONFIG_DIR="$P6D_WIZ/live" \
  DOJO_DATA_DIR="$P6D_WIZ/data" uv run dojo < /dev/null
```

```text
DOJO_API_KEY is not set.
Run `dojo` in an interactive terminal to finish setup, or export
DOJO_API_KEY. Set [llm] provider = "mock" in /Users/andywang/dojo-p6d-wizard/live/settings.toml to run offline.
```

The same message appears for `DOJO_NO_SETUP=1`. A terminal is a TTY; a pipe, a script or
CI is not, and the wizard never tries to prompt there.

`--help` and `--version` never run setup (argparse handles them before the setup check):

```bash
env -u DOJO_API_KEY DOJO_CONFIG_DIR="$P6D_WIZ/missing" uv run dojo --version
# dojo 0.1.0
```

A malformed settings file is not overwritten either: `dojo` reports
`error: invalid TOML in <path>: ...` and exits 1, while `dojo settings` opens the broken
file in your editor for repair. An existing but empty file is treated as no config and
starts the full wizard.

## 5. An isolated test profile and settings

Use a throwaway directory so the test cannot touch your real dojo database or history.
The profile has its own settings file in the same one-config shape; section 4's real
setup stays where it is.

```bash
export P6D="$HOME/dojo-p6d"
mkdir -p "$P6D/data" "$P6D/config" "$P6D/workbench"
export DOJO_DATA_DIR="$P6D/data"
export DOJO_CONFIG_DIR="$P6D/config"
export DOJO_WORKBENCH_DIR="$P6D/workbench"
export UV_CACHE_DIR=/Users/andywang/Projects/dojo-workspace/.uv-cache
```

Create `$P6D/config/settings.toml` with the offline provider and your editor. The mock
provider needs no key and makes the whole LLM path deterministic:

```bash
cat > "$P6D/config/settings.toml" <<'EOF'
# dojo settings. API keys stay in the environment, never in this file.
[editor]
command = "code --wait"          # replace with your editor, or use DOJO_EDITOR

[llm]
provider = "mock"                # offline: no key, no network
model = "mock"

[models]
# tutor = "deepseek-chat"

[study]
warmup_budget = 2

# The same table the reviewer reads. Ignored while provider = "mock"; with a live
# provider and DOJO_API_KEY this is the reviewer's optional model override.
[curricula."neetcode-150".reviewer]
model = "deepseek-reasoner"
EOF
```

If you want the real provider in the profile instead, copy the real file and do not
hand-write a key:

```bash
# same one-config shape, still isolated data
cp "$HOME/.config/dojo/settings.toml" "$P6D/config/settings.toml"
# the new terminal already exported DOJO_API_KEY from the shell rc
```

The defaults, when the `DOJO_*` variables are unset, are:

| setting | default |
|---|---|
| database | `~/.local/share/dojo/dojo.db` (`$XDG_DATA_HOME/dojo/dojo.db`) |
| curricula | `~/.local/share/dojo/curricula/<id>` |
| workbench | `~/.local/share/dojo/workbench` |
| settings | `~/.config/dojo/settings.toml` (`$XDG_CONFIG_HOME/dojo/settings.toml`) |

If you do not want the editor window during the walkthrough, export
`DOJO_EDITOR=true` (it still opens, but exits immediately) or use your normal editor.
`dojo` prints the workspace path either way.

## 6. The NeetCode A2A reviewer

The reviewer is **not** a separate terminal any more. The curriculum declares how to
start it; `dojo` probes the card first, starts the command in the curriculum root when it
is missing, waits for the card, and stops the process it started when `dojo` exits. This
happens for `dojo enroll` and for every `dojo` session. The only entrypoint is `dojo`.

```toml
[agents.reviewer]
url = "http://127.0.0.1:8766/"
command = ["uv", "run", "--project", ".", "python", "-m", "reviewer.server"]

[capabilities.review]
impl = "a2a"
agent = "reviewer"
skill = "review"
```

The agent serves:

| endpoint | value |
|---|---|
| agent card | `GET http://127.0.0.1:8766/.well-known/agent-card.json` |
| A2A JSON-RPC | `POST http://127.0.0.1:8766/` (protocol v1.0, `JSONRPC` binding, `SendMessage`) |
| skill | `review` |

A manually started reviewer is left alone: if the card is already reachable, dojo does not
spawn a second copy and does not stop yours. To debug the agent directly you can still run
`uv run python -m reviewer.server` from `$CURRICULUM`, but the normal flow never requires
it.

The reviewer runs deterministically whenever no key is available (or the provider is
`mock`); it needs no key. It reads the **engine's one** `settings.toml` and **one** key; it
has no reviewer-specific configuration:

- config: `$DOJO_CONFIG_DIR/settings.toml`, or `$XDG_CONFIG_HOME/dojo/settings.toml`
  (`~/.config/dojo/settings.toml`) when `DOJO_CONFIG_DIR` is unset;
- key: `DOJO_API_KEY`, and nothing else.

It never reads `DOJO_REVIEWER_API_KEY`, `DOJO_REVIEWER_BASE_URL`, `DOJO_REVIEWER_MODEL`,
`DOJO_REVIEWER_TIMEOUT_SECONDS`, `OPENAI_API_KEY`, `OPENAI_BASE_URL`,
`DEEPSEEK_API_KEY`, `ANTHROPIC_API_KEY` or any other provider-specific variable. Those are
not fallbacks; they are ignored. The model path is enabled only when `DOJO_API_KEY` is
set, the settings file exists and the provider is not `mock`.

If the command cannot start or exits before serving its card, dojo prints the last lines
of its output. Enrollment then refuses and keeps the installed files; a session continues
without the advisory review and prints `review unavailable` after submit.

### 6.1 Deterministic mode (the offline walkthrough)

With no key, no settings file or `provider = "mock"`, the deterministic rubric writes the
review and no network call is made. The review is still complete: summary, strengths,
improvements, next steps and the advisory `quality` score. Leave the key unset for the
exact transcripts in sections 8-11.

### 6.2 Model mode (the same key and config)

With the real config from section 4 and `DOJO_API_KEY` exported by the shell rc, the
reviewer starts in model mode automatically. The model is `[llm].model`, or the
`[curricula."neetcode-150".reviewer].model` override. The model writes the review prose
from the same review view the deterministic rubric uses (statement, submitted files,
evidence, grade and claims). The rubric keeps the `quality` score, the model's own
`quality` (if it sends one) is ignored, and the grade, card and evidence are never
changed. A transport failure becomes `review unavailable: ...`; the agent stays up and the
engine stores no review. A malformed settings file leaves the reviewer deterministic.

## 7. Enroll the curriculum

Terminal 2 (the engine), with the same `DOJO_*` exports as section 5:

```bash
cd "$ENGINE"
export UV_CACHE_DIR=/Users/andywang/Projects/dojo-workspace/.uv-cache
export DOJO_DATA_DIR="$HOME/dojo-p6d/data"
export DOJO_CONFIG_DIR="$HOME/dojo-p6d/config"
export DOJO_WORKBENCH_DIR="$HOME/dojo-p6d/workbench"

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
(18 topics, 157 items; 5 retired items are addressable but not served). It updates the
`[study] curriculum` key in the profile settings and preserves any `[curricula.<id>]`
table, including the reviewer override. Check the catalog:

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

If the launch command cannot start or exits before serving its card, enrollment refuses
and enrolls nothing, with the last lines of the command's output in the error. The
installer leaves the `$DOJO_DATA_DIR/curricula/neetcode-150` symlink, and the database has
zero `curricula` rows. `dojo` will try again on the next run; you do not start the
reviewer yourself.

## 8. A real practice session: contains_duplicate

`dojo` serves the first unlocked item, which is `contains_duplicate` in Arrays & Hashing.
It has all four item evaluators: `tests`, `oracle`, `complexity` (measured) and `style`
(advisory, assurance `judged`). `dojo` does **not** open your editor at startup, so you can
read the statement first.

```bash
cd "$ENGINE"
# same DOJO_* exports as section 7
uv run dojo
```

Expected start (the panel is rounded and the hint is one dim line):

```text
╭───────────────────── NeetCode 150 · Contains Duplicate ──────────────────────╮
│ Given an integer array nums, return true if any value appears more than once │
│ in the array, otherwise return false.                                        │
│                                                                              │
│ Example 1: Input: nums = [1, 2, 3, 3] Output: true                           │
│ Example 2: Input: nums = [1, 2, 3, 4] Output: false                          │
│                                                                              │
│ You should aim for a solution with O(n) time and O(n) space, where n is the  │
│ size of the input array.                                                     │
╰──────────────────────────────────────────────────────────────────────────────╯
open · check · submit · learn · quit · statement · help
dojo> 
```

Type `open` to open `solution.py`. The statement is prepended to the file as a docstring,
so you do not need to switch back to the terminal to read it. The visible `check.py` is not
in the workspace root; it lives under `.dojo/` and is never opened by `open`. Replace the
stub with a correct solution and save. For this runbook a set is enough:

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
╭─────────────────────────────────── check ────────────────────────────────────╮
│ check exited 0                                                               │
│ 4 of 4 visible checks passed                                                 │
╰──────────────────────────────────────────────────────────────────────────────╯
```

Before you submit, you can run section 9's mock tutor/`learn` flow in this same session
(it works on the current workspace and abandons the session at `practice`); otherwise
skip it and submit now. After a passing submit the card is scheduled in 2 days, so this
item is not served again until it is due.

```text
dojo> submit
```

Expected evidence and grade (timings and the last decimals vary):

```text
dojo> submit
╭────────────────────────────────── evidence ──────────────────────────────────╮
│ evaluator   assurance   outcome   summary                                    │
│ tests       machine     pass      26/26 private cases passed                 │
│ oracle      machine     pass      26/26 private cases passed                 │
│ complexity  measured    pass      time like the reference (1.10x); space ... │
│ style       judged      pass      no advisory style flags                    │
│                                                                              │
│ Grade: 3 (pass)                                                              │
│ Next review: <date> (in 2 days)                                              │
╰──────────────────────────────────────────────────────────────────────────────╯
╭──────────────────── review · advisory, the grade stands ─────────────────────╮
│ Summary. Review of contains_duplicate in neetcode-150: grade 3 (pass); 4 of  │
│ 4 evaluator reports passed. The code reads as Arrays & Hashing and uses a    │
│ set for O(1) membership ...                                                  │
│                                                                              │
│ Strengths                                                                    │
│  • ...                                                                       │
│                                                                              │
│ Quality. 0.76 / 1                                                            │
╰──────────────────────────────────────────────────────────────────────────────╯
```

The review block is the deterministic P6-C rubric from section 6.1. In model mode
(section 6.2) the summary/strengths prose is model-written and varies; the `quality`
value still comes from the rubric, and the grade, card and evidence are untouched.

What to verify in the database (SQLite is fine; the engine uses one file):

```bash
python3 - "$DOJO_DATA_DIR/dojo.db" <<'PY'
import sqlite3, sys

db = sqlite3.connect(sys.argv[1])
db.row_factory = sqlite3.Row
for sql in (
    "select item_id, grade, outcome from attempts",
    "select evaluator_id, assurance, outcome from evidence order by evaluator_id",
    "select item_id, reps, stability, difficulty from cards",
    "select agent from reviews",
    "select purpose, provider, model, prompt_sha256 from ai_calls order by call_id",
):
    print(sql)
    for row in db.execute(sql):
        print(" ", dict(row))
PY
```

Expected:

- one `attempts` row, `contains_duplicate`, grade 3, outcome `pass`;
- four `evidence` rows (in evaluator-id order): `complexity`/`measured`/`pass`,
  `oracle`/`machine`/`pass`, `style`/`judged`/`pass`, `tests`/`machine`/`pass`;
- one `cards` row, reps 1, next review in 2 days (FSRS);
- one `reviews` row with `agent = reviewer/review` (the P6-C agent), not `reviewer`;
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

## 9. Tutor, teacher, hints and `learn` / `practice`

Do this in a session **before** its submit (section 8), or in a fresh profile: after a
passing submit the item is scheduled and is not served again until it is due. The
transcript below is from the run before the submit, with the mock provider (the profile in
section 5). Inside the same session, type a question:

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
9 ladder problems in this pattern, 10 of them curated so far.
0/152 exercises done. Recent grades, newest first: none yet.
practice · done · quit · help
learn> what is an invariant?
teacher · Arrays & Hashing
Mock teacher: state the invariant in one sentence, then test it on a small input.
learn> done
Left learn. The practice session was already abandoned.
```

`practice` instead of `done` starts a fresh session on the next unsolved item — on this
first run that is `contains_duplicate` again. Type `open` to open the new `solution.py`
(its statement docstring is already there); write the solution before `check`/`submit`.
`done` or `quit` leaves the teacher loop. The abandoned session keeps its hint level and
is not an attempt.

With a live provider in the profile config (section 5) the same commands call the real
model, so the answers are real prose rather than the `Mock tutor:`/`Mock teacher:` text.
The boundary is unchanged: the tutor sees the statement, the **current solution.py** (as
its own labelled block), the other workspace files, the last check output, prior turns
and the question; the teacher sees the curriculum, topic and a compact learner summary,
never the item statement.

**No key is now a setup gate, not a mid-session mode.** A live provider with no
`DOJO_API_KEY` never reaches a session: `dojo` stops at the setup check (section 4.5/4.7).
Use the mock provider (this profile) to run the LLM path offline, or export the key. If a
provider call fails while a session is already running (an unreachable `base_url`, an
outage), the tutor/teacher report unavailable and `check`/`submit` continue; the A2A review
still works; dojo restarts the reviewer before the review. Section 11 covers the no-key gate and the deterministic
reviewer.

### Blocked leak-auditor check (optional, loopback stub)

With the mock provider the auditor always returns `allow`, so a block is not visible. To
see the withhold path live, run a tiny OpenAI-compatible stub that answers tutor requests
with a leak and always blocks the audit. Terminal 3:

```bash
cat > /tmp/p6d-block-stub.py <<'PY'
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
python3 /tmp/p6d-block-stub.py
```

In a separate profile (rerun section 5 with `$P6D` plus `-block`), replace the `[llm]`
table in `$P6D/config/settings.toml` with:

```toml
[llm]
provider = "openai"
model = "p6d-stub"
base_url = "http://127.0.0.1:8799/v1"
```

and export `DOJO_API_KEY=stub-key` (any non-empty value; the stub does not check it; the
setup check only requires that the key exists). Enroll, start a session and ask a
question:

```text
dojo> how do I solve this?
tutor · withheld
The answer was not shown: the answer gives away the solution
The hint level is unchanged. Ask again, or type `help`.
```

The student turn and the tutor/auditor provenance are recorded; no tutor turn is stored
and the level does not move. Stop the stub with Ctrl-C. The reviewer reads the same
config, so this stub may also make its optional model path fail; the review is still
advisory and the grade, evidence and card are unaffected.

## 10. Progress, history, curricula, settings and unenroll

```bash
cd "$ENGINE"
# with the same DOJO_* exports as section 7
uv run dojo progress neetcode-150
```

The roadmap is a compact tree inside a rounded panel. The **current** pattern is expanded
with every item and its status (`done`, `next`, `open`, `locked`, `retired`); every other
pattern is one collapsed line (`locked`, `open` or `complete`), not a table:

```text
╭───────────────────────── neetcode-150 · 1/152 done ──────────────────────────╮
│ Arrays & Hashing  ·  1/10                                                    │
│   ✓ Contains Duplicate  done                                                 │
│   → Valid Anagram  next                                                      │
│   ○ Two Sum  open                                                            │
│   ...                                                                        │
│   - Array Intersection  retired                                              │
│ Two Pointers  ·  5 items  ·  locked                                          │
│ ...                                                                          │
╰──────────────────────────────────────────────────────────────────────────────╯
```

This is the full-corpus smoke: the catalog has all 157 items and all their
statements/workspaces resolved; 152 are served, 5 are retired.

```bash
uv run dojo history
```

```text
History
┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━┓
┃ date             ┃ curriculum   ┃ item               ┃ grade ┃ outcome ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━┩
│ 2026-10-28 01:59 │ neetcode-150 │ Contains Duplicate │ 3     │ pass    │
└──────────────────┴──────────────┴────────────────────┴───────┴─────────┘
```

```bash
uv run dojo settings
```

`settings` opens `$DOJO_CONFIG_DIR/settings.toml` in the configured editor. To print it
instead without editing the profile, override the editor for this one command:

```bash
DOJO_EDITOR=cat uv run dojo settings
# prints the settings file, then:
# Settings file: /Users/andywang/dojo-p6d/config/settings.toml
```

The file never contains a key. If no editor is configured, the command prints the reason
and the path instead of failing.

```bash
uv run dojo unenroll neetcode-150
```

```text
Unenrolled neetcode-150. Installed files and history are kept.
No active curriculum. Run `dojo enroll <path-or-url>` to add one.
```

`unenroll` pauses the enrollment, clears `[study].curriculum` in the settings file (the
`[curricula.<id>]` table stays) and leaves the attempts and the installed symlink. Re-enroll
with the same command to resume; `dojo history` still shows the attempts.

## 11. The failure paths

Run these in order; each one is a boundary check.

### 11.1 Missing config

Use a fresh empty profile and a non-TTY (or `--no-setup`) so the wizard cannot prompt:

```bash
export P6D="$HOME/dojo-p6d-missing"
export DOJO_DATA_DIR="$P6D/data" DOJO_CONFIG_DIR="$P6D/config" DOJO_WORKBENCH_DIR="$P6D/workbench"
mkdir -p "$DOJO_DATA_DIR" "$DOJO_CONFIG_DIR" "$DOJO_WORKBENCH_DIR"
cd "$ENGINE"
env -u DOJO_API_KEY uv run dojo --no-setup
```

Expected: exit code 1 and

```text
dojo setup is not complete: no settings file at /Users/andywang/dojo-p6d-missing/config/settings.toml.
Run `dojo` in an interactive terminal to finish setup.
```

The same message appears for a non-TTY stdin (`uv run dojo < /dev/null`) and for
`DOJO_NO_SETUP=1`. Nothing is created.

### 11.2 Missing key

A live config without `DOJO_API_KEY` in the shell (the classic "I forgot to open a new
terminal after setup") stops at the same gate; it does not start a session and does not
silently use a model:

```bash
# a live config without the key; the key stays out of the environment
mkdir -p "$HOME/dojo-p6d-live/config"
cat > "$HOME/dojo-p6d-live/config/settings.toml" <<'EOF'
[llm]
provider = "deepseek"
model = "deepseek-chat"
EOF
env -u DOJO_API_KEY DOJO_CONFIG_DIR="$HOME/dojo-p6d-live/config" \
  DOJO_DATA_DIR="$HOME/dojo-p6d/data" uv run dojo < /dev/null
```

```text
DOJO_API_KEY is not set.
Run `dojo` in an interactive terminal to finish setup, or export
DOJO_API_KEY. Set [llm] provider = "mock" in /Users/andywang/dojo-p6d-live/config/settings.toml to run offline.
```

In a real terminal the same condition runs the key-only setup (section 4.5) instead of
failing. `mock` never needs a key. The reviewer is different: with no key it is
deterministic, not unavailable (section 11.6).

### 11.3 Mock: no key, no network

Section 5's profile is the mock boundary:

- the setup wizard asks no key and writes no rc block (`shell: unchanged`);
- the engine's tutor/teacher answer offline (`Mock tutor:`/`Mock teacher:`);
- dojo starts the reviewer itself; with no key it is deterministic;
- `check`, `submit` and the A2A review all work; no request leaves the machine.

This is the recommended first run and the exact transcript source for sections 8-9.

### 11.4 Reviewer launch failure (optional)

The old "start the reviewer by hand, then enroll" path no longer exists. To exercise the
failure, use a scratch copy of the curriculum whose agent command cannot start:

```bash
export P6D="$HOME/dojo-p6d-down"
export DOJO_DATA_DIR="$P6D/data" DOJO_CONFIG_DIR="$P6D/config" DOJO_WORKBENCH_DIR="$P6D/workbench"
mkdir -p "$DOJO_DATA_DIR" "$DOJO_CONFIG_DIR" "$DOJO_WORKBENCH_DIR"
cp "$HOME/dojo-p6d/config/settings.toml" "$DOJO_CONFIG_DIR/settings.toml"
cp -R "$CURRICULUM" "$HOME/neetcode-broken"
python3 - "$HOME/neetcode-broken/curriculum.toml" <<'PY'
import sys
from pathlib import Path

path = Path(sys.argv[1])
text = path.read_text()
text = text.replace(
    'command = ["uv", "run", "--project", ".", "python", "-m", "reviewer.server"]',
    'command = ["false"]',
)
path.write_text(text)
PY
cd "$ENGINE"
uv run dojo enroll "$HOME/neetcode-broken"
```

Expected: exit code 1, the error names the agent and includes the command's last output,
ending `not enrolled, the installed files are kept`. The installer leaves the symlink and
the database has zero `curricula` rows. Delete the scratch copy; `dojo` retries on the next
run.

### 11.5 Reviewer restart while a session is open

Start a session, then in another terminal kill the agent process
(`pkill -f 'reviewer.server'`). On `submit`, dojo notices the card is unreachable, starts
the declared command again, and the review is produced. There is no separate server to
restart and no reviewer-specific state to preserve.

### 11.6 No key for the reviewer

With the profile's mock config (or with `provider = "mock"`, or with no settings file) the
reviewer stays deterministic and complete; there is no "reviewer key" to set. The engine
starts it on demand and stores the review; no `DOJO_REVIEWER_*` or `OPENAI_*` variable is
read. To see model prose, set the one `DOJO_API_KEY` and a live provider in the same
settings file (section 6.2).

### 11.7 Blocked leak audit

Section 9's optional stub. The answer is withheld, the hint level is unchanged, and the
student turn/provenance are kept.

## 12. Test suites and static checks

From the curriculum checkout:

```bash
cd "$CURRICULUM"
export UV_CACHE_DIR=/Users/andywang/Projects/dojo-workspace/.uv-cache
uv sync
uv run pytest                 # 373: 223 curriculum + 150 reviewer
uv run pytest tests           # 223
uv run pytest reviewer/tests  # 150
uv run ruff check .
uv run ruff format --check .
uv run ty check .
```

`ty` excludes only `content/` and `src/neetcode_dojo/assessment/`; everything else is
checked. The repository has no second lockfile or virtualenv for the reviewer.

From the engine checkout (read-only for P6-D):

```bash
cd "$ENGINE"
uv run pytest                 # 580
uv run ruff check .           # clean
uv run ty check .             # clean
uv run ruff format --check .  # see the known-issue note below
```

Known issue: the engine's `uv run ruff format --check .` reports one pre-existing
Markdown file, `docs/phase-2.md` (a Python code block in the read-only docs). It is not
caused by this curriculum and the engine is not edited here;
`uv run ruff format --check src tests` is clean.

The optional reference agent:

```bash
cd "$ENGINE/curriculum-kit/a2a-reviewer"
uv run pytest                 # 17
```

The curriculum and reviewer suites are offline: no network, no API key and no bound
port. The reviewer tests use `httpx.ASGITransport` against the real ASGI app; the config
tests write a throwaway `settings.toml` under `tmp_path`; the evaluator tests use
subprocesses and fixture assessment trees. The engine suite is also offline except for
its one A2A integration test, which starts the reference agent on loopback port 8765.

## 13. Sampling the evaluator shapes and the full corpus

The end-to-end run covers `contains_duplicate` (tests + oracle + measured complexity +
advisory style) and the A2A review. The catalog is complete and the counts are:

| count | value |
|---|---|
| topics | 18 |
| corpus items | 157 |
| active (served) | 152 |
| retired (addressable, not served) | 5 |
| evaluators | 6 (4 attached to items) |

The 5 retired duplicates are `array_intersection`, `peak_elements`,
`mirror_image_binary_tree`, `k_smallest_elem_matrix`, `max_prod_3_nums`. `dojo curricula`
shows `items: 152`; `dojo progress neetcode-150` lists all 157 with the retired ones
marked. A full 157-item submission run is not repeated here: the item corpus and the
assessment registration are covered by the offline suite and the enrollment loader.

Two more evaluator shapes are worth checking:

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

## 14. Data locations, cleanup and privacy

The real setup and the isolated profile are separate:

| path | contents |
|---|---|
| `~/.config/dojo/settings.toml` | the one real config: `[editor]`, `[llm]`, `[models]`, `[study]`, `[curricula]`; never a key |
| `~/.zshrc` (or `~/.bashrc` / `~/.config/fish/config.fish`) | the marked `DOJO_API_KEY` block; backup `*.dojo-backup` |
| `~/.local/share/dojo/dojo.db` | SQLite: catalog, sessions, attempts, evidence, cards, reviews, AI provenance |
| `~/.local/share/dojo/curricula/neetcode-150` | symlink to the curriculum (a local install) |
| `~/.local/share/dojo/workbench/neetcode-150/<item>/<session>/` | the student's workspace snapshots |
| `$P6D/data/dojo.db` | the same schema for the isolated test profile |
| `$P6D/data/curricula/neetcode-150` | the test profile's symlink |
| `$P6D/workbench/neetcode-150/<item>/<session>/` | the test profile's workspace snapshots |
| `$P6D/config/settings.toml` | the test profile's copy; never a key |

Cleanup after testing (the real config and rc block stay; they are the actual setup):

```bash
# stop any optional stub (section 9); dojo stops the reviewer when it exits
rm -rf "$HOME/dojo-p6d" "$HOME/dojo-p6d-down" "$HOME/dojo-p6d-missing" \
       "$HOME/dojo-p6d-live" "$HOME/dojo-p6d-block" "$HOME/dojo-p6d-wizard"
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
  history. The `review.v1` request rejects extra fields, and
  `reviewer/tests/test_boundary.py` checks the reviewer's production modules for file
  reads and imports into the private tree. `reviewer/config.py` is the only production
  module that opens a file, and it reads exactly the one settings path.
- The key boundary: `DOJO_API_KEY` is read from the environment by the engine and by the
  reviewer. It is not in `settings.toml`, the database, the workbench, the review view or
  the MCP child's environment. The setup summary never prints it, and a validation error
  redacts it. Do not commit the shell rc or paste the key into a log or an issue.
- Outbound requests: with a live provider, the engine sends its tutor/teacher/auditor
  prompts and the reviewer sends its review prompt to that provider; key validation sends
  one tiny request. With `provider = "mock"` or no key, no request leaves the machine
  except loopback to the reviewer and the MCP server. The only loopback listeners are the
  reviewer on 8766 (and the optional reference agent on 8765).

## 15. What "good" looks like

- `uv sync` succeeds in the engine, the curriculum and the optional reference agent.
- The first-run wizard completes, `[llm]` and `[editor]` are in the one `settings.toml`,
  no key is in the file, and a new shell has `DOJO_API_KEY` from the rc block.
- The key-only step asks only for the key and leaves the settings bytes unchanged;
  `--no-setup`, `DOJO_NO_SETUP` and a non-TTY fail actionably instead of prompting;
  `--help` and `--version` never run setup.
- The reviewer serves `NeetCode 150 reviewer` with the `review` skill on 8766; its
  review is deterministic with no key and model-written with the one
  key and a live config; it reads no reviewer-specific environment.
- `dojo enroll` prints `Enrolled NeetCode 150 (neetcode-150)`, `items: 157`, `active: yes`.
- `dojo curricula` shows 152 active items; `dojo progress` lists 18 patterns and every
  item, with the 5 retired ones marked `retired`.
- `check` is 0 and `submit` reports `tests`/`oracle`/`complexity`/`style` with the
  manifest's assurance (`machine`, `machine`, `measured`, `judged`), grade 3 and a card.
- The review is advisory, comes from `reviewer/review`, and is stored with
  `provider = a2a`; the attempt/card are untouched.
- Killing the reviewer mid-session is repaired on submit: dojo starts the declared
  command again and the review is produced.
- With a live provider and no key, the CLI stops actionably; with `mock` the whole flow is
  offline; with no key the reviewer is deterministic.
- The curriculum suite is 373 (223 + 150), `ruff` and `ty` are clean; the engine is 580
  and clean apart from the pre-existing `docs/phase-2.md` formatting note; the reference
  agent is 17.
- No private material appears in any prompt, workspace, review request or committed file.

## 16. Phase 6

The cutover is separate: back up the old `dojo` and old curriculum, rename the rebuild,
force-push the new engine over the old `dojo`, rename the new curriculum repository, start
the fresh single-user database and discard the old history. Do not run it as part of this
runbook. The P6 setup/credential and integration result above is the gate for that
decision.
