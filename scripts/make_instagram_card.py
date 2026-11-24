"""Animated Instagram card (logo draws itself, follower count ticks up).

    python scripts/make_instagram_card.py          # writes instagram-card.svg
    STATIC=1 python scripts/make_instagram_card.py # frozen final frame
"""
import os
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "instagram-card.svg"

HANDLE = "@parth_jairam.exe"
FOLLOWERS = "40K"
TAGLINE = "tech & building in public"
COUNT_STEPS = ["0", "2K", "5K", "9K", "14K", "20K", "26K", "31K", "35K", "38K", "39K", FOLLOWERS]

WIDTH = 514
HEIGHT = 447
TITLE_H = 30
BG = "#0d1117"
BORDER = "#30363d"
FG = "#e6edf3"
MUTED = "#8b949e"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"

LOGO = 112
LOGO_Y = 56
DRAW_END = 1.6
COUNT_START, COUNT_DUR = 1.7, 1.3
TYPE_START, TYPE_DUR = 3.1, 1.1
BUTTON_AT = 4.3


def main() -> None:
    static = os.environ.get("STATIC") == "1"
    cx = WIDTH / 2
    lx = cx - LOGO / 2
    char_w = 15 * 0.6
    tag_w = len(TAGLINE) * char_w
    tag_x = cx - tag_w / 2

    css = [f"text{{font-family:{MONO};}}"]
    if not static:
        css += [
            "@keyframes draw{to{stroke-dashoffset:0;}}",
            "@keyframes up{from{opacity:0;transform:translateY(10px);}to{opacity:1;transform:none;}}",
            "@keyframes glow{0%,100%{opacity:.18;transform:scale(.92);}50%{opacity:.42;transform:scale(1.08);}}",
            "@keyframes pulse{0%,100%{transform:scale(1);}50%{transform:scale(1.06);}}",
            "@keyframes blink{50%{opacity:0;}}",
            "@keyframes on{from,to{opacity:1;}}",
            ".d{stroke-dasharray:100;stroke-dashoffset:100;animation:draw 1.1s cubic-bezier(.6,0,.2,1) forwards;}",
            ".d2{animation-delay:.45s;}.d3{animation-delay:.9s;}",
            ".u{opacity:0;animation:up .5s ease-out forwards;}",
            ".g{transform-box:fill-box;transform-origin:center;opacity:0;"
            f"animation:glow 2.8s ease-in-out {DRAW_END}s infinite;}}",
            ".b{transform-box:fill-box;transform-origin:center;"
            f"animation:pulse 2.4s ease-in-out {BUTTON_AT + 0.6}s infinite;}}",
            f".c{{animation:blink 1s step-end {TYPE_START + TYPE_DUR}s infinite;}}",
        ]

    def delay(t: float) -> str:
        return "" if static else f' style="animation-delay:{t:.2f}s"'

    s = LOGO
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">',
        f"<style>{''.join(css)}</style>",
        "<defs>",
        '<linearGradient id="ig" x1="0" y1="1" x2="1" y2="0">'
        '<stop offset="0" stop-color="#feda75"/><stop offset=".3" stop-color="#fa7e1e"/>'
        '<stop offset=".55" stop-color="#d62976"/><stop offset=".8" stop-color="#962fbf"/>'
        '<stop offset="1" stop-color="#4f5bd5"/></linearGradient>',
        '<radialGradient id="halo"><stop offset="0" stop-color="#d62976" stop-opacity=".9"/>'
        '<stop offset=".55" stop-color="#962fbf" stop-opacity=".35"/>'
        '<stop offset="1" stop-color="#4f5bd5" stop-opacity="0"/></radialGradient>',
        f'<clipPath id="type"><rect x="{tag_x:.1f}" y="300" width="{0 if not static else tag_w:.1f}" height="30">'
        + (
            ""
            if static
            else f'<animate attributeName="width" from="0" to="{tag_w:.1f}" begin="{TYPE_START}s" '
            f'dur="{TYPE_DUR}s" fill="freeze" calcMode="discrete" '
            f'values="{";".join(f"{i * char_w:.1f}" for i in range(len(TAGLINE) + 1))}"/>'
        )
        + "</rect></clipPath>",
        "</defs>",
        f'<rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{HEIGHT - 1}" rx="10" fill="{BG}" stroke="{BORDER}"/>',
        '<circle cx="18" cy="15" r="5" fill="#ff5f56"/><circle cx="34" cy="15" r="5" fill="#ffbd2e"/>'
        '<circle cx="50" cy="15" r="5" fill="#27c93f"/>',
        f'<text x="{cx}" y="19" fill="{MUTED}" font-size="11" text-anchor="middle" style="font-size:11px">'
        "instagram.app</text>",
        f'<line x1="0" y1="{TITLE_H}" x2="{WIDTH}" y2="{TITLE_H}" stroke="{BORDER}"/>',
        # Halo behind the logo
        f'<circle class="g" cx="{cx}" cy="{LOGO_Y + s / 2}" r="{s * 0.78:.0f}" fill="url(#halo)"'
        + (' opacity=".3"' if static else "")
        + "/>",
        # Logo: rounded square, lens, flash dot
        f'<g fill="none" stroke="url(#ig)" stroke-width="9" stroke-linecap="round">'
        f'<rect class="d" pathLength="100" x="{lx + 4.5}" y="{LOGO_Y + 4.5}" width="{s - 9}" height="{s - 9}" rx="30"/>'
        f'<circle class="d d2" pathLength="100" cx="{cx}" cy="{LOGO_Y + s / 2}" r="{s * 0.23:.1f}"/></g>',
        f'<circle class="u" cx="{lx + s * 0.76:.1f}" cy="{LOGO_Y + s * 0.24:.1f}" r="7" fill="url(#ig)"{delay(1.35)}/>',
        # Handle
        f'<text class="u" x="{cx}" y="{LOGO_Y + s + 40}" fill="{FG}" font-size="20" font-weight="bold" '
        f'text-anchor="middle"{delay(1.5)}>{HANDLE}</text>',
    ]

    # Follower counter
    count_y = LOGO_Y + s + 92
    steps = [FOLLOWERS] if static else COUNT_STEPS
    n = len(steps)
    for i, label in enumerate(steps):
        attrs = f'x="{cx}" y="{count_y}" fill="url(#ig)" font-size="44" font-weight="bold" text-anchor="middle"'
        if static:
            parts.append(f"<text {attrs}>{label}</text>")
            continue
        # ease-out: steps get further apart as the count settles
        t0 = COUNT_START + COUNT_DUR * (1 - (1 - i / n) ** 2)
        t1 = COUNT_START + COUNT_DUR * (1 - (1 - (i + 1) / n) ** 2)
        if i == n - 1:
            anim = f"animation:up .35s ease-out {t0:.3f}s forwards"
        else:
            anim = f"animation:on {t1 - t0:.3f}s linear {t0:.3f}s"
        parts.append(f'<text {attrs} opacity="0" style="{anim}">{label}</text>')
    parts.append(
        f'<text class="u" x="{cx}" y="{count_y + 24}" fill="{MUTED}" font-size="15" text-anchor="middle"'
        f'{delay(COUNT_START)}>followers</text>'
    )

    # Tagline types itself in, followed by a blinking cursor
    tag_y = 321
    parts.append(
        f'<text x="{tag_x:.1f}" y="{tag_y}" fill="{FG}" font-size="15" clip-path="url(#type)">{escape(TAGLINE)}</text>'
    )
    if not static:
        parts.append(
            f'<rect class="c" x="{tag_x:.1f}" y="{tag_y - 13}" width="8" height="16" fill="#39d353" opacity="0">'
            f'<set attributeName="opacity" to="1" begin="{TYPE_START}s"/>'
            f'<animate attributeName="x" begin="{TYPE_START}s" dur="{TYPE_DUR}s" fill="freeze" calcMode="discrete" '
            f'values="{";".join(f"{tag_x + i * char_w:.1f}" for i in range(len(TAGLINE) + 1))}"/></rect>'
        )

    # Follow button
    bw, bh, by = 170, 42, 356
    parts.append(
        f'<g class="u"{delay(BUTTON_AT)}><g class="b">'
        f'<rect x="{cx - bw / 2}" y="{by}" width="{bw}" height="{bh}" rx="{bh / 2}" fill="url(#ig)"/>'
        f'<text x="{cx}" y="{by + 27}" fill="#ffffff" font-size="16" font-weight="bold" text-anchor="middle">'
        "Follow \u2197</text></g></g>"
    )
    parts.append("</svg>")
    OUT.write_text("\n".join(parts) + "\n")
    print(f"wrote {OUT.name}: {WIDTH}x{HEIGHT}")


if __name__ == "__main__":
    main()
