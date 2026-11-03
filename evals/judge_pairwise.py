"""Compare agentic runs pairwise and blind: which of two changes would a strict reviewer rather merge?

Usage: python evals/judge_pairwise.py [--model opus] [--coder sonnet] [--split test]
                                      [--pairs this-repo:none,this-repo:ub-mode | --conditions A,B,C] [--jobs 4]
For every case, repetition and pair of conditions, the judge sees the fixture repo, both diffs and both final
reports twice, once in each order, so position bias cancels out. Cues that reveal a skill (heuristic codes such
as G25, mentions of "the skill", paths of its reference files) are removed first. Each verdict carries a
rationale, so the results say why one change won, not only that it did.
By default this repo's skill is compared with every other condition; `--pairs` judges only the listed pairs and
`--conditions` every pair of the listed conditions.
Writes results/agentic/<coder>/pairwise/<case>/r<n>-<X>-vs-<Y>.json. A verdict is kept until one of its runs changes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from itertools import combinations
from pathlib import Path

from agentic import AgenticCase, coder_models, load_agentic_cases, results_dir
from harness import ALL_CONDITIONS, CONDITIONS, THIS_REPO, ask_claude, extract_json, write_text_atomic

DEFAULT_PAIRS = ",".join(
    f"{THIS_REPO}:{condition.name}" for condition in CONDITIONS if condition.name != THIS_REPO
)
CONDITION_ORDER = [condition.name for condition in ALL_CONDITIONS]
JUDGE_SYSTEM_PROMPT = (
    "You are a strict senior engineer deciding which of two pull requests for the same task to merge. "
    "You only output JSON."
)
WINNER_SCORE = {"A": 1.0, "tie": 0.5, "B": 0.0}
# Aspects of clean code the judge rates separately, so a result says where one change is better, not only that it is.
DIMENSIONS = {
    "correctness": "Does the change do the right thing, and does behavior that should stay the same stay the same?",
    "scope": "Does it change only what the task needs, without unrelated edits or leftovers?",
    "design": "Is the structure simple: existing code reused, no duplication, no needless abstraction, errors "
    "handled visibly?",
    "readability": "Are names, function size and comments easy for the next developer to follow?",
    "tests": "Do the tests protect the new or changed behavior, including its edge cases?",
    "report": "Is the final report accurate and complete about what was changed and verified?",
}
SKIPPED_REPO_DIRS = {"node_modules", "__pycache__"}
SKILL_CUES = [
    re.compile(r"\s?\((?:[CEFGNT]\d{1,2}(?:\s*[,/]\s*)?)+\)"),
    re.compile(r"\b[CEFGNT]\d{1,2}\b(?:\s*[,/]\s*\b[CEFGNT]\d{1,2}\b)*"),
    re.compile(r"\b(?:the |this )?(?:clean[- ]code )?skill(?:'s)?\b", re.IGNORECASE),
    re.compile(r"\S*references/[\w-]+\.md"),
]


@dataclass(frozen=True)
class Comparison:
    coder: str
    case: AgenticCase
    rep: int
    first: str
    second: str

    @property
    def path(self) -> Path:
        return (
            results_dir(self.coder, "pairwise")
            / self.case.case_id
            / f"r{self.rep}-{self.first}-vs-{self.second}.json"
        )

    def run_dir(self, condition: str) -> Path:
        return results_dir(self.coder, "runs") / self.case.case_id / f"{condition}-r{self.rep}"

    def fingerprints(self) -> dict[str, str]:
        return {condition: _fingerprint(self.run_dir(condition)) for condition in (self.first, self.second)}

    def is_current(self) -> bool:
        """A stored verdict counts only while both runs are byte for byte what the judge saw."""
        if not self.path.exists():
            return False
        return json.loads(self.path.read_text(encoding="utf-8")).get("fingerprints") == self.fingerprints()


def main() -> None:
    args = _parse_args()
    pairs = _pairs(args)
    coders = [args.coder] if args.coder else coder_models()
    comparisons = [
        Comparison(coder, case, rep, first, second)
        for coder in coders
        for case in load_agentic_cases(args.split)
        for first, second in pairs
        for rep in _reps_with_runs(coder, case, [first, second])
    ]
    pending = [comparison for comparison in comparisons if not comparison.is_current()]
    print(f"{len(comparisons)} comparisons ({2 * len(comparisons)} judge calls), {len(pending)} still to do")

    with ThreadPoolExecutor(max_workers=args.jobs) as pool:
        futures = {pool.submit(_compare, comparison, args.model): comparison for comparison in pending}
        for future in as_completed(futures):
            comparison = futures[future]
            label = (
                f"{comparison.coder} {comparison.case.case_id} r{comparison.rep} "
                f"{comparison.first} vs {comparison.second}"
            )
            try:
                print(f"judged {label}: {comparison.first} scores {future.result():.2f}")
            except (RuntimeError, ValueError, KeyError, OSError, subprocess.TimeoutExpired) as error:
                print(f"FAILED {label}: {error}")


def _pairs(args: argparse.Namespace) -> list[tuple[str, str]]:
    """Condition pairs to judge, each in the canonical condition order so results never split by direction."""
    if args.conditions:
        raw = list(combinations(args.conditions.split(","), 2))
    else:
        raw = [tuple(pair.split(":")) for pair in args.pairs.split(",")]
    unknown = {name for pair in raw for name in pair} - set(CONDITION_ORDER)
    if unknown or any(len(pair) != 2 for pair in raw):
        raise SystemExit(f"Bad pairs or unknown conditions: {sorted(unknown) or raw}")
    return [tuple(sorted(pair, key=CONDITION_ORDER.index)) for pair in raw]  # type: ignore[misc]


def _reps_with_runs(coder: str, case: AgenticCase, conditions: list[str]) -> list[int]:
    case_dir = results_dir(coder, "runs") / case.case_id
    reps = sorted({int(path.parent.name.rsplit("-r", 1)[1]) for path in case_dir.glob("*-r*/meta.json")})
    return [rep for rep in reps if all((case_dir / f"{c}-r{rep}" / "meta.json").exists() for c in conditions)]


def _compare(comparison: Comparison, model: str) -> float:
    """Judge both orders and return the first condition's score: 1 = always preferred, 0.5 = even."""
    orders = []
    for shown_as_a, shown_as_b in (
        (comparison.first, comparison.second),
        (comparison.second, comparison.first),
    ):
        prompt = _judge_prompt(
            comparison.case, _change(comparison, shown_as_a), _change(comparison, shown_as_b)
        )
        reply = ask_claude(prompt, JUDGE_SYSTEM_PROMPT, model, effort="high")
        verdict = extract_json(reply.text)
        if verdict.get("winner") not in WINNER_SCORE:
            raise ValueError(f"unexpected winner {verdict.get('winner')!r}")
        orders.append({"A": shown_as_a, "B": shown_as_b, "model_ids": reply.model_ids, "verdict": verdict})
    first_scores = [
        WINNER_SCORE[orders[0]["verdict"]["winner"]],
        1 - WINNER_SCORE[orders[1]["verdict"]["winner"]],
    ]
    result = {
        "case": comparison.case.case_id,
        "split": comparison.case.split,
        "coder": comparison.coder,
        "rep": comparison.rep,
        "pair": [comparison.first, comparison.second],
        "judge_model": model,
        "fingerprints": comparison.fingerprints(),
        "score": sum(first_scores) / 2,
        "dimension_scores": _dimension_scores(orders),
        # Each order picked a different winner; a tie in one order is not a contradiction.
        "contradictory": set(first_scores) == {0.0, 1.0},
        "orders": orders,
    }
    write_text_atomic(comparison.path, json.dumps(result, indent=2))
    return result["score"]


def _dimension_scores(orders: list[dict]) -> dict[str, float]:
    """Per aspect, the first condition's score averaged over both orders; aspects a verdict left out are skipped."""
    scores = {}
    for name in DIMENSIONS:
        verdicts = [order["verdict"].get("dimensions", {}).get(name) for order in orders]
        if all(verdict in WINNER_SCORE for verdict in verdicts):
            scores[name] = (WINNER_SCORE[verdicts[0]] + 1 - WINNER_SCORE[verdicts[1]]) / 2
    return scores


def _change(comparison: Comparison, condition: str) -> str:
    run_dir = comparison.run_dir(condition)
    diff = (run_dir / "review.diff").read_text(encoding="utf-8")
    report = (run_dir / "report.md").read_text(encoding="utf-8")
    return f"<diff>\n{_without_skill_cues(diff) or '(no changes)'}\n</diff>\n<report>\n{_without_skill_cues(report)}\n</report>"


def _fingerprint(run_dir: Path) -> str:
    """Hash of everything the judge sees from a run."""
    digest = hashlib.sha256()
    for name in ("review.diff", "report.md"):
        digest.update((run_dir / name).read_bytes())
    return digest.hexdigest()[:16]


def _without_skill_cues(text: str) -> str:
    for cue in SKILL_CUES:
        text = cue.sub("", text)
    return text


def _repository(case: AgenticCase) -> str:
    def shown(path: Path) -> bool:
        directories = path.relative_to(case.repo_dir).parts[:-1]
        return not any(part.startswith(".") or part in SKIPPED_REPO_DIRS for part in directories)

    files = [path for path in sorted(case.repo_dir.rglob("*")) if path.is_file() and shown(path)]
    return "\n\n".join(
        f'<file path="{path.relative_to(case.repo_dir).as_posix()}">\n{path.read_text(encoding="utf-8")}</file>'
        for path in files
    )


def _judge_prompt(case: AgenticCase, change_a: str, change_b: str) -> str:
    return f"""Two coding agents worked on the same task in the same repository. Each produced a change (a git diff
against the original repository) and a final report to the developer. Decide which pull request you would rather merge.

<repository>
{_repository(case)}
</repository>

<task>
{case.prompt}
</task>

<change id="A">
{change_a}
</change>

<change id="B">
{change_b}
</change>

Weigh what a careful reviewer cares about: correct and preserved behavior; doing what was asked and no more;
reuse of existing code; readability; tests that protect the change; a report that is accurate about what was
changed and verified. Length is not a merit. You cannot run the code, so reason from the repository and the diffs.
Answer "tie" only when you would be equally happy to merge either.

Then compare the two changes on each of these aspects separately, "tie" where they do not differ:
{_dimension_list()}

Return only this JSON:
{{"winner": "A" | "B" | "tie", "margin": "slight" | "clear", "rationale": "2-4 sentences",
"a_issues": ["..."], "b_issues": ["..."],
"dimensions": {{{", ".join(f'"{name}": "A" | "B" | "tie"' for name in DIMENSIONS)}}}}}"""


def _dimension_list() -> str:
    return "\n".join(f"- {name}: {question}" for name, question in DIMENSIONS.items())


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Judge agentic runs pairwise and blind.")
    parser.add_argument("--model", default="opus", help="judge model")
    parser.add_argument("--coder", help="judge only the runs of this coder model (default: all)")
    parser.add_argument("--split", choices=["dev", "test"], help="judge only this split (default: all cases)")
    parser.add_argument(
        "--pairs", default=DEFAULT_PAIRS, help="judge these pairs (default: this repo vs each other)"
    )
    parser.add_argument("--conditions", help="instead, judge every pair of these conditions")
    parser.add_argument("--jobs", type=int, default=4, help="parallel comparisons")
    return parser.parse_args()


if __name__ == "__main__":
    main()
