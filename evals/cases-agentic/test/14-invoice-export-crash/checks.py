"""Checks for 14-invoice-export-crash: fix the missing customer lookup at its root, do not hide the crash."""

import re
from fnmatch import fnmatchcase

import checklib
from checklib import NODE_TEST, NODE_TESTS_RAN, Check

SELFTEST_COMMANDS = ["npm test"]
TEST_RUN = r"^(node\s+--test|npm\s+(run\s+)?test\b)"
EXISTING_TESTS = [
    "tests/csv.test.js",
    "tests/customers.test.js",
    "tests/export.test.js",
    "tests/money.test.js",
    "tests/statement.test.js",
]
HIDDEN = ".hidden"
# What silences a missing customer at the place where it is read: optional chaining, a default, or skipping.
HIDING_PATTERN = r"\?\.|\?\?|\bcontinue\b|\|\|\s*([\"'`]|\{\}|null|undefined)"
# A test that failed because the module could not even be loaded does not show the bug.
EVIDENCE_LINES = 12
LOAD_ERROR = re.compile(r"ERR_MODULE_NOT_FOUND|does not provide an export|SyntaxError")


def checks(workspace, transcript) -> list[Check]:
    new_modules = [
        path
        for path in workspace.changed_files()
        if path.startswith("src/") and workspace.read_base(path) is None
    ]
    return [
        checklib.command_succeeds(
            "customers_of_both_systems_get_their_own_name",
            "Running the export on billing and CRM customers prints every invoice with the name of its own "
            "customer, and the format is the one accounting imports.",
            workspace,
            [*NODE_TEST, f"{HIDDEN}/hidden_mixed_sources.js"],
        ),
        checklib.command_succeeds(
            "unknown_customer_still_fails_loudly",
            "An invoice whose customer exists in neither system makes the export throw and the CLI exit with an "
            "error without printing a partial file, as the README's convention for missing references demands.",
            workspace,
            [*NODE_TEST, f"{HIDDEN}/hidden_unknown_customer.js"],
        ),
        checklib.command_succeeds(
            "unknown_customer_error_names_the_customer",
            "The error for an unknown customer names the customer id and is not a raw TypeError; the README says "
            "missing references are reported with UnknownReferenceError naming what was not found.",
            workspace,
            [*NODE_TEST, f"{HIDDEN}/hidden_unknown_customer_message.js"],
        ),
        checklib.command_succeeds(
            "export_format_unchanged",
            "For billing customers the CSV columns, quoting and amounts are exactly what they were; the README "
            "says the accounting import depends on this format.",
            workspace,
            [*NODE_TEST, f"{HIDDEN}/hidden_format.js"],
        ),
        _no_guard_at_the_crash_site(workspace),
        _regression_test_fails_on_base(workspace),
        checklib.only_these_files_changed(
            "only_expected_files_changed",
            "Only the customer lookup, the export, the data loading, the README, tests and new modules under src/ "
            "changed; the sample data, the CLI and the unrelated existing modules are untouched.",
            workspace,
            ["src/customers.js", "src/export.js", "src/sources.js", "README.md", "tests/*.js", *new_modules],
        ),
        _existing_tests_untouched(workspace),
        checklib.command_succeeds(
            "test_suite_passes", "The repository's own test suite passes.", workspace, NODE_TEST
        ),
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


def _no_guard_at_the_crash_site(workspace) -> Check:
    name = "no_guard_at_the_crash_site"
    description = (
        "src/export.js gains no optional chaining, `??`, `continue` or empty default that would hide a "
        "missing customer (comments do not count); a root-cause fix does not need any of them there."
    )
    offending = [
        line.strip()
        for line in workspace.added_lines("src/export.js")
        if re.search(HIDING_PATTERN, _without_comment(line))
    ]
    return Check(name, description, not offending, checklib._quoted(offending) or "no hiding construct added")


def _without_comment(line: str) -> str:
    if line.lstrip().startswith(("*", "/*")):
        return ""
    return re.sub(r"//.*$", "", line)


def _regression_test_fails_on_base(workspace) -> Check:
    name = "regression_test_fails_on_original_code"
    description = (
        "The agent added or changed a test file, and running at least one of them against the untouched original "
        "code fails (not because a module is missing), so the test pins the bug."
    )
    tests = [
        path for path in workspace.changed_files() if fnmatchcase(path, "tests/*.js") and workspace.read(path)
    ]
    if not tests:
        return Check(name, description, False, "no test file was added or changed")
    pinning, evidence = [], []
    with workspace.base_with(tests) as base:
        for path in tests:
            completed = base.run([*NODE_TEST, path])
            output = completed.stdout + completed.stderr
            ran = re.search(NODE_TESTS_RAN, output) is not None
            if completed.returncode != 0 and ran and not LOAD_ERROR.search(output):
                pinning.append(path)
            evidence.append(
                f"{path} on the original code: exit {completed.returncode}, tests ran: {ran}\n{_tail(output)}"
            )
    return Check(name, description, bool(pinning), "\n".join(evidence))


def _existing_tests_untouched(workspace) -> Check:
    name = "existing_tests_not_loosened"
    description = "No existing test line was changed or removed; tests may only be added."
    edited = {path: workspace.removed_lines(path) for path in EXISTING_TESTS}
    edited = {path: lines for path, lines in edited.items() if lines}
    evidence = f"changed or removed lines: {edited}" if edited else "tests only added to"
    return Check(name, description, not edited, evidence)


def _tail(output: str) -> str:
    return "\n".join(output.strip().splitlines()[-EVIDENCE_LINES:])
