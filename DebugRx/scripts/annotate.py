#!/usr/bin/env python3
"""Mark a visual or wording defect on a screenshot.

Draws a numbered red box around each problem area, optionally crops to the
boxes (plus a margin) and adds a one-line caption bar under the image. The
explanation itself goes in the report next to the image; keep the caption short.

    uv run --with pillow python annotate.py shot.png out.png \
        --box 0,1660,1080,1790 --box 600,1880,1040,1930 \
        --caption "1 繁体“中國運費”出现在简体界面  2 重量 3.0Kg 偏高" --crop 120

Use --redact for other people's personal data (phone numbers, names,
addresses) before the image goes into a report.

Boxes are x1,y1,x2,y2 in the screenshot's own pixels (device pixels for a full
adb/simctl capture — the same numbers as UI-tree bounds). Needs Pillow.
"""
import argparse
import os
import sys

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit("Pillow missing: run with  uv run --with pillow python annotate.py ...  or  pip install pillow")

FONTS = [
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc",
    "C:/Windows/Fonts/msyh.ttc",
]


def font(size):
    for f in FONTS:
        if os.path.exists(f):
            try:
                return ImageFont.truetype(f, size)
            except OSError:
                pass
    return ImageFont.load_default()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--box", action="append", default=[], help="x1,y1,x2,y2 (repeatable)")
    ap.add_argument("--redact", action="append", default=[],
                    help="x1,y1,x2,y2 to black out (phone numbers, names, addresses); applied before boxes")
    ap.add_argument("--caption", default="")
    ap.add_argument("--crop", type=int, default=-1, help="crop to boxes with this margin in px; omit to keep full image")
    ap.add_argument("--max", type=int, default=1400, help="longest side of the output")
    a = ap.parse_args()

    im = Image.open(a.src).convert("RGB")
    w, h = im.size
    boxes = [tuple(int(v) for v in b.split(",")) for b in a.box]
    thick = max(4, w // 180)
    d = ImageDraw.Draw(im)
    for r in a.redact:
        x1, y1, x2, y2 = (int(v) for v in r.split(","))
        d.rectangle([x1, y1, x2, y2], fill=(40, 40, 40))
    badge_f = font(max(28, w // 28))
    for i, (x1, y1, x2, y2) in enumerate(boxes, 1):
        d.rectangle([x1, y1, x2, y2], outline=(230, 30, 30), width=thick)
        r = max(22, w // 40)
        cx, cy = max(r, x1), max(r, y1)
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(230, 30, 30))
        d.text((cx, cy), str(i), fill="white", font=badge_f, anchor="mm")

    if a.crop >= 0 and boxes:
        x1 = max(0, min(b[0] for b in boxes) - a.crop)
        y1 = max(0, min(b[1] for b in boxes) - a.crop)
        x2 = min(w, max(b[2] for b in boxes) + a.crop)
        y2 = min(h, max(b[3] for b in boxes) + a.crop)
        im = im.crop((x1, y1, x2, y2))

    if max(im.size) > a.max:
        s = a.max / max(im.size)
        im = im.resize((int(im.width * s), int(im.height * s)))

    if a.caption:
        cf = font(max(22, im.width // 30))
        pad = 14
        lines, line = [], ""
        for ch in a.caption:  # character wrap works for CJK and Latin alike
            if cf.getlength(line + ch) > im.width - 2 * pad:
                lines.append(line)
                line = ch
            else:
                line += ch
        lines.append(line)
        lh = int(cf.size * 1.4)
        out = Image.new("RGB", (im.width, im.height + lh * len(lines) + 2 * pad), "white")
        out.paste(im, (0, 0))
        dd = ImageDraw.Draw(out)
        for i, l in enumerate(lines):
            dd.text((pad, im.height + pad + i * lh), l, fill=(20, 20, 20), font=cf)
        im = out

    im.save(a.dst)
    print("saved", a.dst, im.size)


if __name__ == "__main__":
    main()
