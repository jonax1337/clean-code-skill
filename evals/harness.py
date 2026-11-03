"""Shared pieces of the eval harness: test cases, skill variants and isolated `claude -p` calls."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
import urllib.request
from dataclasses import dataclass
from pathlib import Path

EVALS_DIR = Path(__file__).resolve().parent
REPO_DIR = EVALS_DIR.parent
CASES_DIR = EVALS_DIR / "cases"
RESULTS_DIR = EVALS_DIR / "results"
RUNS_DIR = RESULTS_DIR / "runs"
GRADES_DIR = RESULTS_DIR / "grades"
CACHE_DIR = EVALS_DIR / ".cache"

SICKN33_COMMIT = "bbfc66fe61e8b6ced7d38481c47600e8ac9b8eea"
SICKN33_URL = (
    "https://raw.githubusercontent.com/sickn33/agentic-awesome-skills/"
    f"{SICKN33_COMMIT}/skills/clean-code/SKILL.md"
)

BASE_SYSTEM_PROMPT = (
    "You are a coding agent helping a developer in their codebase. In this session you cannot "
    "run tools or open other files; work only with what the user shows you. Reply with the code "
    "changes and a short explanation."
)

SKILL_PREAMBLE = "The following skill is active for this task. Follow it."
SKILL_FOOTER = "Files that the skill links to are not available in this session."


@dataclass(frozen=True)
class Case:
    case_id: str
    title: str
    prompt: str
    assertions: list[str]


@dataclass(frozen=True)
class Condition:
    name: str
    label: str
    skill_source: str | None
    references: str | None = None  # folder with the skill's reference files, relative to the repo

    def skill_text(self) -> str | None:
        if self.skill_source is None:
            return None
        if self.skill_source.startswith("https://"):
            return _fetch_cached(self.skill_source)
        return (REPO_DIR / self.skill_source).read_text(encoding="utf-8")

    def references_dir(self) -> Path | None:
        return REPO_DIR / self.references if self.references else None

    def system_prompt(self) -> str:
        skill = self.skill_text()
        if skill is None:
            return BASE_SYSTEM_PROMPT
        return f"{BASE_SYSTEM_PROMPT}\n\n{SKILL_PREAMBLE}\n\n<skill>\n{skill}\n</skill>\n\n{SKILL_FOOTER}"


SKILL_REFERENCES = "skills/clean-code/references"

CONDITIONS = [
    Condition("baseline", "No skill", None),
    Condition("sickn33", "sickn33/clean-code", SICKN33_URL),
    Condition("v1", "This repo, v1", "evals/skills/v1.md"),
    Condition("v2", "This repo, v2", "evals/skills/v2.md", SKILL_REFERENCES),
]

# Versions measured only on the agentic track, so the published single-turn results stay as they are. v3a was
# released as 3.0.0 (`skills/clean-code/SKILL.md` is v3a with the version number bumped); v3b is the shorter
# alternative. Every version is a frozen copy, so changing the skill never changes what a past result measured.
# All of them share the current skill's reference files, so their links resolve.
CANDIDATE_CONDITIONS = [
    Condition("v3a", "This repo, v3", "evals/skills/v3a.md", SKILL_REFERENCES),
    Condition("v3b", "v3b: lean", "evals/skills/v3b.md", SKILL_REFERENCES),
]
ALL_CONDITIONS = CONDITIONS + CANDIDATE_CONDITIONS


def load_cases() -> list[Case]:
    return [_parse_case(path) for path in sorted(CASES_DIR.glob("*.md"))]


def _parse_case(path: Path) -> Case:
    text = path.read_text(encoding="utf-8")
    title = text.splitlines()[0].removeprefix("# ").strip()
    prompt = markdown_section(text, "Prompt")
    assertions = re.findall(r"^\d+\.\s+(.+)$", markdown_section(text, "Assertions"), flags=re.MULTILINE)
    return Case(case_id=path.stem, title=title, prompt=prompt, assertions=assertions)


def markdown_section(text: str, heading: str) -> str:
    match = re.search(rf"^## {heading}\n(.*?)(?=^## |\Z)", text, flags=re.MULTILINE | re.DOTALL)
    if match is None:
        raise ValueError(f"Case is missing the '## {heading}' section")
    return match.group(1).strip()


def _fetch_cached(url: str) -> str:
    CACHE_DIR.mkdir(exist_ok=True)
    cached = CACHE_DIR / re.sub(r"[^A-Za-z0-9.]+", "_", url)
    if not cached.exists():
        with urllib.request.urlopen(url, timeout=30) as response:
            cached.write_bytes(response.read())
    return cached.read_text(encoding="utf-8")


@dataclass(frozen=True)
class ClaudeReply:
    text: str
    duration_ms: int
    cost_usd: float
    output_tokens: int
    model_ids: list[str]


def ask_claude(prompt: str, system_prompt: str, model: str, effort: str | None = None) -> ClaudeReply:
    """Run one headless Claude Code turn that sees no user config, CLAUDE.md, skills, MCP or tools."""
    with tempfile.TemporaryDirectory(prefix="cc-eval-") as workdir:
        system_file = Path(workdir) / "system.txt"
        system_file.write_text(system_prompt, encoding="utf-8")
        completed = subprocess.run(
            _claude_command(model, effort, system_file),
            input=prompt,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=workdir,
            env={**os.environ, "CLAUDE_CODE_DISABLE_CLAUDE_MDS": "1"},
            timeout=900,
            check=False,
        )
    if completed.returncode != 0:
        raise RuntimeError(f"claude -p failed ({completed.returncode}): {completed.stderr.strip()}")
    payload = json.loads(completed.stdout)
    if payload.get("is_error"):
        raise RuntimeError(f"claude -p returned an error: {payload.get('result')}")
    return ClaudeReply(
        text=payload["result"],
        model_ids=sorted(payload.get("modelUsage", {})),
        duration_ms=payload.get("duration_ms", 0),
        cost_usd=payload.get("total_cost_usd", 0.0),
        output_tokens=payload.get("usage", {}).get("output_tokens", 0),
    )


def extract_json(text: str) -> dict:
    """The first JSON object in a model reply, ignoring prose before and after it."""
    start = text.find("{")
    if start == -1:
        raise ValueError(f"Reply contains no JSON: {text[:200]}")
    value, _ = json.JSONDecoder().raw_decode(text, start)
    return value


def write_text_atomic(path: Path, text: str) -> None:
    """Write via a temporary file, so an interrupted run never leaves a truncated file that looks finished."""
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_name(f"{path.name}.partial")
    partial.write_text(text, encoding="utf-8", newline="\n")
    os.replace(partial, path)


def _claude_command(model: str, effort: str | None, system_file: Path) -> list[str]:
    command = [
        claude_executable(),
        "-p",
        "--model",
        model,
        "--tools",
        "",
        *ISOLATION_FLAGS,
        "--output-format",
        "json",
        "--system-prompt-file",
        str(system_file),
    ]
    if effort:
        command += ["--effort", effort]
    return command


# Keep the user's own settings, hooks, plugins, skills, MCP servers and sessions out of every eval run.
ISOLATION_FLAGS = [
    "--setting-sources",
    "project",
    "--disable-slash-commands",
    "--strict-mcp-config",
    "--no-session-persistence",
]


def claude_executable() -> str:
    executable = shutil.which("claude")
    if executable is None:
        raise RuntimeError("The `claude` CLI is not on PATH")
    return executable
