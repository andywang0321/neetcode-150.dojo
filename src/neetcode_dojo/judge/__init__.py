"""The judge: correctness evaluation against a curriculum's test cases.

Design: student code is executed in a subprocess with a JSON protocol — import the
submitted file, call the item's entry point, compare results by JSON equality (or
a per-case comparator: sorted / rounded / approx / mutates / predicate / ops). The
subprocess isolates hangs (timeout) and crashes from the server.

The content side — generated cases, oracles, references and measurement plans —
lives in the curriculum's private `assessment/` tree and is reached only through
the assessment loader, never imported here.
"""

from neetcode_dojo.judge.runner import CaseResult, Checker, JudgeReport, run_cases, run_cases_in

__all__ = [
    "CaseResult",
    "Checker",
    "JudgeReport",
    "run_cases",
    "run_cases_in",
]
