"""The quarantine: assessment code runs *there*, and the server only sees data.

A curriculum's ``assessment/`` holds the answers in machine form — oracles,
references, hidden case generators, measurement plans and predicate checkers. The
contract is:

- it is **never imported by the server** at module scope;
- it is loaded **lazily**, on first use;
- it runs only inside a **bounded subprocess** (``proc.run_capped``, its own process
  group, address-space/file-size/CPU limits, output read back capped);
- it is **never reachable from a prompt builder** — the server carries data, not
  callables, so a request cannot ask for the answers.

Two things happen here, and only these two:

1. **``check_imports``** — a static refusal, before anything is executed: an
   assessment module may import the standard library, the curriculum's declared
   dependencies, and ``neetcode_dojo.registry``. Nothing else.
2. **``run`` / ``probe``** — bounded children that import the modules, generate
   cases, call an oracle/reference/checker, or report what was registered. The
   parent imports none of them.

The plans and rubrics come back as JSON data on purpose: the server needs to know
*what would be measured* (axis, sizes, baseline, compare) to run it, and a plan that
is not data — a callable, an open file — is refused rather than half-used.
"""

from __future__ import annotations

import ast
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from neetcode_dojo import proc
from neetcode_dojo.assessment_harnesses import PROBE_HARNESS, RUN_HARNESS
from neetcode_dojo.measure.probe import Target

#: How long an assessment module gets to import and register. Generous for an
#: import; a module that needs longer is doing something at import time that
#: belongs in a function.
DEFAULT_TIMEOUT = 20.0

#: How long one *run* of assessment code gets. Below the judge's own case timeout,
#: because generating cases must not outlast judging them.
DEFAULT_RUN_TIMEOUT = 10.0

#: The one package module an assessment module may import.
ALLOWED_MODULE = "neetcode_dojo.registry"

#: Item ids are also file names below ``assessment/``; the manifest pattern keeps
#: them path-safe. Re-checked here because a request is untrusted input.
ITEM_ID_RE = r"^[a-z][a-z0-9_-]*$"


@dataclass
class ModuleReport:
    """What one assessment module registered, as seen from outside."""

    path: Path
    registrations: dict[str, list[str]] = field(default_factory=dict)
    #: kind -> registration name -> the Python function's own name, for the
    #: harnesses that import the module and call a function by name.
    functions: dict[str, dict[str, str]] = field(default_factory=dict)
    plans: dict[str, dict[str, Any]] = field(default_factory=dict)
    rubrics: dict[str, dict[str, Any]] = field(default_factory=dict)
    #: What the item's case generator produced when the probe sampled it: whether
    #: every sampled case carried a verdict the judge can decide, and which verdict
    #: tags it used.
    case_samples: dict[str, dict[str, Any]] = field(default_factory=dict)
    error: str | None = None

    @property
    def loaded(self) -> bool:
        return self.error is None

    def names(self, *kinds: str) -> set[str]:
        """The registered names of the given kinds (all item kinds by default)."""
        wanted = kinds or ("oracle", "cases", "inputs", "reference", "rubric", "measure")
        found: set[str] = set()
        for kind in wanted:
            found.update(self.registrations.get(kind, ()))
        return found

    def has(self, kind: str, name: str) -> bool:
        return name in self.registrations.get(kind, ())

    def function_name(self, kind: str, name: str) -> str | None:
        """The Python function behind a registration, for a harness that calls it."""
        return (self.functions.get(kind) or {}).get(name)


@dataclass
class ProbeReport:
    """The result of probing a curriculum's assessment modules."""

    modules: dict[Path, ModuleReport] = field(default_factory=dict)
    timed_out: bool = False
    stderr: str = ""
    fatal: str | None = None

    def report_for(self, path: Path) -> ModuleReport | None:
        return self.modules.get(Path(path))

    def plan_for(self, path: Path, item_id: str) -> dict[str, Any] | None:
        report = self.report_for(path)
        return report.plans.get(item_id) if report else None

    def errors(self) -> list[str]:
        found: list[str] = []
        if self.fatal:
            found.append(self.fatal)
        if self.timed_out:
            found.append(f"the assessment probe timed out; its stderr was: {self.stderr.strip()}")
        for path, report in self.modules.items():
            if report.error:
                found.append(f"{path.name}: {report.error}")
        return found


@dataclass
class RunResult:
    """What one bounded run of a curriculum's assessment code produced.

    Never raises: code that hangs, crashes or returns something the server cannot
    use is a *result*, because the submission has to keep going and the evidence
    has to say what happened."""

    ok: bool
    value: Any = None
    error: str | None = None
    timed_out: bool = False
    #: For an `oracle`/`reference` call only: the argument list as the call left it.
    mutated_args: Any = None

    def __bool__(self) -> bool:
        return self.ok


def check_imports(source: str, *, dependencies: tuple[str, ...] = ()) -> list[str]:
    """Static refusal of imports outside the allowances.

    Returns problems, each naming the line — it executes nothing, so it can be
    called before the module is ever run."""
    allowed = set(sys.stdlib_module_names)
    allowed.update(
        dependency.split("[")[0].split("=")[0].split(">")[0].strip() for dependency in dependencies
    )
    problems: list[str] = []
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        return [f"line {exc.lineno}: does not parse ({exc.msg})"]
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if not _allowed(alias.name, allowed):
                    problems.append(f"line {node.lineno}: imports {alias.name!r}")
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                problems.append(
                    f"line {node.lineno}: relative imports are not allowed in an "
                    "assessment module (it is loaded by path)"
                )
                continue
            module = node.module or ""
            for alias in node.names:
                candidate = f"{module}.{alias.name}" if module else alias.name
                if _allowed(candidate, allowed) or _allowed(module, allowed):
                    continue
                problems.append(f"line {node.lineno}: imports {candidate!r}")
    return problems


def _allowed(module: str, allowed: set[str]) -> bool:
    if not module:
        return False
    if module.split(".")[0] in allowed:
        return True
    return module == ALLOWED_MODULE or module.startswith(ALLOWED_MODULE + ".")


def probe_modules(
    paths: list[Path],
    *,
    python: str | None = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> ProbeReport:
    """Import ``paths`` in one bounded child and report what they registered.

    The parent imports none of them. A module that raises at import time, a
    measurement plan that is not JSON data, and a module that hangs are all
    *reported*, never raised."""
    paths = [Path(path) for path in paths]
    report = ProbeReport()
    if not paths:
        return report
    interpreter = python or sys.executable
    result = proc.run_capped(
        [interpreter, "-c", PROBE_HARNESS, json.dumps([str(path) for path in paths])],
        cwd=str(paths[0].parent),
        timeout=timeout,
    )
    if result.timed_out:
        report.timed_out = True
        report.stderr = result.stderr
        return report
    payload = proc.last_json_object(result.stdout)
    if not isinstance(payload, dict):
        report.fatal = (
            "the assessment probe produced no readable result "
            f"(exit {result.returncode}): "
            f"{result.stderr.strip()[:400] or result.stdout.strip()[:400]}"
        )
        return report
    if "fatal" in payload:
        report.fatal = str(payload["fatal"])
        return report
    for raw_path, entry in payload.items():
        path = Path(raw_path)
        if not isinstance(entry, dict):
            continue
        report.modules[path] = ModuleReport(
            path=path,
            registrations=entry.get("registrations") or {},
            functions=entry.get("functions") or {},
            plans=entry.get("plans") or {},
            rubrics=entry.get("rubrics") or {},
            case_samples=entry.get("case_samples") or {},
            error=entry.get("error") or None,
        )
    return report


def run(
    request: dict[str, Any],
    *,
    python: str | None = None,
    timeout: float = DEFAULT_RUN_TIMEOUT,
    cwd: Path | str | None = None,
) -> RunResult:
    """Run one assessment request in a bounded child and return its result."""
    module = Path(request.get("module", ""))
    interpreter = python or sys.executable
    working = cwd
    if working is None:
        working = module.parent if module.parent.exists() else Path.cwd()
    result = proc.run_capped(
        [interpreter, "-c", RUN_HARNESS, json.dumps(request)],
        cwd=str(working),
        timeout=timeout,
    )
    if result.timed_out:
        return RunResult(False, None, f"timed out after {timeout:g}s", timed_out=True)
    payload = proc.last_json_object(result.stdout)
    if not isinstance(payload, dict):
        detail = (result.stderr or result.stdout or "").strip()[:400]
        return RunResult(False, None, f"the run produced no readable result: {detail}")
    if not payload.get("ok"):
        return RunResult(False, None, str(payload.get("error") or "the run failed"))
    if "cases" in payload:
        return RunResult(True, payload["cases"])
    if "inputs" in payload:
        return RunResult(True, payload["inputs"])
    if "values" in payload:
        return RunResult(True, payload["values"])
    if "passed" in payload:
        return RunResult(True, bool(payload["passed"]))
    if "args" in payload:
        return RunResult(True, payload["args"])
    if "mutated_args" in payload:
        return RunResult(True, payload.get("value"), mutated_args=payload["mutated_args"])
    return RunResult(True, payload.get("value"))


def run_cases(
    module: Path,
    item_id: str,
    requests: list[dict[str, Any]],
    *,
    python: str | None = None,
    timeout: float = DEFAULT_RUN_TIMEOUT,
) -> RunResult:
    """Generate judge cases: ``[{"n": 8, "seed": "…"}, …]`` -> the judge's case shape."""
    return run(
        {"module": str(module), "kind": "cases", "item": item_id, "requests": requests},
        python=python,
        timeout=timeout,
    )


def run_inputs(
    module: Path,
    item_id: str,
    n: int,
    seed: str,
    *,
    python: str | None = None,
    timeout: float = DEFAULT_RUN_TIMEOUT,
) -> RunResult:
    """The input at one rung of the measurement ladder (no expected value)."""
    return run(
        {"module": str(module), "kind": "inputs", "item": item_id, "n": n, "seed": seed},
        python=python,
        timeout=timeout,
    )


def run_inputs_many(
    module: Path,
    item_id: str,
    requests: list[dict[str, Any]],
    *,
    python: str | None = None,
    timeout: float = DEFAULT_RUN_TIMEOUT,
) -> RunResult:
    """The whole ladder in one child: ``[{"n": 100, "seed": "…"}, …]`` -> inputs.

    One process for seven rungs rather than seven: the measurement is already the
    most expensive thing a submission does, and a spawn per size is time nobody gets
    back."""
    return run(
        {"module": str(module), "kind": "inputs_many", "item": item_id, "requests": requests},
        python=python,
        timeout=timeout,
    )


def call(
    module: Path,
    item_id: str,
    kind: str,
    args: list[Any] | None = None,
    *,
    python: str | None = None,
    timeout: float = DEFAULT_RUN_TIMEOUT,
) -> RunResult:
    """Call ``@oracle``, ``@reference`` or ``@rubric`` for an item, in a child."""
    return run(
        {"module": str(module), "kind": kind, "item": item_id, "args": list(args or [])},
        python=python,
        timeout=timeout,
    )


def call_oracle_many(
    module: Path,
    item_id: str,
    calls: list[dict[str, Any]],
    *,
    python: str | None = None,
    timeout: float = DEFAULT_RUN_TIMEOUT,
) -> RunResult:
    """Call ``@oracle`` once per entry in one child.

    ``calls`` entries are ``{"args": [...]}`` or ``{"ops": [...]}``; each result is
    ``{"ok": bool, "value": ..., "mutated_args": [...]}`` or an error. Batching keeps
    a 20-case oracle check to one process instead of twenty."""
    return run(
        {"module": str(module), "kind": "oracle_many", "item": item_id, "calls": calls},
        python=python,
        timeout=timeout,
    )


def call_checker(
    module: Path,
    item_id: str,
    checker: str,
    got: Any,
    args: Any,
    *,
    code_file: str,
    cwd: Path,
    python: str | None = None,
    timeout: float = DEFAULT_RUN_TIMEOUT,
) -> RunResult:
    """Decide one predicate case in a bounded child.

    The child's working directory is the materialized submission, so the checker can
    load the student's module by ``code_file`` — the old ``(module, got, args)``
    checker signature — without crossing into the server's process."""
    return run(
        {
            "module": str(module),
            "kind": "checker",
            "item": item_id,
            "checker": checker,
            "got": got,
            "args": args,
            "code_file": code_file,
        },
        python=python,
        timeout=timeout,
        cwd=cwd,
    )


class AssessmentStore:
    """One curriculum's private assessment tree, reached only through children."""

    def __init__(self, root: Path | str | None = None, *, python: str | None = None):
        self.root = Path(root).expanduser().resolve() if root is not None else None
        self.python = python
        self._reports: dict[str, ModuleReport] = {}

    @classmethod
    def from_package(cls, *, python: str | None = None) -> AssessmentStore:
        """The store for this package's own ``assessment/`` directory."""
        return cls(Path(__file__).resolve().parent / "assessment", python=python)

    def module_for(self, item_id: str) -> Path | None:
        """The private module for one item, by the port-plan file convention."""
        if self.root is None or not _is_item_id(item_id):
            return None
        candidate = self.root / f"{item_id}.py"
        return candidate if candidate.is_file() else None

    def paths(self) -> list[Path]:
        """Every assessment module in the tree, sorted (a curriculum gate view)."""
        if self.root is None or not self.root.is_dir():
            return []
        return sorted(path for path in self.root.glob("*.py") if path.name != "__init__.py")

    def report(self, item_id: str, *, refresh: bool = False) -> ModuleReport | None:
        """Probe one item's module, cached for the life of the server process."""
        path = self.module_for(item_id)
        if path is None:
            return None
        if not refresh and item_id in self._reports:
            return self._reports[item_id]
        probe = probe_modules([path], python=self.python)
        report = probe.report_for(path)
        if report is None:
            report = ModuleReport(
                path=path,
                error=probe.fatal or "the assessment probe produced no report",
            )
        self._reports[item_id] = report
        return report

    def registrations(self, item_id: str) -> dict[str, list[str]]:
        report = self.report(item_id)
        return report.registrations if report else {}

    def has(self, item_id: str, kind: str) -> bool:
        report = self.report(item_id)
        return bool(report and report.has(kind, item_id))

    def plan(self, item_id: str) -> dict[str, Any] | None:
        report = self.report(item_id)
        if report is None:
            return None
        return report.plans.get(item_id)

    def function_name(self, item_id: str, kind: str) -> str | None:
        report = self.report(item_id)
        return report.function_name(kind, item_id) if report else None

    def reference_target(self, item_id: str) -> Target | None:
        """The canonical reference as a measurement target, or None."""
        path = self.module_for(item_id)
        function = self.function_name(item_id, "reference")
        if path is None or function is None:
            return None
        return Target("reference", path, function)

    def cases(
        self, item_id: str, requests: list[dict[str, Any]], *, timeout: float = DEFAULT_RUN_TIMEOUT
    ) -> RunResult:
        path = self.module_for(item_id)
        if path is None:
            return RunResult(False, None, f"{item_id!r} has no assessment module")
        return run_cases(path, item_id, requests, python=self.python, timeout=timeout)

    def inputs(
        self,
        item_id: str,
        n: int,
        seed: str,
        *,
        timeout: float = DEFAULT_RUN_TIMEOUT,
    ) -> RunResult:
        path = self.module_for(item_id)
        if path is None:
            return RunResult(False, None, f"{item_id!r} has no assessment module")
        return run_inputs(path, item_id, n, seed, python=self.python, timeout=timeout)

    def inputs_many(
        self,
        item_id: str,
        requests: list[dict[str, Any]],
        *,
        timeout: float = DEFAULT_RUN_TIMEOUT,
    ) -> RunResult:
        path = self.module_for(item_id)
        if path is None:
            return RunResult(False, None, f"{item_id!r} has no assessment module")
        return run_inputs_many(path, item_id, requests, python=self.python, timeout=timeout)

    def call(
        self,
        item_id: str,
        kind: str,
        args: list[Any] | None = None,
        *,
        timeout: float = DEFAULT_RUN_TIMEOUT,
    ) -> RunResult:
        path = self.module_for(item_id)
        if path is None:
            return RunResult(False, None, f"{item_id!r} has no assessment module")
        return call(path, item_id, kind, args, python=self.python, timeout=timeout)

    def oracle_many(
        self,
        item_id: str,
        calls: list[dict[str, Any]],
        *,
        timeout: float = DEFAULT_RUN_TIMEOUT,
    ) -> RunResult:
        path = self.module_for(item_id)
        if path is None:
            return RunResult(False, None, f"{item_id!r} has no assessment module")
        return call_oracle_many(path, item_id, calls, python=self.python, timeout=timeout)

    def check_predicate(
        self,
        item_id: str,
        checker: str,
        got: Any,
        args: Any,
        *,
        code_file: str,
        cwd: Path,
        timeout: float = DEFAULT_RUN_TIMEOUT,
    ) -> bool:
        """Decide a predicate, or raise with the child's error (the judge turns that
        into a case error rather than a crash)."""
        path = self.module_for(item_id)
        if path is None:
            raise LookupError(f"{item_id!r} has no assessment module")
        result = call_checker(
            path,
            item_id,
            checker,
            got,
            args,
            code_file=code_file,
            cwd=cwd,
            python=self.python,
            timeout=timeout,
        )
        if not result.ok:
            raise RuntimeError(result.error or "the predicate checker failed")
        return bool(result.value)


def _is_item_id(item_id: str) -> bool:
    return re.fullmatch(ITEM_ID_RE, item_id) is not None
