from agentic import Transcript, Workspace
from checklib import (
    PYTEST,
    PYTEST_RUN,
    Check,
    added_test_mentions,
    all_of,
    at_most_removed_lines,
    clean_diff,
    command_succeeds,
    no_added_lines,
    only_these_files_changed,
    python_calls,
    python_definitions_unchanged,
    ran_after_last_edit,
)

TARGET = "shop/emails.py"
TESTS = ["tests/*.py"]
SELFTEST_COMMANDS = ["python -m pytest -q"]


def checks(workspace: Workspace, transcript: Transcript) -> list[Check]:
    return [
        command_succeeds(
            "hidden_behavior",
            "The email shows the gross total with per-line VAT rounding, shipping and German formatting, "
            "right after the item list, and the rest of the email is unchanged (hidden tests).",
            workspace,
            [*PYTEST, ".hidden/test_hidden_emails.py"],
        ),
        python_calls(
            "reuses_helpers",
            "The new line uses the shop's existing `format_eur` and `gross_total`.",
            workspace,
            TARGET,
            ["format_eur", "gross_total"],
        ),
        no_added_lines(
            "no_reimplemented_money_logic",
            "No money formatting, rounding or VAT logic is reimplemented in the shop code.",
            workspace,
            r"quantize|:,\.2f|\.replace\(|translate\(|VAT_RATES|0\.19|0\.07",
            ["shop/*"],
        ),
        only_these_files_changed(
            "scope_files", "Only `shop/emails.py` and test files are changed.", workspace, [TARGET, *TESTS]
        ),
        all_of(
            "no_drive_by_edits",
            "The legacy code around the change is left alone: `subject` and `is_sendable` are untouched and at "
            "most two existing lines of `shop/emails.py` change.",
            python_definitions_unchanged("untouched", "", workspace, TARGET, ["subject", "is_sendable"]),
            at_most_removed_lines("small", "", workspace, TARGET, limit=2),
        ),
        added_test_mentions(
            "test_added", "A test for the new total line is added.", workspace, TESTS, "Gesamtbetrag"
        ),
        command_succeeds(
            "suite_green", "The full test suite passes, including the agent's own tests.", workspace, PYTEST
        ),
        clean_diff(
            "clean_diff", "No debug output, commented-out code or comments that narrate the edit.", workspace
        ),
        ran_after_last_edit("verified", "The agent ran the tests after its last edit.", transcript, PYTEST_RUN),
    ]
