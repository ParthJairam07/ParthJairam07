"""Convert source-prepped.png into a self-typing monochrome ASCII SVG.

    python scripts/make_ascii_svg.py        # writes parth-ascii.svg
    STATIC=1 python scripts/make_ascii_svg.py   # frozen final frame
"""
import os
from pathlib import Path
from xml.sax.saxutils import escape

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "parth-ascii.svg"

COLS = 92
# Head-and-shoulders crop of source-prepped.png as (left, top, right, bottom) fractions.
CROP = (0.12, 0.06, 0.88, 0.78)
CELL_W = 5.24
CELL_H = 11.0
FONT_SIZE = 10.4
PAD = 16
TITLE_H = 30
RAMP = " .`:-=+*cs#%@"  # sparse -> dense
NBSP = "\u00a0"  # plain spaces collapse in SVG text and break column alignment
FG = "#c9d1d9"
BG = "#0d1117"
BORDER = "#30363d"

ROW_DELAY = 0.045
ROW_DUR = 0.32


def grid() -> list[str]:
    gray = Image.open(ROOT / "source-prepped.png").convert("L")
    mask = Image.open(ROOT / "source-mask.png").convert("L")
    w, h = gray.size
    box = (round(CROP[0] * w), round(CROP[1] * h), round(CROP[2] * w), round(CROP[3] * h))
    gray, mask = gray.crop(box), mask.crop(box)
    w, h = gray.size
    rows = round(COLS * (h / w) * (CELL_W / CELL_H))
    g = np.asarray(gray.resize((COLS, rows), Image.LANCZOS), dtype=np.float32) / 255.0
    m = np.asarray(mask.resize((COLS, rows), Image.LANCZOS), dtype=np.float32) / 255.0
    # Dark areas (hair, jacket) get dense glyphs so the subject reads as a solid shape.
    g = 1.0 - np.clip((g - g[m > 0.5].min()) / max(1e-6, np.ptp(g[m > 0.5])), 0.0, 1.0)
    idx = np.clip((g ** 1.1) * (len(RAMP) - 1), 1, len(RAMP) - 1).round().astype(int)
    idx[m < 0.5] = 0
    return ["".join(RAMP[i] for i in row) for row in idx]


def main() -> None:
    static = os.environ.get("STATIC") == "1"
    lines = grid()
    text_w = COLS * CELL_W
    width = text_w + 2 * PAD
    height = TITLE_H + len(lines) * CELL_H + 2 * PAD

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" '
        f'viewBox="0 0 {width:.0f} {height:.0f}">',
        f'<rect x="0.5" y="0.5" width="{width - 1:.0f}" height="{height - 1:.0f}" rx="10" '
        f'fill="{BG}" stroke="{BORDER}"/>',
        '<circle cx="18" cy="15" r="5" fill="#ff5f56"/><circle cx="34" cy="15" r="5" fill="#ffbd2e"/>'
        '<circle cx="50" cy="15" r="5" fill="#27c93f"/>',
        f'<text x="{width / 2:.0f}" y="19" fill="#8b949e" font-size="11" text-anchor="middle" '
        'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">parth.txt</text>',
        f'<line x1="0" y1="{TITLE_H}" x2="{width:.0f}" y2="{TITLE_H}" stroke="{BORDER}"/>',
        "<defs>",
    ]
    y0 = TITLE_H + PAD
    for i in range(len(lines)):
        y = y0 + i * CELL_H
        begin = i * ROW_DELAY
        rect_w = text_w if static else 0
        anim = (
            ""
            if static
            else f'<animate attributeName="width" from="0" to="{text_w:.0f}" begin="{begin:.3f}s" '
            f'dur="{ROW_DUR}s" fill="freeze"/>'
        )
        parts.append(
            f'<clipPath id="r{i}"><rect x="{PAD}" y="{y:.1f}" width="{rect_w:.0f}" '
            f'height="{CELL_H:.1f}">{anim}</rect></clipPath>'
        )
    parts.append("</defs>")
    parts.append(
        f'<g fill="{FG}" font-size="{FONT_SIZE}" '
        'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,\'Liberation Mono\',monospace" '
        'xml:space="preserve">'
    )
    for i, line in enumerate(lines):
        if not line.strip():
            continue
        y = y0 + i * CELL_H
        parts.append(
            f'<text x="{PAD}" y="{y + CELL_H * 0.8:.1f}" textLength="{text_w:.0f}" '
            f'lengthAdjust="spacingAndGlyphs" clip-path="url(#r{i})">{escape(line).replace(" ", NBSP)}</text>'
        )
    parts.append("</g>")

    if not static:
        # A block cursor rides the wipe edge of each row, then disappears.
        for i, line in enumerate(lines):
            if not line.strip():
                continue
            y = y0 + i * CELL_H
            begin = i * ROW_DELAY
            parts.append(
                f'<rect x="{PAD}" y="{y + 1:.1f}" width="{CELL_W:.0f}" height="{CELL_H - 2:.1f}" '
                f'fill="#39d353" opacity="0">'
                f'<set attributeName="opacity" to="1" begin="{begin:.3f}s"/>'
                f'<animate attributeName="x" from="{PAD}" to="{PAD + text_w:.0f}" '
                f'begin="{begin:.3f}s" dur="{ROW_DUR}s" fill="freeze"/>'
                f'<set attributeName="opacity" to="0" begin="{begin + ROW_DUR:.3f}s"/>'
                "</rect>"
            )
    parts.append("</svg>")
    OUT.write_text("\n".join(parts) + "\n")
    print(f"wrote {OUT.name}: {COLS}x{len(lines)} chars")


if __name__ == "__main__":
    main()
