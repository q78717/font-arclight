#!/usr/bin/env bash
# Build Arclight in one command:  sources/build.sh
#   1. sources/build_arclight.py strokes every glyph skeleton and writes the Light, Regular and Bold UFOs
#   2. gftools builder compiles, hints and checks them into fonts/ttf and fonts/webfonts
#   3. a STAT table is added, the specimen page is rebuilt, and the fonts are smoke-tested
set -euo pipefail
cd "$(dirname "$0")/.."
# Build venv: $FONT_VENV (set by make), else the shared ../.venv-fonts, else ./venv.
for v in "${FONT_VENV:-}" "$PWD/../.venv-fonts" "$PWD/venv"; do
  if [ -n "$v" ] && [ -x "$v/bin/python3" ]; then export PATH="$v/bin:$PATH"; break; fi
done
python3 sources/build_arclight.py --ufo sources/ufo
(cd sources && gftools builder config.yaml)
python3 sources/tools/add_stat.py fonts/ttf fonts/webfonts
python3 sources/build_specimen.py --fonts fonts/webfonts --out documentation/specimen/index.html
# Short segments: the 45-degree pieces of the small round caps and joins are under FontBakery's
# 0.6% rule (a WARN there). Jaggy: the cusp where the arc of @ meets its stem is drawn that way.
fonts=(fonts/ttf/Arclight-Light.ttf fonts/ttf/Arclight-Regular.ttf fonts/ttf/Arclight-Bold.ttf)
font-tools check-font "${fonts[@]}" --kern To --kern LT --kern Yo --skip short-segments --skip jaggy
