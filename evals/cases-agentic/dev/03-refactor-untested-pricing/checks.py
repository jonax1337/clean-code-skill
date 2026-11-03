from pathlib import Path

from agentic import Transcript, Workspace
from checklib import (
    NODE_TEST,
    NODE_TESTS_RAN,
    TSC,
    Check,
    all_of,
    characterization_tests_pass_on_base,
    clean_diff,
    command_succeeds,
    count_at_most,
    install_node_toolchain,
    literals_only_in_constants,
    no_match_in_code,
    only_these_files_changed,
    ran_after_last_edit,
)

TARGET = "src/pricing.ts"
TESTS = ["test/*.test.ts", "src/*.test.ts", "src/**/*.test.ts"]
NODE_TOOLCHAIN = ["typescript@7.0.2", "@types/node@26.6.6"]
SELFTEST_COMMANDS = ["npm test", "npx tsc --noEmit"]
TEST_COMMAND = r"^(node\s+--test|npm\s+(run\s+)?test\b|npm\s+t\b)"
TYPECHECK_COMMAND = r"^((npx|pnpm|yarn)\s+)?tsc\b|^npm\s+run\s+typecheck\b|^node\s+\S*tsc\b"
# Function declarations and arrow functions bound to a name, including async and generic ones.
FUNCTION_DEFINITION = (
    r"^\s*(export\s+)?(async\s+)?function\b|"
    r"^\s*(export\s+)?const\s+\w+\s*(:[^=]+)?=\s*(async\s+)?(<[^>]*>\s*)?(\(|\w+\s*=>)"
)


def setup(repo: Path) -> None:
    install_node_toolchain(repo, NODE_TOOLCHAIN)


def checks(workspace: Workspace, transcript: Transcript) -> list[Check]:
    return [
        command_succeeds(
            "hidden_behavior",
            "Behavior is preserved for every input the old code handled: member rates, missing category, coupon "
            "after the discount and floored at 0, ignored coupons, no clamp without a coupon, rounding (hidden tests).",
            workspace,
            [*NODE_TEST, ".hidden/hidden_pricing.ts"],
        ),
        all_of(
            "callers_compatible",
            "The callers are untouched and the project still type-checks.",
            only_these_files_changed("files", "", workspace, [TARGET, *TESTS]),
            command_succeeds("typecheck", "", workspace, TSC),
        ),
        no_match_in_code(
            "any_replaced", "`any` is replaced by a type for the product parameter.", workspace, TARGET, r"\bany\b"
        ),
        literals_only_in_constants(
            "magic_numbers_named",
            "The member rates, the coupon code and the coupon amount are named, not bare literals in the logic.",
            workspace,
            TARGET,
            r"\b0?\.95?\b|\b10\b|[\"']SAVE10[\"']",
        ),
        characterization_tests_pass_on_base(
            "characterization_tests",
            "Tests for `getPrice` are added, and they run and pass on the original code, so they pin the old behavior.",
            workspace,
            TESTS,
            NODE_TEST,
            NODE_TESTS_RAN,
        ),
        all_of(
            "no_over_engineering",
            "No classes, strategies or extra layers: no `class` and at most four functions in the file.",
            no_match_in_code("no_class", "", workspace, TARGET, r"\bclass\b"),
            count_at_most("functions", "", workspace, TARGET, FUNCTION_DEFINITION, limit=4),
        ),
        command_succeeds(
            "suite_green", "The full test suite passes, including the agent's own tests.", workspace, NODE_TEST
        ),
        clean_diff(
            "clean_diff", "No debug output, commented-out code or comments that narrate the edit.", workspace
        ),
        all_of(
            "verified",
            "The agent ran the tests and the type checker after its last edit.",
            ran_after_last_edit("tests", "", transcript, TEST_COMMAND),
            ran_after_last_edit("typecheck", "", transcript, TYPECHECK_COMMAND),
        ),
    ]
