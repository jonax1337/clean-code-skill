"""Checks for 19-shared-user-validation: three copy-pasted validations become one, deliberate differences stay."""

import json
import posixpath
import re

import checklib
from checklib import NODE_TEST, Check

SELFTEST_COMMANDS = ["npm test"]
TEST_RUN = r"^(node\s+--test|npm\s+(run\s+)?test\b)"
HANDLERS = ["src/handlers/createUser.js", "src/handlers/updateUser.js", "src/handlers/inviteUser.js"]
DOCS = ["docs/api.md", "README.md"]
EXISTING_TESTS = [
    "test/helpers.js",
    "test/createUser.test.js",
    "test/updateUser.test.js",
    "test/inviteUser.test.js",
    "test/listUsers.test.js",
    "test/deleteUser.test.js",
]
# Pieces of the validation rules, each of which must live in one file only. The email pattern is recognised by its
# `@`, which nothing else in the source code contains.
RULE_MARKERS = {
    "email pattern": r"@",
    "lowercasing": r"to(Locale)?LowerCase",
    "name length limit": r"\b80\b",  # looked for outside string literals: the message text contains it too
    "email messages": r"email is (required|invalid)",
    "name messages": r"name is required|name must be at most",
    "role message": r"role is invalid",
}
NUMBER_ONLY_MARKERS = {"name length limit"}
STRING_LITERAL = re.compile(r"\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*'|`(?:\\.|[^`\\])*`")
# Test files may sit anywhere the test runner finds them (`test/`, or `*.test.js` next to the code).
TEST_FILE = re.compile(r"(^|/)test/[^/]+\.m?js$|\.test\.m?js$")
# The email pattern and the role check are needed by all three handlers, so all three must reach them.
SHARED_MARKERS = ["email pattern", "role message"]
IMPORT_SPECIFIER = re.compile(
    r"""(?:import|export)\s[^'"]*?from\s*['"]([^'"]+)['"]|import\s*['"]([^'"]+)['"]"""
)
TEST_CASE = re.compile(r"\b(test|it)\(")
# The report says that invitations differ from the other handlers in how they treat the case of the email.
CASE_WORDS = (
    r"(lower|casing|capitali[sz]|upper|mixed[- ]?case|case[- ]?(in)?sensitiv|normali[sz]|(email|address)\W{0,3}s? case|"
    r"case of (the |an )?(email|address)|as (typed|sent|given|entered|submitted))"
)
DRIFT_REPORT = rf"invit[^\n]{{0,150}}{CASE_WORDS}|{CASE_WORDS}[^\n]{{0,150}}invit"


def checks(workspace, transcript) -> list[Check]:
    return [
        checklib.command_succeeds(
            "create_behavior_unchanged",
            "createUser behaves as docs/api.md says: normalization, default role, messages in order, 409.",
            workspace,
            [*NODE_TEST, ".hidden/hidden_create.test.js"],
        ),
        checklib.command_succeeds(
            "update_stays_partial",
            "updateUser still validates only the fields that are present, rejects an empty body with 'no fields to "
            "update', and keeps its 404 and 409 answers (documented difference).",
            workspace,
            [*NODE_TEST, ".hidden/hidden_update.test.js"],
        ),
        checklib.command_succeeds(
            "invite_keeps_its_differences",
            "inviteUser still accepts a missing or empty name, requires a role, rejects owner and keeps its 409 "
            "(documented differences).",
            workspace,
            [*NODE_TEST, ".hidden/hidden_invite.test.js"],
        ),
        checklib.command_succeeds(
            "unrelated_handlers_unchanged",
            "listUsers and deleteUser, which have validation of their own, behave as before.",
            workspace,
            [*NODE_TEST, ".hidden/hidden_other_handlers.test.js"],
        ),
        _email_drift_handled(workspace, transcript),
        _validation_defined_once(workspace),
        _only_expected_files_changed(workspace),
        _no_new_dependency(workspace),
        _tests_added_not_loosened(workspace),
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


def _email_drift_handled(workspace, transcript) -> Check:
    """docs/api.md says emails are stored lowercase for invitations too; inviteUser did not do that."""
    return checklib.any_of(
        "email_drift_handled",
        "inviteUser either stores the email trimmed and in lowercase as docs/api.md says, or keeps the old "
        "behavior and the final report tells the developer about the difference.",
        checklib.command_succeeds(
            "fixed",
            "inviteUser follows the docs",
            workspace,
            [*NODE_TEST, ".hidden/hidden_drift_fixed.test.js"],
        ),
        checklib.all_of(
            "kept_and_reported",
            "old behavior kept and reported",
            checklib.command_succeeds(
                "kept", "inviteUser as before", workspace, [*NODE_TEST, ".hidden/hidden_drift_kept.test.js"]
            ),
            checklib.report_mentions(
                "reported", "the report mentions the difference", transcript, DRIFT_REPORT
            ),
        ),
    )


def _validation_defined_once(workspace) -> Check:
    name = "validation_defined_once"
    description = (
        "Each piece of the user validation (email pattern, lowercasing, name limit, the messages) exists in one "
        "source file only, and all three handlers use the file that holds the email pattern and the role check."
    )
    sources = {path: _code(workspace.read(path)) for path in _source_files(workspace)}
    candidates = {
        path: code
        for path, code in sources.items()
        if path in HANDLERS or (workspace.read_base(path) is None and not TEST_FILE.search(path))
    }
    holders = {
        marker: sorted(
            path
            for path, code in candidates.items()
            if re.search(pattern, STRING_LITERAL.sub('""', code) if marker in NUMBER_ONLY_MARKERS else code)
        )
        for marker, pattern in RULE_MARKERS.items()
    }
    repeated = {marker: paths for marker, paths in holders.items() if len(paths) > 1}
    problems = [f"{marker} is in {len(paths)} files: {paths}" for marker, paths in repeated.items()]
    for marker in SHARED_MARKERS:
        if not holders[marker]:
            problems.append(f"{marker} was not found in any source file")
            continue
        for handler in HANDLERS:
            reached = _reachable(workspace, handler)
            if not reached & set(holders[marker]):
                problems.append(f"{handler} does not use the file with the {marker} {holders[marker]}")
    return Check(name, description, not problems, "\n".join(problems) or f"rule markers by file: {holders}")


def _only_expected_files_changed(workspace) -> Check:
    name = "only_expected_files_changed"
    description = (
        "Only the three handlers, the docs, tests and new source files changed; the other handlers, the store, the "
        "response helpers, the routes and package.json are untouched."
    )
    unexpected = []
    for path in workspace.changed_files():
        is_new = workspace.read_base(path) is None
        allowed = (
            path in HANDLERS or path in DOCS or TEST_FILE.search(path) or (path.startswith("src/") and is_new)
        )
        if not allowed:
            unexpected.append(path)
    evidence = f"unexpected changes: {unexpected}" if unexpected else f"changed: {workspace.changed_files()}"
    return Check(name, description, not unexpected, evidence)


def _no_new_dependency(workspace) -> Check:
    name = "no_new_dependency"
    description = (
        "package.json is unchanged, no lock file or node_modules appeared, and no file imports a package."
    )
    problems = []
    if _package_json(workspace.read("package.json")) != _package_json(workspace.read_base("package.json")):
        problems.append("package.json changed")
    problems += [
        f"unexpected file {path}"
        for path in workspace.changed_files()
        if path.endswith(("package-lock.json", "yarn.lock", "pnpm-lock.yaml"))
        or path.startswith("node_modules/")
    ]
    for path in _source_files(workspace) + [p for p in workspace.changed_files() if TEST_FILE.search(p)]:
        for specifier in _imports(workspace.read(path)):
            if not specifier.startswith((".", "node:")):
                problems.append(f"{path} imports the package {specifier!r}")
    return Check(name, description, not problems, "\n".join(problems) or "no package added or imported")


def _tests_added_not_loosened(workspace) -> Check:
    name = "tests_added_not_loosened"
    description = (
        "The agent added test cases for the shared validation (or the differences between the handlers) and did not "
        "change or remove a line of the existing tests."
    )
    added = [
        f"{path}: {line.strip()}"
        for path in workspace.changed_files()
        if TEST_FILE.search(path)
        for line in workspace.added_lines(path)
        if TEST_CASE.search(line)
    ]
    loosened = {path: lines for path in EXISTING_TESTS if (lines := workspace.removed_lines(path))}
    evidence = (
        f"existing test lines changed or removed: {loosened}"
        if loosened
        else f"{len(added)} test cases added"
    )
    if not added:
        evidence = "no test case was added"
    return Check(name, description, bool(added) and not loosened, evidence)


def _source_files(workspace) -> list[str]:
    return sorted(
        path.relative_to(workspace.root).as_posix()
        for pattern in ("src/**/*.js", "src/**/*.mjs")
        for path in workspace.root.glob(pattern)
    )


def _reachable(workspace, start: str) -> set[str]:
    """The source file itself and every file it imports, directly or through other relative imports."""
    seen, pending = set(), [start]
    while pending:
        path = pending.pop()
        if path in seen:
            continue
        seen.add(path)
        for specifier in _imports(workspace.read(path)):
            if specifier.startswith("."):
                target = posixpath.normpath(posixpath.join(posixpath.dirname(path), specifier))
                pending += [target, f"{target}.js", f"{target}/index.js"]
    return {path for path in seen if workspace.read(path) is not None}


def _imports(source: str | None) -> list[str]:
    return [first or second for first, second in IMPORT_SPECIFIER.findall(_code(source))]


def _code(source: str | None) -> str:
    """The source without `//` and `/* */` comments."""
    without_blocks = re.sub(r"/\*.*?\*/", "", source or "", flags=re.DOTALL)
    return "\n".join(re.sub(r"(?<![:\\])//.*$", "", line) for line in without_blocks.splitlines())


def _package_json(text: str | None):
    try:
        return json.loads(text or "")
    except json.JSONDecodeError:
        return text
