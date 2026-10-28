"""Shared review.v1 fixtures for the reviewer's tests."""

from collections.abc import Mapping, Sequence

from reviewer.contracts import OutcomeName, ReviewEvidence, ReviewRequest, SubmissionFile

TWO_SUM_STATEMENT = (
    "Given an array of integers nums and an integer target, return the indices of the "
    "two numbers that add up to target. Each input has exactly one solution."
)

HASH_SOLUTION = """\
def two_sum(nums: list[int], target: int) -> list[int]:
    seen: dict[int, int] = {}
    for index, value in enumerate(nums):
        complement = target - value
        if complement in seen:
            return [seen[complement], index]
        seen[value] = index
    return []
"""

MESSY_SOLUTION = """\
def two_sum(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                print(i, j)
                return [i, j]
"""

BINARY_SOLUTION = """\
def search(nums: list[int], target: int) -> int:
    low, high = 0, len(nums) - 1
    while low <= high:
        mid = (low + high) // 2
        if nums[mid] == target:
            return mid
        if nums[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1
"""


def evidence(
    evaluator: str = "tests",
    outcome: OutcomeName = "pass",
    summary: str = "5/5 cases passed",
    assurance: str = "machine",
) -> ReviewEvidence:
    """Build one evaluator report."""
    return ReviewEvidence(
        evaluator=evaluator,
        assurance=assurance,
        outcome=outcome,
        summary=summary,
    )


def make_request(
    *,
    item: str = "two-sum",
    statement: str = TWO_SUM_STATEMENT,
    files: Sequence[SubmissionFile] | None = None,
    evidence_items: Sequence[ReviewEvidence] | None = None,
    grade: int | None = 3,
    claims: Mapping[str, str] | None = None,
) -> ReviewRequest:
    """Build the review request, varied by the caller."""
    submitted = (
        (SubmissionFile(path="solution.py", content=HASH_SOLUTION),)
        if files is None
        else tuple(files)
    )
    reports = (evidence(),) if evidence_items is None else tuple(evidence_items)
    return ReviewRequest(
        curriculum="neetcode-150",
        item=item,
        statement=statement,
        files=submitted,
        evidence=reports,
        grade=grade,
        claims={"time": "O(n)", "space": "O(n)"} if claims is None else dict(claims),
    )
