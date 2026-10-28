"""Subprocess-isolated execution of student code against test cases.

Verdict model: case dicts carry an optional ``compare`` mode; the default is
strict JSON equality (no leniency — a non-serializable return fails the case):

- ``"sorted"``    — deep-sort both sides before JSON equality (any order).
- ``"rounded:n"`` — round floats to n decimals before equality.
- ``"approx:t"``  — recursive absolute tolerance t for floats.
- ``"mutates"``   — in-place items: ``expected`` is the argument list as it must
  stand *after* the call, and the post-call arguments are what gets compared (the
  return value is ``None`` and carries no information).
- ``"predicate"`` — the case names a checker the *parent* holds. The harness runs
  the call and reports the raw value; the runner asks the checker for the verdict
  in a separate bounded child (assessment code never runs in the server's process
  and never executes in the same process as the student's module). A predicate case
  with no checker available is an error, never a strict compare — "any valid
  sample" graded as equality against ``expected`` would be a wrong verdict wearing
  a right one's clothes.
- ``"ops"``       — class problems: the case has ``ops`` (a list of
  ``[method, *args]``) and ``expected`` (per-op outputs); the harness instantiates
  ``function_name`` and replays the sequence.

Hardening: output is collected through temp files and read back capped, the child
runs in its own process group and is killed as a group on timeout, the result JSON
is read as "the last parseable line" (so a print from a stray thread cannot corrupt
it), and a malformed protocol is a ``status="error"`` report rather than an
exception out of :func:`run_cases`.

``python=`` is the runner seam: the judge executes the harness with an interpreter
the curriculum chooses.
"""

from __future__ import annotations

import contextlib
import json
import sys
import tempfile
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from neetcode_dojo.proc import last_json_object, run_capped

#: A case's predicate: (name, got, args) -> bool. Supplied by the caller (the
#: assessment loader's bounded child), never imported into this process.
type Checker = Callable[[str, Any, Any], bool]

HARNESS = r'''
import importlib.util
import json
import os
import sys
import tempfile
import time

sys.path.insert(0, os.getcwd())

# Verdict semantics live in one place, shared with the parent runner.
from neetcode_dojo.judge.compare import case_verdict

from neetcode_dojo.proc import apply_child_limits

apply_child_limits()

PRINT_CAP = 4000
#: Raw file-descriptor 1 output kept per case (before the combined truncation).
FD_CAP = 8192


class Capped:
    """stdout replacement that stops growing at ``cap`` bytes.

    The old version accumulated everything in a StringIO and sliced afterwards,
    so the cap bounded what was *shown* and nothing else: a print loop reached
    ~1.9 GB in three seconds."""

    def __init__(self, cap=PRINT_CAP):
        self.cap = cap
        self._parts = []
        self._size = 0
        self.truncated = False

    def write(self, text):
        if self._size >= self.cap:
            self.truncated = True
            return len(text)
        room = self.cap - self._size
        self._parts.append(text[:room])
        self._size += min(len(text), room)
        if len(text) > room:
            self.truncated = True
        return len(text)

    def flush(self):
        pass

    def isatty(self):
        return False

    def getvalue(self):
        text = "".join(self._parts)
        return text + "\n[neetcode_dojo: further output truncated]" if self.truncated else text


#: The output of the most recent isolated call. Kept outside the call so a case
#: that *raises* still reports what it printed — prints are the debugging loop.
LAST = {"printed": ""}


def isolated(call):
    """Run user code with stdout captured at both levels.

    ``sys.stdout`` catches `print`; file descriptor 1 catches `os.write(1, …)`,
    `print(..., file=sys.__stdout__)`, and output a child process inherits. The
    fd goes to a temp file, and only a bounded slice is read back."""
    real_stdout = sys.stdout
    buffer = Capped()
    sys.stdout = buffer
    saved_fd = None
    tmp = None
    LAST["printed"] = ""
    try:
        try:
            sys.stdout.flush()
            saved_fd = os.dup(1)
            tmp = tempfile.TemporaryFile()
            os.dup2(tmp.fileno(), 1)
        except OSError:
            saved_fd = None
        try:
            return call()
        finally:
            LAST["printed"] = _collect(buffer, tmp)
    finally:
        sys.stdout = real_stdout
        if tmp is not None:
            try:
                sys.stdout.flush()
            except Exception:
                pass
            if saved_fd is not None:
                try:
                    os.dup2(saved_fd, 1)
                    os.close(saved_fd)
                except OSError:
                    pass
            try:
                tmp.close()
            except OSError:
                pass


def _collect(buffer, tmp):
    text = buffer.getvalue()
    if tmp is not None:
        try:
            tmp.seek(0)
            raw = tmp.read(FD_CAP).decode("utf-8", "replace")
        except OSError:
            raw = ""
        if raw:
            text = text + ("\n" if text and not text.endswith("\n") else "") + raw
    return text[: 2 * PRINT_CAP]


def _expected(case):
    """The case's expected value — read defensively, inside the per-case try.

    It used to be read outside the per-case try, so one malformed case killed the
    harness and took every other case's result with it."""
    return case["expected"]


def main():
    function_name = sys.argv[1]
    code_file = sys.argv[2]
    with open("_dojo_cases.json") as f:
        cases = json.load(f)
    spec = importlib.util.spec_from_file_location("solution", code_file)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load the submission file {code_file!r}")
    solution = importlib.util.module_from_spec(spec)
    try:
        isolated(lambda: spec.loader.exec_module(solution))
    except BaseException as exc:  # import failure is a real verdict
        results = [
            {
                "label": "import",
                "passed": False,
                "expected": None,
                "got": None,
                "error": f"{type(exc).__name__}: {exc}",
                "printed": LAST["printed"],
                "elapsed_ms": 0.0,
            }
        ]
        _emit(results)
        return
    results = []
    for i, case in enumerate(cases):
        label = case.get("label", f"case {i}")
        mode = case.get("compare", "strict")
        predicate = case.get("predicate")
        t0 = time.perf_counter()
        expected = None
        try:
            expected = _expected(case)
            if "ops" in case:
                obj = isolated(
                    lambda: getattr(solution, function_name)(*case.get("ctor_args", []))
                )
                got = isolated(
                    lambda: [getattr(obj, method)(*args) for method, *args in case["ops"]]
                )
            else:
                fn = getattr(solution, function_name)
                got = isolated(lambda: fn(*case["args"]))
            record = {
                "label": label,
                "passed": False,
                "expected": expected,
                "got": got,
                "error": None,
                "printed": LAST["printed"],
                "elapsed_ms": (time.perf_counter() - t0) * 1000,
            }
            if predicate:
                # The parent owns the checker; the harness only reports the raw
                # value it produced. Deciding here would require importing the
                # assessment module into the student's process.
                record["predicate"] = predicate
            else:
                passed = case_verdict(case, got, case.get("args"))
                if mode == "mutates":
                    # The contract is the effect on the arguments, so that is
                    # what "got" must show — reporting None (the return) beside
                    # an expected matrix reads as an evaluator bug.
                    record["got"] = case["args"]
                record["passed"] = bool(passed)
            results.append(record)
        except BaseException as exc:  # SystemExit and friends included
            results.append(
                {
                    "label": label,
                    "passed": False,
                    "expected": expected,
                    "got": None,
                    "error": f"{type(exc).__name__}: {exc}",
                    "printed": LAST["printed"],
                    "elapsed_ms": (time.perf_counter() - t0) * 1000,
                }
            )
    _emit(results)


def _emit(results):
    """Write the protocol line with one `os.write` on the real fd 1.

    A single write cannot be interleaved with a print from a background thread,
    and the parent reads the last parseable line regardless."""
    blob = (json.dumps(results) + "\n").encode("utf-8", "replace")
    os.write(1, blob)


if __name__ == "__main__":
    main()
'''

#: Harness and protocol file names inside a submission directory. Prefixed so they
#: cannot collide with a student's own files, and removed after the run.
HARNESS_FILE = "_dojo_harness.py"
CASES_FILE = "_dojo_cases.json"


@dataclass
class CaseResult:
    label: str
    passed: bool
    expected: Any
    got: Any
    error: str | None
    elapsed_ms: float
    printed: str = ""
    predicate: str | None = None


@dataclass
class JudgeReport:
    status: str  # correct | wrong_answer | error | timed_out
    results: list[CaseResult] = field(default_factory=list)
    total: int = 0
    passed: int = 0

    @property
    def all_passed(self) -> bool:
        return self.status == "correct"


def _error_report(total: int, label: str, message: str) -> JudgeReport:
    return JudgeReport(
        status="error",
        total=total,
        passed=0,
        results=[
            CaseResult(
                label=label,
                passed=False,
                expected=None,
                got=None,
                error=message,
                elapsed_ms=0.0,
            )
        ],
    )


def _status(results: list[CaseResult]) -> str:
    passed = sum(1 for result in results if result.passed)
    if passed == len(results):
        return "correct"
    if any(result.error for result in results):
        # A crash is not a wrong answer: "my code raised" and "my logic is wrong"
        # are different coaching problems.
        return "error"
    return "wrong_answer"


def run_cases(
    code_path: Path,
    function_name: str,
    cases: Sequence[Mapping[str, Any]],
    timeout: float = 10.0,
    python: Path | str | None = None,
    checker: Checker | None = None,
) -> JudgeReport:
    """Run ``cases`` against the single file in ``code_path`` in a subprocess.

    A convenience wrapper over :func:`run_cases_in` for one-file submissions and the
    ported tests; multi-file snapshots use ``run_cases_in`` directly so sibling
    imports resolve."""
    with tempfile.TemporaryDirectory(prefix="neetcode_dojo_judge_") as tmp:
        root = Path(tmp)
        target = root / "solution.py"
        try:
            target.write_text(code_path.read_text(encoding="utf-8"), encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            return _error_report(
                len(cases), "harness", f"cannot read the submission: {type(exc).__name__}: {exc}"
            )
        return run_cases_in(
            root,
            "solution.py",
            function_name,
            cases,
            timeout=timeout,
            python=python,
            checker=checker,
        )


def run_cases_in(
    root: Path,
    code_file: str,
    function_name: str,
    cases: Sequence[Mapping[str, Any]],
    timeout: float = 10.0,
    python: Path | str | None = None,
    checker: Checker | None = None,
) -> JudgeReport:
    """Run ``cases`` against ``root/code_file`` in a bounded subprocess.

    Never raises for anything the child does: a timeout, a dead process, or an
    unreadable protocol each come back as a report. **An empty case list is
    refused** rather than graded as a pass — ``all_passed`` is true for zero cases,
    which would make an uncurated problem a free solve.

    Predicate cases are decided here, by the caller's ``checker``, after the child
    has returned the raw value: assessment code stays out of the student's process,
    and the caller (the assessment loader) can run the checker in its own bounded
    child. A predicate case with no checker is an error, matching the old engine's
    refusal rather than falling through to equality."""
    case_list = [dict(case) for case in cases]
    if not case_list:
        return _error_report(
            0,
            "no cases",
            "refusing to grade: this item generated no cases — the assessment "
            "module must register @cases",
        )
    harness = root / HARNESS_FILE
    cases_file = root / CASES_FILE
    try:
        harness.write_text(HARNESS, encoding="utf-8")
        cases_file.write_text(json.dumps(case_list), encoding="utf-8")
        result = run_capped(
            [str(python or sys.executable), HARNESS_FILE, function_name, code_file],
            cwd=root,
            timeout=timeout,
        )
    finally:
        for path in (harness, cases_file):
            with contextlib.suppress(OSError):
                path.unlink()
    if result.timed_out:
        return JudgeReport(status="timed_out", total=len(case_list), passed=0)
    raw = last_json_object(result.stdout)
    if raw is None:
        detail = [line for line in (result.stderr or "").strip().splitlines() if line.strip()]
        tail = " | ".join(detail[-3:])[:500]
        return _error_report(
            len(case_list),
            "harness",
            tail
            or "the judge process produced no readable result (it may have been "
            "killed by a resource limit)",
        )
    if not isinstance(raw, list):
        return _error_report(
            len(case_list), "harness", f"unexpected protocol payload: {raw!r}"[:200]
        )

    results: list[CaseResult] = []
    for index, entry in enumerate(raw):
        if not isinstance(entry, Mapping):
            results.append(
                CaseResult(
                    label="harness",
                    passed=False,
                    expected=None,
                    got=None,
                    error=f"unexpected case result: {entry!r}"[:300],
                    elapsed_ms=0.0,
                )
            )
            continue
        case = case_list[index] if index < len(case_list) else {}
        predicate = entry.get("predicate")
        passed = bool(entry.get("passed"))
        error = entry.get("error")
        if predicate and not error:
            passed, error = _decide_predicate(
                checker, str(predicate), entry.get("got"), case, index
            )
        results.append(
            CaseResult(
                label=str(entry.get("label", "?")),
                passed=passed,
                expected=entry.get("expected"),
                got=entry.get("got"),
                error=error,
                elapsed_ms=float(entry.get("elapsed_ms", 0.0) or 0.0),
                printed=str(entry.get("printed", "")),
                predicate=str(predicate) if predicate else None,
            )
        )
    passed_count = sum(1 for result in results if result.passed)
    return JudgeReport(
        status=_status(results),
        results=results,
        total=len(results),
        passed=passed_count,
    )


def _decide_predicate(
    checker: Checker | None,
    name: str,
    got: Any,
    case: Mapping[str, Any],
    index: int,
) -> tuple[bool, str | None]:
    """Ask the caller's checker for one predicate case's verdict."""
    if checker is None:
        return False, (
            f"no checker for the predicate {name!r}: predicate checkers live in the "
            "item's assessment module, which the judge harness does not import"
        )
    try:
        return bool(checker(name, got, case.get("args"))), None
    except BaseException as exc:  # a checker crash is a case error
        return False, f"the {name!r} checker failed: {type(exc).__name__}: {exc}"
