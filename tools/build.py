"""Makes the profile page's pictures from idanach.com's own material, so the profile looks like the site.

    python -X utf8 tools/build.py [out folder, default assets]

- banner-dark.svg / banner-light.svg: the site's first screen as a banner: the name inside an orbit of project
  pictures, the kicker above it and the line under it, in the site's fonts (subset and embedded, so GitHub shows them)
  and colours (night and paper). GitHub picks one by the reader's theme (<picture> in README.md).
- work/<slug>.jpg: each featured project's colour cover, 800 px wide, for the cards that open its case study.

Everything comes from the Portfolio repository next to this one (its fonts, its covers and tiles, its mark), so the
same inputs give the same files.
"""
from __future__ import annotations

import base64
import io
import math
import sys
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT.parent / "Portfolio"
FONTS = SITE / "public" / "fonts"
GEN = SITE / "src" / "assets" / "generated"
OUT = ROOT / (sys.argv[1] if len(sys.argv) > 1 else "assets")

# the site's colours (src/styles/tokens.css): paper and night
LOOKS = {
    "light": {"bg": "#EFEDE6", "fg": "#121212", "muted": "#67655E", "line": "#CFCBBE", "accent": "#5B3DF5", "tile": "#DAD6CA"},
    "dark": {"bg": "#0A0E22", "fg": "#EEF0FA", "muted": "#8E95B8", "line": "#232B52", "accent": "#8F7BFF", "tile": "#161D42"},
}
KICKER = "SENIOR FULL STACK DEVELOPER · SYSTEM BUILDER · DESIGNER"
NAME = "IDAN ACHRAK"
LEAD = ("I build whole systems, from the server to ", "the last pixel", ".")
# the projects whose pictures turn round the name (the site's orbit tiles), and the cards under the banner
ORBIT = ["taaz-platform", "tovanto", "console-ui", "launchpad", "mobilesign", "hamal", "milestone", "taaztv",
         "aka-conference-clock", "pinger", "t100", "aka-attendees-tracker"]
WORK = ["taaz-platform", "tovanto", "console-ui", "transport-platform", "launchpad", "mobilesign"]
W, H = 1200, 470


def font_face(family: str, file: str, text: str, weight: str, style: str = "normal") -> str:
    """A @font-face holding only the letters the banner uses, as woff2 in a data address."""
    font = TTFont(FONTS / file)
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = ["*"]
    sub = subset.Subsetter(opts)
    sub.populate(text=text)
    sub.subset(font)
    buf = io.BytesIO()
    font.flavor = "woff2"
    font.save(buf)
    data = base64.b64encode(buf.getvalue()).decode()
    return (f"@font-face{{font-family:'{family}';font-style:{style};font-weight:{weight};"
            f"src:url(data:font/woff2;base64,{data}) format('woff2')}}")


def tile_data(slug: str, width: int = 240) -> str:
    im = Image.open(GEN / "tiles" / f"{slug}.jpg").convert("RGB")
    im = im.resize((width, round(width * im.height / im.width)), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=72, optimize=True)
    return base64.b64encode(buf.getvalue()).decode()


def mark(c: dict, x: float, y: float, size: float) -> str:
    """The site's orbit mark (public/favicon.svg), drawn at x, y in a size x size box."""
    s = size / 64
    return (f'<g transform="translate({x},{y}) scale({s})">'
            f'<g transform="rotate(-24 32 32)"><path fill="none" stroke="{c["fg"]}" stroke-width="3.6" d="M3 32 A29 11 0 0 1 61 32"/></g>'
            f'<path fill="{c["fg"]}" transform="translate(18.25,52) scale(0.02778,-0.02778)" d="M84 0V345H290V1095H84V1440H906V1095H700V345H906V0Z"/>'
            f'<g transform="rotate(-24 32 32)"><path fill="none" stroke="{c["fg"]}" stroke-width="3.6" d="M61 32 A29 11 0 0 1 3 32"/>'
            f'<circle fill="{c["accent"]}" cx="46" cy="41.3" r="5.6"/></g></g>')


def banner(look: str, faces: str, tiles: dict[str, str]) -> str:
    c = LOOKS[look]
    cx, cy, rx, ry = W / 2, 240, 545, 158
    placed = []
    n = len(ORBIT)
    for i, slug in enumerate(ORBIT):
        a = 2 * math.pi * i / n + 0.35
        depth = (math.sin(a) + 1) / 2          # 0 at the back (top), 1 at the front (bottom)
        w = 88 + 92 * depth
        h = w * 10 / 16
        x = cx + rx * math.cos(a) - w / 2
        y = cy + ry * math.sin(a) - h / 2
        placed.append((depth, slug, x, y, w, h))
    parts = []
    for depth, slug, x, y, w, h in sorted(placed):
        o = 0.28 + 0.5 * depth
        parts.append(
            f'<g opacity="{o:.2f}"><clipPath id="c-{slug}"><rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="6"/></clipPath>'
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="6" fill="{c["tile"]}"/>'
            f'<image href="data:image/jpeg;base64,{tiles[slug]}" x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'preserveAspectRatio="xMidYMid slice" clip-path="url(#c-{slug})"/>'
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="6" fill="none" stroke="{c["line"]}"/></g>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Idan Achrak. I build whole systems, from the server to the last pixel.">
<style>{faces}
.k{{font-family:'JetBrains Mono',monospace;font-size:13px;letter-spacing:3px;fill:{c["muted"]}}}
.n{{font-family:'Schibsted Grotesk',sans-serif;font-weight:850;font-size:94px;letter-spacing:-2px;fill:{c["fg"]}}}
.l{{font-family:'Schibsted Grotesk',sans-serif;font-weight:400;font-size:25px;fill:{c["fg"]}}}
.a{{font-family:'Instrument Serif',serif;font-style:italic;font-size:30px;fill:{c["accent"]}}}
.b{{font-family:'Schibsted Grotesk',sans-serif;font-weight:700;font-size:15px;letter-spacing:.5px;fill:{c["fg"]}}}
.u{{font-family:'JetBrains Mono',monospace;font-size:13px;fill:{c["muted"]}}}
</style>
<defs><radialGradient id="glow" cx="50%" cy="54%" r="38%"><stop offset="0" stop-color="{c["bg"]}" stop-opacity=".92"/><stop offset="1" stop-color="{c["bg"]}" stop-opacity="0"/></radialGradient></defs>
<rect width="{W}" height="{H}" rx="18" fill="{c["bg"]}"/>
<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="none" stroke="{c["line"]}" stroke-dasharray="2 7"/>
{"".join(parts)}
<rect width="{W}" height="{H}" fill="url(#glow)"/>
{mark(c, 34, 24, 30)}<text class="b" x="72" y="45">IDAN ACHRAK</text><text class="u" x="{W - 34}" y="45" text-anchor="end">idanach.com</text>
<text class="k" x="{cx}" y="176" text-anchor="middle">{KICKER}</text>
<text class="n" x="{cx}" y="262" text-anchor="middle">{NAME}</text>
<text class="l" x="{cx}" y="312" text-anchor="middle">{LEAD[0]}<tspan class="a">{LEAD[1]}</tspan>{LEAD[2]}</text>
</svg>
'''


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    grotesk = NAME + LEAD[0] + LEAD[2] + "IDAN ACHRAK"
    faces = "".join([
        font_face("Schibsted Grotesk", "schibsted-grotesk-latin-wght-normal.woff2", grotesk, "400 900"),
        font_face("Instrument Serif", "instrument-serif-latin-400-italic.woff2", LEAD[1], "400", "italic"),
        font_face("JetBrains Mono", "jetbrains-mono-latin-wght-normal.woff2", KICKER + "idanach.com", "100 800"),
    ])
    tiles = {s: tile_data(s) for s in ORBIT}
    for look in LOOKS:
        f = OUT / f"banner-{look}.svg"
        f.write_text(banner(look, faces, tiles), encoding="utf-8")
        print(f"{f.relative_to(ROOT)}: {f.stat().st_size // 1024} KB")
    (OUT / "work").mkdir(exist_ok=True)
    for slug in WORK:
        im = Image.open(GEN / "covers" / f"{slug}.jpg").convert("RGB")
        im = im.resize((800, 500), Image.LANCZOS)
        f = OUT / "work" / f"{slug}.jpg"
        im.save(f, "JPEG", quality=82, optimize=True, progressive=True)
        print(f"{f.relative_to(ROOT)}: {f.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
