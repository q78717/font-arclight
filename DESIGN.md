# Design — Arclight

## 1. Introduction
Arclight is a contemporary geometric monoline typeface family designed with pure vector geometry. Its technical philosophy is "Code as Font Forge": every glyph outline is defined programmatically in Python as stroked vector paths and compiled directly into TrueType and WOFF2 formats without proprietary GUI font editors.

## 2. Tech Stack
- **Language**: Python 3.10+
- **Font Generation**: `fontTools` (`FontBuilder`, `TTGlyphPen`, `TransformPen`, `ReverseContourPen`)
- **Geometry & Path Operations**: `skia-pathops` (stroke expansion, path simplification, boolean operations)
- **SVG Processing**: `fontTools.svgLib.path`
- **Specimen Presentation**: HTML5, CSS3, Web Fonts

## 3. Technical Architecture
- **Parametric Stroke Expansion**: Glyph designs are authored as monoline skeleton paths (lines and SVG arc commands). `build_arclight.py` scales coordinates to a 1000 UPM grid and expands strokes using Skia pathops with round caps and joins.
- **Winding Correction**: Automatically simplifies intersecting strokes and inverts path winding to conform to TrueType non-zero winding rules.
- **Multi-Weight Generation**: Interpolates or parameterizes stroke widths to build Light, Regular, and Bold weights from unified glyph definitions.

## 4. File Structure
```text
font-arclight/
├── build_arclight.py       # Primary build script compiling vector skeletons into TTF
├── Arclight-Light.ttf      # Light weight TrueType binary
├── Arclight-Regular.ttf    # Regular weight TrueType binary
├── Arclight-Bold.ttf       # Bold weight TrueType binary
├── arclight-fonts.zip      # Packaged font distribution archive
└── arclight-typeface.html  # Interactive specimen showcase and typography preview
```

## 5. Implementation Details
- **Grid Coordinates**: SVG authoring grid (y-down: cap 20, x-height 70, baseline 130, descender 170) maps via scale factor 6.4 to font units (y-up: cap 704, x-height 384, descender -256, 1000 UPM).
- **Glyph Set**: Uppercase, lowercase, numerals, punctuation, mathematical operators, and Latin symbols.
- **Metrics**: Consistent sidebearing (46 units) and word space (300 units) calculated parametrically.

## 6. Build & Run
- **Install Dependencies**: `pip install fonttools skia-pathops`
- **Build Fonts**: `python3 build_arclight.py`
- **Preview**: Open `arclight-typeface.html` in any modern web browser.

## 7. Tooling & Dependencies
- `fontTools`: Low-level OpenType table synthesis (head, hhea, hmtx, maxp, cmap, glyf, loca, name, OS/2, post).
- `skia-pathops`: High-performance 2D geometric path clipping and offsetting.

## 8. Security & Standards
- **Standard Conformance**: Generates valid OpenType/TrueType tables conforming to ISO/IEC 14496-22 (OpenType specification).
- **Clean Builds**: Standalone deterministic Python script with reproducible binary outputs.
