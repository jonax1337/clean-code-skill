"""Checks for 12-remove-compact-flag: remove the deprecated `--compact` option from a small Rust CLI."""

from __future__ import annotations

import re
import tempfile

import checklib
from agentic import Transcript, Workspace
from checklib import Check

SELFTEST_COMMANDS = ["cargo test"]

HIDDEN_MANIFEST = ".hidden/Cargo.toml"
CARGO_TEST_RUN = r"^cargo\s+test\b"
RUST_FILES = ["src/*.rs", "tests/*.rs"]
RUST_TEST_NAME = re.compile(r"#\[test\]\s*\n\s*(?:pub\s+)?fn\s+(\w+)")
TESTS_PASSED = re.compile(r"test result: ok\. (\d+) passed")
README_TABLE_ROW = re.compile(r"^\s*\|.*compact", re.IGNORECASE)


def checks(workspace: Workspace, transcript: Transcript) -> list[Check]:
    return [
        _hidden_tests(
            "flag_is_rejected",
            "`--compact` and `-c` are rejected as unknown options, also between other options, and the help no longer mentions them.",
            workspace,
            "removed_",
        ),
        _hidden_tests(
            "other_behavior_preserved",
            "The output of the remaining options (alignment, header, border, delimiter, max width) and their error messages are unchanged.",
            workspace,
            "preserved_",
        ),
        _builds_without_warnings(workspace),
        _no_leftovers(workspace),
        _other_tests_kept(workspace),
        _changelog_records_removal(workspace),
        checklib.only_these_files_changed(
            "only_expected_files",
            "Only Rust sources, tests, the README and the changelog changed; Cargo.toml and Cargo.lock were left alone.",
            workspace,
            [*RUST_FILES, "README.md", "CHANGELOG.md"],
        ),
        checklib.command_succeeds(
            "suite_passes",
            "The project's own test suite passes.",
            workspace,
            ["cargo", "test"],
        ),
        checklib.clean_diff(
            "clean_diff",
            "The diff has no debug output, commented-out code or narrating comments.",
            workspace,
        ),
        checklib.ran_after_last_edit(
            "tests_run_after_edit",
            "The agent ran `cargo test` successfully after its last edit.",
            transcript,
            CARGO_TEST_RUN,
        ),
    ]


def _hidden_tests(name: str, description: str, workspace: Workspace, test_filter: str) -> Check:
    """Run the hidden crate's tests whose names start with `test_filter`; at least one must run and all must pass."""
    completed = workspace.run(["cargo", "test", "--manifest-path", HIDDEN_MANIFEST, test_filter])
    output = completed.stdout + completed.stderr
    passed = sum(int(count) for count in TESTS_PASSED.findall(output))
    evidence = f"exit {completed.returncode}, {passed} tests passed\n" + "\n".join(output.strip().splitlines()[-12:])
    return Check(name, description, completed.returncode == 0 and passed > 0, evidence)


def _builds_without_warnings(workspace: Workspace) -> Check:
    """A fresh build of every target has no compiler warnings, and none were silenced with `allow` attributes."""
    description = (
        "Every target builds without compiler warnings (nothing is left unused), and no warning was silenced with an `allow` attribute."
    )
    with tempfile.TemporaryDirectory(prefix="cc-target-", ignore_cleanup_errors=True) as target:
        completed = workspace.run(["cargo", "build", "--all-targets", "--target-dir", target])
    output = completed.stdout + completed.stderr
    warnings = [line.strip() for line in output.splitlines() if line.startswith("warning")]
    silenced = checklib.no_added_lines("", "", workspace, r"#!?\[allow\(", ["src/*.rs", "tests/*.rs"])
    passed = completed.returncode == 0 and not warnings and silenced.passed
    evidence = f"build exit {completed.returncode}; warnings: {warnings[:6]}; allow attributes: {silenced.evidence}"
    return Check("builds_without_warnings", description, passed, evidence)


def _no_leftovers(workspace: Workspace) -> Check:
    description = (
        "Nothing about the removed option remains in the source files, and the README option table no longer lists it."
    )
    # Unit tests in a `#[cfg(test)]` module are idiomatic Rust; a regression test there must be able to name the flag.
    leftovers = [
        f"{path}: {line.strip()}"
        for path in _rust_files(workspace, "src")
        for line in (workspace.read(path) or "").split("#[cfg(test)]", 1)[0].splitlines()
        if re.search("compact", line, re.IGNORECASE)
    ]
    leftovers += [
        f"README.md: {line.strip()}"
        for line in (workspace.read("README.md") or "").splitlines()
        if README_TABLE_ROW.search(line)
    ]
    return Check("no_leftovers", description, not leftovers, checklib._quoted(leftovers) or "no leftovers")


def _other_tests_kept(workspace: Workspace) -> Check:
    description = "Every test that is not about the removed option is still there; none was deleted or renamed to make things pass."
    before = {name for path in _rust_files(workspace, "src", "tests", base=True) for name in _test_names(workspace.read_base(path))}
    expected = {name for name in before if "compact" not in name}
    present = {name for path in _rust_files(workspace, "src", "tests") for name in _test_names(workspace.read(path))}
    missing = sorted(expected - present)
    evidence = f"missing tests: {missing}" if missing else f"all {len(expected)} other tests are still present"
    return Check("other_tests_kept", description, not missing and bool(expected), evidence)


def _changelog_records_removal(workspace: Workspace) -> Check:
    description = (
        "The changelog has a new entry for the removal under Unreleased, and the 0.8.0 deprecation entry was not rewritten."
    )
    text = workspace.read("CHANGELOG.md") or ""
    lines = text.splitlines()
    released = next((i for i, line in enumerate(lines) if line.startswith("## ") and "Unreleased" not in line), len(lines))
    unreleased_mentions = [line for line in lines[:released] if "compact" in line.lower()]
    rewritten = workspace.removed_lines("CHANGELOG.md")
    evidence = f"unreleased entries: {unreleased_mentions}; changed existing lines: {rewritten}"
    return Check("changelog_entry", description, bool(unreleased_mentions) and not rewritten, evidence)


def _test_names(source: str | None) -> list[str]:
    return RUST_TEST_NAME.findall(source or "")


def _rust_files(workspace: Workspace, *directories: str, base: bool = False) -> list[str]:
    """Rust files below the directories, as they are now or (with `base`) in the untouched fixture."""
    if base:
        listing = workspace.git("ls-tree", "-r", "--name-only", "eval-base").splitlines()
    else:
        listing = [path.relative_to(workspace.root).as_posix() for path in workspace.root.rglob("*.rs")]
    return sorted(path for path in listing if path.endswith(".rs") and path.split("/")[0] in directories)
