# Driver guide: Android app (emulator or USB device)

Drive with `adb` from Bash. Works for an emulator and for a physical device with USB debugging on; the user must authorise the computer on the device.

## 1. Connect

```bash
adb devices                         # one entry, state "device"
adb shell dumpsys window | grep mCurrentFocus   # which activity is on top
adb exec-out screencap -p > /path/shot.png      # screenshot (read it with Read)
```

Confirm the screenshot shows the app's own UI and note the package name from `mCurrentFocus`. Finish Phase 1 with the screen size:

```bash
adb shell wm size
```

## 2. Act

```bash
adb shell input tap X Y
adb shell input swipe X1 Y1 X2 Y2 300
adb shell input text 'hello%sworld'    # %s is a space; escape shell metacharacters
adb shell input keyevent KEYCODE_BACK  # 4
adb shell input keyevent KEYCODE_HOME  # 3
adb shell am start -a android.intent.action.VIEW -d 'scheme://deep/link'
adb shell am force-stop <package>      # kill (state-persistence probe)
adb shell pm revoke <package> android.permission.CAMERA
adb shell svc wifi disable && adb shell svc data disable   # offline probe; re-enable after
```

Read the view hierarchy when coordinates are unclear:

```bash
adb shell uiautomator dump /sdcard/ui.xml && adb pull /sdcard/ui.xml /path/ui.xml
```

It lists `text`, `resource-id`, `bounds` for every node — the fastest way to find a button's centre and to read small text exactly.

## 3. Traps

- `input text` cannot type non-ASCII reliably; for Chinese or emoji, use the clipboard (`adb shell am broadcast` with a clipper app) or type via the emulator window with computer-use. Say which you did.
- Hardware Back is a real probe on Android (every screen must handle it), distinct from in-app back arrows. Test both.
- WebView-based screens (hybrid apps, mini programs inside super-apps) don't show in `uiautomator dump`; fall back to screenshots.
- A physical device may lock its screen mid-session: `adb shell input keyevent KEYCODE_WAKEUP` then swipe up.

## 4. Platform-specific probes

- Hardware Back on every screen, including dialogs and bottom sheets.
- Rotate (`adb shell settings put system user_rotation 1`), then back to 0: state kept?
- Kill and relaunch (`force-stop`, then `monkey -p <package> 1` or tap the icon): where does it reopen?
- Deny/revoke each runtime permission and retry the feature.
- "Don't keep activities" in Developer options: the most reliable way to surface state loss.
- Logcat while reproducing a crash: `adb logcat -d | grep -i -E 'fatal|exception' | tail -50` — paste the top frame into the report.

## 5. Release

Re-enable wifi/data, re-grant any permission you revoked, rotate back, and say so in the report.
