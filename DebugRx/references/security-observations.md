# Security observations (black-box, non-intrusive)

What a tester can notice *while operating the app normally* that a developer should fix. This is not a penetration test: you do not fuzz endpoints, replay or forge requests, brute-force anything, or touch another user's account. If a finding would need that to confirm, write it as "needs a security review" with what you saw, and stop.

## Contents

1. Sensitive data where it can be seen
2. Identifiers and access
3. Input that reaches other users
4. Authentication flows
5. Payments and money-like values
6. Platform-specific
7. How to write these up

---

## 1. Sensitive data where it can be seen

| Look for | Where | Why it matters |
|---|---|---|
| Tokens, session ids, `initData`, phone numbers, emails in the **URL** (share links, deep links, "copy link") | share sheet, address bar, QR content | URLs are logged, forwarded, screenshotted |
| Full card numbers, ID numbers, passwords shown in clear | profile, order, settings | should be masked |
| Other users' phone/email in a friend list or leaderboard | lists | data exposure |
| Tokens or PII in local storage (web/mini program Storage panel) | DevTools | readable by anything on the device |
| Stack traces, SQL, internal hostnames in error toasts | error states (§7 of checklist) | information leak |
| Debug menus, "test mode" switches, hidden admin pages reachable by tap | settings, about page, long-press on logo | should not ship |

## 2. Identifiers and access

| Look for | How you notice it without attacking |
|---|---|
| Sequential numeric ids in URLs or UI (`/order/1042`, "Room #88") | Two of your own objects differ by 1 — note it as "predictable id; verify server-side authorisation" |
| A page reachable by deep link without being logged in | Open the deep link in a fresh session (your own) |
| Actions available in the UI for objects you don't own (edit/delete on another user's post) | Visible controls, don't press them |
| Role-based screens (admin, host) visible to a normal member | Visible, don't act |

## 3. Input that reaches other users

While doing checklist §4 (input validation), use names and messages like:

```
<b>bold</b>   {{name}}   ' OR 1=1   😀🔥   مرحبا   ThisIsAVeryLongNameWithoutSpaces
```

Then look at every place that value is rendered — lists, toasts, notifications, the other participant's view if you can see it. Wrong looks like: tags rendered as formatting, template braces evaluated, layout broken by a long token, RTL text flipping a row. Rendering `<b>` as bold is a real finding (XSS surface in a WebView); the SQL-looking string is only there to see it echoed literally — never go further.

## 4. Authentication flows

| Probe | Wrong looks like |
|---|---|
| OTP / verification code field | Unlimited attempts, no cooldown shown, code visible in a toast |
| "Resend code" | No throttle |
| Password field | No masking, no paste blocked where it should be allowed, max length tiny |
| Log out, press Back | Protected page still shows cached content |
| Session expiry (wait, or clear the cookie on web) | Infinite spinner instead of re-login |
| Account switching (if the host allows) | Previous user's data flashes |

## 5. Payments and money-like values

Never complete a real payment. Test up to the confirmation screen and the cancel path.

| Look for |
|---|
| Price or quantity editable client-side after the server computed a total (change it, see if the total follows — then cancel) |
| Exchange rates / steppers that accept 0, negative, or absurd values |
| Rounding differences between list and checkout |
| "Pay" button enabled before validation completes |

## 6. Platform-specific

- **Telegram Mini App**: `initData` in a share link or visible in the UI; `start_param` trusted without validation (open a link with a modified param to *your own* object only); theme params leaking nothing.
- **WeChat mini program**: `wx.setStorage` holding tokens/PII; `wx.getUserProfile` called before it is needed.
- **iOS/Android**: screenshots allowed on sensitive screens (banking apps block them); clipboard reads at launch (Android 10+ and iOS 14+ show a banner — note it); permissions requested at cold start before the feature is used.
- **Web**: mixed content, `http://` links, auth token in `localStorage` rather than an HttpOnly cookie, console errors that reveal API shapes.

## 7. How to write these up

Same format as a bug — where, steps, what was seen — plus one line on impact and one on what you did *not* do:

> **Predictable room ids.** Rooms I created were #1041 and #1042. I did not try to open other ids. Verify that the server checks membership on every room request.

Put findings that expose other users' data or skip authentication at the top of the report regardless of how small they look.
