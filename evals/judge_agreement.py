"""How far two pairwise judges agree on the same comparisons, and whether the headline changes with the judge.

Usage: python evals/judge_agreement.py --other gpt-6.1-sol [--coder sonnet] [--split test]
Reads the default judge's verdicts from results/agentic/<coder>/pairwise/ and the other judge's from
pairwise-<other>/, matches them by case, repetition and pair, and writes results/agentic/judge-agreement.md:
per pair the share of verdicts the first condition won under each judge, the share of comparisons on which both
judges prefer the same side, Cohen's kappa for that, and the same per dimension. Costs nothing.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter

from agentic import AGENTIC_RESULTS_DIR, results_dir
from harness import write_text_atomic
from judge_pairwise import DEFAULT_JUDGE, DIMENSIONS, verdicts_kind

REPORT = AGENTIC_RESULTS_DIR / "judge-agreement.md"
OUTCOMES = ("first", "tie", "second")


def preferred(score: float) -> str:
    """Which side a comparison score favors: 1 means the first condition won both orders."""
    if score > 0.5:
        return "first"
    return "second" if score < 0.5 else "tie"


def load_verdicts(coder: str, judge: str, split: str | None) -> dict[tuple, dict]:
    """A judge's verdicts keyed by (case, rep, first condition, second condition)."""
    verdicts = {}
    for path in sorted(results_dir(coder, verdicts_kind(judge)).glob("*/*.json")):
        verdict = json.loads(path.read_text(encoding="utf-8"))
        if split in (None, verdict["split"]):
            verdicts[(verdict["case"], verdict["rep"], *verdict["pair"])] = verdict
    return verdicts


def cohens_kappa(pairs: list[tuple[str, str]]) -> float | None:
    """Agreement beyond chance between two raters over the same items; None when chance already explains all."""
    if not pairs:
        return None
    observed = sum(a == b for a, b in pairs) / len(pairs)
    left, right = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    expected = sum(left[o] * right[o] for o in OUTCOMES) / len(pairs) ** 2
    return None if expected == 1 else (observed - expected) / (1 - expected)


def kappa_text(kappa: float | None) -> str:
    return "–" if kappa is None else f"{kappa:.2f}"


def agreement_rows(base: dict[tuple, dict], other: dict[tuple, dict]) -> list[str]:
    # Only verdicts on the same version of both runs are comparable.
    shared = sorted(
        key for key in base.keys() & other.keys() if base[key]["fingerprints"] == other[key]["fingerprints"]
    )
    by_pair: dict[tuple[str, str], list[tuple]] = {}
    for key in shared:
        by_pair.setdefault((key[2], key[3]), []).append(key)
    lines = [
        "| Pair | Comparisons | First wins, default judge | First wins, other judge | Same side | Kappa |",
        "|---|---|---|---|---|---|",
    ]
    rows = [(f"{first} vs {second}", keys) for (first, second), keys in sorted(by_pair.items())]
    for label, keys in [*rows, ("all pairs, pooled", shared)]:
        sides = [(preferred(base[k]["score"]), preferred(other[k]["score"])) for k in keys]
        base_score = sum(base[k]["score"] for k in keys) / len(keys)
        other_score = sum(other[k]["score"] for k in keys) / len(keys)
        same = sum(a == b for a, b in sides) / len(sides)
        lines.append(
            f"| {label} | {len(keys)} | {base_score:.2f} | {other_score:.2f} | {same:.0%} "
            f"| {kappa_text(cohens_kappa(sides))} |"
        )
    lines += ["", "| Dimension | Same side | Kappa |", "|---|---|---|"]
    for name in DIMENSIONS:
        sides = [
            (preferred(base[k]["dimension_scores"][name]), preferred(other[k]["dimension_scores"][name]))
            for k in shared
            if name in base[k]["dimension_scores"] and name in other[k]["dimension_scores"]
        ]
        if sides:
            same = sum(a == b for a, b in sides) / len(sides)
            lines.append(f"| {name} | {same:.0%} | {kappa_text(cohens_kappa(sides))} |")
    return lines


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare two pairwise judges on the same comparisons.")
    parser.add_argument(
        "--other", required=True, help="the second judge model, as passed to judge_pairwise.py"
    )
    parser.add_argument("--coder", default="sonnet", help="coder model whose comparisons were judged twice")
    parser.add_argument("--split", choices=["dev", "test"], default="test")
    args = parser.parse_args()
    base = load_verdicts(args.coder, DEFAULT_JUDGE, args.split)
    other = load_verdicts(args.coder, args.other, args.split)
    if not base.keys() & other.keys():
        raise SystemExit(f"No comparison was judged by both {DEFAULT_JUDGE} and {args.other}")
    lines = [
        f"# Judge agreement: {DEFAULT_JUDGE} and {args.other}",
        "",
        f"Coder {args.coder}, {args.split} cases. A score is the share of verdicts the first condition of the pair",
        "won (ties count half). Same side: both judges prefer the same condition, or both call it even. The pooled",
        "kappa mixes pairs with different base rates; read the per-pair rows first.",
        "",
        *agreement_rows(base, other),
    ]
    write_text_atomic(REPORT, "\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
