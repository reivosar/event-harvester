#!/usr/bin/env python3
"""Tests for pre-commit.sh: secret detection, branch validation, trailing whitespace."""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HOOK = os.path.join(os.path.dirname(__file__), "pre-commit.sh")


def make_git_repo():
    tmpdir = tempfile.mkdtemp(prefix="hook_test_commit_")
    subprocess.run(["git", "init", tmpdir], check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmpdir, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmpdir, check=True, capture_output=True)
    subprocess.run(["git", "checkout", "-b", "feat/test-branch"], cwd=tmpdir, check=True, capture_output=True)
    init_path = os.path.join(tmpdir, "init.txt")
    with open(init_path, "w") as f:
        f.write("init\n")
    subprocess.run(["git", "add", "init.txt"], cwd=tmpdir, check=True, capture_output=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=tmpdir, check=True, capture_output=True)
    return tmpdir


def make_branch(tmpdir, name):
    subprocess.run(["git", "checkout", "-b", name], cwd=tmpdir, check=True, capture_output=True)


def stage_file(tmpdir, name, content):
    path = os.path.join(tmpdir, name)
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "w") as f:
        f.write(content)
    subprocess.run(["git", "add", name], cwd=tmpdir, check=True, capture_output=True)


def run_hook(tmpdir, command):
    payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": command}})
    result = subprocess.run(
        ["bash", HOOK],
        input=payload, capture_output=True, text=True, cwd=tmpdir,
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


# TC-CM-01: non-commit command is not inspected by the hook
tmpdir = make_git_repo()
try:
    check("TC-CM-01 non-commit command skipped", run_hook(tmpdir, "git status"), 0)
finally:
    cleanup(tmpdir)

# TC-CM-02: git commit with nothing staged exits early
tmpdir = make_git_repo()
try:
    check("TC-CM-02 nothing staged exits 0", run_hook(tmpdir, "git commit -m 'x'"), 0)
finally:
    cleanup(tmpdir)

# TC-CM-03: clean file staged on valid branch → allowed
tmpdir = make_git_repo()
try:
    stage_file(tmpdir, "app.py", "x = 1\n")
    check("TC-CM-03 clean file allowed", run_hook(tmpdir, "git commit -m 'x'"), 0)
finally:
    cleanup(tmpdir)

# TC-CM-04: file with password secret → blocked
# String split so this source file doesn't match the secret-detection pattern
tmpdir = make_git_repo()
try:
    stage_file(tmpdir, "app.py", "pass" + 'word = "mysecret"\n')
    check("TC-CM-04 password secret blocked", run_hook(tmpdir, "git commit -m 'x'"), 2)
finally:
    cleanup(tmpdir)

# TC-CM-05: file with api_key secret → blocked
tmpdir = make_git_repo()
try:
    stage_file(tmpdir, "config.py", "api_" + "key = 'abcdef12'\n")
    check("TC-CM-05 api_key secret blocked", run_hook(tmpdir, "git commit -m 'x'"), 2)
finally:
    cleanup(tmpdir)

# TC-CM-06: token value only 3 chars — below the 4-char threshold → allowed
tmpdir = make_git_repo()
try:
    stage_file(tmpdir, "config.py", 'token = "abc"\n')
    check("TC-CM-06 short token not blocked", run_hook(tmpdir, "git commit -m 'x'"), 0)
finally:
    cleanup(tmpdir)

# TC-CM-07: feat/ branch prefix → allowed
tmpdir = make_git_repo()
try:
    make_branch(tmpdir, "feat/my-feature")
    stage_file(tmpdir, "app.py", "x = 1\n")
    check("TC-CM-07 feat/ branch allowed", run_hook(tmpdir, "git commit -m 'x'"), 0)
finally:
    cleanup(tmpdir)

# TC-CM-08: fix/ branch prefix → allowed
tmpdir = make_git_repo()
try:
    make_branch(tmpdir, "fix/bug-123")
    stage_file(tmpdir, "app.py", "x = 1\n")
    check("TC-CM-08 fix/ branch allowed", run_hook(tmpdir, "git commit -m 'x'"), 0)
finally:
    cleanup(tmpdir)

# TC-CM-09: no recognised prefix → blocked
tmpdir = make_git_repo()
try:
    make_branch(tmpdir, "my-feature")
    stage_file(tmpdir, "app.py", "x = 1\n")
    check("TC-CM-09 unprefixed branch blocked", run_hook(tmpdir, "git commit -m 'x'"), 2)
finally:
    cleanup(tmpdir)

# TC-CM-10: branch named 'main' is exempt from prefix check → allowed
tmpdir = make_git_repo()
try:
    make_branch(tmpdir, "main")
    stage_file(tmpdir, "app.py", "x = 1\n")
    check("TC-CM-10 main branch allowed", run_hook(tmpdir, "git commit -m 'x'"), 0)
finally:
    cleanup(tmpdir)

# TC-CM-11: branch named 'master' is exempt → allowed
tmpdir = make_git_repo()
try:
    make_branch(tmpdir, "master")
    stage_file(tmpdir, "app.py", "x = 1\n")
    check("TC-CM-11 master branch allowed", run_hook(tmpdir, "git commit -m 'x'"), 0)
finally:
    cleanup(tmpdir)

# TC-CM-12: detached HEAD — git rev-parse returns "HEAD" which is exempt → allowed
tmpdir = make_git_repo()
try:
    subprocess.run(["git", "checkout", "--detach", "HEAD"], cwd=tmpdir, check=True, capture_output=True)
    stage_file(tmpdir, "app.py", "x = 1\n")
    check("TC-CM-12 detached HEAD allowed", run_hook(tmpdir, "git commit -m 'x'"), 0)
finally:
    cleanup(tmpdir)

# TC-CM-13: file with trailing whitespace → blocked
tmpdir = make_git_repo()
try:
    stage_file(tmpdir, "app.py", "hello \n")
    check("TC-CM-13 trailing whitespace blocked", run_hook(tmpdir, "git commit -m 'x'"), 2)
finally:
    cleanup(tmpdir)

# TC-CM-14: file with no trailing whitespace → allowed
tmpdir = make_git_repo()
try:
    stage_file(tmpdir, "app.py", "hello\n")
    check("TC-CM-14 no trailing whitespace allowed", run_hook(tmpdir, "git commit -m 'x'"), 0)
finally:
    cleanup(tmpdir)

# TC-CM-15: secret and trailing whitespace combined → blocked (multiple errors reported)
tmpdir = make_git_repo()
try:
    stage_file(tmpdir, "app.py", "pass" + 'word = "mysecret" \n')
    check("TC-CM-15 secret and trailing whitespace blocked", run_hook(tmpdir, "git commit -m 'x'"), 2)
finally:
    cleanup(tmpdir)

print(f"\n{passed} passed, {failed} failed")
sys.exit(0 if failed == 0 else 1)
