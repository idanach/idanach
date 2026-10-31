"""A LinkedIn cover in the GitHub banner's blueprint look: 1584 x 396, LinkedIn's size. The profile photo covers the
lower left, so everything sits right of it: the kicker, the line, and the stack drawn from the server to the last
pixel, with idanach.com.

    python -X utf8 tools/linkedin_cover.py [out folder, default linkedin]     writes cover-<look>.svg
    node tools/render.mjs linkedin/cover-night.svg                            the PNG to upload, at the same size
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build import KICKER, LEAD, LOOKS, font_face  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / (sys.argv[1] if len(sys.argv) > 1 else "linkedin")
W, H = 1584, 396
STACK = [("DATABASE", "PostgreSQL · SQL Server"), ("SERVER", "Flask · REST APIs"), ("DEPLOY", "Docker · CI/CD"),
         ("INTERFACE", "React · TypeScript")]


def cover(look: str, faces: str) -> str:
    c = LOOKS[look]
    x0 = 470                                   # the photo's column ends about here
    bw, gap, by = 186, 28, 252
    boxes = ""
    for i, (title, sub) in enumerate(STACK):
        x = x0 + i * (bw + gap)
        boxes += (f'<rect x="{x}" y="{by}" width="{bw}" height="62" rx="8" fill="{c["bg"]}" stroke="{c["line"]}"/>'
                  f'<text class="bt" x="{x + 16}" y="{by + 26}">{i + 1:02d} {title}</text><text class="bs" x="{x + 16}" y="{by + 46}">{sub}</text>'
                  f'<line x1="{x + bw}" y1="{by + 31}" x2="{x + bw + gap - 3}" y2="{by + 31}" stroke="{c["muted"]}" marker-end="url(#ar)"/>')
    px = x0 + len(STACK) * (bw + gap)
    boxes += (f'<rect x="{px}" y="{by + 17}" width="28" height="28" rx="3" fill="{c["accent"]}"/>'
              f'<text class="pa" x="{px + 40}" y="{by + 38}">the last pixel</text>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
<style>{faces}
.k{{font-family:'JetBrains Mono',monospace;font-size:14px;letter-spacing:2.5px;fill:{c["muted"]}}}
.l{{font-family:'Schibsted Grotesk',sans-serif;font-weight:500;font-size:44px;letter-spacing:-.5px;fill:{c["fg"]}}}
.a{{font-family:'Instrument Serif',serif;font-style:italic;font-size:52px;fill:{c["accent"]}}}
.bt{{font-family:'JetBrains Mono',monospace;font-size:13px;letter-spacing:1px;fill:{c["fg"]}}}
.bs{{font-family:'JetBrains Mono',monospace;font-size:12px;fill:{c["muted"]}}}
.pa{{font-family:'Instrument Serif',serif;font-style:italic;font-size:27px;fill:{c["accent"]}}}
</style>
<defs><pattern id="g" width="22" height="22" patternUnits="userSpaceOnUse"><path d="M22 0H0V22" fill="none" stroke="{c["line"]}" stroke-width=".6" opacity=".55"/></pattern>
<pattern id="G" width="110" height="110" patternUnits="userSpaceOnUse"><path d="M110 0H0V110" fill="none" stroke="{c["line"]}"/></pattern>
<marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path d="M0 0L10 5L0 10z" fill="{c["muted"]}"/></marker></defs>
<rect width="{W}" height="{H}" fill="{c["bg"]}"/>
<rect width="{W}" height="{H}" fill="url(#g)"/><rect width="{W}" height="{H}" fill="url(#G)" opacity=".6"/>
<rect x="20" y="20" width="{W - 40}" height="{H - 40}" rx="10" fill="none" stroke="{c["muted"]}"/>
<text class="k" x="44" y="56">PLATE 01 · PROFILE</text>
<text class="k" x="{W - 44}" y="56" text-anchor="end">IDANACH.COM</text>
<text class="k" x="{x0}" y="128">{KICKER}</text>
<text class="l" x="{x0}" y="196">{LEAD[0]}<tspan class="a">{LEAD[1]}</tspan>{LEAD[2]}</text>
{boxes}
</svg>
'''


def main() -> None:
    letters = "".join(chr(i) for i in range(32, 127)) + "·"
    faces = "".join([
        font_face("Schibsted Grotesk", "schibsted-grotesk-latin-wght-normal.woff2", letters, "400 900"),
        font_face("Instrument Serif", "instrument-serif-latin-400-italic.woff2", LEAD[1] + "the last pixel", "400", "italic"),
        font_face("JetBrains Mono", "jetbrains-mono-latin-wght-normal.woff2", letters, "100 800"),
    ])
    OUT.mkdir(parents=True, exist_ok=True)
    for look in ("dark", "light"):
        name = "night" if look == "dark" else "paper"
        f = OUT / f"cover-{name}.svg"
        f.write_text(cover(look, faces), encoding="utf-8")
        print(f.relative_to(ROOT))


if __name__ == "__main__":
    main()
