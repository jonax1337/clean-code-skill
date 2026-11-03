"""Clean-code metrics of the source files a run changed, measured before and after the run with lizard.

The metrics are reported next to the checks and never graded pass or fail: one long function is not wrong by itself.
Across many runs, though, they show whether a skill makes agents leave smaller and simpler functions in the code they
touch. Test files, hidden tests and toolchain folders are not measured.
"""

from __future__ import annotations

import csv
import io
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

from agentic import HIDDEN_TESTS_DIR, Workspace
from checklib import TEST_FILE

LIZARD = ["uvx", "--quiet", "--from", "lizard==1.25.0", "lizard", "--csv"]
SOURCE_SUFFIXES = {".py", ".ts", ".js", ".mjs", ".java", ".rs"}
SKIPPED_DIRS = {HIDDEN_TESTS_DIR, "node_modules", "build", "target", "tools", "lib"}
# Thresholds for the counts below. They follow common linter defaults (for example ruff's C901 and PLR0913 and the
# usual 30-line function guideline); the raw maxima are reported too, so a reader can apply other limits.
LONG_FUNCTION_NLOC = 30
COMPLEX_FUNCTION_CCN = 10
MANY_PARAMETERS = 4


@dataclass(frozen=True)
class FunctionSize:
    path: str
    name: str
    nloc: int
    ccn: int
    parameters: int


def change_metrics(workspace: Workspace) -> dict:
    """Function metrics of the changed source files, before and after the run."""
    paths = [path for path in workspace.changed_files() if _is_measured_source(path)]
    before = {path: workspace.read_base(path) for path in paths}
    after = {path: workspace.read(path) for path in paths}
    sizes = _measure({"before": before, "after": after})
    return {
        "files": paths,
        "before": _summary(sizes.get("before", [])),
        "after": _summary(sizes.get("after", [])),
    }


def _is_measured_source(path: str) -> bool:
    parts = Path(path).parts
    return (
        Path(path).suffix in SOURCE_SUFFIXES
        and not TEST_FILE.search(path)
        and not any(part in SKIPPED_DIRS for part in parts)
    )


def _measure(trees: dict[str, dict[str, str | None]]) -> dict[str, list[FunctionSize]]:
    """Run lizard once over every tree and group the functions it finds by tree."""
    with tempfile.TemporaryDirectory(prefix="metrics-") as temp:
        root = Path(temp)
        for tree, files in trees.items():
            for path, text in files.items():
                if text is not None:
                    target = root / tree / path
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_text(text, encoding="utf-8")
        if not any(root.iterdir()):
            return {}
        completed = subprocess.run(
            [*LIZARD, str(root)], capture_output=True, text=True, encoding="utf-8", timeout=300, check=False
        )
        if completed.returncode != 0:
            raise RuntimeError(f"lizard failed: {completed.stderr.strip()[-500:]}")
        return _parse(completed.stdout, root)


def _parse(output: str, root: Path) -> dict[str, list[FunctionSize]]:
    by_tree: dict[str, list[FunctionSize]] = {}
    for row in csv.reader(io.StringIO(output)):
        if len(row) < 11 or not row[0].isdigit():
            continue
        nloc, ccn, _tokens, parameters, _length, _location, file_name, name = row[:8]
        tree, *rest = Path(file_name).resolve().relative_to(root.resolve()).parts
        by_tree.setdefault(tree, []).append(
            FunctionSize(Path(*rest).as_posix(), name, int(nloc), int(ccn), int(parameters))
        )
    return by_tree


def _summary(functions: list[FunctionSize]) -> dict:
    return {
        "functions": len(functions),
        "nloc": sum(function.nloc for function in functions),
        "max_nloc": max((function.nloc for function in functions), default=0),
        "max_ccn": max((function.ccn for function in functions), default=0),
        "long_functions": sum(function.nloc > LONG_FUNCTION_NLOC for function in functions),
        "complex_functions": sum(function.ccn > COMPLEX_FUNCTION_CCN for function in functions),
        "many_parameter_functions": sum(function.parameters > MANY_PARAMETERS for function in functions),
    }
