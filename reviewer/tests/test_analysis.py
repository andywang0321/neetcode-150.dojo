"""The static analysis is pure, exhaustive and excludes the visible harness."""

from reviewer.analysis import Analysis, analyze
from reviewer.contracts import SubmissionFile
from reviewer.tests.support import BINARY_SOLUTION, HASH_SOLUTION, MESSY_SOLUTION


def _facts(*files: tuple[str, str]) -> Analysis:
    return analyze([SubmissionFile(path=path, content=content) for path, content in files])


def test_hash_solution_detects_hash_map_and_annotations() -> None:
    analysis = _facts(("solution.py", HASH_SOLUTION))

    assert analysis.paths == ("solution.py",)
    assert "hash_map" in analysis.constructs
    assert "list_ops" not in analysis.constructs
    assert analysis.type_hints == 1.0
    assert analysis.guards is False
    assert analysis.syntax_errors == ()


def test_messy_solution_detects_nested_loops_range_len_and_print() -> None:
    analysis = _facts(("solution.py", MESSY_SOLUTION))

    assert "nested_loop" in analysis.constructs
    codes = {issue.code for issue in analysis.issues}
    assert "range_len" in codes
    assert "print" in codes
    assert analysis.guards is False
    assert analysis.max_nesting >= 3


def test_binary_search_detects_the_halving_loop() -> None:
    analysis = _facts(("solution.py", BINARY_SOLUTION))

    assert "binary_search_loop" in analysis.constructs
    function = analysis.functions[0]
    assert function.annotated is True
    assert function.branches >= 2


def test_guard_and_two_pointer_are_detected() -> None:
    code = """\
def is_palindrome(text: str) -> bool:
    if not text:
        return True
    left, right = 0, len(text) - 1
    while left < right:
        if text[left] != text[right]:
            return False
        left += 1
        right -= 1
    return True
"""
    analysis = _facts(("solution.py", code))

    assert analysis.guards is True
    assert "two_pointer" in analysis.constructs


def test_check_py_is_scaffolding_and_is_not_reviewed() -> None:
    analysis = _facts(("check.py", "def broken(:\n"), ("solution.py", HASH_SOLUTION))

    assert analysis.paths == ("solution.py",)
    assert analysis.syntax_errors == ()


def test_every_python_file_is_reviewed_except_the_harness() -> None:
    analysis = _facts(
        ("solution.py", HASH_SOLUTION),
        ("helpers.py", "def helper(value):\n    return value\n"),
        ("check.py", "raise SystemExit\n"),
    )

    assert analysis.paths == ("solution.py", "helpers.py")
    assert len(analysis.functions) == 2


def test_syntax_error_is_a_high_finding_not_an_exception() -> None:
    analysis = _facts(("solution.py", "def solve(:\n    return 1\n"))

    assert len(analysis.syntax_errors) == 1
    issue = analysis.syntax_errors[0]
    assert issue.severity == "high"
    assert issue.path == "solution.py"
    assert "syntax error" in issue.message


def test_common_python_hazards_become_specific_findings() -> None:
    code = """\
def walk(items, cache={}):
    try:
        return cache[items]
    except:
        return None


def check(value):
    if value == None:
        return False
    return eval(value)
"""
    analysis = _facts(("solution.py", code))
    codes = {issue.code for issue in analysis.issues}

    assert {"mutable_default", "bare_except", "none_comparison", "eval"} <= codes


def test_long_functions_deep_nesting_and_names_are_flagged() -> None:
    long_body = "".join(f"    value_{index} = {index}\n" for index in range(22))
    code = (
        "def findThing(nums):\n"
        f"{long_body}"
        "    if nums:\n"
        "        for value in nums:\n"
        "            if value:\n"
        "                for other in nums:\n"
        "                    if other:\n"
        "                        return value\n"
        "    return None\n"
    )
    analysis = _facts(("solution.py", code))
    codes = {issue.code for issue in analysis.issues}

    assert {"long_function", "deep_nesting", "naming"} <= codes


def test_heap_visited_memo_and_dp_constructs_are_recognized() -> None:
    code = """\
import heapq
from collections import deque


def traverse(graph, start, target):
    visited = set()
    seen = set()
    queue = deque([start])
    memo = {}
    dp = [0] * 10
    heapq.heappush(heap, start)
    visited.add(start)
    seen.add(start)
    while queue:
        node = queue.popleft()
        memo[node] = 1
    return dp, target
"""
    analysis = _facts(("solution.py", code))

    assert {"heap", "deque", "visited", "memo", "dp_array"} <= analysis.constructs


def test_no_python_files_yields_empty_analysis() -> None:
    analysis = _facts(("notes.txt", "not python"))

    assert analysis.files == ()
    assert analysis.issues == ()
    assert analysis.functions == ()
    assert analysis.type_hints == 0.0


def test_a_harness_only_submission_has_no_student_code() -> None:
    analysis = _facts(("check.py", "raise SystemExit\n"))

    assert analysis.files == ()
    assert analysis.paths == ()
