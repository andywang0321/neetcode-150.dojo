"""Pure static analysis of the submitted files.

The package exposes the value types and one function. `facts` is the only module that
touches a submission; `rules` and `shape` are AST helpers with no I/O.
"""

from reviewer.analysis.facts import analyze
from reviewer.analysis.model import Analysis, FileFacts, FunctionFacts, Issue, Severity

__all__ = ["Analysis", "FileFacts", "FunctionFacts", "Issue", "Severity", "analyze"]
