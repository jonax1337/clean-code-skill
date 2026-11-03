"""Checks for 22-checkout-refactor: split up process_order without changing what it does."""

import ast

import checklib
from checklib import PYTEST, Check

SELFTEST_COMMANDS = ["python -m pytest -q"]
MAX_FUNCTION_LINES = 30
EXISTING_TESTS = ["tests/conftest.py", "tests/test_checkout.py", "tests/test_api.py"]
HIDDEN_TESTS = ".hidden"


def checks(workspace, transcript) -> list[Check]:
    return [
        checklib.command_succeeds(
            "totals_unchanged",
            "Prices, tax rounding per line, discounts and shipping come out exactly as before for orders that "
            "exercise rounding, coupons, VIP customers and the free-shipping boundary.",
            workspace,
            [*PYTEST, f"{HIDDEN_TESTS}/test_hidden_totals.py"],
        ),
        checklib.command_succeeds(
            "failures_and_side_effects_unchanged",
            "Rejections, stock reservation and release order, charge timing, coupon redemption, logging and "
            "swallowed receipt errors behave exactly as before.",
            workspace,
            [*PYTEST, f"{HIDDEN_TESTS}/test_hidden_failures.py", f"{HIDDEN_TESTS}/test_hidden_side_effects.py"],
        ),
        checklib.only_these_files_changed(
            "only_expected_files_changed",
            "Only the checkout module, the pricing helpers it uses and tests changed; callers and models are untouched.",
            workspace,
            ["shop/checkout.py", "shop/pricing.py", "tests/*.py"],
        ),
        _existing_tests_untouched(workspace),
        _new_tests_describe_old_behavior(workspace),
        checklib.command_succeeds(
            "test_suite_passes", "The repository's own test suite passes.", workspace, PYTEST
        ),
        _process_order_is_split(workspace),
        _public_interface_untouched(workspace),
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


def _existing_tests_untouched(workspace) -> Check:
    name = "existing_tests_not_loosened"
    description = "No existing test line was changed or removed; tests may only be added."
    edited = {path: workspace.removed_lines(path) for path in EXISTING_TESTS}
    edited = {path: lines for path, lines in edited.items() if lines}
    return Check(name, description, not edited, f"changed or removed lines: {edited}" if edited else "tests only added to")


def _new_tests_describe_old_behavior(workspace) -> Check:
    name = "new_tests_pass_on_original_code"
    description = "Any test the agent added passes on the untouched original code, so it pins existing behavior."
    changed = [path for path in workspace.changed_files() if path.startswith("tests/") and path.endswith(".py")]
    if not changed:
        return Check(name, description, True, "no tests were added or changed")
    return checklib.characterization_tests_pass_on_base(
        name, description, workspace, ["tests/*.py"], PYTEST, r"\d+ passed"
    )


def _process_order_is_split(workspace) -> Check:
    name = "no_function_longer_than_thirty_lines"
    description = f"No function in shop/checkout.py is longer than {MAX_FUNCTION_LINES} lines, so process_order is broken up."
    tree = ast.parse(workspace.read("shop/checkout.py") or "")
    lengths = {
        node.name: node.end_lineno - node.lineno + 1
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef)
    }
    too_long = {function: length for function, length in lengths.items() if length > MAX_FUNCTION_LINES}
    return Check(name, description, not too_long, f"too long: {too_long}" if too_long else f"function lengths: {lengths}")


def _public_interface_untouched(workspace) -> Check:
    name = "public_interface_and_refund_untouched"
    description = (
        "process_order keeps its name, parameters and return type, and refund_order, which was not part of the "
        "request, is unchanged."
    )
    before = _signature(workspace.read_base("shop/checkout.py"), "process_order")
    after = _signature(workspace.read("shop/checkout.py"), "process_order")
    refund = checklib.python_definitions_unchanged(name, description, workspace, "shop/checkout.py", ["refund_order"])
    passed = before is not None and before == after and refund.passed
    return Check(name, description, passed, f"signature unchanged: {before == after}; {refund.evidence}")


def _signature(source, function):
    tree = ast.parse(source or "")
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == function:
            return ast.dump(node.args) + ast.dump(node.returns) if node.returns else ast.dump(node.args)
    return None
