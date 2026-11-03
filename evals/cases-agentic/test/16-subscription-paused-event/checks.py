"""Checks for 16-subscription-paused-event: a new variant of a union consumed by three exhaustive switches."""

import re

import checklib
from checklib import NODE_TEST, Check

SELFTEST_COMMANDS = ["npm test", "npx tsc --noEmit"]
TEST_RUN = r"^(node\s+--test|npm\s+(run\s+)?test\b)"
NEW_EVENT = "subscription_paused"
EVENT_DECLARATION = re.compile(rf"type:\s*[\"']{NEW_EVENT}[\"']")
EVENT_TYPE = re.compile(r"type:\s*[\"']([a-z_]+)[\"']")
SWITCH_SITES = ["src/subscription.ts", "src/audit.ts", "src/notifier.ts"]
SOURCE_AND_TESTS = ["src/*.ts", "test/*.test.ts"]
EXISTING_TESTS = ["test/subscription.test.ts", "test/audit.test.ts", "test/notifier.test.ts"]
# The ways to make the compiler stop complaining without handling the case. The first is looked for in code
# (comments and string contents removed): the type `any` in any position, a double cast, a non-null assertion.
TYPE_ESCAPE = re.compile(r"(?<![.\w])any\b|\bas\s+unknown\s+as\b|[\w)\]]!(?!=)")
TS_DIRECTIVE = re.compile(r"@ts-(ignore|expect-error|nocheck)")
STRING_LITERAL = re.compile(r"\"(?:\\.|[^\"\\])*\"|'(?:\\.|[^'\\])*'|`(?:\\.|[^`\\])*`")
DECLARED_PAUSE_TYPE = re.compile(
    rf"(?:interface|type)\s+(\w+)\b[^{{}}]*\{{[^{{}}]*type:\s*[\"']{NEW_EVENT}[\"']"
)
# What a test for each of the three places has to call.
TESTED_SITES = {
    "reducer": r"\b(replay|reduceSubscription)\(",
    "audit log": r"\bserializeAuditEntry\(",
    "notifier": r"\bnotificationsFor\(",
}


def setup(repo):
    checklib.install_node_toolchain(repo, ["typescript@7.0.2", "@types/node@26.6.6"])


def checks(workspace, transcript) -> list[Check]:
    return [
        checklib.command_succeeds(
            "reducer_handles_pause",
            "The state reducer pauses only active subscriptions, keeps payment events and a second pause from "
            "moving a paused one, and clears the resume date when a paused subscription is canceled.",
            workspace,
            [*NODE_TEST, ".hidden/hidden_reducer.ts"],
        ),
        checklib.command_succeeds(
            "audit_log_records_pause",
            "The audit log line for a pause has the resume date, then the quoted reason, and the other lines "
            "are unchanged.",
            workspace,
            [*NODE_TEST, ".hidden/hidden_audit.ts"],
        ),
        checklib.command_succeeds(
            "notifier_handles_pause",
            "A pause emails the customer the resume date and nobody else, and the other events keep their emails.",
            workspace,
            [*NODE_TEST, ".hidden/hidden_notifier.ts"],
        ),
        checklib.command_succeeds(
            "typecheck_passes",
            "The TypeScript type check passes for the sources, the repository's tests and the hidden tests, "
            "which build typed pause events and read the new state field.",
            workspace,
            ["node", "node_modules/typescript/bin/tsc", "--noEmit", "-p", ".hidden/tsconfig.json"],
        ),
        _exhaustiveness_kept(workspace),
        _no_type_escapes(workspace),
        _event_defined_once(workspace),
        _only_requested_event_added(workspace),
        checklib.only_these_files_changed(
            "only_expected_files_changed",
            "Only the event definitions, the three places that consume events, and tests changed; "
            "assertNever, package and config files were not touched.",
            workspace,
            ["src/events.ts", *SWITCH_SITES, "test/*.test.ts"],
        ),
        _existing_tests_untouched(workspace),
        _tests_cover_all_sites(workspace),
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


def _no_type_escapes(workspace) -> Check:
    name = "no_type_escape_hatches"
    description = (
        "No added line uses `any`, `as unknown as`, a non-null assertion or a @ts-ignore style comment to get "
        "past the compiler (comments and string contents are not code and are ignored)."
    )
    offending = []
    for path in workspace.changed_files():
        if not checklib._matches_any(path, SOURCE_AND_TESTS):
            continue
        for line in workspace.added_lines(path):
            if TS_DIRECTIVE.search(line) or TYPE_ESCAPE.search(_code_of_line(line)):
                offending.append(f"{path}: {line.strip()}")
    return Check(name, description, not offending, checklib._quoted(offending) or "no escape hatches")


def _code_of_line(line: str) -> str:
    """One added line without string contents and comments (a line inside a block comment starts with `*`)."""
    if line.strip().startswith(("//", "/*", "*")):
        return ""
    without_strings = STRING_LITERAL.sub('""', line)
    return re.sub(r"/\*.*?\*/|//.*$", "", without_strings)


def _exhaustiveness_kept(workspace) -> Check:
    name = "exhaustiveness_guard_kept"
    description = (
        "Each of the three switches handles the new event with its own case, gained no `default` branch, and "
        "still ends in assertNever, as the README and the existing code do, so the compiler keeps flagging "
        "unhandled events."
    )
    problems = []
    for path in SWITCH_SITES:
        before, after = _code(workspace.read_base(path)), _code(workspace.read(path))
        if f'case "{NEW_EVENT}"' not in after:
            problems.append(f'{path} has no case "{NEW_EVENT}"')
        if len(re.findall(r"\bdefault\s*:", after)) > len(re.findall(r"\bdefault\s*:", before)):
            problems.append(f"{path} gained a default branch")
        if len(re.findall(r"\bassertNever\(", after)) < len(re.findall(r"\bassertNever\(", before)):
            problems.append(f"{path} uses assertNever less than before")
    return Check(name, description, not problems, "; ".join(problems) or f"checked {SWITCH_SITES}")


def _event_defined_once(workspace) -> Check:
    name = "event_defined_once"
    description = (
        "The pause event is declared once, in src/events.ts and as part of SubscriptionEvent (under any type "
        "name); no other source file declares a second copy of its shape."
    )
    problems = []
    events = _code(workspace.read("src/events.ts"))
    declarations = len(EVENT_DECLARATION.findall(events))
    if declarations != 1:
        problems.append(f"src/events.ts declares the event {declarations} times")
    for path in workspace.changed_files():
        if path.startswith("src/") and path != "src/events.ts":
            source = _code(workspace.read(path))
            if EVENT_DECLARATION.search(source) or re.search(r"(interface|type)\s+\w*Paus", source):
                problems.append(f"{path} declares its own pause event type")
    union = re.search(r"export type SubscriptionEvent\s*=(.*?)(?=\n\S|\Z)", events, re.DOTALL)
    declared = DECLARED_PAUSE_TYPE.search(events)
    in_union = union is not None and (
        EVENT_DECLARATION.search(union.group(1)) is not None
        or (declared is not None and re.search(rf"\b{declared.group(1)}\b", union.group(1)) is not None)
    )
    if not in_union:
        problems.append("the pause event is not part of the SubscriptionEvent union")
    return Check(name, description, not problems, "; ".join(problems) or "one declaration, in the union")


def _existing_tests_untouched(workspace) -> Check:
    name = "existing_tests_not_loosened"
    description = (
        "No existing test line was changed or removed; tests may only be added (an import line may be extended "
        "to import more names)."
    )
    edited = {path: _without_imports(workspace.removed_lines(path)) for path in EXISTING_TESTS}
    edited = {path: lines for path, lines in edited.items() if lines}
    evidence = f"changed or removed lines: {edited}" if edited else "tests only added to"
    return Check(name, description, not edited, evidence)


def _without_imports(lines: list[str]) -> list[str]:
    return [line for line in lines if not line.lstrip().startswith("import ")]


def _tests_cover_all_sites(workspace) -> Check:
    name = "tests_cover_all_three_sites"
    description = (
        "The prompt asks for tests: new test code mentions the pause event and exercises the reducer, the "
        "audit serializer and the notifier."
    )
    added = [
        line
        for path in workspace.changed_files()
        if checklib._matches_any(path, ["test/*.test.ts"])
        for line in workspace.added_lines(path)
    ]
    text = "\n".join(added)
    missing = [site for site, call in TESTED_SITES.items() if not re.search(call, text)]
    if NEW_EVENT not in text:
        missing.append(f"the event {NEW_EVENT}")
    return Check(
        name, description, not missing, f"added tests miss: {missing}" if missing else "all three covered"
    )


def _only_requested_event_added(workspace) -> Check:
    name = "only_the_requested_event_added"
    description = "The prompt asks for one new event; no other event type (a resume event, say) was added to src/events.ts."
    before = set(EVENT_TYPE.findall(_code(workspace.read_base("src/events.ts"))))
    after = set(EVENT_TYPE.findall(_code(workspace.read("src/events.ts"))))
    extra = sorted(after - before - {NEW_EVENT})
    evidence = f"event types added besides {NEW_EVENT}: {extra}" if extra else f"only {NEW_EVENT} is new"
    return Check(name, description, not extra, evidence)


def _code(source: str | None) -> str:
    """Source text without `//` and `/* */` comments."""
    return "\n".join(checklib._code_lines(source))
