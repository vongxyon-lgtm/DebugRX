#!/usr/bin/env python3
"""Record a reproduction as video and log each step with its timestamp.

Logic bugs are reported with a recording plus a narrated step list. This script
starts and stops the platform's own recorder and keeps the step log, so the
narration under the video uses real timestamps.

    record.py start --platform android --name B01-cart-badge --out evidence
    record.py step "Tap 加入购物车 on the SKU sheet"
    record.py step "EXPECTED: toast + sheet closes | ACTUAL: nothing visible"
    record.py stop

Platforms
  android  adb shell screenrecord (max 180 s per clip, 4 Mbit/s), with the "pointer
           location" overlay on during the clip, restored afterwards. Uses $ADB or adb on
           PATH; --serial picks a device when several are attached.
  ios      xcrun simctl io <udid|booted> recordVideo (stop sends SIGINT).
  mac      macOS screencapture video of the whole screen or --rect x,y,w,h, for
           desktop hosts (Telegram Desktop, WeChat DevTools, a browser window).
           The app running this script needs Screen Recording permission.

Outputs in --out: <name>.mp4 (or .mov for mac) and <name>.steps.md.
Only one recording at a time; state lives in --out/.recording.json.
"""
import argparse
import json
import os
import shutil
import signal
import subprocess
import sys
import time

STATE = ".recording.json"


def adb_path():
    for cand in (os.environ.get("ADB"), shutil.which("adb"),
                 "/opt/homebrew/share/android-commandlinetools/platform-tools/adb",
                 os.path.expanduser("~/Library/Android/sdk/platform-tools/adb")):
        if cand and os.path.exists(cand):
            return cand
    sys.exit("adb not found: set $ADB or put adb on PATH")


def adb(serial):
    a = [adb_path()]
    return a + (["-s", serial] if serial else [])


def find_state(out=None):
    for d in ([out] if out else []) + [".", "evidence"]:
        p = os.path.join(d, STATE)
        if os.path.exists(p):
            return p
    sys.exit("no recording in progress (looked for %s)" % STATE)


def start(a):
    os.makedirs(a.out, exist_ok=True)
    sp = os.path.join(a.out, STATE)
    if os.path.exists(sp):
        sys.exit("a recording is already running; stop it first")
    st = {"platform": a.platform, "name": a.name, "out": os.path.abspath(a.out),
          "serial": a.serial, "t0": None, "steps": []}
    if a.platform == "android":
        remote = "/sdcard/debugrx_%s.mp4" % a.name
        # Pointer-location overlay (crosshair + X/Y) so viewers see where each tap landed;
        # "show_touches" does not draw for adb-injected taps. Restored on stop.
        prev = subprocess.run(adb(a.serial) + ["shell", "settings", "get", "system", "pointer_location"],
                              capture_output=True, text=True).stdout.strip()
        subprocess.run(adb(a.serial) + ["shell", "settings", "put", "system", "pointer_location", "1"], check=False)
        st["pointer_prev"] = prev if prev in ("0", "1") else "0"
        p = subprocess.Popen(adb(a.serial) + ["shell", "screenrecord", "--bit-rate", "4000000",
                                              "--time-limit", "180", remote],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        st.update(pid=p.pid, remote=remote, file=os.path.join(st["out"], a.name + ".mp4"))
    elif a.platform == "ios":
        f = os.path.join(st["out"], a.name + ".mp4")
        p = subprocess.Popen(["xcrun", "simctl", "io", a.udid or "booted", "recordVideo", "--codec=h264", "--force", f],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        st.update(pid=p.pid, file=f)
    else:
        f = os.path.join(st["out"], a.name + ".mov")
        cmd = ["screencapture", "-x", "-k", "-V", "180"] + (["-R", a.rect] if a.rect else []) + [f]
        p = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        st.update(pid=p.pid, file=f)
    time.sleep(1.5)  # recorder warm-up; the first step should not fall into the blind second
    if p.poll() is not None:
        hint = {"mac": "macOS Screen Recording permission is missing for the app running this script "
                       "(System Settings > Privacy & Security > Screen Recording). Ask the user to grant it, "
                       "or fall back to a numbered screenshot sequence.",
                "ios": "is a simulator booted? (xcrun simctl list devices booted)",
                "android": "is a device attached and authorised? (adb devices)"}[a.platform]
        sys.exit("recorder exited immediately: " + hint)
    st["t0"] = time.time()
    json.dump(st, open(sp, "w"))
    print("recording %s -> %s" % (a.name, st["file"]))


def step(a):
    sp = find_state(a.out)
    st = json.load(open(sp))
    t = time.time() - st["t0"]
    st["steps"].append([round(t, 1), a.text])
    json.dump(st, open(sp, "w"))
    print("%02d:%02d  %s" % (t // 60, t % 60, a.text))


def stop(a):
    sp = find_state(a.out)
    st = json.load(open(sp))
    time.sleep(1.0)  # let the last frame land
    if st["platform"] == "android":
        subprocess.run(adb(st["serial"]) + ["shell", "pkill", "-INT", "screenrecord"], check=False)
        time.sleep(2.5)
        subprocess.run(adb(st["serial"]) + ["pull", st["remote"], st["file"]], check=False,
                       stdout=subprocess.DEVNULL)
        subprocess.run(adb(st["serial"]) + ["shell", "rm", "-f", st["remote"]], check=False)
        subprocess.run(adb(st["serial"]) + ["shell", "settings", "put", "system", "pointer_location",
                                            st.get("pointer_prev", "0")], check=False)
    else:
        try:
            os.killpg(st["pid"], signal.SIGINT)
        except ProcessLookupError:
            pass
        for _ in range(20):
            try:
                os.kill(st["pid"], 0)
                time.sleep(0.5)
            except ProcessLookupError:
                break
    steps_md = os.path.join(st["out"], st["name"] + ".steps.md")
    with open(steps_md, "w", encoding="utf-8") as f:
        for t, text in st["steps"]:
            f.write("- %02d:%02d — %s\n" % (t // 60, t % 60, text))
    os.remove(sp)
    ok = os.path.exists(st["file"]) and os.path.getsize(st["file"]) > 0
    print(("saved %s (%d KB)" % (st["file"], os.path.getsize(st["file"]) // 1024)) if ok
          else "WARNING: no video file at %s" % st["file"])
    print("steps  %s" % steps_md)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("start")
    s.add_argument("--platform", choices=["android", "ios", "mac"], required=True)
    s.add_argument("--name", required=True, help="e.g. B03-home-search-login-gate")
    s.add_argument("--out", default="evidence")
    s.add_argument("--serial", help="adb device serial")
    s.add_argument("--udid", help="simulator UDID (default: booted)")
    s.add_argument("--rect", help="mac only: x,y,w,h screen rectangle")
    t = sub.add_parser("step")
    t.add_argument("text")
    t.add_argument("--out")
    p = sub.add_parser("stop")
    p.add_argument("--out")
    a = ap.parse_args()
    {"start": start, "step": step, "stop": stop}[a.cmd](a)


if __name__ == "__main__":
    main()
