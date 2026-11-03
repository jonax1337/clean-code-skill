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
from charts import ASSETS_DIR, chart_frame, short_label
from harness import ALL_CONDITIONS, write_text_atomic

LABELS = {condition.name: condition.label for condition in ALL_CONDITIONS}
ORDER = [condition.name for condition in ALL_CONDITIONS]
REFERENCES = ["baseline", "v2"]  # conditions every other condition is compared against
WINNER_SCORE = {"A": 1.0, "tie": 0.5, "B": 0.0}
RESAMPLES = 10_000

RELEASED, PREVIOUS = "v3a", "v2"  # the version released as the current skill, and the release before it
CHECKS_CHART_MODEL = "sonnet"
CHECKS_CHART_CONDITIONS = ["baseline", "sickn33", PREVIOUS, RELEASED]
SPLIT_PANELS = {
    "dev": ("Dev tasks", "used while writing v3"),
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
        "deltas": {},
    }
    for reference in REFERENCES:
        if reference in shares and reference != name and shares[reference].keys() == shares[name].keys():
            stats["deltas"][reference] = {
                "delta": _case_mean(shares[name]) - _case_mean(shares[reference]),
                "ci": bootstrap_ci(shares[name], minus=shares[reference]),
            }
    return stats


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
        }
    return stats


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
        "| Condition | Runs | Checks passed | Δ vs no skill | Δ vs v2 | Runs passing every check | Avg. cost | Avg. turns |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for name, s in stats["conditions"].items():
        low, high = s["checks_passed_ci"]
        deltas = [_delta_cell(s["deltas"].get(reference)) for reference in REFERENCES]
        lines.append(
            f"| {LABELS[name]} | {s['runs']} | {s['checks_passed']:.0%} [{low:.0%}–{high:.0%}] | {deltas[0]} | "
            f"{deltas[1]} | {s['runs_all_passed']}/{s['runs']} | ${s['cost_usd']:.3f} | {s['turns']:.1f} |"
        )
    if stats["pairwise"]:
        lines += [
            "",
            "| Blind comparison | Units | Score of first [CI] | First / tie / second | Contradictory |",
            "|---|---|---|---|---|",
        ]
        for p in stats["pairwise"].values():
            low, high = p["first_score_ci"]
            lines.append(
                f"| {LABELS[p['first']]} vs {LABELS[p['second']]} | {p['units']} | {p['first_score']:.2f} "
                f"[{low:.2f}–{high:.2f}] | {p['first_wins']} / {p['ties']} / {p['second_wins']} | "
                f"{p['contradictory']:.0%} |"
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
    """How the blind judge decided between the released skill and the release before it, for one coder model."""

    model: str
    wins: int
    ties: int
    losses: int
    score: float  # share of comparisons won by the released skill, a tie counting half
    ci: tuple[float, float]

    @property
    def comparisons(self) -> int:
        return self.wins + self.ties + self.losses


def _preferences(summary: dict, split: str) -> list[Preference]:
    rows = []
    for model, splits in summary.items():
        pairwise = splits.get(split, {}).get("pairwise", {})
        pair = pairwise.get(f"{PREVIOUS} vs {RELEASED}") or pairwise.get(f"{RELEASED} vs {PREVIOUS}")
        if pair:
            rows.append(_released_side(model, pair))
    return sorted(rows, key=lambda row: row.score, reverse=True)


def _released_side(model: str, pair: dict) -> Preference:
    """The pair's result seen from the released skill, whichever side of the pair it is stored on."""
    low, high = pair["first_score_ci"]
    if pair["first"] == RELEASED:
        return Preference(
            model, pair["first_wins"], pair["ties"], pair["second_wins"], pair["first_score"], (low, high)
        )
    return Preference(
        model,
        pair["second_wins"],
        pair["ties"],
        pair["first_wins"],
        1 - pair["first_score"],
        (1 - high, 1 - low),
    )


def _preference_chart(preferences: list[Preference], case_count: int) -> str:
    released, previous = short_label(LABELS[RELEASED]), short_label(LABELS[PREVIOUS])
    parts_of_bar = [
        (f"{released} preferred", "accent"),
        ("tie", "bar"),
        (f"{previous} preferred", "bar-strong"),
    ]
    width, bar_x, bar_width, bar_height, row_pitch, top = 760, 176, 330, 28, 56, 100
    value_x = bar_x + bar_width + 28
    height = top + len(preferences) * row_pitch + 24
    comparisons = preferences[0].comparisons
    parts = chart_frame(
        width,
        height,
        title=f"Blind judge preference for {released} over {previous} on held-out tasks, per coding agent",
        heading=f"Held-out tasks: {released} against {previous}, judged blind",
        subheading=(
            f"{comparisons} comparisons per coding agent: {case_count} unseen tasks × "
            f"{comparisons // case_count} runs, each pair judged in both orders"
        ),
    )
    parts += _legend(bar_x, 80, parts_of_bar)
    parts.append(_text(value_x, 80, f"Preference for {released}", "ink2", 12))
    for index, row in enumerate(preferences):
        y = top + index * row_pitch
        model_name = _model_name(row.model)
        counts = [row.wins, row.ties, row.losses]
        segments = [(name, count, fill) for (name, fill), count in zip(parts_of_bar, counts)]
        low, high = row.ci
        interval = f"95% CI {low * 100:.0f}–{high:.0%}" + (" · includes 50%" if low <= 0.5 <= high else "")
        parts += [
            _text(24, y + bar_height / 2 + 5, model_name, "ink", 13, weight="600"),
            *_segmented_bar(bar_x, y, bar_width, bar_height, segments, model_name),
            _text(value_x, y + 13, f"{row.score:.0%}", "ink", 16, weight="600"),
            _text(value_x, y + 28, interval, "muted", 11),
        ]
    footer = (
        f"Preference: share of all verdicts, both orders, that went to {released}, a tie counting half. "
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
    first = splits[panels[0]]
    runs_per_case = next(iter(first["conditions"].values()))["runs"] // first["cases"]
    parts = chart_frame(
        width,
        height,
        title="Share of deterministic checks passed per skill condition, "
        + " and ".join(SPLIT_PANELS[split][0].lower() for split in panels),
        heading="Deterministic checks passed",
        subheading=f"{_model_name(model)} as the coding agent, {runs_per_case} runs per task and condition",
    )
    for index, split in enumerate(panels):
        parts += _checks_panel(24 + index * (panel_width + gap), top, panel_width, split, splits[split])
    parts.append("</svg>")
    return "\n".join(parts)


def _checks_panel(x: float, top: float, width: float, split: str, stats: dict) -> list[str]:
    label_width, value_room, bar_height, row_pitch = 72, 44, 20, 32
    bar_x, bar_max = x + label_width, width - label_width - value_room
    rows_top = top + 36
    rows_bottom = rows_top + len(CHECKS_CHART_CONDITIONS) * row_pitch - (row_pitch - bar_height)
    title, caption = SPLIT_PANELS[split]
    elements = [
        _text(x, top, f"{title} ({stats['cases']})", "ink", 13, weight="600"),
        _text(x, top + 16, caption, "muted", 11),
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
        label, weight = short_label(LABELS[name]), "600" if name == RELEASED else None
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
            f'<path class="{"accent" if name == RELEASED else "bar"}" d="{_bar_path(bar_x, y, bar_width, bar_height)}"/>',
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


def _model_name(model: str) -> str:
    """Display name from the model ID the runs recorded (`claude-sonnet-5-5` → `Claude Sonnet 5.5`)."""
    meta = next(results_dir(model, "runs").glob("*/*/meta.json"), None)
    model_ids = json.loads(meta.read_text(encoding="utf-8"))["model_ids"] if meta else []
    match = MODEL_ID.fullmatch(model_ids[0]) if model_ids else None
    return f"Claude {match[1].title()} {match[2]}.{match[3]}" if match else model


if __name__ == "__main__":
    main()
