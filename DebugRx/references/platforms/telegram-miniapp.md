# Driver guide: Telegram Mini App (Telegram Desktop, macOS)

How to get control of a Mini App running inside Telegram Desktop using the Claude desktop app's computer-use tools (`mcp__computer-use__*`). Other harnesses: same ideas — find the WebView window, prefer background actions, screenshot after every batch.

## Contents

1. Access and window setup
2. Background vs. full-screen tools
3. The Back / Close trap
4. Recovering a closed mini app
5. Reading the screen reliably
6. Batching
7. Cleanup

---

## 1. Access and window setup

1. `request_access(["Telegram"])`. The WebView is part of the Telegram process; no browser grant is needed.
2. `app_list_windows` → the mini app is its own phone-shaped window (≈ 400×800). The main chat window is large. Note both ids; the main one is for recovery only (§4).
3. Work on the mini-app window id. If a call reports the window is not on the current Space, `app_bring_to_current_space` first.
4. Finish Phase 1 with `app_screenshot` of the mini-app window showing the app's tab bar.

## 2. Background vs. full-screen tools

- `app_screenshot`, `app_click`, `app_type`, `app_key`, `app_scroll`, `app_zoom`, `app_ax_find`, `app_batch` act on one window without taking the screen. Default to these; the user keeps working.
- `computer_batch` and other full-screen tools take the screen and are **refused while you hold an `app_*` lock**: `app_release` first, `release_full_control` right after. In practice you need full-screen only when a background click in the *main* Telegram window does not register (observed for the chat's OPEN button).
- `app_ax_find` sees native Telegram controls but usually nothing inside the WebView. Use screenshots + coordinates for the app's own UI.

## 3. The Back / Close trap

Telegram draws one control at the top-left of the WebView (≈ (35,35) window coordinates):

- **Back** (arrow) while the app has a page pushed and the BackButton registered.
- **Close** (×) on the app's root screen.

Pressing it on the root closes the mini app and destroys the window. `app_zoom` the corner before pressing. For navigation tests prefer the app's own in-page back control if it has one, and use Telegram's button when you are specifically testing BackButton handling — which is exactly where the "Back lands on the wrong tab" class of bug shows.

## 4. Recovering a closed mini app

1. `app_bring_to_current_space` the main Telegram window.
2. `app_release` your lock.
3. Click the bot's **OPEN** button beside the chat (full-screen `computer_batch`, screenshot first, if the background click does not register), then `release_full_control`.
4. `app_list_windows` again — the mini app gets a **new window id**. Expect a blank loading screen for a few seconds and possibly an ad/consent popup; dismiss it with its own ×, not Telegram's.

Report this as a side effect: a relaunch resets in-memory state.

## 5. Reading the screen reliably

- Full-window screenshots for layout; `app_zoom` for any text you will quote (labels, counts, dates, plurals).
- When comparing two screens, zoom the same region on both and keep the zooms adjacent in your log.
- Chart tooltips vanish on the next click — screenshot inside the same batch as the tap.

## 6. Batching

`app_batch` runs a list of actions on one window:

```
[click tab] → [click item] → [screenshot]
```

- **No wait action.** End with a screenshot; if it shows a spinner, screenshot again in a new call.
- Stop the batch where the next coordinate depends on what you see.
- Never put the top-left Telegram control in a batch unless you zoomed it in the same state.

## 7. Cleanup

- `app_release` every locked window (mini app and main).
- `release_full_control` if any full-screen call was made.
- `list_granted_applications` to confirm nothing unexpected was granted.

## Platform-specific probes to add to the checklist

- Telegram BackButton from every route (see §3).
- `MainButton` state after Back: does a stale main button remain on the previous page?
- Theme: switch Telegram to dark mode — does the app follow `themeParams`?
- Viewport: resize the mini-app window / expand-collapse — does the layout recover?
- `initData` is never shown in the UI or in a share link (see `security-observations.md`).
