# Manual testing

A concise end-to-end checklist for maintainers. Use isolated paths so a test cannot touch
your real history.

## Setup

```bash
export TEST_ROOT="$HOME/dojo-neetcode-manual/$(date +%Y%m%d-%H%M%S)"
export DOJO_DATA_DIR="$TEST_ROOT/data"
export DOJO_CONFIG_DIR="$TEST_ROOT/config"
export DOJO_CURRICULA_DIR="$TEST_ROOT/data/curricula"
export DOJO_DB_PATH="$TEST_ROOT/data/dojo.db"
export DOJO_WORKBENCH_DIR="$TEST_ROOT/data/workbench"
mkdir -p "$DOJO_DATA_DIR" "$DOJO_WORKBENCH_DIR" "$DOJO_CONFIG_DIR"

# A mock profile is deterministic and needs no key.
cat > "$DOJO_CONFIG_DIR/settings.toml" <<'TOML'
[llm]
provider = "mock"
model = "mock"

[editor]
command = "true"
TOML
```

Enroll the curriculum from its checkout:

```bash
cd /path/to/neetcode-150.dojo
dojo enroll .
dojo curricula          # neetcode-150, 152 active
dojo progress           # 18 patterns, 0/152
```

## The session

Use a temporary editor command that writes a known-correct solution, or edit
`solution.py` by hand. A minimal pass:

```text
dojo
open
check
submit
O(n) one pass
O(n) the set
why is the set needed?
polish
open
check
submit
O(n) one pass
O(n) the set
done
```

Verify:

- the statement, `solution.py` header and hidden `.dojo/check.py` are present;
- the visible check runs, and is not the grade;
- submission asks both complexity questions;
- evidence shows tests/oracle/complexity/style as applicable;
- grade 3 and a next review date appear;
- the A2A review is rendered and stored (or `review unavailable` when the reviewer is
  stopped);
- discussion answers in Markdown, with no hint ladder;
- polish allows a second submission (revision 2);
- `done` prints `Session complete.`;
- `dojo history` shows two numbered attempts and the footer;
- `dojo show 1` shows the newest attempt with solution, evidence, review, conversation
  and snapshot timeline; `dojo show 2` the earlier one;
- the active session is gone.

## Reviewer failure

Stop the reviewer (or enroll with port 8766 occupied by a non-reviewer). At enrollment,
the card/skill probe must fail and keep the installed files. After enrollment, stop the
reviewer and submit: the attempt, grade and card must survive and `review unavailable`
must be printed. Restart with `dojo`; it starts the declared command again.

## Offline and missing key

With `provider = "mock"`, `check`, `submit`, the review and the discussion work without
`DOJO_API_KEY`. With a live provider and no key, the first `dojo` stops at the setup gate
with an actionable message; the session does not start partially configured.

## Privacy

- No hidden case, oracle, reference solution or assessment path appears in a workspace,
  prompt or review request.
- The reviewer receives only the review view.
- The curriculum's MCP server does not receive `DOJO_API_KEY`.
- `content/` and the prompts contain no private material.
- `license = "private"` remains in the manifest.

## Cleanup

```bash
rm -rf "$TEST_ROOT"
unset DOJO_DATA_DIR DOJO_CONFIG_DIR DOJO_CURRICULA_DIR DOJO_DB_PATH DOJO_WORKBENCH_DIR
```

Do not run this checklist against your real data directory.
