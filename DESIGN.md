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
- **Placement**: Each outline is placed so that its TrueType control box starts 46 units from the origin. That matches where the original FontBuilder build rendered it, because that build wrote `hmtx` lsb = 46 regardless of the outline's `xMin`. Advance widths are the ink width plus 2 × 46.
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
- Vertical metrics are unchanged from the original build: hhea 800 / −260 / 0, typo 760 / −260 / 90, win 800 / 260.

## 6. Build & QA Verification
- **Build All Artifacts**: `make build` (or `./sources/build.sh`)
- **Regenerate Documentation Images**: `make images`
- **Google Fonts QA**: `make test` (fontspector) and `make qa` (FontBakery)

## 7. Open QA Findings
`font-tools check-font` reports the following on the fonts as originally drawn. The build lists them in `out-check-font.txt` and does not fail on them.
- **usWin metrics clip glyphs**: the descenders of `g`, `j`, `p`, `q` and `y` go below win descent 260, so Windows can clip them.
- **Short segments**: round caps and joins expanded by Skia leave many short quadratic pieces.
- **On-curve points just off a vertical zone**, plus one jaggy join in `@` (Regular).
- **Not yet in the glyph set**: no kerning, no accented letters, and no `uni00A0` (no-break space).
- **Line height is 1.06 em**, below the 1.2 em Google Fonts asks for.
