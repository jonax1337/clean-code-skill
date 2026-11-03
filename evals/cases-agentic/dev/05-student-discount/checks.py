"""Checks for 05-student-discount: one new customer type with a 10% rate that never stacks with loyalty."""

import re

import checklib
from checklib import JAVA_TEST, Check

SELFTEST_COMMANDS = ["java tools/RunTests.java"]
MAIN_SOURCES = "src/main/java/*"
TEST_SOURCES = "src/test/java/*"
EXISTING_TESTS = [
    "src/test/java/pricing/MoneyTest.java",
    "src/test/java/pricing/DiscountPolicyTest.java",
    "src/test/java/pricing/PriceCalculatorTest.java",
    "src/test/java/pricing/ReceiptFormatterTest.java",
]
MAX_NEW_MAIN_FILES = 1
TESTS_RAN = r"\b[1-9]\d* tests successful"
ABSTRACTION = r"\b(interface|abstract\s+class|sealed|permits)\b|\b(class|record|enum)\s+\w*(Factory|Registry|Strategy)\b"
NOT_MONEY_SAFE = (
    r"\b(double|float|Double|Float)\b|RoundingMode|setScale\(|MathContext|Math\.round|\.(double|float)Value\("
    r"|\b\d*\.\d+[dDfF]\b|(new BigDecimal|BigDecimal\.valueOf)\(\s*\d*\.\d"
)
PRICE_ARITHMETIC = r"\.(multiply|subtract|divide)\("
# The library prints nothing, so any added output call is a debugging leftover (checklib's list is for Python/JS).
JAVA_DEBUG_OUTPUT = r"\bSystem\.(out|err)\b|\.printStackTrace\("
# checklib.JAVA_TEST_RUN, but a Windows shell may also write the path with a backslash.
JAVA_TEST_RUN = r"^java\s+(\S*[/\\])?RunTests\.java\b"
STRING_LITERAL = re.compile(r'"(?:\\.|[^"\\])*"')
BLOCK_COMMENT = re.compile(r"/\*.*?\*/")


def setup(repo):
    checklib.install_java_toolchain(repo)


def checks(workspace, transcript) -> list[Check]:
    return [
        _hidden_tests(
            workspace,
            "student_discount_applies",
            "A STUDENT without loyalty points gets 10% off in the quote, the catalog unit price and the receipt, "
            "with the discount rounded half up like every other amount.",
            "student",
        ),
        _hidden_tests(
            workspace,
            "larger_discount_wins_without_stacking",
            "The prompt: a student who is also a loyalty member gets whichever discount is bigger, never both; "
            "silver loyalty loses to 10%, gold loyalty (15%) wins, employees are unaffected.",
            "combination",
        ),
        _hidden_tests(
            workspace,
            "existing_behavior_unchanged",
            "Regular and employee customers get exactly the same rates, quotes, catalog prices and receipts as before.",
            "existing",
        ),
        checklib.only_these_files_changed(
            "only_expected_files_changed",
            "Only library sources, tests and the README changed; no build files, resources or configuration "
            "were added for a single rule.",
            workspace,
            [MAIN_SOURCES, TEST_SOURCES, "README.md"],
        ),
        _existing_tests_untouched(workspace),
        checklib.command_succeeds(
            "test_suite_passes", "The repository's own test suite passes.", workspace, JAVA_TEST
        ),
        checklib.added_test_mentions(
            "student_tests_added",
            "The prompt adds behavior, so the agent added at least one test that uses CustomerType.STUDENT.",
            workspace,
            [TEST_SOURCES],
            "STUDENT",
        ),
        _no_new_abstraction_layers(workspace),
        _no_added_code(
            "money_stays_bigdecimal_with_one_rounding",
            "The codebase keeps money in BigDecimal and rounds only in Money.round; the change adds no double, "
            "float or floating-point literal, RoundingMode, setScale or Math.round of its own (comments and "
            "strings do not count).",
            workspace,
            NOT_MONEY_SAFE,
            [MAIN_SOURCES],
        ),
        _price_calculation_not_duplicated(workspace),
        _clean_diff(workspace),
        checklib.ran_after_last_edit(
            "tests_run_after_last_edit",
            "After its last edit the agent ran the test suite and it passed.",
            transcript,
            JAVA_TEST_RUN,
        ),
    ]


def _code_without_comments(line: str) -> str:
    """One added line with block comments, `//` comments and string contents removed; comment-only lines are empty."""
    stripped = line.strip()
    if stripped.startswith(("//", "/*", "*")):
        return ""
    return re.sub(r"//.*$", "", BLOCK_COMMENT.sub("", STRING_LITERAL.sub('""', line)))


def _no_added_code(name: str, description: str, workspace, pattern: str, paths: list[str]) -> Check:
    """Like checklib.no_added_lines, but a word in a comment or a string (`no double discount`) is not code."""
    offending = [
        f"{path}: {line.strip()}"
        for path in workspace.changed_files()
        if checklib._matches_any(path, paths)
        for line in workspace.added_lines(path)
        if re.search(pattern, _code_without_comments(line))
    ]
    return Check(name, description, not offending, checklib._quoted(offending) or "no matching added code")


def _clean_diff(workspace) -> Check:
    name = "clean_diff"
    description = (
        "The diff has no debug output (System.out, System.err, printStackTrace), commented-out code or narrating "
        "comments."
    )
    generic = checklib.clean_diff(name, description, workspace)
    output = _no_added_code(name, description, workspace, JAVA_DEBUG_OUTPUT, [MAIN_SOURCES, TEST_SOURCES])
    return checklib.all_of(name, description, generic, output)


def _hidden_tests(workspace, name: str, description: str, folder: str) -> Check:
    completed = workspace.run([*JAVA_TEST, f".hidden/{folder}"])
    output = completed.stdout + completed.stderr
    ran = re.search(TESTS_RAN, output) is not None
    evidence = f"exit {completed.returncode}, tests ran: {ran}\n{checklib._tail(output)}"
    return Check(name, description, completed.returncode == 0 and ran, evidence)


def _existing_tests_untouched(workspace) -> Check:
    name = "existing_tests_not_loosened"
    description = (
        "No existing test line was changed or removed; tests may only be added. An import line may change, "
        "for example to a wildcard: it cannot loosen a test."
    )
    edited = {
        path: [line for line in workspace.removed_lines(path) if not line.lstrip().startswith("import ")]
        for path in EXISTING_TESTS
    }
    edited = {path: lines for path, lines in edited.items() if lines}
    evidence = f"changed or removed lines: {edited}" if edited else "tests only added to"
    return Check(name, description, not edited, evidence)


def _no_new_abstraction_layers(workspace) -> Check:
    name = "no_new_abstraction_layers"
    description = (
        f"One rate rule in an existing method needs no interface, abstract class, sealed hierarchy or "
        f"factory/registry/strategy type, and at most {MAX_NEW_MAIN_FILES} new main source file."
    )
    declarations = _no_added_code(name, description, workspace, ABSTRACTION, [MAIN_SOURCES])
    new_files = [
        path
        for path in workspace.changed_files()
        if path.startswith("src/main/") and workspace.read_base(path) is None
    ]
    within_limit = len(new_files) <= MAX_NEW_MAIN_FILES
    evidence = f"{declarations.evidence}; new main files: {new_files}"
    return Check(name, description, declarations.passed and within_limit, evidence)


def _price_calculation_not_duplicated(workspace) -> Check:
    name = "price_calculation_not_duplicated"
    description = (
        "Choosing the rate is DiscountPolicy's job and PriceCalculator already turns a rate into a price for "
        "both quote and catalog: the change adds no price arithmetic to the main sources and does not "
        "special-case customer types in PriceCalculator."
    )
    arithmetic = _no_added_code(name, description, workspace, PRICE_ARITHMETIC, [MAIN_SOURCES])
    special_case = _no_added_code(
        name,
        description,
        workspace,
        r"(?i)student|CustomerType",
        ["src/main/java/pricing/PriceCalculator.java"],
    )
    return checklib.all_of(name, description, arithmetic, special_case)
