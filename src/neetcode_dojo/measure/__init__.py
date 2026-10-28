"""The scale probe: measure a solution against a reference at increasing size.

``probe`` runs both implementations at a ladder of sizes in isolated subprocesses
and reports, per size, the wall time, peak memory, the result digest, and any
exception or timeout. ``growth`` turns the paired ratios into a verdict.

There is deliberately no absolute complexity fitting here: fitting a single curve
to wall-clock samples cannot separate O(n) from O(n log n) over a feasible ladder,
and the honest output of trying was a bracket nobody could use. Measuring the
student *against a reference implementation* cancels every constant factor the two
share, which is what makes a verdict possible.
"""

from neetcode_dojo.measure.growth import (
    BETTER,
    FAILED,
    MATCHES,
    UNREFERENCED,
    UNRESOLVED,
    WORSE,
    Verdict,
    verdict,
)
from neetcode_dojo.measure.probe import (
    DEFAULT_MAX_N,
    DEFAULT_REPEATS,
    DEFAULT_TIMEOUT,
    LADDER_POINTS,
    Probe,
    Run,
    ScalePoint,
    Target,
    ladder,
    locate_mismatch,
    run_one,
    run_probe,
)

__all__ = [
    "BETTER",
    "DEFAULT_MAX_N",
    "DEFAULT_REPEATS",
    "DEFAULT_TIMEOUT",
    "FAILED",
    "LADDER_POINTS",
    "MATCHES",
    "UNREFERENCED",
    "UNRESOLVED",
    "WORSE",
    "Probe",
    "Run",
    "ScalePoint",
    "Target",
    "Verdict",
    "ladder",
    "locate_mismatch",
    "run_one",
    "run_probe",
    "verdict",
]
