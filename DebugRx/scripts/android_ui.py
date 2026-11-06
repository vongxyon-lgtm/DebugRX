#!/usr/bin/env python3
"""Print a compact view of an Android UI dump (uiautomator XML).

Usage:
    adb shell rm -f /sdcard/ui.xml
    adb shell uiautomator dump /sdcard/ui.xml && adb pull /sdcard/ui.xml ui.xml
    python3 android_ui.py ui.xml            # every node with text or a clickable id
    python3 android_ui.py ui.xml --click    # clickable nodes only, with tap centre

Each line: bounds  centre  resource-id  | text-or-description  [*clickable]
Bounds and centres are in device pixels — tap these, not screenshot pixels.
"""
import re
import sys

NODE = re.compile(r"<node [^>]*>")


def attr(node, key):
    m = re.search(key + r'="([^"]*)"', node)
    return m.group(1) if m else ""


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    only_click = "--click" in sys.argv[2:]
    xml = open(sys.argv[1], encoding="utf-8").read()
    for node in NODE.findall(xml):
        text = attr(node, "text") or attr(node, "content-desc")
        rid = attr(node, "resource-id").split("/")[-1]
        clickable = attr(node, "clickable") == "true"
        if only_click and not clickable:
            continue
        if not (text or (clickable and rid) or only_click):
            continue
        b = re.findall(r"\d+", attr(node, "bounds"))
        centre = ""
        if len(b) == 4:
            x1, y1, x2, y2 = map(int, b)
            centre = f"({(x1 + x2) // 2},{(y1 + y2) // 2})"
        print(f"{attr(node, 'bounds'):<24} {centre:<12} {rid:<28} | {text[:60]} {'*' if clickable else ''}")


if __name__ == "__main__":
    main()
