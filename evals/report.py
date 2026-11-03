"""Aggregate the judge grades into a summary and render the charts used in the README.

Usage: python evals/report.py
Writes evals/results/summary.json, evals/results/summary.md and docs/assets/results-*.svg.
"""

from __future__ import annotations

import json
import sys
from collections.abc import Callable
from dataclasses import dataclass
from html import escape
from statistics import mean

from charts import ASSETS_DIR, SEQUENTIAL_STEPS, chart_frame, row_highlight, short_label
from harness import ALL_CONDITIONS, GRADES_DIR, RESULTS_DIR, RUNS_DIR, THIS_REPO, load_cases

HIGHLIGHTED_CONDITION = THIS_REPO
NOT_RUN = "n/a"


@dataclass
class ConditionStats:
    name: str
    label: str
    pass_rate: float
    quality: float
    cost_usd: float
    per_case: dict[str, float]
    per_case_quality: dict[str, float]

    @property
    def chart_label(self) -> str:
        """The label, marked when the condition ran only some of the tasks (a skill without that language)."""
        total = len(load_cases())
        count = len(self.per_case)
        return self.label if count == total else f"{self.label} ({count} of {total} tasks)"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[attr-defined]  # stdout is a TextIOWrapper here
    stats = _collect_stats()
    _write_summary(stats)
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    (ASSETS_DIR / "results-single-turn.svg").write_text(_metrics_chart(stats), encoding="utf-8")
    (ASSETS_DIR / "results-by-case.svg").write_text(_case_heatmap(stats), encoding="utf-8")
    print((RESULTS_DIR / "summary.md").read_text(encoding="utf-8"))


def _collect_stats() -> list[ConditionStats]:
    grades = [json.loads(path.read_text(encoding="utf-8")) for path in GRADES_DIR.glob("*.json")]
    if not grades:
        raise SystemExit("No grades found. Run evals/judge.py first.")
    graded = {name for grade in grades for name in grade["results"]}
    return [
        _stats_for(condition.name, condition.label, grades)
        for condition in ALL_CONDITIONS
        if condition.name in graded
    ]


def _stats_for(name: str, label: str, grades: list[dict]) -> ConditionStats:
    per_case_passes: dict[str, list[bool]] = {}
    per_case_qualities: dict[str, list[float]] = {}
    for grade in grades:
        result = grade["results"].get(name)
        if result is None:
            continue
        per_case_passes.setdefault(grade["case"], []).extend(a["passed"] for a in result["assertions"])
        per_case_qualities.setdefault(grade["case"], []).append(result["quality"])
    all_passes = [passed for passes in per_case_passes.values() for passed in passes]
    costs = [
        json.loads(path.read_text(encoding="utf-8"))["cost_usd"]
        for path in RUNS_DIR.glob(f"*/{name}-r*.json")
    ]
    return ConditionStats(
        name=name,
        label=label,
        pass_rate=mean(all_passes),
        quality=mean(q for qualities in per_case_qualities.values() for q in qualities),
        cost_usd=mean(costs),
        per_case={case: mean(passes) for case, passes in sorted(per_case_passes.items())},
        per_case_quality={case: mean(qs) for case, qs in sorted(per_case_qualities.items())},
    )


def _write_summary(stats: list[ConditionStats]) -> None:
    summary = [stat.__dict__ for stat in stats]
    (RESULTS_DIR / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    titles = {case.case_id: case.title for case in load_cases()}
    header = (
        "| Condition | Assertions passed | Judge quality (1–10) | Avg. cost per task |\n|---|---|---|---|"
    )
    rows = [f"| {s.chart_label} | {s.pass_rate:.1%} | {s.quality:.1f} | ${s.cost_usd:.3f} |" for s in stats]
    case_header = "| Case | " + " | ".join(s.label for s in stats) + " |\n|---|" + "---|" * len(stats)
    case_rows = [
        f"| {titles[case]} | " + " | ".join(_cell(s.per_case, case, "{:.0%}") for s in stats) + " |"
        for case in titles
    ]
    quality_rows = [
        f"| {titles[case]} | " + " | ".join(_cell(s.per_case_quality, case, "{:.1f}") for s in stats) + " |"
        for case in titles
    ]
    text = "\n".join(
        [
            "# Eval results",
            "",
            f"{_run_description()}. Coding model: {_coding_model()}, judge: {_judge_model()}.",
            "",
            header,
            *rows,
            "",
            "## By case (assertions passed)",
            "",
            case_header,
            *case_rows,
            "",
            "## By case (judge quality, 1–10)",
            "",
            case_header,
            *quality_rows,
            "",
        ]
    )
    (RESULTS_DIR / "summary.md").write_text(text, encoding="utf-8")


def _cell(values: dict[str, float], case: str, number_format: str) -> str:
    return number_format.format(values[case]) if case in values else NOT_RUN


def _run_description() -> str:
    case_count = len(load_cases())
    rep_count = len(list(GRADES_DIR.glob("*.json"))) // case_count
    return f"{case_count} coding tasks, {rep_count} runs each, graded blind"


def _coding_model() -> str:
    return json.loads(next(RUNS_DIR.glob("*/*.json")).read_text(encoding="utf-8"))["model"]


def _judge_model() -> str:
    return json.loads(next(GRADES_DIR.glob("*.json")).read_text(encoding="utf-8"))["judge_model"]


@dataclass(frozen=True)
class BarMetric:
    title: str
    value: Callable[[ConditionStats], float]
    maximum: float
    ticks: tuple[float, ...]
    format: str
    tick_format: str


PASS_RATE = BarMetric("Assertions passed", lambda s: s.pass_rate, 1, (0, 0.5, 1), "{:.1%}", "{:.0%}")
QUALITY = BarMetric("Judge quality score (1–10)", lambda s: s.quality, 10, (0, 5, 10), "{:.1f}", "{:.0f}")
METRIC_BAR_HEIGHT, METRIC_ROW_PITCH = 22, 34


def _metrics_chart(stats: list[ConditionStats], metrics: tuple[BarMetric, ...] = (QUALITY, PASS_RATE)) -> str:
    """One panel per metric, side by side, sharing the condition labels on the left."""
    width, label_width, panel_gap, value_room, top = 760, 196, 32, 48, 100
    panel_width = (width - 24 - label_width - panel_gap * (len(metrics) - 1)) / len(metrics)
    rows_bottom = top + len(stats) * METRIC_ROW_PITCH - (METRIC_ROW_PITCH - METRIC_BAR_HEIGHT)
    height = rows_bottom + 44
    parts = chart_frame(
        width,
        height,
        title="Judge quality score and assertions passed per skill condition, single-turn suite",
        heading="Single-turn suite",
        subheading=_run_description(),
    )
    for index, stat in enumerate(stats):
        y = top + index * METRIC_ROW_PITCH
        if stat.name == HIGHLIGHTED_CONDITION:
            parts.append(row_highlight(12, y - 6, width - 24, METRIC_BAR_HEIGHT + 12))
        parts.append(
            f'<text class="ink" x="{24 + label_width - 12}" y="{y + METRIC_BAR_HEIGHT / 2 + 4:.1f}" '
            f'font-size="13" font-weight="{_weight(stat)}" text-anchor="end">'
            f"{escape(short_label(stat.chart_label))}</text>"
        )
    for index, metric in enumerate(metrics):
        x = 24 + label_width + index * (panel_width + panel_gap)
        parts += _metric_panel(x, top, panel_width - value_room, rows_bottom, stats, metric)
    parts.append("</svg>")
    return "\n".join(parts)


def _metric_panel(
    x: float,
    top: float,
    plot_width: float,
    rows_bottom: float,
    stats: list[ConditionStats],
    metric: BarMetric,
) -> list[str]:
    elements = [
        f'<text class="ink" x="{x}" y="{top - 22}" font-size="13" font-weight="600">{escape(metric.title)}</text>'
    ]
    for tick in metric.ticks:
        tick_x = x + tick / metric.maximum * plot_width
        elements += [
            (
                f'<line class="{"axis" if tick == 0 else "grid"}" x1="{tick_x:.1f}" y1="{top - 8}" '
                f'x2="{tick_x:.1f}" y2="{rows_bottom + 6}" stroke-width="1"/>'
            ),
            (
                f'<text class="muted" x="{tick_x:.1f}" y="{rows_bottom + 22}" font-size="11" '
                f'text-anchor="middle">{metric.tick_format.format(tick)}</text>'
            ),
        ]
    for index, stat in enumerate(stats):
        y = top + index * METRIC_ROW_PITCH
        value = metric.value(stat)
        bar_width = max(value / metric.maximum * plot_width, 4)
        bar_class = "accent" if stat.name == HIGHLIGHTED_CONDITION else "bar"
        formatted = metric.format.format(value)
        elements += [
            f"<g><title>{escape(short_label(stat.chart_label))}: {escape(metric.title)} {formatted}</title>",
            (
                f'<rect class="{bar_class}" x="{x}" y="{y}" width="{bar_width:.1f}" '
                f'height="{METRIC_BAR_HEIGHT}" rx="4"/>'
            ),
            "</g>",
            (
                f'<text class="ink" x="{x + bar_width + 8:.1f}" y="{y + METRIC_BAR_HEIGHT / 2 + 4:.1f}" '
                f'font-size="13" font-weight="{_weight(stat)}">{formatted}</text>'
            ),
        ]
    return elements


def _weight(stat: ConditionStats) -> str:
    return "700" if stat.name == HIGHLIGHTED_CONDITION else "400"


def _case_heatmap(stats: list[ConditionStats]) -> str:
    titles = {case.case_id: case.title for case in load_cases()}
    case_ids = list(titles)
    label_width, cell_width, cell_height, top = 330, 96, 34, 92
    width = label_width + cell_width * len(stats) + 24
    height = top + cell_height * len(case_ids) + 24
    parts = chart_frame(
        width,
        height,
        title="Share of assertions passed per eval case and skill condition",
        heading="Assertions passed by case",
        subheading="Stronger color means more assertions passed",
    )
    for column, stat in enumerate(stats):
        x = label_width + column * cell_width + cell_width / 2
        weight = "600" if stat.name == HIGHLIGHTED_CONDITION else "400"
        parts.append(
            f'<text class="ink" x="{x:.1f}" y="{top - 12}" font-size="12" font-weight="{weight}" '
            f'text-anchor="middle">{escape(short_label(stat.label))}</text>'
        )
    for row, case_id in enumerate(case_ids):
        y = top + row * cell_height
        parts.append(
            f'<text class="ink" x="24" y="{y + cell_height / 2 + 4:.1f}" font-size="13">'
            f"{escape(titles[case_id])}</text>"
        )
        for column, stat in enumerate(stats):
            x = label_width + column * cell_width
            if case_id not in stat.per_case:
                parts.append(
                    f'<text class="muted" x="{x + cell_width / 2:.1f}" y="{y + cell_height / 2 + 4:.1f}" '
                    f'font-size="12" text-anchor="middle">{NOT_RUN}</text>'
                )
                continue
            value = stat.per_case[case_id]
            step = min(int(value * SEQUENTIAL_STEPS), SEQUENTIAL_STEPS - 1)
            parts += [
                (
                    f'<rect class="seq-{step}" x="{x + 1}" y="{y + 1}" width="{cell_width - 2}" '
                    f'height="{cell_height - 2}" rx="4"/>'
                ),
                (
                    f'<text class="on-seq-{step}" x="{x + cell_width / 2:.1f}" y="{y + cell_height / 2 + 4:.1f}" '
                    f'font-size="12" text-anchor="middle">{value:.0%}</text>'
                ),
            ]
    parts.append("</svg>")
    return "\n".join(parts)


if __name__ == "__main__":
    main()
