"""Deterministic checks for the agentic track. Every check carries the evidence a human needs to audit it."""

from __future__ import annotations

import ast
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.request
from dataclasses import dataclass
from fnmatch import fnmatchcase
from pathlib import Path

from agentic import Transcript, Workspace
from harness import CACHE_DIR

PYTEST = [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider"]
PYTEST_TESTS_FAILED = (
    1  # pytest's exit code when tests ran and some failed; 2 is a collection error, 5 no tests
)
# Patterns for ran_after_last_edit match the start of one shell segment, after `cd x &&`, `(` or `VAR=1`.
PYTEST_RUN = r"^((uv|poetry|pipenv)\s+run\s+)?(\S*python\S*(\s+-[A-Za-z]+)*\s+-m\s+)?pytest\b"
NODE_TEST = ["node", "--test"]
NODE_TESTS_RAN = r"\btests [1-9]\d*\b"  # "# tests 3" (TAP) or "ℹ tests 3" (spec)
TSC = ["node", "node_modules/typescript/bin/tsc", "--noEmit"]
NODE_CACHE_DIR = CACHE_DIR / "node"
# Java fixtures build without Maven or Gradle: `java tools/RunTests.java [extra test dir]` (see cases-agentic/_java).
JAVA_TEST = ["java", "tools/RunTests.java"]
JAVA_TEST_RUN = r"^java\s+(\S*[/\\])?RunTests\.java\b"  # a Windows shell may write tools\RunTests.java
JUNIT_VERSION = "1.11.4"
JAVA_CACHE_DIR = CACHE_DIR / "java"
JAVA_SUPPORT_DIR = Path(__file__).resolve().parent / "cases-agentic" / "_java"
EVIDENCE_LINES = 12

DEBUG_OUTPUT = re.compile(r"\bprint\(|\bbreakpoint\(|\bpdb\b|console\.log\(|\bdebugger\b|\bdbg!\(")
# Comments that tell the story of the edit instead of explaining the code.
NARRATING_COMMENT = re.compile(
    r"(^|\s)(#|//)\s.*\b(fixed(\s+(the|a|an|this|it|bug|issue|crash|problem)\b|:|$)|changed (to|from)\b|"
    r"updated (to|for)\b|refactored\b|previously\b|no longer\b|now (uses|handles|returns|includes|calls|supports)\b)",
    re.IGNORECASE,
)
PYTHON_CODE_NODES = (
    ast.Assign, ast.AugAssign, ast.Return, ast.Import, ast.ImportFrom, ast.For, ast.While, ast.If,
    ast.With, ast.Try, ast.FunctionDef, ast.ClassDef, ast.Call,
)  # fmt: skip
JS_CODE_LINE = re.compile(
    r"^((const|let|var|return|throw|import|export|function)\b.*[;{}()=]|[\w.$\[\]]+\s*[-+]?=\s*[^=].*;|"
    r"[\w.$]+\(.*\);|(if|for|while)\s*\(.*\)\s*\{?)\s*$"
)
TEST_FILE = re.compile(r"(^|/)tests?/|(^|/)test_[^/]*$|[._-]test\.\w+$")
NOT_A_TEST_RUN = re.compile(r"--help\b|--version\b|--collect-only\b")


@dataclass(frozen=True)
class Check:
    name: str
    description: str
    passed: bool
    evidence: str


def command_succeeds(name: str, description: str, workspace: Workspace, command: list[str]) -> Check:
    completed = workspace.run(command)
    return Check(name, description, completed.returncode == 0, _tail(completed.stdout + completed.stderr))


def only_these_files_changed(name: str, description: str, workspace: Workspace, allowed: list[str]) -> Check:
    changed = workspace.changed_files()
    unexpected = [path for path in changed if not _matches_any(path, allowed)]
    evidence = f"unexpected changes: {unexpected}" if unexpected else f"changed: {changed}"
    return Check(name, description, not unexpected, evidence)


def python_definitions_unchanged(
    name: str, description: str, workspace: Workspace, path: str, definitions: list[str]
) -> Check:
    before = _python_definitions(workspace.read_base(path))
    after = _python_definitions(workspace.read(path))
    changed = [definition for definition in definitions if before.get(definition) != after.get(definition)]
    evidence = f"changed in {path}: {changed}" if changed else f"unchanged in {path}: {definitions}"
    return Check(name, description, not changed, evidence)


def at_most_removed_lines(name: str, description: str, workspace: Workspace, path: str, limit: int) -> Check:
    removed = workspace.removed_lines(path)
    evidence = f"{len(removed)} existing lines of {path} changed or removed" + _quoted(removed)
    return Check(name, description, len(removed) <= limit, evidence)


def python_calls(name: str, description: str, workspace: Workspace, path: str, functions: list[str]) -> Check:
    called = _python_called_names(workspace.read(path))
    missing = [function for function in functions if function not in called]
    evidence = f"not called in {path}: {missing}" if missing else f"{path} calls {functions}"
    return Check(name, description, not missing, evidence)


def no_added_lines(
    name: str, description: str, workspace: Workspace, pattern: str, paths: list[str]
) -> Check:
    offending = [
        f"{path}: {line.strip()}"
        for path in workspace.changed_files()
        if _matches_any(path, paths)
        for line in workspace.added_lines(path)
        if re.search(pattern, line)
    ]
    return Check(name, description, not offending, _quoted(offending) or "no matching added lines")


def no_match_in_code(name: str, description: str, workspace: Workspace, path: str, pattern: str) -> Check:
    """The pattern must not occur in the file's code; comments do not count."""
    offending = [line.strip() for line in _code_lines(workspace.read(path)) if re.search(pattern, line)]
    return Check(
        name, description, not offending, _quoted(offending) or f"no match for {pattern!r} in {path}"
    )


def count_at_most(
    name: str, description: str, workspace: Workspace, path: str, pattern: str, limit: int
) -> Check:
    matches = [line.strip() for line in _code_lines(workspace.read(path)) if re.search(pattern, line)]
    return Check(
        name, description, len(matches) <= limit, f"{len(matches)} matches (limit {limit})" + _quoted(matches)
    )


def literals_only_in_constants(
    name: str, description: str, workspace: Workspace, path: str, literal: str
) -> Check:
    """Bare literals may appear only in constant declarations or lookup-table entries, not in the logic."""
    constant_line = re.compile(
        r"^\s*(export\s+)?const\s+\w+\s*(:[^=]+)?=\s*(?!\(|async\b|function\b)|^\s*[\"']?[\w-]+[\"']?\s*:\s*\S"
    )
    offending = [line.strip() for line in _code_lines(workspace.read(path)) if re.search(literal, line)]
    offending = [line for line in offending if not constant_line.match(line)]
    return Check(name, description, not offending, _quoted(offending) or "all literals are named")


def clean_diff(name: str, description: str, workspace: Workspace) -> Check:
    offending = []
    for path in workspace.changed_files():
        # In a file that already printed before (a CLI, a script), new output calls are its job, not debug leftovers.
        prints_by_design = DEBUG_OUTPUT.search(workspace.read_base(path) or "") is not None
        for line in workspace.added_lines(path):
            if DEBUG_OUTPUT.search(line) and not prints_by_design:
                offending.append(f"debug output in {path}: {line.strip()}")
            elif _is_commented_out_code(line):
                offending.append(f"commented-out code in {path}: {line.strip()}")
            elif NARRATING_COMMENT.search(line) and not TEST_FILE.search(path):
                offending.append(f"narrating comment in {path}: {line.strip()}")
    return Check(name, description, not offending, _quoted(offending) or "clean")


def regression_tests_fail_on_base(
    name: str, description: str, workspace: Workspace, test_paths: list[str]
) -> Check:
    """The pytest tests the agent added must fail on the untouched fixture: run, and fail, not error."""
    new_tests = _new_python_tests(workspace, test_paths)
    if not new_tests:
        return Check(name, description, False, "no new test function was added")
    files = sorted({node_id.split("::")[0] for node_id in new_tests})
    with workspace.base_with(files) as base:
        completed = base.run([*PYTEST, *new_tests])
    evidence = f"{new_tests} on the original code: exit {completed.returncode}\n{_tail(completed.stdout)}"
    return Check(name, description, completed.returncode == PYTEST_TESTS_FAILED, evidence)


def characterization_tests_pass_on_base(
    name: str,
    description: str,
    workspace: Workspace,
    test_paths: list[str],
    runner: list[str],
    ran_pattern: str,
) -> Check:
    """The tests the agent added or changed must run and pass on the untouched fixture: they pin the old behavior."""
    tests = [
        path for path in workspace.changed_files() if _matches_any(path, test_paths) and workspace.read(path)
    ]
    if not tests:
        return Check(name, description, False, "no test file was added or changed")
    with workspace.base_with(tests) as base:
        completed = base.run([*runner, *tests])
    output = completed.stdout + completed.stderr
    ran = re.search(ran_pattern, output) is not None
    evidence = f"{tests} on the original code: exit {completed.returncode}, tests ran: {ran}\n{_tail(output)}"
    return Check(name, description, completed.returncode == 0 and ran, evidence)


def added_test_mentions(
    name: str, description: str, workspace: Workspace, test_paths: list[str], text: str
) -> Check:
    hits = [
        f"{path}: {line.strip()}"
        for path in workspace.changed_files()
        if _matches_any(path, test_paths)
        for line in workspace.added_lines(path)
        if text in line
    ]
    return Check(name, description, bool(hits), _quoted(hits[:3]) or f"no added test line mentions {text!r}")


def ran_after_last_edit(name: str, description: str, transcript: Transcript, pattern: str) -> Check:
    """After its last file edit, the agent ran a command matching the pattern, and the command succeeded."""
    commands = transcript.commands_after_last_edit()
    runs = [(command, failed) for command, failed in commands if _runs(command, pattern)]
    passing = [command for command, failed in runs if not failed]
    if passing:
        return Check(name, description, True, passing[-1][-300:])
    if runs:
        return Check(name, description, False, f"ran but failed: {runs[-1][0][-300:]}")
    shown = [command[-120:] for command, _ in commands]
    return Check(name, description, False, f"bash commands after the last edit: {shown or 'none'}")


def report_mentions(name: str, description: str, transcript: Transcript, pattern: str) -> Check:
    match = re.search(rf".{{0,80}}({pattern}).{{0,80}}", transcript.final_message, re.IGNORECASE)
    return Check(
        name, description, match is not None, match.group(0) if match else "not mentioned in the report"
    )


def all_of(name: str, description: str, *checks: Check) -> Check:
    return Check(name, description, all(check.passed for check in checks), _combined_evidence(checks))


def any_of(name: str, description: str, *checks: Check) -> Check:
    return Check(name, description, any(check.passed for check in checks), _combined_evidence(checks))


def install_node_toolchain(repo: Path, packages: list[str]) -> None:
    """Give the fixture a `node_modules` like a real checkout has, from a cache filled once with npm."""
    modules = NODE_CACHE_DIR / "node_modules"
    if not modules.is_dir():
        _fill_node_cache(packages)
    shutil.copytree(modules, repo / "node_modules")


def install_java_toolchain(repo: Path) -> None:
    """Give a Java fixture the JUnit console launcher in `lib/` and the test runner in `tools/`."""
    jar_name = f"junit-platform-console-standalone-{JUNIT_VERSION}.jar"
    cached = JAVA_CACHE_DIR / jar_name
    if not cached.exists():
        url = f"https://repo1.maven.org/maven2/org/junit/platform/junit-platform-console-standalone/{JUNIT_VERSION}/{jar_name}"
        JAVA_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        partial = cached.with_name(f"{jar_name}.{os.getpid()}.partial")
        with urllib.request.urlopen(url, timeout=60) as response:
            partial.write_bytes(response.read())
        os.replace(partial, cached)
    (repo / "lib").mkdir(exist_ok=True)
    shutil.copyfile(cached, repo / "lib" / "junit-platform-console-standalone.jar")
    (repo / "tools").mkdir(exist_ok=True)
    shutil.copyfile(JAVA_SUPPORT_DIR / "RunTests.java", repo / "tools" / "RunTests.java")


def _fill_node_cache(packages: list[str]) -> None:
    """Install into a scratch prefix and move it into place, so a crash or a parallel run never leaves half a cache."""
    npm = shutil.which("npm")
    if npm is None:
        raise RuntimeError("npm is needed once to fill the Node toolchain cache")
    NODE_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    scratch = Path(tempfile.mkdtemp(prefix="install-", dir=NODE_CACHE_DIR))
    subprocess.run(
        [npm, "install", "--prefix", str(scratch), "--no-audit", "--no-fund", *packages], check=True
    )
    try:
        os.replace(scratch / "node_modules", NODE_CACHE_DIR / "node_modules")
    except OSError:
        pass  # another run filled the cache first; its copy is as good as ours
    shutil.rmtree(scratch, ignore_errors=True)


def _new_python_tests(workspace: Workspace, test_paths: list[str]) -> list[str]:
    """pytest node ids of test functions that exist now but did not exist in the fixture."""
    node_ids = []
    for path in workspace.changed_files():
        if _matches_any(path, test_paths) and workspace.read(path):
            before = set(_python_test_ids(workspace.read_base(path)))
            node_ids += [
                f"{path}::{test}" for test in _python_test_ids(workspace.read(path)) if test not in before
            ]
    return node_ids


def _python_test_ids(source: str | None) -> list[str]:
    tree = _parse_python(source)
    ids = []
    for node in tree.body if tree else []:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test"):
            ids.append(node.name)
        elif isinstance(node, ast.ClassDef) and node.name.startswith("Test"):
            ids += [
                f"{node.name}::{item.name}"
                for item in node.body
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and item.name.startswith("test")
            ]
    return ids


def _python_definitions(source: str | None) -> dict[str, str]:
    tree = _parse_python(source)
    definitions = (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
    return {
        node.name: ast.dump(node) for node in (tree.body if tree else []) if isinstance(node, definitions)
    }


def _python_called_names(source: str | None) -> set[str]:
    tree = _parse_python(source)
    names = set()
    for node in ast.walk(tree) if tree else []:
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            names.add(node.func.id)
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
            names.add(node.func.attr)
    return names


def _parse_python(source: str | None) -> ast.Module | None:
    try:
        return ast.parse(source or "")
    except SyntaxError:
        return None


def _is_commented_out_code(line: str) -> bool:
    stripped = line.strip()
    if stripped.startswith(("#[", "#!")):
        return False  # a Rust attribute (#[derive(..)], #![allow(..)]) or a shebang, not a comment
    if stripped.startswith("#"):
        return _is_python_code(stripped.lstrip("#").strip())
    if stripped.startswith("//"):
        return JS_CODE_LINE.match(stripped.lstrip("/").strip()) is not None
    return False


def _is_python_code(text: str) -> bool:
    """True when a comment's text parses as a Python statement, not as prose such as "Note: see RFC 1234"."""
    for candidate in (text, f"{text}\n    pass"):
        tree = _parse_python(candidate) if candidate.strip() else None
        if tree is not None and any(isinstance(node, PYTHON_CODE_NODES) for node in ast.walk(tree)):
            return True
    return False


def _code_lines(source: str | None) -> list[str]:
    """Lines of a C-style source file without `//` and `/* */` comments."""
    without_blocks = re.sub(r"/\*.*?\*/", "", source or "", flags=re.DOTALL)
    return [re.sub(r"//.*$", "", line) for line in without_blocks.splitlines()]


def _runs(command: str, pattern: str) -> bool:
    """Whether one segment of a shell command starts with the program the pattern describes."""
    segments = (re.sub(r"^[\s({]*(\w+=\S*\s+)*", "", part) for part in re.split(r"&&|\|\||[;|\n]", command))
    return any(re.search(pattern, segment) and not NOT_A_TEST_RUN.search(segment) for segment in segments)


def _matches_any(path: str, patterns: list[str]) -> bool:
    return any(fnmatchcase(path, pattern) for pattern in patterns)


def _combined_evidence(checks: tuple[Check, ...]) -> str:
    return "\n".join(
        f"[{'pass' if check.passed else 'fail'}] {check.name}: {check.evidence}" for check in checks
    )


def _quoted(lines: list[str]) -> str:
    return "".join(f"\n  {line}" for line in lines[:EVIDENCE_LINES])


def _tail(output: str) -> str:
    return "\n".join(output.strip().splitlines()[-EVIDENCE_LINES:])
