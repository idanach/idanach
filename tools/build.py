"""Makes the profile page's pictures from idanach.com's own material, so the profile looks like the site.

    python -X utf8 tools/build.py [out folder, default assets] [site|terminal|blueprint]

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


def banner_terminal(look: str, faces: str, tiles: dict[str, str]) -> str:
    """The same first screen as a terminal: `whoami` prints the name, `ls ~/work` the projects, and the cursor
    blinks; a few project pictures turn at the window's right, as the orbit does on the site."""
    c = LOOKS[look]
    win = "#0E1330" if look == "dark" else "#F6F4EE"
    x0, y0, w, h = 40, 28, W - 80, H - 56
    pics = []
    for i, slug in enumerate(ORBIT[:7]):
        a = 2 * math.pi * i / 7 + 0.6
        depth = (math.sin(a) + 1) / 2
        tw = 70 + 70 * depth
        th = tw * 10 / 16
        pics.append((depth, slug, 965 + 120 * math.cos(a) - tw / 2, 250 + 150 * math.sin(a) - th / 2, tw, th))
    tiles_svg = "".join(
        f'<g opacity="{0.25 + 0.45 * d:.2f}"><clipPath id="t-{s}"><rect x="{x:.1f}" y="{y:.1f}" width="{tw:.1f}" height="{th:.1f}" rx="5"/></clipPath>'
        f'<image href="data:image/jpeg;base64,{tiles[s]}" x="{x:.1f}" y="{y:.1f}" width="{tw:.1f}" height="{th:.1f}" '
        f'preserveAspectRatio="xMidYMid slice" clip-path="url(#t-{s})"/>'
        f'<rect x="{x:.1f}" y="{y:.1f}" width="{tw:.1f}" height="{th:.1f}" rx="5" fill="none" stroke="{c["line"]}"/></g>'
        for d, s, x, y, tw, th in sorted(pics))
    prompt = f'<tspan fill="{c["accent"]}">idan@idanach.com</tspan><tspan fill="{c["muted"]}">:~$ </tspan>'
    work1 = "  ".join(s + "/" for s in WORK[:4])
    work2 = "  ".join(s + "/" for s in ["launchpad", "mobilesign", "hamal", "milestone", "wicogen"]) + "  +6"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Idan Achrak. I build whole systems, from the server to the last pixel.">
<style>{faces}
.m{{font-family:'JetBrains Mono',monospace;font-size:18px;fill:{c["fg"]}}}
.s{{font-family:'JetBrains Mono',monospace;font-size:16px;fill:{c["accent"]};white-space:pre}}
.t{{font-family:'JetBrains Mono',monospace;font-size:13px;fill:{c["muted"]}}}
.n{{font-family:'Schibsted Grotesk',sans-serif;font-weight:850;font-size:80px;letter-spacing:-2px;fill:{c["fg"]}}}
.l{{font-family:'Schibsted Grotesk',sans-serif;font-weight:400;font-size:24px;fill:{c["fg"]}}}
.a{{font-family:'Instrument Serif',serif;font-style:italic;font-size:29px;fill:{c["accent"]}}}
.cur{{animation:blink 1.1s steps(1) infinite}}@keyframes blink{{50%{{opacity:0}}}}
</style>
<rect width="{W}" height="{H}" rx="18" fill="{c["bg"]}"/>
<clipPath id="win"><rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="14"/></clipPath>
<rect x="{x0}" y="{y0}" width="{w}" height="{h}" rx="14" fill="{win}" stroke="{c["line"]}"/>
<g clip-path="url(#win)">{tiles_svg}</g>
<circle cx="{x0 + 24}" cy="{y0 + 19}" r="6" fill="{c["line"]}"/><circle cx="{x0 + 44}" cy="{y0 + 19}" r="6" fill="{c["line"]}"/><circle cx="{x0 + 64}" cy="{y0 + 19}" r="6" fill="{c["accent"]}"/>
<text class="t" x="{W / 2}" y="{y0 + 24}" text-anchor="middle">idan@idanach.com: ~</text>
<line x1="{x0}" y1="{y0 + 38}" x2="{x0 + w}" y2="{y0 + 38}" stroke="{c["line"]}"/>
<text class="m" x="72" y="104">{prompt}whoami</text>
<text class="n" x="68" y="188">{NAME}</text>
<text class="l" x="72" y="232">{LEAD[0]}<tspan class="a">{LEAD[1]}</tspan>{LEAD[2]}</text>
<text class="m" x="72" y="294">{prompt}ls ~/work</text>
<text class="s" x="72" y="330">{work1}</text>
<text class="s" x="72" y="358">{work2}</text>
<text class="m" x="72" y="412">{prompt}</text><rect class="cur" x="{72 + 21 * 10.84:.1f}" y="396" width="11" height="21" fill="{c["fg"]}"/>
</svg>
'''


def banner_blueprint(look: str, faces: str) -> str:
    """The first screen as one of the site's blueprint plates: the name measured on a grid, and under it the stack
    drawn from the server to the last pixel."""
    c = LOOKS[look]
    defs = (f'<defs><pattern id="g" width="20" height="20" patternUnits="userSpaceOnUse"><path d="M20 0H0V20" fill="none" stroke="{c["line"]}" stroke-width=".6" opacity=".55"/></pattern>'
            f'<pattern id="G" width="100" height="100" patternUnits="userSpaceOnUse"><path d="M100 0H0V100" fill="none" stroke="{c["line"]}" stroke-width="1"/></pattern>'
            f'<marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L10 5L0 10z" fill="{c["muted"]}"/></marker></defs>')
    nx0, nx1 = 290, 910
    stack = [("DATABASE", "PostgreSQL · SQL Server"), ("SERVER", "Flask · REST APIs"), ("DEPLOY", "Docker · OpenShift"), ("INTERFACE", "React · TypeScript")]
    bw, gap, by = 182, 34, 352
    bx0 = (W - (len(stack) * bw + len(stack) * gap + 150)) / 2
    boxes = ""
    for i, (title, sub) in enumerate(stack):
        x = bx0 + i * (bw + gap)
        boxes += (f'<rect x="{x:.1f}" y="{by}" width="{bw}" height="62" rx="8" fill="{c["bg"]}" stroke="{c["line"]}"/>'
                  f'<text class="bt" x="{x + 16:.1f}" y="{by + 26}">{i + 1:02d} {title}</text><text class="bs" x="{x + 16:.1f}" y="{by + 46}">{sub}</text>'
                  f'<line x1="{x + bw:.1f}" y1="{by + 31}" x2="{x + bw + gap - 3:.1f}" y2="{by + 31}" stroke="{c["muted"]}" marker-end="url(#ar)"/>')
    px = bx0 + len(stack) * (bw + gap)
    boxes += (f'<rect x="{px:.1f}" y="{by + 17}" width="28" height="28" rx="3" fill="{c["accent"]}"/>'
              f'<text class="pa" x="{px + 40:.1f}" y="{by + 38}">the last pixel</text>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Idan Achrak. I build whole systems, from the server to the last pixel.">
<style>{faces}
.k{{font-family:'JetBrains Mono',monospace;font-size:12px;letter-spacing:2px;fill:{c["muted"]}}}
.d{{font-family:'JetBrains Mono',monospace;font-size:12px;fill:{c["accent"]}}}
.n{{font-family:'Schibsted Grotesk',sans-serif;font-weight:850;font-size:92px;fill:{c["fg"]}}}
.l{{font-family:'Schibsted Grotesk',sans-serif;font-weight:400;font-size:23px;fill:{c["fg"]}}}
.bt{{font-family:'JetBrains Mono',monospace;font-size:12px;letter-spacing:1px;fill:{c["fg"]}}}
.bs{{font-family:'JetBrains Mono',monospace;font-size:11px;fill:{c["muted"]}}}
.pa{{font-family:'Instrument Serif',serif;font-style:italic;font-size:24px;fill:{c["accent"]}}}
</style>
{defs}
<rect width="{W}" height="{H}" rx="18" fill="{c["bg"]}"/>
<rect width="{W}" height="{H}" rx="18" fill="url(#g)"/><rect width="{W}" height="{H}" rx="18" fill="url(#G)" opacity=".6"/>
<rect x="22" y="22" width="{W - 44}" height="{H - 44}" rx="10" fill="none" stroke="{c["muted"]}"/>
<text class="k" x="44" y="54">PLATE 01 · PROFILE</text>
<text class="k" x="{W - 44}" y="54" text-anchor="end">SCALE 1 : 1 · IDANACH.COM</text>
<line x1="{nx0}" y1="104" x2="{nx1}" y2="104" stroke="{c["accent"]}"/>
<line x1="{nx0}" y1="96" x2="{nx0}" y2="128" stroke="{c["accent"]}"/><line x1="{nx1}" y1="96" x2="{nx1}" y2="128" stroke="{c["accent"]}"/>
<rect x="{W / 2 - 74}" y="94" width="148" height="20" fill="{c["bg"]}"/><text class="d" x="{W / 2}" y="108" text-anchor="middle">FULL STACK · {nx1 - nx0}</text>
<text class="n" x="{nx0}" y="214" textLength="{nx1 - nx0}" lengthAdjust="spacing">{NAME}</text>
<text class="l" x="{W / 2}" y="268" text-anchor="middle">{LEAD[0]}<tspan class="pa" font-size="28">{LEAD[1]}</tspan>{LEAD[2]}</text>
<text class="k" x="{W / 2}" y="326" text-anchor="middle">{KICKER}</text>
{boxes}
</svg>
'''


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    variant = sys.argv[2] if len(sys.argv) > 2 else "site"
    # every banner's letters: printable ASCII and the middle dot, in each font
    letters = "".join(chr(i) for i in range(32, 127)) + "·"
    faces = "".join([
        font_face("Schibsted Grotesk", "schibsted-grotesk-latin-wght-normal.woff2", letters, "400 900"),
        font_face("Instrument Serif", "instrument-serif-latin-400-italic.woff2", LEAD[1], "400", "italic"),
        font_face("JetBrains Mono", "jetbrains-mono-latin-wght-normal.woff2", letters, "100 800"),
    ])
    tiles = {s: tile_data(s) for s in ORBIT}
    for look in LOOKS:
        f = OUT / f"banner-{look}.svg"
        svg = (banner_terminal(look, faces, tiles) if variant == "terminal"
               else banner_blueprint(look, faces) if variant == "blueprint" else banner(look, faces, tiles))
        f.write_text(svg, encoding="utf-8")
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
