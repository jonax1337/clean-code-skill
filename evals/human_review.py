"""A blind sample of pull-request pairs for a human to rate, and how the human's verdicts compare with the judges'.

Usage: python evals/human_review.py sample [--n 15] [--seed 2026]
       python evals/human_review.py score [--other gpt-6.1-sol]
`sample` draws comparisons the judges rated (Sonnet, held-out cases, this repo against no skill and against the
CLAUDE.md baseline), shows each pair under the letters A and B in a random order, and writes
results/agentic/human/pairs.md to read and ratings.csv to fill in. Which condition wrote which change is in
key.json; open it only after rating. The changes are shown as the judge saw them, with skill cues removed.
`score` reads ratings.csv (winner A, B or tie per id) and reports, for each judge, how often it prefers the same
side as the human, with Cohen's kappa. Costs nothing.
"""

from __future__ import annotations

import argparse
import csv
import json
import random

from agentic import AGENTIC_RESULTS_DIR, load_agentic_cases
from harness import CLAUDEMD_BASELINE, NO_SKILL, THIS_REPO, write_text_atomic
from judge_agreement import cohens_kappa, kappa_text, load_verdicts, preferred
from judge_pairwise import DEFAULT_JUDGE, Comparison, shown_change

HUMAN_DIR = AGENTIC_RESULTS_DIR / "human"
PAIRS_FILE = HUMAN_DIR / "pairs.md"
KEY_FILE = HUMAN_DIR / "key.json"
RATINGS_FILE = HUMAN_DIR / "ratings.csv"
CODER = "sonnet"
SAMPLED_PAIRS = {(NO_SKILL, THIS_REPO), (THIS_REPO, CLAUDEMD_BASELINE)}


def sample(count: int, seed: int, force: bool) -> None:
    if _rated(_read_ratings()) and not force:
        raise SystemExit(
            f"{RATINGS_FILE} already holds ratings; a new sample would replace them (use --force)"
        )
    cases = {case.case_id: case for case in load_agentic_cases("test")}
    verdicts = {
        key: verdict
        for key, verdict in load_verdicts(CODER, DEFAULT_JUDGE, "test").items()
        if Comparison(CODER, cases[key[0]], key[1], key[2], key[3]).is_current()
    }
    rng = random.Random(seed)
    # As many items per pair as possible, so the contested pair is not drowned out by the one with more runs.
    chosen = []
    for index, pair in enumerate(sorted(SAMPLED_PAIRS)):
        keys = sorted(key for key in verdicts if (key[2], key[3]) == pair)
        share = count // len(SAMPLED_PAIRS) + (index < count % len(SAMPLED_PAIRS))
        chosen += rng.sample(keys, min(share, len(keys)))
    rng.shuffle(chosen)
    sections, key_entries = [PAIRS_INTRO], {}
    for number, (case_id, rep, first, second) in enumerate(chosen, start=1):
        item_id = f"P{number:02d}"
        case = cases[case_id]
        shown = [first, second]
        rng.shuffle(shown)
        comparison = Comparison(CODER, case, rep, first, second)
        key_entries[item_id] = {
            "case": case_id,
            "rep": rep,
            "pair": [first, second],
            "A": shown[0],
            "B": shown[1],
        }
        sections.append(
            f"## {item_id}: {case.title}\n\n"
            f"Repository: `evals/cases-agentic/{case.split}/{case_id}/repo/`\n\n"
            f"### Task\n\n{case.prompt}\n\n"
            f"### Change A\n\n{_fenced(shown_change(comparison, shown[0]))}\n\n"
            f"### Change B\n\n{_fenced(shown_change(comparison, shown[1]))}\n"
        )
    HUMAN_DIR.mkdir(parents=True, exist_ok=True)
    write_text_atomic(PAIRS_FILE, "\n".join(sections))
    write_text_atomic(KEY_FILE, json.dumps({"seed": seed, "items": key_entries}, indent=2))
    with RATINGS_FILE.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["id", "winner", "notes"])
        writer.writerows([item_id, "", ""] for item_id in key_entries)
    print(f"{len(chosen)} pairs in {PAIRS_FILE}; rate them in {RATINGS_FILE} (winner: A, B or tie)")


PAIRS_INTRO = """# Blind pull-request pairs

Two coding agents did the same task. For each pair, decide which pull request you would rather merge, as a strict
reviewer: correct and preserved behavior, only what was asked, reuse, readability, tests that protect the change,
and a report that is accurate about what was changed and verified. Length is not a merit.

Write A, B or tie into the `winner` column of `ratings.csv`. Do not open `key.json` before you are done.
"""


def _fenced(change: str) -> str:
    return f"````text\n{change}\n````"


def score(other: str | None) -> None:
    key = json.loads(KEY_FILE.read_text(encoding="utf-8"))["items"]
    ratings = _rated(_read_ratings())
    unknown = sorted(set(ratings) - set(key))
    invalid = sorted(item_id for item_id, winner in ratings.items() if winner not in ("A", "B", "TIE"))
    if unknown or invalid:
        raise SystemExit(
            f"In {RATINGS_FILE}: unknown ids {unknown}, winners other than A, B or tie for {invalid}"
        )
    human = {item_id: _human_side(key[item_id], winner) for item_id, winner in ratings.items()}
    if not human:
        raise SystemExit(f"No ratings yet in {RATINGS_FILE}")
    print(f"{len(human)} pairs rated")
    print("| Judge | Rated pairs it also judged | Same side as you | Kappa |")
    print("|---|---|---|---|")
    for judge in [DEFAULT_JUDGE, *([other] if other else [])]:
        verdicts = load_verdicts(CODER, judge, "test")
        sides = [
            (side, preferred(verdicts[_verdict_key(key[item_id])]["score"]))
            for item_id, side in human.items()
            if _verdict_key(key[item_id]) in verdicts
        ]
        if not sides:
            print(f"| {judge} | 0 | – | – |")
            continue
        same = sum(a == b for a, b in sides) / len(sides)
        print(f"| {judge} | {len(sides)} | {same:.0%} | {kappa_text(cohens_kappa(sides))} |")


def _read_ratings() -> dict[str, str]:
    """Id to winner as typed. Spreadsheet saves are accepted: a byte-order mark, `;` instead of `,`."""
    if not RATINGS_FILE.exists():
        return {}
    lines = RATINGS_FILE.read_text(encoding="utf-8-sig").splitlines()
    dialect = csv.Sniffer().sniff(lines[0], delimiters=",;")
    return {
        row["id"].strip(): (row["winner"] or "").strip().upper()
        for row in csv.DictReader(lines, dialect=dialect)
    }


def _rated(ratings: dict[str, str]) -> dict[str, str]:
    return {item_id: winner for item_id, winner in ratings.items() if winner}


def _human_side(item: dict, winner: str) -> str:
    """The human's choice as the side of the stored pair (first or second condition), or tie."""
    if winner == "TIE":
        return "tie"
    return "first" if item[winner] == item["pair"][0] else "second"


def _verdict_key(item: dict) -> tuple:
    return (item["case"], item["rep"], *item["pair"])


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Blind pull-request pairs for a human, and the human's agreement."
    )
    commands = parser.add_subparsers(dest="command", required=True)
    sample_parser = commands.add_parser("sample", help="write the blind pairs and an empty ratings file")
    sample_parser.add_argument("--n", type=int, default=15, help="number of pairs")
    sample_parser.add_argument(
        "--seed", type=int, default=2026, help="random seed, so the sample can be redrawn"
    )
    sample_parser.add_argument(
        "--force", action="store_true", help="replace a ratings file that holds ratings"
    )
    score_parser = commands.add_parser("score", help="compare the ratings with the judges")
    score_parser.add_argument("--other", help="a second judge model whose verdicts to compare as well")
    args = parser.parse_args()
    if args.command == "sample":
        sample(args.n, args.seed, args.force)
    else:
        score(args.other)


if __name__ == "__main__":
    main()
