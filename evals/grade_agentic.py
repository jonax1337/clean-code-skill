"""Grade the agentic runs with each case's deterministic checks.

Usage: python evals/grade_agentic.py [--model sonnet] [--case ID]
Grading is deterministic and costs nothing, so every stored run is regraded each time. Each grade rebuilds the
workspace from the fixture plus the run's diff, adds the hidden tests and writes
results/agentic/<model>/checks/<case>/<condition>-r<n>.json.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from agentic import AgenticCase, Transcript, coder_models, load_agentic_cases, results_dir, workspace_for
from harness import write_text_atomic


def main() -> None:
    parser = argparse.ArgumentParser(description="Grade the stored agentic runs.")
    parser.add_argument("--model", help="grade only the runs of this coder model (default: all)")
    parser.add_argument("--case", help="grade only this case id")
    args = parser.parse_args()
    for model in [args.model] if args.model else coder_models():
        for case in load_agentic_cases():
            if args.case not in (None, case.case_id):
                continue
            for run_dir in sorted((results_dir(model, "runs") / case.case_id).glob("*-r*")):
                if not (run_dir / "meta.json").exists():
                    continue
                try:
                    _grade(model, case, run_dir)
                except (RuntimeError, OSError, ValueError, SyntaxError) as error:
                    print(f"FAILED {model} {case.case_id} {run_dir.name}: {error}")


def _grade(model: str, case: AgenticCase, run_dir: Path) -> None:
    transcript = Transcript.from_jsonl((run_dir / "transcript.jsonl").read_text(encoding="utf-8"))
    with workspace_for(case) as workspace:
        workspace.apply((run_dir / "diff.patch").read_bytes().decode("utf-8"))
        workspace.add_hidden_tests()
        checks = case.checks_module().checks(workspace, transcript)
    condition, rep = run_dir.name.rsplit("-r", 1)
    grade = {
        "case": case.case_id,
        "split": case.split,
        "condition": condition,
        "rep": int(rep),
        "checks": [asdict(check) for check in checks],
    }
    write_text_atomic(
        results_dir(model, "checks") / case.case_id / f"{run_dir.name}.json", json.dumps(grade, indent=2)
    )
    failed = [check.name for check in checks if not check.passed]
    print(
        f"{model} {case.case_id} {run_dir.name}: {len(checks) - len(failed)}/{len(checks)}; failed: {failed or '-'}"
    )


if __name__ == "__main__":
    main()
