"""Per-case verdict semantics, one test per comparison mode."""

from __future__ import annotations

from neetcode_dojo.judge.compare import (
    approx_equal,
    canonical,
    case_verdict,
    check_equal,
    rounded,
)


def test_strict_equality_is_json_equality() -> None:
    assert check_equal([1, 2], [1, 2], "strict")
    assert not check_equal([1, 2], [2, 1], "strict")
    assert not check_equal(1.0, 1, "strict")  # "approximately right" must be asked for
    assert check_equal({"b": 1, "a": 2}, {"a": 2, "b": 1}, "strict")


def test_sorted_deep_sorts_both_sides() -> None:
    assert check_equal([[2], [1]], [[1], [2]], "sorted")
    assert check_equal([{"b": 1, "a": 2}], [{"a": 2, "b": 1}], "sorted")
    assert canonical([3, 1, 2]) == [1, 2, 3]


def test_rounded_rounds_floats_recursively() -> None:
    assert check_equal([1.234], [1.23], "rounded:2")
    assert not check_equal([1.234], [1.23], "strict")
    assert rounded({"a": 1.2345}, 2) == {"a": 1.23}


def test_approx_uses_a_tolerance() -> None:
    assert check_equal(1.0000001, 1.0, "approx:1e-5")
    assert not check_equal(1.1, 1.0, "approx:1e-5")
    assert approx_equal([1.0, 2.0], [1.000001, 2.0], 1e-4)
    assert not approx_equal(1, 2, 1e-4)


def test_unknown_modes_are_strict() -> None:
    """An unrecognized comparator must not become a free pass."""
    assert check_equal(1, 1, "mystery")
    assert not check_equal(1, 2, "mystery")


def test_mutates_compares_the_arguments_after_the_call() -> None:
    matrix = [[1, 2], [3, 4]]
    expected = [[3, 1], [4, 2]]
    case = {"args": [matrix], "expected": expected, "compare": "mutates"}
    matrix[:] = expected
    assert case_verdict(case, None, matrix)
    assert not case_verdict({**case, "expected": [[1, 2], [3, 4]]}, None, matrix)
