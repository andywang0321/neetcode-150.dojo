"""Test fixture assessment with an oracle but no case generator."""

from neetcode_dojo.registry import oracle


@oracle("no_cases")
def _oracle(value: int) -> int:
    return value + 1
