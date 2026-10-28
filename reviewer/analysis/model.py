"""The value types the static analysis produces."""

from dataclasses import dataclass
from typing import Literal

type Severity = Literal["high", "medium", "low"]

_SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2}


@dataclass(frozen=True, slots=True)
class Issue:
    """One concrete code finding, with enough location for the review to cite it."""

    code: str
    path: str
    line: int
    severity: Severity
    message: str


@dataclass(frozen=True, slots=True)
class FunctionFacts:
    """Shape of one function; no semantic judgement is made here."""

    name: str
    line: int
    length: int
    branches: int
    max_nesting: int
    annotated: bool
    recursive: bool


@dataclass(frozen=True, slots=True)
class FileFacts:
    """Facts about one submitted file."""

    path: str
    lines: int
    syntax_error: str | None
    functions: tuple[FunctionFacts, ...]
    imports: frozenset[str]
    constructs: frozenset[str]
    issues: tuple[Issue, ...]
    guards: bool
    type_hints: float
    max_nesting: int


@dataclass(frozen=True, slots=True)
class Analysis:
    """The facts for all reviewable submitted files."""

    files: tuple[FileFacts, ...]

    @property
    def functions(self) -> tuple[FunctionFacts, ...]:
        return tuple(function for file in self.files for function in file.functions)

    @property
    def constructs(self) -> frozenset[str]:
        combined: frozenset[str] = frozenset()
        for file in self.files:
            combined = combined | file.constructs
        return combined

    @property
    def issues(self) -> tuple[Issue, ...]:
        """Deduplicated findings, worst first, at most two of each kind."""
        ordered = sorted(
            (issue for file in self.files for issue in file.issues),
            key=lambda issue: (_SEVERITY_ORDER[issue.severity], issue.path, issue.line),
        )
        seen: dict[str, int] = {}
        kept: list[Issue] = []
        for issue in ordered:
            if seen.get(issue.code, 0) >= 2:
                continue
            seen[issue.code] = seen.get(issue.code, 0) + 1
            kept.append(issue)
        return tuple(kept)

    @property
    def syntax_errors(self) -> tuple[Issue, ...]:
        return tuple(issue for issue in self.issues if issue.code == "syntax")

    @property
    def guards(self) -> bool:
        return any(file.guards for file in self.files)

    @property
    def type_hints(self) -> float:
        functions = self.functions
        if not functions:
            return 0.0
        return sum(1 for function in functions if function.annotated) / len(functions)

    @property
    def max_nesting(self) -> int:
        return max((file.max_nesting for file in self.files), default=0)

    @property
    def paths(self) -> tuple[str, ...]:
        return tuple(file.path for file in self.files)
