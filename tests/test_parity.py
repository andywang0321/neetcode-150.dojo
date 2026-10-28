"""Parity: the old engine's judge and the new case runner agree on submissions.

The old judge is executed **in a subprocess** with the old checkout's ``src/`` on
``PYTHONPATH``; this test module never imports ``dojo``. When the old checkout is not
present (a fresh clone of the curriculum), the parity tests skip rather than fail —
the curriculum's own tests must not depend on a sibling repository.

Cases and submissions are shared verbatim between the two judges, so the comparison
is of semantics, not of test data. Wall-clock timeouts are excluded on purpose: a
timeout is a property of the machine, not a verdict two implementations can be
expected to reproduce to the millisecond.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from neetcode_dojo.judge.runner import run_cases

DRIVER = Path(__file__).resolve().parent / "parity" / "old_judge_driver.py"


def _old_engine() -> Path | None:
    """The read-only old checkout, if this machine has one."""
    candidates: list[Path] = []
    configured = os.environ.get("DOJO_OLD_ENGINE")
    if configured:
        candidates.append(Path(configured).expanduser())
    here = Path(__file__).resolve()
    for parent in here.parents:
        candidates.append(parent / "dojo")
    for candidate in candidates:
        if (candidate / "src" / "dojo" / "judge" / "runner.py").is_file():
            return candidate.resolve()
    return None


OLD_ENGINE = _old_engine()

pytestmark = pytest.mark.skipif(
    OLD_ENGINE is None,
    reason="the read-only old engine checkout is not available for a parity run",
)


def _run_old(code: str, function: str, cases: list[dict[str, Any]]) -> dict[str, Any]:
    assert OLD_ENGINE is not None
    env = dict(os.environ)
    source = str(OLD_ENGINE / "src")
    env["PYTHONPATH"] = source + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    completed = subprocess.run(
        [sys.executable, str(DRIVER)],
        input=json.dumps({"code": code, "function": function, "cases": cases}),
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(DRIVER.parent),
        env=env,
        check=False,
    )
    assert completed.returncode == 0, completed.stderr
    return json.loads(completed.stdout.strip().splitlines()[-1])


def _run_new(tmp_path: Path, code: str, function: str, cases: list[dict[str, Any]]) -> Any:
    path = tmp_path / "solution.py"
    path.write_text(code, encoding="utf-8")
    return run_cases(path, function, cases)


def _assert_parity(tmp_path: Path, code: str, function: str, cases: list[dict[str, Any]]) -> None:
    old = _run_old(code, function, cases)
    new = _run_new(tmp_path, code, function, cases)
    assert old["status"] == new.status, (old, new)
    assert old["passed"] == new.passed
    assert old["total"] == new.total
    assert [(entry["label"], entry["passed"]) for entry in old["results"]] == [
        (result.label, result.passed) for result in new.results
    ], (old, new)


# The representative comparison/checker shapes from the old corpus: strict 113,
# mutates 5, sorted 3, none 6 (measurement-only), plus ops and predicate cases.

PARENS_CASES = [
    {"args": ["()"], "expected": True, "label": "ok1"},
    {"args": ["([)]"], "expected": False, "label": "ok2"},
    {"args": ["("], "expected": False, "label": "ok3"},
]
PARENS_CORRECT = (
    "def is_valid(s):\n"
    "    pairs = {')': '(', ']': '[', '}': '{'}\n"
    "    stack = []\n"
    "    for char in s:\n"
    "        if char in '([{':\n"
    "            stack.append(char)\n"
    "        elif not stack or stack.pop() != pairs[char]:\n"
    "            return False\n"
    "    return not stack\n"
)
PARENS_WRONG = "def is_valid(s):\n    return s.count('(') == s.count(')')\n"
PARENS_CRASH = "def is_valid(s):\n    raise RuntimeError('boom')\n"

SORTED_CASES = [
    {
        "args": [[["b", "a"], ["c"]]],
        "expected": [["c"], ["a", "b"]],
        "compare": "sorted",
        "label": "sorted",
    },
]
SORTED_CORRECT = (
    "def group_anagrams(strs):\n"
    "    groups = {}\n"
    "    for word in strs:\n"
    "        groups.setdefault(''.join(sorted(word)), []).append(word)\n"
    "    return list(groups.values())\n"
)
SORTED_WRONG = "def group_anagrams(strs):\n    return list(strs)\n"

ROTATE_CASES = [
    {
        "args": [[[1, 2], [3, 4]]],
        "expected": [[[3, 1], [4, 2]]],
        "compare": "mutates",
        "label": "2x2",
    },
    {"args": [[[7]]], "expected": [[[7]]], "compare": "mutates", "label": "1x1"},
]
ROTATE_CORRECT = "def rotate(matrix):\n    matrix[:] = [list(row) for row in zip(*matrix[::-1])]\n"
ROTATE_REBIND = "def rotate(matrix):\n    matrix = [list(row) for row in zip(*matrix[::-1])]\n"

OPS_CASES = [
    {
        "ops": [["push", 1], ["push", 2], ["getMin"], ["pop"], ["top"], ["getMin"]],
        "expected": [None, None, 1, None, 2, 2],
        "label": "stack",
    }
]
OPS_CORRECT = (
    "class MinStack:\n"
    "    def __init__(self):\n"
    "        self.stack = []\n"
    "        self.mins = []\n"
    "    def push(self, val):\n"
    "        self.stack.append(val)\n"
    "        self.mins.append(min(val, self.mins[-1]) if self.mins else val)\n"
    "    def pop(self):\n"
    "        self.stack.pop()\n"
    "        self.mins.pop()\n"
    "    def top(self):\n"
    "        return self.stack[-1]\n"
    "    def getMin(self):\n"
    "        return self.mins[-1]\n"
)
OPS_WRONG = (
    "class MinStack:\n"
    "    def __init__(self):\n"
    "        self.stack = []\n"
    "    def push(self, val):\n"
    "        self.stack.append(val)\n"
    "    def pop(self):\n"
    "        self.stack.pop()\n"
    "    def top(self):\n"
    "        return self.stack[-1]\n"
    "    def getMin(self):\n"
    "        return self.stack[0]\n"
)

NONE_CASES = [
    {"args": [1], "expected": 2, "compare": "none", "label": "none-ok"},
    {"args": [2], "expected": 9, "compare": "none", "label": "none-bad"},
]
NONE_CORRECT = "def f(x):\n    return x + 1\n"

PREDICATE_CASES = [
    {"args": [[1, 2]], "expected": True, "predicate": "positive", "label": "pred"},
]
PREDICATE_CODE = "def f(values):\n    return sum(values) > 0\n"


@pytest.mark.parametrize(
    ("code", "function", "cases"),
    [
        (PARENS_CORRECT, "is_valid", PARENS_CASES),
        (PARENS_WRONG, "is_valid", PARENS_CASES),
        (PARENS_CRASH, "is_valid", PARENS_CASES),
        (SORTED_CORRECT, "group_anagrams", SORTED_CASES),
        (SORTED_WRONG, "group_anagrams", SORTED_CASES),
        (ROTATE_CORRECT, "rotate", ROTATE_CASES),
        (ROTATE_REBIND, "rotate", ROTATE_CASES),
        (OPS_CORRECT, "MinStack", OPS_CASES),
        (OPS_WRONG, "MinStack", OPS_CASES),
        (NONE_CORRECT, "f", NONE_CASES),
        (PREDICATE_CODE, "f", PREDICATE_CASES),
    ],
)
def test_the_old_judge_and_the_new_runner_agree(
    tmp_path: Path, code: str, function: str, cases: list[dict[str, Any]]
) -> None:
    _assert_parity(tmp_path, code, function, cases)


def test_an_empty_case_list_is_refused_by_both(tmp_path: Path) -> None:
    _assert_parity(tmp_path, PARENS_CORRECT, "is_valid", [])


def test_the_new_runner_decides_predicates_the_old_harness_could_not(
    tmp_path: Path,
) -> None:
    """The intended deviation from the old judge: a predicate case is decided by the
    curriculum's checker. The old engine's harness had an empty checker registry, so
    it reported every predicate case as an error; the port plan calls the new server
    owning the checker "the clean fix"."""
    old = _run_old(PREDICATE_CODE, "f", PREDICATE_CASES)
    assert old["status"] == "error"
    assert all(entry["passed"] is False for entry in old["results"])

    path = tmp_path / "solution.py"
    path.write_text(PREDICATE_CODE, encoding="utf-8")

    def checker(name: str, got: Any, args: Any) -> bool:
        return name == "positive" and got > 0

    new = run_cases(path, "f", PREDICATE_CASES, checker=checker)
    assert new.status == "correct"
    assert new.passed == 1
