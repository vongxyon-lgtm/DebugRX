# Case study: BaboBuy Android APK — a session that found real bugs and still disappointed

The user handed over an archive with a release APK and asked for bugs, then added two concerns mid-session: "we renamed babmall to BaboBuy — find every leftover" and, later, a logged-in round with a test account. The user's verdict at the end: *worse than the Telegram session.* This write-up is mostly about why, because those mistakes are the ones the current SKILL.md rules exist to prevent.

## 1. What happened, phase by phase

| Phase | What was done | Time |
|---|---|---|
| 0 Prepare | Archive extracted into its own folder; no adb, no emulator, no Java. Asked the user: emulator or real phone? → emulator. | short |
| 1 Connect | Installed command-line tools, OpenJDK 17 (formula — the cask needed sudo), Android 14 arm64 image; created an AVD; `monkey` failed with -5, `am start -n` worked. Noted: no Huawei HMS on the image. | long (downloads) |
| 2 Map | Five tabs, header icons, settings, login page. **Skipped the "responds?" check** — the dead home headset was found an hour later by accident. | short |
| 3 Explore (guest) | Category list, sort, product detail, login validation, language round-trip, search input, camera denial, offline/online, rotation, Back on root. Then a long detour into the package resources for brand strings. | long |
| 3 Explore (logged in) | Orders, wallet, coupons, invites, address book, favourites, help centre, cart add/delete with a before/after diff, search history, messages, web-view pages. | long |
| 4 Reproduce | Done for most candidates; three candidates turned out to be the tester's own mistakes. | — |
| 5 Restore | Cart diffed line by line against the snapshot: identical. Search history (2 entries) could not be removed — the app has no clear button. | short |
| 6 Report | Two reports, the second appended to the first; ~30 items; security finding ranked 7th in round two. | — |

## 2. Findings worth keeping (logic first)

1. **Logged-in state not passed to embedded web pages** — earn: "未登录,请先登录"; activity: web login form; member: "登录" + "暂无法开通"; wallet's web block blank.
2. **Invite records show invitees' full phone numbers** — 19 people, unmasked. (Security; should have been item 1.)
3. **Home headset icon is dead; home bell works only on its tiny unread badge** — the same icons work on the "Me" page.
4. **Add to cart is silent** — item added, no toast, SKU sheet stays open → repeat taps.
5. **Product-page cart badge shows 3** on every product while the cart holds 13; doesn't update after adding.
6. **Home stays blank after the network comes back** — no error while offline, no recovery until a hidden pull-to-refresh (reproduced twice).
7. **Camera denied twice → find-similar page permanently black**, no explanation, no route to settings.
8. **Search gate differs by entry** — guest: home search box → login; Category → list search works.
9. **Search history stores the newest keyword twice.**
10. Presentation, grouped: old brand names in ~20 places (text, images, loading animation, avatars, permission prompt "bab168", server tip "BABmall平台", web headers); Traditional characters and English in the Simplified UI; clipped English labels; one- vs two-decimal money.

## 3. What went wrong

1. **The checklist and report template were not re-read.** Only the Android driver guide was opened. Phase 3 drifted into "open page, screenshot, back"; the report ignored the template's steps/expected/actual shape and its ordering rule.
2. **Blind loops.** A shell loop tapped a list of entries, pressing Back after each. A Back fired during a transition left an extra page on the stack; the following taps landed on the wrong screens and produced three false candidates ("orders page opened twice", "group-buy View all opens the wrong list", "footprints does nothing"). Each was retracted after a clean re-test — but they cost time and, in one case, briefly reached the user.
3. **Scaled coordinates.** Screenshots were downscaled 2.4× for viewing; several taps used the small image's numbers and hit the wrong element (a password field instead of the Login button, the language picker instead of the headset).
4. **A tap landed inside a web page.** While re-testing the VIP button, two follow-up taps fell on the freshly loaded member page. Nothing was triggered ("暂无法开通"), but on a page with a working buy button this could have been a purchase.
5. **Breadth over depth.** Many screens were opened without any check that could fail. Wallet balance was never compared with transactions; order totals were never recomputed from their lines.
6. **Static analysis took over.** Mapping brand strings to resource keys was useful for the rename question, but it ran long and pulled time from logic probing.
7. **Report padding.** Thirty-odd items, many wording nits, the security finding buried, two rounds appended instead of merged. No screenshots or recordings were attached — the user had to trust prose.

## 4. What the session taught (now in SKILL.md)

1. **Re-read the whole skill every session**, not just the platform guide.
2. **One action, then verify.** Never loop taps or Backs; check the screen stack between probes.
3. **Tap from the UI tree**, in device pixels.
4. **Rule out yourself before calling it a bug** — stack clean? page loaded? tap on target?
5. **Map "responds?" for every icon**, tapping the icon body, not its badge.
6. **Write invariants and test before/after** — badge = cart, total = lines, logged in ⇒ every page knows it.
7. **Logic first, presentation in one sweep.** Most findings that matter here were logic.
8. **Evidence with every finding** — recordings with narration for logic, annotated screenshots for presentation, personal data redacted.
9. **One merged, ranked report**, about ten logic findings, presentation grouped, self-checked before sending.
10. **Snapshot the account before, diff after.**
