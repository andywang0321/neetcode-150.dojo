"""Node-level rules: the cheap checks that turn AST shapes into findings."""

import ast

from reviewer.analysis.model import FunctionFacts, Issue, Severity


def issue(node: ast.AST, path: str, code: str, severity: Severity, message: str) -> Issue:
    """Build a located finding."""
    line = getattr(node, "lineno", 1)
    return Issue(code=code, path=path, line=line, severity=severity, message=message)


def dotted(node: ast.expr) -> str:
    """Render a Name/Attribute chain as dotted text (empty for anything else)."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return f"{dotted(node.value)}.{node.attr}"
    return ""


def call_name(node: ast.Call) -> str:
    return dotted(node.func)


def call_constructs(node: ast.Call) -> set[str]:
    """Map one call to the pattern constructs it evidences."""
    name = call_name(node)
    constructs: set[str] = set()
    if name in {"dict", "defaultdict", "Counter"}:
        constructs.add("hash_map")
    elif name in {"set", "frozenset"}:
        constructs.add("set")
    elif name == "sorted" or name.endswith(".sort"):
        constructs.add("sort")
    elif name in {"deque", "collections.deque"}:
        constructs.add("deque")
    elif name in {
        "heappush",
        "heappop",
        "heapify",
        "nlargest",
        "nsmallest",
        "heapq.heappush",
        "heapq.heappop",
        "heapq.heapify",
        "heapq.nlargest",
        "heapq.nsmallest",
    }:
        constructs.add("heap")
    elif name in {
        "bisect_left",
        "bisect_right",
        "bisect",
        "bisect.bisect_left",
        "bisect.bisect_right",
    }:
        constructs.add("bisect")
    if isinstance(node.func, ast.Attribute):
        if node.func.attr == "sort":
            constructs.add("sort")
        elif node.func.attr in {"append", "pop"}:
            constructs.add("list_ops")
    return constructs


def is_dp_row(node: ast.expr) -> bool:
    """Whether a comprehension element builds a row of a 2-D table."""
    return isinstance(node, ast.ListComp | ast.List) or (
        isinstance(node, ast.BinOp) and isinstance(node.left, ast.List)
    )


def uses_memo(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    """Whether a function caches results explicitly or with a cache decorator."""
    names = {
        child.id
        for child in ast.walk(node)
        if isinstance(child, ast.Name) and child.id in {"memo", "cache"}
    }
    return bool(names) or has_cache_decorator(node)


def has_cache_decorator(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    for decorator in node.decorator_list:
        name = call_name(decorator) if isinstance(decorator, ast.Call) else dotted(decorator)
        if name.endswith(("cache", "lru_cache")):
            return True
    return False


def except_issues(node: ast.ExceptHandler, path: str) -> list[Issue]:
    """Bare and broad exception handlers, with the old rubric's severity."""
    if node.type is None:
        return [
            issue(
                node,
                path,
                "bare_except",
                "high",
                "A bare `except:` swallows every error; catch the specific exception.",
            )
        ]
    name = dotted(node.type)
    if name in {"Exception", "BaseException"}:
        return [
            issue(
                node,
                path,
                "broad_except",
                "medium",
                f"`except {name}` is broad; catch the exception the code can actually raise.",
            )
        ]
    return []


def compares_none(node: ast.Compare) -> bool:
    operands = (node.left, *node.comparators)
    has_none = any(isinstance(item, ast.Constant) and item.value is None for item in operands)
    return has_none and any(isinstance(operator, ast.Eq | ast.NotEq) for operator in node.ops)


def is_guard(test: ast.expr) -> bool:
    """Recognise `if not xs` and `if len(xs) <= 1` style guards."""
    if isinstance(test, ast.UnaryOp) and isinstance(test.op, ast.Not):
        return True
    if isinstance(test, ast.Compare) and isinstance(test.left, ast.Call):
        function = test.left.func
        return (
            isinstance(function, ast.Name)
            and function.id == "len"
            and any(
                isinstance(item, ast.Constant) and isinstance(item.value, int) and item.value <= 1
                for item in test.comparators
            )
        )
    return False


def range_len(node: ast.For | ast.AsyncFor) -> bool:
    return (
        isinstance(node.iter, ast.Call)
        and isinstance(node.iter.func, ast.Name)
        and node.iter.func.id == "range"
        and any(
            isinstance(argument, ast.Call)
            and isinstance(argument.func, ast.Name)
            and argument.func.id == "len"
            for argument in node.iter.args
        )
    )


def type_hint_ratio(functions: tuple[FunctionFacts, ...]) -> float:
    if not functions:
        return 0.0
    return sum(1 for function in functions if function.annotated) / len(functions)
