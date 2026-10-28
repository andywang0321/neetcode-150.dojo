"""Analyze submitted files into the facts the review cites.

The analysis is pure: it reads only the `SubmissionFile.content` strings that arrived in
the review request. It never executes the submission and never touches the filesystem.
"""

import ast
from collections.abc import Sequence

from reviewer.analysis.model import Analysis, FileFacts, FunctionFacts, Issue
from reviewer.analysis.rules import (
    call_constructs,
    call_name,
    compares_none,
    except_issues,
    is_dp_row,
    is_guard,
    issue,
    range_len,
    type_hint_ratio,
    uses_memo,
)
from reviewer.analysis.shape import (
    function_facts,
    has_binary_search_loop,
    has_two_pointer,
    max_loop_depth,
    max_nesting,
)
from reviewer.contracts import SubmissionFile

_HARNESS_FILES = frozenset({"check.py", "conftest.py", "__init__.py"})
_LONG_FUNCTION = 20
_DEEP_NESTING = 4


def analyze(files: Sequence[SubmissionFile]) -> Analysis:
    """Analyze the student's Python files; never raises on malformed source."""
    selected = tuple(file for file in files if _is_reviewable(file.path))
    return Analysis(files=tuple(_analyze_file(file) for file in selected))


def _is_reviewable(path: str) -> bool:
    name = path.rsplit("/", 1)[-1].lower()
    return name.endswith(".py") and name not in _HARNESS_FILES


def _analyze_file(file: SubmissionFile) -> FileFacts:
    lines = 0 if not file.content else file.content.count("\n") + 1
    try:
        tree = ast.parse(file.content, filename=file.path)
    except SyntaxError as error:
        return _broken(file, lines, error.msg, error.lineno or 1)
    except ValueError as error:
        return _broken(file, lines, str(error), 1)
    return _facts(file, lines, tree)


def _broken(file: SubmissionFile, lines: int, reason: str, line: int) -> FileFacts:
    finding = Issue("syntax", file.path, line, "high", f"syntax error: {reason}")
    return FileFacts(
        path=file.path,
        lines=lines,
        syntax_error=reason,
        functions=(),
        imports=frozenset(),
        constructs=frozenset(),
        issues=(finding,),
        guards=False,
        type_hints=0.0,
        max_nesting=0,
    )


def _facts(file: SubmissionFile, lines: int, tree: ast.Module) -> FileFacts:
    imports: set[str] = set()
    constructs: set[str] = set()
    findings: list[Issue] = []
    guards = False
    functions: list[FunctionFacts] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.update(f"{node.module}.{alias.name}" for alias in node.names)
        elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
            facts = function_facts(node)
            functions.append(facts)
            if uses_memo(node):
                constructs.add("memo")
            findings.extend(_default_issues(node, file.path))
            findings.extend(_shape_issues(node, facts, file.path))
            findings.extend(_naming_issues(node, file.path))
        elif isinstance(node, ast.ExceptHandler):
            findings.extend(except_issues(node, file.path))
        elif isinstance(node, ast.Compare) and compares_none(node):
            findings.append(
                issue(
                    node,
                    file.path,
                    "none_comparison",
                    "low",
                    "Use `is None`/`is not None` instead of `== None`.",
                )
            )
        elif isinstance(node, ast.Global):
            findings.append(
                issue(
                    node,
                    file.path,
                    "global",
                    "medium",
                    "A `global` statement makes the solution's state hard to follow.",
                )
            )
        elif isinstance(node, ast.Call):
            constructs.update(call_constructs(node))
            name = call_name(node)
            if name in {"eval", "exec"}:
                findings.append(
                    issue(
                        node,
                        file.path,
                        "eval",
                        "high",
                        f"`{name}` executes arbitrary input; avoid it in a solution.",
                    )
                )
            elif name == "print":
                findings.append(
                    issue(
                        node,
                        file.path,
                        "print",
                        "low",
                        "A `print` call looks like debug output left in the submission.",
                    )
                )
        elif isinstance(node, ast.Dict):
            constructs.add("hash_map")
        elif isinstance(node, ast.Name):
            if isinstance(node.ctx, ast.Store) and node.id in {"visited", "seen"}:
                constructs.add("visited")
            if node.id == "dp":
                constructs.add("dp_array")
        elif isinstance(node, ast.Set):
            constructs.add("set")
        elif isinstance(node, ast.ListComp | ast.SetComp | ast.DictComp | ast.GeneratorExp):
            constructs.add("comprehension")
            if isinstance(node, ast.ListComp) and is_dp_row(node.elt):
                constructs.add("dp_table")
        elif isinstance(node, ast.BinOp) and isinstance(
            node.op, ast.BitAnd | ast.BitOr | ast.BitXor | ast.LShift | ast.RShift
        ):
            constructs.add("bit_ops")
        elif isinstance(node, ast.ClassDef):
            constructs.add("class")
        elif isinstance(node, ast.Try):
            constructs.add("try")
        elif isinstance(node, ast.If) and is_guard(node.test):
            guards = True
        if isinstance(node, ast.For | ast.AsyncFor) and range_len(node):
            findings.append(
                issue(
                    node,
                    file.path,
                    "range_len",
                    "low",
                    "`for i in range(len(...))` can usually be `enumerate` or direct iteration.",
                )
            )

    constructs.update(_import_constructs(imports))
    if max_loop_depth(tree) > 1:
        constructs.add("nested_loop")
    if has_two_pointer(tree):
        constructs.add("two_pointer")
    if has_binary_search_loop(tree):
        constructs.add("binary_search_loop")

    return FileFacts(
        path=file.path,
        lines=lines,
        syntax_error=None,
        functions=tuple(functions),
        imports=frozenset(imports),
        constructs=frozenset(constructs),
        issues=tuple(findings),
        guards=guards,
        type_hints=type_hint_ratio(tuple(functions)),
        max_nesting=max_nesting(tree),
    )


def _default_issues(node: ast.FunctionDef | ast.AsyncFunctionDef, path: str) -> list[Issue]:
    mutable = [
        default
        for default in node.args.defaults
        if isinstance(default, ast.List | ast.Dict | ast.Set | ast.Call)
    ]
    if not mutable:
        return []
    return [
        issue(
            node,
            path,
            "mutable_default",
            "high",
            f"`{node.name}` has a mutable default argument; it is shared between calls.",
        )
    ]


def _shape_issues(
    node: ast.FunctionDef | ast.AsyncFunctionDef, facts: FunctionFacts, path: str
) -> list[Issue]:
    shape: list[Issue] = []
    if facts.length > _LONG_FUNCTION:
        shape.append(
            issue(
                node,
                path,
                "long_function",
                "low",
                f"`{facts.name}` is {facts.length} lines; split the setup/loop/cleanup "
                "if it has natural seams.",
            )
        )
    if facts.max_nesting > _DEEP_NESTING:
        shape.append(
            issue(
                node,
                path,
                "deep_nesting",
                "medium",
                f"`{facts.name}` nests {facts.max_nesting} levels deep; flatten it with "
                "early returns or a helper.",
            )
        )
    return shape


def _naming_issues(node: ast.FunctionDef | ast.AsyncFunctionDef, path: str) -> list[Issue]:
    arguments = (
        *node.args.posonlyargs,
        *node.args.args,
        *node.args.kwonlyargs,
        node.args.vararg,
        node.args.kwarg,
    )
    names = [node.name, *(argument.arg for argument in arguments if argument is not None)]
    bad = [name for name in names if name not in {"self", "cls"} and _not_snake_case(name)]
    if not bad:
        return []
    return [
        issue(
            node,
            path,
            "naming",
            "low",
            f"`{bad[0]}` is not snake_case; prefer a descriptive snake_case name.",
        )
    ]


def _not_snake_case(name: str) -> bool:
    if name.startswith("__") and name.endswith("__"):
        return False
    return name != name.lower()


def _import_constructs(imports: set[str]) -> set[str]:
    constructs: set[str] = set()
    if any(name.startswith("heapq") for name in imports):
        constructs.add("heap")
    if any(name.startswith("bisect") for name in imports):
        constructs.add("bisect")
    if any(name.endswith((".deque", ".defaultdict", ".Counter")) for name in imports):
        constructs.update({"deque", "hash_map"})
    return constructs
