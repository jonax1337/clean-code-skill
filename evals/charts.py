"""SVG building blocks shared by the eval reports: one theme for light and dark mode, and the chart frame."""

from __future__ import annotations

from html import escape

from harness import REPO_DIR

ASSETS_DIR = REPO_DIR / "docs" / "assets"
FONT = "system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif"

# Every role becomes a CSS class of the same name. `on-*` roles are for text set inside a filled mark.
LIGHT = {
    "bg": "#fcfcfb",
    "ink": "#0b0b0b",
    "ink2": "#52514e",
    "muted": "#898781",
    "grid": "#e1e0d9",
    "bar": "#c3c2b7",
    "accent": "#2a78d6",
    "axis": "#c3c2b7",
    "bar-strong": "#898781",
    "on-accent": "#ffffff",
    "on-bar": "#0b0b0b",
    "on-bar-strong": "#0b0b0b",
}
DARK = {
    "bg": "#1a1a19",
    "ink": "#f0efec",
    "ink2": "#c3c2b7",
    "muted": "#898781",
    "grid": "#2c2c2a",
    "bar": "#52514e",
    "accent": "#3987e5",
    "axis": "#383835",
    "bar-strong": "#898781",
    "on-accent": "#ffffff",
    "on-bar": "#ffffff",
    "on-bar-strong": "#0b0b0b",
}
LINE_ROLES = {"grid", "axis"}


def theme_style() -> str:
    def rules(palette: dict[str, str]) -> str:
        return " ".join(
            f".{role}{{{'stroke' if role in LINE_ROLES else 'fill'}:{color}}}"
            for role, color in palette.items()
        )

    return (
        f"<style>text{{font-family:{FONT}}} {rules(LIGHT)} "
        f"@media (prefers-color-scheme: dark){{{rules(DARK)}}}</style>"
    )


def chart_frame(width: int, height: int, *, title: str, heading: str, subheading: str) -> list[str]:
    """Opening elements of a chart: the svg root with an accessible title, the theme, the background and headings."""
    return [
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}" role="img" aria-labelledby="t">'
        ),
        theme_style(),
        f'<title id="t">{escape(title)}</title>',
        f'<rect class="bg" width="{width}" height="{height}" rx="8"/>',
        f'<text class="ink" x="24" y="32" font-size="16" font-weight="600">{escape(heading)}</text>',
        f'<text class="ink2" x="24" y="50" font-size="12">{escape(subheading)}</text>',
    ]


def short_label(label: str) -> str:
    return label.replace("This repo, ", "").replace("/clean-code", "")
