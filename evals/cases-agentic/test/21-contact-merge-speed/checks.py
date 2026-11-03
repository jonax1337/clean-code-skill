"""Checks for 21-contact-merge-speed: mergeContacts is quadratic and must become linear without changing behavior."""

import checklib
from checklib import Check, NODE_TEST

SELFTEST_COMMANDS = ["npm test", "npx tsc --noEmit"]
TEST_RUN = r"^(node\s+--test|npm\s+(run\s+)?test\b)"
EXISTING_TESTS = [
    "test/import.test.ts",
    "test/merge.test.ts",
    "test/normalize.test.ts",
    "test/pipeline.test.ts",
    "test/summary.test.ts",
]


def setup(repo):
    checklib.install_node_toolchain(repo, ["typescript@7.0.2", "@types/node@26.6.6"])


def checks(workspace, transcript) -> list[Check]:
    return [
        checklib.command_succeeds(
            "same_result_as_before",
            "mergeContacts returns exactly what the old implementation returned on random inputs with many "
            "duplicates, on a book that already holds the same email twice, and when called repeatedly.",
            workspace,
            [*NODE_TEST, ".hidden/hidden_equivalence.ts"],
        ),
        checklib.command_succeeds(
            "inputs_not_modified",
            "mergeContacts does not modify the arrays or contacts it receives and always returns a new array.",
            workspace,
            [*NODE_TEST, ".hidden/hidden_inputs.ts"],
        ),
        checklib.command_succeeds(
            "work_grows_linearly",
            "Merging 3000 contacts reads each email only a handful of times instead of once per other contact.",
            workspace,
            [*NODE_TEST, ".hidden/hidden_scaling.ts"],
        ),
        checklib.only_these_files_changed(
            "only_expected_files_changed",
            "Only the merge code, the email normalizer and tests changed; no package or config files were touched.",
            workspace,
            ["src/import.ts", "src/normalize.ts", "test/*.test.ts"],
        ),
        _existing_tests_untouched(workspace),
        checklib.command_succeeds(
            "test_suite_passes", "The repository's own test suite passes.", workspace, NODE_TEST
        ),
        checklib.command_succeeds(
            "typecheck_passes", "The TypeScript type check passes.", workspace, checklib.TSC
        ),
        checklib.no_added_lines(
            "no_second_normalization",
            "The merge does not re-implement email normalization inline; it keeps using normalizeEmail.",
            workspace,
            r"toLowerCase\(|toLocaleLowerCase\(|\.trim\(",
            ["src/import.ts"],
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


def _existing_tests_untouched(workspace) -> Check:
    name = "existing_tests_not_loosened"
    description = "No existing test line was changed or removed; tests may only be added."
    edited = {path: workspace.removed_lines(path) for path in EXISTING_TESTS}
    edited = {path: lines for path, lines in edited.items() if lines}
    return Check(name, description, not edited, f"changed or removed lines: {edited}" if edited else "tests only added to")
