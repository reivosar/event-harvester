#!/usr/bin/env python3
"""Tests for trash.sh: moves files to session trash, blocks paths outside project root."""
import os
import shutil
import subprocess
import sys
import tempfile

HOOK = os.path.join(os.path.dirname(__file__), "trash.sh")
SESSION_FILE = "/tmp/claude-session-trash-dir"


def make_git_repo():
    tmpdir = os.path.realpath(tempfile.mkdtemp(prefix="hook_test_trash_"))
    clean_env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    subprocess.run(["git", "init", tmpdir], check=True, capture_output=True, env=clean_env)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmpdir, check=True, capture_output=True, env=clean_env)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmpdir, check=True, capture_output=True, env=clean_env)
    init_path = os.path.join(tmpdir, "init.txt")
    with open(init_path, "w") as f:
        f.write("init\n")
    subprocess.run(["git", "add", "init.txt"], cwd=tmpdir, check=True, capture_output=True, env=clean_env)
    subprocess.run(["git", "commit", "-m", "init"], cwd=tmpdir, check=True, capture_output=True, env=clean_env)
    return tmpdir


def reset_session():
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)


def run_hook(tmpdir, *targets):
    clean_env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    result = subprocess.run(
        ["bash", HOOK] + list(targets),
        capture_output=True, text=True, cwd=tmpdir, env=clean_env,
    )
    return result.returncode


def cleanup(tmpdir):
    shutil.rmtree(tmpdir, ignore_errors=True)


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


# TC-TR-01: file inside project root is moved to trash
reset_session()
tmpdir = make_git_repo()
try:
    target = os.path.join(tmpdir, "delete_me.txt")
    with open(target, "w") as f:
        f.write("bye\n")
    rc = run_hook(tmpdir, target)
    file_gone = not os.path.exists(target)
    trash_dir = open(SESSION_FILE).read().strip() if os.path.exists(SESSION_FILE) else ""
    file_in_trash = trash_dir and os.path.exists(os.path.join(trash_dir, "delete_me.txt"))
    check("TC-TR-01 in-project file moved", rc, 0)
    ok = file_gone and file_in_trash
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] TC-TR-01 file gone from original, present in trash")
    if ok:
        passed += 1
    else:
        failed += 1
finally:
    cleanup(tmpdir)

# TC-TR-02: file outside project root is blocked, file remains
reset_session()
tmpdir = make_git_repo()
outside = tempfile.NamedTemporaryFile(delete=False, dir="/tmp", prefix="trash_test_", suffix=".txt")
outside.write(b"outside\n")
outside.close()
try:
    rc = run_hook(tmpdir, outside.name)
    file_still_exists = os.path.exists(outside.name)
    check("TC-TR-02 outside-root file blocked", rc, 2)
    ok = file_still_exists
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] TC-TR-02 file outside root not moved")
    if ok:
        passed += 1
    else:
        failed += 1
finally:
    os.unlink(outside.name)
    cleanup(tmpdir)

# TC-TR-03: two sequential calls share the same trash directory within a session
reset_session()
tmpdir = make_git_repo()
try:
    f1 = os.path.join(tmpdir, "file1.txt")
    f2 = os.path.join(tmpdir, "file2.txt")
    with open(f1, "w") as f:
        f.write("one\n")
    with open(f2, "w") as f:
        f.write("two\n")
    run_hook(tmpdir, f1)
    trash_after_first = open(SESSION_FILE).read().strip() if os.path.exists(SESSION_FILE) else ""
    run_hook(tmpdir, f2)
    trash_after_second = open(SESSION_FILE).read().strip() if os.path.exists(SESSION_FILE) else ""
    ok = bool(trash_after_first) and trash_after_first == trash_after_second
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] TC-TR-03 same trash dir on second call")
    if ok:
        passed += 1
    else:
        failed += 1
finally:
    cleanup(tmpdir)

# TC-TR-04: no session file before call → hook creates SESSION_FILE
reset_session()
tmpdir = make_git_repo()
try:
    target = os.path.join(tmpdir, "new_file.txt")
    with open(target, "w") as f:
        f.write("new\n")
    rc = run_hook(tmpdir, target)
    session_created = os.path.exists(SESSION_FILE)
    check("TC-TR-04 creates session file", rc, 0)
    ok = session_created
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] TC-TR-04 SESSION_FILE created after first call")
    if ok:
        passed += 1
    else:
        failed += 1
finally:
    cleanup(tmpdir)

# TC-TR-05: multiple files passed as arguments — all moved in one call
reset_session()
tmpdir = make_git_repo()
try:
    files = []
    for i in range(3):
        p = os.path.join(tmpdir, f"multi_{i}.txt")
        with open(p, "w") as f:
            f.write(f"file {i}\n")
        files.append(p)
    rc = run_hook(tmpdir, *files)
    check("TC-TR-05 multi-file move exits 0", rc, 0)
    all_gone = all(not os.path.exists(p) for p in files)
    trash_dir = open(SESSION_FILE).read().strip() if os.path.exists(SESSION_FILE) else ""
    all_in_trash = trash_dir and all(
        os.path.exists(os.path.join(trash_dir, os.path.basename(p))) for p in files
    )
    ok = all_gone and all_in_trash
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] TC-TR-05 all files moved to trash")
    if ok:
        passed += 1
    else:
        failed += 1
finally:
    cleanup(tmpdir)
    reset_session()

print(f"\n{passed} passed, {failed} failed")
sys.exit(0 if failed == 0 else 1)
