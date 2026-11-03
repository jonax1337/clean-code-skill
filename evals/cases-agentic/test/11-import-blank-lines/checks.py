"""Checks for 11-import-blank-lines: make the CSV importer skip blank lines without hiding real format errors."""

from __future__ import annotations

import checklib
from agentic import Transcript, Workspace
from checklib import Check

SELFTEST_COMMANDS = ["python -m pytest -q"]

HIDDEN_TESTS = ".hidden/test_import_blank_lines.py"
EXISTING_TEST_FILES = ["tests/test_cli.py", "tests/test_importer.py", "tests/test_report.py", "tests/test_store.py"]
CATCH_ALL_HANDLER = r"^\s*except\s*:|^\s*except\s+\(?\s*(Exception|BaseException)\b"


def checks(workspace: Workspace, transcript: Transcript) -> list[Check]:
    return [
        _hidden(
            "blank_lines_skipped",
            "Blank lines are skipped wherever they are in the file: empty, whitespace-only and Windows line endings, at the start, in the middle and at the end.",
            workspace,
            "blank_lines_are_skipped or only_blank or imports_a_file",
        ),
        _hidden(
            "malformed_lines_still_rejected",
            "Rows that are really malformed (missing or extra fields, bad date, bad or negative minutes, empty project) still fail the import, and the error names the line's position in the file even after blank lines.",
            workspace,
            "malformed",
        ),
        checklib.no_added_lines(
            "no_catch_all_handler",
            "No bare `except:` or `except Exception` was added to the package.",
            workspace,
            CATCH_ALL_HANDLER,
            ["hourlog/*.py"],
        ),
        checklib.only_these_files_changed(
            "only_expected_files",
            "Only the importer and the tests changed.",
            workspace,
            ["hourlog/importer.py", "tests/*.py"],
        ),
        checklib.all_of(
            "existing_tests_untouched",
            "No line of the existing tests was changed or removed.",
            *[checklib.at_most_removed_lines("", "", workspace, path, 0) for path in EXISTING_TEST_FILES],
        ),
        checklib.regression_tests_fail_on_base(
            "regression_test_added",
            "The agent added at least one test that fails on the original code, so the bug cannot return unnoticed.",
            workspace,
            ["tests/*.py"],
        ),
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


def _hidden(name: str, description: str, workspace: Workspace, expression: str) -> Check:
    return checklib.command_succeeds(name, description, workspace, [*checklib.PYTEST, HIDDEN_TESTS, "-k", expression])
