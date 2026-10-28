"""Submitted files: safe materialization and entry-point discovery.

The engine sends a snapshot of the student's workspace. The server writes it into a
throwaway directory, then decides two things before it can run anything:

- **which file holds the item's entry point** — the curriculum's own template under
  ``content/<item>/workspace/`` names the function or class the student must keep;
- **what that entry point is called** — the first top-level ``def`` or ``class`` in
  the template (the port-plan workspace shape), or an explicit ``entry_point`` on
  the request when a curriculum wants to override it.

Neither answer is taken from the student's code alone: a submission that renames the
entry point is an error the reviewer can see, not a silently different item.
"""

from __future__ import annotations

import ast
import tempfile
from collections.abc import Generator, Sequence
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from neetcode_dojo.protocol import SubmissionFile


class SubmissionError(Exception):
    """A submission that cannot be materialized or resolved to an entry point."""


@dataclass(frozen=True, slots=True)
class EntryPoint:
    function: str
    code_file: str


def python_files(files: Sequence[SubmissionFile]) -> list[str]:
    """The Python files in a snapshot, in the order the engine sent them."""
    return [file.path for file in files if file.path.endswith(".py")]


def analyze_files(files: Sequence[SubmissionFile]) -> list[str]:
    """The files static analysis should see: Python, minus the visible check.

    ``check.py`` is curriculum-provided chrome, not the student's work; linting it
    reports findings the reviewer would repeat as if they were the student's."""
    return [path for path in python_files(files) if PurePosixPath(path).name != "check.py"]


@contextmanager
def materialized(files: Sequence[SubmissionFile]) -> Generator[Path]:
    """Write ``files`` under a fresh temporary directory and yield its root."""
    with tempfile.TemporaryDirectory(prefix="neetcode_dojo_submission_") as directory:
        root = Path(directory).resolve()
        write_files(root, files)
        yield root


def write_files(root: Path, files: Sequence[SubmissionFile]) -> None:
    """Write a snapshot under ``root``, refusing paths that escape it."""
    seen: set[str] = set()
    for file in files:
        relative = _safe_relative(file.path)
        if relative in seen:
            raise SubmissionError(f"the submission lists {file.path!r} more than once")
        seen.add(relative)
        target = (root / relative).resolve()
        if target != root and root not in target.parents:
            raise SubmissionError(f"{file.path!r} escapes the submission directory")
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(file.content, encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            raise SubmissionError(f"cannot write {file.path!r}: {exc}") from exc


def resolve_entry(
    files: Sequence[SubmissionFile],
    *,
    root: Path,
    item: str,
    explicit: str | None = None,
) -> EntryPoint | None:
    """Decide the entry point and the file that defines it.

    Order: an explicit ``entry_point`` on the request, else the curriculum's
    workspace template, else the first top-level definition in a submitted
    ``solution.py``. The submitted file is then the preferred ``solution.py``, the
    first file that defines the symbol, or the only Python file."""
    function = explicit
    if function is None:
        template = _template_source(root, item)
        if template is not None:
            function = parse_entry_point(template)
    if function is None:
        function = _first_definition_in_solution(files)
    if function is None:
        return None
    code_file = _code_file_for(files, function)
    if code_file is None:
        return None
    return EntryPoint(function=function, code_file=code_file)


def parse_entry_point(source: str) -> str | None:
    """The first top-level function or class defined in a workspace template."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            return node.name
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return node.name
    return None


def defines(source: str, name: str) -> bool:
    """Whether ``source`` defines ``name`` at module level (syntax errors: no)."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return False
    return any(
        isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
        and node.name == name
        for node in tree.body
    )


def _code_file_for(files: Sequence[SubmissionFile], function: str) -> str | None:
    candidates = [
        file
        for file in files
        if file.path.endswith(".py") and PurePosixPath(file.path).name != "check.py"
    ]
    preferred = next(
        (file for file in candidates if PurePosixPath(file.path).name == "solution.py"),
        None,
    )
    if preferred is not None and defines(preferred.content, function):
        return preferred.path
    for file in candidates:
        if defines(file.content, function):
            return file.path
    if preferred is not None:
        return preferred.path
    if len(candidates) == 1:
        return candidates[0].path
    return None


def _first_definition_in_solution(files: Sequence[SubmissionFile]) -> str | None:
    for file in files:
        if PurePosixPath(file.path).name == "solution.py":
            return parse_entry_point(file.content)
    return None


def _template_source(root: Path, item: str) -> str | None:
    """The first workspace template the port-plan layout could hold, read as text."""
    content = root / "content" / item
    candidates: list[Path] = []
    workspace = content / "workspace"
    if workspace.is_file():
        candidates.append(workspace)
    elif workspace.is_dir():
        solution = workspace / "solution.py"
        if solution.is_file():
            candidates.append(solution)
        candidates.extend(sorted(workspace.glob("*.py")))
    candidates.append(content / "workspace.py")
    candidates.append(content / "solution.py")
    for path in candidates:
        if not path.is_file():
            continue
        try:
            return path.read_text(encoding="utf-8")
        except OSError, UnicodeDecodeError:
            continue
    return None


def _safe_relative(path: str) -> str:
    """Reject absolute paths, parent traversal and NUL bytes."""
    if not path or "\x00" in path:
        raise SubmissionError("a submission path is empty or contains a NUL byte")
    pure = PurePosixPath(path)
    if pure.is_absolute() or any(part == ".." for part in pure.parts):
        raise SubmissionError(f"submission path {path!r} escapes the workspace")
    if not pure.parts:
        raise SubmissionError(f"submission path {path!r} is empty")
    return str(pure)
