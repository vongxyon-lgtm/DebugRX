#!/usr/bin/env python3
"""Turn a DebugRx Markdown report into one HTML page that shows the evidence.

- ![caption](evidence/V01-x.png)   -> image with its caption
- ![caption](evidence/B01-x.mp4)   -> playable video (.mp4/.mov/.webm/.m4v); if
  evidence/B01-x.steps.md exists (written by record.py), its timestamped steps
  are shown under the video as a timeline.

    uv run --with markdown python build_report.py report.md        # -> report.html
    uv run --with markdown python build_report.py report.md --out out.html

Evidence paths stay relative, so keep report.html next to the evidence folder
when you move or zip it.
"""
import argparse
import html
import os
import re
import sys

try:
    import markdown
except ImportError:
    sys.exit("markdown missing: run with  uv run --with markdown python build_report.py ...  or  pip install markdown")

VIDEO = (".mp4", ".mov", ".webm", ".m4v")

CSS = """
:root{--bg:#fff;--fg:#1d1d1f;--muted:#6e6e73;--line:#e5e5ea;--card:#f7f7f9;--accent:#d93025}
@media (prefers-color-scheme:dark){:root{--bg:#141416;--fg:#f2f2f4;--muted:#a1a1a6;--line:#2c2c30;--card:#1d1d20;--accent:#ff6b5e}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.65 -apple-system,BlinkMacSystemFont,"PingFang SC","Noto Sans CJK SC","Segoe UI",sans-serif}
main{max-width:860px;margin:0 auto;padding:32px 16px 80px}
h1{font-size:28px;line-height:1.25}h2{margin-top:44px;padding-top:12px;border-top:1px solid var(--line);font-size:22px}h3{font-size:18px;margin-top:28px}
table{border-collapse:collapse;width:100%;font-size:14px;display:block;overflow-x:auto}th,td{border:1px solid var(--line);padding:6px 10px;text-align:left;vertical-align:top}th{background:var(--card)}
code{background:var(--card);padding:1px 5px;border-radius:4px;font-size:.92em}
figure{margin:16px 0;padding:12px;background:var(--card);border:1px solid var(--line);border-radius:10px}
figure img,figure video{display:block;max-width:100%;max-height:640px;margin:0 auto;border-radius:6px}
figcaption{margin-top:8px;color:var(--muted);font-size:14px}
.timeline{margin:10px 0 0;padding:0;list-style:none;font-size:14px}.timeline li{padding:3px 0;border-top:1px dashed var(--line)}
.timeline b{display:inline-block;min-width:3.4em;color:var(--accent);font-variant-numeric:tabular-nums}
blockquote{margin:12px 0;padding:4px 14px;border-left:3px solid var(--accent);color:var(--muted)}
"""


def steps_for(base_dir, src):
    p = os.path.join(base_dir, os.path.splitext(src)[0] + ".steps.md")
    if not os.path.exists(p):
        return ""
    items = []
    for line in open(p, encoding="utf-8"):
        m = re.match(r"-\s*(\d\d:\d\d)\s*—\s*(.*)", line.strip())
        if m:
            items.append("<li><b>%s</b> %s</li>" % (m.group(1), html.escape(m.group(2))))
    return '<ol class="timeline">%s</ol>' % "".join(items) if items else ""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("report")
    ap.add_argument("--out")
    ap.add_argument("--title", default="")
    a = ap.parse_args()
    base = os.path.dirname(os.path.abspath(a.report))
    src = open(a.report, encoding="utf-8").read()
    title = a.title or (re.search(r"^#\s+(.+)$", src, re.M) or [None, "DebugRx report"])[1]
    body = markdown.markdown(src, extensions=["tables", "fenced_code", "sane_lists"])

    def media(m):
        tag = m.group(0)
        s = re.search(r'src="([^"]+)"', tag).group(1)
        alt = html.unescape((re.search(r'alt="([^"]*)"', tag) or [None, ""])[1])
        cap = "<figcaption>%s</figcaption>" % html.escape(alt) if alt else ""
        if s.lower().endswith(VIDEO):
            return '<figure><video controls preload="metadata" src="%s"></video>%s%s</figure>' % (s, cap, steps_for(base, s))
        return '<figure><a href="%s"><img src="%s" alt="%s"></a>%s</figure>' % (s, s, html.escape(alt), cap)

    body = re.sub(r"<img [^>]*>", media, body)
    body = re.sub(r"<p>\s*(<figure>.*?</figure>)\s*</p>", r"\1", body, flags=re.S)
    out = a.out or os.path.splitext(a.report)[0] + ".html"
    with open(out, "w", encoding="utf-8") as f:
        f.write('<!doctype html><html lang="zh"><head><meta charset="utf-8">'
                '<meta name="viewport" content="width=device-width,initial-scale=1">'
                "<title>%s</title><style>%s</style></head><body><main>%s</main></body></html>"
                % (html.escape(title), CSS, body))
    missing = [s for s in re.findall(r'src="([^"]+)"', body)
               if not s.startswith(("http:", "https:", "data:")) and not os.path.exists(os.path.join(base, s))]
    print("saved", out)
    for s in missing:
        print("WARNING: missing evidence file", s)


if __name__ == "__main__":
    main()
