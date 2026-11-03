"""Checks for 18-config-errors-visible: a loader that silently falls back to defaults must fail loudly instead."""

import re
from fnmatch import fnmatchcase

import checklib
from checklib import JAVA_TEST, Check

SELFTEST_COMMANDS = ["java tools/RunTests.java"]
HIDDEN_TESTS = ".hidden"
MAIN_SOURCES = "src/main/java"
CONFIG_PACKAGE = "/config/"
ENTRY_POINT = "src/main/java/com/acme/relay/Main.java"
TEST_FILES = "src/test/java/*"
ASSERTS_FAILURE = re.compile(
    r"\bassertThrows(Exactly)?\b|\bassertThatThrownBy\b|\bassertThatExceptionOfType\b|\bfail\("
)
# A catch block that records the problem for a later exception instead of throwing at once, or that reports
# "no value" as an empty Optional, does not absorb the error: the caller still has to decide.
THROW = re.compile(r"\bthrow\b")
RECORDS_PROBLEM = re.compile(r"\.(add|addAll|put|append|accept|offer|push)\s*\(")
EMPTY_OPTIONAL_RETURN = re.compile(r"\breturn\s+Optional(Int|Long|Double)?\s*\.\s*empty\s*\(\s*\)\s*;")
EXIT_CALL = re.compile(
    r"\bSystem\s*\.\s*exit\s*\(|\bRuntime\s*\.\s*getRuntime\s*\(\s*\)\s*\.\s*(exit|halt)\s*\("
)
CATCH_HEAD = re.compile(r"\bcatch\s*\(([^)]*)\)\s*\{")
EVIDENCE_LINES = 12


def setup(repo):
    checklib.install_java_toolchain(repo)


def checks(workspace, transcript) -> list[Check]:
    return [
        checklib.command_succeeds(
            "malformed_values_fail_naming_key_and_value",
            "A value that is present but malformed (a non-number, a number out of range, a timeout without a "
            "unit, the boolean typo `ture`, an unparsable URL) makes the loader throw, and the exception "
            "message names the key and shows the bad value.",
            workspace,
            [*JAVA_TEST, f"{HIDDEN_TESTS}/malformed"],
        ),
        checklib.command_succeeds(
            "missing_required_keys_and_unreadable_file_fail",
            "A missing upstream.url or api.token, and a configuration file that cannot be read, make the "
            "loader throw with a message that names the key or the file.",
            workspace,
            [*JAVA_TEST, f"{HIDDEN_TESTS}/required"],
        ),
        checklib.command_succeeds(
            "optional_keys_and_valid_files_unchanged",
            "A file with only the two required keys still loads with the documented defaults, each optional key "
            "can be left out on its own, and a valid full file (comments, padded values, `True`, every "
            "timeout unit) loads exactly as before.",
            workspace,
            [*JAVA_TEST, f"{HIDDEN_TESTS}/defaults"],
        ),
        checklib.command_succeeds(
            "entry_point_refuses_to_start_cleanly",
            "Started as a real process, Main exits with a non-zero status and a short stderr message that names "
            "the bad key and value (or the missing file), without a stack trace and without processing any "
            "message; with a valid file it still relays messages and exits 0.",
            workspace,
            [*JAVA_TEST, f"{HIDDEN_TESTS}/startup"],
        ),
        checklib.only_these_files_changed(
            "only_expected_files_changed",
            "Only Java sources, tests, the README and the sample config (to document the stricter rules) changed; "
            "no build tooling or library files were touched.",
            workspace,
            [f"{MAIN_SOURCES}/*", TEST_FILES, "README.md", "config.example.properties"],
        ),
        _no_swallowing_catch(workspace),
        _caught_exceptions_keep_their_cause(workspace),
        _no_exit_outside_entry_point(workspace),
        _tests_pin_the_new_behavior(workspace),
        checklib.command_succeeds(
            "test_suite_passes", "The repository's own test suite passes.", workspace, JAVA_TEST
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
            checklib.JAVA_TEST_RUN,
        ),
    ]


def _no_swallowing_catch(workspace) -> Check:
    name = "no_swallowing_catch_in_config_package"
    description = (
        "No catch block in the configuration package absorbs the error: each one throws, records the problem "
        "for a later ConfigException (adds it to a collection), or reports 'no value' as an empty Optional; "
        "none returns a default or null, logs and continues, or is empty. This is the point of the request."
    )
    offending = [
        f"{path}: catch ({caught}) neither throws nor records the problem"
        for path, source in _config_sources(workspace)
        for caught, body in _catch_blocks(source)
        if not _reports_the_error(body)
    ]
    return Check(name, description, not offending, _quoted(offending) or "no catch block absorbs an error")


def _caught_exceptions_keep_their_cause(workspace) -> Check:
    name = "caught_exceptions_keep_their_cause"
    description = (
        "A catch block in the configuration package that throws passes the caught exception on (as the cause or "
        "rethrown itself), so the operator and the log keep the original failure."
    )
    offending = []
    for path, source in _config_sources(workspace):
        for caught, body in _catch_blocks(source):
            variable = caught.split()[-1] if caught.split() else ""
            thrown = re.findall(r"\bthrow\b[^;]*;", body)
            if thrown and not any(
                re.search(rf"\b{re.escape(variable)}\b", statement) for statement in thrown
            ):
                offending.append(f"{path}: catch ({caught}) throws without using {variable}")
    return Check(name, description, not offending, _quoted(offending) or "causes are kept")


def _no_exit_outside_entry_point(workspace) -> Check:
    name = "no_exit_outside_the_entry_point"
    description = (
        "System.exit and Runtime.exit/halt appear neither in the configuration package nor in the classes that "
        "existed before (Main aside): the loader reports the error and the startup code decides to stop the "
        "process. A new startup class next to Main may do it."
    )
    offending = [
        f"{path}: {line.strip()}"
        for path, source in _main_sources(workspace)
        if path != ENTRY_POINT and (CONFIG_PACKAGE in path or workspace.read_base(path) is not None)
        for line in _strip_comments_and_strings(source).splitlines()
        if EXIT_CALL.search(line)
    ]
    return Check(
        name, description, not offending, _quoted(offending) or "no exit call outside the startup code"
    )


def _tests_pin_the_new_behavior(workspace) -> Check:
    name = "tests_assert_the_new_failures"
    description = (
        "The agent added or rewrote tests that assert a configuration error is thrown (the old tests pinned the "
        "silent fallback), and the changed tests do not pass on the untouched original code."
    )
    tests = [
        path for path in workspace.changed_files() if fnmatchcase(path, TEST_FILES) and workspace.read(path)
    ]
    asserting = [
        line.strip() for path in tests for line in workspace.added_lines(path) if ASSERTS_FAILURE.search(line)
    ]
    if not asserting:
        return Check(
            name, description, False, f"no added test line asserts an exception; changed tests: {tests}"
        )
    with workspace.base_with(tests) as base:
        completed = base.run(JAVA_TEST)
    tail = "\n".join((completed.stdout + completed.stderr).strip().splitlines()[-EVIDENCE_LINES:])
    evidence = f"{tests} on the original code: exit {completed.returncode}\n{tail}"
    return Check(name, description, completed.returncode != 0, evidence)


def _main_sources(workspace) -> list[tuple[str, str]]:
    root = workspace.root
    return [
        (path.relative_to(root).as_posix(), path.read_text(encoding="utf-8"))
        for path in sorted((root / MAIN_SOURCES).rglob("*.java"))
    ]


def _config_sources(workspace) -> list[tuple[str, str]]:
    return [(path, source) for path, source in _main_sources(workspace) if CONFIG_PACKAGE in path]


def _strip_comments_and_strings(source: str) -> str:
    """Java source with comments and string or character literals blanked out, line structure kept."""
    patterns = [
        r'"""[\s\S]*?"""',
        r'"(?:\\.|[^"\\\n])*"',
        r"'(?:\\.|[^'\\\n])'",
        r"/\*[\s\S]*?\*/",
        r"//[^\n]*",
    ]
    for pattern in patterns:
        source = re.sub(pattern, lambda match: re.sub(r"[^\n]", " ", match.group(0)), source)
    return source


def _catch_blocks(source: str) -> list[tuple[str, str]]:
    """Each catch clause of the source as (caught type and variable, body)."""
    code = _strip_comments_and_strings(source)
    blocks = []
    for head in CATCH_HEAD.finditer(code):
        depth, position = 1, head.end()
        while depth and position < len(code):
            depth += {"{": 1, "}": -1}.get(code[position], 0)
            position += 1
        blocks.append((head.group(1).strip(), code[head.end() : position - 1]))
    return blocks


def _reports_the_error(catch_body: str) -> bool:
    """Whether a catch body throws, records the problem, or reports 'no value' as an empty Optional."""
    return any(pattern.search(catch_body) for pattern in (THROW, EMPTY_OPTIONAL_RETURN, RECORDS_PROBLEM))


def _quoted(lines: list[str]) -> str:
    return "".join(f"\n  {line}" for line in lines[:EVIDENCE_LINES])
