# Report template

Write it in the language the user used. Keep the app's labels in the app's own language inside quotes so the developer can find them. Replace bracketed text; if a section is genuinely empty, keep the heading and say so in one line.

---

I operated **[app name]** on **[platform: Telegram Desktop / iOS Simulator / Android emulator / WeChat DevTools / mobile web]** ([date], [build: production / test], [language(s) tested]) and confirmed the following.

### Confirmed bugs & security findings

1. **[Short title — what is wrong]** *(reproduced [N]×)* — severity: [blocks/misleads · visual · wording · security]
   - Where: [tab › page]
   - Steps: [1 → 2 → 3, using the app's own labels]
   - Expected: [one line]
   - Actual: [one line, what the screen showed]
   - Why it matters: [one line, only if not obvious]
   - Evidence: [screenshot name / console line / network status, if any]

2. …

### Observed once, not reproduced
- [What, where, what you tried to reproduce it]

### Minor / possibly by design
- [Observation] — [why it may confuse users]

### Verified OK
- [What was checked and found correct, grouped by screen]

### Side effects of this test session
- [Every change: data created, settings toggled, permissions granted/revoked, app relaunched] — [undone / left as-is, and how to clear it]
- [Own mistakes, e.g. accidentally closed the app and reopened it]

### Not tested
- [Feature] — [reason: needs another user / real device / would create shared data / payment / permission]. [Offer: can be tested with consent / a second account / a test build.]

---

Ordering rule: worst first. **Blocks or misleads normal use** (wrong navigation, wrong data, data loss) and **security** (other users' data, auth skipped) > visual defects > wording. Don't promote wording issues to make the list look fuller; don't bury a security note under visuals because it was "just an observation".
