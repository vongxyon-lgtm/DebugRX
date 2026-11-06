---
name: debugrx
description: Hands-on, black-box QA of a mobile app or mini app that is already running — a Telegram Mini App, WeChat mini program, iOS/Android app in a simulator or emulator, an APK the user hands over to install, or a mobile web app — by actually operating it (tapping, typing, switching language, going offline, leaving mid-flow) and reporting bugs and visible security weaknesses with reproduction steps. Use this whenever the user asks to "find bugs", "debug", "test", "QA", "click through", "check for problems/vulnerabilities" in an app that is on their screen, in a simulator, in an APK/IPA file, or reachable by URL — even when they only say "the app on my desktop/phone" and never say the word "test", and even when source code is also available but they want problems found by using the app. Do not use it for pure static code review, unit-test writing, or server-side penetration testing.
---

# DebugRx — standard hands-on test flow for running apps

> 面向已发布或测试中的手机 App、小程序、Mini App 的实机/模拟器黑盒测试流程。大模型照此流程操作，就能有条理地逐页发现 bug 和可见的安全问题，并交出带复现步骤的报告。
> A standard flow for black-box testing of released or in-testing mobile apps and mini apps. Follow it and you will find bugs screen by screen, with reproduction steps, instead of wandering.

You are the tester, not the reviewer. Everything you report must have been *seen on screen*, reproduced from a clean state, and written down with the steps that produce it. Source code or package contents are only for answering a question the user asked, or for locating the cause of a bug you already saw.

**Logic first.** The bugs that cost users money, orders and trust are logic bugs: a dead entry, a number that disagrees with another screen, an action that silently does nothing, a gate that one route enforces and another skips, a screen that never recovers. Spend most of your time hunting those. Wording, language and brand slips are real but cheap to find — one sweep per screen, grouped in the report.

**Quality over quantity.** Ten reproduced bugs with evidence beat forty observations. A long report full of wording nits buries the one finding that matters, and a finding you later have to retract costs the user's trust in all the others.

**Show, don't just tell.** Every confirmed logic bug comes with a screen recording and a narrated, timestamped walkthrough. Every confirmed language or layout bug comes with an annotated screenshot and an explanation. See `references/evidence.md`.

## Read these at the start of every session

Not just the platform guide. Skipping the checklist and template is how a session turns into "open page, screenshot, back" with a padded report.

| Read | When |
|---|---|
| This file, in full | Before Phase 0, every session, even if you wrote it. |
| `references/platforms/<platform>.md` | Right after Phase 0. How to get control of that platform, and its traps. |
| `references/checklist.md` | Before Phase 2 — the map should already note which categories each screen needs. |
| `references/security-observations.md` | Before Phase 3 if the app has login, payments, invites, uploads or sharing. Non-intrusive only. |
| `references/evidence.md` | Before Phase 4. How to record logic bugs with narration and annotate screenshots; the scripts that do it. |
| `references/report-template.md` | Before Phase 3 (so you log in its shape) and again at Phase 6. |
| `scripts/` | `record.py` (record + step log), `annotate.py` (boxes, captions, redaction), `build_report.py` (report page with images and videos), `android_ui.py` (UI-tree reader). Paths in this skill are relative to the skill's own folder — call the scripts by their full path. |
| `references/case-studies/*.md` | Once, to see the flow applied — including the mistakes. Don't copy their findings. |

## The flow

```
0 Prepare   → what app, which platform, off-limits, account snapshot, user's own concerns
1 Connect   → get control; prove you see the app itself; know your coordinate scale
2 Map       → every entry point once; a page map with the checks each screen needs
3 Explore   → logic probes first (≈70 %), then one presentation sweep per screen
4 Reproduce → each candidate from a clean start, twice; rule out your own mistakes;
              record the logic ones, annotate the presentation ones
5 Restore   → undo what you changed; diff the account snapshot; release every control
6 Report    → one ranked report page with evidence: logic & security · presentation (grouped)
              · once · minor · OK · side effects · not tested
```

**Start line:** you hold a screenshot of the app's own UI and can name its top-level navigation.
**Finish line:** the app is back in the state you found it (or every leftover is named), controls are released, one report is written in the user's language and has passed the self-check in Phase 6.

---

## Operating discipline (applies to every phase)

Most wasted time and every false finding in past sessions came from sloppy driving, not from the app.

1. **One action, then verify.** After every tap, type or Back: wait for the screen to settle, then confirm where you are (screenshot, UI tree, or the platform's "current screen" query) before the next action. Never run a loop of taps or Backs without a check between them — a Back pressed during a transition leaves a page behind, and your next tap lands somewhere else.
2. **Know your coordinate scale.** Screenshots are often downscaled for viewing. Take tap coordinates from the UI tree (element bounds in device pixels) or convert explicitly. A tap "a bit off" opens the wrong thing and costs a reproduction cycle.
3. **Start every probe from a clean state.** Root screen, nothing stacked, no sheet open. If the platform can tell you the screen stack depth, check it.
4. **Read a page before you tap inside it.** Especially web pages and anything with buy, pay, submit, send, delete or share. A tap meant for a native button can land in a web page that just loaded under your finger. If it happens, screenshot immediately and report what, if anything, was triggered.
5. **Log as you go** in the scratch log: step → what I saw → candidate? → side effect created.
6. **The user's own concern is a probe, not a detour.** If the user says "we renamed X to Y" or "check payments", add it as an explicit category across every screen. Don't let it replace the flow.

## Phase 0 — Prepare

Answer these before touching anything. Write them at the top of your scratch log.

1. **Which app, exactly?** "The app on my desktop" means *on screen* far more often than a file on the Desktop. Screenshot the screen first. If it is an install package (APK/IPA, maybe inside an archive), extract it into its own empty folder and install it on an emulator/simulator — the test still happens in the running app.
2. **Which platform?** Pick the driver guide:
   - Telegram Mini App in Telegram Desktop → `platforms/telegram-miniapp.md`
   - WeChat / Alipay / other mini program in its DevTools simulator → `platforms/wechat-miniprogram.md`
   - iOS app in the Simulator → `platforms/ios-simulator.md`
   - Android app (emulator, USB device, or an APK to install) → `platforms/android.md`
   - H5 / PWA / mobile web → `platforms/mobile-web.md`
   - A real phone mirrored to the desktop → treat as the platform it mirrors, driven with computer-use.
3. **Environment gaps.** Will the emulator lack something the app needs (Google/Huawei services, camera, SIM)? Say so up front; findings that may come from the environment are labelled as such in the report.
4. **What is off-limits?** State it to the user and act on it: anything that creates data visible to other people (order, post, invite, share, message), spends or moves money, changes the account or profile, or needs a permission grant. Local-only state may be changed but must be restored or reported.
5. **Production or test build? Guest or logged in?** On production or a real account be even more conservative.
6. **Account snapshot (logged in only).** Before testing, record what you might disturb: cart lines and quantities, unread counts, balances, favourites, search history. You will diff against it in Phase 5.
7. **Scratch log.** One file. You will take 50–150 screenshots; memory is not enough.

## Phase 1 — Connect

Follow the platform guide. Finish this phase with:

- A screenshot that shows the app's own UI — not a chat, launcher, or DevTools chrome.
- The identifiers you need to act (window id, simulator UDID, device serial, package name, tab id).
- The **coordinate scale** between your screenshots and the device.
- The **system-level controls that can eject you** (host Back/Close, Home gesture, browser back) — zoom on them before pressing.
- A known recovery route (how to reopen the app, how to get back to the root screen).

## Phase 2 — Map (short, 10–15 minutes)

Visit every tab, menu item, icon and obvious entry point **once**. For each write one line:

```
<name> | entry points: … | responds? | shows numbers/money? | web page? | writes data: no / local / server
```

"Responds?" catches dead icons early: tap the icon body, not just its badge or label. "Shows numbers/money?" marks the screens that must get a cross-check in Phase 3. "Web page?" marks embedded pages that need the hybrid probes.

If the app has a language setting, switch it once and back — note where it lives. The map is your coverage plan and, at the end, your "Not tested" list.

## Phase 3 — Explore

Work screen by screen, in map order. Probes and real examples for every category are in `references/checklist.md`.

**A. Logic probes — the main work (about 70 % of Phase 3):**

1. **Navigation stack** — reach each page from *every* entry, press Back, check you land where you came from.
2. **Cross-screen consistency** — the same fact in two places (badge vs. list, list vs. detail, total vs. lines, balance vs. transactions, status vs. timestamps). Recompute.
3. **Action feedback & state change** — every primary action gives visible feedback *and* the state actually changes (count, list, badge) everywhere it is shown.
4. **Entry rules** — the same feature reached from two places obeys the same rules (login gate, permission, limits).
5. **Input → downstream** — empty, long, duplicate, boundary, special characters — then follow the value to lists, history, totals, results.
6. **State & persistence** — leave mid-flow, kill and reopen, rotate, switch account or language; nothing half-kept.
7. **Error & recovery** — network off *and back on*, slow network, empty data; the screen must explain itself and recover without a relaunch.
8. **Hybrid / embedded web pages** — login state carried in, one back control, no unannounced jump outside the app.
9. **Permission flows** — deny once, deny twice, revoke: the feature explains itself and offers a way back.
10. **Security observations** (non-intrusive — `references/security-observations.md`) — other people's data visible, auth that differs by route, unescaped content.

How to hunt logic bugs instead of browsing:

- **Write the invariants of the screen first.** "Badge = sum of cart quantities." "Order total = Σ lines." "Completed ⇒ completion time set." "Logged in ⇒ every page knows it." Then try to break each one.
- **Before / after every action.** Read the numbers that should change (badge, count, balance, list length) before the action, do it once, read them again on *every* screen that shows them.
- **Every transition, not just the happy path:** twice in a row, out of order, interrupted (Back, tab switch, network off), from the second entry, at the boundary (0, 1, minimum, maximum).
- **Same object, two doors.** Open the same item from list, search, history and notification; compare what each door shows and allows.
- **Undo paths.** Whatever you can add, can you remove? Whatever you can turn on, can you turn off? Is the removal reflected everywhere?

**B. Presentation sweep — once per screen, captured as annotated screenshots:**

11. **Localisation** — full language round-trip: untranslated or mixed-script text, clipped translations, untranslated images, plurals, date and currency formats.
12. **Branding & naming** — old names in text, images, loading animations, placeholders, prompts, share text, web pages, server messages.
13. **Layout & visuals** — overlap, clipping, invisible contrast, controls that look enabled but aren't.

Take the full-resolution screenshot the moment you see a presentation defect; it is cheap now and annoying to find again later.

Rules while exploring:

- **Depth before breadth.** A screen counts as tested only when at least one check *could have failed*: a recomputed total, a compared number, a second entry route, a downstream follow-up. Opening and closing a screen is mapping, not testing.
- **Read small text by zooming.** Plural errors, clipped labels, wrong dates and old brand names live there.
- **One change per probe.** Chain five actions and you won't know which one broke it.
- **Stop and ask** before anything off-limits, before granting a permission, and when a screen shows another user's data.

### Looking inside the package (optional, bounded)

Unpacking an APK/IPA or reading resources is allowed only to (a) answer a specific question the user asked — "where does the old brand name still appear?" — or (b) point the developer at the source of a bug you already reproduced on screen. Time-box it to about 10 % of the session, list static findings in their own clearly labelled group, and never let it replace running the app.

## Phase 4 — Reproduce

A candidate becomes a confirmed bug only after it repeats from a described starting point.

1. **Rule out yourself first.** Was the previous screen fully closed (stack clean)? Had the page finished loading? Did your tap land on the element you meant (check its bounds)? Was the environment (no network, missing services) the cause? If you find your own mistake, drop the candidate and note it only in the scratch log.
2. Return to a clean state (root screen, or relaunch).
3. Perform the minimal steps, one action at a time.
4. Observe the same wrong outcome. **Twice** is the bar; vary one thing (another product, another entry) when you can.
5. **Capture the evidence on the confirming run** (`references/evidence.md`): logic and security bugs → start `scripts/record.py`, log each step as you perform it, hold 2–3 s on the wrong state, stop; presentation bugs → full-resolution screenshot, then `scripts/annotate.py` with numbered boxes (and `--redact` for other people's data).

Write the steps *now*, with labels exactly as the app shows them. What doesn't repeat (and wasn't your mistake) goes under "observed once" — without a recording.

Severity, decided now: **security / other users' data** > **blocks or misleads normal use** (dead entry, wrong data, wrong navigation, lost state, no feedback that causes repeats) > **visual** > **wording**.

## Phase 5 — Restore and release

- Settings back (language, theme, rotation, network).
- Diff the account snapshot from Phase 0: every line back as it was, or the difference named.
- Test data deleted where the UI allows; otherwise name every leftover precisely, including what the UI gives no way to remove.
- App on its root screen; permissions granted or revoked during testing noted.
- Release every control: window locks, full-screen control, simulator attach, browser tabs; say whether emulators/tools you installed are still running.

## Phase 6 — Report

Use `references/report-template.md`, in the user's language, app labels quoted in the app's language. **One report per app.** If you test in rounds (guest, then logged in), merge and re-rank; don't append round two below round one. Write `report.md` with the evidence embedded, then build `report.html` with `scripts/build_report.py` and hand the user the page.

1. **Logic & security findings** — at most about 10, worst first. Each has where · steps · expected · actual · why it matters · **recording + narration**.
2. **Presentation findings** — grouped by kind (language, branding, layout), each group one finding with **annotated screenshots + explanation**; a table when the same defect appears in many places.
3. **Observed once, not reproduced.**
4. **Minor / possibly by design** — at most about 10 bullets; the rest stay in the scratch log.
5. **Verified OK** — what you checked that worked, especially the logic checks that passed (they show where *not* to look).
6. **Side effects of this session** — every change, undone or not, including your own mistakes and what the account diff showed.
7. **Not tested, and why** — with an offer.

**Self-check before sending** — if any answer is no, fix the report first:
- Is the most severe finding (security or blocking) the first item?
- Does every confirmed item have steps a developer can follow without you?
- Is anything in the report a candidate you later disproved? Remove it.
- Did same-kind items get merged instead of listed separately?
- Does every logic finding have a recording with narration, and every presentation finding an annotated screenshot? Are other people's personal data redacted?
- Do logic findings outnumber or outrank presentation ones? If the report is mostly wording, you spent Phase 3 on the wrong half.
- Could the user read the confirmed section in two minutes?

Factual language only: "tooltip covers the value and is clipped at the right edge", not "the chart looks bad".

## Time budget (typical 5-tab app)

| Phase | Share |
|---|---|
| 0–1 Prepare, connect (incl. environment setup) | 10 % |
| 2 Map | 10 % |
| 3 Explore | 50 % |
| 4 Reproduce | 15 % |
| 5–6 Restore, report | 15 % |

Environment setup (installing an emulator, SDKs) can eat a session; do it in the background while you read the checklist. If the user gives you a fixed time, cut breadth (fewer screens, all categories) rather than depth.
