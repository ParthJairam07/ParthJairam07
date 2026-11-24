"""Hand-authored neofetch-style info card.

    python scripts/make_info_card.py          # writes info-card.svg
    STATIC=1 python scripts/make_info_card.py # frozen final frame
"""
import os
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "info-card.svg"

BG = "#0d1117"
BORDER = "#30363d"
FG = "#c9d1d9"
MUTED = "#8b949e"
KEY = "#39d353"
ACCENT = "#58a6ff"
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace"

WIDTH = 620
FONT_SIZE = 15
LINE_H = 25
PAD_X = 22
KEY_W = 12  # characters reserved for the key column

# (key, value). Empty key = continuation line; None = blank spacer.
ROWS = [
    ("Now", "Forward Deployed Engineer @ Turing Labs (YC W20)"),
    ("Prev", "Data Scientist Co-op @ Kenvue (Johnson & Johnson)"),
    ("", "Software Engineer Intern @ Savi-Finance"),
    ("School", "University of Toronto"),
    ("", "Computer Science & Statistics (GPA = 3.7)"),
    None,
    ("Founded", "Eyeris: sold to a hospital"),
    ("", "raised an angel pre-seed round"),
    ("Clubs", "Co-President, UofT Creator Club"),
    ("", "Director of Academics, GDSC"),
    ("", "VP of AI, Neuravia Research Inc."),
    ("Mentor", "HackThe6ix, HuskyHacks, UofTHacks"),
    None,
    ("Langs", "Python, TypeScript, Kotlin, Go, C/C++"),
    ("Stack", "FastAPI, Node.js, React/Next.js, React Native"),
    ("ML", "PyTorch, LangChain, XGBoost, Databricks"),
    ("Cloud", "Docker, Google Cloud Run, Azure, CI/CD"),
    None,
    ("Instagram", "40K followers · tech & building in public"),
    ("Web", "parthjairam.codes"),
    ("LinkedIn", "linkedin.com/in/parth-jairam"),
    ("Email", "parth.jairam06@gmail.com"),
]

ICON = 15


def instagram_logo(x: float, y: float) -> str:
    s = ICON
    return (
        f'<g transform="translate({x:.1f},{y:.1f})">'
        f'<rect x="0.9" y="0.9" width="{s - 1.8}" height="{s - 1.8}" rx="4.2" fill="none" stroke="url(#ig)" stroke-width="1.8"/>'
        f'<circle cx="{s / 2}" cy="{s / 2}" r="3.3" fill="none" stroke="url(#ig)" stroke-width="1.8"/>'
        f'<circle cx="{s - 4}" cy="4" r="1.1" fill="url(#ig)"/></g>'
    )

SWATCHES = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0", "#58a6ff", "#d2a8ff"]


def main() -> None:
    static = os.environ.get("STATIC") == "1"
    title_h = 30
    y = title_h + 34
    char_w = FONT_SIZE * 0.6

    css = [f"text{{font-family:{FONT};font-size:{FONT_SIZE}px;}}"]
    if not static:
        css += [
            "@keyframes in{from{opacity:0;transform:translateX(-10px);}to{opacity:1;transform:none;}}",
            ".l{opacity:0;animation:in .35s ease-out forwards;}",
        ]

    body = []
    step = 0

    def line(content: str) -> None:
        nonlocal step
        style = "" if static else f' style="animation-delay:{0.25 + step * 0.09:.2f}s"'
        body.append(f'<g class="l"{style}>{content}</g>')
        step += 1

    line(
        f'<text x="{PAD_X}" y="{y}"><tspan fill="{KEY}" font-weight="bold">parth</tspan>'
        f'<tspan fill="{FG}">@</tspan><tspan fill="{ACCENT}" font-weight="bold">github</tspan></text>'
    )
    y += LINE_H - 6
    line(
        f'<text x="{PAD_X}" y="{y}" fill="{MUTED}">{"-" * 12}</text>'
    )
    y += LINE_H
    vx = PAD_X + KEY_W * char_w
    for row in ROWS:
        if row is None:
            y += LINE_H // 2
            continue
        key, val = row
        tx = vx
        icon = ""
        if key == "Instagram":
            icon = instagram_logo(vx, y - ICON + 3)
            tx = vx + ICON + 7
        k = f'<tspan fill="{KEY}" font-weight="bold">{escape(key)}</tspan><tspan fill="{MUTED}">:</tspan>' if key else ""
        line(
            f'<text x="{PAD_X}" y="{y}">{k}</text>'
            f'{icon}<text x="{tx:.1f}" y="{y}" fill="{FG}">{escape(val)}</text>'
        )
        y += LINE_H
    y += 6
    sw = "".join(
        f'<rect x="{PAD_X + i * 26}" y="{y - 12}" width="22" height="14" rx="2" fill="{c}"/>'
        for i, c in enumerate(SWATCHES)
    )
    line(sw)
    height = y + 26

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" '
        f'viewBox="0 0 {WIDTH} {height}">',
        f"<style>{''.join(css)}</style>",
        '<defs><linearGradient id="ig" x1="0" y1="1" x2="1" y2="0">'
        '<stop offset="0" stop-color="#feda75"/><stop offset=".35" stop-color="#fa7e1e"/>'
        '<stop offset=".6" stop-color="#d62976"/><stop offset=".8" stop-color="#962fbf"/>'
        '<stop offset="1" stop-color="#4f5bd5"/></linearGradient></defs>',
        f'<rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1}" rx="10" fill="{BG}" stroke="{BORDER}"/>',
        '<circle cx="18" cy="15" r="5" fill="#ff5f56"/><circle cx="34" cy="15" r="5" fill="#ffbd2e"/>'
        '<circle cx="50" cy="15" r="5" fill="#27c93f"/>',
        f'<text x="{WIDTH / 2}" y="19" fill="{MUTED}" font-size="11" text-anchor="middle" '
        'style="font-size:11px">parth@github: ~ $ neofetch</text>',
        f'<line x1="0" y1="{title_h}" x2="{WIDTH}" y2="{title_h}" stroke="{BORDER}"/>',
        *body,
        "</svg>",
    ]
    OUT.write_text("\n".join(parts) + "\n")
    print(f"wrote {OUT.name}: {WIDTH}x{height}")


if __name__ == "__main__":
    main()
