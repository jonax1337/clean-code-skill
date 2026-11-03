"""Checks for 04-cleanup-report-module: clean up a grown report module without changing a cent of its output."""

import re
from fnmatch import fnmatchcase

import checklib
from checklib import NODE_TEST, NODE_TESTS_RAN, Check

SELFTEST_COMMANDS = ["npm test"]
TEST_RUN = r"^(node\s+--test|npm\s+(run\s+)?test\b)"
REPORT = "src/report.js"
CALLERS = ["src/export.js", "src/digest.js", "src/sales.js", "src/cli.js"]
# The prompt says nobody can read the module; the original buildReport is about 150 lines. 40 lines is roughly one
# screen and leaves room for a long table or a render function, while forcing the three regional blocks apart.
MAX_FUNCTION_LINES = 40
# The money rendering, the name truncation and the cent rounding each existed once per region (three blocks plus
# formatMoney). After consolidation they may still appear a couple of times, but not once per region.
MAX_TO_FIXED = 2
MAX_ELLIPSES = 1
MAX_MATH_ROUND = 4
# The net amount (units times unit price) starts the discount math, which also existed once per region.
MAX_NET_MULTIPLICATIONS = 2
NET_MULTIPLICATION = re.compile(r"\bunits\s*\*\s*(?:\w+\.)?unitPrice\b|\bunitPrice\s*\*\s*(?:\w+\.)?units\b")
# Literals that carry a business rule: VAT rates, bulk factor and threshold, large-order limit, column widths and
# the cut-off length of a product name (20 characters, 19 plus the ellipsis).
MAGIC_NUMBERS = re.compile(
    r"(?<![\d.])0?\.(19|95|2)(?!\d)|\b10000\b|[<>]=?\s*100\b|pad(End|Start)\(\s*\d|"
    r"length\s*[<>]=?\s*2[01]\b|(slice|substring)\(0,\s*19\)"
)
# Any module the agent adds under src/ counts as source, at any depth; a test placed next to the code does not.
SOURCE_FILE = re.compile(r"src/(?!.*\.test\.js$).+\.js")
FUNCTION_START = re.compile(
    r"^\s*(export\s+)?(async\s+)?function\b|=>\s*\{\s*$|\bfunction\s*\w*\s*\(.*\)\s*\{\s*$|"
    r"^\s*(async\s+)?(?!if\b|for\b|while\b|switch\b|catch\b)\w+\s*\([^)]*\)\s*\{\s*$"
)


def checks(workspace, transcript) -> list[Check]:
    return [
        checklib.command_succeeds(
            "output_unchanged",
            "buildReport and formatMoney produce byte-for-byte what the original produced: literal reports for all "
            "three regions, name truncation, thousands grouping, bulk and large-order boundaries, cent rounding "
            "order, ordering, filters, errors, an unmodified input list, and 400 random reports compared with the "
            "original implementation.",
            workspace,
            [*NODE_TEST, ".hidden/hidden_output.js"],
        ),
        checklib.command_succeeds(
            "exports_and_callers_intact",
            "report.js still exports exactly buildReport and formatMoney, and the finance export and the digest "
            "that import them still produce their old output.",
            workspace,
            [*NODE_TEST, ".hidden/hidden_callers.js"],
        ),
        checklib.only_these_files_changed(
            "only_expected_files_changed",
            "Only source files under src/ and tests under test/ changed; no package, README or data files.",
            workspace,
            ["src/*.js", "test/*.js"],
        ),
        _callers_untouched(workspace),
        checklib.command_succeeds(
            "test_suite_passes", "The repository's own test suite passes.", workspace, NODE_TEST
        ),
        _no_long_function(workspace),
        _duplication_consolidated(workspace),
        _magic_numbers_named(workspace),
        _dead_code_removed(workspace),
        _characterization_tests_added(workspace),
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


def _callers_untouched(workspace) -> Check:
    name = "callers_untouched"
    description = (
        "The modules that import from report.js (export, digest) and the unrelated parsing and CLI modules are "
        "unchanged: the request was about report.js."
    )
    touched = [path for path in workspace.changed_files() if path in CALLERS]
    return Check(
        name, description, not touched, f"changed: {touched}" if touched else f"unchanged: {CALLERS}"
    )


def _source_files(workspace) -> dict[str, str]:
    """report.js plus any other source file the agent added or changed, with comments removed."""
    paths = {REPORT} | {p for p in workspace.changed_files() if SOURCE_FILE.fullmatch(p)}
    return {path: _strip_comments(workspace.read(path)) for path in sorted(paths) if workspace.read(path)}


def _strip_comments(source: str) -> str:
    """The source without `//` and `/* */` comments, keeping every line break so line counts stay right."""
    without_blocks = re.sub(
        r"/\*.*?\*/", lambda found: "\n" * found.group().count("\n"), source, flags=re.DOTALL
    )
    return re.sub(r"//.*$", "", without_blocks, flags=re.MULTILINE)


def _no_long_function(workspace) -> Check:
    name = "no_function_longer_than_forty_lines"
    description = (
        f"No function in the source files is longer than {MAX_FUNCTION_LINES} lines; the original buildReport "
        "is about 150 and the prompt says nobody can read it."
    )
    lengths = {
        f"{path}:{line_no}": length
        for path, source in _source_files(workspace).items()
        for line_no, length in _function_lengths(source)
    }
    too_long = {where: length for where, length in lengths.items() if length > MAX_FUNCTION_LINES}
    longest = max(lengths.values(), default=0)
    return Check(
        name, description, not too_long, f"too long: {too_long}" if too_long else f"longest: {longest}"
    )


def _function_lengths(source: str) -> list[tuple[int, int]]:
    """(start line, length) of every brace-bodied function, found by indentation of the closing brace."""
    lines = source.splitlines()
    lengths = []
    for index, line in enumerate(lines):
        if not FUNCTION_START.search(line):
            continue
        indent = len(line) - len(line.lstrip())
        opens = index
        while not lines[opens].rstrip().endswith("{") and opens < min(index + 12, len(lines) - 1):
            opens += 1
        if not lines[opens].rstrip().endswith("{"):
            continue
        for end in range(opens + 1, len(lines)):
            closing = lines[end]
            if (
                closing.strip()
                and len(closing) - len(closing.lstrip()) == indent
                and closing.lstrip().startswith("}")
            ):
                lengths.append((index + 1, end - index + 1))
                break
    return lengths


def _duplication_consolidated(workspace) -> Check:
    name = "regional_copies_consolidated"
    description = (
        "The three copied regional blocks are one: money rendering (toFixed), name truncation (the ellipsis), "
        "cent rounding (Math.round) and the discount math (units * unitPrice) no longer appear once per region."
    )
    code = "\n".join(_source_files(workspace).values())
    counts = {
        "toFixed": (len(re.findall(r"\.toFixed\(", code)), MAX_TO_FIXED),
        "ellipsis": (len(re.findall("…|\\\\u2026|\\\\u\\{2026\\}", code)), MAX_ELLIPSES),
        "Math.round": (len(re.findall(r"Math\.round\(", code)), MAX_MATH_ROUND),
        "units * unitPrice": (len(NET_MULTIPLICATION.findall(code)), MAX_NET_MULTIPLICATIONS),
    }
    over = {key: count for key, (count, limit) in counts.items() if count > limit}
    evidence = ", ".join(f"{key}: {count} (limit {limit})" for key, (count, limit) in counts.items())
    return Check(name, description, not over, evidence)


def _magic_numbers_named(workspace) -> Check:
    name = "magic_numbers_named"
    description = (
        "VAT rates, the bulk factor and threshold, the large-order limit, the column widths and the name cut-off "
        "appear only where they are named: in a constant declaration, in a lookup table or in a class constant, "
        "not in the logic."
    )
    offending = [
        f"{path}: {line.strip()}"
        for path, source in _source_files(workspace).items()
        for line in _logic_lines(source)
        if MAGIC_NUMBERS.search(line)
    ]
    return Check(
        name, description, not offending, checklib._quoted(offending) or "all rule literals are named"
    )


def _logic_lines(source: str) -> list[str]:
    """Lines of the source that are neither a named constant nor part of a lookup table.

    A module-level `const NAME = ...` is a constant, and so is a multi-line one (an object, an array of rows or a
    `new Map([...])`) up to the closing bracket at column 0. An arrow function or `function` assigned to a
    module-level `const` is logic. Further named forms: `static NAME = literal;` in a class, `const name = literal;`
    at any depth, `key: value` entries of a table inside a function, and lines inside a multi-line constant.
    """
    named_constant = re.compile(r"^(export\s+)?const\s+\w+\s*=")
    constant_with_body = re.compile(r"^(export\s+)?const\s+\w+\s*=[^;]*$")
    class_constant = re.compile(r"^\s*static\s+#?\w+\s*=\s*[^=>(]*;?\s*$")
    local_constant = re.compile(r"^\s*const\s+\w+\s*=\s*-?[\d_.]+;?\s*$")
    table_entry = re.compile(r"^\s+[\w'\"]+\s*:\s")
    logic, in_constant = [], False
    for line in source.splitlines():
        if in_constant:
            in_constant = not re.match(r"[\]})]", line)
            continue
        is_function = "=>" in line or re.search(r"\bfunction\b", line)
        if named_constant.match(line) and not is_function:
            in_constant = constant_with_body.match(line) is not None
        elif not (class_constant.match(line) or local_constant.match(line) or table_entry.match(line)):
            logic.append(line)
    return logic


def _dead_code_removed(workspace) -> Check:
    name = "dead_code_removed"
    description = (
        "The unreachable legacy-format branch (an earlier guard rejects every format but text) and the "
        "commented-out code in report.js are gone."
    )
    source = workspace.read(REPORT) or ""
    legacy = [line.strip() for line in _strip_comments(source).splitlines() if re.search("(?i)legacy", line)]
    commented = [line for line in _comment_lines(source) if checklib._is_commented_out_code(line)]
    offending = [f"legacy branch: {line}" for line in legacy] + [
        f"commented-out code: {line}" for line in commented
    ]
    return Check(
        name, description, not offending, checklib._quoted(offending) or "no legacy branch, no commented code"
    )


def _comment_lines(source: str) -> list[str]:
    """Text of every `//` comment and every line inside a `/* */` comment, as `// text`."""
    lines = [f"// {m.group(1)}" for m in re.finditer(r"(?:^|\s)//\s?(.*)$", source, re.MULTILINE)]
    for block in re.findall(r"/\*(.*?)\*/", source, flags=re.DOTALL):
        lines += [f"// {line.strip().lstrip('*').strip()}" for line in block.splitlines() if line.strip()]
    return lines


def _characterization_tests_added(workspace) -> Check:
    name = "characterization_tests_added"
    description = (
        "Before refactoring, the agent pinned the old behavior: it added tests that pass on the untouched original "
        "code and that exercise the French and the British path, which the existing tests do not cover. Tests of "
        "new modules cannot run on the original code; they are not pinning tests and do not count either way."
    )
    changed_tests = [
        path for path in workspace.changed_files() if fnmatchcase(path, "test/*.js") and workspace.read(path)
    ]
    pinning = [
        path
        for path in changed_tests
        if checklib.characterization_tests_pass_on_base(
            "passes_on_base", description, workspace, [path], NODE_TEST, NODE_TESTS_RAN
        ).passed
    ]
    passes_on_base = Check(
        "passes_on_base",
        description,
        bool(pinning),
        f"changed or added test files: {changed_tests}; they pass on the original code: {pinning}",
    )
    regions = [
        checklib.any_of(
            f"covers_{code}",
            description,
            *(
                checklib.added_test_mentions(
                    f"mentions_{quote}", description, workspace, pinning, f"{quote}{code}{quote}"
                )
                for quote in ("'", '"')
            ),
        )
        for code in ("FR", "UK")
    ]
    return checklib.all_of(name, description, passes_on_base, *regions)
