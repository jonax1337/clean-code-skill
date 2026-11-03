"""Agentic track: a coding agent with real tools works on a throwaway copy of a small fixture repo.

Cases live in `cases-agentic/<split>/<id>/`. The split is `dev` (cases skill changes may be tuned on) or `test`
(held-out cases, written without seeing the skill, used only to confirm a change). Each case has
- `case.md`     title and the prompt the agent gets,
- `repo/`       the project as the agent finds it,
- `hidden/`     tests the agent never sees; grading copies them to `<repo>/.hidden/`,
- `checks.py`   `checks(workspace, transcript)` with the deterministic checks, optionally `setup(repo)` for
                tooling such as `node_modules`, and the `SELFTEST_COMMANDS` an honest agent would run,
- `reference/`  a solution, as files laid over `repo/`, that `selftest_agentic.py` checks against every check.

Results live in `results/agentic/<coder model>/{runs,checks,pairwise}/`.
"""

from __future__ import annotations

import importlib.util
import json
import os
import re
import shutil
import subprocess
import tempfile
from collections.abc import Generator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType

from harness import (
    EVALS_DIR,
    ISOLATION_FLAGS,
    RESULTS_DIR,
    SKILL_PREAMBLE,
    Condition,
    claude_executable,
    markdown_section,
)

AGENTIC_CASES_DIR = EVALS_DIR / "cases-agentic"
AGENTIC_RESULTS_DIR = RESULTS_DIR / "agentic"
SPLITS = ("dev", "test")
HIDDEN_TESTS_DIR = ".hidden"

AGENT_TOOLS = ["Read", "Grep", "Glob", "Edit", "Write", "Bash"]
FILE_EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}
# Bash commands that write project files: sed -i, tee, a redirect into a file, Python writing a file, applying a
# patch. Scratch files under /tmp and writes to /dev do not change the project.
BASH_FILE_WRITE = re.compile(
    r"\bsed\s+(-\w*\s+)*-i|\btee\s+(-a\s+)?(?!/tmp/|/dev/)|(?<![\d&>=-])>{1,2}\s*(?!&|/dev/|/tmp/)[\w./\\~\"'-]|"
    r"\.write(_text|_bytes)?\(|open\([^)]*['\"][wa]b?['\"]|\bgit\s+apply\b|\bpatch\s+-p"
)
SECRET_VARIABLE = re.compile(
    r"(^|_)(TOKEN|SECRET|PASSWORD|PASSWD|CREDENTIALS?|API_?KEY|ACCESS_KEY|PRIVATE_KEY)$", re.IGNORECASE
)
AGENT_TIMEOUT_S = 1800
BASE_TAG = "eval-base"


def results_dir(model: str, kind: str) -> Path:
    """Where results for one coder model live; kind is `runs`, `checks` or `pairwise`."""
    return AGENTIC_RESULTS_DIR / model / kind


def coder_models() -> list[str]:
    """Coder models that have stored runs."""
    return sorted(path.parent.name for path in AGENTIC_RESULTS_DIR.glob("*/runs") if path.is_dir())


@dataclass(frozen=True)
class AgenticCase:
    case_id: str
    split: str
    title: str
    prompt: str
    directory: Path

    @property
    def repo_dir(self) -> Path:
        return self.directory / "repo"

    @property
    def hidden_dir(self) -> Path:
        return self.directory / "hidden"

    @property
    def reference_dir(self) -> Path:
        return self.directory / "reference"

    def checks_module(self) -> ModuleType:
        path = self.directory / "checks.py"
        spec = importlib.util.spec_from_file_location(f"checks_{self.case_id.replace('-', '_')}", path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Cannot load {path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module


def load_agentic_cases(split: str | None = None) -> list[AgenticCase]:
    """All cases, or the cases of one split, ordered by split and id."""
    splits = SPLITS if split is None else (split,)
    return [
        _parse_case(path.parent)
        for name in splits
        for path in sorted((AGENTIC_CASES_DIR / name).glob("*/case.md"))
    ]


def _parse_case(directory: Path) -> AgenticCase:
    text = (directory / "case.md").read_text(encoding="utf-8")
    title = text.splitlines()[0].removeprefix("# ").strip()
    return AgenticCase(
        directory.name, directory.parent.name, title, markdown_section(text, "Prompt"), directory
    )


class Workspace:
    """A git repository with a copy of a case repo. The tag `eval-base` marks the untouched fixture."""

    def __init__(self, root: Path, case: AgenticCase) -> None:
        self.root = root
        self.case = case

    def git(self, *args: str) -> str:
        # Bytes, not text mode: text mode turns CRLF into LF, which would hide line-ending rewrites from the diff.
        completed = subprocess.run(
            ["git", "-c", "core.autocrlf=false", "-c", "core.safecrlf=false", *args],
            cwd=self.root,
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0:
            stderr = completed.stderr.decode("utf-8", errors="replace").strip()
            raise RuntimeError(f"git {' '.join(args)} failed: {stderr}")
        return completed.stdout.decode("utf-8", errors="replace")

    def run(self, command: list[str], timeout: int = 300) -> subprocess.CompletedProcess[str]:
        """Run a command in the workspace; a timeout or a missing program becomes a failed result."""
        try:
            return subprocess.run(
                command,
                cwd=self.root,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout,
                check=False,
            )
        except (subprocess.TimeoutExpired, OSError) as error:
            return subprocess.CompletedProcess(command, -1, "", f"could not run {command[0]}: {error}")

    def diff(self, context_lines: int = 8, ignore_cr_at_eol: bool = False) -> str:
        """Everything changed since the fixture, new files included, as an applicable patch.

        With `ignore_cr_at_eol` the diff is for reading only: it hides line-ending rewrites.
        """
        self.git("add", "-A")
        reading_options = ["--ignore-cr-at-eol"] if ignore_cr_at_eol else []
        return self.git(
            "diff", "--cached", "--no-renames", "--binary", *reading_options, f"-U{context_lines}", BASE_TAG
        )

    def apply(self, patch: str) -> None:
        if not patch.strip():
            return
        patch_file = self.root.parent / "agent.patch"
        patch_file.write_bytes(patch.encode("utf-8"))
        self.git("apply", "--whitespace=nowarn", str(patch_file))

    def changed_files(self) -> list[str]:
        self.git("add", "-A")
        return self.git("diff", "--cached", "--no-renames", "--name-only", BASE_TAG).splitlines()

    def added_lines(self, path: str) -> list[str]:
        return self._diff_lines(path, "+")

    def removed_lines(self, path: str) -> list[str]:
        return self._diff_lines(path, "-")

    def _diff_lines(self, path: str, sign: str) -> list[str]:
        # A line whose only change is a CR is not a content change. On Windows, agents that write files from
        # Python in text mode turn LF into CRLF, which is noise from the platform, not from the agent's work.
        self.git("add", "-A")
        diff = self.git("diff", "--cached", "--no-renames", "--ignore-cr-at-eol", "-U0", BASE_TAG, "--", path)
        lines, in_hunk = [], False
        for line in diff.splitlines():
            if line.startswith("diff --git"):
                in_hunk = False
            elif line.startswith("@@"):
                in_hunk = True
            elif in_hunk and line.startswith(sign):
                lines.append(line[1:])
        return lines

    def read(self, path: str) -> str | None:
        file = self.root / path
        return file.read_text(encoding="utf-8") if file.is_file() else None

    def read_base(self, path: str) -> str | None:
        try:
            return self.git("show", f"{BASE_TAG}:{path}")
        except RuntimeError:
            return None

    def add_hidden_tests(self) -> None:
        shutil.copytree(self.case.hidden_dir, self.root / HIDDEN_TESTS_DIR, dirs_exist_ok=True)

    @contextmanager
    def base_with(self, paths: list[str]) -> Generator[Workspace, None, None]:
        """A fresh copy of the untouched fixture with the given files copied over from this workspace."""
        with workspace_for(self.case) as base:
            for path in paths:
                target = base.root / path
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(self.root / path, target)
            yield base


@contextmanager
def workspace_for(case: AgenticCase) -> Generator[Workspace, None, None]:
    with tempfile.TemporaryDirectory(prefix="cc-agentic-", ignore_cleanup_errors=True) as temp:
        root = Path(temp) / "repo"
        shutil.copytree(case.repo_dir, root)
        setup = getattr(case.checks_module(), "setup", None)
        if setup is not None:
            setup(root)
        workspace = Workspace(root, case)
        workspace.git("init", "-q")
        (root / ".git" / "info" / "exclude").write_text(f"{HIDDEN_TESTS_DIR}/\n", encoding="utf-8")
        workspace.git("add", "-A")
        workspace.git(
            *("-c", "user.name=eval", "-c", "user.email=eval@example.invalid", "-c", "commit.gpgsign=false"),
            *("commit", "-qm", "fixture"),
        )
        workspace.git("tag", BASE_TAG)
        yield workspace


@dataclass(frozen=True)
class ToolCall:
    name: str
    input: dict
    failed: bool

    @property
    def command(self) -> str:
        return self.input.get("command", "") if self.name == "Bash" else ""

    @property
    def edits_files(self) -> bool:
        return self.name in FILE_EDIT_TOOLS or BASH_FILE_WRITE.search(self.command) is not None


class Transcript:
    """The `--output-format stream-json` event log of one agent run."""

    def __init__(self, events: list[dict]) -> None:
        self.events = events

    @classmethod
    def from_jsonl(cls, text: str) -> Transcript:
        return cls([json.loads(line) for line in text.splitlines() if line.strip().startswith("{")])

    @property
    def tool_calls(self) -> list[ToolCall]:
        failed_ids = {
            block.get("tool_use_id")
            for event in self.events
            if event.get("type") == "user"
            for block in _content_blocks(event)
            if block.get("type") == "tool_result" and block.get("is_error")
        }
        return [
            ToolCall(block["name"], block.get("input", {}), block.get("id") in failed_ids)
            for event in self.events
            if event.get("type") == "assistant"
            for block in _content_blocks(event)
            if block.get("type") == "tool_use"
        ]

    @property
    def result(self) -> dict:
        return next((event for event in reversed(self.events) if event.get("type") == "result"), {})

    @property
    def init(self) -> dict:
        return next((event for event in self.events if event.get("subtype") == "init"), {})

    @property
    def final_message(self) -> str:
        return self.result.get("result", "")

    def commands_after_last_edit(self) -> list[tuple[str, bool]]:
        """Bash commands run after the last file edit, each with whether it failed.

        A Bash command that writes files counts as an edit. Its text after the last write still counts as run
        after the edit, so `cat >> t.py <<EOF ... EOF` followed by `pytest` in the same command is a test run.
        """
        calls = self.tool_calls
        last_edit = max((i for i, call in enumerate(calls) if call.edits_files), default=-1)
        commands = [(call.command, call.failed) for call in calls[last_edit + 1 :] if call.name == "Bash"]
        if last_edit >= 0 and calls[last_edit].name == "Bash":
            edit = calls[last_edit]
            *_, last_write = BASH_FILE_WRITE.finditer(edit.command)
            commands.insert(0, (edit.command[last_write.end() :], edit.failed))
        return commands

    def files_read(self) -> list[str]:
        return [call.input.get("file_path", "") for call in self.tool_calls if call.name == "Read"]


def _content_blocks(event: dict) -> list[dict]:
    content = event.get("message", {}).get("content", [])
    return content if isinstance(content, list) else []


@dataclass(frozen=True)
class AgentRun:
    transcript_jsonl: str
    patch: str
    review_diff: str
    returncode: int
    stderr: str


def run_agent(case: AgenticCase, condition: Condition, model: str, budget_usd: float) -> AgentRun:
    """Let the agent work on a fresh copy of the case repo and capture its transcript and diff."""
    with (
        workspace_for(case) as workspace,
        tempfile.TemporaryDirectory(prefix="cc-skill-", ignore_cleanup_errors=True) as skill_temp,
    ):
        command = _agent_command(model, budget_usd)
        if condition.skill_source is not None:
            skill_dir = _install_skill(condition, Path(skill_temp) / "skill")
            prompt_file = Path(skill_temp) / "skill-prompt.txt"
            prompt_file.write_text(_skill_prompt(condition, skill_dir), encoding="utf-8")
            command += ["--append-system-prompt-file", str(prompt_file), "--add-dir", str(skill_dir)]
        completed = subprocess.run(
            command,
            input=case.prompt,
            cwd=workspace.root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=_agent_environment(),
            timeout=AGENT_TIMEOUT_S,
            check=False,
        )
        return AgentRun(
            transcript_jsonl=completed.stdout,
            patch=workspace.diff(),
            review_diff=workspace.diff(ignore_cr_at_eol=True),
            returncode=completed.returncode,
            stderr=completed.stderr,
        )


def _agent_environment() -> dict[str, str]:
    """The current environment without variables that look like secrets: the agent can run any command."""
    kept = {name: value for name, value in os.environ.items() if not SECRET_VARIABLE.search(name)}
    return {**kept, "CLAUDE_CODE_DISABLE_CLAUDE_MDS": "1"}


def _agent_command(model: str, budget_usd: float) -> list[str]:
    return [
        claude_executable(),
        "-p",
        "--model",
        model,
        "--tools",
        ",".join(AGENT_TOOLS),
        "--allowedTools",
        *AGENT_TOOLS,
        "--permission-mode",
        "dontAsk",
        *ISOLATION_FLAGS,
        "--max-budget-usd",
        f"{budget_usd:.2f}",
        "--output-format",
        "stream-json",
        "--verbose",
    ]


def _install_skill(condition: Condition, target: Path) -> Path:
    """Lay the skill out the way an installed skill looks: SKILL.md plus its reference files."""
    target.mkdir(parents=True)
    (target / "SKILL.md").write_text(condition.skill_text() or "", encoding="utf-8")
    references = condition.references_dir()
    if references is not None:
        shutil.copytree(references, target / "references")
    return target


def _skill_prompt(condition: Condition, skill_dir: Path) -> str:
    return (
        f"{SKILL_PREAMBLE} Its files are in {skill_dir.as_posix()}; "
        "read the files it links to from there when you need them.\n\n"
        f"<skill>\n{condition.skill_text()}\n</skill>"
    )
