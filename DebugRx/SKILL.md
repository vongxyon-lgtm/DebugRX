---
name: debugrx
description: Hands-on, black-box QA of a mobile app or mini app that is already running — a Telegram Mini App, WeChat mini program, iOS/Android app in a simulator or emulator, or a mobile web app — by actually operating it (tapping, typing, switching language, leaving mid-flow) and reporting bugs and visible security weaknesses with reproduction steps. Use this whenever the user asks to "find bugs", "debug", "test", "QA", "click through", "check for problems/vulnerabilities" in an app that is on their screen, in a simulator, or reachable by URL — even when they only say "the app on my desktop/phone" and never say the word "test", and even when source code is also available but they want problems found by using the app. Do not use it for pure static code review, unit-test writing, or server-side penetration testing.
---

# DebugRx — standard hands-on test flow for running apps

> 面向已发布或测试中的手机 App、小程序、Mini App 的实机/模拟器黑盒测试流程。大模型照此流程操作，就能有条理地逐页发现 bug 和可见的安全问题，并交出带复现步骤的报告。
> A standard flow for black-box testing of released or in-testing mobile apps and mini apps. Follow it and you will find bugs screen by screen, with reproduction steps, instead of wandering.

You are the tester, not the reviewer. Everything you report must have been *seen on screen*, reproduced, and written down with the steps that produce it. Source code, if present, is only for confirming a cause after the fact.

## Files in this skill and when to read them

| Read | When |
|---|---|
| `references/platforms/<platform>.md` | Right after Phase 0, once you know what kind of app it is. It tells you how to get control of that platform and its traps. |
| `references/checklist.md` | At the start of Phase 3. Concrete probes per category, with real examples. |
| `references/security-observations.md` | During Phase 3 when you see anything involving login, tokens, IDs, payments, uploads or sharing. Non-intrusive only. |
| `references/report-template.md` | Phase 6. |
| `references/case-studies/*.md` | Once, before your first real session, to see the flow applied end to end — then don't copy their findings. |

## The flow

```
0 Prepare   → what app, which platform, what is off-limits, how you'll drive it
1 Connect   → get control of the device/window; prove you see the app itself
2 Map       → one pass over every entry point; a page map; no deep testing
3 Explore   → per screen, the checklist categories; log candidates
4 Reproduce → each candidate from a clean start, twice; keep only what repeats
5 Restore   → undo what you changed; release every lock/control
6 Report    → bugs (steps) · minor · verified OK · side effects · not tested
```

**Start line:** you hold a screenshot of the app's own UI and can name its top-level navigation.
**Finish line:** the app is back in the state you found it (or every leftover is named), controls are released, the report is written in the user's language.

---

## Phase 0 — Prepare

Answer these before touching anything. Write them at the top of your scratch log.

1. **Which app, exactly?** "The app on my desktop" means *on screen* far more often than a file on the Desktop. Take a screenshot of the screen first. If you also find a source folder or archive, ask which one is the target — don't start reviewing files. (This misread cost a full review pass in the Babobuy case study.)
2. **Which platform?** Pick the driver guide:
   - Telegram Mini App in Telegram Desktop → `platforms/telegram-miniapp.md`
   - WeChat / Alipay / other mini program in its DevTools simulator → `platforms/wechat-miniprogram.md`
   - iOS app in the Simulator → `platforms/ios-simulator.md`
   - Android app in an emulator or a USB-connected device → `platforms/android.md`
   - H5 / PWA / mobile web → `platforms/mobile-web.md`
   - A real phone mirrored to the desktop → treat as the platform it mirrors, driven with computer-use.
3. **What is off-limits?** State it to the user and act on it: anything that creates data visible to other people (create room/order/post, invite, share, message), spends money, deletes an account, or needs a permission grant (camera, location, contacts). Local-only state (a single-device game, a language toggle) may be changed but must be restored or reported.
4. **Build or environment?** Ask whether this is production or a test build. On production, be even more conservative: no orders, no posts, no account changes.
5. **Scratch log.** One file. Columns: *step → what I saw → candidate?* You will take 50–150 screenshots; memory is not enough.

## Phase 1 — Connect

Follow the platform guide to obtain control. Whatever the platform, finish this phase with:

- A screenshot that shows the app's own UI (tab bar, brand, first screen) — not a chat, launcher, or DevTools chrome.
- The identifiers you need to act (window id, simulator UDID, device serial, tab id).
- Knowledge of the **system-level controls that can eject you**: the host's Back/Close button, the simulator's Home gesture, the browser's back. Zoom on them before pressing them. Pressing Close on a root screen ends the session and resets in-memory state.
- A known recovery route (how to reopen the app) — test it mentally now, not after you've lost the window.

## Phase 2 — Map (short, 10–15 minutes)

Visit every tab, menu item and obvious entry point **once**. For each write one line:

```
<name> | shows: … | links to: … | writes data: no / local / server
```

If the app has a language or theme setting, switch it once and switch straight back — you want to know *that* it exists and *where*, not test it yet.

The map is your coverage plan and, at the end, your "Not tested" list. Don't skip it to save time; it is what makes the rest systematic instead of random.

## Phase 3 — Explore

Work screen by screen, in map order. On every screen run the categories below (probes in `references/checklist.md`). They are ordered by how often they yield real bugs in practice:

1. **Navigation stack** — reach each page from *every* entry, press Back, check you land where you came from. Pages with two routes are the classic failure.
2. **Cross-screen consistency** — the same fact in two places (list vs. detail, card vs. stats page, badge vs. count). Read both, compare numbers and wording, recompute simple totals.
3. **Localisation** — switch language, revisit every screen: untranslated strings, strings stored in the creator's language, plurals of 1, clipped translations, date/weekday formats.
4. **Input validation** — empty, whitespace, very long, duplicate, special characters, boundary numbers — then follow the value downstream to where it becomes ambiguous or breaks layout.
5. **Data display & charts** — tap every bar/point; tooltips overlapping values, clipping, mixed time windows on one card, rankings of one.
6. **State & persistence** — leave mid-flow (Back, tab switch, kill and reopen); progress kept and signalled, or cleanly discarded; no leftovers in the next flow.
7. **Loading, empty, error** — cold start, empty data, airplane mode / network off, slow network; spinners that never end, NaN/undefined, raw error JSON.
8. **Permissions & device** — deny a permission, revoke it, rotate, background/foreground, incoming call interruption (simulator), low-memory kill.
9. **Security observations** (black-box, non-intrusive — see `references/security-observations.md`) — sensitive data visible in UI or URLs, predictable IDs, debug toggles, OTP/password fields without limits, deep links that skip auth, content from other users rendered unescaped.

Rules while exploring:

- **Read text by zooming**, not from a full screenshot. Plural errors, clipped labels and wrong dates live in small text.
- **Batch predictable sequences** but end every batch with a screenshot; most batch tools have no wait, so a screenshot is your wait.
- **One change per probe.** Chain five actions and you won't know which one broke it.
- **Log every side effect the moment you create it** — what, where, how to undo.
- **Stop and ask** before anything on the off-limits list, before granting a permission, and when a screen appears to show another user's data.

## Phase 4 — Reproduce

A candidate becomes a confirmed bug only after it repeats from a described starting point.

1. Return to a known state (root screen, or relaunch).
2. Perform the minimal steps.
3. Observe the same wrong outcome. **Twice** is the bar.

Write the steps *now*, with the labels exactly as the app shows them (in the app's language). What doesn't repeat goes under "observed once, not reproduced" — never silently dropped, never promoted.

Severity, decided now, not in the report: **blocks or misleads normal use** (wrong navigation, wrong data, data loss, auth bypass) > **visual defects** > **wording**. Security observations that expose other users' data or skip auth sit at the top regardless of how small they look.

## Phase 5 — Restore and release

- Settings back (language, theme, notifications).
- Test data deleted where the UI allows; otherwise name every leftover precisely.
- App on its root screen; permissions you granted during testing noted.
- Release every control: window locks, full-screen control, simulator attach, browser tabs you opened.

## Phase 6 — Report

Use `references/report-template.md`, in the user's language, app labels quoted in the app's language. Sections in this order, because the first is what the developer acts on and the last two are what keep you honest:

1. **Confirmed bugs & security findings** — numbered, worst first: where · steps · expected · actual · why it matters.
2. **Minor / possibly by design.**
3. **Verified OK** — what you checked that worked; tells the developer where *not* to look.
4. **Side effects of this session** — every change, undone or not, including your own mistakes.
5. **Not tested, and why** — needs another user / real device / would write shared data / payment / permission. Offer to test with consent.

Factual language only: "tooltip covers the value and is clipped at the right edge", not "the chart looks bad".

## Time budget (typical 5-tab app)

| Phase | Share |
|---|---|
| 0–1 Prepare, connect | 10 % |
| 2 Map | 10 % |
| 3 Explore | 50 % |
| 4 Reproduce | 15 % |
| 5–6 Restore, report | 15 % |

If the user gives you a fixed time, cut Phase 3 breadth (fewer screens, all categories) rather than depth (all screens, fewer categories): a half-tested screen produces unreproduced candidates, which are worth little.
