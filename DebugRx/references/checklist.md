# Exploration checklist

Concrete probes for each category in SKILL.md Phase 3. Each probe says what to do, what "wrong" looks like, and a real example of the bug class it catches (most from the Babobuy case study). Run every category on every screen; the examples are there so you recognise the pattern, not so you look for that exact bug.

## Contents

1. Navigation stack
2. Cross-screen consistency
3. Localisation
4. Input validation
5. Data display and charts
6. State and persistence
7. Loading, empty and error states
8. Permissions, device and interruptions
9. Things that are usually fine (check once, move on)

Security probes are in `security-observations.md`.

---

## 1. Navigation stack

| Probe | Wrong looks like | Example caught |
|---|---|---|
| Open page P from entry A, press Back | Lands anywhere other than A | Home → "History" → Back lands on the Profile tab; a second Back is needed |
| Open the same P from entry B, press Back | Same — the bug usually shows only from the *second* route | same |
| Open a sheet/modal, press host/hardware Back | Sheet stays and the page behind navigates | — |
| Deep page → switch bottom tab → return | Stack lost, or stale page shown | — |
| Root screen: zoom the host's top-left/hardware control | It is Close/Exit while you expect Back | Pressing it closed the whole mini app |
| Deep link / notification into a deep page, then Back | Nowhere to go, or exits the app | — |

Why it matters: hosts (Telegram, WeChat, Android) give the app one back callback; apps that hard-code "Back goes to tab X" break every alternate route.

## 2. Cross-screen consistency

| Probe | Wrong looks like | Example caught |
|---|---|---|
| Same entity in list and detail | Different number, range, label | List "2+ players", detail "2–20 players" |
| Card summary vs. the page it links to | Totals/averages differ | — |
| Value and its period on one card | Two windows side by side | "This week 76" beside "14-day daily average 5.4" |
| Ranking with one participant | Rank shown where meaningless | 1-person table with 0 drinks shown as "1st place" |
| Badge counts vs. list length | Off by one, stale | — |

Zoom to read numbers; recompute simple totals and averages from the detail rows yourself.

## 3. Localisation

Switch to each language the app offers and walk *every* screen again. Switch back at the end.

| Probe | Wrong looks like | Example caught |
|---|---|---|
| Static labels | Untranslated or mixed | — |
| User-generated names created in language A, viewed in B | Rendered with A's template | "AH.YEUNG的局" in the English UI while new ones read "AH.YEUNG's table" — the name was stored at creation |
| Counts of 1 | Plural with 1 | "1 drinking days" |
| Long translations | Clipped, overlapping icons | — |
| Dates, weekdays, numbers, currency | Wrong locale format; weekday off by one | verify calendar weekdays against a real calendar |
| RTL language if offered | Mirrored layout broken | — |

## 4. Input validation

Every text field and every "add item" list.

| Input | Expect | Then check downstream |
|---|---|---|
| Empty / whitespace only | Rejected with a message | — |
| Very long (30+ chars) | Rejected or truncated *consistently* | Does the truncated value fit in lists, toasts, result screens? |
| Duplicate of an existing item | Rejected or disambiguated | Two "Player 2" → whose turn, who got the penalty? The downstream ambiguity is the bug |
| Special characters, emoji, `<b>`, quotes | Rendered literally everywhere the value appears | see security §3 |
| Numeric stepper / range | Min, max, step enforced at both ends | 0.5 step, min 0.5 — go below and above |
| Paste a 10 000-char string | No freeze, no crash | — |
| Submit twice fast (double tap) | One record, not two | — |

## 5. Data display and charts

| Probe | Wrong looks like | Example caught |
|---|---|---|
| Tap every bar/point, especially first, last, highest | Tooltip covers the value; clipped at an edge; wrong date | "11月4日 周三" tooltip overlapped the "76" value and the summary line, clipped on the right |
| Chart value vs. the list it summarises | Mismatch | — |
| Zero / missing days | Gaps vs. zeros confusingly rendered | — |
| Legend vs. series colours | Mismatch | — |
| Very large / very small values | Axis breaks, labels overlap | — |

## 6. State and persistence

| Probe | Expect |
|---|---|
| Start a flow, Back mid-way, return | Progress kept and signalled ("Continue" badge) — or clearly discarded, not half of each |
| Kill the app / close the mini app, reopen | Same, plus no stale screen from last session |
| Finish a flow, start a new one | No leftovers (old players, old scores, old form values) |
| Change a setting, relaunch | Persisted |
| Two tabs/windows of the same account (web) | No clobbered state |

Everything you create here is a side effect — log it with enough detail to undo or report.

## 7. Loading, empty and error states

| Probe | Wrong looks like |
|---|---|
| Cold start | Blank for seconds with no spinner; ad/consent popup covering the UI |
| Screen with no data (new user) | Empty table, "undefined", NaN, crash |
| Network off (airplane mode / offline) then act | Spinner forever, raw error JSON, silent failure |
| Network back on | App recovers without relaunch |
| Server error (if a test build lets you force one) | Friendly message, retry path |
| Slow network | Content flashes twice, duplicated list items |

Note rough timings ("blank ~4 s then popup"); the developer can't see what you saw.

## 8. Permissions, device and interruptions

| Probe | Expect |
|---|---|
| Deny a permission at the prompt, use the feature | Clear explanation and a way to the settings, no crash |
| Revoke after granting, retry | Same |
| Rotate (if allowed) | Layout and state kept |
| Background → foreground after 1 min | Screen restored; countdowns correct |
| Dark mode / large font | Readable, nothing clipped |
| Small screen model (simulator/DevTools) | No overlap |

## 9. Things that are usually fine (check once, move on)

- Active tab highlighted.
- Sheets close on Back.
- Stepper limits.
- Friend/contact counts match list lengths.

Verify once so they can go in "Verified OK". No second pass.
