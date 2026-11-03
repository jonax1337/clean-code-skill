"""Checks for 15-review-pull-request: review PR 482 into REVIEW.md without changing any code.

The PR plants three real problems (SQL injection in search_users, a wrong page count in the list handler, a
swallowed sqlite3 error in audit.record), a decoy that only looks like injection (deactivate_users builds its
`IN (?, ?, ...)` list with an f-string and re-raises after rollback) and a few harmless nits.
"""

import json
import re

import checklib
from checklib import PYTEST, Check

SELFTEST_COMMANDS = ["cat pr/482.diff"]
REVIEW = "REVIEW.md"
HIDDEN_TESTS = ".hidden"
WINDOW = 400  # characters around a finding's location in which its problem keywords must appear

# Each real finding: where it is (identifiers a reviewer must mention) and what is wrong (any accepted synonym).
INJECTION = (
    r"search",
    (
        r"inject|sqli\b|f-string|fstring|interpolat|concatenat|string (formatting|building)|unsanitiz|unsanitis|"
        r"(not|n't|never) (be )?(parameteri[sz]ed|bound)|attacker|untrusted|user[- ]controlled"
    ),
)
PAGE_COUNT = (
    r"\bpages\b|total_pages|page count|number of pages|pager|count_users",
    (
        r"floor|integer division|//|ceil|round(s|ed|ing)? (down|up)|partial|last page|remainder|truncat|"
        r"off-by-one|off by one|multiple of|zero pages|0 pages|divisible|evenly|undercount|too (low|small|few)|"
        r"rounding|wrong (number|count|value|total)"
    ),
)
SWALLOWED = (
    r"audit",
    (
        r"swallow|silent|ignor|suppress|\bhides?\b|hiding|discard|except sqlite3\.error|except:\s*pass|"
        r"errors? (is|are) (dropped|lost)|except.{0,40}\bpass\b|does nothing|do nothing|no-op|unnoticed|"
        r"undetected|(not|never) (re-?raised|propagat|logged|surfaced|reported)|"
        r"(entries|rows|records|trail).{0,40}(lost|dropped|missing|gaps?)|(lost|dropped|missing|gaps? in) "
        r"(the )?(audit|entries|rows|trail)"
    ),
)
LINE_REFERENCE = re.compile(r"\.py\W{0,8}(l|lines?)?\s*\d+|\blines?\s+\d+|\bl\d{1,4}\b")

# The decoy: where it is, what counts as accusing it, and what shows the reviewer found it fine.
DECOY_PLACE = re.compile(
    r"deactivate_users|\bin[- ]clause\b|\bin \((\{|\?)|users\.py\W{0,8}(l|lines?)?\s*(5[5-9]|6[0-8])\b"
)
DECOY_EXCEPTION = re.compile(r"deactivate_users|rollback|except exception")
# What it takes to accuse the decoy's exception handling when the sentence is part of the audit finding.
BROAD_EXCEPT = re.compile(
    r"except exception|too broad|overly broad|broad except|bare except|catch-all|catch(es)? everything"
)
# Words that put the decoy in one breath with the real injection ("both build SQL with f-strings").
GROUPED_WITH_SEARCH = re.compile(r"\bboth\b|\balso\b|\bsame\b|\btoo\b|as well|similar|likewise|another")
ACCUSES_INJECTION = re.compile(
    r"inject|vulnerab|exploit|unsafe|insecure|unsanitiz|unsanitis|should use (a )?parameteri|"
    r"use parameteri[sz]ed (queries|sql)|replace the f-string|avoid (the )?f-string|"
    r"sql built|builds? (the )?(sql|query) (with|using|via|from) (an? )?(f-string|string)"
)
ACCUSES_SWALLOWING = re.compile(
    r"swallow|too broad|overly broad|broad except|bare except|catch-all|catches everything|\bhides?\b|\bmasks?\b"
)
FOUND_FINE = re.compile(
    r"(?<!make it )(?<!make this )\bsafe|\bfine\b|\bok\b|okay|\bcorrect|not (a |an )?(bug|issue|problem|vulnerab|injection|injectable|risk|"
    r"exploitable)|no (bug|issue|problem|vulnerab|injection|risk|concern)|false positive|already (parameteri|bound)|"
    r"(is|are|being) (parameteri|bound)|bound (as |via |through )?(param|\?)|binds? (the )?(ids|values)|"
    r"only (contains|consist|interpolat)|harmless|benign|legitimate|acceptable|intentional|looks (suspicious|scary|"
    r"alarming)|re-?rais|unlike|in contrast|as in|like in|same as|compare|\bmodel\b|properly"
)
NAMES_SEARCH_FINDING = re.compile(r"search_users|search\.py")

# Remarks about the planted nits; only these specific ones are matched, a generic "nits" heading is not.
NIT = re.compile(
    r"unused import|import os\b|\btodo\b|(no|missing|lacks?|without)( a)? docstring|magic number|"
    r"duplicat\w* (the |of )?(default|constant|page)|variable name|(vague|poor|short|unclear|cryptic) name|`res`"
)
BLOCKS_MERGE = re.compile(
    r"request(ed|ing)? changes|changes requested|do(es)? not merge|don't merge|do not approve|not approv|"
    r"not (yet )?(ready|safe|mergeable|approved|good to go)|\bunsafe to merge|should not (be )?merged|"
    r"shouldn'?t (be )?merged|"
    r"\b(would|will|can|could|should|do|does|did|am)\s*(not|n't)\s+(\w+\s+){0,2}(merge|merged|merging|ship|approve|land)\b|"
    r"\b(wouldn|shouldn|can|don|won)'t\s+(\w+\s+){0,2}(merge|merged|ship|approve|land)\b|"
    r"should not go in|hold (off|the merge)|send (it )?back|merge:?\s*no\b|"
    r"\bblock(s|ing|er|ers)?\b|must (be )?fix|needs? (to be )?(fixed|changes|work)|before (merging|this (is )?merged)|"
    r"can(no|')t (be )?merge|hold off|don't ship|do not ship|reject"
)
APPROVES = re.compile(
    r"(?<!not )(?<!n't )\blgtm\b|(?<!not )(?<!n't )ship it|(?<!un)(?<!not )(?<!n't )safe to merge|"
    r"looks good to merge"
)
# `482.diff` by name, or the whole `pr/` folder by glob (`cat pr/*`, `Read pr/482*`).
OPENS_PR_DIFF = re.compile(r"482\.diff|pr[/\\]+(\*|482\*)")
LIST_ITEM = re.compile(r"\s*([-*+]|\d+[.)])\s")
HEADING = re.compile(r"\s*#{1,6}\s")
TABLE_ROW = re.compile(r"\s*\|")


def checks(workspace, transcript) -> list[Check]:
    review = (workspace.read(REVIEW) or "").lower().replace("’", "'")
    flat = re.sub(r"\s+", " ", review)
    return [
        _finding(
            "finds_the_sql_injection",
            "The review reports the f-string SQL built from the `q` parameter in search_users as an SQL injection.",
            flat,
            INJECTION,
        ),
        _finding(
            "finds_the_wrong_page_count",
            "The review reports that the number of pages in the list handler is computed with a floor division "
            "and so drops the last partial page (a bug the PR's tests do not cover).",
            flat,
            PAGE_COUNT,
        ),
        _finding(
            "finds_the_swallowed_audit_error",
            "The review reports that audit.record swallows the database error, so audit entries can be lost "
            "silently.",
            flat,
            SWALLOWED,
        ),
        _findings_cite_file_and_line(flat),
        _decoy_not_reported_as_bug(review),
        _injection_before_nits(flat),
        _does_not_approve(flat),
        checklib.only_these_files_changed(
            "only_review_added",
            "The review is the only change: no source or test file was edited (applying the patch to try it and "
            "reverting it is fine) and no scratch files are left behind.",
            workspace,
            [REVIEW],
        ),
        checklib.command_succeeds(
            "pr_not_left_applied",
            "Hidden tests confirm the code is still the state before PR 482: the PR was neither merged nor "
            "left applied in the working tree.",
            workspace,
            [*PYTEST, f"{HIDDEN_TESTS}/test_pr_not_applied.py"],
        ),
        checklib.command_succeeds(
            "test_suite_passes", "The repository's own test suite passes.", workspace, PYTEST
        ),
        checklib.clean_diff(
            "clean_diff",
            "The code files have no debug output, commented-out code or narrating comments left in them (the "
            "review itself is prose and not checked).",
            _WithoutReview(workspace),
        ),
        _looked_at_the_diff(transcript),
    ]


class _WithoutReview:
    """The workspace as `checklib.clean_diff` sees it, minus REVIEW.md: its headings and inline code are prose."""

    def __init__(self, workspace) -> None:
        self._workspace = workspace

    def changed_files(self) -> list[str]:
        return [path for path in self._workspace.changed_files() if path != REVIEW]

    def __getattr__(self, name: str):
        return getattr(self._workspace, name)


def _finding_windows(flat: str, place: str, problem: str) -> list[str]:
    """Stretches of the review where the location and a problem keyword occur within WINDOW characters."""
    windows = []
    for found in re.finditer(place, flat):
        start, end = max(0, found.start() - WINDOW), found.end() + WINDOW
        if re.search(problem, flat[start:end]):
            windows.append(flat[start:end])
    return windows


def _finding(name: str, description: str, flat: str, finding: tuple[str, str]) -> Check:
    windows = _finding_windows(flat, *finding)
    evidence = (
        windows[0][:300] if windows else f"no passage mentions {finding[0]!r} together with its problem"
    )
    return Check(name, description, bool(windows), evidence)


def _first_mention(flat: str, place: str, problem: str) -> int | None:
    """Where the first passage that reports the finding starts: its earliest problem keyword near the location."""
    starts = []
    for found in re.finditer(place, flat):
        start, end = max(0, found.start() - WINDOW), found.end() + WINDOW
        keyword = re.search(problem, flat[start:end])
        if keyword:
            starts.append(start + keyword.start())
    return min(starts, default=None)


def _findings_cite_file_and_line(flat: str) -> Check:
    name = "findings_cite_file_and_line"
    description = (
        "Each of the three real findings names a Python file and a line in the passage that reports it, as the "
        "prompt asked (either the line in the patched file or in the diff is accepted)."
    )
    uncited = []
    for label, finding in (
        ("injection", INJECTION),
        ("page count", PAGE_COUNT),
        ("swallowed error", SWALLOWED),
    ):
        windows = _finding_windows(flat, *finding)
        if not any(".py" in window and LINE_REFERENCE.search(window) for window in windows):
            uncited.append(label)
    return Check(
        name, description, not uncited, f"no file and line next to: {uncited}" if uncited else "all cited"
    )


def _review_items(review: str) -> list[str]:
    """Paragraphs and list items; a heading is kept together with the text that follows it."""
    items: list[list[str]] = [[]]
    for line in review.splitlines():
        only_heading_so_far = bool(items[-1]) and all(HEADING.match(text) for text in items[-1])
        starts_new_item = (
            not line.strip() or LIST_ITEM.match(line) or HEADING.match(line) or TABLE_ROW.match(line)
        )
        if starts_new_item and items[-1] and not only_heading_so_far:
            items.append([])
        if line.strip():
            items[-1].append(line.strip())
    return [" ".join(lines) for lines in items if lines]


def _sentences(item: str) -> list[str]:
    return [sentence for sentence in re.split(r"(?<=[.!?;])\s+", item) if sentence]


def _decoy_not_reported_as_bug(review: str) -> Check:
    name = "decoy_not_reported_as_bug"
    description = (
        "deactivate_users (f-string with only generated `?` placeholders, values bound, rollback then re-raise) "
        "is not reported as an injection or a swallowed exception; calling it fine or contrasting it with the "
        "real injection is allowed."
    )
    flagged = []
    for item in _review_items(review):
        about_audit = "audit" in item
        units = _sentences(item) if NAMES_SEARCH_FINDING.search(item) or about_audit else [item]
        for unit in units:
            if FOUND_FINE.search(unit):
                continue
            if NAMES_SEARCH_FINDING.search(unit) and not GROUPED_WITH_SEARCH.search(unit):
                continue
            # Inside the audit finding, "swallowed" is about audit.record; only a complaint about the broad
            # `except Exception` can be about the decoy.
            swallowing = BROAD_EXCEPT if about_audit else ACCUSES_SWALLOWING
            accuses_injection = DECOY_PLACE.search(unit) and ACCUSES_INJECTION.search(unit)
            accuses_swallowing = (
                DECOY_EXCEPTION.search(unit) and swallowing.search(unit) and "audit" not in unit
            )
            if accuses_injection or accuses_swallowing:
                flagged.append(unit[:200])
    return Check(name, description, not flagged, "\n".join(flagged) if flagged else "decoy not accused")


def _injection_before_nits(flat: str) -> Check:
    name = "injection_before_style_remarks"
    description = (
        "The SQL injection is reported before any remark about the planted nits (unused import, TODO, "
        "docstring, magic number, vague names), because the prompt asked for the most important findings first."
    )
    injection = _first_mention(flat, *INJECTION)
    nit = NIT.search(flat)
    if injection is None:
        return Check(name, description, False, "the injection is not reported")
    passed = nit is None or injection < nit.start()
    evidence = f"injection at {injection}, first nit at {nit.start() if nit else 'none'}"
    return Check(name, description, passed, evidence)


def _does_not_approve(flat: str) -> Check:
    name = "does_not_approve"
    description = (
        "The review ends with a clear do-not-merge verdict (request changes, blocking, do not merge) and does "
        "not approve the PR, since it contains an injection hole."
    )
    blocks, approves = BLOCKS_MERGE.search(flat), APPROVES.search(flat)
    evidence = f"blocking wording: {blocks.group(0) if blocks else None}; approving wording: {approves}"
    return Check(name, description, blocks is not None and approves is None, evidence)


def _looked_at_the_diff(transcript) -> Check:
    name = "looked_at_the_diff"
    description = (
        "Instead of ran_after_last_edit (a review has no tests to rerun): the agent opened pr/482.diff, the "
        "thing it was asked to review, with a tool call."
    )
    opened = [call.name for call in transcript.tool_calls if OPENS_PR_DIFF.search(json.dumps(call.input))]
    return Check(name, description, bool(opened), f"tool calls touching 482.diff: {opened}")
