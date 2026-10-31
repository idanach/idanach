"""A preview of a draft README as it would sit on the GitHub profile page, for choosing between drafts.

    python -X utf8 tools/preview.py drafts/a          # writes drafts/a/preview.html

The README goes through GitHub's own markdown API (gh api markdown, the converter the profile page uses), and the page
around it copies the profile page's layout and GitHub's dark theme: the avatar, name and links on the left with the
proposed profile details, the README and the pinned repositories on the right. Pictures load from the draft folder.
"""
from __future__ import annotations

import html
import json
import subprocess
import sys
from pathlib import Path

DRAFT = Path(sys.argv[1]).resolve()
CSS = "https://cdnjs.cloudflare.com/ajax/libs/github-markdown-css/5.5.1/github-markdown-dark.min.css"
AVATAR = "https://avatars.githubusercontent.com/u/142310044?v=4"
# the proposed profile details (the left column)
PROFILE = {
    "name": "Idan Achrak",
    "login": "idanach",
    "bio": "Senior full-stack developer & DevOps. I build whole systems, from the server to the last pixel.",
    "location": "Israel",
    "site": "idanach.com",
    "linkedin": "in/idanach",
}
PINNED = [
    ("Wicogen-windows-icon-generator", "Easily customize your folder icons on windows", "Python", "#3572A5"),
    ("nginx-server-deployment", "Automation-manager scripts for fast web apps deployment.", "Batchfile", "#C1F12E"),
]


def render(md: str) -> str:
    out = subprocess.run(["gh", "api", "-X", "POST", "markdown", "--input", "-"], input=json.dumps(
        {"text": md, "mode": "gfm", "context": "idanach/idanach"}), capture_output=True, text=True, encoding="utf-8",
        check=True)
    return out.stdout


def main() -> None:
    body = render((DRAFT / "README.md").read_text(encoding="utf-8"))
    p = PROFILE
    pins = "".join(
        f'<div class="pin"><div class="pn"><span class="ri"></span>{html.escape(n)}<span class="pub">Public</span></div>'
        f'<p>{html.escape(d)}</p><div class="pl"><span class="dot" style="background:{c}"></span>{html.escape(lang)}</div></div>'
        for n, d, lang, c in PINNED)
    page = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Preview</title>
<link rel="stylesheet" href="{CSS}">
<style>
body {{ margin: 0; background: #0d1117; color: #e6edf3; font: 14px/1.5 -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", Helvetica, Arial, sans-serif; }}
.top {{ height: 64px; background: #010409; border-bottom: 1px solid #30363d; }}
.wrap {{ max-width: 1280px; margin: 0 auto; padding: 32px; display: flex; gap: 24px; }}
.side {{ width: 296px; flex: none; }}
.side img {{ width: 296px; height: 296px; border-radius: 50%; border: 1px solid #30363d; display: block; }}
.side h1 {{ margin: 16px 0 0; font-size: 24px; line-height: 1.25; font-weight: 600; }}
.side .lg {{ font-size: 20px; font-weight: 300; color: #8b949e; }}
.side .bio {{ margin: 16px 0; font-size: 16px; }}
.side .btn {{ display: block; text-align: center; padding: 5px 16px; border: 1px solid #30363d; border-radius: 6px; background: #21262d; font-weight: 500; margin-bottom: 16px; }}
.side ul {{ list-style: none; padding: 0; margin: 0; color: #e6edf3; }}
.side li {{ margin: 4px 0; }} .side li a {{ color: #e6edf3; text-decoration: none; }}
.side li span {{ color: #8b949e; display: inline-block; width: 22px; }}
.main {{ flex: 1; min-width: 0; }}
.tabs {{ border-bottom: 1px solid #30363d; margin: -8px 0 24px; padding-bottom: 8px; color: #e6edf3; }}
.tabs b {{ border-bottom: 2px solid #f78166; padding-bottom: 9px; }}
.readme {{ border: 1px solid #30363d; border-radius: 6px; padding: 24px; }}
.readme .hd {{ font-size: 12px; color: #8b949e; margin-bottom: 16px; font-family: ui-monospace, SFMono-Regular, Consolas, monospace; }}
.markdown-body {{ background: transparent; }}
h2.pinned {{ font-size: 16px; font-weight: 400; margin: 24px 0 8px; }}
.pins {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
.pin {{ border: 1px solid #30363d; border-radius: 6px; padding: 16px; }}
.pin .pn {{ color: #4493f8; font-weight: 600; }} .pin .pub {{ margin-left: 8px; border: 1px solid #30363d; border-radius: 2em; padding: 0 7px; font-size: 12px; color: #8b949e; font-weight: 500; }}
.pin p {{ color: #8b949e; font-size: 12px; margin: 8px 0 16px; }} .pin .pl {{ color: #8b949e; font-size: 12px; }}
.dot {{ display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin-right: 4px; vertical-align: -1px; }}
</style></head><body><div class="top"></div>
<div class="wrap"><aside class="side"><img src="{AVATAR}" alt="">
<h1>{p["name"]}<br><span class="lg">{p["login"]}</span></h1>
<div class="bio">{html.escape(p["bio"])}</div><div class="btn">Follow</div>
<ul><li><span>⌖</span>{p["location"]}</li><li><span>🔗</span><a href="#">{p["site"]}</a></li><li><span>in</span><a href="#">{p["linkedin"]}</a></li></ul></aside>
<main class="main"><div class="tabs"><b>Overview</b> &nbsp; Repositories &nbsp; Projects &nbsp; Packages &nbsp; Stars</div>
<div class="readme"><div class="hd">idanach / README.md</div><article class="markdown-body">{body}</article></div>
<h2 class="pinned">Pinned</h2><div class="pins">{pins}</div></main></div></body></html>'''
    out = DRAFT / "preview.html"
    out.write_text(page, encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
