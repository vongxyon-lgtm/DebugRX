# Driver guide: WeChat / Alipay mini program (DevTools simulator)

Mini programs run inside the platform's DevTools (微信开发者工具, 支付宝小程序开发者工具) on the desktop. Drive the simulator pane with computer-use; use the DevTools panels for network and console evidence.

## 1. Connect

1. `request_access` for the DevTools app (e.g. "wechatwebdevtools"). It is a native app → full tier.
2. `app_list_windows`; the simulator is a pane inside the main DevTools window, not a separate window. Screenshot the whole window, then `app_zoom` on the phone frame for everything afterwards.
3. Note the DevTools toolbar controls that can eject you: **编译** (recompile — resets state), **清缓存** (clear cache/storage), and the device/model dropdown. Don't press them unless that is the probe.

## 2. Act

Clicks and typing go through `app_click` / `app_type` on the simulator pane. The pane's top-left back arrow is the mini program's own navigation bar (not the host's), so it is safe to use for navigation probes. For the **host-level** controls (the capsule ··· menu and ⊙ close at top-right), zoom first — ⊙ closes the mini program.

Evidence panels, read with screenshots/zoom:

- **Console** — JS errors on each screen; `wx.request` failures.
- **Network** — request/response of the action you just took: status codes, payload shape, error JSON that the UI swallowed.
- **Storage** — what is persisted locally (tokens, user data: see `security-observations.md`).

## 3. Traps

- **编译** recompiles and relaunches; everything in memory is gone. Use it deliberately for the cold-start probe, and log it as a side effect.
- The simulator's "真机预览" (preview on real device) needs the user's phone and WeChat account — "Not tested" unless they do it.
- Payments (`wx.requestPayment`) and sharing to chats need a real phone; test the *prelude* (button, loading state, cancel path) in the simulator only.
- Scanning (`wx.scanCode`), shake, location: the simulator mocks some of these (location can be set in the toolbar); say whether you used a mock.

## 4. Platform-specific probes

- Navigation-bar Back vs. `wx.navigateBack` from every route; page stack limit (10 pages) — push deep and check nothing is lost.
- Pull-to-refresh and `onReachBottom` pagination: duplicates, end-of-list state.
- `onShow` after returning from another page: data refreshed or stale?
- Subpackage/lazy-loaded pages: first-open delay and error when offline.
- `setStorage` contents (Storage panel): any token or PII that should not be there.
- Switch the simulator device model (small/large screen) and the system font size: clipping.

## 5. Release

`app_release` the DevTools window; leave the simulator on the home page.

## Evidence

- **Logic bug → recording** of the DevTools simulator panel with the mac recorder: `python3 scripts/record.py start --platform mac --rect X,Y,W,H --name B01-… --out evidence` (rectangle = the phone frame only, not the whole IDE), log steps, act, stop. Needs Screen Recording permission.
- **Presentation bug → screenshot** of the simulator panel, then `scripts/annotate.py`. For text bugs also copy the WXML node from the inspector into the report.
