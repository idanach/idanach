"""The year's contributions as a map of days in idanach.com's colours, counted across all of Idan's repositories,
private ones included (GitHub's own calendar, which shows only how many on each day, never where).

    python -X utf8 tools/heatmap.py [out folder, default assets]

Reads the calendar through the gh command line (signed in as Idan, or GH_TOKEN when a scheduled workflow runs it) and
writes activity-dark.svg and activity-light.svg; README.md picks one by the reader's theme.
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / (sys.argv[1] if len(sys.argv) > 1 else "assets")
LOOKS = {
    "light": {"bg": "#EFEDE6", "fg": "#121212", "muted": "#67655E", "line": "#CFCBBE", "accent": (91, 61, 245), "empty": "#DAD6CA"},
    "dark": {"bg": "#0A0E22", "fg": "#EEF0FA", "muted": "#8E95B8", "line": "#232B52", "accent": (143, 123, 255), "empty": "#161D42"},
}
FONT = "'JetBrains Mono', ui-monospace, Consolas, monospace"
QUERY = """{ user(login:"idanach"){ contributionsCollection { contributionCalendar { totalContributions
  weeks { contributionDays { date contributionCount } } } } } }"""
CELL, GAP, LEFT, TOP = 12, 3, 40, 52


def fetch() -> dict:
    out = subprocess.run(["gh", "api", "graphql", "-f", f"query={QUERY}"], capture_output=True, text=True,
                         encoding="utf-8", check=True)
    return json.loads(out.stdout)["data"]["user"]["contributionsCollection"]["contributionCalendar"]


def level(n: int, top: int) -> int:
    if n == 0:
        return 0
    return min(4, 1 + int(4 * n / (top + 1)))


def svg(cal: dict, look: str) -> str:
    c = LOOKS[look]
    weeks = cal["weeks"]
    counts = sorted(d["contributionCount"] for w in weeks for d in w["contributionDays"] if d["contributionCount"])
    top = counts[int(len(counts) * 0.95)] if counts else 1          # a few very busy days do not wash the rest out
    r, g, b = c["accent"]
    shade = lambda lv: c["empty"] if lv == 0 else f"rgba({r},{g},{b},{[0, .3, .52, .76, 1][lv]})"
    cells, months, last_month = [], [], None
    for x, w in enumerate(weeks):
        for d in w["contributionDays"]:
            day = date.fromisoformat(d["date"])
            y = (day.weekday() + 1) % 7                               # Sunday on top, as GitHub draws it
            cells.append(f'<rect x="{LEFT + x * (CELL + GAP)}" y="{TOP + y * (CELL + GAP)}" width="{CELL}" height="{CELL}" rx="3" '
                         f'fill="{shade(level(d["contributionCount"], top))}"><title>{d["contributionCount"]} on {d["date"]}</title></rect>')
            if day.day <= 7 and y == 0 and day.month != last_month:
                months.append(f'<text x="{LEFT + x * (CELL + GAP)}" y="{TOP - 10}" class="t">{day.strftime("%b")}</text>')
                last_month = day.month
    width = LEFT + len(weeks) * (CELL + GAP) + 20
    height = TOP + 7 * (CELL + GAP) + 44
    legend_x = width - 20 - 5 * (CELL + GAP) - 80
    legend = "".join(f'<rect x="{legend_x + 40 + i * (CELL + GAP)}" y="{height - 30}" width="{CELL}" height="{CELL}" rx="3" fill="{shade(i)}"/>' for i in range(5))
    total = cal["totalContributions"]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-label="{total:,} contributions in the last year">
<style>text{{font-family:{FONT}}} .t{{font-size:11px;fill:{c["muted"]}}} .h{{font-size:13px;fill:{c["fg"]}}}</style>
<rect x=".5" y=".5" width="{width - 1}" height="{height - 1}" rx="14" fill="{c["bg"]}" stroke="{c["line"]}"/>
<text class="h" x="{LEFT}" y="26"><tspan font-weight="700">{total:,}</tspan> contributions in the last year<tspan fill="{c["muted"]}">, most of them in private repositories</tspan></text>
{"".join(months)}
<text class="t" x="{LEFT - 8}" y="{TOP + 1 * (CELL + GAP) + 10}" text-anchor="end">Mon</text>
<text class="t" x="{LEFT - 8}" y="{TOP + 3 * (CELL + GAP) + 10}" text-anchor="end">Wed</text>
<text class="t" x="{LEFT - 8}" y="{TOP + 5 * (CELL + GAP) + 10}" text-anchor="end">Fri</text>
{"".join(cells)}
<text class="t" x="{legend_x}" y="{height - 20}">Less</text>{legend}<text class="t" x="{legend_x + 40 + 5 * (CELL + GAP) + 4}" y="{height - 20}">More</text>
</svg>
'''


def main() -> None:
    cal = fetch()
    OUT.mkdir(parents=True, exist_ok=True)
    for look in LOOKS:
        f = OUT / f"activity-{look}.svg"
        f.write_text(svg(cal, look), encoding="utf-8")
        print(f"{f.relative_to(ROOT)}: {f.stat().st_size // 1024} KB, {cal['totalContributions']:,} contributions")


if __name__ == "__main__":
    main()
