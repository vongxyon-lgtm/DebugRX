# Exploration checklist

Concrete probes for each category in SKILL.md Phase 3. Each probe says what to do, what "wrong" looks like, and a real example of the bug class it catches — from the Telegram mini app case study (TG) and the Android APK case study (APK). The examples are there so you recognise the pattern, not so you look for that exact bug.

Every probe below is something that *could fail*. If you only opened a screen, you mapped it; you did not test it.

**Part A is the main work.** Logic bugs are what users lose orders and money over; give them about 70 % of the exploring time and capture each confirmed one as a **recording with narration**. Part B is one sweep per screen; capture each confirmed one as an **annotated screenshot**. (`evidence.md`)

## Contents

**A. Logic** — 1 Navigation stack · 2 Cross-screen consistency · 3 Action feedback and state change · 4 Entry rules · 5 Input → downstream · 6 State and persistence · 7 Error and recovery · 8 Hybrid / embedded web pages · 9 Permission flows · (10 Security → `security-observations.md`)

**B. Presentation** — 11 Localisation · 12 Branding and naming · 13 Layout and visuals

**C.** Things that are usually fine

---

# A. Logic

## 1. Navigation stack

| Probe | Wrong looks like | Example caught |
|---|---|---|
| Open page P from entry A, press Back | Lands anywhere other than A | TG: Home → "History" → Back lands on the Profile tab |
| Open the same P from entry B, press Back | Same — the bug usually shows only from the *second* route | same |
| Open a sheet/modal, press host/hardware Back | Sheet stays and the page behind navigates | — |
| Deep page → switch bottom tab → return | Stack lost, or stale page shown | — |
| Root screen: zoom the host's top-left/hardware control | It is Close/Exit while you expect Back | TG: pressing it closed the whole mini app |
| Root screen, hardware Back twice | Exits without warning, or never exits | APK: "press again to exit" toast — verified OK |

## 2. Cross-screen consistency

Write the invariant, then try to break it.

| Invariant | Wrong looks like | Example caught |
|---|---|---|
| Badge = what it counts, on *every* screen showing it | One screen right, another wrong or stale | APK: tab badge 13 (correct), product-page cart badge 3 on every product, not updated after adding |
| Total = Σ lines | Mismatch, rounding drift | APK: cart 0.41×2 + 4.17 = 4.99 — verified OK |
| Balance = Σ transactions; status ↔ timestamps | "Completed" with an empty completion time; "querying payment" for days | APK: order "已完成" with empty purchase-completion time |
| List = detail for the same entity | Different number, range, label | TG: list "2+ players", detail "2–20 players" |
| Value and its period agree on one card | Two time windows side by side | TG: "This week 76" beside "14-day daily average 5.4" |
| Sort order is what the control says | Out of order — but read the *layout* first | APK: a staggered two-column grid read top-to-bottom looked unsorted; interleaved it was correct (not a bug) |
| Notifications cover the events that happened | Latest message months older than latest order | APK: last message 04-27 while orders exist through November |

Zoom to read numbers; recompute totals and averages yourself.

## 3. Action feedback and state change

| Probe | Wrong looks like | Example caught |
|---|---|---|
| Every primary action (add, save, submit, delete) | No toast, no state change, sheet stays open — user taps again | APK: "加入购物车" added the item silently and left the SKU sheet open |
| Read every counter before and after the action | Some counters update, others don't | APK: tab badge 13 → 14, product-page badge stayed 3 |
| Tap the *body* of each icon, not just its badge or label | Only the tiny badge responds | APK: home bell icon dead; only the red unread-count badge opened messages |
| Same icon on two screens | Works on one, dead on the other | APK: headset opens support from "Me", does nothing on Home (3/3 taps) |
| Read the UI tree's clickable elements (`scripts/android_ui.py --click`) | An obvious icon is not clickable at all | APK: home headset absent from clickable nodes |
| Control at its limit | Looks enabled but does nothing, or the reverse | APK: minus button dark at the 2-piece minimum, does nothing (limit itself enforced) |
| Undo path | Added/turned on, but can't be removed/turned off | APK: search history has no clear button |

## 4. Entry rules

| Probe | Wrong looks like | Example caught |
|---|---|---|
| Same feature from two entries, as guest | One entry demands login, the other doesn't | APK: guest taps the home search box → login page; guest searches freely from Category → list |
| Same feature from two entries, logged in | Different limits, prices, options | — |
| Deep link / notification into a gated page | Gate skipped | — |

## 5. Input → downstream

| Input | Expect | Then check downstream |
|---|---|---|
| Empty / whitespace only | Rejected with a message | APK: empty home search does nothing, no hint |
| Very long (30+ chars) | Rejected or truncated consistently | Lists, toasts, result screens |
| Duplicate of an existing item | Rejected or disambiguated | TG: two "Player 2" → whose turn? |
| Special characters, emoji, `<b>`, quotes | Rendered literally everywhere | APK: `<b>x</b>'%&#` shown literally — verified OK |
| Nonsense query | "No results" | APK: unrelated products returned |
| Search, then reopen search | One history entry per search | APK: each new keyword stored twice ("cap, cap, socks") |
| Numeric stepper / minimum purchase | Min, max, step enforced at both ends | APK: "2件起购" minimum enforced — verified OK |
| Submit twice fast (double tap) | One record, not two | — |

## 6. State and persistence

| Probe | Expect |
|---|---|
| Start a flow, Back mid-way, return | Progress kept and signalled, or clearly discarded |
| Kill the app, reopen | Same; settings persisted — APK: language kept, verified OK |
| Finish a flow, start a new one | No leftovers |
| Rotate | Layout and state kept; no repeated prompts — APK: notification permission asked again after rotation |
| Pre-selected option in a long list | The selected item is visible — APK: default SKU colour was option 44 of 44, off-screen |

Everything you create here is a side effect — log it.

## 7. Error and recovery

| Probe | Wrong looks like | Example caught |
|---|---|---|
| Network off, open each main screen | Blank page with no message, or a misleading one | APK: Home blank with no error; Category said "正在努力修复中" (as if the server were broken) |
| Network back on, wait 30 s, *without* relaunching | Screen stays broken | APK: Home stayed blank until a hidden pull-to-refresh (reproduced twice) |
| Retry affordance | Visible button or hint | APK: Category retries on tap, but nothing says so |
| Cold start / after a language switch | Blank for seconds with no spinner | APK: Home blank ~5 s after switching language |
| Slow first load | Stuck spinner | APK: favourites >15 s once, then 2–3 s (observed once) |

Note rough timings; the developer can't see what you saw.

## 8. Hybrid / embedded web pages

Many "native" apps show member, wallet, activity or help pages as web views. Mark them in the map.

| Probe | Wrong looks like | Example caught |
|---|---|---|
| Log in in the app, open each web page | "Please log in", a login form, or a login button | APK: earn → "未登录,请先登录"; activity → web login form; member → "登录" + "暂无法开通" |
| Content area | Blank block where options should be | APK: wallet recharge area empty (likely the same session issue) |
| Back controls | Native and web back bars stacked | APK: two back arrows on the activity page |
| Links leaving the app | Jumps to an external browser/app with no notice | APK: blind box opened Chrome at bababox.vip |

Do not tap inside a web page until you have read it — buy and submit buttons move as it loads.

## 9. Permission flows

| Probe | Expect | Example caught |
|---|---|---|
| Deny once, use the feature | Explanation and a way to settings | — |
| Deny twice ("don't ask again"), reopen the feature | Still an explanation and a way to settings | APK: scan page permanently black, shutter does nothing |
| Revoke after granting, retry | Same | — |
| Background → foreground after 1 min | Screen restored | — |

---

# B. Presentation

One sweep per screen. Screenshot at full resolution the moment you see it; annotate later.

## 11. Localisation

Switch to each language the app offers and walk *every* screen again. Switch back at the end.

| Probe | Wrong looks like | Example caught |
|---|---|---|
| Static labels | Untranslated or mixed language | APK: "Order #" and English help-centre headings in the Chinese UI |
| Mixed script within one language | Traditional characters in a Simplified UI, or the reverse | APK: "中國運費：點擊查詢", "消費", "其他登入方式" in Simplified Chinese |
| Longer languages | Labels clipped with "…" | APK: "Make…", "Mem…", "Find same st…" in English |
| Images and banners | Text baked into images stays in one language | APK: Chinese and Khmer banners in the English UI |
| User-generated names created in language A, viewed in B | Rendered with A's template | TG: "AH.YEUNG的局" in the English UI |
| Counts of 1 | Plural with 1 | TG: "1 drinking days" |
| Dates, numbers, currency | Wrong format; missing year; inconsistent decimals | APK: "$45.31" beside "$2.4", "$0.0"; messages dated "04-27" across two years |
| Language picker labels | Country name instead of language name | APK: Khmer option reads "កម្ពុជា។" ("Cambodia.") |

## 12. Branding and naming

Run this whenever the user mentions a rename, a merger, or several brands — and glance at it anyway.

| Where to look | Example caught |
|---|---|
| Plain UI text, welcome lines, terms text, About page | APK: "欢迎来到 bab1688", "关于bAb1688 APP", "Bab1688 的服务条款" under a BaboBuy logo |
| Images: banners, header logos, mascots, QR-code centres | APK: "babmall" on home banners and the category header |
| Placeholders: default avatars, empty-state art, loading animations | APK: "bab × 1688" avatar; old "bab" loading animation |
| Prompts the app writes: permission rationales, share text | APK: "允许“bab168”使用相机" — old name and a missing digit |
| Server-sent text: tips, notices, help centre | APK: "BABmall平台会协助您…" in the order tip — backend must change it |
| Embedded web pages | APK: "bab × 1688" header on member, earn and activity pages |
| Identifiers users see: order numbers, chat titles | APK: order numbers "BAB…", chat title "BAB客服" |

Report all brand residue as **one finding** with a table (where · text · source: package / image / server / web) and one or two annotated screenshots. Separate what users see from internal identifiers (package name, backend project ids, deep-link schemes) and say which must *not* be changed casually.

## 13. Layout and visuals

| Probe | Wrong looks like | Example caught |
|---|---|---|
| Tap every chart bar/point, especially first, last, highest | Tooltip covers the value; clipped at an edge | TG: tooltip overlapped "76" and was clipped |
| Logos and text on coloured bars | Invisible contrast | APK: orange "babmall" logo on an orange header |
| Elements at the screen edge | Half-cut graphics | APK: half a yellow mark top-left on Home (a loading animation peeking out) |
| Error text placement | Message under the wrong field | APK: "请输入手机号码" under the country-code box |

---

# C. Things that are usually fine (check once, move on)

- Active tab highlighted.
- Sheets close on Back.
- Delete asks for confirmation.
- Language persists across relaunch.

Verify once so they can go in "Verified OK". No second pass.
