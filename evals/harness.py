"""Shared pieces of the eval harness: test cases, skill variants and isolated `claude -p` calls."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import time
import urllib.error
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

CANDIDATES_DIR = EVALS_DIR / "candidates"

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
    language: str
    prompt: str
    assertions: list[str]


LANGUAGES = ("TypeScript", "JavaScript", "Python", "Kotlin", "Java", "Rust", "Go", "C#")


def language_of(title: str) -> str:
    """The language a case title names, as in "Bugfix in a legacy module (Python)" or "Error handling in Go"."""
    for language in LANGUAGES:
        if re.search(rf"(?<!\w){re.escape(language)}(?![\w#])", title):
            return language
    raise ValueError(f"Case title names none of {LANGUAGES}: {title!r}")


@dataclass(frozen=True)
class Skill:
    """A skill as an agent has it installed: a folder, and the SKILL.md in it that gets loaded."""

    directory: Path
    entry: str = "SKILL.md"

    def text(self) -> str:
        return (self.directory / self.entry).read_text(encoding="utf-8")

    @property
    def name(self) -> str:
        """The `name` in the frontmatter of the loaded SKILL.md."""
        match = re.search(r"^name:\s*(\S+)", self.text(), flags=re.MULTILINE)
        return match.group(1) if match else self.directory.name

    def installed_folders(self) -> dict[str, Path]:
        """The skill folders an installer puts into a skills directory, by folder name.

        A single skill is one folder named after the skill; a pack (its loaded SKILL.md sits in a subfolder) installs
        every subfolder that has a SKILL.md.
        """
        if (self.directory / self.entry).parent == self.directory:
            return {self.name: self.directory}
        return {path.parent.name: path.parent for path in sorted(self.directory.glob("*/SKILL.md"))}

    def fingerprint(self) -> str:
        """Hash of every file in the folder, so each result records which version of the skill it measured.

        The `version:` line in a SKILL.md frontmatter is left out: a release bump changes no rule, so it must not
        turn finished runs into stale ones.
        """
        digest = hashlib.sha256()
        for path in sorted(path for path in self.directory.rglob("*") if path.is_file()):
            content = path.read_bytes().replace(b"\r\n", b"\n")
            if path.name == "SKILL.md":
                content = _without_version_line(content)
            digest.update(path.relative_to(self.directory).as_posix().encode())
            digest.update(content)
        return digest.hexdigest()[:16]


FRONTMATTER_VERSION = re.compile(rb"^[ \t]*version:[^\n]*\n", re.MULTILINE)


def _without_version_line(skill_md: bytes) -> bytes:
    """The SKILL.md without the `version:` line of its frontmatter; the body is left as it is."""
    if not skill_md.startswith(b"---\n"):
        return skill_md
    end = skill_md.find(b"\n---", 3)
    if end < 0:
        return skill_md
    frontmatter, body = skill_md[: end + 1], skill_md[end + 1 :]
    return FRONTMATTER_VERSION.sub(b"", frontmatter, count=1) + body


@dataclass(frozen=True)
class LocalSkill:
    folder: str  # relative to the repo
    entry: str = "SKILL.md"

    def resolve(self) -> Skill:
        return Skill(REPO_DIR / self.folder, self.entry)


@dataclass(frozen=True)
class GitHubSkill:
    """A published skill pinned to a commit: the files its install instructions put into the skills folder."""

    repo: str
    commit: str
    folder: str
    files: tuple[str, ...] = ()  # empty: every file in the folder at that commit
    entry: str = "SKILL.md"

    @property
    def _cache_key(self) -> str:
        return f"{self.repo.replace('/', '__')}@{self.commit[:10]}"

    def resolve(self) -> Skill:
        directory = CACHE_DIR / "skills" / self._cache_key / self.folder
        for name in self.files or self._folder_files():
            target = directory / name
            if not target.exists():
                path = "/".join(part for part in (self.folder, name) if part)
                target.parent.mkdir(parents=True, exist_ok=True)
                url = f"https://raw.githubusercontent.com/{self.repo}/{self.commit}/{path}"
                partial = target.with_name(
                    f"{target.name}.partial"
                )  # an interrupted download never looks finished
                with urllib.request.urlopen(url, timeout=30) as response:
                    partial.write_bytes(response.read())
                os.replace(partial, target)
        return Skill(directory, self.entry)

    def _folder_files(self) -> list[str]:
        """Every file in the folder at the pinned commit, listed once through the GitHub API and then cached."""
        listing = CACHE_DIR / "skills" / f"{self._cache_key}.files.json"
        if not listing.exists():
            url = f"https://api.github.com/repos/{self.repo}/git/trees/{self.commit}?recursive=1"
            with urllib.request.urlopen(url, timeout=30) as response:
                tree = json.load(response)
            if tree.get("truncated"):
                raise RuntimeError(f"GitHub returned a truncated file list for {self.repo}@{self.commit}")
            prefix = f"{self.folder}/" if self.folder else ""
            names = [
                entry["path"].removeprefix(prefix)
                for entry in tree["tree"]
                if entry["type"] == "blob" and entry["path"].startswith(prefix)
            ]
            if self.entry not in names:
                raise RuntimeError(f"{self.repo}@{self.commit} has no {self.entry} in '{self.folder}'")
            write_text_atomic(listing, json.dumps(names, indent=2))
        return json.loads(listing.read_text(encoding="utf-8"))


SkillSource = LocalSkill | GitHubSkill
ANY_LANGUAGE = "*"


@dataclass(frozen=True)
class Condition:
    """What the agent gets: no skill, or for each language the skill it would install for it.

    A condition without a source for a case's language does not run that case; it is not counted as a loss.
    """

    name: str
    label: str
    sources: tuple[tuple[str, SkillSource], ...] = ()  # (language or ANY_LANGUAGE, source); empty: no skill
    # What a project would write into its CLAUDE.md, for the agentic track only. It is appended to the system
    # prompt: with CLAUDE.md files switched on, Claude Code also loads the user's own ~/.claude/CLAUDE.md.
    project_instructions: str = ""
    # Added after the single-turn suite was graded. Its judge grades all conditions of a case in one call, so a new
    # condition there would change every published single-turn number.
    agentic_only: bool = False

    def applies_to(self, language: str) -> bool:
        return not self.sources or self._source(language) is not None

    def skill(self, language: str) -> Skill | None:
        source = self._source(language)
        return source.resolve() if source else None

    def fingerprint(self, language: str) -> str | None:
        """What a run of this condition measured: its skill's files or its CLAUDE.md text; None for no skill."""
        skill = self.skill(language)
        if skill is not None:
            return skill.fingerprint()
        if self.project_instructions:
            return hashlib.sha256(self.project_instructions.encode()).hexdigest()[:16]
        return None

    def system_prompt(self, language: str) -> str:
        skill = self.skill(language)
        if skill is None:
            return BASE_SYSTEM_PROMPT
        return (
            f"{BASE_SYSTEM_PROMPT}\n\n{SKILL_PREAMBLE}\n\n<skill>\n{skill.text()}\n</skill>\n\n{SKILL_FOOTER}"
        )

    def _source(self, language: str) -> SkillSource | None:
        by_language = dict(self.sources)
        return by_language.get(language) or by_language.get(ANY_LANGUAGE)


def _ertugrul_track(track: str) -> GitHubSkill:
    """One language track of ertugrul-dmr/clean-code-skills, loaded through its master skill as its README advises."""
    skills = ("boy-scout", "clean-comments", "clean-functions", "clean-general", "clean-names", "clean-tests")
    master = f"{track}-clean-code"
    return GitHubSkill(
        "ertugrul-dmr/clean-code-skills",
        "1b6b3cc1264b8fbe921c65002d05a3bf90ede178",
        f"skills/{track}",
        tuple(f"{name}/SKILL.md" for name in (*skills, master)),
        entry=f"{master}/SKILL.md",
    )


THIS_REPO = "this-repo"
NO_SKILL = "none"
CLAUDEMD_BASELINE = "claudemd-baseline"
# The habits the skill's lead comes from (tests, a scoped diff, an honest report) in four sentences, as a project
# would write them into CLAUDE.md. It shows how much of the lead a cheap instruction already gets.
BASELINE_INSTRUCTIONS = (
    "Keep the diff to the task. Add a regression test for every fix and a test for every new behavior. "
    "Run the tests after your last edit. End with a short report that only claims what you actually ran and checked."
)
CONDITIONS = [
    Condition(NO_SKILL, "No skill"),
    Condition(THIS_REPO, "This repo", ((ANY_LANGUAGE, LocalSkill("skills/clean-code")),)),
    Condition(
        "ub-mode",
        "unclebob/ub-mode",
        (
            (
                ANY_LANGUAGE,
                GitHubSkill(
                    "unclebob/ub-mode", "3da62bf3fcfd2034de41f30d920d2739e566171f", "", ("SKILL.md",)
                ),
            ),
        ),
    ),
    Condition(
        "sickn33",
        "sickn33/clean-code",
        (
            (
                ANY_LANGUAGE,
                GitHubSkill(
                    "sickn33/agentic-awesome-skills",
                    "bbfc66fe61e8b6ced7d38481c47600e8ac9b8eea",
                    "skills/clean-code",
                    ("SKILL.md",),
                ),
            ),
        ),
    ),
    # Its two tracks cover Python and TypeScript only, so it does not run cases in other languages.
    Condition(
        "ertugrul-dmr",
        "ertugrul-dmr/clean-code",
        (("Python", _ertugrul_track("python")), ("TypeScript", _ertugrul_track("typescript"))),
    ),
    # The whole skill folder (language and framework packs, scripts), as `npx skills add` installs it. Its `init`
    # is a one-time interactive project setup that writes `.clean/`; the skill says plain sessions work without it.
    Condition(
        "btseee",
        "btseee/clean-code",
        (
            (
                ANY_LANGUAGE,
                GitHubSkill(
                    "btseee/clean-code-skills",
                    "49b1354be3ec9d0158c99b1c1c9bc1f833133640",
                    "skills/clean-code",
                ),
            ),
        ),
        agentic_only=True,
    ),
    Condition(
        CLAUDEMD_BASELINE,
        "CLAUDE.md baseline",
        project_instructions=BASELINE_INSTRUCTIONS,
        agentic_only=True,
    ),
]


def candidate_conditions() -> list[Condition]:
    """Skill drafts in `evals/candidates/<name>/` (not committed): measured while developing, never published."""
    return [
        Condition(
            f"candidate-{folder.name}",
            f"Candidate {folder.name}",
            ((ANY_LANGUAGE, LocalSkill(folder.relative_to(REPO_DIR).as_posix())),),
        )
        for folder in sorted(path.parent for path in CANDIDATES_DIR.glob("*/SKILL.md"))
    ]


ALL_CONDITIONS = CONDITIONS + candidate_conditions()
SINGLE_TURN_CONDITIONS = [condition for condition in ALL_CONDITIONS if not condition.agentic_only]


def load_cases() -> list[Case]:
    return [_parse_case(path) for path in sorted(CASES_DIR.glob("*.md"))]


def _parse_case(path: Path) -> Case:
    text = path.read_text(encoding="utf-8")
    title = text.splitlines()[0].removeprefix("# ").strip()
    prompt = markdown_section(text, "Prompt")
    assertions = re.findall(r"^\d+\.\s+(.+)$", markdown_section(text, "Assertions"), flags=re.MULTILINE)
    return Case(
        case_id=path.stem, title=title, language=language_of(title), prompt=prompt, assertions=assertions
    )


def markdown_section(text: str, heading: str) -> str:
    match = re.search(rf"^## {heading}\n(.*?)(?=^## |\Z)", text, flags=re.MULTILINE | re.DOTALL)
    if match is None:
        raise ValueError(f"Case is missing the '## {heading}' section")
    return match.group(1).strip()


@dataclass(frozen=True)
class ClaudeReply:
    text: str
    duration_ms: int
    cost_usd: float | None  # None where the endpoint reports no price
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


GATEWAY_MAX_TOKENS = 16000


def ask_gateway(prompt: str, system_prompt: str, model: str, effort: str | None = None) -> ClaudeReply:
    """One turn through an Anthropic-compatible Messages endpoint, for judge models the `claude` CLI does not know.

    Uses the endpoint and credentials Claude Code itself is configured with: `ANTHROPIC_BASE_URL` plus
    `ANTHROPIC_CUSTOM_HEADERS` (a gateway such as Claudapter that routes to other providers) or `ANTHROPIC_API_KEY`.
    The gateway reports tokens but no price, so the cost is None.
    """
    base_url = os.environ.get("ANTHROPIC_BASE_URL", "https://api.anthropic.com").rstrip("/")
    headers = {"content-type": "application/json", "anthropic-version": "2023-06-01", **_credential_headers()}
    body: dict = {
        "model": model,
        "max_tokens": GATEWAY_MAX_TOKENS,
        "system": system_prompt,
        "messages": [{"role": "user", "content": prompt}],
    }
    if effort:
        body["output_config"] = {"effort": effort}
    request = urllib.request.Request(
        f"{base_url}/v1/messages", data=json.dumps(body).encode("utf-8"), headers=headers
    )
    started = time.monotonic()
    try:
        with urllib.request.urlopen(request, timeout=900) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as error:
        raise RuntimeError(
            f"{model} via {base_url} failed ({error.code}): {error.read().decode()[:300]}"
        ) from error
    text = "".join(
        block.get("text", "") for block in payload.get("content", []) if block.get("type") == "text"
    )
    return ClaudeReply(
        text=text,
        model_ids=[payload.get("model", model)],
        duration_ms=int((time.monotonic() - started) * 1000),
        cost_usd=None,
        output_tokens=payload.get("usage", {}).get("output_tokens", 0),
    )


def _credential_headers() -> dict[str, str]:
    """The credentials Claude Code would send: `ANTHROPIC_CUSTOM_HEADERS` (`Name: value` lines), an API key, a token."""
    custom = os.environ.get("ANTHROPIC_CUSTOM_HEADERS", "")
    headers = {
        name.strip(): value.strip()
        for name, _, value in (line.partition(":") for line in custom.splitlines())
        if name.strip()
    }
    names = {name.lower() for name in headers}
    if os.environ.get("ANTHROPIC_API_KEY") and "x-api-key" not in names:
        headers["x-api-key"] = os.environ["ANTHROPIC_API_KEY"]
    if os.environ.get("ANTHROPIC_AUTH_TOKEN") and "authorization" not in names:
        headers["Authorization"] = f"Bearer {os.environ['ANTHROPIC_AUTH_TOKEN']}"
    return headers


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
