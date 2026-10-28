"""Run the old engine's judge for the parity tests — a test-only subprocess seam.

This file is deliberately not a pytest module. It is executed by
``tests/test_parity.py`` with the old engine's ``src/`` on ``PYTHONPATH``; the test
process itself never imports ``dojo``. Keeping the old import in a child is what lets
the suite assert agreement without making the curriculum depend on the old engine.
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path


def main() -> None:
    payload = json.loads(sys.stdin.read())
    # Imported dynamically: the old engine is deliberately not on this project's
    # import path, so a static checker must not try to resolve it.
    runner = __import__("dojo.judge.runner", fromlist=["run_cases"])
    run_cases = runner.run_cases

    with tempfile.TemporaryDirectory(prefix="old_judge_parity_") as directory:
        path = Path(directory) / "solution.py"
        path.write_text(payload["code"], encoding="utf-8")
        report = run_cases(
            path,
            payload["function"],
            payload["cases"],
            timeout=payload.get("timeout", 10.0),
        )
    json.dump(
        {
            "status": report.status,
            "passed": report.passed,
            "total": report.total,
            "results": [
                {
                    "label": result.label,
                    "passed": result.passed,
                    "error": result.error,
                    "got": result.got,
                    "expected": result.expected,
                }
                for result in report.results
            ],
        },
        sys.stdout,
    )


if __name__ == "__main__":
    main()
