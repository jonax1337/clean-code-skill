"""SVG building blocks shared by the eval reports: one theme for light and dark mode, and the chart frame."""

from __future__ import annotations

from html import escape

from harness import REPO_DIR

ASSETS_DIR = REPO_DIR / "docs" / "assets"
FONT = "Inter, ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif"
MONO_FONT = "'Cascadia Code', 'JetBrains Mono', 'SF Mono', Consolas, monospace"
BRAND = "Clean Code Skill"

# Magnitude ramps for heatmaps, weakest to strongest; in dark mode the strongest step is the brightest.
SEQUENTIAL_LIGHT = ["#e1e8fb", "#c3d2f5", "#a0b9eb", "#7b9adf", "#4b6fc8", "#284fba"]
SEQUENTIAL_DARK = ["#22395b", "#2b4674", "#385a95", "#4269a9", "#8fabff", "#b4c9ff"]
SEQUENTIAL_STEPS = len(SEQUENTIAL_LIGHT)
FIRST_STRONG_STEP = 4  # from this step on, cell text switches to the color that reads on strong fills


def _sequential_roles(ramp: list[str], on_weak: str, on_strong: str) -> dict[str, str]:
    """Roles `seq-0` … for one ramp, each with an `on-seq-*` text color that reads on it."""
    roles = {}
    for step, color in enumerate(ramp):
        roles[f"seq-{step}"] = color
        roles[f"on-seq-{step}"] = on_strong if step >= FIRST_STRONG_STEP else on_weak
    return roles


# Every role becomes a CSS class of the same name. `on-*` roles are for text set inside a filled mark.
LIGHT = {
    "bg": "#eceff8",
    "frame": "#ccd6ea",
    "ink": "#172740",
    "ink2": "#435573",
    "muted": "#566985",
    "grid": "#ccd6ea",
    "bar": "#ced8eb",
    "accent": "#284fba",
    "axis": "#adbbd5",
    "ref": "#435573",
    "bar-strong": "#607393",
    "on-accent": "#ffffff",
    "on-bar": "#172740",
    "on-bar-strong": "#ffffff",
    **_sequential_roles(SEQUENTIAL_LIGHT, on_weak="#172740", on_strong="#ffffff"),
}
DARK = {
    "bg": "#172740",
    "frame": "#2c4260",
    "ink": "#f3f6fc",
    "ink2": "#cbd5e7",
    "muted": "#aabad5",
    "grid": "#2c4260",
    "bar": "#354d71",
    "accent": "#8fabff",
    "axis": "#4b6386",
    "ref": "#cbd5e7",
    "bar-strong": "#536c90",
    "on-accent": "#172740",
    "on-bar": "#f3f6fc",
    "on-bar-strong": "#ffffff",
    **_sequential_roles(SEQUENTIAL_DARK, on_weak="#f3f6fc", on_strong="#172740"),
}
LINE_ROLES = {"frame", "grid", "axis", "ref"}

# Chart display names for condition labels that read differently in the README's prose.
DISPLAY_LABELS = {"This repo": "This skill"}


def theme_style() -> str:
    def rules(palette: dict[str, str]) -> str:
        return " ".join(
            f".{role}{{{'stroke' if role in LINE_ROLES else 'fill'}:{color}}}"
            for role, color in palette.items()
        )

    return (
        f"<style>text{{font-family:{FONT}}} .mono{{font-family:{MONO_FONT}}} {rules(LIGHT)} "
        f"@media (prefers-color-scheme: dark){{{rules(DARK)}}}</style>"
    )


def chart_frame(width: int, height: int, *, title: str, heading: str, subheading: str) -> list[str]:
    """Opening elements of a chart: the svg root with an accessible title, the theme, the card and headings."""
    return [
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="t">'
        ),
        theme_style(),
        f'<title id="t">{escape(title)}</title>',
        (
            f'<rect class="bg frame" x="0.5" y="0.5" width="{width - 1}" height="{height - 1}" '
            'rx="12" stroke-width="1"/>'
        ),
        f'<text class="ink" x="24" y="34" font-size="17" font-weight="700">{escape(heading)}</text>',
        f'<text class="ink2" x="24" y="54" font-size="12.5">{escape(subheading)}</text>',
        f'<rect class="accent" x="{width - 24 - _mono_width(BRAND, 11) - 16:.1f}" y="47" width="7" height="7"/>',
        f'<text class="muted mono" x="{width - 24}" y="54" font-size="11" text-anchor="end">{BRAND}</text>',
    ]


def row_highlight(x: float, y: float, width: float, height: float) -> str:
    """A faint accent band behind the row of the condition the chart is about."""
    return f'<rect class="accent" x="{x}" y="{y}" width="{width}" height="{height}" rx="6" opacity="0.08"/>'


def short_label(label: str) -> str:
    return DISPLAY_LABELS.get(label, label).replace("/clean-code", "")


def _mono_width(text: str, size: float) -> float:
    """Rendered width of `text` in a monospace font, whose glyphs are about 0.6 em wide."""
    return len(text) * size * 0.6
