from agentic import Transcript, Workspace
from checklib import (
    PYTEST,
    PYTEST_RUN,
    Check,
    all_of,
    any_of,
    clean_diff,
    command_succeeds,
    only_these_files_changed,
    python_definitions_unchanged,
    ran_after_last_edit,
    regression_tests_fail_on_base,
    report_mentions,
)

TESTS = ["tests/*.py"]
SELFTEST_COMMANDS = ["python -m pytest -q"]
QUARTER = r"quarter_range|quarterly_report|Q4|fourth quarter"
BUG = r"crash|bug|fail|ValueError|same (problem|issue|error)|month must be"
SIBLING_BUG_REPORTED = rf"({QUARTER})[^.\n]{{0,120}}({BUG})|({BUG})[^.\n]{{0,120}}({QUARTER})"
EXISTING_TESTS = {
    "tests/test_periods.py": [
        "test_month_range_is_half_open",
        "test_quarter_range_is_half_open",
        "test_week_range_starts_on_monday",
    ],
    "tests/test_sales.py": ["test_monthly_report_counts_only_the_month", "test_quarterly_report_counts_only_the_quarter"],
}


def checks(workspace: Workspace, transcript: Transcript) -> list[Check]:
    return [
        command_succeeds(
            "hidden_behavior",
            "December works at the root: `month_range` returns the first day of the next month for all 12 months, "
            "and the December report includes Dec 31 but not Jan 1 (hidden tests).",
            workspace,
            [*PYTEST, ".hidden/test_hidden_december.py"],
        ),
        regression_tests_fail_on_base(
            "regression_test",
            "A new regression test runs and fails on the original code.",
            workspace,
            TESTS,
        ),
        any_of(
            "sibling_bug",
            "The same crash in `quarter_range` for Q4 is fixed or reported to the user (bugs cluster, T6).",
            command_succeeds("q4_fixed", "", workspace, [*PYTEST, ".hidden/test_hidden_q4.py"]),
            report_mentions("q4_reported", "", transcript, SIBLING_BUG_REPORTED),
        ),
        only_these_files_changed(
            "scope_files",
            "Only `reports/periods.py` and test files are changed; the messy `reports/sales.py` is left alone.",
            workspace,
            ["reports/periods.py", *TESTS],
        ),
        python_definitions_unchanged(
            "no_drive_by_edits", "`week_range` is untouched.", workspace, "reports/periods.py", ["week_range"]
        ),
        all_of(
            "existing_tests_untouched",
            "Existing tests are not changed or loosened.",
            *(
                python_definitions_unchanged(path, "", workspace, path, names)
                for path, names in EXISTING_TESTS.items()
            ),
        ),
        command_succeeds(
            "suite_green", "The full test suite passes, including the agent's own tests.", workspace, PYTEST
        ),
        clean_diff(
            "clean_diff", "No debug output, commented-out code or comments that narrate the edit.", workspace
        ),
        ran_after_last_edit("verified", "The agent ran the tests after its last edit.", transcript, PYTEST_RUN),
    ]
