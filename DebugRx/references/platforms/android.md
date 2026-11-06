# Driver guide: Android app (emulator, USB device, or an APK to install)

Drive with `adb` from Bash. Works for an emulator and for a physical device with USB debugging on; the user must authorise the computer on the device.

## 0. No emulator yet? Set one up (macOS, no Android Studio)

Start the downloads in the background and read the checklist while they run — this takes a while and ~7–8 GB.

```bash
brew install --cask android-commandlinetools          # sdkmanager, avdmanager
brew install openjdk@17                               # formula: no sudo needed (the temurin cask asks for a password)
export JAVA_HOME=/opt/homebrew/opt/openjdk@17
export ANDROID_HOME=/opt/homebrew/share/android-commandlinetools
yes | $ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager --sdk_root=$ANDROID_HOME --licenses
$ANDROID_HOME/cmdline-tools/latest/bin/sdkmanager --sdk_root=$ANDROID_HOME \
  "platform-tools" "emulator" "system-images;android-34;google_apis;arm64-v8a"
echo no | $ANDROID_HOME/cmdline-tools/latest/bin/avdmanager create avd -n debugrx -k "system-images;android-34;google_apis;arm64-v8a" -d pixel_6
$ANDROID_HOME/emulator/emulator -avd debugrx -no-snapshot-save -no-audio -no-boot-anim   # run in background
adb wait-for-device; until [ "$(adb shell getprop sys.boot_completed | tr -d '\r')" = 1 ]; do sleep 2; done
```

Tell the user what you installed and how big it is; it goes in "Side effects".

**Environment gaps.** A Google-APIs image has no Huawei HMS; a Huawei-oriented app may lose push, map or ML features. Note it in the report header and label any finding that might come from it.

**APK inside an archive.** Extract into its own empty folder (`unar`/`7z`), rename to `.apk` if needed, `adb install -r app.apk`. Record the package name: `adb shell pm list packages -3` before and after.

## 1. Connect

```bash
adb devices                                          # one entry, state "device"
adb shell cmd package resolve-activity --brief -c android.intent.category.LAUNCHER <package>
adb shell am start -W -n <package>/<activity>        # monkey can exit -5 on some apps; this always works
adb shell dumpsys window | grep mCurrentFocus        # which activity is on top
adb exec-out screencap -p > shot.png                 # full resolution: device pixels
adb shell wm size                                    # e.g. 1080x2400
```

**Coordinate scale.** `screencap` is full device resolution. If you downscale screenshots to view them (e.g. to 450×1000), every coordinate you read off them must be multiplied back (×2.4 here). Better: take tap coordinates from the UI tree.

## 2. Read the screen — UI tree first

```bash
adb shell rm -f /sdcard/ui.xml                       # never read a stale dump
adb shell uiautomator dump /sdcard/ui.xml && adb pull /sdcard/ui.xml ui.xml
python3 scripts/android_ui.py ui.xml                 # text + ids + bounds + tap centre
python3 scripts/android_ui.py ui.xml --click         # clickable elements only
```

- `ERROR: could not get idle state` means the screen is animating (banners, loaders). The dump is not written — with the `rm` above you get "file not found" instead of silently reading the previous screen. Wait and retry, or use a screenshot.
- An icon the user would tap that is **missing from `--click`** is a dead control — a logic finding (see checklist §3).
- WebView content (member, wallet, activity, help pages) often doesn't appear in the dump; use screenshots there, and read before tapping.

## 3. Act — one action, then verify

```bash
adb shell input tap X Y                              # X,Y from the UI tree, in device pixels
adb shell input swipe X1 Y1 X2 Y2 300
adb shell input text 'hello%sworld'                  # %s = space; ASCII only
adb shell input keyevent 4                           # hardware Back   (3 = Home, 66 = Enter)
```

After each action: wait for the screen to settle, then check `mCurrentFocus` or a fresh dump. **Never loop taps or Backs blind.** A Back pressed during a page transition leaves an extra page on the stack and your next tap lands on the wrong screen — the source of every false finding in the APK case study.

**Clean state between probes:**

```bash
adb shell dumpsys activity activities | grep -E '\* ActivityRecord' | grep -c <package>   # stack depth
# press Back one at a time, checking depth each time, until it is 1; then tap the bottom tab you need
```

## 4. Traps

- `input text` can't type non-ASCII; for Chinese, use a clipboard helper app or type through the emulator window with computer-use, and say which.
- Hardware Back is a real probe (every screen must handle it), distinct from the in-app back arrow. Test both.
- `pm clear <package>` resets data **and permissions and logs the user out** — use it only on guest sessions or with the user's consent.
- Links that leave the app open Chrome's first-run screen on a fresh emulator. Don't accept Chrome's terms; press Back.
- A physical device may lock mid-session: `adb shell input keyevent KEYCODE_WAKEUP`, then swipe up.

## 5. Platform-specific probes

| Probe | Command |
|---|---|
| Network off / on (error & recovery) | `adb shell svc wifi disable; adb shell svc data disable` … `enable` — then wait 30 s *without* relaunching |
| Kill and relaunch (state) | `adb shell am force-stop <package>`, then `am start -n …` |
| Rotate | `adb shell settings put system user_rotation 1`, then `0` |
| Deny / revoke a permission | deny in the dialog twice for "don't ask again"; or `adb shell pm revoke <package> android.permission.CAMERA` |
| "Don't keep activities" (state loss) | Developer options; restore afterwards |
| Crash evidence | `adb logcat -b crash -d`, or `adb logcat -d \| grep -iE 'fatal\|exception' \| tail -50` — paste the top frame |

## 6. Evidence

```bash
# logic bug: record the confirming run with a step log (pointer-location overlay switched on automatically)
python3 scripts/record.py start --platform android --name B01-home-bell-dead --out evidence
python3 scripts/record.py step "Tap the bell icon body" --out evidence
adb shell input tap 995 210
python3 scripts/record.py step "EXPECTED message centre | ACTUAL nothing" --out evidence
python3 scripts/record.py stop --out evidence

# presentation bug: full-resolution screenshot, then annotate with UI-tree bounds
adb exec-out screencap -p > raw.png
uv run --with pillow python scripts/annotate.py raw.png evidence/V01-mixed-script.png --box 740,1873,1048,1941 --crop 260 --caption "1 …"
```

Several devices attached: add `--serial emulator-5554`.

## 7. Release

Re-enable wifi/data, re-grant permissions you revoked, rotation back to 0, pointer location back off (record.py does this), developer options back. Say whether the emulator is still running and how to stop it (`adb emu kill`).
