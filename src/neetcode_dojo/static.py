"""Static analysis at submit: radon cyclomatic complexity + ruff.

Evidence for the reviewer and the learner, not a verdict: complexity above the
McCabe convention (10) and lint findings are flags, never failures.
"""

from __future__ import annotations

import contextlib
import json
import os
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

COMPLEXITY_THRESHOLD = 10  # the McCabe convention

#: Where ruff writes its cache. The cache belongs to the evaluator, not to whatever
#: directory the server happened to start in: without this, a run created
#: ``.ruff_cache/`` in the curriculum root or the student's workspace.
CACHE_DIR_ENV = "NEETCODE_DOJO_CACHE_DIR"


@dataclass
class StaticReport:
    """What one file's static analysis found. Advisory data, never a verdict."""

    complexity: list[dict[str, Any]] = field(default_factory=list)  # {name, complexity, rank}
    ruff: list[dict[str, Any]] = field(default_factory=list)  # {code, message, line}
    notes: list[str] = field(default_factory=list)  # tooling hiccups, if any

    @property
    def flags(self) -> list[str]:
        out: list[str] = []
        for entry in self.complexity:
            if entry["complexity"] > COMPLEXITY_THRESHOLD:
                out.append(
                    f"{entry['name']}: complexity {entry['complexity']} "
                    f"(rank {entry['rank']}) — consider refactoring"
                )
        for finding in self.ruff[:5]:
            out.append(f"ruff {finding['code']} line {finding['line']}: {finding['message']}")
        return out

    def to_dict(self) -> dict[str, Any]:
        return {
            "complexity": self.complexity,
            "ruff": self.ruff,
            "notes": self.notes,
        }


def default_cache_dir() -> Path:
    """The ruff cache directory: the environment's choice, else the system temp."""
    configured = os.environ.get(CACHE_DIR_ENV)
    if configured:
        return Path(configured).expanduser() / "ruff"
    return Path(tempfile.gettempdir()) / "neetcode_dojo" / "ruff"


def analyze(
    code_path: Path,
    source: str | None = None,
    *,
    cache_dir: Path | str | None = None,
    ruff_timeout: float = 60.0,
) -> StaticReport:
    """Cyclomatic complexity per function (radon) + lint findings (ruff).

    Never raises — including when the file cannot be read at all: a missing file
    (``FileNotFoundError``) or a non-UTF-8 one (``UnicodeDecodeError``) is a note,
    not a lost submission."""
    report = StaticReport()
    lint_source = source
    if lint_source is None:
        try:
            lint_source = code_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            report.notes.append(f"static analysis skipped: {type(exc).__name__}: {exc}")
            return report

    try:
        from radon.complexity import cc_visit
        from radon.visitors import Function

        for block in cc_visit(lint_source):
            if isinstance(block, Function):
                report.complexity.append(
                    {
                        "name": block.name,
                        "complexity": block.complexity,
                        # radon >= 5 spells the A-F grade `.letter`; older `.rank`.
                        "rank": getattr(block, "letter", None) or getattr(block, "rank", ""),
                    }
                )
    except Exception as exc:  # evidence gathering must survive
        report.notes.append(f"radon skipped: {exc}")

    target_cache = Path(cache_dir) if cache_dir is not None else default_cache_dir()
    tmp_dir: tempfile.TemporaryDirectory[str] | None = None
    try:
        tmp_dir = tempfile.TemporaryDirectory(prefix="neetcode_dojo_static_")
        lint_target = Path(tmp_dir.name) / code_path.name
        lint_target.write_text(lint_source, encoding="utf-8")
        with contextlib.suppress(OSError):
            target_cache.mkdir(parents=True, exist_ok=True)
        # The shebang rules are silenced: the venv shebang is curriculum chrome,
        # not user code. `--isolated` keeps ambient project configuration out of the
        # evidence, so the same file lints the same way wherever the server runs.
        completed = subprocess.run(
            [
                sys.executable,
                "-m",
                "ruff",
                "check",
                "--isolated",
                "--output-format=json",
                "--cache-dir",
                str(target_cache),
                "--ignore",
                "EXE001,EXE002,EXE004",
                str(lint_target),
            ],
            capture_output=True,
            text=True,
            timeout=ruff_timeout,
            check=False,
        )
        if completed.stdout.strip():
            for finding in json.loads(completed.stdout):
                location = finding.get("location") or {}
                report.ruff.append(
                    {
                        "code": finding.get("code", "?"),
                        "message": finding.get("message", ""),
                        "line": location.get("row", 0),
                    }
                )
        elif completed.returncode != 0 and completed.stderr.strip():
            report.notes.append(f"ruff: {completed.stderr.strip()[:200]}")
    except Exception as exc:  # a lint tool must not fail a submit
        report.notes.append(f"ruff skipped: {exc}")
    finally:
        if tmp_dir is not None:
            tmp_dir.cleanup()

    return report
