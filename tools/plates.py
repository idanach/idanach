"""The profile page's developer plates, drawn like the blueprint banner (PLATE 01): the same grid, frame, labels and
fonts, in idanach.com's night and paper colours. Counted across all of Idan's repositories, private ones included;
only totals and days are shown, never a repository's name.

    python -X utf8 tools/plates.py [out folder, default assets]

  plate-glance-<look>.svg     PLATE 02 · contributions in the last year, repositories, stars, the year he started
  plate-activity-<look>.svg   PLATE 03 · the last twelve months, day by day (GitHub's own calendar)
  plate-languages-<look>.svg  PLATE 04 · his languages by share of code

Reads GitHub's GraphQL API through the gh command line (signed in as Idan, or GH_TOKEN with read access to his private
repositories when a scheduled workflow runs it). README.md shows each through <picture>, by the reader's theme.
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build import LOOKS, font_face  # noqa: E402  (the banner's colours and fonts)

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / (sys.argv[1] if len(sys.argv) > 1 else "assets")
W = 1200
QUERY = """{ user(login:"idanach"){ createdAt
  contributionsCollection { contributionCalendar { totalContributions weeks { contributionDays { date contributionCount } } } }
  repositories(first:100, ownerAffiliations:OWNER){ totalCount nodes { isFork stargazerCount
    languages(first:10, orderBy:{field:SIZE,direction:DESC}){ edges { size node { name color } } } } } } }"""


def fetch() -> dict:
    out = subprocess.run(["gh", "api", "graphql", "-f", f"query={QUERY}"], capture_output=True, text=True,
                         encoding="utf-8", check=True)
    return json.loads(out.stdout)["data"]["user"]


def rgba(hex_: str, a: float) -> str:
    h = hex_.lstrip("#")
    return f"rgba({int(h[0:2], 16)},{int(h[2:4], 16)},{int(h[4:6], 16)},{a})"


def plate(look: str, faces: str, h: int, label: str, right: str, body: str) -> str:
    """A plate: the grid, the frame and its two labels, with `body` drawn on it."""
    c = LOOKS[look]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" width="{W}" height="{h}" role="img" aria-label="{label}">
<style>{faces}
.k{{font-family:'JetBrains Mono',monospace;font-size:12px;letter-spacing:2px;fill:{c["muted"]}}}
.m{{font-family:'JetBrains Mono',monospace;font-size:13px;fill:{c["muted"]}}}
.f{{font-family:'JetBrains Mono',monospace;font-size:14px;fill:{c["fg"]}}}
.n{{font-family:'Schibsted Grotesk',sans-serif;font-weight:850;font-size:58px;letter-spacing:-1px;fill:{c["fg"]}}}
</style>
<defs><pattern id="g" width="20" height="20" patternUnits="userSpaceOnUse"><path d="M20 0H0V20" fill="none" stroke="{c["line"]}" stroke-width=".6" opacity=".55"/></pattern>
<pattern id="G" width="100" height="100" patternUnits="userSpaceOnUse"><path d="M100 0H0V100" fill="none" stroke="{c["line"]}"/></pattern></defs>
<rect width="{W}" height="{h}" rx="18" fill="{c["bg"]}"/>
<rect width="{W}" height="{h}" rx="18" fill="url(#g)"/><rect width="{W}" height="{h}" rx="18" fill="url(#G)" opacity=".6"/>
<rect x="22" y="22" width="{W - 44}" height="{h - 44}" rx="10" fill="none" stroke="{c["muted"]}"/>
<text class="k" x="44" y="54">{label}</text><text class="k" x="{W - 44}" y="54" text-anchor="end">{right}</text>
{body}
</svg>
'''


def glance(u: dict, look: str, faces: str) -> str:
    c = LOOKS[look]
    total = u["contributionsCollection"]["contributionCalendar"]["totalContributions"]
    repos = u["repositories"]["totalCount"]
    stars = sum(n["stargazerCount"] for n in u["repositories"]["nodes"])
    figures = [(f"{total:,}", "contributions in", "the last year"), (str(repos), "repositories,", "most of them private"),
               (str(stars), "stars on my", "open-source projects"), (u["createdAt"][:4], "on GitHub", "since")]
    col = (W - 120) / len(figures)
    body = ""
    for i, (v, a, b) in enumerate(figures):
        x = 60 + i * col
        body += (f'<text class="n" x="{x:.0f}" y="138">{v}</text>'
                 f'<text class="m" x="{x:.0f}" y="168">{a}</text><text class="m" x="{x:.0f}" y="186">{b}</text>')
        if i:
            body += f'<line x1="{x - 24:.0f}" y1="88" x2="{x - 24:.0f}" y2="186" stroke="{c["line"]}"/>'
    return plate(look, faces, 220, "PLATE 02 · AT A GLANCE", "COUNTED ACROSS ALL MY REPOSITORIES", body)


def activity(u: dict, look: str, faces: str) -> str:
    c = LOOKS[look]
    cal = u["contributionsCollection"]["contributionCalendar"]
    weeks = cal["weeks"]
    counts = sorted(d["contributionCount"] for w in weeks for d in w["contributionDays"] if d["contributionCount"])
    top = counts[int(len(counts) * 0.95)] if counts else 1          # a few very busy days do not wash the rest out
    step = (W - 140) / len(weeks)
    cell = step - 4
    x0, y0 = 96, 106

    def tone(lv: int) -> str:
        return c["tile"] if lv == 0 else rgba(c["accent"], [0, .3, .52, .76, 1][lv])

    def shade(n: int) -> str:
        return tone(0 if n == 0 else min(4, 1 + int(4 * n / (top + 1))))

    cells, months, last = [], [], None
    for i, w in enumerate(weeks):
        for d in w["contributionDays"]:
            day = date.fromisoformat(d["date"])
            row = (day.weekday() + 1) % 7                            # Sunday on top, as GitHub draws it
            x, y = x0 + i * step, y0 + row * step
            cells.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{cell:.1f}" height="{cell:.1f}" rx="3" fill="{shade(d["contributionCount"])}">'
                         f'<title>{d["contributionCount"]} on {d["date"]}</title></rect>')
            if row == 0 and day.day <= 7 and day.month != last:
                months.append(f'<text class="m" x="{x:.1f}" y="{y0 - 12}">{day.strftime("%b").upper()}</text>')
                last = day.month
    days = "".join(f'<text class="m" x="{x0 - 12}" y="{y0 + r * step + cell - 3:.1f}" text-anchor="end">{n}</text>'
                   for r, n in ((1, "MON"), (3, "WED"), (5, "FRI")))
    h = int(y0 + 7 * step + 70)
    lx = W - 60 - 5 * 22 - 90
    legend = (f'<text class="m" x="{lx}" y="{h - 40}">LESS</text>'
              + "".join(f'<rect x="{lx + 46 + i * 22}" y="{h - 52}" width="16" height="16" rx="3" fill="{tone(i)}"/>' for i in range(5))
              + f'<text class="m" x="{lx + 46 + 5 * 22 + 6}" y="{h - 40}">MORE</text>')
    total = cal["totalContributions"]
    return plate(look, faces, h, "PLATE 03 · ACTIVITY", f"{total:,} CONTRIBUTIONS · LAST 12 MONTHS",
                 "".join(months) + days + "".join(cells) + legend)


def languages(u: dict, look: str, faces: str) -> str:
    c = LOOKS[look]
    sizes: dict[str, list] = {}
    for n in u["repositories"]["nodes"]:
        if n["isFork"]:
            continue
        for e in n["languages"]["edges"]:
            sizes.setdefault(e["node"]["name"], [0, e["node"]["color"] or c["muted"]])[0] += e["size"]
    whole = sum(v[0] for v in sizes.values())
    # (a language under 1% would read as 0%)
    top = [x for x in sorted(sizes.items(), key=lambda x: -x[1][0]) if x[1][0] / whole >= .01][:6]
    x, bar = 60.0, []
    for name, (size, color) in top:
        w = (W - 120) * size / whole
        bar.append(f'<rect x="{x:.1f}" y="88" width="{w:.1f}" height="14" fill="{color}"/>')
        x += w
    col = (W - 120) / len(top)
    legend = "".join(
        f'<circle cx="{66 + i * col:.0f}" cy="140" r="6" fill="{color}"/>'
        f'<text class="f" x="{80 + i * col:.0f}" y="145">{name} <tspan fill="{c["muted"]}">{100 * size / whole:.0f}%</tspan></text>'
        for i, (name, (size, color)) in enumerate(top))
    body = (f'<clipPath id="r"><rect x="60" y="88" width="{W - 120}" height="14" rx="7"/></clipPath>'
            f'<g clip-path="url(#r)">{"".join(bar)}</g>{legend}')
    return plate(look, faces, 190, "PLATE 04 · LANGUAGES", "BY SHARE OF CODE", body)


def main() -> None:
    u = fetch()
    letters = "".join(chr(i) for i in range(32, 127)) + "·"
    faces = "".join([
        font_face("Schibsted Grotesk", "schibsted-grotesk-latin-wght-normal.woff2", "0123456789,", "400 900"),
        font_face("JetBrains Mono", "jetbrains-mono-latin-wght-normal.woff2", letters, "100 800"),
    ])
    OUT.mkdir(parents=True, exist_ok=True)
    for look in LOOKS:
        for name, fn in (("glance", glance), ("activity", activity), ("languages", languages)):
            f = OUT / f"plate-{name}-{look}.svg"
            f.write_text(fn(u, look, faces), encoding="utf-8")
            print(f"{f.relative_to(ROOT)}: {f.stat().st_size // 1024} KB")


if __name__ == "__main__":
    main()
