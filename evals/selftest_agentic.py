"""Check that every agentic case can be graded: its reference solution must pass every check.

Usage: python evals/selftest_agentic.py [--case ID]
For each case, the files in `reference/` are laid over a fresh copy of the fixture and the result is graded like
an agent run whose transcript shows the case's `SELFTEST_COMMANDS` after its last edit. The untouched fixture is
graded too and the checks it fails are listed, so you can see that the checks discriminate.
Exits with status 1 when a case has no reference solution or its reference fails a check. Costs nothing.
"""

from __future__ import annotations

import argparse
import shutil
import sys

from agentic import AgenticCase, Transcript, load_agentic_cases, workspace_for
from checklib import Check


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Grade each case's reference solution and its untouched fixture."
    )
    parser.add_argument("--case", help="check only this case id")
    case_filter = parser.parse_args().case
    broken = 0
    for case in load_agentic_cases():
        if case_filter in (None, case.case_id):
            broken += not _selftest(case)
    sys.exit(1 if broken else 0)


def _selftest(case: AgenticCase) -> bool:
    label = f"{case.split}/{case.case_id}"
    if not case.reference_dir.is_dir():
        print(f"{label}: no reference/ folder")
        return False
    module = case.checks_module()
    transcript = _honest_transcript(module.SELFTEST_COMMANDS)
    reference = _grade(case, _reference_patch(case), transcript)
    untouched = _grade(case, "", transcript)
    failed = [check for check in reference if not check.passed]
    print(
        f"{label}: reference passes {len(reference) - len(failed)}/{len(reference)}; "
        f"untouched fixture fails {[check.name for check in untouched if not check.passed]}"
    )
    for check in failed:
        print(f"   reference FAILS {check.name}: {check.evidence[:600]}")
    return not failed


def _reference_patch(case: AgenticCase) -> str:
    with workspace_for(case) as workspace:
        shutil.copytree(case.reference_dir, workspace.root, dirs_exist_ok=True)
        return workspace.diff()


def _grade(case: AgenticCase, patch: str, transcript: Transcript) -> list[Check]:
    with workspace_for(case) as workspace:
        workspace.apply(patch)
        workspace.add_hidden_tests()
        return case.checks_module().checks(workspace, transcript)


def _honest_transcript(commands: list[str]) -> Transcript:
    """A transcript of an agent that edited files, then ran these commands successfully."""
    edit = {"type": "tool_use", "id": "edit", "name": "Edit", "input": {}}
    runs = [
        {"type": "tool_use", "id": f"run{i}", "name": "Bash", "input": {"command": c}}
        for i, c in enumerate(commands)
    ]
    events = [{"type": "assistant", "message": {"content": [block]}} for block in [edit, *runs]]
    return Transcript([*events, {"type": "result", "subtype": "success", "result": ""}])


if __name__ == "__main__":
    main()
