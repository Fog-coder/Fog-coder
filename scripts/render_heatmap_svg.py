#!/usr/bin/env python3
"""Render data/contributions.json as an animated 53x7 contribution heatmap SVG.

Diagonal slide-in wave, month + weekday labels, legend, stats footer.
Output: contrib-heatmap.svg
"""
import json
import datetime as dt

INP = "data/contributions.json"
OUT = "contrib-heatmap.svg"

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
BG = "#0d1117"
TEXT = "#8b949e"
BRIGHT = "#c9d1d9"

CELL = 11
GAP = 3
STEP = CELL + GAP
LEFT = 30      # weekday label column
TOP = 22       # month label row
WAVE = 0.012   # per-diagonal-step delay
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def color(day):
    lvl = day["level"]
    if lvl >= 4 and day["count"] >= 10:
        return PALETTE[5]
    return PALETTE[min(lvl, 4)]


def main():
    data = json.load(open(INP))
    days = data["days"]
    if not days:
        raise SystemExit("No days in contributions.json")

    # place each day into (col=week, row=weekday, Sunday top)
    first = dt.date.fromisoformat(days[0]["date"])
    start = first - dt.timedelta(days=(first.weekday() + 1) % 7)  # back to Sunday

    cells = []
    max_col = 0
    month_at = {}
    for d in days:
        date = dt.date.fromisoformat(d["date"])
        col = (date - start).days // 7
        row = (date.weekday() + 1) % 7
        max_col = max(max_col, col)
        cells.append((col, row, d, date))
        if date.day <= 7 and row == 0:
            month_at.setdefault(col, MONTHS[date.month - 1])

    weeks = max_col + 1
    grid_w = weeks * STEP
    W = LEFT + grid_w + 16
    H = TOP + 7 * STEP + 60

    p = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" font-family="{FONT}" font-size="10">',
        f'<rect width="{W}" height="{H}" rx="10" fill="{BG}"/>',
    ]

    # month labels
    for col, name in sorted(month_at.items()):
        x = LEFT + col * STEP
        p.append(f'<text x="{x}" y="14" fill="{TEXT}">{name}</text>')

    # weekday labels
    for row, name in [(1, "Mon"), (3, "Wed"), (5, "Fri")]:
        y = TOP + row * STEP + CELL - 1
        p.append(f'<text x="0" y="{y}" fill="{TEXT}">{name}</text>')

    # day cells with diagonal wave
    for col, row, d, date in cells:
        x = LEFT + col * STEP
        y = TOP + row * STEP
        begin = (col + row) * WAVE
        p.append(
            f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" '
            f'fill="{color(d)}" opacity="0">'
            f'<animate attributeName="opacity" from="0" to="1" dur="0.35s" '
            f'begin="{begin:.3f}s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" '
            f'from="0 -6" to="0 0" dur="0.35s" begin="{begin:.3f}s" '
            f'calcMode="spline" keySplines="0.2 0 0 1" keyTimes="0;1" fill="freeze"/>'
            f'<title>{d["count"]} on {d["date"]}</title>'
            f'</rect>'
        )

    # legend
    lx = W - 16 - 6 * STEP - 60
    ly = TOP + 7 * STEP + 18
    p.append(f'<text x="{lx}" y="{ly + CELL - 1}" fill="{TEXT}">Less</text>')
    for i, c in enumerate(PALETTE[:5]):
        cx = lx + 34 + i * STEP
        p.append(f'<rect x="{cx}" y="{ly}" width="{CELL}" height="{CELL}" '
                 f'rx="2" fill="{c}"/>')
    p.append(f'<text x="{lx + 34 + 5 * STEP + 4}" y="{ly + CELL - 1}" '
             f'fill="{TEXT}">More</text>')

    # stats footer
    fy = TOP + 7 * STEP + 40
    stats = (f'{data["total"]} contributions in the last year   ·   '
             f'current streak {data["current_streak"]}d   ·   '
             f'longest {data["longest_streak"]}d')
    p.append(f'<text x="{LEFT}" y="{fy}" fill="{BRIGHT}" font-size="11">{stats}</text>')

    p.append("</svg>")
    with open(OUT, "w") as f:
        f.write("\n".join(p))
    print(f"Saved {OUT} ({weeks} weeks, {len(cells)} days)")


if __name__ == "__main__":
    main()
