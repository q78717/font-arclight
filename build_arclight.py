#!/usr/bin/env python3
"""
Arclight — build stroked SVG glyph outlines into real TTF / WOFF2 fonts.

Design grid (SVG, y down):  cap 20 · x-height 70 · baseline 130 · descender 170
Font grid  (y up, 1000 upm): scale 6.4  ->  cap 704 · x-height 384 · desc -256

Each glyph is a monoline path. Skia expands the stroke (round cap + round join),
simplify() removes the self-overlap, conics become quadratics, contours are
reversed for the TrueType winding convention.
"""
import os, sys
import pathops
from fontTools.svgLib.path import parse_path
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.reverseContourPen import ReverseContourPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.fontBuilder import FontBuilder

SCALE, BASELINE, UPM = 6.4, 130, 1000
SIDE, SPACE = 46, 300   # sidebearing and word-space, in font units

# ---------------------------------------------------------------- glyph source
G = {
"A":["M10,130 L10,58 A40,40 0 0 1 90,58 L90,130 M10,92 L90,92",105],
"B":["M10,20 L10,130 M10,20 A27.5,27.5 0 0 1 10,75 M10,75 A27.5,27.5 0 0 1 10,130",90],
"C":["M82,43 A45,45 0 1 0 82,107",105],
"D":["M10,20 L10,130 M10,20 A40,55 0 0 1 10,130",105],
"E":["M10,50 A30,30 0 0 1 40,20 L78,20 M10,50 L10,100 M10,100 A30,30 0 0 0 40,130 L78,130 M10,75 L62,75",95],
"F":["M10,50 A30,30 0 0 1 40,20 L78,20 M10,50 L10,130 M10,75 L62,75",90],
"G":["M82,43 A45,45 0 1 0 95,75 L60,75",108],
"H":["M10,20 L10,130 M90,20 L90,130 M10,75 L90,75",105],
"I":["M50,20 L50,130",65],
"J":["M75,20 L75,95 A32.5,32.5 0 0 1 10,95",95],
"K":["M10,20 L10,130 M85,22 C58,34 26,50 10,72 M10,78 C26,100 58,116 85,128",100],
"L":["M10,20 L10,100 A30,30 0 0 0 40,130 L82,130",95],
"M":["M10,130 L10,45 A20,20 0 0 1 50,45 L50,130 M50,45 A20,20 0 0 1 90,45 L90,130",105],
"N":["M10,20 L10,130 M90,20 L90,130 M10,32 C10,82 90,78 90,120",105],
"O":["M10,90 L10,60 A40,40 0 0 1 90,60 L90,90 A40,40 0 0 1 10,90 Z",105],
"P":["M10,20 L10,130 M10,20 A30,30 0 0 1 10,80",92],
"Q":["M10,90 L10,60 A40,40 0 0 1 90,60 L90,90 A40,40 0 0 1 10,90 Z M58,104 Q84,118 90,142",105],
"R":["M10,20 L10,130 M10,20 A30,30 0 0 1 10,80 M38,80 C58,96 74,112 86,130",100],
"S":["M69,29 A27,27 0 1 0 50,75 A27,27 0 1 1 31,121",95],
"T":["M50,20 L50,130 M14,20 L86,20",100],
"U":["M10,20 L10,90 A40,40 0 0 0 90,90 L90,20",105],
"V":["M12,20 C12,100 30,128 50,128 C70,128 88,100 88,20",102],
"W":["M8,20 L8,90 A21,21 0 0 0 50,90 A21,21 0 0 0 92,90 L92,20",108],
"X":["M15,20 C40,50 60,100 85,130 M85,20 C60,50 40,100 15,130",102],
"Y":["M15,20 C15,60 50,68 50,78 L50,130 M85,20 C85,60 50,68 50,78",102],
"Z":["M12,20 L80,20 Q40,62 12,130 L82,130",98],

"a":["M13,100 A32,30 0 1 1 77,100 A32,30 0 1 1 13,100 M77,70 L77,130",92],
"b":["M10,20 L10,130 M10,70 A30,30 0 0 1 10,130",88],
"c":["M68,74 A35,35 0 1 0 68,126",88],
"d":["M76,20 L76,130 M76,70 A30,30 0 0 0 76,130",92],
"e":["M10,100 L80,100 M80,100 A35,35 0 1 0 62,130",95],
"f":["M68,34 Q30,26 30,60 L30,130 M12,72 L58,72",72],
"g":["M13,100 A32,30 0 1 1 77,100 A32,30 0 1 1 13,100 M77,70 L77,146 Q77,170 46,170 Q26,170 18,160",92],
"h":["M10,20 L10,130 M10,100 A35,35 0 0 1 80,100 L80,130",92],
"i":["M45,130 L45,78 M40,52 A5,5 0 1 1 50,52 A5,5 0 1 1 40,52",60],
"j":["M50,78 L50,148 Q50,170 24,167 M40,52 A5,5 0 1 1 50,52 A5,5 0 1 1 40,52",62],
"k":["M10,20 L10,130 M75,72 C52,84 26,94 10,104 M10,100 C28,110 52,120 75,130",88],
"l":["M45,20 L45,130",60],
"m":["M10,70 L10,130 M10,100 A22.5,22.5 0 0 1 55,100 L55,130 M55,100 A22.5,22.5 0 0 1 100,100 L100,130",112],
"n":["M10,70 L10,130 M10,100 A35,35 0 0 1 80,100 L80,130",92],
"o":["M10,100 A35,35 0 1 1 80,100 A35,35 0 1 1 10,100",92],
"p":["M10,70 L10,170 M10,70 A30,30 0 0 1 10,130",88],
"q":["M76,70 L76,170 M76,70 A30,30 0 0 0 76,130",92],
"r":["M10,70 L10,130 M10,100 A30,30 0 0 1 60,79",72],
"s":["M59,74 A20,15 0 1 0 45,100 A20,15 0 1 1 31,126",82],
"t":["M45,36 L45,110 Q45,130 72,126 M16,70 L70,70",84],
"u":["M10,70 L10,100 A35,35 0 0 0 80,100 L80,70 M80,100 L80,130",92],
"v":["M12,70 C12,105 28,130 45,130 C62,130 78,105 78,70",90],
"w":["M8,70 L8,105 A19,19 0 0 0 46,105 A19,19 0 0 0 84,105 L84,70",96],
"x":["M12,72 C34,92 56,110 78,128 M78,72 C56,92 34,110 12,128",90],
"y":["M12,70 C12,108 28,126 46,126 M78,70 C78,120 76,156 42,170",90],
"z":["M12,70 L72,70 Q40,100 12,130 L74,130",86],

"0":["M20,90 L20,60 A30,40 0 0 1 80,60 L80,90 A30,40 0 0 1 20,90 Z",100],
"1":["M28,44 Q50,40 50,20 L50,130",80],
"2":["M14,52 A34,34 0 1 1 76,70 Q46,96 14,130 L84,130",100],
"3":["M16,42 A30,26 0 1 1 46,74 M46,74 A32,30 0 1 1 16,112",96],
"4":["M66,130 L66,26 Q30,70 14,98 L84,98",100],
"5":["M80,20 L28,20 L22,72 Q46,62 62,72 A33,33 0 1 1 20,118",100],
"6":["M18,98 A32,32 0 1 1 82,98 A32,32 0 1 1 18,98 M72,30 Q26,50 18,98",100],
"7":["M12,20 L86,20 Q54,70 44,130",96],
"8":["M24,50 A26,26 0 1 1 76,50 A26,26 0 1 1 24,50 M22,102 A28,28 0 1 1 78,102 A28,28 0 1 1 22,102",100],
"9":["M18,52 A32,32 0 1 1 82,52 A32,32 0 1 1 18,52 M82,52 Q74,100 28,120",100],

".":["M44,124 A6,6 0 1 1 56,124 A6,6 0 1 1 44,124",55],
",":["M56,120 Q56,142 42,150",55],
":":["M44,80 A6,6 0 1 1 56,80 A6,6 0 1 1 44,80 M44,124 A6,6 0 1 1 56,124 A6,6 0 1 1 44,124",55],
";":["M44,80 A6,6 0 1 1 56,80 A6,6 0 1 1 44,80 M56,120 Q56,142 42,150",55],
"!":["M50,20 L50,96 M44,124 A6,6 0 1 1 56,124 A6,6 0 1 1 44,124",55],
"?":["M18,46 A30,30 0 1 1 50,80 L50,96 M44,124 A6,6 0 1 1 56,124 A6,6 0 1 1 44,124",92],
"-":["M18,78 L72,78",90],
"\u2013":["M12,78 L88,78",100],
"\u2014":["M6,78 L112,78",120],
"_":["M8,146 L92,146",100],
"'":["M50,20 L50,50",45],
"\"":["M36,20 L36,50 M64,20 L64,50",70],
"/":["M20,136 C40,100 60,54 78,16",90],
"\\":["M20,16 C40,54 60,100 78,136",90],
"(":["M62,20 A55,55 0 0 0 62,130",70],
")":["M38,20 A55,55 0 0 1 38,130",70],
"[":["M66,20 L48,20 A22,22 0 0 0 36,42 L36,108 A22,22 0 0 0 48,130 L66,130",70],
"]":["M34,20 L52,20 A22,22 0 0 1 64,42 L64,108 A22,22 0 0 1 52,130 L34,130",70],
"+":["M50,48 L50,108 M20,78 L80,78",100],
"=":["M20,62 L80,62 M20,94 L80,94",100],
"*":["M50,18 L50,74 M26,32 L74,60 M26,60 L74,32",100],
"#":["M34,26 L26,124 M70,26 L62,124 M14,56 L82,56 M12,94 L80,94",100],
"&":["M88,130 C40,130 12,112 12,84 C12,58 62,50 62,36 A18,18 0 0 0 26,38 C26,72 62,104 88,66",110],
"@":["M66,102 A22,22 0 1 1 66,86 L66,110 A45,45 0 1 0 40,128",115],
"%":["M22,32 A13,13 0 1 1 22,58 A13,13 0 1 1 22,32 M78,92 A13,13 0 1 1 78,118 A13,13 0 1 1 78,92 M18,132 C38,96 62,52 82,18",112],
"$":["M69,44 A22,22 0 1 0 50,80 A22,22 0 1 1 31,116 M50,18 L50,142",95],
"<":["M76,32 C40,50 24,68 22,76 C24,86 40,104 76,122",100],
">":["M24,32 C60,50 76,68 78,76 C76,86 60,104 24,122",100],
" ":["",60],
}

NAMES = {  # unicode char -> glyph name
    **{c: c for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"},
    "0":"zero","1":"one","2":"two","3":"three","4":"four","5":"five","6":"six",
    "7":"seven","8":"eight","9":"nine",".":"period",",":"comma",":":"colon",
    ";":"semicolon","!":"exclam","?":"question","-":"hyphen","\u2013":"endash",
    "\u2014":"emdash","_":"underscore","'":"quotesingle","\"":"quotedbl",
    "/":"slash","\\":"backslash","(":"parenleft",")":"parenright",
    "[":"bracketleft","]":"bracketright","+":"plus","=":"equal","*":"asterisk",
    "#":"numbersign","&":"ampersand","@":"at","%":"percent","$":"dollar",
    "<":"less",">":"greater"," ":"space",
}

WEIGHTS = [  # style name, stroke width (design units), usWeightClass
    ("Light",   5.0, 300),
    ("Regular", 7.5, 400),
    ("Bold",   12.0, 700),
]

def outline(d, stroke_w):
    """Expand a monoline SVG path into a filled, TrueType-wound glyf outline."""
    path = pathops.Path()
    tp = TransformPen(path.getPen(), (SCALE, 0, 0, -SCALE, 0, BASELINE * SCALE))
    parse_path(d, tp)
    path.stroke(stroke_w * SCALE, pathops.LineCap.ROUND_CAP,
                pathops.LineJoin.ROUND_JOIN, 4)
    path.convertConicsToQuads(0.25)
    path.simplify(fix_winding=True, keep_starting_points=False)
    x_min, _, x_max, _ = path.bounds
    dx = SIDE - x_min                          # left sidebearing is optical, not drawn
    glyph_pen = TTGlyphPen(None)
    path.draw(TransformPen(ReverseContourPen(glyph_pen), (1, 0, 0, 1, dx, 0)))
    return glyph_pen.glyph(), round(x_max - x_min + 2 * SIDE)

def notdef():
    pen = TTGlyphPen(None)
    for box in ((60, 0, 500, 700), (110, 50, 450, 650)):
        x0, y0, x1, y1 = box
        pen.moveTo((x0, y0)); pen.lineTo((x0, y1)); pen.lineTo((x1, y1))
        pen.lineTo((x1, y0)); pen.closePath()
    return pen.glyph()

def build(style, stroke_w, weight_class, outdir):
    order = [".notdef"] + [NAMES[c] for c in G]
    glyphs = {".notdef": notdef()}
    metrics = {".notdef": (600, 60)}
    for ch, (d, _) in G.items():
        name = NAMES[ch]
        if d:
            glyphs[name], adv = outline(d, stroke_w)
            metrics[name] = (adv, SIDE)
        else:
            glyphs[name] = TTGlyphPen(None).glyph()
            metrics[name] = (SPACE, 0)

    fb = FontBuilder(UPM, isTTF=True)
    fb.setupGlyphOrder(order)
    fb.setupCharacterMap({ord(c): NAMES[c] for c in G})
    fb.setupGlyf(glyphs)
    fb.setupHorizontalMetrics({n: (w, lsb) for n, (w, lsb) in metrics.items()})
    fb.setupHorizontalHeader(ascent=800, descent=-260, lineGap=0)
    fam = "Arclight"
    ps = f"Arclight-{style}"
    fb.setupNameTable({
        "familyName": fam, "styleName": style,
        "uniqueFontIdentifier": f"{ps};1.000",
        "fullName": f"{fam} {style}", "psName": ps, "version": "Version 1.000",
        "copyright": "Arclight. Monoline arc typeface.",
        "designer": "Drawn as strokes on a 200-unit grid; expanded to outlines.",
    })
    fb.setupOS2(sTypoAscender=760, sTypoDescender=-260, sTypoLineGap=90,
                usWinAscent=800, usWinDescent=260, sxHeight=384, sCapHeight=704,
                usWeightClass=weight_class, achVendID="ARCL",
                fsSelection=(1 << 5) if style == "Bold" else (1 << 6))
    fb.setupPost(isFixedPitch=0, underlinePosition=-120, underlineThickness=round(stroke_w * SCALE))
    fb.font["head"].macStyle = 1 if style == "Bold" else 0

    ttf = os.path.join(outdir, f"{ps}.ttf")
    fb.save(ttf)
    fb.font.flavor = "woff2"
    fb.save(os.path.join(outdir, f"{ps}.woff2"))
    print(f"{ps}: {len(order)} glyphs, {os.path.getsize(ttf)/1024:.0f} KB ttf")
    return ttf

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    os.makedirs(out, exist_ok=True)
    for style, w, wc in WEIGHTS:
        build(style, w, wc, out)
