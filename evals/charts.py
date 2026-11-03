"""SVG building blocks shared by the eval reports: one theme for light and dark mode, and the chart frame."""

from __future__ import annotations

from html import escape

from harness import REPO_DIR

ASSETS_DIR = REPO_DIR / "docs" / "assets"
FONT = "Inter, ui-sans-serif, system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif"
MONO_FONT = "ui-monospace, 'SF Mono', 'Cascadia Code', 'JetBrains Mono', Menlo, Consolas, monospace"
BRAND = "clean-code"

# Magnitude ramps for heatmaps, weakest to strongest; in dark mode the strongest step is the brightest.
SEQUENTIAL_LIGHT = ["#e3f5ed", "#c2e9d8", "#8fd6b9", "#4fbb92", "#12906a", "#0a7253"]
SEQUENTIAL_DARK = ["#15302a", "#1a4739", "#1f634e", "#238866", "#2db27f", "#56dba3"]
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
    "bg": "#f6f8f7",
    "frame": "#e2e8e5",
    "ink": "#0b1215",
    "ink2": "#47554f",
    "muted": "#6f7d77",
    "grid": "#e2e8e5",
    "bar": "#cfd7d3",
    "accent": "#08805f",
    "axis": "#c3ccc8",
    "ref": "#47554f",
    "bar-strong": "#74817c",
    "on-accent": "#ffffff",
    "on-bar": "#0b1215",
    "on-bar-strong": "#ffffff",
    **_sequential_roles(SEQUENTIAL_LIGHT, on_weak="#0b1215", on_strong="#ffffff"),
}
DARK = {
    "bg": "#0f1614",
    "frame": "#1f2a26",
    "ink": "#edf3f0",
    "ink2": "#b4c1bb",
    "muted": "#83918b",
    "grid": "#1f2a26",
    "bar": "#34403c",
    "accent": "#34d399",
    "axis": "#3a4642",
    "ref": "#b4c1bb",
    "bar-strong": "#64716c",
    "on-accent": "#04140e",
    "on-bar": "#edf3f0",
    "on-bar-strong": "#ffffff",
    **_sequential_roles(SEQUENTIAL_DARK, on_weak="#edf3f0", on_strong="#04140e"),
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
        f'<circle class="accent" cx="{width - 24 - _mono_width(BRAND, 11) - 9:.1f}" cy="30" r="3.5"/>',
        f'<text class="muted mono" x="{width - 24}" y="34" font-size="11" text-anchor="end">{BRAND}</text>',
    ]


def row_highlight(x: float, y: float, width: float, height: float) -> str:
    """A faint accent band behind the row of the condition the chart is about."""
    return f'<rect class="accent" x="{x}" y="{y}" width="{width}" height="{height}" rx="6" opacity="0.08"/>'


def short_label(label: str) -> str:
    return DISPLAY_LABELS.get(label, label).replace("/clean-code", "")


def _mono_width(text: str, size: float) -> float:
    """Rendered width of `text` in a monospace font, whose glyphs are about 0.6 em wide."""
    return len(text) * size * 0.6
