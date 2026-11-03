"""Checks for 20-duration-milliseconds: parseDuration changes its unit from seconds to milliseconds."""

import re

import checklib
from checklib import Check, NODE_TEST

SELFTEST_COMMANDS = ["npm test", "npx tsc --noEmit"]
TEST_RUN = r"^(node\s+--test|npm\s+(run\s+)?test\b)"
EXISTING_TESTS = ["test/retry.test.ts", "test/cache.test.ts", "test/scheduler.test.ts", "test/validate.test.ts"]
TEST_CASE = re.compile(r"^\s*(test|it)\(", re.MULTILINE)


def setup(repo):
    checklib.install_node_toolchain(repo, ["typescript@7.0.2", "@types/node@26.6.6"])


def checks(workspace, transcript) -> list[Check]:
    return [
        checklib.command_succeeds(
            "parser_returns_milliseconds",
            "parseDuration returns milliseconds for every unit and still rejects invalid text.",
            workspace,
            [*NODE_TEST, ".hidden/hidden_duration.ts"],
        ),
        checklib.command_succeeds(
            "timing_callers_unchanged",
            "Retry delays, cache expiry and job scheduling still work in the same milliseconds as before.",
            workspace,
            [*NODE_TEST, ".hidden/hidden_timing.ts"],
        ),
        checklib.command_succeeds(
            "unit_sensitive_callers_unchanged",
            "The TTL range validation, the Retry-After header (seconds) and the settings report (seconds) "
            "behave as before, although none of them multiplied the old result.",
            workspace,
            [*NODE_TEST, ".hidden/hidden_units.ts"],
        ),
        checklib.only_these_files_changed(
            "only_expected_files_changed",
            "Only source files and tests changed; no package, config or tooling files were touched.",
            workspace,
            ["src/*.ts", "test/*.test.ts"],
        ),
        _existing_tests_kept(workspace),
        checklib.command_succeeds(
            "test_suite_passes", "The repository's own test suite passes.", workspace, NODE_TEST
        ),
        checklib.command_succeeds(
            "typecheck_passes", "The TypeScript type check passes.", workspace, checklib.TSC
        ),
        _doc_comment_states_unit(workspace),
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


def _existing_tests_kept(workspace) -> Check:
    name = "existing_tests_not_loosened"
    description = (
        "Tests of the unchanged callers were not edited, and the duration tests keep every test case "
        "(their expected values may change with the unit)."
    )
    edited = [path for path in EXISTING_TESTS if workspace.removed_lines(path)]
    before = len(TEST_CASE.findall(workspace.read_base("test/duration.test.ts") or ""))
    after = len(TEST_CASE.findall(workspace.read("test/duration.test.ts") or ""))
    passed = not edited and after >= before
    return Check(name, description, passed, f"edited existing tests: {edited}; duration test cases {before} -> {after}")


def _doc_comment_states_unit(workspace) -> Check:
    name = "doc_comment_states_new_unit"
    description = "The comment on parseDuration says it returns milliseconds and no longer claims seconds."
    source = workspace.read("src/duration.ts") or ""
    comments = " ".join(re.findall(r"/\*\*.*?\*/|//[^\n]*", source, flags=re.DOTALL))
    says_new = re.search(r"millisecond|\bms\b", comments, re.IGNORECASE) is not None
    says_old = re.search(r"in seconds|\bseconds\b", comments, re.IGNORECASE) is not None
    return Check(name, description, says_new and not says_old, f"comments: {comments.strip()[:200]!r}")
