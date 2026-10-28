"""The curriculum-local registry: the old decorator surface, no engine import."""

from __future__ import annotations

import pytest

from neetcode_dojo import registry


@pytest.fixture(autouse=True)
def _clean() -> None:
    registry.reset()


def test_each_decorator_registers_under_the_item_id_and_returns_the_function() -> None:
    @registry.oracle("item")
    def oracle(value: int) -> int:
        return value

    @registry.cases("item")
    def cases(n: int, rng: object) -> tuple[list, int]:
        return [[n]], n

    @registry.inputs("item")
    def inputs(n: int, rng: object) -> list:
        return [n]

    @registry.reference("item")
    def reference(value: int) -> int:
        return value

    @registry.measure("item")
    def measure(ctx: dict) -> dict:
        return {"axis": "n"}

    @registry.checker("positive")
    def checker(module: object, got: object, args: object) -> bool:
        return True

    assert registry.ORACLES["item"] is oracle
    assert registry.CASES["item"] is cases
    assert registry.INPUTS["item"] is inputs
    assert registry.REFERENCES["item"] is reference
    assert registry.MEASURES["item"] is measure
    assert registry.CHECKERS["positive"] is checker


def test_rubric_is_still_part_of_the_surface() -> None:
    @registry.rubric("item")
    def rubric() -> dict:
        return {"dimensions": ["correctness"]}

    assert registry.RUBRICS["item"] is rubric


def test_registrations_are_sorted_by_kind_and_include_every_store() -> None:
    registry.oracle("beta")(lambda: None)
    registry.oracle("alpha")(lambda: None)
    registered = registry.registrations()
    assert set(registered) == set(registry.STORES)
    assert registered["oracle"] == ["alpha", "beta"]
    assert registered["cases"] == []


def test_an_empty_or_non_string_name_is_refused() -> None:
    with pytest.raises(ValueError):
        registry.cases("")
    with pytest.raises(ValueError):
        registry.oracle(42)  # ty: ignore[invalid-argument-type]


def test_reset_forgets_everything() -> None:
    registry.oracle("item")(lambda: None)
    registry.checker("predicate")(lambda *args: True)
    registry.reset()
    assert registry.registrations() == {kind: [] for kind in registry.STORES}
