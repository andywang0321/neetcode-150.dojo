# Getting started

This curriculum is private. You need access to
`github.com/andywang0321/neetcode-150.dojo` and a working dojo installation.

## 1. Install dojo

Follow the engine's [install guide](https://github.com/andywang0321/dojo/blob/main/docs/install.md).
In short, with uv:

```bash
git clone https://github.com/andywang0321/dojo.git
cd dojo
uv tool install .
dojo --version
```

The first `dojo` starts the setup wizard. It asks for one provider (DeepSeek, OpenAI,
Anthropic or the offline mock), an optional model and editor, and the single
`DOJO_API_KEY`. The key is written to your shell rc, not the settings file. The wizard
exits; open a new terminal.

## 2. Clone and enroll

```bash
git clone git@github.com:andywang0321/neetcode-150.dojo.git
cd neetcode-150.dojo
dojo enroll .
```

Enrollment:

- installs the curriculum under dojo's data directory;
- validates `curriculum.toml` and the content paths;
- starts the MCP evaluator server and verifies all six declared tools;
- starts the A2A reviewer from its manifest command, fetches its card and verifies the
  `review` skill;
- makes the curriculum active.

You do **not** run a separate reviewer server in normal use. dojo starts it and stops the
process it started when dojo exits.

Check it:

```bash
dojo curricula
dojo progress
```

`progress` shows the 18-pattern roadmap; the five retired duplicates are kept for history
but are not in the roadmap or queue.

## 3. Practise

```bash
dojo
```

The first item is shown. In the workspace, `solution.py` starts with the statement as a
docstring and a stub. `check.py` is the visible check and is hidden under `.dojo/`; it is
excluded from the submission.

```text
dojo> open          # edit solution.py
dojo> check         # run the visible check; not the grade
dojo> submit        # answer the complexity questions, then assess
```

After `submit`, dojo shows evidence and a grade, stores the attempt and enters discussion
with the reviewer. Ask about the code or the complexity, or type `polish` to revise and
submit again. `done` ends the session.

```bash
dojo history        # numbered attempts, newest first (default 5)
dojo show 1         # solution, evidence, review, conversation, snapshots
```

## Requirements and credentials

The engine and reviewer share one config, one provider and one `DOJO_API_KEY`. With
`provider = "mock"` everything runs offline; the reviewer is deterministic. A live
provider without a key stops at the setup gate.

The curriculum's MCP server never receives the key. The A2A reviewer reads the same
settings file read-only and uses the optional
`[curricula."neetcode-150".reviewer].model` override.

## If the reviewer fails

- At enrollment, a reviewer that cannot start or serve its card fails enrollment and keeps
  the installed files. Check `uv sync` in the curriculum and that port 8766 is free.
- At submit, a stopped reviewer leaves the attempt, grade and card intact and prints
  `review unavailable`.
- For debugging, run the reviewer directly:

  ```bash
  uv run python -m reviewer.server
  ```

  Stop it with Ctrl-C. dojo leaves a manually started server alone.

The full evaluator, review and privacy model is in [How it works](how-it-works.md).
