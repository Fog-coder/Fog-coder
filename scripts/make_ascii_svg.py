#!/usr/bin/env python3
"""Convert source-prepped.png into an animated ASCII-art SVG portrait.

Downsamples to a character grid, maps brightness to a density ramp, and
reveals the art with a staggered per-row horizontal wipe (SMIL clipPath).

Output: avi-ascii.svg
"""
from PIL import Image, ImageOps

INP = "source-prepped.png"
OUT = "avi-ascii.svg"

# lightest -> densest
RAMP = " .`:-=+*cs#%@"
COLS = 74            # character columns
CHAR_ASPECT = 0.52  # glyph width / height for monospace
CELL_W = 7.2
CELL_H = 13.0
FONT_SIZE = 12
FG = "#39d353"      # terminal green
BG = "#0d1117"
STAGGER = 0.045     # seconds between row reveals
DUR = 0.5           # per-row wipe duration


def to_rows():
    img = ImageOps.grayscale(Image.open(INP).convert("RGB"))
    w, h = img.size
    rows = max(1, int(COLS * (h / w) * CHAR_ASPECT))
    img = img.resize((COLS, rows))
    px = img.load()
    n = len(RAMP) - 1
    out = []
    for y in range(rows):
        line = []
        for x in range(COLS):
            b = px[x, y]                 # 0 dark .. 255 light
            idx = int((255 - b) / 255 * n)  # dark -> dense
            line.append(RAMP[idx])
        out.append("".join(line).rstrip() or " ")
    return out


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def main():
    rows = to_rows()
    grid_w = COLS * CELL_W
    grid_h = len(rows) * CELL_H
    pad = 16
    W = grid_w + pad * 2
    H = grid_h + pad * 2

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="{H:.0f}" '
        f'viewBox="0 0 {W:.0f} {H:.0f}" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">',
        f'<rect width="{W:.0f}" height="{H:.0f}" rx="10" fill="{BG}"/>',
        "<defs>",
    ]
    # one clip per row for the staggered horizontal wipe
    for i in range(len(rows)):
        begin = i * STAGGER
        parts.append(
            f'<clipPath id="c{i}"><rect x="{pad}" y="{pad + i * CELL_H:.1f}" '
            f'height="{CELL_H:.1f}" width="0">'
            f'<animate attributeName="width" from="0" to="{grid_w:.1f}" '
            f'dur="{DUR}s" begin="{begin:.3f}s" fill="freeze" '
            f'calcMode="spline" keySplines="0.2 0 0 1" keyTimes="0;1"/>'
            f'</rect></clipPath>'
        )
    parts.append("</defs>")

    for i, line in enumerate(rows):
        y = pad + i * CELL_H + FONT_SIZE
        parts.append(
            f'<text x="{pad}" y="{y:.1f}" clip-path="url(#c{i})" '
            f'xml:space="preserve" font-size="{FONT_SIZE}" fill="{FG}" '
            f'letter-spacing="0">{esc(line)}</text>'
        )
    parts.append("</svg>")

    with open(OUT, "w") as f:
        f.write("\n".join(parts))
    print(f"Saved {OUT} ({len(rows)} rows x {COLS} cols)")


if __name__ == "__main__":
    main()
