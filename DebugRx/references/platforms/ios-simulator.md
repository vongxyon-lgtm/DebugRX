# Driver guide: iOS app in the Simulator

Use the iOS Simulator tool when the session has it (`mcp__Claude_Code_iOS_Simulator__control` in the Claude desktop app); otherwise `xcrun simctl` from Bash plus computer-use on the Simulator window. Simulators only — a physical iPhone cannot be driven this way.

## 1. Connect

1. If the user wants to watch, `attach` first (cheap; errors harmlessly if nothing is booted).
2. Build with the project's own tooling or the server's `build` tool, then `launch` with the `.app` path. The launch result reports the device's point dimensions — coordinates below are in points, origin top-left.
3. `screenshot` to confirm the app's first screen. If a system dialog (notifications, tracking) is up, note it — that is a permission-flow probe (checklist §9), not an obstacle.

Fallback without the tool:

```bash
xcrun simctl list devices booted
xcrun simctl io booted screenshot /path/shot.png
xcrun simctl openurl booted "scheme://deep/link"
xcrun simctl privacy booted revoke camera <bundle-id>
```

Tapping without the tool means computer-use on the Simulator window (grant "Simulator"); the window scale differs from points, so measure from a screenshot of that window.

## 2. Traps

- A `swipe`/`touch_path` starting within 4 pt of a screen edge is an **OS edge gesture** (left = back, bottom = home/app switcher, top = notifications, right = Control Center). Start further in to scroll content near the bezel.
- `press_key` and `text` hide the on-screen keyboard; take a screenshot after typing if you need to see the field.
- `rotate` changes the coordinate frame — screenshot before tapping again.
- Simulator has no camera, no SMS, no real push: those go to "Not tested" with that reason.

## 3. Platform-specific probes

- Deny each permission at the system prompt, then try the feature; revoke with `simctl privacy` and retry.
- Background → foreground (`button HOME`, relaunch via the app switcher): does the screen restore, does a timer or OTP countdown survive?
- `set_appearance dark`: unreadable text, hard-coded white backgrounds.
- Dynamic Type: Settings › Accessibility › Larger Text — clipped labels.
- Deep links via `open_url`: do they skip login or land on a page the user can't leave?
- Low network: Settings › Developer › Network Link Conditioner.

## 4. Release

`detach` when done; leave the simulator booted unless the user asks otherwise.

## Evidence

- **Logic bug → recording:** `python3 scripts/record.py start --platform ios --name B01-… --out evidence` (uses `xcrun simctl io booted recordVideo`; add `--udid` if several simulators are booted), log each step, act, `record.py stop`.
- **Presentation bug → screenshot:** `xcrun simctl io booted screenshot raw.png` (device pixels — points × scale factor), then `scripts/annotate.py`.
- Taps don't show in simulator recordings; name each tap position in the narration.
