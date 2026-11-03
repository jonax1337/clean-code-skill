"""Checks for 13-refund-command-handler: add a RefundOrder command to an order service with strong conventions."""

import os
import re

import checklib
from checklib import JAVA_TEST, Check

SELFTEST_COMMANDS = ["java tools/RunTests.java"]
HIDDEN_DIR = ".hidden"
JUNIT_LAUNCHER = "lib/junit-platform-console-standalone.jar"
MAIN_DIR = "src/main/java/"
TEST_DIR = "src/test/java/"
# Existing files a refund feature may legitimately touch: the order and its status (to record a refund or say
# which statuses allow one), the one place that registers handlers, the error codes and the validator (to extend
# them), and the README's command table.
EXTENDABLE_FILES = {
    "README.md",
    "src/main/java/shop/Order.java",
    "src/main/java/shop/OrderStatus.java",
    "src/main/java/shop/OrderServices.java",
    "src/main/java/shop/ErrorCode.java",
    "src/main/java/shop/Validator.java",
}
MIN_NEW_TESTS = 2  # an accepted and a rejected refund at least; two parameterized tests may cover every rule
MONEY_AS_FLOATING_POINT = r"\b(double|float|Double|Float)\b|\b(double|float)Value\(|new BigDecimal\(\s*-?\d*\.\d|Math\.(round|floor|ceil)\("
CONSOLE_OUTPUT = r"System\.(out|err)\b|printStackTrace\("
# What the other handlers delegate to the Validator: blank text, missing values, decimal places.
HAND_ROLLED_VALIDATION = r"\.isBlank\(\)|\.scale\(\)|[!=]=\s*null"
THROWS = r"\bthrow\b|\bcatch\b"
# What a handler must contain, as patterns over its code; `Result::ok` counts like `Result.ok(`.
HANDLER_PARTS = {
    "CommandHandler": r"\bimplements\s+CommandHandler\s*<",
    "Validator": r"\bnew\s+Validator\s*\(",
    "Result.failure": r"\bResult\s*(\.|::)\s*failure\b",
    "Result.ok": r"\bResult\s*(\.|::)\s*ok\b",
}
# Text blocks, string and character literals, block and line comments: what is not code.
JAVA_NON_CODE = re.compile(
    r'"""[\s\S]*?"""|"(?:\\.|[^"\\\n])*"|\'(?:\\.|[^\'\\\n])\'|/\*[\s\S]*?\*/|//[^\n]*'
)
_hidden_builds: dict[str, object] = {}


def setup(repo):
    checklib.install_java_toolchain(repo)


def checks(workspace, transcript) -> list[Check]:
    return [
        _hidden_test_class(
            workspace,
            "refund_follows_business_rules",
            "Only shipped or delivered orders are refunded; refunds add up and never exceed what was paid "
            "(not the order total); the exact remaining amount works at any scale; failures change nothing; "
            "the command is reachable through the bus.",
            "RefundOrderRulesTest",
        ),
        _hidden_test_class(
            workspace,
            "refund_rejects_bad_input",
            "A blank or missing order id and a missing, zero, negative or three-decimal amount come back as "
            "INVALID_INPUT failures, before the order is looked up, without throwing.",
            "RefundOrderInputTest",
        ),
        _hidden_test_class(
            workspace,
            "refund_money_is_exact",
            "Repeated small refunds and very large amounts add up to the cent, which floating point cannot do.",
            "RefundOrderMoneyTest",
        ),
        _only_expected_files_changed(workspace),
        _existing_tests_untouched(workspace),
        _new_tests_cover_the_command(workspace),
        checklib.command_succeeds(
            "test_suite_passes", "The repository's own test suite passes.", workspace, JAVA_TEST
        ),
        _handler_follows_the_pattern(workspace),
        checklib.no_added_lines(
            "money_stays_decimal",
            "No double or float and no BigDecimal built from a floating-point literal: the codebase keeps money "
            "in BigDecimal.",
            workspace,
            MONEY_AS_FLOATING_POINT,
            ["src/*"],
        ),
        checklib.no_added_lines(
            "no_console_output",
            "The change prints nothing to the console: the service reports problems through Result.",
            workspace,
            CONSOLE_OUTPUT,
            ["src/*"],
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


def _hidden_test_class(workspace, name: str, description: str, test_class: str) -> Check:
    """Compile the hidden tests once per workspace, then run one test class of them with the JUnit launcher."""
    key = str(workspace.root)
    if key not in _hidden_builds:
        _hidden_builds[key] = workspace.run([*JAVA_TEST, HIDDEN_DIR])
    build = _hidden_builds[key]
    if "Compilation of" in build.stderr:
        return Check(name, description, False, _tail(build.stderr))
    class_path = os.pathsep.join(["build/extra-classes", "build/classes"])
    launcher = [
        *("java", "-jar", JUNIT_LAUNCHER, "execute"),
        *("--class-path", class_path, "--select-class", f"shop.{test_class}"),
        *("--disable-banner", "--disable-ansi-colors", "--details=summary"),
    ]
    completed = workspace.run(launcher)
    output = completed.stdout + completed.stderr
    ran = re.search(r"\b[1-9]\d* tests successful", output) is not None
    return Check(name, description, completed.returncode == 0 and ran, _tail(output))


def _only_expected_files_changed(workspace) -> Check:
    name = "only_expected_files_changed"
    description = (
        "New files are only sources or tests; the only existing files touched are the order, its status and error codes, "
        "the validator, the handler registration, the README and tests. The other handlers, the bus, the result "
        "type and the repository stay as they are."
    )
    unexpected = []
    for path in workspace.changed_files():
        if workspace.read_base(path) is not None:
            allowed = path in EXTENDABLE_FILES or path.startswith(TEST_DIR)
        else:
            allowed = path.startswith((MAIN_DIR, TEST_DIR)) and path.endswith(".java")
        if not allowed:
            unexpected.append(path)
    evidence = f"unexpected changes: {unexpected}" if unexpected else f"changed: {workspace.changed_files()}"
    return Check(name, description, not unexpected, evidence)


def _existing_tests_untouched(workspace) -> Check:
    name = "existing_tests_not_loosened"
    description = "No line of a test that existed before was changed or removed; tests may only be added."
    edited = {
        path: workspace.removed_lines(path)
        for path in workspace.changed_files()
        if path.startswith(TEST_DIR) and workspace.read_base(path) is not None
    }
    edited = {path: lines for path, lines in edited.items() if lines}
    evidence = f"changed or removed lines: {edited}" if edited else "tests only added to"
    return Check(name, description, not edited, evidence)


def _new_tests_cover_the_command(workspace) -> Check:
    name = "new_tests_cover_refund"
    description = (
        f"At least {MIN_NEW_TESTS} test methods that mention RefundOrder were added to the project's tests; the "
        "rules in the request (accepted status, rejected status, amount limit) need that many at the minimum."
    )
    added = [
        line
        for path in workspace.changed_files()
        if path.startswith(TEST_DIR) and path.endswith(".java")
        for line in workspace.added_lines(path)
    ]
    test_count = sum(1 for line in added if re.match(r"\s*@(Parameterized)?Test\b", line))
    mentions_refund = any("RefundOrder" in line for line in added)
    evidence = f"{test_count} test methods added; tests mention RefundOrder: {mentions_refund}"
    return Check(name, description, test_count >= MIN_NEW_TESTS and mentions_refund, evidence)


def _handler_follows_the_pattern(workspace) -> Check:
    name = "handler_follows_the_pattern"
    description = (
        "A new *Handler class implements CommandHandler like the existing ones, validates through the existing "
        "Validator instead of its own checks, and reports failures as Result values instead of throwing "
        "(judged on the code, not on comments or strings)."
    )
    handlers = [
        path
        for path in workspace.changed_files()
        if path.startswith(MAIN_DIR) and path.endswith("Handler.java") and workspace.read_base(path) is None
    ]
    if not handlers:
        return Check(name, description, False, "no new *Handler class was added under src/main/java")
    problems = []
    for path in handlers:
        source = workspace.read(path) or ""
        code = _strip_comments_and_strings(source)
        for label, required in HANDLER_PARTS.items():
            if not re.search(required, code):
                problems.append(f"{path}: does not use {label}")
        problems += [
            f"{path}: {line.strip()}"
            for line in code.splitlines()
            if re.search(HAND_ROLLED_VALIDATION, line) or re.search(THROWS, line)
        ]
    return Check(name, description, not problems, "\n".join(problems[:12]) or f"checked {handlers}")


def _strip_comments_and_strings(source: str) -> str:
    """Java source with comments and string or character literals blanked out, line structure kept."""
    return JAVA_NON_CODE.sub(lambda match: re.sub(r"[^\n]", " ", match.group(0)), source)


def _tail(output: str) -> str:
    return "\n".join(output.strip().splitlines()[-checklib.EVIDENCE_LINES :])
