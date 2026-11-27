#!/usr/bin/env python3
"""Build the self-contained specimen page (three weights and the glyph skeletons inlined).

Usage: python3 sources/build_specimen.py [--fonts fonts/webfonts] [--out documentation/specimen/index.html]
"""
import argparse
import os
import sys

from rvfont import specimen

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import build_arclight as B  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fonts", default="fonts/webfonts")
    ap.add_argument("--template", default=os.path.join(HERE, "specimen_template.html"))
    ap.add_argument("--out", default="documentation/specimen/index.html")
    a = ap.parse_args()

    skeletons = {ch: [d, w] for ch, (d, w) in B.G.items() if d}
    chars = sum(1 for ch in B.G if ch != " ")
    size = specimen.fill(
        a.template,
        a.out,
        fonts={f"__FONT_{style.upper()}__": os.path.join(a.fonts, f"{B.FAMILY}-{style}.woff2")
               for style, _, _ in B.WEIGHTS},
        values={
            "__GLYPH_DATA__": specimen.to_json(skeletons),
            "__VERSION__": B.VERSION,
            "__REPO__": B.REPO_URL,
            "__CHARS__": chars,
        },
    )
    print(f"specimen -> {a.out} ({size:,} bytes, {chars} characters)")


if __name__ == "__main__":
    main()
