"""Function shape and loop-shape detection, all from the AST."""

import ast

from reviewer.analysis.model import FunctionFacts


def function_facts(node: ast.FunctionDef | ast.AsyncFunctionDef) -> FunctionFacts:
    end = node.end_lineno or node.lineno
    branches = sum(
        1
        for child in ast.walk(node)
        if isinstance(child, ast.If | ast.For | ast.AsyncFor | ast.While | ast.ExceptHandler)
    )
    return FunctionFacts(
        name=node.name,
        line=node.lineno,
        length=end - node.lineno + 1,
        branches=branches,
        max_nesting=max_nesting(node),
        annotated=is_annotated(node),
        recursive=is_recursive(node),
    )


def is_annotated(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    arguments = (
        *node.args.posonlyargs,
        *node.args.args,
        *node.args.kwonlyargs,
        node.args.vararg,
        node.args.kwarg,
    )
    required = (
        argument
        for argument in arguments
        if argument is not None and argument.arg not in {"self", "cls"}
    )
    return node.returns is not None and all(
        argument.annotation is not None for argument in required
    )


def is_recursive(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    return any(
        isinstance(child, ast.Call)
        and isinstance(child.func, ast.Name)
        and child.func.id == node.name
        for child in ast.walk(node)
    )


def has_two_pointer(tree: ast.AST) -> bool:
    """A while loop that advances at least two index variables is pointer-like."""
    for node in ast.walk(tree):
        if not isinstance(node, ast.While):
            continue
        names = {child.id for child in ast.walk(node.test) if isinstance(child, ast.Name)}
        changed = {
            child.target.id
            for child in ast.walk(node)
            if isinstance(child, ast.AugAssign) and isinstance(child.target, ast.Name)
        }
        changed.update(
            child.targets[0].id
            for child in ast.walk(node)
            if isinstance(child, ast.Assign)
            and len(child.targets) == 1
            and isinstance(child.targets[0], ast.Name)
        )
        if len(names & changed) >= 2 or (len(changed) >= 2 and bool(names & changed)):
            return True
    return False


def has_binary_search_loop(tree: ast.AST) -> bool:
    """A while loop that computes a midpoint and moves a bound is a halving loop."""
    for node in ast.walk(tree):
        if isinstance(node, ast.While):
            names = {child.id for child in ast.walk(node) if isinstance(child, ast.Name)}
            if "mid" in names and names & {"low", "high", "left", "right"}:
                return True
    return False


def max_nesting(tree: ast.AST) -> int:
    return _Nesting().measure(tree)


def max_loop_depth(tree: ast.AST) -> int:
    return _LoopDepth().measure(tree)


class _Nesting(ast.NodeVisitor):
    """Maximum nesting of loops/ifs/try blocks."""

    def __init__(self) -> None:
        self.depth = 0
        self.maximum = 0

    def measure(self, node: ast.AST) -> int:
        self.visit(node)
        return self.maximum

    def _enter(self, node: ast.AST) -> None:
        self.depth += 1
        self.maximum = max(self.maximum, self.depth)
        self.generic_visit(node)
        self.depth -= 1

    def visit_For(self, node: ast.For) -> None:
        self._enter(node)

    def visit_AsyncFor(self, node: ast.AsyncFor) -> None:
        self._enter(node)

    def visit_While(self, node: ast.While) -> None:
        self._enter(node)

    def visit_If(self, node: ast.If) -> None:
        self._enter(node)

    def visit_Try(self, node: ast.Try) -> None:
        self._enter(node)


class _LoopDepth(ast.NodeVisitor):
    """Maximum nesting of loops only, which is what `nested_loop` means."""

    def __init__(self) -> None:
        self.depth = 0
        self.maximum = 0

    def measure(self, node: ast.AST) -> int:
        self.visit(node)
        return self.maximum

    def _enter(self, node: ast.AST) -> None:
        self.depth += 1
        self.maximum = max(self.maximum, self.depth)
        self.generic_visit(node)
        self.depth -= 1

    def visit_For(self, node: ast.For) -> None:
        self._enter(node)

    def visit_AsyncFor(self, node: ast.AsyncFor) -> None:
        self._enter(node)

    def visit_While(self, node: ast.While) -> None:
        self._enter(node)
