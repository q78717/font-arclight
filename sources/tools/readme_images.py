#!/usr/bin/env python3
"""Render the README images in documentation/images/ from the built fonts (`make images`)."""
import os

from font_tools.grid import grid, printing_chars
from font_tools.palette import DENIM, RED
from font_tools.raster import line, save_rows

L = "fonts/ttf/Arclight-Light.ttf"
R = "fonts/ttf/Arclight-Regular.ttf"
B = "fonts/ttf/Arclight-Bold.ttf"
OUT = "documentation/images"
ART_OUT = "documentation/article"


def main():
    save_rows([line(R, "Arclight", 200, pad=36),
               line(R, "Monoline display type from arcs and straights.", 52, pad=36),
               line(B, "Orbital transit, gate 14", 96, color=RED, pad=36)],
              os.path.join(OUT, "arclight-banner.png"))
    save_rows([line(L, "Light  Orbital transit 2049", 84, pad=30),
               line(R, "Regular  Orbital transit 2049", 84, color=DENIM, pad=30),
               line(B, "Bold  Orbital transit 2049", 84, pad=30)],
              os.path.join(OUT, "weights.png"))
    save_rows([line(R, "Arclight", 160, pad=30),
               line(R, "Monoline arc display, three weights", 56, pad=30),
               line(B, "Arclight 2049", 92, color=RED, pad=30)],
              os.path.join(ART_OUT, "arclight-article.png"))
    grid(R, printing_chars(R), os.path.join(OUT, "glyphs.png"), px=88, cols=16, guides=(704, 384))


if __name__ == "__main__":
    main()
