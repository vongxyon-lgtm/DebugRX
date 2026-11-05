# Case study: Babobuy — a drinking-game Telegram Mini App

One real session, start to finish, mapped onto the six phases of SKILL.md. The team calls the product **Babobuy**; the in-app brand read "WineTime / Hellowine". Telegram Desktop on macOS, 2026-11-05, Chinese UI with an English option, driven with the Claude desktop app's computer-use tools. About 150 screenshots over roughly two hours.

Read it once to see how the phases feel in practice, including the two mistakes. Then don't look for these bugs in your app — look for these *patterns*.

## Contents

1. Phase 0 — Prepare (and the wrong start)
2. Phase 1 — Connect
3. Phase 2 — Map
4. Phase 3 — Explore, screen by screen
5. Phase 4 — Reproduce
6. Phase 5 — Restore and release
7. Phase 6 — The report that was handed back
8. What the session taught (generalised)

---

## 1. Phase 0 — Prepare (and the wrong start)

User: *"There's a Telegram mini app on my desktop, help me find the bugs."*

What happened first: the Desktop folder was empty, a `menu-src.zip` sat in Downloads, so it was unpacked and a code-review agent started on it. It was an unrelated restaurant-ordering project. The user clarified: *"I mean it's already open on the screen — control the computer and actually operate it."* The agent was stopped and the session restarted on the right footing.

**Generalised rule (now SKILL.md Phase 0 §1):** "on my desktop/phone" means on screen. Screenshot first; if a source folder and a running app both exist, ask which.

Then:
- `request_access(["Telegram"])` — only Telegram; the WebView lives inside it.
- A scratch log file with *step → saw → candidate?*
- Scope stated to the user: no room creation, no invites, nothing that writes server data others can see. Single-device games and the language setting may be touched but will be restored or reported.
- Build: production (the real bot), so the conservative setting applied.

## 2. Phase 1 — Connect

- `app_list_windows` → main Telegram window `1735` (large) and a phone-shaped window `4365` ≈ 400×800.
- `app_screenshot(4365)`: brand header, bottom tabs **首页 · 游戏 · 开局(+) · 酒友 · 我的**. This is the app. Start line reached.
- Zoomed the top-left control: **×** (Close) on Home. Noted that on pushed pages it becomes an arrow.
- Recovery route known: main window → bot chat → **OPEN** button.

## 3. Phase 2 — Map

| Entry | Shows | Links to | Writes data |
|---|---|---|---|
| 首页 Home | weekly card (本周 76), recent tables, 历史记录 link | 我的战绩 stats page | no |
| 游戏 Games | 15 single-device party games, "Continue" badges | detail → player setup → play | local game state |
| 开局 + | create-table form: name placeholder, exchange-rate stepper | server room | **yes — off-limits** |
| 酒友 Friends | friend list with counts | friend detail | no |
| 我的 Me | stats card, 近14天 chart, 本月/今年 pages, language setting | 我的战绩 | language |

Language switch located under 我的. Switched to English once and straight back to confirm the mechanism. Map done in ~12 minutes.

## 4. Phase 3 — Explore, screen by screen

### 首页 Home

- **Navigation (category 1).** 首页 → 历史记录 → Telegram Back. Landed on the **我的** tab, not Home; a second Back reached Home. Candidate **#1**.
- **Mistake #2.** On Home the top-left control was already ×; it was pressed once more by reflex and the whole mini app closed. Recovery: `app_bring_to_current_space(1735)` → `app_release` → background click on OPEN did not register → `computer_batch` full-screen click at (275,268) → `release_full_control` → `app_list_windows` showed a **new** window id. Cold start: blank ~4 s, then an ad popup dismissed with its own ×. Logged as a side effect (relaunch) and as a loading-state observation (category 7).
- **Consistency (2).** The weekly card shows "本周 76" next to "日均 5.4", but 5.4 is the 14-day average. Minor.

### 我的 Me

- **Charts (5).** Tapped every bar of 近14天. On the 周三 bar the tooltip "11月4日 周三" sat on top of the "76" value and ran into the "喝了 1 天 · 日均 5.4" line, clipped at the right edge. Candidate **#2**. Other bars rendered cleanly — the overlap depends on the bar's height and position, which is why *every* bar is tapped.
- **Consistency (2).** 本月 and 今年 pages: recomputed table count, total 壶, average per table and the "most often with" friend from the six listed tables — all matched. Drinking calendar: weekday columns matched a real calendar. A one-person table with 0 壶 showed "第 1 名" — minor.

### Language round-trip (3)

Switched to English and revisited all five tabs:
- 我的: "**1 drinking days**". Candidate **#3**.
- 首页 recent tables: "**AH.YEUNG的局**" unchanged, while the create-table placeholder now read "AH.YEUNG's table" → the table name is composed and stored at creation time. Candidate **#4**.
- Everything else translated. Switched back to 中文.

### 游戏 Games → Drinking Wheel

- **Consistency (2).** Games list: "2+ players". Detail page: "2–20 players". Candidate **#6**.
- **Input validation (4), player setup.** Whitespace-only name → rejected ✔. 30-char name → silently truncated to 14 ("ThisIsAVeryVe") ✔ but noted for layout. A second "Player 2" → **accepted**. Played one round: the turn prompt and the penalty toast both say "Player 2" — nobody can tell which. Candidate **#5** (the downstream ambiguity, not the duplicate itself).
- **State (6).** Left the game at Round 2 with Telegram Back. Games list shows **Continue** on Drinking Wheel ✔; reopening resumed at Round 2 ✔. Logged as a side effect: a saved game with players AH.YEUNG / Player 2 / Player 2 / ThisIsAVeryVe.

### 开局 Create table

- Opened the form only. **Stepper (4):** exchange rate steps by 0.5, refuses to go below 0.5 ✔. Did **not** submit (off-limits).

### 酒友 Friends

- Friend counts matched list lengths ✔; detail pages consistent ✔.

### Security observations (9)

- Share/invite links were not opened (off-limits), so `initData`-in-URL could not be checked → "Not tested".
- No tokens or phone numbers visible in the UI. No debug toggles found in 我的.

## 5. Phase 4 — Reproduce

| # | How it was reproduced |
|---|---|
| 1 | Twice, from a clean Home tab each time, same steps, same wrong landing tab |
| 2 | Switched tabs away and back, tapped the same bar — same overlap |
| 3, 4, 6 | Static text; re-read after a second language round-trip |
| 5 | Started a second round; the ambiguity recurred |

Severity assigned: #1 (misleads navigation) > #2 (visual, data hidden) > #5 (ambiguous play) > #6, #4, #3 (wording/consistency). Nothing security-relevant confirmed.

## 6. Phase 5 — Restore and release

- Language back to 中文 ✔.
- The Drinking Wheel test game could not be deleted from the UI → named in the report.
- App left on 首页. `app_release(4365)`, `app_release(1735)`; full-screen control had already been released after the recovery click.

## 7. Phase 6 — The report that was handed back (abridged)

> **Confirmed bugs** — 1. Back from 历史记录 lands on 我的 instead of 首页 (×2). 2. 近14天 tooltip overlaps the value and is clipped. 3. "1 drinking days". 4. Table names not localised ("AH.YEUNG的局" in English UI). 5. Duplicate player names accepted; turn/penalty ambiguous. 6. "2+ players" vs "2–20 players".
> **Minor** — weekly total beside a 14-day average; "第 1 名" for a one-person table.
> **Verified OK** — 本月/今年 totals and averages, calendar weekdays, friend counts, stepper limits, game progress persistence with Continue badge, sheets close on Back.
> **Side effects** — app closed by mistake and relaunched; a saved Drinking Wheel game with test players left behind; language restored; no room created.
> **Not tested** — create/join room, scan, shake, location, multiplayer, share links: each needs another user, phone hardware, or writes shared data. Offered to test with consent.

## 8. What the session taught (generalised)

1. **The second route is where navigation bugs live.** The first route to a page usually works; the alternate entry is what the developer never tried.
2. **Text bugs appear only after a full language round-trip of every screen**, not one screen. Stored strings and plurals hide on pages you didn't revisit.
3. **"Duplicate accepted" is a finding only once you show the ambiguity downstream.** Play the round.
4. **Tap every bar.** Overlap depends on geometry; the first bar you tap is rarely the bad one.
5. **Zoom the host's Back/Close glyph every time** before pressing it. The relaunch cost ten minutes and reset state.
6. **Side effects are reported with the same precision as bugs** — the developer has to clean up after you.
7. **Say what you did not test and why**, and offer the path (a second account, a test build) rather than silently skipping.
