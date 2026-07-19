#!/usr/bin/env python3
"""Render a neofetch-style info card SVG with staggered fade/slide-in rows.

Output: info-card.svg
Edit ROWS below (Prev / Highlights) with your real details.
"""

USER = "fog"
HOST = "github"

# (key, value). key="" -> full-width value line; key=None -> blank spacer
ROWS = [
    (None, ""),
    ("Now", "side projects — padel-court-finder, World-Monitor, arb_bot"),
    ("Prev", "<edit me: previous role / studies>"),
    ("Stack", "TypeScript · JavaScript · Python · Go · CSS"),
    ("Focus", "web apps, bots, data monitoring"),
    ("Highlights", "<edit me: a thing you're proud of>"),
    (None, ""),
]

BG = "#0d1117"
BORDER = "#30363d"
ACCENT = "#39d353"   # green
KEY = "#58a6ff"      # blue
VAL = "#c9d1d9"      # light gray
DIM = "#8b949e"

W = 620
PAD = 22
LINE_H = 26
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
STAGGER = 0.08
DUR = 0.45


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def anim(begin):
    return (
        f'<animateTransform attributeName="transform" type="translate" '
        f'from="-16 0" to="0 0" dur="{DUR}s" begin="{begin:.3f}s" '
        f'calcMode="spline" keySplines="0.2 0 0 1" keyTimes="0;1" fill="freeze"/>'
        f'<animate attributeName="opacity" from="0" to="1" dur="{DUR}s" '
        f'begin="{begin:.3f}s" fill="freeze"/>'
    )


def main():
    header = f"{USER}@{HOST}"
    rule = "─" * (len(header))
    lines = [("_header", header), ("_rule", rule)] + ROWS
    H = PAD * 2 + LINE_H * len(lines) + 6

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" font-family="{FONT}" font-size="14">',
        f'<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="10" '
        f'fill="{BG}" stroke="{BORDER}"/>',
        # faux window dots
        f'<circle cx="20" cy="18" r="5" fill="#ff5f56"/>'
        f'<circle cx="38" cy="18" r="5" fill="#ffbd2e"/>'
        f'<circle cx="56" cy="18" r="5" fill="#27c93f"/>',
    ]

    y0 = 44
    i = 0
    for kind, val in lines:
        y = y0 + i * LINE_H
        begin = i * STAGGER
        g = [f'<g opacity="0">{anim(begin)}']
        if kind == "_header":
            g.append(f'<text x="{PAD}" y="{y}" fill="{ACCENT}" '
                     f'font-weight="bold">{esc(val)}</text>')
        elif kind == "_rule":
            g.append(f'<text x="{PAD}" y="{y}" fill="{DIM}">{esc(val)}</text>')
        elif kind is None:
            g.append(f'<text x="{PAD}" y="{y}" fill="{DIM}"> </text>')
        elif kind == "":
            g.append(f'<text x="{PAD}" y="{y}" fill="{VAL}">{esc(val)}</text>')
        else:
            g.append(
                f'<text x="{PAD}" y="{y}"><tspan fill="{KEY}" '
                f'font-weight="bold">{esc(kind)}</tspan>'
                f'<tspan fill="{DIM}">: </tspan>'
                f'<tspan fill="{VAL}">{esc(val)}</tspan></text>'
            )
        g.append("</g>")
        parts.append("".join(g))
        i += 1

    parts.append("</svg>")
    with open("info-card.svg", "w") as f:
        f.write("\n".join(parts))
    print(f"Saved info-card.svg ({len(lines)} lines)")


if __name__ == "__main__":
    main()
