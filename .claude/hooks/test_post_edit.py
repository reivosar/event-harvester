#!/usr/bin/env python3
"""Tests for post-edit.sh: auto-format dispatch and graceful skip on missing files."""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HOOK = os.path.join(os.path.dirname(__file__), "post-edit.sh")


def run_hook(file_path, raw_stdin=None):
    if raw_stdin is None:
        payload = json.dumps({"tool_name": "Write", "tool_input": {"file_path": file_path}})
    else:
        payload = raw_stdin
    result = subprocess.run(
        ["bash", HOOK],
        input=payload, capture_output=True, text=True,
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


# TC-PE-01: nonexistent file path → hook skips silently
check("TC-PE-01 nonexistent file exits 0", run_hook("/nonexistent/path/file.py"), 0)

# TC-PE-02: empty file_path → hook skips silently
check("TC-PE-02 empty path exits 0", run_hook(""), 0)

# TC-PE-03: .sh file — shfmt if available, otherwise skip — always exit 0
with tempfile.NamedTemporaryFile(suffix=".sh", delete=False, mode="w") as f:
    f.write("#!/usr/bin/env bash\necho hello\n")
    sh_file = f.name
try:
    check("TC-PE-03 sh file exits 0", run_hook(sh_file), 0)
finally:
    os.unlink(sh_file)

# TC-PE-04: .py file — black/autopep8 if available, otherwise skip — always exit 0
with tempfile.NamedTemporaryFile(suffix=".py", delete=False, mode="w") as f:
    f.write("x=1\n")
    py_file = f.name
try:
    check("TC-PE-04 py file exits 0", run_hook(py_file), 0)
finally:
    os.unlink(py_file)

# TC-PE-05: .go file — gofmt if available, otherwise skip — always exit 0
with tempfile.NamedTemporaryFile(suffix=".go", delete=False, mode="w") as f:
    f.write("package main\nfunc main() {}\n")
    go_file = f.name
try:
    check("TC-PE-05 go file exits 0", run_hook(go_file), 0)
finally:
    os.unlink(go_file)

# TC-PE-06: unknown extension — no formatter mapped — hook exits 0
with tempfile.NamedTemporaryFile(suffix=".xyz", delete=False, mode="w") as f:
    f.write("hello\n")
    xyz_file = f.name
try:
    check("TC-PE-06 unknown extension exits 0", run_hook(xyz_file), 0)
finally:
    os.unlink(xyz_file)

# TC-PE-07: malformed JSON stdin — hook exits 0 (python3 parse fails, FILE becomes empty)
check("TC-PE-07 malformed JSON exits 0", run_hook(None, raw_stdin="not-json"), 0)

print(f"\n{passed} passed, {failed} failed")
sys.exit(0 if failed == 0 else 1)
