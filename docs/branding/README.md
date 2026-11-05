# Clean Code Skill — Focus

The visual identity is **Focus**: a clear frame around one deliberate change.

![Clean Code Skill banner](../assets/banner.png)

**The right change. Right here.**

## Logo and assets

The mark has four open corners around one central square. The upper-left and lower-right corners have a diagonal bevel. The other corners stay square. Keep the mark upright, preserve its proportions and leave clear space around all five pieces.

| Asset | File | Use |
| --- | --- | --- |
| README banner | [banner.png](../assets/banner.png) | Repository header; includes wordmark and tagline |
| Standalone mark | [mark.png](../assets/mark.png) | Cobalt symbol on a transparent background |
| Icon | [icon.png](../assets/icon.png) | White symbol on an ink tile; transparent outside the rounded tile |

The banner, mark and icon were created with the built-in image-generation tool using the approved Brandkit direction. They are PNG image assets.

## Palette

| Role | Color | Hex |
| --- | --- | --- |
| Primary accent | Cobalt | `#284FBA` |
| Light surface | Pale ice | `#ECEFF8` |
| Main text and dark surface | Deep ink | `#172740` |
| Dark-mode accent | Pale cobalt | `#8FABFF` |
| Dark-mode text | Ice white | `#F3F6FC` |

Use cobalt for the selected result, a focal point or the primary brand mark. Supporting series use blue-gray neutrals. Heatmaps use a sequential blue ramp so magnitude remains readable without introducing unrelated accent colors.

## Typography and layout

The wordmark uses a strong monospaced style. Small brand labels use Cascadia Code, JetBrains Mono, SF Mono or Consolas. Dense chart labels keep the existing sans-serif stack for readability.

Use pale surfaces, fine blue-gray borders, generous clear space and a restrained diagonal corner detail. Dark surfaces use deep ink with pale blue accents. Keep the full product name **Clean Code Skill** in visible branding.

## Maintaining the charts

`evals/charts.py` owns the shared light and dark chart themes and the chart header. The four generated result charts use that theme. The highlights, precedence and workflow illustrations use the same palette in their self-contained SVG styles.

When regenerating report graphics, use the existing report tools and the recorded evaluation data. A visual update changes styling and brand labels; numerical data and evidence stay tied to those recorded results.
