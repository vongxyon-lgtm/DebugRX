# Evidence: screenshots for what looks wrong, recordings for what behaves wrong

Every confirmed finding ships with evidence the developer can see without you. The kind of evidence follows the kind of bug:

| Finding | Evidence | Under it in the report |
|---|---|---|
| **Logic** — wrong navigation, wrong number, dead entry, silent action, lost state, gate that differs by route, no recovery after error | **Screen recording** of the minimal reproduction, from a clean start | **Narration**: timestamped steps, the moment of EXPECTED vs ACTUAL, and why it matters |
| **Presentation** — wording, language, mixed script, old brand name, clipped or overlapping layout, untranslated image | **Annotated screenshot**: numbered red boxes, cropped to the area, one-line caption | **Explanation**: what each number shows and what it should say |
| **Security** — other people's data visible, auth gap | Screenshot or recording as above, **with personal data redacted** | What is exposed, to whom, and the suggested fix (mask, gate) |

Name files by finding: `B01-…` logic (bug), `V01-…` presentation (visual/wording), `S01-…` security. Keep them in `evidence/` next to the report.

## Recording a logic bug

Record the **second** reproduction (Phase 4), not the first exploration — you already know the minimal steps, so the clip is short and clean.

```bash
python3 scripts/record.py start --platform android --name B03-home-search-login-gate --out evidence
python3 scripts/record.py step "Guest on Home; tap the search box"            --out evidence
#   …perform the action, wait for the screen to settle…
python3 scripts/record.py step "EXPECTED: search page | ACTUAL: login page"   --out evidence
python3 scripts/record.py step "Back; Category › T恤 › type 'hoodie' › Enter" --out evidence
python3 scripts/record.py step "Results shown — the same guest can search here" --out evidence
python3 scripts/record.py stop --out evidence
```

`record.py` writes `B03-….mp4` (or `.mov` on mac) and `B03-….steps.md` with real timestamps.

Rules:
- **Log the step, then act.** The timestamp should point at the moment the viewer needs to look.
- **Pause 2–3 s on the wrong state** so it is visible in the clip.
- **Show the contrast in the same clip** when there is one (dead icon vs. working badge; gated route vs. open route; badge 3 vs. cart 13).
- **Keep clips under 60 s.** One finding per clip. Android `screenrecord` stops at 180 s regardless.
- **Touches visible.** On Android `record.py` turns on the "pointer location" overlay (crosshair plus X/Y readout) for the clip and restores it — "show touches" does not draw for adb-injected taps. On iOS Simulator and desktop hosts, say in the narration where you tapped.
- **No credentials or other people's data on screen** while recording. If a screen shows them, record a different screen or redact a key frame instead.

Platform recorders (what `record.py` runs):

| Platform | Recorder | Notes |
|---|---|---|
| Android emulator / device | `adb shell screenrecord --bit-rate 4000000 --time-limit 180 /sdcard/x.mp4`, then `adb pull` | Stop with `adb shell pkill -INT screenrecord` so the file is finalised |
| iOS Simulator | `xcrun simctl io booted recordVideo --codec=h264 x.mp4` | Stop with SIGINT (Ctrl-C) |
| Telegram Desktop, WeChat DevTools, any desktop window (macOS) | `screencapture -x -k -V 180 [-R x,y,w,h] x.mov` | The app running the command needs Screen Recording permission; `-k` shows clicks; `-R` limits to the app window |
| Mobile web in a browser | the browser tool's GIF/recording feature if it has one; otherwise the mac recorder on the window | — |

If no recorder works, fall back to a **numbered screenshot sequence** (`B03-1.png`, `B03-2.png`, …) and narrate each frame. Say in the report that it is a sequence, not a video.

## Writing the narration

Under each recording, in the user's language:

```
![录屏：游客点首页搜索框被要求登录，同一游客从分类却能搜索](evidence/B03-home-search-login-gate.mp4)

**解说**
- 0:00 游客身份在首页，点顶部搜索框。
- 0:03 **实际**跳到登录页。**预期**进入搜索页，因为下一段证明游客本来就能搜索。
- 0:07 返回，进入 分类 › T恤，在列表页搜索框输入 "hoodie" 回车。
- 0:12 出现搜索结果。
- **影响**：两个入口规则不一致；如果游客可以搜，首页这道拦截会白白挡住新用户。
```

Start from the `.steps.md` file, rewrite each line as a sentence a developer understands, and mark **预期 / Expected** and **实际 / Actual** in bold.

## Annotating a presentation bug

Take the screenshot at full device resolution (adb `screencap`, `simctl io screenshot`, or a window capture), read the element's bounds from the UI tree, then:

```bash
uv run --with pillow python scripts/annotate.py raw.png evidence/V02-traditional-in-simplified.png \
    --box 740,1873,1048,1941 --crop 260 \
    --caption "1 简体界面里出现繁体“中國運費：點擊查詢”"
```

- One image per defect type per screen; several boxes on one image are fine — number them and explain each number.
- `--crop` keeps the reader's eye on the problem; leave enough margin to show where on the screen it is.
- For a language problem, show **both languages side by side** when the bug is a difference between them (two images in a row).
- `--redact x1,y1,x2,y2` blacks out phone numbers, names and addresses that belong to other people.

Explanation under the image:

```
![1 运费一栏是繁体](evidence/V02-traditional-in-simplified.png)

**说明**：① 运费一栏写作"中國運費：點擊查詢"，简体应为"中国运费：点击查询"。每个商品详情页都一样（看了 4 个）。
```

## Building the report page

Write `report.md` with the images and videos embedded as Markdown images, then:

```bash
uv run --with markdown python scripts/build_report.py report.md
```

This produces `report.html` next to it: images inline, videos as players, and each video's `.steps.md` timeline shown under it. Hand the user the HTML (and the folder, if they will forward it) — not a list of file paths.
