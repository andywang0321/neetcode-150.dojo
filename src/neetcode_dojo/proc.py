"""Bounded subprocess execution — the one place the evaluator runs code it did not write.

Every safeguard here exists because of an observed failure:

- an infinite ``print`` loop filled RAM, because the output cap was applied *after*
  the whole output existed;
- a solution that printed in a hot loop filled the parent's memory, because a
  captured stream was read whole;
- a timed-out run left a spawned grandchild alive, because ``subprocess.run`` kills
  only the direct child;
- a solution that wrote to file descriptor 1 bypassed the ``sys.stdout`` swap and
  corrupted the JSON protocol channel.

So: output is collected into temp *files* and only a bounded slice is read back;
the child runs in its own session and its whole process **group** is killed on
timeout; and results come back as data rather than exceptions. The child-side limits
(address space, file size, CPU) are set inside the harnesses, the only place they can
be applied to the child's own process.
"""

from __future__ import annotations

import contextlib
import os
import signal
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

#: Protocol output (a judge's result JSON) — generous, because cases with
#: expected/got values can be large, and the whole point is that it is bounded.
OUT_CAP = 1 * 1024 * 1024
#: Diagnostics (tracebacks, a dying harness's last words, compiler output).
ERR_CAP = 16 * 1024
#: Hard limits installed inside the child by the harnesses.
MEM_LIMIT_BYTES = 4 * 1024**3
FSIZE_LIMIT_BYTES = 256 * 1024 * 1024
CPU_LIMIT_SECONDS = 60


@dataclass(frozen=True, slots=True)
class ProcResult:
    """What a bounded child run produced. Never raises for a child that failed."""

    returncode: int | None
    stdout: str
    stderr: str
    timed_out: bool


def kill_group(proc: subprocess.Popen[bytes]) -> None:
    """Kill the child *and everything it spawned*.

    ``start_new_session=True`` makes the child a process-group leader, so one
    ``killpg`` reaches its grandchildren too — a solution that forks a background
    worker must not outlive the run that timed out."""
    try:
        os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
    except ProcessLookupError, PermissionError, OSError:
        with contextlib.suppress(OSError):
            proc.kill()
    with contextlib.suppress(subprocess.TimeoutExpired):
        proc.wait(timeout=5)


def run_capped(
    cmd: list[str],
    cwd: Path | str | None,
    timeout: float,
    *,
    out_cap: int = OUT_CAP,
    err_cap: int = ERR_CAP,
    env: dict[str, str] | None = None,
) -> ProcResult:
    """Run ``cmd`` with bounded output and no survivors on timeout.

    Output goes to temp files (disk, not memory) and only the first ``out_cap`` /
    last ``err_cap`` bytes are returned. A timeout is reported, not raised."""
    with tempfile.TemporaryFile() as out_file, tempfile.TemporaryFile() as err_file:
        try:
            proc = subprocess.Popen(
                cmd,
                cwd=cwd,
                stdout=out_file,
                stderr=err_file,
                stdin=subprocess.DEVNULL,
                start_new_session=True,
                env=env,
            )
        except OSError as exc:
            return ProcResult(None, "", f"could not start the process: {exc}", False)
        try:
            proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            kill_group(proc)
            return ProcResult(None, "", f"timed out after {timeout:g}s", True)
        returncode = proc.returncode
        out_file.seek(0)
        err_file.seek(0)
        stdout = out_file.read(out_cap).decode("utf-8", "replace")
        raw_err = err_file.read()
        stderr = raw_err[-err_cap:].decode("utf-8", "replace")
        return ProcResult(returncode, stdout, stderr, False)


def last_json_object(stdout: str) -> dict[str, Any] | list[Any] | None:
    """The last JSON object or list in ``stdout``, or None.

    Reading the last parseable line (rather than the whole stream) is what makes
    the protocol robust against a stray ``print`` from a background thread or an
    ``atexit`` handler landing after the result line: the child writes its JSON with
    a single ``os.write``, and anything after it is simply ignored."""
    import json

    for line in reversed(stdout.splitlines()):
        line = line.strip()
        if not line or line[0] not in "[{":
            continue
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict | list):
            return parsed
    return None


def apply_child_limits() -> None:
    """Install hard resource limits on *this* process (call from a harness).

    Soft limits are raised to the hard ones so user code cannot relax them again.
    Silent on platforms without ``resource`` (or with a lower hard limit already in
    place) — a limit that cannot be set must never break a run."""
    try:
        import resource
    except ImportError:  # pragma: no cover - non-POSIX
        return
    for name, value in (
        ("RLIMIT_AS", MEM_LIMIT_BYTES),
        ("RLIMIT_FSIZE", FSIZE_LIMIT_BYTES),
        ("RLIMIT_CPU", CPU_LIMIT_SECONDS),
    ):
        limit = getattr(resource, name, None)
        if limit is None:
            continue
        try:
            resource.setrlimit(limit, (value, value))
        except ValueError, OSError:
            continue
