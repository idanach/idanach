"""Activity cards for the profile page, counted across all of Idan's repositories, private ones included, and drawn in
idanach.com's night colours. Only totals are shown: no repository names.

    python -X utf8 tools/stats.py [out folder, default assets]

Reads GitHub's GraphQL API through the gh command line (signed in as Idan, or GH_TOKEN with read access to his private
repositories when run by a scheduled workflow) and writes stats.svg (contributions in the last year, repositories, the
year he started) and langs.svg (his languages by share of code).
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / (sys.argv[1] if len(sys.argv) > 1 else "assets")
C = {"bg": "#0A0E22", "fg": "#EEF0FA", "muted": "#8E95B8", "line": "#232B52", "accent": "#8F7BFF"}
FONT = "'Segoe UI', system-ui, -apple-system, Helvetica, Arial, sans-serif"
QUERY = """{ user(login:"idanach"){ createdAt
  contributionsCollection { contributionCalendar { totalContributions } }
  repositories(first:100, ownerAffiliations:OWNER){ totalCount nodes { isFork
    languages(first:10, orderBy:{field:SIZE,direction:DESC}){ edges { size node { name color } } } } } } }"""


def fetch() -> dict:
    out = subprocess.run(["gh", "api", "graphql", "-f", f"query={QUERY}"], capture_output=True, text=True,
                         encoding="utf-8", check=True)
    return json.loads(out.stdout)["data"]["user"]


def card(w: int, h: int, title: str, inner: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{title}">'
            f'<style>text{{font-family:{FONT}}}</style>'
            f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="12" fill="{C["bg"]}" stroke="{C["line"]}"/>'
            f'<text x="24" y="38" font-size="15" font-weight="600" fill="{C["accent"]}">{title}</text>{inner}</svg>\n')


def main() -> None:
    u = fetch()
    year = u["createdAt"][:4]
    total = u["contributionsCollection"]["contributionCalendar"]["totalContributions"]
    repos = u["repositories"]["totalCount"]
    figures = [(f"{total:,}", "contributions in the last year"), (str(repos), "repositories, most of them private"),
               (year, "on GitHub since")]
    inner = "".join(
        f'<text x="{24 + i * 128}" y="96" font-size="34" font-weight="700" fill="{C["fg"]}">{v}</text>'
        f'<text x="{24 + i * 128}" y="120" font-size="12" fill="{C["muted"]}">'
        + "".join(f'<tspan x="{24 + i * 128}" dy="{0 if j == 0 else 15}">{part}</tspan>' for j, part in enumerate(_wrap(k)))
        + "</text>"
        for i, (v, k) in enumerate(figures))
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "stats.svg").write_text(card(410, 165, "At a glance", inner), encoding="utf-8")

    langs: dict[str, list] = {}
    for n in u["repositories"]["nodes"]:
        if n["isFork"]:
            continue
        for e in n["languages"]["edges"]:
            langs.setdefault(e["node"]["name"], [0, e["node"]["color"] or C["muted"]])[0] += e["size"]
    top = sorted(langs.items(), key=lambda x: -x[1][0])[:5]
    whole = sum(v[0] for v in langs.values())
    x, bar = 24.0, []
    for name, (size, color) in top:
        w = 362 * size / whole
        bar.append(f'<rect x="{x:.1f}" y="58" width="{w:.1f}" height="10" fill="{color}"/>')
        x += w
    legend = "".join(
        f'<circle cx="{30 + (i % 3) * 125}" cy="{96 + (i // 3) * 26}" r="5" fill="{color}"/>'
        f'<text x="{42 + (i % 3) * 125}" y="{101 + (i // 3) * 26}" font-size="13" fill="{C["fg"]}">{name} '
        f'<tspan fill="{C["muted"]}">{100 * size / whole:.0f}%</tspan></text>'
        for i, (name, (size, color)) in enumerate(top))
    clip = '<clipPath id="r"><rect x="24" y="58" width="362" height="10" rx="5"/></clipPath>'
    (OUT / "langs.svg").write_text(card(410, 165, "Languages", f'{clip}<g clip-path="url(#r)">{"".join(bar)}</g>{legend}'),
                                   encoding="utf-8")
    print(f"stats: {total:,} contributions, {repos} repositories; languages: {', '.join(n for n, _ in top)}")


def _wrap(text: str, width: int = 18) -> list[str]:
    words, lines, line = text.split(), [], ""
    for w in words:
        if len(line) + len(w) + 1 > width and line:
            lines.append(line)
            line = w
        else:
            line = f"{line} {w}".strip()
    return lines + [line]


if __name__ == "__main__":
    main()
