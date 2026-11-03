"""Checks for 10-split-by-percent: add a percentage split to a small expense-sharing CLI that counts in cents."""

from __future__ import annotations

import checklib
from agentic import Transcript, Workspace
from checklib import Check

SELFTEST_COMMANDS = ["python -m pytest -q"]

HIDDEN_TESTS = ".hidden/test_percent_split.py"
EXISTING_TEST_FILES = [
    "tests/test_balances.py",
    "tests/test_cli.py",
    "tests/test_money.py",
    "tests/test_splitting.py",
    "tests/test_store.py",
]


def checks(workspace: Workspace, transcript: Transcript) -> list[Check]:
    return [
        _hidden(
            "shares_add_up",
            "A percentage split gives every person a whole number of cents next to their exact share, and the shares add up to the amount, even when the percentages do not divide it evenly.",
            workspace,
            "add_up or accumulate",
        ),
        _hidden(
            "invalid_input_rejected",
            "Percentages that do not add up to 100, are not whole numbers, are negative, lack `=` or repeat a person are reported as an error with exit code 2 and nothing is saved.",
            workspace,
            "rejected",
        ),
        _hidden(
            "equal_split_unchanged",
            "Equal splits with `--with` still work exactly as before and can be mixed with percentage splits.",
            workspace,
            "unchanged or mixed",
        ),
        checklib.no_added_lines(
            "no_float_money",
            "No amount or percentage goes through `float()` or `round()`, which lose cents.",
            workspace,
            r"\bfloat\(|\bround\(",
            ["tabtally/*.py"],
        ),
        checklib.only_these_files_changed(
            "only_expected_files",
            "Only the package, the tests and the README changed.",
            workspace,
            ["tabtally/*.py", "tests/*.py", "README.md"],
        ),
        _existing_tests_untouched(workspace),
        checklib.added_test_mentions(
            "tests_added",
            "The agent added tests that exercise the percentage split.",
            workspace,
            ["tests/*.py"],
            "percent",
        ),
        _readme_documents_option(workspace),
        checklib.command_succeeds(
            "suite_passes",
            "The project's own test suite passes.",
            workspace,
            [*checklib.PYTEST],
        ),
        checklib.clean_diff(
            "clean_diff",
            "The diff has no debug output, commented-out code or narrating comments.",
            workspace,
        ),
        checklib.ran_after_last_edit(
            "tests_run_after_edit",
            "The agent ran the tests successfully after its last edit.",
            transcript,
            checklib.PYTEST_RUN,
        ),
    ]


def _existing_tests_untouched(workspace: Workspace) -> Check:
    """Existing tests may gain new imports, but none of their other lines may be changed or removed."""
    description = "No existing test was changed or removed; the only existing lines that may change are imports."
    altered = [
        f"{path}: {line.strip()}"
        for path in EXISTING_TEST_FILES
        for line in workspace.removed_lines(path)
        if not line.startswith(("from ", "import "))
    ]
    return Check("existing_tests_untouched", description, not altered, checklib._quoted(altered) or "no existing test line altered")


def _hidden(name: str, description: str, workspace: Workspace, expression: str) -> Check:
    return checklib.command_succeeds(name, description, workspace, [*checklib.PYTEST, HIDDEN_TESTS, "-k", expression])


def _readme_documents_option(workspace: Workspace) -> Check:
    description = "The README documents the new `--percent` option."
    documented = "--percent" in (workspace.read("README.md") or "")
    return Check("readme_updated", description, documented, "README mentions --percent" if documented else "README does not mention --percent")
