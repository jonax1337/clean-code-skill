"""Checks for 07-tests-for-rates: write a proper test suite for an untested module, without touching the module.

The central check lays ten hidden mutants of `src/rates.ts` (see hidden/mutants.json) over a temporary copy of the
agent's project, one at a time, and runs the project's tests on each. A suite that only covers the happy path, skips
boundaries, ties and error cases, or restates the implementation lets most mutants live.
"""

import json
import re
import shutil
import tempfile
from fnmatch import fnmatchcase
from pathlib import Path

import checklib
from agentic import HIDDEN_TESTS_DIR, Workspace
from checklib import NODE_TEST, NODE_TESTS_RAN, Check

SELFTEST_COMMANDS = ["npm test", "npx tsc --noEmit"]
TEST_RUN = r"^(node\s+(--[\w-]+(=\S+)?\s+)*--test\b|(npm|pnpm|yarn)\s+(run\s+)?test\b|npm\s+t\b)"
# What `node --test` picks up in this project: everything under test/ and files named *.test.ts.
TEST_PATHS = ["test/*", "*.test.ts"]
RATES = "src/rates.ts"
EXISTING_TESTS = ["test/format.test.ts", "test/iban.test.ts", "test/schedule.test.ts"]
RATES_IMPORT = re.compile(r"""\bfrom\s+["'][^"']*\b(rates|index)(\.ts)?["']""")  # index re-exports rates
TESTS_RUN = re.compile(r"(?:#|ℹ) tests (\d+)")  # the summary line of `node --test`, TAP or spec reporter
MINIMUM_TEST_CASES = 4  # one per exported function of rates.ts
# Of ten mutants, each a single change to one documented rule, a suite that covers the rules the code states
# (boundaries, ties, negative and zero amounts, each currency, each error) kills all ten. A careful suite written
# without seeing the mutants killed 8 in review, so three misses are allowed; a happy-path suite kills 1 to 3.
MINIMUM_MUTANTS_KILLED = 7


def setup(repo):
    checklib.install_node_toolchain(repo, ["typescript@7.0.2", "@types/node@26.6.6"])


def checks(workspace, transcript) -> list[Check]:
    return [
        _rates_tests_added(workspace),
        checklib.characterization_tests_pass_on_base(
            "new_tests_pass_on_original_code",
            "The tests the agent added run and pass against the untouched fixture (including the original rates.ts).",
            workspace,
            TEST_PATHS,
            NODE_TEST,
            NODE_TESTS_RAN,
        ),
        _mutants_caught(workspace),
        _source_unchanged(workspace),
        checklib.only_these_files_changed(
            "only_test_files_changed",
            "Only test files changed; the prompt says to leave the code alone, so no source, config or package file "
            "was touched.",
            workspace,
            TEST_PATHS,
        ),
        checklib.command_succeeds(
            "test_suite_passes", "The repository's own test suite passes.", workspace, NODE_TEST
        ),
        checklib.command_succeeds(
            "typecheck_passes", "The TypeScript type check passes, tests included.", workspace, checklib.TSC
        ),
        _existing_tests_untouched(workspace),
        checklib.clean_diff(
            "clean_diff",
            "The diff has no debug output, commented-out code or narrating comments.",
            workspace,
        ),
        checklib.ran_after_last_edit(
            "tests_run_after_last_edit",
            "After its last edit the agent ran the test suite and it passed.",
            transcript,
            TEST_RUN,
        ),
    ]


def _rates_tests_added(workspace: Workspace) -> Check:
    name = "rates_tests_added_where_runner_finds_them"
    description = (
        "At least four test cases (one per exported function of rates.ts) importing rates.ts, directly or through "
        "src/index.ts, were added in a file that `node --test` picks up (under test/ or named *.test.ts), without "
        "snapshot assertions."
    )
    files = {path: workspace.read(path) or "" for path in workspace.changed_files() if _is_test_path(path)}
    about_rates = {path: text for path, text in files.items() if RATES_IMPORT.search(text)}
    cases = _count_test_cases(workspace, sorted(about_rates)) if about_rates else 0
    snapshots = [path for path, text in about_rates.items() if "snapshot" in text.lower()]
    evidence = (
        f"files importing rates.ts: {sorted(about_rates)}; test cases: {cases}; snapshot use: {snapshots}"
    )
    return Check(name, description, cases >= MINIMUM_TEST_CASES and not snapshots, evidence)


def _count_test_cases(workspace: Workspace, files: list[str]) -> int:
    """How many tests `node --test` runs in these files; table-driven suites count by what they run."""
    completed = workspace.run([*NODE_TEST, *files])
    match = TESTS_RUN.search(completed.stdout + completed.stderr)
    return int(match.group(1)) if match else 0


def _mutants_caught(workspace: Workspace) -> Check:
    name = "tests_catch_mutants_of_rates"
    description = (
        f"The project's tests pass on the original code and fail on at least {MINIMUM_MUTANTS_KILLED} of "
        f"{_mutant_count(workspace)} hidden mutants of rates.ts, each a one-line change to a documented rule."
    )
    original = (workspace.read_base(RATES) or "").replace("\r\n", "\n")
    if _tests_fail_on(workspace, original):
        return Check(name, description, False, "the tests already fail on the original rates.ts")
    killed, survived = [], []
    for mutant in _load_mutants(workspace):
        if original.count(mutant["old"]) != 1:
            raise ValueError(f"mutant {mutant['name']} does not match rates.ts exactly once")
        mutated = original.replace(mutant["old"], mutant["new"])
        (killed if _tests_fail_on(workspace, mutated) else survived).append(mutant)
    evidence = f"killed {len(killed)}: {[m['name'] for m in killed]}\nsurvived {len(survived)}:" + "".join(
        f"\n  {m['name']}: {m['description']}" for m in survived
    )
    return Check(name, description, len(killed) >= MINIMUM_MUTANTS_KILLED, evidence)


def _source_unchanged(workspace: Workspace) -> Check:
    name = "source_code_unchanged"
    description = (
        "No file under src/ (rates.ts and its neighbors) differs from the fixture; "
        "the prompt says to leave the code alone."
    )
    changed = [
        path
        for path in workspace.changed_files()
        if path.startswith("src/")
        and not _is_test_path(path)
        and _normalized(workspace.read(path)) != _normalized(workspace.read_base(path))
    ]
    return Check(
        name, description, not changed, f"changed source files: {changed}" if changed else "unchanged"
    )


def _existing_tests_untouched(workspace: Workspace) -> Check:
    name = "existing_tests_not_loosened"
    description = "No line of the existing tests was changed or removed; tests may only be added."
    edited = {path: workspace.removed_lines(path) for path in EXISTING_TESTS}
    edited = {path: lines for path, lines in edited.items() if lines}
    evidence = f"changed or removed lines: {edited}" if edited else "tests only added to"
    return Check(name, description, not edited, evidence)


def _tests_fail_on(workspace: Workspace, rates_source: str) -> bool:
    """Run the project's tests on a temporary copy of the workspace whose rates.ts is replaced."""
    with tempfile.TemporaryDirectory(prefix="cc-mutant-", ignore_cleanup_errors=True) as temp:
        root = Path(temp) / "repo"
        ignored = shutil.ignore_patterns(".git", "node_modules", HIDDEN_TESTS_DIR)
        shutil.copytree(workspace.root, root, ignore=ignored)
        (root / RATES).write_text(rates_source, encoding="utf-8", newline="\n")
        return Workspace(root, workspace.case).run(NODE_TEST).returncode != 0


def _load_mutants(workspace: Workspace) -> list[dict[str, str]]:
    return json.loads((workspace.root / HIDDEN_TESTS_DIR / "mutants.json").read_text(encoding="utf-8"))


def _mutant_count(workspace: Workspace) -> int:
    return len(_load_mutants(workspace))


def _is_test_path(path: str) -> bool:
    return any(fnmatchcase(path, pattern) for pattern in TEST_PATHS)


def _normalized(text: str | None) -> str | None:
    return None if text is None else text.replace("\r\n", "\n")
