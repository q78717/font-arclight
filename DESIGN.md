# Design — Arclight

## 1. Introduction
Arclight is a contemporary geometric monoline typeface family designed with pure vector geometry. Every glyph outline is defined in Python as a stroked vector path. The script writes standard UFO sources, which Google Fonts' `gftools builder` pipeline compiles into TrueType and WOFF2.

## 2. Tech Stack
- **Language**: Python 3.10+
- **Outline Synthesis**: `skia-pathops` (stroke expansion, overlap removal), `fontTools` (`svgLib.path`, pens), `ufoLib2`
- **Font Compilation & Hinting**: `gftools builder`, `fontmake`, `ufo2ft`, `ttfautohint-py`
- **Proofs, Specimen & QA**: [`font-tools`](https://github.com/q78717/font-tools) (shared by the rv font repos), `fontspector`, `FontBakery`
- **License**: SIL Open Font License 1.1 (`OFL.txt`)

## 3. Technical Architecture
- **Parametric Stroke Expansion**: Glyphs are monoline skeleton paths made of lines, SVG arc commands and curves. `build_arclight.py` scales them to a 1000 UPM grid and expands the strokes with Skia pathops, using round caps and joins.
- **Overlap Removal**: `simplify(fix_winding=True)` merges self-overlapping strokes. The UFOs keep PostScript contour direction, and ufo2ft reverses it for TrueType.
- **Outline Cleanup** (for the Google Fonts outline checks): conics become quadratics at a 2-unit tolerance. The script spells out implied on-curve points, snaps points within 2 units onto the baseline, x-height, cap height and descender, and drops segments under 3 units. It also merges pairs of quadratics where one stays within 1 unit, and joins straight runs. Each step is checked with a boolean XOR against the raw outline, and a glyph falls back to a lighter cleanup, or to the fine 0.25-tolerance outline, when the step would change its ink. Bold `e`, `S`, `&` and a few marks use the fallback.
- **Placement**: Spacing is measured on the fine outline. The control box starts 46 units from the origin and the advance is the ink width plus 2 × 46. That is where the original FontBuilder build rendered every glyph, because it wrote `hmtx` lsb = 46 regardless of the outline's `xMin`.
- **Kerning**: Pairs are kerned per weight from glyph profiles, the same method Vektra uses. Each pair is tightened toward a gap of two sidebearings (92 units), by at most 160 units, and never loosened. That gives about 2,400–2,600 pairs per weight.
- **Multi-Weight Generation**: Light, Regular and Bold use the same skeletons with stroke widths of 5.0, 7.5 and 12.0 design units.

## 4. Repository Layout (Google Fonts Template)
```text
font-arclight/
├── .github/workflows/            # CI build/test, GitHub Pages specimen, Release packaging (via font-tools)
├── AUTHORS.txt / CONTRIBUTORS.txt
├── DESIGN.md                     # This document
├── Makefile                      # help, venv, clean; shared targets from font-tools (.font-tools.mk)
├── OFL.txt                       # SIL Open Font License 1.1
├── README.md
├── requirements.in / requirements.txt / requirements-qa.txt
├── documentation/
│   ├── article/                  # Article image
│   ├── images/                   # README images
│   └── specimen/index.html       # Self-contained interactive specimen
├── fonts/
│   ├── ttf/Arclight-{Light,Regular,Bold}.ttf
│   └── webfonts/Arclight-{Light,Regular,Bold}.woff2
└── sources/
    ├── build.sh                  # Single-command build pipeline
    ├── build_arclight.py         # Glyph skeletons and UFO generator
    ├── build_specimen.py         # Specimen compiler
    ├── config.yaml               # gftools builder configuration
    ├── specimen_template.html
    ├── tools/                    # STAT builder, README image renderer
    └── ufo/                      # Generated UFO sources
```

## 5. Metrics
- 1000 UPM; cap height 704, x-height 384, descender −256, measured from the SVG grid (y down: cap 20, x-height 70, baseline 130, descender 170; scale 6.4).
- Sidebearings 46; word space 300.
- Vertical metrics clear every glyph in all three weights and give a 1.2 em line: hhea = typo = 840 / −360 / 0, win 840 / 360, `USE_TYPO_METRICS` set. The original build had 1.06 em, and win metrics that clipped the descenders of `g j p q y`.
- U+00A0 (no-break space) maps to `space`.

## 6. Build & QA Verification
- **Build All Artifacts**: `make build` (or `./sources/build.sh`)
- **Regenerate Documentation Images**: `make images`
- **Google Fonts QA**: `make test` (fontspector) and `make qa` (FontBakery)

## 7. QA Status
- `font-tools check-font` passes and fails the build on regressions. It skips two findings that are part of the design:
  - **Short segments**: the 45° pieces of the small round caps and joins are under FontBakery's 0.6% rule (a WARN there).
  - **Jaggy join**: the cusp where the arc of `@` meets its stem.
- FontBakery (`googlefonts` profile): 0 ERROR and 2 FAILs, both about glyph coverage:
  - `glyph_coverage`: missing `^ ` { } | ~ ¡ ¢ £ ¥`.
  - `shape_languages`: no Google Fonts glyph set is 80% covered, because there are no accented letters.
- The remaining WARNs are uppercase not centred in the em box, contour count, the widths of the two math signs, no article, codepoints outside the subsets, the unregistered vendor ID `ARCL`, and short segments in Regular and Bold.
