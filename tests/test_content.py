"""Every item has the three student-visible pieces, and each one is well formed.

The manifest says where the statement, workspace and check are; this test opens every
one of them. It also enforces the boundary that makes the workspace safe to hand over:
the starter is a stub, never a solution, and the visible check imports the new
`workspace/solution.py` rather than the old item-named artifact.
"""

from __future__ import annotations

import ast

import pytest

from tests.conftest import ROOT


def _items(manifest: dict) -> list[dict]:
    return manifest["item"]


def _top_level(tree: ast.Module) -> list[ast.FunctionDef | ast.ClassDef]:
    return [node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.ClassDef))]


def _raises_not_implemented(node: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    for statement in ast.walk(node):
        if not isinstance(statement, ast.Raise):
            continue
        exc = statement.exc
        if isinstance(exc, ast.Name) and exc.id == "NotImplementedError":
            return True
        if (
            isinstance(exc, ast.Call)
            and isinstance(exc.func, ast.Name)
            and exc.func.id == "NotImplementedError"
        ):
            return True
    return False


def test_every_statement_is_prose_without_the_manifest_title(manifest: dict) -> None:
    for item in _items(manifest):
        path = ROOT / item["statement"]
        assert path.is_file(), item["id"]
        text = path.read_text(encoding="utf-8")
        assert text.strip(), f"{item['id']}: empty statement"
        first = text.splitlines()[0]
        assert first != f"{item['title']} [{item['difficulty']}]", (
            f"{item['id']}: the title/difficulty line belongs in the manifest, not the prose"
        )
        assert not first.endswith((" [Easy]", " [Medium]", " [Hard]")), (
            f"{item['id']}: statement starts with a bracketed difficulty heading"
        )
        assert text.endswith("\n")
        for marker in ("@oracle", "@reference", "@cases", "neetcode_dojo.assessment"):
            assert marker not in text, f"{item['id']}: private marker in statement"


def test_every_workspace_has_a_stub_solution_and_a_visible_check(manifest: dict) -> None:
    for item in _items(manifest):
        workspace = ROOT / item["workspace"]
        solution_path = workspace / "solution.py"
        check_path = workspace / "check.py"
        assert solution_path.is_file(), f"{item['id']}: no workspace/solution.py"
        assert check_path.is_file(), f"{item['id']}: no workspace/check.py"

        solution_source = solution_path.read_text(encoding="utf-8")
        tree = ast.parse(solution_source, str(solution_path))
        definitions = _top_level(tree)
        assert definitions, f"{item['id']}: solution has no top-level def/class"
        for node in definitions:
            if isinstance(node, ast.FunctionDef):
                assert _raises_not_implemented(node), f"{item['id']}: {node.name} is not a stub"
            elif isinstance(node, ast.ClassDef):
                methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                assert methods, f"{item['id']}: class {node.name} has no methods"
                for method in methods:
                    assert _raises_not_implemented(method), (
                        f"{item['id']}: {node.name}.{method.name} is not a stub"
                    )

        assert "# --- dojo: visible examples" in solution_source, (
            f"{item['id']}: the old examples block was not preserved"
        )
        assert solution_source.rstrip().endswith("# --- end dojo ---"), item["id"]

        check_source = check_path.read_text(encoding="utf-8")
        check_tree = ast.parse(check_source, str(check_path))
        cases = _literal_cases(check_tree)
        assert cases, f"{item['id']}: check.py has no literal CASES"
        assert any(
            isinstance(node, ast.FunctionDef) and node.name == "check" for node in check_tree.body
        ), f"{item['id']}: check.py has no check()"
        assert "solution" in check_source, f"{item['id']}: check does not target solution.py"
        assert f'"{item["id"]}.py"' not in check_source, (
            f"{item['id']}: check still loads the old item-named artifact"
        )
        assert f"from {item['id']} import" not in check_source, (
            f"{item['id']}: check still imports the old item module"
        )


def _literal_cases(tree: ast.Module) -> list[dict]:
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(
            isinstance(target, ast.Name) and target.id == "CASES" for target in node.targets
        ):
            continue
        value = ast.literal_eval(node.value)
        assert isinstance(value, list), "CASES must be a literal list"
        return value
    return []


def test_every_visible_case_is_decidable(manifest: dict) -> None:
    for item in _items(manifest):
        check_path = ROOT / item["workspace"] / "check.py"
        cases = _literal_cases(ast.parse(check_path.read_text(encoding="utf-8")))
        for number, case in enumerate(cases, 1):
            assert isinstance(case, dict), f"{item['id']}: case {number} is not a table"
            assert "args" in case or "ops" in case, (
                f"{item['id']}: case {number} has neither args nor ops"
            )
            assert "expected" in case, f"{item['id']}: case {number} has no expected"


def test_statement_workspace_and_check_counts(manifest: dict) -> None:
    items = _items(manifest)
    statements = list((ROOT / "content").glob("*/statement.md"))
    solutions = list((ROOT / "content").glob("*/workspace/solution.py"))
    checks = list((ROOT / "content").glob("*/workspace/check.py"))
    assert len(statements) == len(solutions) == len(checks) == len(items) == 157
    assert not list((ROOT / "content").glob("*/assessment*"))


def test_the_workspace_never_ships_the_private_tree(manifest: dict) -> None:
    for item in _items(manifest):
        workspace = ROOT / item["workspace"]
        for path in workspace.rglob("*"):
            assert "assessment" not in path.parts, f"{item['id']}: {path}"
            assert "__pycache__" not in path.parts, f"{item['id']}: {path}"
        for path in workspace.iterdir():
            assert path.is_file(), f"{item['id']}: unexpected directory {path.name}"


@pytest.mark.parametrize(
    "item_id", ["two_sum", "add-two-numbers", "min_stack", "encode_and_decode_strings"]
)
def test_specific_workspace_adaptations(manifest: dict, item_id: str) -> None:
    item = next(item for item in _items(manifest) if item["id"] == item_id)
    check = (ROOT / item["workspace"] / "check.py").read_text(encoding="utf-8")
    if "-" in item_id:
        assert 'with_name("solution.py")' in check
    else:
        assert "from solution import" in check


def test_mutating_visible_checks_compare_the_post_call_arguments() -> None:
    """In-place items: the effect on the argument is the result, not the None return.

    The old visible checks for these five items compared the return value and
    therefore failed every correct in-place solution. The judge already used the
    post-call arguments; the student's check has to use the same contract.
    """
    for item_id in (
        "reorder-list",
        "rotate-image",
        "set-matrix-zeroes",
        "surrounded-regions",
        "walls-and-gates",
    ):
        source = (ROOT / "content" / item_id / "workspace" / "check.py").read_text(encoding="utf-8")
        assert 'case.get("compare") == "mutates"' in source, item_id
        assert 'compared = case["args"]' in source, item_id
