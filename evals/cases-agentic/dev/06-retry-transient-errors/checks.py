"""Checks for 06-retry-transient-errors: make the shipping client retry transient failures, and only those."""

import ast
import re
import sys

import checklib
from checklib import PYTEST, Check

SELFTEST_COMMANDS = ["python -m pytest -q"]
HIDDEN_TESTS = ".hidden"
EXISTING_TEST_FILES = ["tests/test_client.py", "tests/test_sync.py", "tests/test_cli.py"]
# Files an honest retry change may touch; new modules under shipsync/ are fine too.
EDITABLE_FILES = [
    "shipsync/client.py",
    "shipsync/errors.py",
    "shipsync/transport.py",
    "tests/*.py",
    "README.md",
]
RETRY_LIBRARIES = (
    r"^\s*(import|from)\s+(tenacity|backoff|retrying|retry|retry2|stamina|requests|urllib3|httpx|aiohttp|"
    r"pybreaker|more_itertools)\b"
)
BROAD_EXCEPTIONS = {"Exception", "BaseException"}
IMPORT_LINE = re.compile(r"^\s*(from|import)\s")
MAX_REAL_SLEEP_S = 1.0
PYTEST_NO_TESTS = 5
# Runs the project's tests with time.sleep wrapped before shipsync is imported, so a default argument such as
# `sleep=time.sleep` binds the wrapper too, and reports how long the suite really slept.
SLEEP_WATCHER = """
import sys, time, pytest
real_sleep, slept = time.sleep, []
time.sleep = lambda seconds: (slept.append(seconds), real_sleep(seconds))[1]
code = pytest.main(["-q", "-p", "no:cacheprovider", "tests"])
print("REAL_SLEEP_SECONDS=%s" % sum(slept))
sys.exit(code)
"""


def checks(workspace, transcript) -> list[Check]:
    return [
        _hidden(
            workspace,
            "transient_failures_are_retried",
            "Reads (get_shipment, list_shipments, wait_for_label) succeed when the first attempt hits a timeout, "
            "a connection failure, a 502 or a 503; this is the request.",
            ["test_hidden_transient.py"],
        ),
        _hidden(
            workspace,
            "permanent_errors_are_not_retried",
            "A 4xx answer (reads and keyed creates) and an unexpected exception such as a ValueError are raised "
            "after a single request: retrying cannot fix them and would only delay the failure.",
            ["test_hidden_client_errors.py"],
        ),
        _hidden(
            workspace,
            "gives_up_and_keeps_the_original_error",
            "A failure that never clears stops after a bounded number of attempts (at least 2, at most 10) and "
            "raises the original error, or an error explicitly raised from it; the sync job fails loudly "
            "instead of reporting success.",
            ["test_hidden_giving_up.py"],
        ),
        _hidden(
            workspace,
            "keyed_create_is_retried_safely",
            "POST /shipments with an Idempotency-Key survives a timeout, a lost response and a 503, repeated "
            "with the same key, so the carrier ends up with exactly one shipment per order (the README says a "
            "repeated key returns the first shipment).",
            ["test_hidden_keyed_create.py"],
        ),
        _hidden(
            workspace,
            "unsafe_posts_are_not_repeated",
            "A create without a key and POST /pickups are sent once when they time out: the README says every "
            "such call creates a new shipment or books a new pickup, so a repeat could duplicate it.",
            ["test_hidden_unsafe_posts.py"],
        ),
        _no_real_waiting(workspace),
        _no_swallowing_catch_all(workspace),
        _scope_and_dependencies(workspace),
        _existing_tests_untouched(workspace),
        _new_tests_fail_on_original_code(workspace),
        checklib.command_succeeds(
            "test_suite_passes", "The repository's own test suite passes.", workspace, PYTEST
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
            checklib.PYTEST_RUN,
        ),
    ]


def _hidden(workspace, name: str, description: str, files: list[str]) -> Check:
    return checklib.command_succeeds(
        name, description, workspace, [*PYTEST, *[f"{HIDDEN_TESTS}/{file}" for file in files]]
    )


def _no_real_waiting(workspace) -> Check:
    name = "waiting_is_injectable_and_never_real_in_tests"
    description = (
        "The pauses between attempts go through the client's existing `sleep` argument (the README and the "
        "existing tests inject it), and neither the hidden tests nor the project's own tests really sleep."
    )
    hidden = _hidden(workspace, name, description, ["test_hidden_waiting.py"])
    completed = workspace.run([sys.executable, "-c", SLEEP_WATCHER])
    match = re.search(r"REAL_SLEEP_SECONDS=([\d.]+)", completed.stdout)
    slept = float(match.group(1)) if match else None
    own_suite = Check(
        name,
        description,
        slept is not None and slept < MAX_REAL_SLEEP_S,
        f"the project's tests really slept {slept}s (limit {MAX_REAL_SLEEP_S}s)",
    )
    return checklib.all_of(name, description, hidden, own_suite)


def _no_swallowing_catch_all(workspace) -> Check:
    name = "no_new_catch_all_that_swallows"
    description = (
        "No new bare `except:` or `except Exception/BaseException` handler in shipsync/ lacks a `raise`: a "
        "catch-all that returns, logs or continues would hide real failures behind the retry."
    )
    offending = []
    for path in workspace.changed_files():
        if not (path.startswith("shipsync/") and path.endswith(".py")):
            continue
        known = {ast.dump(handler) for handler in _catch_alls(workspace.read_base(path))}
        for handler in _catch_alls(workspace.read(path)):
            if ast.dump(handler) not in known and not any(
                isinstance(n, ast.Raise) for n in ast.walk(handler)
            ):
                offending.append(f"{path}:{handler.lineno}")
    return Check(
        name, description, not offending, f"swallowing catch-alls at {offending}" if offending else "none"
    )


def _catch_alls(source: str | None) -> list[ast.ExceptHandler]:
    try:
        tree = ast.parse(source or "")
    except SyntaxError:
        return []
    return [
        node for node in ast.walk(tree) if isinstance(node, ast.ExceptHandler) and _names_catch_all(node.type)
    ]


def _names_catch_all(exception_type: ast.expr | None) -> bool:
    if exception_type is None:
        return True
    names = exception_type.elts if isinstance(exception_type, ast.Tuple) else [exception_type]
    return any(isinstance(name, ast.Name) and name.id in BROAD_EXCEPTIONS for name in names)


def _scope_and_dependencies(workspace) -> Check:
    name = "only_expected_files_changed_and_no_new_dependency"
    description = (
        "Only the client, its error and transport modules, new modules under shipsync/, tests and the README "
        "changed (the sync job, the CLI, the models and pyproject.toml stay as they are), and no retry or HTTP "
        "library is imported: the request is about the client, and the project has no dependencies."
    )
    new_modules = [
        path
        for path in workspace.changed_files()
        if path.startswith("shipsync/") and workspace.read_base(path) is None
    ]
    scope = checklib.only_these_files_changed(name, description, workspace, EDITABLE_FILES + new_modules)
    libraries = checklib.no_added_lines(name, description, workspace, RETRY_LIBRARIES, ["*.py"])
    return checklib.all_of(name, description, scope, libraries)


def _existing_tests_untouched(workspace) -> Check:
    name = "existing_tests_not_loosened"
    description = (
        "No line of the existing test modules was changed or removed, apart from import lines that grow to "
        "bring in new names; tests may only be added."
    )
    edited = {
        path: [line for line in workspace.removed_lines(path) if not IMPORT_LINE.match(line)]
        for path in EXISTING_TEST_FILES
    }
    edited = {path: lines for path, lines in edited.items() if lines}
    return Check(
        name,
        description,
        not edited,
        f"changed or removed lines: {edited}" if edited else "tests only added to",
    )


def _new_tests_fail_on_original_code(workspace) -> Check:
    name = "regression_tests_fail_on_original_code"
    description = (
        "The agent added at least one test, and the added tests do not all pass on the untouched client: they "
        "pin the new retry behavior."
    )
    new_tests = checklib._new_python_tests(workspace, ["tests/*.py"])
    if not new_tests:
        return Check(name, description, False, "no new test function was added")
    files = sorted({node_id.split("::")[0] for node_id in new_tests})
    with workspace.base_with(files) as base:
        completed = base.run([*PYTEST, *new_tests])
    # Exit 1: some failed. Exit 2 or 4: the tests cannot even be collected without the new code, which also
    # counts. Exit 5 means the ids matched no tests, which proves nothing.
    passed = completed.returncode not in (0, PYTEST_NO_TESTS)
    evidence = f"{len(new_tests)} new tests on the original code: exit {completed.returncode}"
    return Check(name, description, passed, evidence)
