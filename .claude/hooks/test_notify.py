#!/usr/bin/env python3
"""Tests for notify.sh and on-stop.sh: always exit 0 regardless of input."""
import json
import os
import subprocess
import sys

NOTIFY_HOOK = os.path.join(os.path.dirname(__file__), "notify.sh")
STOP_HOOK = os.path.join(os.path.dirname(__file__), "on-stop.sh")


def run_notify(payload):
    result = subprocess.run(
        ["bash", NOTIFY_HOOK],
        input=payload, capture_output=True, text=True,
    )
    return result.returncode


def run_stop():
    result = subprocess.run(
        ["bash", STOP_HOOK],
        input="", capture_output=True, text=True,
    )
    return result.returncode


passed = failed = 0


def check(label, got, expected):
    global passed, failed
    ok = got == expected
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {label} → expected exit {expected}, got {got}")
    if ok:
        passed += 1
    else:
        failed += 1


# notify.sh: each notification_type maps to a message — hook always exits 0
for ntype in ("permission_prompt", "idle_prompt", "auth_success"):
    payload = json.dumps({"notification_type": ntype})
    check(f"notify.sh notification_type={ntype!r}", run_notify(payload), 0)

# unknown type falls through to default message — still exits 0
check("notify.sh unknown type", run_notify(json.dumps({"notification_type": "whatever"})), 0)

# missing key — python3 parse returns '' which falls through default — exits 0
check("notify.sh missing notification_type key", run_notify(json.dumps({})), 0)

# malformed JSON — python3 -c parse fails silently (2>/dev/null), TYPE is empty — exits 0
check("notify.sh malformed JSON", run_notify("not-json"), 0)

# on-stop.sh: no stdin required — always exits 0
check("on-stop.sh exits 0", run_stop(), 0)

print(f"\n{passed} passed, {failed} failed")
sys.exit(0 if failed == 0 else 1)
