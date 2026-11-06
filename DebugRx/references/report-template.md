# Report template

Write it in the language the user used. Keep the app's labels in the app's own language inside quotes so the developer can find them. Replace bracketed text; if a section is genuinely empty, keep the heading and say so in one line.

**One report per app.** If you tested in rounds (guest, then logged in; build 1, then build 2), merge the findings and re-rank them. Never append a second report under the first.

**Logic first.** Logic and security findings come before presentation findings and should be most of the report. If the report is mostly wording, the exploring time went to the wrong half.

**Evidence.** Logic and security → recording + narration. Presentation → annotated screenshot + explanation. Build the page with `scripts/build_report.py report.md` and hand the user `report.html`.

**Budget.** About 10 logic/security findings, a few grouped presentation findings, and about 10 minor bullets at most. If you have more, you are listing instances instead of defects — group them. Everything else stays in the scratch log.

---

I operated **[app name]** on **[platform: Telegram Desktop / iOS Simulator / Android emulator / WeChat DevTools / mobile web]** ([date], [build: production / test], [guest / logged in as test account], [language(s) tested]) and confirmed the following.
[If the environment lacks something the app relies on — e.g. no Huawei/Google services on the emulator — say so here in one line.]

### Logic & security findings

Worst first, at most about 10. Each one is shown with a recording and narrated (`evidence.md`).

1. **[Short title — what is wrong]** *(reproduced [N]×)* — severity: [security · blocks/misleads]
   - Where: [tab › page]
   - Steps: [1 → 2 → 3, using the app's own labels]
   - Expected: [one line]
   - Actual: [one line, what the screen showed]
   - Why it matters: [one line — lost orders, wrong money, users stuck, data exposed]
   - [Possibly environment-related: say why, if so]

   ![录屏：[one-line summary of what the clip shows]](evidence/B01-[slug].mp4)

   **解说 / Narration**
   - 0:00 [starting state]
   - 0:03 [action] — **实际 / Actual**: [what happened]. **预期 / Expected**: [what should have happened].
   - 0:08 [the contrast, if any: the other route, the working control, the other screen's number]
   - **影响 / Impact**: [one line]

2. …

### Presentation findings (language, branding, layout)

Grouped by kind — one finding per kind, not one per screen. Each is shown with annotated screenshots.

N. **[Defect kind, e.g. "Old brand names still shown after the rename"]** *(seen in [K] places)* — severity: [visual · wording]

   ![① … ② …](evidence/V01-[slug].png)

   **说明 / Explanation**: ① [what box 1 shows and what it should say] ② […]

   | Where | Text / image | Source |
   |---|---|---|
   | [screen] | "[exact text]" | package resource `[key]` / image / server text / web page |

   - Do not change: [internal identifiers that would break things if renamed, e.g. package name, backend project id]

### Observed once, not reproduced
- [What, where, what you tried to reproduce it]
- (Candidates you traced to your own mistake — wrong tap, page still loading, stack not clean — are **not** listed here or anywhere in the report.)

### Minor / possibly by design
- [Observation] — [why it may confuse users]

### Static findings (only if the user asked a question that needed the package)
- [Finding] — [file / resource key] — [what the developer should do]

### Verified OK
- [What was checked and found correct, grouped by screen]

### Side effects of this test session
- [Every change: data created, settings toggled, permissions granted/revoked, app relaunched, account diff result] — [undone / left as-is, and how to clear it]
- [Own mistakes, e.g. a tap landed inside a web page; what, if anything, it triggered]
- [Tools or emulators installed on the user's machine, size, whether still running]

### Not tested
- [Feature] — [reason: needs another user / real device / would create shared data / payment / permission]. [Offer: can be tested with consent / a second account / a test build.]

---

**Ordering rule:** worst first. **Security** (other users' data, auth gaps) and **blocks or misleads normal use** (dead entry, wrong data, wrong navigation, lost state, silent actions) > visual defects > wording. Don't promote wording issues to make the list look fuller; don't bury a security note under visuals because it was "just an observation".

**Self-check before sending:**
1. Is the most severe finding first?
2. Can a developer follow every confirmed item's steps without you?
3. Is anything here a candidate you later disproved? Delete it.
4. Are same-kind defects grouped into one finding?
5. Does every logic/security finding have a recording with narration, and every presentation finding an annotated screenshot? Is other people's personal data redacted?
6. Do logic findings lead the report?
7. Can the user read the findings sections in two minutes?
