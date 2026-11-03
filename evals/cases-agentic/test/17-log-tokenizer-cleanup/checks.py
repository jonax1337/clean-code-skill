"""Checks for 17-log-tokenizer-cleanup: make a zero-copy log tokenizer readable without allocating or changing it."""

from __future__ import annotations

import re
import tempfile

import checklib
from agentic import Transcript, Workspace
from checklib import Check

SELFTEST_COMMANDS = ["cargo test"]

HIDDEN_MANIFEST = ".hidden/Cargo.toml"
CARGO_TEST_RUN = r"^cargo\s+test\b"
RUST_TEST_NAME = re.compile(r"#\[test\]\s*\n\s*(?:pub\s+)?fn\s+(\w+)")
# The files around the tokenizer that are allowed to allocate: the CLI, the consumer, the error type, `unescape`.
NOT_THE_TOKENIZER = {"src/main.rs", "src/lib.rs", "src/stats.rs", "src/escape.rs", "src/error.rs"}
ALLOCATING_CODE = re.compile(
    r"\.to_string\(|\.to_owned\(|\.to_vec\(|\.into_boxed|\.repeat\(|\.join\(|\.concat\(|\.to_(lower|upper)case\(|"
    r"\bString\b|\bformat!|\bvec!|\bVec\b|\.collect\b|\bBox\b|\bCow\b|\bRc\b|\bArc\b"
)
# A reviewer's limit for "one huge function": the fixture's longest function has more than twice this.
MAX_FUNCTION_LINES = 60
MAX_BLANK_TESTS = 3
BLANK_TEST = re.compile(r"' '.*'\\t'|'\\t'.*' '")
# Comments, string literals (raw ones too) and char/byte literals, so braces inside them do not count.
RUST_LITERAL = re.compile(
    r"""//[^\n]*|/\*.*?\*/|b?r(#*)".*?"\1|b?"(?:\\.|[^"\\])*"|"""
    r"""b?'(?:\\u\{[0-9a-fA-F_]+\}|\\x[0-9a-fA-F]{2}|\\.|[^\\'])'""",
    re.DOTALL,
)
RUST_PRINT = re.compile(r"\b(e?print(ln)?)!")
TESTS_PASSED = re.compile(r"test result: ok\. (\d+) passed")


def checks(workspace: Workspace, transcript: Transcript) -> list[Check]:
    results = [
        _hidden_tests(
            "token_stream_unchanged",
            "For about 20 groups of edge cases (blanks, empty values, escapes, unterminated quotes and timestamps, stray quotes, empty keys, non-ASCII text) the tokens and the error with its byte position are exactly what the original produced, and nothing follows an error.",
            workspace,
            "tokens",
        ),
        _hidden_tests(
            "public_api_unchanged",
            "A test crate that uses `tokenize`, `Tokens`, `Token`, `LexError`, `Stats` and `unescape` as before (signatures, variants, derives, `Clone` iterator, tokens outliving the iterator) still compiles and passes.",
            workspace,
            "api",
        ),
        _hidden_tests(
            "tokenizing_does_not_allocate",
            "With a counting global allocator, tokenizing 4000 valid and 2000 malformed lines performs zero heap allocations.",
            workspace,
            "alloc",
        ),
        _no_allocating_code(workspace),
        _functions_are_short(workspace),
        _blank_test_not_repeated(workspace),
        checklib.only_these_files_changed(
            "only_expected_files",
            "Only Rust sources, tests and the README changed; Cargo.toml and Cargo.lock were left alone, so no dependency was added.",
            workspace,
            ["src/*.rs", "tests/*.rs", "README.md"],
        ),
        checklib.command_succeeds(
            "suite_passes",
            "The project's own test suite passes.",
            workspace,
            ["cargo", "test"],
        ),
        _other_tests_kept(workspace),
    ]
    if _clippy_installed(workspace):
        results.append(_clippy_clean(workspace))
    results += [
        _clean_diff(workspace),
        checklib.ran_after_last_edit(
            "tests_run_after_edit",
            "The agent ran `cargo test` successfully after its last edit.",
            transcript,
            CARGO_TEST_RUN,
        ),
    ]
    return results


def _clean_diff(workspace: Workspace) -> Check:
    """Like `checklib.clean_diff`, which reads a Rust attribute such as `#[derive(Debug)]` as a commented-out Python list."""
    description = "The diff has no `dbg!`, new print macros in files that did not print before, commented-out code or narrating comments."
    offending = []
    for path in workspace.changed_files():
        prints_by_design = RUST_PRINT.search(workspace.read_base(path) or "") is not None
        for line in workspace.added_lines(path):
            stripped = line.strip()
            if re.search(r"\bdbg!", line) or (RUST_PRINT.search(line) and not prints_by_design):
                offending.append(f"debug output in {path}: {stripped}")
            elif stripped.startswith("//") and checklib._is_commented_out_code(stripped):
                offending.append(f"commented-out code in {path}: {stripped}")
            elif checklib.NARRATING_COMMENT.search(line) and not checklib.TEST_FILE.search(path):
                offending.append(f"narrating comment in {path}: {stripped}")
    return Check("clean_diff", description, not offending, checklib._quoted(offending) or "clean")


def _hidden_tests(name: str, description: str, workspace: Workspace, test_target: str) -> Check:
    """Run one test file of the hidden crate; at least one test must run and all must pass."""
    completed = workspace.run(["cargo", "test", "--manifest-path", HIDDEN_MANIFEST, "--test", test_target])
    output = completed.stdout + completed.stderr
    passed = sum(int(count) for count in TESTS_PASSED.findall(output))
    evidence = f"exit {completed.returncode}, {passed} tests passed\n" + "\n".join(
        output.strip().splitlines()[-14:]
    )
    return Check(name, description, completed.returncode == 0 and passed > 0, evidence)


def _no_allocating_code(workspace: Workspace) -> Check:
    description = (
        "The tokenizer's code (every source file except main, lib, stats, escape and error; unit tests excluded) has no "
        "`to_string`, `String`, `format!`, `vec!`, `Vec`, `collect`, `Box`, `Cow` or similar. The README says the "
        "tokenizer borrows from the line and does not allocate, and the prompt says it must not get slower."
    )
    offending = [
        f"{path}: {line.strip()}"
        for path in _source_files(workspace)
        if path not in NOT_THE_TOKENIZER
        for line in checklib._code_lines(_without_unit_tests(workspace.read(path)))
        if ALLOCATING_CODE.search(line)
    ]
    return Check(
        "no_allocating_code_in_tokenizer",
        description,
        not offending,
        checklib._quoted(offending) or "no allocating constructs in the tokenizer",
    )


def _functions_are_short(workspace: Workspace) -> Check:
    description = (
        f"The longest function in the sources is at most {MAX_FUNCTION_LINES} lines and shorter than the longest one "
        "before. The request is to break up one huge function, and the fixture's `next` is more than twice that long."
    )
    now = _longest_function(workspace, base=False)
    before = _longest_function(workspace, base=True)
    passed = now[1] <= MAX_FUNCTION_LINES and now[1] < before[1]
    evidence = f"longest function now: {now[0]} ({now[1]} lines); before: {before[0]} ({before[1]} lines)"
    return Check("functions_are_short", description, passed, evidence)


def _blank_test_not_repeated(workspace: Workspace) -> Check:
    description = (
        f"The test for a space or tab appears on at most {MAX_BLANK_TESTS} code lines of the tokenizer. The fixture "
        "writes it out six times, and the prompt asks for code that is easier to maintain."
    )
    lines = [
        f"{path}: {line.strip()}"
        for path in _source_files(workspace)
        if path not in NOT_THE_TOKENIZER
        for line in checklib._code_lines(_without_unit_tests(workspace.read(path)))
        if BLANK_TEST.search(line)
    ]
    evidence = f"{len(lines)} lines test for a space or tab (limit {MAX_BLANK_TESTS})" + checklib._quoted(
        lines
    )
    return Check("blank_test_not_repeated", description, len(lines) <= MAX_BLANK_TESTS, evidence)


def _other_tests_kept(workspace: Workspace) -> Check:
    description = "Every test of the fixture is still there; none was deleted or renamed to make things pass."
    before = _test_names(workspace, base=True)
    missing = sorted(before - _test_names(workspace, base=False))
    evidence = f"missing tests: {missing}" if missing else f"all {len(before)} tests are still present"
    return Check("existing_tests_kept", description, not missing and bool(before), evidence)


def _clippy_installed(workspace: Workspace) -> bool:
    return workspace.run(["cargo", "clippy", "--version"]).returncode == 0


def _clippy_clean(workspace: Workspace) -> Check:
    description = (
        "`cargo clippy --all-targets -- -D warnings` reports nothing (the fixture is clean), and no lint was "
        "silenced with an `allow` attribute."
    )
    with tempfile.TemporaryDirectory(prefix="cc-target-", ignore_cleanup_errors=True) as target:
        completed = workspace.run(
            ["cargo", "clippy", "--all-targets", "--target-dir", target, "--", "-D", "warnings"]
        )
    output = completed.stdout + completed.stderr
    silenced = checklib.no_added_lines("", "", workspace, r"#!?\[allow\(", ["src/*.rs", "tests/*.rs"])
    passed = completed.returncode == 0 and silenced.passed
    evidence = f"clippy exit {completed.returncode}; allow attributes: {silenced.evidence}\n" + "\n".join(
        output.strip().splitlines()[-10:]
    )
    return Check("clippy_clean", description, passed, evidence)


def _longest_function(workspace: Workspace, base: bool) -> tuple[str, int]:
    longest = ("none", 0)
    for path in _source_files(workspace, base=base):
        source = workspace.read_base(path) if base else workspace.read(path)
        for name, lines in _rust_function_lengths(source):
            if lines > longest[1]:
                longest = (f"{path}::{name}", lines)
    return longest


def _rust_function_lengths(source: str | None) -> list[tuple[str, int]]:
    """Name and line count of every function outside the unit-test module, braces in literals ignored."""
    code = _mask_literals(_without_unit_tests(source))
    lengths = []
    for match in re.finditer(r"\bfn\s+(\w+)", code):
        opening = _body_start(code, match.end())
        closing = _matching_brace(code, opening) if opening is not None else None
        if closing is not None:
            lengths.append((match.group(1), code.count("\n", match.start(), closing) + 1))
    return lengths


def _mask_literals(code: str) -> str:
    return RUST_LITERAL.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), code)


def _body_start(code: str, position: int) -> int | None:
    """Index of the `{` that opens a function body, or None for a declaration that ends with `;`."""
    depth = 0
    for index in range(position, len(code)):
        char = code[index]
        if char in "([":
            depth += 1
        elif char in ")]":
            depth -= 1
        elif depth == 0 and char == ";":
            return None
        elif depth == 0 and char == "{":
            return index
    return None


def _matching_brace(code: str, opening: int) -> int | None:
    depth = 0
    for index in range(opening, len(code)):
        depth += {"{": 1, "}": -1}.get(code[index], 0)
        if depth == 0:
            return index
    return None


def _without_unit_tests(source: str | None) -> str:
    return (source or "").split("#[cfg(test)]", 1)[0]


def _source_files(workspace: Workspace, base: bool = False) -> list[str]:
    if base:
        listing = workspace.git("ls-tree", "-r", "--name-only", "eval-base").splitlines()
    else:
        listing = [
            path.relative_to(workspace.root).as_posix() for path in (workspace.root / "src").rglob("*.rs")
        ]
    return sorted(path for path in listing if path.startswith("src/") and path.endswith(".rs"))


def _test_names(workspace: Workspace, base: bool) -> set[str]:
    paths = [*_source_files(workspace, base=base)]
    if base:
        listing = workspace.git("ls-tree", "-r", "--name-only", "eval-base").splitlines()
    else:
        listing = [
            path.relative_to(workspace.root).as_posix() for path in (workspace.root / "tests").rglob("*.rs")
        ]
    paths += [path for path in listing if path.startswith("tests/") and path.endswith(".rs")]
    names: set[str] = set()
    for path in paths:
        source = workspace.read_base(path) if base else workspace.read(path)
        names |= set(RUST_TEST_NAME.findall(source or ""))
    return names
