# Driver guide: H5 / PWA / mobile web app

Use the browser tools (`mcp__Claude_Browser__*` built-in browser, or `mcp__claude-in-chrome__*`), not computer-use. They are DOM-aware: `read_page`/`find` give you exact text and element refs, which is faster and more reliable than screenshots.

## 1. Connect

1. `navigate` to the URL (or `preview_start` for a local dev server). Ask the user before opening a production URL that needs their login; never type their password — ask them to sign in in the pane.
2. `resize_window preset: "mobile"` (375×812, mobile user agent, touch). Reload after switching so load-time device checks re-run.
3. `screenshot` to confirm the app's UI at phone width, then `read_page filter: "interactive"` to list the controls — that is your Phase 2 map in one call.

## 2. Act

- Prefer `find` + `ref` clicks over coordinates; a `ref` survives small layout shifts.
- `form_input` for fields; `computer key` for Enter/Escape.
- `get_page_text` to read a whole screen's text for consistency checks — it catches "1 days" instantly.
- `read_console_messages onlyErrors: true` after each screen; `read_network_requests` after each action for failed calls and for response bodies that the UI hides.

## 3. Traps

- Browser Back (`navigate "back"`) is the navigation probe; in-app back arrows are a second one. SPAs often break one of them.
- `localStorage`/cookies persist across your reloads; for the cold-start probe open a fresh tab or clear site data (ask first on production).
- Fixed-position bars and 100vh layouts behave differently with the mobile URL bar; test with `tablet` and a custom narrow size (320×568) too.
- Cookie/consent banners: pick the most private option; don't accept terms on the user's behalf.

## 4. Platform-specific probes

- Hard refresh on every route: a deep URL that 404s or redirects to home loses the user's place.
- Offline (DevTools offline, or disconnect): PWA shell vs. blank page.
- Pinch-zoom disabled? Text at 320 px width clipped?
- Tokens in the URL, query strings or `localStorage` (see `security-observations.md`); `read_network_requests` shows them in headers as REDACTED — the URL list does not.
- Session expiry: wait or clear the auth cookie — does the app recover gracefully or spin forever?

## 5. Release

Reset the viewport (`resize_window preset: "desktop"`), close tabs you opened, don't sign out an account the user signed in.

## Evidence

- **Logic bug → recording:** use the browser tool's GIF/recording feature if it has one (Claude in Chrome has a GIF recorder); otherwise record the browser window with `scripts/record.py --platform mac --rect …`. Log each step either way.
- **Presentation bug → screenshot** at the emulated device size, then `scripts/annotate.py`. For text bugs include the element's selector or text from the DOM so the developer can grep for it.
- Console errors and failed network requests that happen during the reproduction go under the video as part of the narration.
