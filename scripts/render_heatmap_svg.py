"""Render data/contributions.json as an animated contribution heatmap SVG.

    python scripts/render_heatmap_svg.py          # writes contrib-heatmap.svg
    STATIC=1 python scripts/render_heatmap_svg.py # frozen final frame
"""
import json
import os
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "contrib-heatmap.svg"

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
BG = "#0d1117"
BORDER = "#30363d"
MUTED = "#8b949e"
FG = "#c9d1d9"
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"

CELL = 12
GAP = 3
LEFT = 44
TOP = 58
WIDTH = 860


def main() -> None:
    static = os.environ.get("STATIC") == "1"
    data = json.loads((ROOT / "data" / "contributions.json").read_text())
    days = data["days"]
    first = date.fromisoformat(days[0]["date"])
    start = first - timedelta(days=(first.weekday() + 1) % 7)  # back to Sunday
    best = max(d["count"] for d in days) or 1

    cells = []
    weeks = 0
    for d in days:
        dt = date.fromisoformat(d["date"])
        offset = (dt - start).days
        wk, dow = divmod(offset, 7)
        weeks = max(weeks, wk + 1)
        level = d["level"]
        if d["count"] and d["count"] >= max(best * 0.75, 1) and level == 4:
            level = 5
        cells.append((wk, dow, level, d))

    grid_w = weeks * (CELL + GAP) - GAP
    left = (WIDTH - grid_w) / 2 + 12
    height = TOP + 7 * (CELL + GAP) + 74

    css = [
        f"text{{font-family:{FONT};}}",
        ".c{transform-box:fill-box;transform-origin:center;}",
    ]
    if not static:
        css += [
            "@keyframes drop{0%{opacity:0;transform:translateY(-8px) scale(.6);}"
            "100%{opacity:1;transform:none;}}",
            "@keyframes fade{from{opacity:0;}to{opacity:1;}}",
            ".c{opacity:0;animation:drop .45s cubic-bezier(.2,.8,.2,1) forwards;}",
            ".f{opacity:0;animation:fade .6s ease-out forwards;}",
        ]

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height:.0f}" '
        f'viewBox="0 0 {WIDTH} {height:.0f}">',
        f"<style>{''.join(css)}</style>",
        f'<rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1:.0f}" rx="10" fill="{BG}" '
        f'stroke="{BORDER}"/>',
        '<circle cx="18" cy="15" r="5" fill="#ff5f56"/><circle cx="34" cy="15" r="5" fill="#ffbd2e"/>'
        '<circle cx="50" cy="15" r="5" fill="#27c93f"/>',
        f'<text x="{WIDTH / 2}" y="19" fill="{MUTED}" font-size="11" text-anchor="middle">'
        f'{data["user"].lower()}@github: ~/contributions</text>',
        f'<line x1="0" y1="30" x2="{WIDTH}" y2="30" stroke="{BORDER}"/>',
    ]

    seen = set()
    for wk, dow, _, d in cells:
        dt = date.fromisoformat(d["date"])
        key = (dt.year, dt.month)
        if dt.day <= 7 and dow == 0 and key not in seen and wk < weeks - 2:
            seen.add(key)
            x = left + wk * (CELL + GAP)
            parts.append(
                f'<text x="{x:.1f}" y="{TOP - 8}" fill="{MUTED}" font-size="10">'
                f'{dt.strftime("%b")}</text>'
            )
    for dow, name in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        y = TOP + dow * (CELL + GAP) + CELL - 2
        parts.append(
            f'<text x="{left - 8:.1f}" y="{y}" fill="{MUTED}" font-size="10" '
            f'text-anchor="end">{name}</text>'
        )

    for wk, dow, level, d in cells:
        x = left + wk * (CELL + GAP)
        y = TOP + dow * (CELL + GAP)
        delay = (wk + dow) * 0.022
        style = "" if static else f' style="animation-delay:{delay:.3f}s"'
        n = d["count"]
        label = f'{n} contribution{"" if n == 1 else "s"} on {d["date"]}'
        parts.append(
            f'<rect class="c" x="{x:.1f}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" '
            f'fill="{PALETTE[level]}"{style}><title>{label}</title></rect>'
        )

    done = (weeks + 7) * 0.022 + 0.3
    fstyle = "" if static else f' style="animation-delay:{done:.2f}s"'
    legend_y = TOP + 7 * (CELL + GAP) + 16
    right = left + grid_w
    lx = right - len(PALETTE) * (CELL + GAP) - 36
    parts.append(f'<g class="f"{fstyle}>')
    parts.append(
        f'<text x="{lx - 6:.1f}" y="{legend_y + 10}" fill="{MUTED}" font-size="10" '
        f'text-anchor="end">Less</text>'
    )
    for i, color in enumerate(PALETTE):
        parts.append(
            f'<rect x="{lx + i * (CELL + GAP):.1f}" y="{legend_y}" width="{CELL}" height="{CELL}" '
            f'rx="2.5" fill="{color}"/>'
        )
    parts.append(
        f'<text x="{lx + len(PALETTE) * (CELL + GAP) + 3:.1f}" y="{legend_y + 10}" fill="{MUTED}" '
        f'font-size="10">More</text>'
    )
    parts.append(
        f'<text x="{left:.1f}" y="{legend_y + 10}" fill="{FG}" font-size="12">'
        f'<tspan fill="#39d353" font-weight="bold">{data["total"]:,}</tspan> contributions in the last year'
        "</text>"
    )

    best_day = date.fromisoformat(data["best_day"]["date"]).strftime("%b %-d")
    stats = [
        ("current streak", f'{data["current_streak"]}d'),
        ("longest streak", f'{data["longest_streak"]}d'),
        ("best day", f'{data["best_day"]["count"]} ({best_day})'),
        ("active days", f'{data["active_days"]}'),
    ]
    sy = legend_y + 40
    col_w = grid_w / len(stats)
    for i, (k, v) in enumerate(stats):
        x = left + i * col_w
        parts.append(
            f'<text x="{x:.1f}" y="{sy}" font-size="11"><tspan fill="{MUTED}">{k}: </tspan>'
            f'<tspan fill="{FG}" font-weight="bold">{v}</tspan></text>'
        )
    parts.append("</g></svg>")
    OUT.write_text("\n".join(parts) + "\n")
    print(f"wrote {OUT.name}: {weeks} weeks, {len(cells)} days")


if __name__ == "__main__":
    main()
