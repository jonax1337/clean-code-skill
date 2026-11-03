"""Summarize the agentic track per coder model and split: checks passed, cost and blind pairwise preferences.

Usage: python evals/report_agentic.py
Reads results/agentic/<model>/{runs,checks,pairwise} and writes results/agentic/summary.md, summary.json,
rationales.md (every judge verdict with its reasons) and the README charts docs/assets/agentic-*.svg.
Every estimate weights the cases equally. Confidence intervals are percentile bootstraps that resample runs within
each case, so they describe these cases; they say nothing about how other tasks would turn out.
"""

from __future__ import annotations

import json
import random
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from html import escape
from pathlib import Path
from statistics import mean

from agentic import AGENTIC_RESULTS_DIR, SPLITS, coder_models, load_agentic_cases, results_dir
from charts import ASSETS_DIR, chart_frame, row_highlight, short_label
from harness import ALL_CONDITIONS, CONDITIONS, NO_SKILL, THIS_REPO, write_text_atomic

LABELS = {condition.name: condition.label for condition in ALL_CONDITIONS}
ORDER = [condition.name for condition in ALL_CONDITIONS]
REFERENCES = [NO_SKILL, THIS_REPO]  # conditions every other condition is compared against
OPPONENTS = [condition.name for condition in CONDITIONS if condition.name != THIS_REPO]
WINNER_SCORE = {"A": 1.0, "tie": 0.5, "B": 0.0}
RESAMPLES = 10_000

# Runs where the skill is installed as a project skill instead of appended, by results folder.
TRIGGER_MODES = {
    "installed": "Installed, nothing mentions it (the agent decides whether to load the skill)",
    "instructed": "Installed, with the CLAUDE.md line that asks the agent to load it",
}
CHART_MODEL_ORDER = ("sonnet", "opus", "haiku")  # the order of the README tables
CHECKS_CHART_MODEL = "sonnet"
CHECKS_CHART_CONDITIONS = [condition.name for condition in CONDITIONS]
SPLIT_PANELS = {
    "dev": ("Dev tasks", "used while developing the skill"),
    "test": ("Held-out tasks", "written without the skill"),
}
MODEL_ID = re.compile(r"claude-([a-z]+)-(\d+)-(\d+)")
SEGMENT_GAP = 2  # surface gap between the blocks of a segmented bar
MIN_LABELLED_BLOCK = 30  # narrower blocks print no count; the tooltip and the README table still carry it
BAR_END_RADIUS = 4

ByCase = dict[str, list[float]]


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]  # stdout is a TextIOWrapper here
    cases = {case.case_id: case for case in load_agentic_cases()}
    summary, lines, rationales = {}, _intro(), ["# Judge rationales", ""]
    for model in coder_models():
        grades = _load(results_dir(model, "checks"))
        comparisons = _load(results_dir(model, "pairwise"))
        if not grades:
            continue
        summary[model] = {}
        lines += ["", f"## Coder: {model}"]
        for split in SPLITS:
            split_grades = [grade for grade in grades if cases[grade["case"]].split == split]
            if not split_grades:
                continue
            split_comparisons = [item for item in comparisons if cases[item["case"]].split == split]
            stats = _split_stats(model, split_grades, split_comparisons)
            summary[model][split] = stats
            lines += _split_markdown(split, stats)
        lines += _checks_markdown(grades, cases)
        for kind, title in TRIGGER_MODES.items():
            stats = _installed_stats(model, kind)
            if stats:
                summary[model][kind] = stats
                lines += _installed_markdown(title, stats)
        rationales += _rationales_markdown(model, comparisons)
    if not summary:
        raise SystemExit("No graded runs found. Run evals/grade_agentic.py first.")
    write_text_atomic(AGENTIC_RESULTS_DIR / "summary.json", json.dumps(summary, indent=2))
    write_text_atomic(AGENTIC_RESULTS_DIR / "summary.md", "\n".join(lines) + "\n")
    write_text_atomic(AGENTIC_RESULTS_DIR / "rationales.md", "\n".join(rationales) + "\n")
    _write_charts(summary)
    print("\n".join(lines))


def _load(directory: Path) -> list[dict]:
    return [json.loads(path.read_text(encoding="utf-8")) for path in sorted(directory.glob("*/*.json"))]


def _split_stats(model: str, grades: list[dict], comparisons: list[dict]) -> dict:
    conditions = [name for name in ORDER if any(grade["condition"] == name for grade in grades)]
    shares = {name: _check_shares(name, grades) for name in conditions}
    return {
        "cases": len({grade["case"] for grade in grades}),
        "conditions": {name: _condition_stats(model, name, grades, shares) for name in conditions},
        "pairwise": _pairwise_stats(comparisons),
    }


def _check_shares(name: str, grades: list[dict]) -> ByCase:
    """Per case, the share of checks each run of the condition passed."""
    by_case: ByCase = defaultdict(list)
    for grade in grades:
        if grade["condition"] == name:
            by_case[grade["case"]].append(mean(check["passed"] for check in grade["checks"]))
    return dict(by_case)


def _condition_stats(model: str, name: str, grades: list[dict], shares: dict[str, ByCase]) -> dict:
    own = [grade for grade in grades if grade["condition"] == name]
    metas = [_meta(model, grade) for grade in own]
    stats = {
        "runs": len(own),
        "checks_passed": _case_mean(shares[name]),
        "checks_passed_ci": bootstrap_ci(shares[name]),
        "runs_all_passed": sum(all(check["passed"] for check in grade["checks"]) for grade in own),
        "cost_usd": mean(meta["cost_usd"] for meta in metas),
        "turns": mean(meta["num_turns"] for meta in metas),
        "duration_s": mean(meta["duration_ms"] for meta in metas) / 1000,
        "runs_reading_skill_files": sum(bool(meta["skill_files_read"]) for meta in metas),
        "metrics": _metrics_stats(own),
        "deltas": {},
    }
    for reference in REFERENCES:
        if reference in shares and reference != name and shares[reference].keys() == shares[name].keys():
            stats["deltas"][reference] = {
                "delta": _case_mean(shares[name]) - _case_mean(shares[reference]),
                "ci": bootstrap_ci(shares[name], minus=shares[reference]),
            }
    return stats


def _metrics_stats(grades: list[dict]) -> dict:
    """Function metrics of the changed source files, averaged over runs; positive deltas mean the run added some."""
    measured = [grade["metrics"] for grade in grades if grade.get("metrics", {}).get("files")]
    if not measured:
        return {}

    def added(key: str) -> list[int]:
        return [metrics["after"][key] - metrics["before"][key] for metrics in measured]

    return {
        "runs": len(measured),
        "long_functions_added": mean(added("long_functions")),
        "complex_functions_added": mean(added("complex_functions")),
        "runs_adding_long_function": mean(delta > 0 for delta in added("long_functions")),
        "runs_adding_complex_function": mean(delta > 0 for delta in added("complex_functions")),
        "max_nloc_after": mean(metrics["after"]["max_nloc"] for metrics in measured),
        "max_ccn_after": mean(metrics["after"]["max_ccn"] for metrics in measured),
    }


def _meta(model: str, grade: dict) -> dict:
    run_dir = results_dir(model, "runs") / grade["case"] / f"{grade['condition']}-r{grade['rep']}"
    return json.loads((run_dir / "meta.json").read_text(encoding="utf-8"))


def _pairwise_stats(comparisons: list[dict]) -> dict:
    by_pair: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for comparison in comparisons:
        by_pair[tuple(comparison["pair"])].append(comparison)
    stats = {}
    for (first, second), items in sorted(by_pair.items(), key=lambda item: [ORDER.index(n) for n in item[0]]):
        scores: ByCase = defaultdict(list)
        for item in items:
            scores[item["case"]].append(item["score"])
        flat = [item["score"] for item in items]
        stats[f"{first} vs {second}"] = {
            "first": first,
            "second": second,
            "units": len(items),
            "first_score": _case_mean(scores),
            "first_score_ci": bootstrap_ci(scores),
            "first_wins": sum(score > 0.5 for score in flat),
            "ties": sum(score == 0.5 for score in flat),
            "second_wins": sum(score < 0.5 for score in flat),
            "contradictory": mean(_is_contradictory(item) for item in items),
            "dimension_scores": _dimension_means(items),
        }
    return stats


def _dimension_means(comparisons: list[dict]) -> dict[str, float]:
    """Per clean-code aspect the judge rated, the first condition's case-weighted score."""
    by_dimension: dict[str, ByCase] = defaultdict(lambda: defaultdict(list))
    for comparison in comparisons:
        for name, score in comparison.get("dimension_scores", {}).items():
            by_dimension[name][comparison["case"]].append(score)
    return {name: _case_mean(scores) for name, scores in by_dimension.items()}


def _is_contradictory(comparison: dict) -> bool:
    """Each order of the same pair picked a different winner."""
    first, second = comparison["orders"]
    first_scores = {WINNER_SCORE[first["verdict"]["winner"]], 1 - WINNER_SCORE[second["verdict"]["winner"]]}
    return first_scores == {0.0, 1.0}


def bootstrap_ci(by_case: ByCase, minus: ByCase | None = None) -> list[float]:
    """95 % interval of the case-weighted mean (or of its difference to `minus`), resampling within each case."""
    rng = random.Random(0)
    estimates = sorted(
        _resampled_case_mean(by_case, rng) - (_resampled_case_mean(minus, rng) if minus else 0.0)
        for _ in range(RESAMPLES)
    )
    return [estimates[int(0.025 * RESAMPLES)], estimates[int(0.975 * RESAMPLES) - 1]]


def _case_mean(by_case: ByCase) -> float:
    return mean(mean(values) for values in by_case.values())


def _resampled_case_mean(by_case: ByCase, rng: random.Random) -> float:
    return mean(mean(rng.choices(values, k=len(values))) for values in by_case.values())


def _intro() -> list[str]:
    return [
        "# Agentic eval results",
        "",
        "A coding agent with Read/Grep/Glob/Edit/Write/Bash works on a fresh copy of a fixture repo; deterministic",
        "checks grade the result and a blind judge compares runs pairwise. `dev` cases may have shaped the skill;",
        "`test` cases are held out. Cases are weighted equally. Brackets are 95 % bootstrap intervals that resample",
        "runs within each case, so they describe these cases only.",
    ]


def _split_markdown(split: str, stats: dict) -> list[str]:
    lines = [
        "",
        f"### {split} cases ({stats['cases']})",
        "",
        "| Condition | Runs | Checks passed | "
        + " | ".join(f"Δ vs {LABELS[reference]}" for reference in REFERENCES)
        + " | Runs passing every check | Avg. cost | Avg. turns |",
        "|---|---|---|" + "---|" * len(REFERENCES) + "---|---|---|",
    ]
    for name, s in stats["conditions"].items():
        low, high = s["checks_passed_ci"]
        deltas = " | ".join(_delta_cell(s["deltas"].get(reference)) for reference in REFERENCES)
        lines.append(
            f"| {LABELS[name]} | {s['runs']} | {s['checks_passed']:.0%} [{low:.0%}–{high:.0%}] | {deltas} | "
            f"{s['runs_all_passed']}/{s['runs']} | ${s['cost_usd']:.3f} | {s['turns']:.1f} |"
        )
    lines += _metrics_markdown(stats["conditions"])
    if stats["pairwise"]:
        lines += _pairwise_markdown(stats["pairwise"])
    return lines


def _metrics_markdown(conditions: dict) -> list[str]:
    rows = [(name, s["metrics"]) for name, s in conditions.items() if s.get("metrics")]
    if not rows:
        return []
    lines = [
        "",
        "Function metrics of the changed source files (lizard; long: more than 30 lines, complex: cyclomatic",
        "complexity above 10). Lower is better; reported, not graded.",
        "",
        (
            "| Condition | Runs | Runs adding a long function | Runs adding a complex function "
            "| Longest function after (lines) | Highest complexity after |"
        ),
        "|---|---|---|---|---|---|",
    ]
    for name, m in rows:
        lines.append(
            f"| {LABELS[name]} | {m['runs']} | {m['runs_adding_long_function']:.0%} | "
            f"{m['runs_adding_complex_function']:.0%} | {m['max_nloc_after']:.1f} | {m['max_ccn_after']:.1f} |"
        )
    return lines


def _pairwise_markdown(pairwise: dict) -> list[str]:
    dimensions = sorted({name for p in pairwise.values() for name in p["dimension_scores"]})
    lines = [
        "",
        "| Blind comparison | Units | Score of first [CI] | First / tie / second | Contradictory | "
        + " | ".join(dimensions)
        + " |",
        "|---|---|---|---|---|" + "---|" * len(dimensions),
    ]
    for p in pairwise.values():
        low, high = p["first_score_ci"]
        aspects = " | ".join(
            f"{p['dimension_scores'][d]:.2f}" if d in p["dimension_scores"] else "–" for d in dimensions
        )
        lines.append(
            f"| {LABELS[p['first']]} vs {LABELS[p['second']]} | {p['units']} | {p['first_score']:.2f} "
            f"[{low:.2f}–{high:.2f}] | {p['first_wins']} / {p['ties']} / {p['second_wins']} | "
            f"{p['contradictory']:.0%} | {aspects} |"
        )
    return lines


def _delta_cell(delta: dict | None) -> str:
    if delta is None:
        return "–"
    low, high = delta["ci"]
    return f"{delta['delta'] * 100:+.0f} pts [{low * 100:+.0f} to {high * 100:+.0f}]"


def _checks_markdown(grades: list[dict], cases: dict) -> list[str]:
    conditions = [name for name in ORDER if any(grade["condition"] == name for grade in grades)]
    table: dict = defaultdict(lambda: defaultdict(lambda: {name: [0, 0] for name in conditions}))
    for grade in grades:
        for check in grade["checks"]:
            cell = table[grade["case"]][check["name"]][grade["condition"]]
            cell[0] += check["passed"]
            cell[1] += 1
    lines = ["", "#### Checks by case (passed / runs)"]
    for case_id in sorted(table, key=lambda case_id: (cases[case_id].split, case_id)):
        case = cases[case_id]
        ran = [name for name in conditions if any(cells[name][1] for cells in table[case_id].values())]
        lines += [
            "",
            f"**{case.split}: {case.title}**",
            "",
            "| Check | " + " | ".join(LABELS[n] for n in ran) + " |",
        ]
        lines.append("|---" * (len(ran) + 1) + "|")
        for check, cells in table[case_id].items():
            lines.append(f"| {check} | " + " | ".join(f"{cells[n][0]}/{cells[n][1]}" for n in ran) + " |")
    return lines


def _installed_stats(model: str, kind: str) -> dict:
    """Runs with the skill installed instead of appended: how often the agent loaded it, and the checks it passed."""
    grades = {(g["case"], g["condition"], g["rep"]): g for g in _load(results_dir(model, f"{kind}-checks"))}
    runs: dict[str, list[tuple[dict, dict | None]]] = defaultdict(list)
    for meta_file in sorted(results_dir(model, kind).glob("*/*/meta.json")):
        condition, rep = meta_file.parent.name.rsplit("-r", 1)
        meta = json.loads(meta_file.read_text(encoding="utf-8"))
        runs[condition].append((meta, grades.get((meta_file.parent.parent.name, condition, int(rep)))))
    stats = {}
    for name in (name for name in ORDER if name in runs):
        shares: ByCase = defaultdict(list)
        for _, grade in runs[name]:
            if grade:
                shares[grade["case"]].append(mean(check["passed"] for check in grade["checks"]))
        stats[name] = {
            "runs": len(runs[name]),
            "skill_loaded": mean(bool(meta.get("skill_loaded")) for meta, _ in runs[name]),
            "checks_passed": _case_mean(shares) if shares else None,
        }
    return stats


def _installed_markdown(title: str, installed: dict) -> list[str]:
    lines = [
        "",
        f"#### {title}",
        "",
        "| Condition | Runs | Runs that loaded the skill | Checks passed |",
        "|---|---|---|---|",
    ]
    for name, s in installed.items():
        checks = f"{s['checks_passed']:.0%}" if s["checks_passed"] is not None else "–"
        lines.append(f"| {LABELS[name]} | {s['runs']} | {s['skill_loaded']:.0%} | {checks} |")
    return lines


def _rationales_markdown(model: str, comparisons: list[dict]) -> list[str]:
    lines = [f"## Coder: {model}", ""]
    for comparison in comparisons:
        first, second = comparison["pair"]
        lines.append(
            f"- **{comparison['case']} r{comparison['rep']}, {first} vs {second}** ({comparison['score']:.2f})"
        )
        for order in comparison["orders"]:
            verdict = order["verdict"]
            winner = order.get(verdict["winner"], "tie")
            lines.append(f"  - A={order['A']}, B={order['B']} → {winner}: {verdict.get('rationale', '')}")
    return [*lines, ""]


def _write_charts(summary: dict) -> None:
    """The README charts: the blind preference on held-out cases, and the share of checks passed per split."""
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    preferences = _preferences(summary, "test")
    if preferences:
        case_count = summary[preferences[0].model]["test"]["cases"]
        write_text_atomic(ASSETS_DIR / "agentic-preference.svg", _preference_chart(preferences, case_count))
    if CHECKS_CHART_MODEL in summary:
        chart = _checks_chart(CHECKS_CHART_MODEL, summary[CHECKS_CHART_MODEL])
        write_text_atomic(ASSETS_DIR / "agentic-checks.svg", chart)


@dataclass(frozen=True)
class Preference:
    """How the blind judge decided between this repo's skill and one alternative, for one coder model."""

    model: str
    opponent: str
    wins: int
    ties: int
    losses: int
    score: float  # share of verdicts won by this repo's skill, a tie counting half
    ci: tuple[float, float]

    @property
    def comparisons(self) -> int:
        return self.wins + self.ties + self.losses


def _preferences(summary: dict, split: str) -> list[Preference]:
    rows = []
    for model, splits in summary.items():
        pairwise = splits.get(split, {}).get("pairwise", {})
        for opponent in OPPONENTS:
            pair = pairwise.get(f"{opponent} vs {THIS_REPO}") or pairwise.get(f"{THIS_REPO} vs {opponent}")
            if pair:
                rows.append(_this_repo_side(model, opponent, pair))
    return rows


def _this_repo_side(model: str, opponent: str, pair: dict) -> Preference:
    """The pair's result seen from this repo's skill, whichever side of the pair it is stored on."""
    low, high = pair["first_score_ci"]
    if pair["first"] == THIS_REPO:
        return Preference(
            model,
            opponent,
            pair["first_wins"],
            pair["ties"],
            pair["second_wins"],
            pair["first_score"],
            (low, high),
        )
    return Preference(
        model,
        opponent,
        pair["second_wins"],
        pair["ties"],
        pair["first_wins"],
        1 - pair["first_score"],
        (1 - high, 1 - low),
    )


def _preference_chart(preferences: list[Preference], case_count: int) -> str:
    this_repo = short_label(LABELS[THIS_REPO])
    parts_of_bar = [
        (f"{this_repo} preferred", "accent"),
        ("tie", "bar"),
        ("alternative preferred", "bar-strong"),
    ]
    width, bar_x, bar_width, bar_height, row_pitch, group_pitch, top = 760, 196, 310, 24, 38, 30, 100
    value_x, parity_x = bar_x + bar_width + 28, bar_x + bar_width / 2
    models = sorted(dict.fromkeys(row.model for row in preferences), key=_chart_rank)
    height = top + len(preferences) * row_pitch + len(models) * group_pitch + 24
    parts = chart_frame(
        width,
        height,
        title=f"Blind judge preference for {this_repo} over each alternative on held-out tasks, per coding agent",
        heading=f"Held-out tasks: {this_repo} against each alternative, judged blind",
        subheading=f"{case_count} unseen tasks, every pair of runs judged in both orders",
    )
    parts += _legend(24, 80, parts_of_bar)
    parts.append(_text(value_x, 80, f"Preference for {this_repo}", "ink2", 12))
    y = top
    for model in models:
        model_name = _model_name(model)
        parts += [
            _text(24, y + 16, model_name, "ink", 14, weight="700"),
            _text(parity_x, y + 22, "50%", "muted", 10, anchor="middle"),
        ]
        y += group_pitch
        rows = [row for row in preferences if row.model == model]
        group_top = y
        most_comparisons = max(row.comparisons for row in rows)
        for row in rows:
            opponent = short_label(LABELS[row.opponent])
            # A skill that exists only for some languages runs on fewer tasks; say so next to its name.
            tasks = round(case_count * row.comparisons / most_comparisons)
            if tasks < case_count:
                opponent += f" ({tasks} tasks)"
            counts = [row.wins, row.ties, row.losses]
            segments = [(name, count, fill) for (name, fill), count in zip(parts_of_bar, counts)]
            low, high = row.ci
            interval = f"95% CI {low * 100:.0f}–{high:.0%}" + (
                " · includes 50%" if low <= 0.5 <= high else ""
            )
            parts += [
                _text(36, y + bar_height / 2 + 4, f"vs {opponent}", "ink2", 12),
                *_segmented_bar(bar_x, y, bar_width, bar_height, segments, f"{model_name} vs {opponent}"),
                _text(value_x, y + 12, f"{row.score:.0%}", "ink", 16, weight="700"),
                _text(value_x + 50, y + 11, interval, "muted", 11),
            ]
            y += row_pitch
        # Where a tie block's middle sits, the preference sits: right of this line, this skill is ahead.
        parts.append(
            f'<line class="ref" x1="{parity_x}" y1="{group_top - 4}" x2="{parity_x}" '
            f'y2="{y - row_pitch + bar_height + 4}" stroke-width="1.25" stroke-dasharray="3 3" opacity="0.7"/>'
        )
    footer = (
        f"Preference: share of all verdicts, both orders, that went to {this_repo}, a tie counting half. "
        "Interval: bootstrap over the runs of each task."
    )
    parts += [_text(24, height - 16, footer, "muted", 11), "</svg>"]
    return "\n".join(parts)


def _segmented_bar(
    x: float, y: float, width: float, height: float, segments: list[tuple[str, int, str]], owner: str
) -> list[str]:
    """One whole split into blocks: a surface gap between blocks, each count printed inside where it fits."""
    total = sum(count for _, count, _ in segments)
    filled = [segment for segment in segments if segment[1]]
    elements, offset = [], 0.0
    for index, (name, count, fill) in enumerate(filled):
        share = count / total * width
        block_width = share - (SEGMENT_GAP if index < len(filled) - 1 else 0)
        elements += [
            f"<g><title>{escape(owner)}: {escape(name)} in {count} of {total} comparisons</title>",
            (
                f'<rect class="{fill}" x="{x + offset:.1f}" y="{y}" width="{block_width:.1f}" '
                f'height="{height}" rx="4"/>'
            ),
        ]
        if block_width >= MIN_LABELLED_BLOCK:
            elements.append(
                _text(x + offset + 8, y + height / 2 + 4, str(count), f"on-{fill}", 12, weight="600")
            )
        elements.append("</g>")
        offset += share
    return elements


def _legend(x: float, y: float, entries: list[tuple[str, str]]) -> list[str]:
    elements = []
    for name, fill in entries:
        elements += [
            f'<rect class="{fill}" x="{x:.1f}" y="{y - 10}" width="12" height="12" rx="3"/>',
            _text(x + 18, y, name, "ink2", 12),
        ]
        x += 18 + _text_width(name, 12) + 20
    return elements


def _checks_chart(model: str, splits: dict) -> str:
    panels = [split for split in SPLITS if split in splits]
    width, gap, top, row_pitch = 760, 24, 84, 32
    panel_width = (width - 48 - gap * (len(panels) - 1)) / len(panels)
    height = top + 36 + len(CHECKS_CHART_CONDITIONS) * row_pitch + 28
    parts = chart_frame(
        width,
        height,
        title="Share of deterministic checks passed per skill condition, "
        + " and ".join(SPLIT_PANELS[split][0].lower() for split in panels),
        heading="Deterministic checks passed",
        subheading=f"{_model_name(model)} as the coding agent",
    )
    for index, split in enumerate(panels):
        parts += _checks_panel(24 + index * (panel_width + gap), top, panel_width, split, splits[split])
    parts.append("</svg>")
    return "\n".join(parts)


def _checks_panel(x: float, top: float, width: float, split: str, stats: dict) -> list[str]:
    label_width, value_room, bar_height, row_pitch = 116, 44, 20, 32
    bar_x, bar_max = x + label_width, width - label_width - value_room
    rows_top = top + 36
    rows_bottom = rows_top + len(CHECKS_CHART_CONDITIONS) * row_pitch - (row_pitch - bar_height)
    title, caption = SPLIT_PANELS[split]
    runs_per_case = stats["conditions"][THIS_REPO]["runs"] // stats["cases"]
    elements = [
        _text(x, top, f"{title} ({stats['cases']})", "ink", 13, weight="600"),
        _text(x, top + 16, f"{caption}, {runs_per_case} runs per task", "muted", 11),
    ]
    for tick in (0, 0.5, 1):
        tick_x = bar_x + tick * bar_max
        elements += [
            (
                f'<line class="{"axis" if tick == 0 else "grid"}" x1="{tick_x:.1f}" y1="{rows_top - 6}" '
                f'x2="{tick_x:.1f}" y2="{rows_bottom + 6}" stroke-width="1"/>'
            ),
            _text(tick_x, rows_bottom + 20, f"{tick:.0%}", "muted", 11, anchor="middle"),
        ]
    for row, name in enumerate(CHECKS_CHART_CONDITIONS):
        y = rows_top + row * row_pitch
        label, weight = short_label(LABELS[name]), "700" if name == THIS_REPO else None
        if name == THIS_REPO:
            elements.append(row_highlight(x - 8, y - 5, width + 8, bar_height + 10))
        elements.append(
            _text(bar_x - 10, y + bar_height / 2 + 4, label, "ink", 12, weight=weight, anchor="end")
        )
        condition = stats["conditions"].get(name)
        if condition is None:
            elements.append(_text(bar_x + 6, y + bar_height / 2 + 4, "not run", "muted", 11))
            continue
        value = condition["checks_passed"]
        bar_width = max(value * bar_max, 4)
        elements += [
            f"<g><title>{escape(label)}, {escape(title.lower())}: {value:.0%} of checks passed</title>",
            f'<path class="{"accent" if name == THIS_REPO else "bar"}" d="{_bar_path(bar_x, y, bar_width, bar_height)}"/>',
            "</g>",
            _text(bar_x + bar_width + 6, y + bar_height / 2 + 4, f"{value:.0%}", "ink", 12, weight=weight),
        ]
    return elements


def _bar_path(x: float, y: float, width: float, height: float) -> str:
    """A horizontal bar, square at the baseline, with a rounded data end."""
    r = min(BAR_END_RADIUS, width)
    end = x + width
    return (
        f"M{x:.1f},{y:.1f} H{end - r:.1f} A{r},{r} 0 0 1 {end:.1f},{y + r:.1f} V{y + height - r:.1f} "
        f"A{r},{r} 0 0 1 {end - r:.1f},{y + height:.1f} H{x:.1f} Z"
    )


def _text(
    x: float,
    y: float,
    content: str,
    css: str,
    size: int,
    *,
    weight: str | None = None,
    anchor: str | None = None,
) -> str:
    attributes = f'class="{css}" x="{x:.1f}" y="{y:.1f}" font-size="{size}"'
    if weight:
        attributes += f' font-weight="{weight}"'
    if anchor:
        attributes += f' text-anchor="{anchor}"'
    return f"<text {attributes}>{escape(content)}</text>"


def _text_width(text: str, size: int) -> float:
    """Rough rendered width of `text` in the system sans; enough to space legend entries."""
    return len(text) * size * 0.56


def _chart_rank(model: str) -> int:
    """Position of a coder model in the charts; models not listed come last."""
    return CHART_MODEL_ORDER.index(model) if model in CHART_MODEL_ORDER else len(CHART_MODEL_ORDER)


def _model_name(model: str) -> str:
    """Display name from the model ID the runs recorded (`claude-sonnet-5-5` → `Claude Sonnet 5.5`)."""
    meta = next(results_dir(model, "runs").glob("*/*/meta.json"), None)
    model_ids = json.loads(meta.read_text(encoding="utf-8"))["model_ids"] if meta else []
    match = MODEL_ID.fullmatch(model_ids[0]) if model_ids else None
    return f"Claude {match[1].title()} {match[2]}.{match[3]}" if match else model


if __name__ == "__main__":
    main()
